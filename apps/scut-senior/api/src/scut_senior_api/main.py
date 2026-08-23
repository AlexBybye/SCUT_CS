from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from hmac import compare_digest
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

from .adapters.bilibili import BilibiliLinkDiscoveryAdapter
from .adapters.byok import (
    ByokGatewayError,
    FailClosedJsonHttpClient,
    FixedByokModelGateway,
)
from .adapters.github import (
    FailClosedHttpTransport,
    GitHubOAuthAdapter,
    GitHubOAuthError,
)
from .adapters.exam_facts import (
    FixtureExamFactsProvider,
    LocalCorpusExamFactsProvider,
)
from .adapters.local_corpus import LocalCorpusRetrievalGateway
from .adapters.mock import (
    FixtureRetrievalGateway,
    MockIdentityProvider,
    MockModelGateway,
)
from .adapters.openrouter import (
    JsonHttpClient,
    OpenRouterGatewayError,
    OpenRouterModelGateway,
)
from .adapters.openrouter_health import OpenRouterCatalogHealthChecker
from .adapters.zhipu import ZhipuPlatformGatewayError, ZhipuPlatformModelGateway
from .adapters.zhipu_health import ZhipuPlatformHealthChecker
from .adapters.sqlite import SQLiteWorkflowRepository
from .auth import (
    OAUTH_STATE_TTL,
    SESSION_COOKIE_HTTP_ONLY,
    SESSION_COOKIE_MAX_AGE,
    SESSION_COOKIE_NAME,
    SESSION_COOKIE_PATH,
    SESSION_COOKIE_SAME_SITE,
    SESSION_COOKIE_SECURE,
    AuthRequired,
    AuthenticatedPrincipal,
    Clock,
    GitHubUserProfile,
    OAuthStateInvalid,
    TokenFactory,
    secure_token,
    utc_now,
)
from .config import Settings

LOGGER = logging.getLogger("scut_senior.api")
from .course_availability import derive_course_runtime_availability
from .contracts import (
    ContributionDraftSubmit,
    ContributionPreview,
    ContributionPreviewRequest,
    ContributionRecord,
    ContributionState,
    ContributionSubmit,
    ConversationCreate,
    ConversationDetail,
    ConversationRename,
    ConversationSummary,
    FeedbackCreate,
    FeedbackRecord,
    MaintainerContributionExport,
    MaintainerContributionTransition,
    ModelCredentialStatus,
    ModelCredentialUpsert,
    TemporaryMaterialCreate,
    TemporaryMaterialDetail,
    TemporaryMaterialRecord,
    WorkflowAttempt,
    WorkflowResult,
    WorkflowRunRequest,
)
from .credentials import CredentialCipher
from .harness_registry import (
    CONTROLLED_TOOL_CATALOG,
    HARNESS_REGISTRY,
    MAINTAINER_SKILLS,
    derive_course_plugin_states,
)
from .contributions import ContributionTransitionError
from .maintenance import MaintenanceScheduler
from .quota import SqlitePlatformQuotaStore
from .model_catalog import (
    ModelCatalog,
    ModelCatalogResponse,
    ModelHealthChecker,
    ModelHealthResult,
    ModelNotRegistered,
)
from .model_credentials import ModelCredentialError, ModelCredentialManager
from .paths import APP_ROOT
from .ports import CapabilityUnavailable, DisabledCapability, HumanizerGateway
from .ports import ModelGateway, UserIdentity
from .registry import CourseRegistry, UnknownCourseError
from .runtime_guards import RuntimeGuardError
from .service import ContractConflict, IterationZeroService, ResourceNotFound
from .workflow_stream import WorkflowStreamSession

# 活跃流式会话登记：run_id → (user_id, session)。
# 静默断线不再取消运行（见 stream_workflow），显式取消端点靠这里定位会话。
_ACTIVE_STREAMS: dict[str, tuple[str, WorkflowStreamSession]] = {}


OAUTH_STATE_COOKIE_NAME = "__Host-scut_senior_oauth_state"
MAX_REQUEST_BODY_BYTES = 2 * 1024 * 1024
MAX_BUFFERED_REQUEST_MESSAGES = 4096


class _RequestBodyLimitMiddleware:
    """Bound JSON/body memory before FastAPI parses user-controlled payloads."""

    def __init__(self, app, *, max_body_bytes: int) -> None:
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope, receive, send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        declared_lengths = [
            value
            for key, value in scope.get("headers", [])
            if key.lower() == b"content-length"
        ]
        if declared_lengths:
            try:
                declared = int(declared_lengths[-1])
            except (TypeError, ValueError):
                declared = -1
            if declared > self.max_body_bytes:
                await self._reject(scope, receive, send)
                return

        received = 0
        buffered_messages = []
        while True:
            message = await receive()
            if len(buffered_messages) >= MAX_BUFFERED_REQUEST_MESSAGES:
                await self._reject(scope, receive, send)
                return
            if message.get("type") == "http.request":
                body = message.get("body", b"")
                if received + len(body) > self.max_body_bytes:
                    await self._reject(scope, receive, send)
                    return
                received += len(body)

            # Preserve each ASGI message instead of coalescing the request body.
            # This keeps the downstream receive order intact while bounding the
            # cached body to max_body_bytes (plus the one chunk being inspected).
            buffered_messages.append(message)
            if message.get("type") == "http.disconnect" or (
                message.get("type") == "http.request"
                and not message.get("more_body", False)
            ):
                break

        replay_index = 0

        async def replay_receive():
            nonlocal replay_index
            if replay_index < len(buffered_messages):
                message = buffered_messages[replay_index]
                replay_index += 1
                return message
            # Streaming responses can continue listening for a disconnect after
            # the complete request body has been replayed.
            return await receive()

        await self.app(scope, replay_receive, send)

    @staticmethod
    async def _reject(scope, receive, send) -> None:
        response = JSONResponse(
            status_code=413,
            content={
                "error": {
                    "code": "request_body_too_large",
                    "detail": "请求内容过大，请缩短后重试。",
                }
            },
            headers={"Cache-Control": "private, no-store"},
        )
        await response(scope, receive, send)


class _FailClosedModelHealthChecker:
    def __init__(self, clock: Clock):
        self._clock = clock

    def check(self, model_ids):
        checked_at = self._clock()
        return {
            model_id: ModelHealthResult("health_check_failed", checked_at)
            for model_id in model_ids
        }


def create_app(
    settings: Settings | None = None,
    *,
    model_http_client: JsonHttpClient | None = None,
    zhipu_http_client: JsonHttpClient | None = None,
    byok_http_client: JsonHttpClient | None = None,
    model_health_checker: ModelHealthChecker | None = None,
    zhipu_health_checker: ModelHealthChecker | None = None,
    github_oauth_adapter: GitHubOAuthAdapter | None = None,
    clock: Clock = utc_now,
    oauth_state_token_factory: TokenFactory = secure_token,
    session_token_factory: TokenFactory = secure_token,
    humanizer: HumanizerGateway | None = None,
) -> FastAPI:
    active_settings = settings or Settings.from_env()
    active_settings.assert_safe()
    registry = CourseRegistry.load()
    mock_identity = MockIdentityProvider().current_user()
    retrieval = (
        LocalCorpusRetrievalGateway(active_settings.corpus_store_path)
        if active_settings.retrieval_mode == "local_corpus"
        else FixtureRetrievalGateway(registry)
    )
    platform_credential_configured = (
        active_settings.model_mode == "openrouter_platform"
    )
    openrouter_configured = bool(
        active_settings.openrouter_api_key
        and active_settings.openrouter_api_key.strip()
    )
    zhipu_configured = bool(
        active_settings.zhipu_api_key and active_settings.zhipu_api_key.strip()
    )
    byok_master_key = active_settings.byok_master_key_bytes()
    byok_runtime_enabled = (
        byok_master_key is not None
        and active_settings.identity_mode == "github_oauth"
        and active_settings.storage_mode == "sqlite"
    )
    if platform_credential_configured and openrouter_configured:
        if model_health_checker is None:
            if active_settings.app_env == "test":
                model_health_checker = _FailClosedModelHealthChecker(clock)
            else:
                model_health_checker = OpenRouterCatalogHealthChecker(
                    api_key=active_settings.openrouter_api_key or "",
                    clock=clock,
                )
    if platform_credential_configured and zhipu_configured:
        if zhipu_health_checker is None:
            zhipu_health_checker = ZhipuPlatformHealthChecker(
                api_key=active_settings.zhipu_api_key or "",
                clock=clock,
            )
    model_catalog = ModelCatalog(
        openrouter_credential_configured=(
            platform_credential_configured and openrouter_configured
        ),
        zhipu_credential_configured=(
            platform_credential_configured and zhipu_configured
        ),
        byok_runtime_enabled=byok_runtime_enabled,
        openrouter_health_checker=model_health_checker,
        zhipu_health_checker=zhipu_health_checker,
        clock=clock,
    )
    resources = BilibiliLinkDiscoveryAdapter()
    repository = SQLiteWorkflowRepository(
        active_settings.database_path,
        clock=clock,
        state_token_factory=oauth_state_token_factory,
        session_token_factory=session_token_factory,
    )
    if platform_credential_configured and openrouter_configured:
        if active_settings.app_env == "test" and model_http_client is None:
            model_http_client = FailClosedJsonHttpClient()
        model = OpenRouterModelGateway(
            api_key=active_settings.openrouter_api_key or "",
            allowed_model_ids=[
                entry.model_id
                for entry in model_catalog.entries
                if entry.provider_id == "openrouter"
            ],
            http_client=model_http_client,
            clock=clock,
            # 迭代 7.5：RPM／每日额度锁存迁移到多 worker 共享存储。
            quota_store=SqlitePlatformQuotaStore(repository),
        )
    else:
        model = MockModelGateway()
    zhipu_model: ModelGateway | None = None
    if platform_credential_configured and zhipu_configured:
        if active_settings.app_env == "test" and zhipu_http_client is None:
            zhipu_http_client = FailClosedJsonHttpClient()
        zhipu_model = ZhipuPlatformModelGateway(
            api_key=active_settings.zhipu_api_key or "",
            allowed_model_ids=[
                entry.model_id
                for entry in model_catalog.entries
                if entry.provider_id == "zhipu"
            ],
            http_client=zhipu_http_client,
        )
    credential_manager = ModelCredentialManager(
        repository=repository,
        catalog=model_catalog.byok_catalog,
        cipher=(
            CredentialCipher(byok_master_key, active_settings.byok_key_version)
            if byok_master_key is not None
            else None
        ),
    )
    if active_settings.app_env == "test" and byok_http_client is None:
        byok_http_client = FailClosedJsonHttpClient()
    byok_model = FixedByokModelGateway(
        http_client=byok_http_client,
        catalog=model_catalog.byok_catalog,
    )
    oauth_adapter = github_oauth_adapter
    if active_settings.identity_mode == "github_oauth" and oauth_adapter is None:
        oauth_adapter = GitHubOAuthAdapter(
            client_id=active_settings.github_client_id or "",
            client_secret=active_settings.github_client_secret or "",
            redirect_uri=active_settings.github_callback_url or "",
            http_transport=(
                FailClosedHttpTransport()
                if active_settings.app_env == "test"
                else None
            ),
        )
    service = IterationZeroService(
        settings=active_settings,
        registry=registry,
        retrieval=retrieval,
        model=model,
        zhipu_model=zhipu_model,
        resources=resources,
        repository=repository,
        model_catalog=model_catalog,
        credential_manager=credential_manager,
        byok_model=byok_model,
        humanizer=humanizer,
        exam_facts=(
            LocalCorpusExamFactsProvider(active_settings.corpus_store_path)
            if active_settings.retrieval_mode == "local_corpus"
            else FixtureExamFactsProvider()
        ),
    )

    maintenance_scheduler: MaintenanceScheduler | None = None
    if isinstance(repository, SQLiteWorkflowRepository):
        maintenance_scheduler = MaintenanceScheduler(
            repository,
            interval_seconds=float(active_settings.maintenance_interval_seconds),
            clock=clock,
        )

    @asynccontextmanager
    async def _maintenance_lifespan(_: FastAPI):
        # 迭代 7.5：启动补扫一次后按固定间隔周期清理；停机等待当前轮结束。
        scheduler = app.state.maintenance_scheduler
        if scheduler is not None and active_settings.maintenance_scheduler_enabled:
            scheduler.start()
        try:
            yield
        finally:
            if scheduler is not None:
                scheduler.stop(timeout=5.0)

    app = FastAPI(
        title="SCUT Senior API",
        version="0.1.0",
        description="SCUT Senior backend contract and guarded model-routing slice.",
        lifespan=_maintenance_lifespan,
    )
    app.add_middleware(
        _RequestBodyLimitMiddleware,
        max_body_bytes=MAX_REQUEST_BODY_BYTES,
    )

    @app.middleware("http")
    async def protect_private_api_responses(request: Request, call_next):
        response = await call_next(request)
        if _is_protected_api_path(request.url.path):
            response.headers["Cache-Control"] = "private, no-store"
        return response

    app.state.settings = active_settings
    app.state.registry = registry
    app.state.service = service
    app.state.repository = repository
    app.state.maintenance_scheduler = maintenance_scheduler
    app.state.github_oauth_adapter = oauth_adapter
    app.state.model_catalog = model_catalog
    app.state.byok_catalog = model_catalog.byok_catalog
    app.state.credential_manager = credential_manager
    app.state.retrieval = retrieval
    app.state.unconfirmed_ports = {
        "vector_index": DisabledCapability("vector_index"),
        "object_store": DisabledCapability("object_store"),
        "task_queue": DisabledCapability("task_queue"),
        "github_app": DisabledCapability("github_app"),
    }

    @app.exception_handler(CapabilityUnavailable)
    async def capability_unavailable_handler(_, exc: CapabilityUnavailable):
        return _error_response(
            status_code=503,
            code="capability_unavailable",
            detail=exc.detail,
            capability=exc.capability,
        )

    @app.exception_handler(AuthRequired)
    async def auth_required_handler(_, __: AuthRequired):
        return _error_response(
            401,
            "auth_required",
            "请先使用 GitHub 登录。",
        )

    @app.exception_handler(OAuthStateInvalid)
    async def oauth_state_invalid_handler(_, __: OAuthStateInvalid):
        response = _error_response(
            400,
            "oauth_state_invalid",
            "GitHub 登录状态无效、已过期或已使用，请重新登录。",
        )
        _clear_oauth_state_cookie(response)
        return response

    @app.exception_handler(GitHubOAuthError)
    async def github_oauth_error_handler(_, exc: GitHubOAuthError):
        response = _error_response(
            502 if exc.code == "github_oauth_unavailable" else 400,
            exc.code,
            exc.detail,
        )
        _clear_oauth_state_cookie(response)
        return response

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(_, __: RequestValidationError):
        # FastAPI's default payload echoes invalid input values. Keep the public
        # error deliberately generic so a mistakenly submitted credential is
        # never reflected in the response.
        return _error_response(
            422,
            "request_validation_error",
            "请求不符合接口契约。",
        )

    @app.exception_handler(UnknownCourseError)
    async def unknown_course_handler(_, exc: UnknownCourseError):
        return _error_response(422, "unknown_course", str(exc))

    @app.exception_handler(ContractConflict)
    async def contract_conflict_handler(_, exc: ContractConflict):
        return _error_response(409, "contract_conflict", str(exc))

    @app.exception_handler(ContributionTransitionError)
    async def contribution_transition_handler(_, exc: ContributionTransitionError):
        return _error_response(
            409, "contribution_transition_invalid", str(exc)
        )

    @app.exception_handler(ResourceNotFound)
    async def resource_not_found_handler(_, exc: ResourceNotFound):
        return _error_response(404, "not_found", str(exc))

    @app.exception_handler(ModelNotRegistered)
    async def model_not_registered_handler(_, exc: ModelNotRegistered):
        return _error_response(422, "model_not_registered", str(exc))

    @app.exception_handler(OpenRouterGatewayError)
    async def openrouter_gateway_error_handler(_, exc: OpenRouterGatewayError):
        return _error_response(exc.status_code, exc.code, exc.detail)

    @app.exception_handler(ZhipuPlatformGatewayError)
    async def zhipu_gateway_error_handler(_, exc: ZhipuPlatformGatewayError):
        return _error_response(exc.status_code, exc.code, exc.detail)

    @app.exception_handler(ByokGatewayError)
    async def byok_gateway_error_handler(_, exc: ByokGatewayError):
        return _error_response(exc.status_code, exc.code, exc.detail)

    @app.exception_handler(ModelCredentialError)
    async def model_credential_error_handler(_, exc: ModelCredentialError):
        return _error_response(exc.status_code, exc.code, exc.detail)

    @app.exception_handler(RuntimeGuardError)
    async def runtime_guard_error_handler(_, __: RuntimeGuardError):
        return _error_response(
            502,
            "workflow_output_rejected",
            "模型输出未通过引用与证据校验，请重试。",
        )

    def current_course_runtime_availability():
        """Read the same runtime gates used by the workflow service.

        The catalog is intentionally derived per request: a plugin may be
        loaded or unloaded while the app stays up, and a local corpus pointer
        can become invalid without a process restart.
        """

        return derive_course_runtime_availability(
            registry,
            service.retrieval,
            service.repository,
            retrieval_mode=active_settings.retrieval_mode,
        )

    @app.get("/api/v1/health")
    def health() -> dict[str, object]:
        model_catalog.refresh_health()
        course_states = current_course_runtime_availability()
        local_corpus_retrieval_available_course_count = sum(
            state.retrieval_availability == "local_corpus"
            for state in course_states
        )
        retrieval_available_course_count = sum(
            state.retrieval_available for state in course_states
        )
        selectable_course_count = sum(state.selectable for state in course_states)
        active_corpus_configured = local_corpus_retrieval_available_course_count > 0
        return {
            "status": "ok",
            "iteration": 7,
            # 口径自声明：状态值内嵌迭代号，避免再次出现字段停在旧迭代的静默滞后。
            "iteration_status": (
                "iteration7_material_governance_with_active_corpus"
                if active_corpus_configured
                else "iteration7_fixture_runtime_active_corpus_required"
            ),
            "formal_exit_blocked": not active_corpus_configured,
            "runtime": (
                f"{active_settings.model_mode}_with_"
                f"{active_settings.identity_mode}_{active_settings.storage_mode}"
            ),
            # Configuration and usable corpus state are intentionally separate:
            # local_corpus mode alone does not prove an active.json is valid.
            "retrieval_mode": active_settings.retrieval_mode,
            "local_corpus_mode_configured": (
                active_settings.retrieval_mode == "local_corpus"
            ),
            "local_corpus_available": active_corpus_configured,
            "local_corpus_retrieval_available_course_count": (
                local_corpus_retrieval_available_course_count
            ),
            "retrieval_available_course_count": retrieval_available_course_count,
            "selectable_course_count": selectable_course_count,
            "capabilities": {
                "github_oauth": active_settings.identity_mode == "github_oauth",
                "server_sessions_7_day": (
                    active_settings.identity_mode == "github_oauth"
                ),
                "resource_ownership": True,
                "sqlite_runtime": active_settings.storage_mode == "sqlite",
                "platform_credential_configured": platform_credential_configured,
                "real_model": model_catalog.real_platform_default_available,
                "byok": byok_runtime_enabled,
                "bilibili_anonymous_search_links": (
                    active_settings.bilibili_resources_enabled
                ),
                "workflow_runtime": True,
                "workflow_stream_ndjson": True,
                "citation_guard": True,
                "response_style_control": True,
                "humanizer_guard": True,
                "humanizer_configured": humanizer is not None,
                "active_corpus_configured": active_corpus_configured,
                "production_retrieval": False,
                "local_corpus_retrieval": active_corpus_configured,
                "cross_course": active_settings.cross_course_enabled,
                "mock_vertical_slice": (
                    active_settings.identity_mode == "mock"
                    and active_settings.model_mode == "mock"
                    and active_settings.storage_mode == "sqlite_mock"
                ),
                # 迭代 7：临时材料治理与贡献待处理队列；自动 PR 仍属
                # GitHub App 决策门之后的未确认能力，保持 fail-closed。
                "temporary_material_ttl_7d": True,
                "contribution_maintainer_queue": True,
                "github_app_auto_pr": False,
                # 迭代 7.5：进程内周期清理调度器（决策门确认形态）。
                "periodic_cleanup_scheduler": (
                    maintenance_scheduler is not None
                    and active_settings.maintenance_scheduler_enabled
                ),
            },
        }

    def require_user(request: Request) -> UserIdentity | AuthenticatedPrincipal:
        if active_settings.identity_mode == "mock":
            return mock_identity
        token = request.cookies.get(SESSION_COOKIE_NAME, "")
        principal = repository.authenticate_session(token)
        if principal is None:
            raise AuthRequired()
        return principal

    def require_github_user(
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> AuthenticatedPrincipal:
        if isinstance(user, UserIdentity) or user.is_mock:
            raise AuthRequired()
        return user

    @app.get("/api/v1/auth/github/start")
    def github_login_start():
        if active_settings.identity_mode != "github_oauth" or oauth_adapter is None:
            raise CapabilityUnavailable(
                "github_oauth",
                "GitHub OAuth 未配置，当前登录入口保持关闭。",
            )
        issued_state = repository.issue_oauth_state()
        response = RedirectResponse(
            oauth_adapter.build_authorization_url(issued_state.state),
            status_code=302,
        )
        response.set_cookie(
            OAUTH_STATE_COOKIE_NAME,
            issued_state.state,
            max_age=int(OAUTH_STATE_TTL.total_seconds()),
            path=SESSION_COOKIE_PATH,
            secure=SESSION_COOKIE_SECURE,
            httponly=SESSION_COOKIE_HTTP_ONLY,
            samesite=SESSION_COOKIE_SAME_SITE,
        )
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/api/v1/auth/github/callback")
    def github_login_callback(request: Request, code: str = "", state: str = ""):
        if active_settings.identity_mode != "github_oauth" or oauth_adapter is None:
            raise CapabilityUnavailable(
                "github_oauth",
                "GitHub OAuth 未配置，当前登录回调保持关闭。",
            )
        cookie_state = request.cookies.get(OAUTH_STATE_COOKIE_NAME, "")
        if (
            not state
            or not cookie_state
            or not compare_digest(state, cookie_state)
            or not repository.consume_oauth_state(state)
        ):
            raise OAuthStateInvalid()

        identity = oauth_adapter.authenticate(code)
        user_id = repository.upsert_github_user(
            GitHubUserProfile(
                github_user_id=identity.github_id,
                login=identity.login,
                display_name=identity.display_name,
            )
        )
        session = repository.issue_session(user_id)
        response = RedirectResponse(
            active_settings.post_login_redirect_url or "/",
            status_code=303,
        )
        response.set_cookie(
            SESSION_COOKIE_NAME,
            session.token,
            max_age=SESSION_COOKIE_MAX_AGE,
            path=SESSION_COOKIE_PATH,
            secure=SESSION_COOKIE_SECURE,
            httponly=SESSION_COOKIE_HTTP_ONLY,
            samesite=SESSION_COOKIE_SAME_SITE,
        )
        _clear_oauth_state_cookie(response)
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.post("/api/v1/auth/logout")
    def logout(
        request: Request,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ):
        if not user.is_mock:
            repository.revoke_session(request.cookies.get(SESSION_COOKIE_NAME, ""))
        response = JSONResponse({"logged_out": not user.is_mock})
        _clear_session_cookie(response)
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/api/v1/me")
    def me(
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> dict[str, object]:
        return {
            "user_id": str(user.user_id),
            "display_name": user.display_name,
            "auth_mode": "mock" if user.is_mock else "github_oauth",
            "is_mock": user.is_mock,
            "github_login": (
                None if user.is_mock else user.github_login
            ),
            "session_expires_at": (
                None if user.is_mock else user.expires_at.isoformat()
            ),
        }

    @app.get("/api/v1/models", response_model=ModelCatalogResponse)
    def models() -> dict[str, object]:
        return model_catalog.public_payload()

    @app.get(
        "/api/v1/model-credentials",
        response_model=list[ModelCredentialStatus],
    )
    def list_model_credentials(
        user: AuthenticatedPrincipal = Depends(require_github_user),
    ) -> list[ModelCredentialStatus]:
        return credential_manager.list_statuses(user)

    @app.put(
        "/api/v1/model-credentials/{provider_id}",
        response_model=ModelCredentialStatus,
    )
    def replace_model_credential(
        provider_id: str,
        payload: ModelCredentialUpsert,
        user: AuthenticatedPrincipal = Depends(require_github_user),
    ) -> ModelCredentialStatus:
        return credential_manager.replace(user, provider_id, payload)

    @app.delete(
        "/api/v1/model-credentials/{provider_id}",
        status_code=204,
    )
    def delete_model_credential(
        provider_id: str,
        user: AuthenticatedPrincipal = Depends(require_github_user),
    ) -> Response:
        credential_manager.delete(user, provider_id)
        return Response(status_code=204)

    @app.get("/api/v1/courses")
    def courses() -> dict[str, object]:
        course_states = current_course_runtime_availability()
        return {
            "contract_version": registry.contract_version,
            "retrieval_mode": active_settings.retrieval_mode,
            # Keep the older field during the transition; new clients must use
            # retrieval_mode and each course's runtime availability instead.
            "runtime": active_settings.retrieval_mode,
            "courses": [state.as_public_dict() for state in course_states],
        }

    @app.get("/api/v1/plugin-registry")
    def plugin_registry() -> dict[str, object]:
        """Controlled plugin metadata for internal management.

        Safe by construction: immutable registry metadata plus honest
        per-course states derived from the CourseRegistry, the current
        RetrievalGateway availability and the persisted plugin load state.
        Never exposes prompts, directives, secrets or user data.
        """
        course_states = derive_course_plugin_states(
            registry,
            retrieval,
            retrieval_mode=active_settings.retrieval_mode,
        )
        return {
            "registry_version": HARNESS_REGISTRY.version,
            "retrieval_mode": active_settings.retrieval_mode,
            "agent_presets": [
                preset.as_public_dict() for preset in HARNESS_REGISTRY.presets
            ],
            "controlled_tools": [
                tool.as_public_dict() for tool in CONTROLLED_TOOL_CATALOG
            ],
            "maintainer_skills": [
                skill.as_public_dict() for skill in MAINTAINER_SKILLS
            ],
            "courses": [
                {
                    "course_id": state.course_id,
                    "display_name": state.display_name,
                    "state": state.state.value,
                    "loaded": repository.is_course_plugin_loaded(state.course_id),
                    "enabled_workflows": (
                        [
                            workflow.value
                            for workflow in state.enabled_workflows
                        ]
                        if repository.is_course_plugin_loaded(state.course_id)
                        else []
                    ),
                }
                for state in course_states
            ],
        }

    @app.post("/api/v1/plugin-registry/courses/{course_id}/load")
    def load_course_plugin(
        course_id: str,
        user: AuthenticatedPrincipal = Depends(require_github_user),
    ) -> dict[str, object]:
        return {"course_id": service.load_course_plugin(user, course_id), "loaded": True}

    @app.post("/api/v1/plugin-registry/courses/{course_id}/unload")
    def unload_course_plugin(
        course_id: str,
        user: AuthenticatedPrincipal = Depends(require_github_user),
    ) -> dict[str, object]:
        return {"course_id": service.unload_course_plugin(user, course_id), "loaded": False}

    @app.post(
        "/api/v1/conversations",
        response_model=ConversationSummary,
        status_code=201,
    )
    def create_conversation(
        payload: ConversationCreate,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> ConversationSummary:
        return service.create_conversation(user, payload.course_id)

    @app.get(
        "/api/v1/conversations",
        response_model=list[ConversationSummary],
    )
    def list_conversations(
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> list[ConversationSummary]:
        return service.list_conversations(user)

    @app.get(
        "/api/v1/conversations/{conversation_id}",
        response_model=ConversationDetail,
    )
    def get_conversation(
        conversation_id: UUID,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> ConversationDetail:
        return service.get_conversation(user, conversation_id)

    @app.patch(
        "/api/v1/conversations/{conversation_id}",
        response_model=ConversationSummary,
    )
    def rename_conversation(
        conversation_id: UUID,
        payload: ConversationRename,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> ConversationSummary:
        return service.rename_conversation(user, conversation_id, payload.title)

    @app.delete(
        "/api/v1/conversations/{conversation_id}",
        status_code=204,
    )
    def delete_conversation(
        conversation_id: UUID,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> Response:
        service.delete_conversation(user, conversation_id)
        return Response(status_code=204)

    @app.post(
        "/api/v1/workflow-runs", response_model=WorkflowResult, status_code=201
    )
    def run_workflow(
        payload: WorkflowRunRequest,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> WorkflowResult:
        return service.run(user, payload)

    @app.post("/api/v1/workflow-runs/stream")
    async def stream_workflow(
        payload: WorkflowRunRequest,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> StreamingResponse:
        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[object] = asyncio.Queue()
        finished = object()

        def enqueue_event(event: object) -> None:
            try:
                loop.call_soon_threadsafe(queue.put_nowait, event)
            except RuntimeError:
                # 事件循环已关闭（进程退出）：流已无处可送，取消是唯一选择。
                session.cancel()

        session = WorkflowStreamSession(enqueue_event)
        run_key = str(session.workflow_run_id)
        # 显式取消端点需要按 run_id 找到会话；静默断线不再等价于取消。
        _ACTIVE_STREAMS[run_key] = (str(user.user_id), session)

        def execute() -> None:
            try:
                service.run_stream(user, payload, session)
            except Exception as exc:
                if not session.terminal_emitted:
                    # Failed attempts are persisted by the Runtime, while the
                    # stream keeps the provider's bounded public error code so
                    # quota/auth guidance is not lost behind a generic result.
                    code, detail = _safe_stream_error(exc)
                    session.emit_error(code, detail)
            finally:
                try:
                    loop.call_soon_threadsafe(queue.put_nowait, finished)
                except RuntimeError:
                    session.cancel()

        async def event_source():
            task = asyncio.create_task(asyncio.to_thread(execute))
            try:
                while True:
                    item = await queue.get()
                    if item is finished:
                        break
                    # Omitting unrelated payload fields is part of the wire
                    # protocol; explicit null siblings are rejected by clients.
                    event_payload = item.model_dump(mode="json")
                    for sibling in (
                        "trace_event",
                        "answer_delta",
                        "result",
                        "error",
                    ):
                        if event_payload.get(sibling) is None:
                            event_payload.pop(sibling, None)
                    yield json.dumps(
                        event_payload,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ) + "\n"
                await task
            except (asyncio.CancelledError, GeneratorExit):
                # 迭代 7.5（SOP §12A 分组 B）：取代迭代 5"客户端断开后后台跑
                # 完落库"的过渡语义——页面断开（aclose 触发 GeneratorExit，
                # 任务取消触发 CancelledError）即请求尽力取消上游调用：
                # cancel_check 置位后可取消 transport 放弃等待，运行在下一个
                # 节点边界收敛为 interrupted 并留 trace／日志证据。供应商侧
                # 是否因此停止计费只如实描述，不冒充已完成取消。
                session.cancel()
                LOGGER.warning(
                    "stream disconnected; best-effort upstream cancellation "
                    "requested for workflow run %s",
                    run_key,
                )
                raise
            finally:
                _ACTIVE_STREAMS.pop(run_key, None)
                if task.done() and not task.cancelled():
                    task.exception()

        return StreamingResponse(
            event_source(),
            media_type="application/x-ndjson",
            headers={
                "Cache-Control": "private, no-store",
                "X-Accel-Buffering": "no",
            },
        )

    @app.post("/api/v1/workflow-runs/{run_id}/cancel")
    async def cancel_workflow(
        run_id: UUID,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> dict[str, bool]:
        entry = _ACTIVE_STREAMS.get(str(run_id))
        if entry is None or entry[0] != str(user.user_id):
            raise HTTPException(
                status_code=404,
                detail="没有正在运行的该工作流（可能已完成、已取消或不属于当前用户）。",
            )
        entry[1].cancel()
        return {"cancel_requested": True}

    @app.post(
        "/api/v1/workflow-runs/{run_id}/regenerate",
        response_model=WorkflowAttempt,
        status_code=201,
    )
    def regenerate_workflow_run(
        run_id: UUID,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> WorkflowAttempt:
        return service.regenerate(user, run_id)

    @app.get("/api/v1/workflow-runs/{run_id}", response_model=WorkflowResult)
    def get_workflow_run(
        run_id: UUID,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> WorkflowResult:
        return service.get_run(user, run_id)

    @app.get("/api/v1/workflow-runs/{run_id}/trace")
    def get_trace(
        run_id: UUID,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> dict[str, object]:
        result = service.get_run(user, run_id)
        return {
            "workflow_run_id": str(result.workflow_run_id),
            "trace": [event.model_dump(mode="json") for event in result.trace],
        }

    @app.post("/api/v1/feedback", response_model=FeedbackRecord, status_code=201)
    def submit_feedback(
        payload: FeedbackCreate,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> FeedbackRecord:
        return service.submit_feedback(user, payload)

    @app.get("/api/v1/feedback", response_model=list[FeedbackRecord])
    def list_feedback(
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> list[FeedbackRecord]:
        return service.list_feedback(user)

    # ------------------------------------------------------------------
    # 迭代 7（SOP §12）：临时材料精读与贡献待处理队列。
    # ------------------------------------------------------------------

    @app.post(
        "/api/v1/temporary-materials",
        response_model=TemporaryMaterialRecord,
        status_code=201,
    )
    def save_temporary_material(
        payload: TemporaryMaterialCreate,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> TemporaryMaterialRecord:
        return service.save_temporary_material(user, payload)

    @app.get(
        "/api/v1/temporary-materials",
        response_model=list[TemporaryMaterialRecord],
    )
    def list_temporary_materials(
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> list[TemporaryMaterialRecord]:
        return service.list_temporary_materials(user)

    @app.get(
        "/api/v1/temporary-materials/{material_id}",
        response_model=TemporaryMaterialDetail,
    )
    def get_temporary_material(
        material_id: UUID,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> TemporaryMaterialDetail:
        return service.get_temporary_material(user, material_id)

    @app.delete("/api/v1/temporary-materials/{material_id}", status_code=204)
    def delete_temporary_material(
        material_id: UUID,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> Response:
        service.delete_temporary_material(user, material_id)
        return Response(status_code=204)

    @app.post(
        "/api/v1/contributions/preview",
        response_model=ContributionPreview,
    )
    def preview_contribution(
        payload: ContributionPreviewRequest,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> ContributionPreview:
        return service.build_contribution_preview(user, payload)

    @app.post(
        "/api/v1/contributions",
        response_model=ContributionRecord,
        status_code=201,
    )
    def submit_contribution(
        payload: ContributionSubmit,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> ContributionRecord:
        return service.submit_contribution(user, payload)

    @app.get(
        "/api/v1/contributions",
        response_model=list[ContributionRecord],
    )
    def list_contributions(
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> list[ContributionRecord]:
        return service.list_contributions(user)

    @app.get(
        "/api/v1/contributions/{contribution_id}",
        response_model=ContributionRecord,
    )
    def get_contribution(
        contribution_id: UUID,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> ContributionRecord:
        return service.get_contribution(user, contribution_id)

    @app.post(
        "/api/v1/contributions/{contribution_id}/submit",
        response_model=ContributionRecord,
    )
    def submit_contribution_draft(
        contribution_id: UUID,
        payload: ContributionDraftSubmit,
        user: UserIdentity | AuthenticatedPrincipal = Depends(require_user),
    ) -> ContributionRecord:
        return service.submit_contribution_draft(user, contribution_id, payload)

    @app.get(
        "/api/v1/maintainer/contributions",
        response_model=list[ContributionRecord],
    )
    def maintainer_contribution_queue(
        state: str | None = None,
        user: AuthenticatedPrincipal = Depends(require_github_user),
    ) -> list[ContributionRecord]:
        parsed_state: ContributionState | None = None
        if state is not None:
            try:
                parsed_state = ContributionState(state)
            except ValueError:
                raise HTTPException(
                    status_code=422, detail="unknown contribution state"
                ) from None
        return service.list_maintainer_queue(parsed_state)

    @app.get(
        "/api/v1/maintainer/contributions/{contribution_id}/export",
        response_model=MaintainerContributionExport,
    )
    def maintainer_export_contribution(
        contribution_id: UUID,
        user: AuthenticatedPrincipal = Depends(require_github_user),
    ) -> MaintainerContributionExport:
        return service.maintainer_export_contribution(contribution_id)

    @app.post(
        "/api/v1/maintainer/contributions/{contribution_id}/transition",
        response_model=ContributionRecord,
    )
    def maintainer_transition_contribution(
        contribution_id: UUID,
        payload: MaintainerContributionTransition,
        user: AuthenticatedPrincipal = Depends(require_github_user),
    ) -> ContributionRecord:
        return service.maintainer_transition_contribution(
            contribution_id, payload
        )

    static_root = APP_ROOT / "web" / "dist"
    if static_root.is_dir():
        app.mount("/", StaticFiles(directory=static_root, html=True), name="web")
    return app


def _clear_oauth_state_cookie(response: Response) -> None:
    response.delete_cookie(
        OAUTH_STATE_COOKIE_NAME,
        path=SESSION_COOKIE_PATH,
        secure=SESSION_COOKIE_SECURE,
        httponly=SESSION_COOKIE_HTTP_ONLY,
        samesite=SESSION_COOKIE_SAME_SITE,
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        SESSION_COOKIE_NAME,
        path=SESSION_COOKIE_PATH,
        secure=SESSION_COOKIE_SECURE,
        httponly=SESSION_COOKIE_HTTP_ONLY,
        samesite=SESSION_COOKIE_SAME_SITE,
    )


def _is_protected_api_path(path: str) -> bool:
    protected_roots = (
        "/api/v1/me",
        "/api/v1/auth/logout",
        "/api/v1/conversations",
        "/api/v1/workflow-runs",
        "/api/v1/model-credentials",
        "/api/v1/feedback",
        "/api/v1/plugin-registry",
        "/api/v1/temporary-materials",
        "/api/v1/contributions",
        "/api/v1/maintainer",
    )
    return any(path == root or path.startswith(f"{root}/") for root in protected_roots)


def _error_response(
    status_code: int,
    code: str,
    detail: str,
    capability: str | None = None,
):
    from fastapi.responses import JSONResponse

    payload: dict[str, object] = {"error": {"code": code, "detail": detail}}
    if capability is not None:
        payload["error"]["capability"] = capability  # type: ignore[index]
    return JSONResponse(status_code=status_code, content=payload)


def _safe_stream_error(exc: Exception) -> tuple[str, str]:
    """Map execution failures to the same bounded public error vocabulary."""

    if isinstance(exc, AuthRequired):
        return "auth_required", "请先使用 GitHub 登录。"
    if isinstance(exc, RuntimeGuardError):
        return (
            "workflow_output_rejected",
            "模型输出未通过引用与证据校验，请重试。",
        )
    if isinstance(
        exc, OpenRouterGatewayError | ZhipuPlatformGatewayError | ByokGatewayError
    ):
        return exc.code, exc.detail
    if isinstance(exc, ModelCredentialError):
        return exc.code, exc.detail
    if isinstance(exc, CapabilityUnavailable):
        return "capability_unavailable", exc.detail
    if isinstance(exc, ModelNotRegistered):
        return "model_not_registered", "所选模型未登记。"
    if isinstance(exc, ResourceNotFound):
        return "not_found", "请求的资源不存在。"
    if isinstance(exc, ContractConflict | UnknownCourseError):
        return "contract_conflict", "请求与当前会话或课程范围冲突。"
    return "workflow_execution_failed", "本次运行失败，请稍后重试。"


app = create_app()
