from __future__ import annotations

import asyncio
import json
from hmac import compare_digest
from uuid import UUID

from fastapi import Depends, FastAPI, Request
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
from .contracts import (
    ConversationCreate,
    ConversationDetail,
    ConversationRename,
    ConversationSummary,
    FeedbackCreate,
    FeedbackRecord,
    ModelCredentialStatus,
    ModelCredentialUpsert,
    WorkflowAttempt,
    WorkflowResult,
    WorkflowRunRequest,
)
from .credentials import CredentialCipher
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
from .ports import UserIdentity
from .registry import CourseRegistry, UnknownCourseError
from .runtime_guards import RuntimeGuardError
from .service import ContractConflict, IterationZeroService, ResourceNotFound
from .workflow_stream import WorkflowStreamSession


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
    byok_http_client: JsonHttpClient | None = None,
    model_health_checker: ModelHealthChecker | None = None,
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
    byok_master_key = active_settings.byok_master_key_bytes()
    byok_runtime_enabled = (
        byok_master_key is not None
        and active_settings.identity_mode == "github_oauth"
        and active_settings.storage_mode == "sqlite"
    )
    if platform_credential_configured and model_health_checker is None:
        if active_settings.app_env == "test":
            model_health_checker = _FailClosedModelHealthChecker(clock)
        else:
            model_health_checker = OpenRouterCatalogHealthChecker(
                api_key=active_settings.openrouter_api_key or "",
                clock=clock,
            )
    model_catalog = ModelCatalog(
        platform_credential_configured=platform_credential_configured,
        byok_runtime_enabled=byok_runtime_enabled,
        health_checker=model_health_checker,
        clock=clock,
    )
    if platform_credential_configured:
        if active_settings.app_env == "test" and model_http_client is None:
            model_http_client = FailClosedJsonHttpClient()
        model = OpenRouterModelGateway(
            api_key=active_settings.openrouter_api_key or "",
            allowed_model_ids=[entry.model_id for entry in model_catalog.entries],
            http_client=model_http_client,
            clock=clock,
        )
    else:
        model = MockModelGateway()
    resources = BilibiliLinkDiscoveryAdapter()
    repository = SQLiteWorkflowRepository(
        active_settings.database_path,
        clock=clock,
        state_token_factory=oauth_state_token_factory,
        session_token_factory=session_token_factory,
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
    byok_model = FixedByokModelGateway(http_client=byok_http_client)
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
        resources=resources,
        repository=repository,
        model_catalog=model_catalog,
        credential_manager=credential_manager,
        byok_model=byok_model,
        humanizer=humanizer,
    )

    app = FastAPI(
        title="SCUT Senior API",
        version="0.1.0",
        description="SCUT Senior backend contract and guarded model-routing slice.",
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

    @app.exception_handler(ResourceNotFound)
    async def resource_not_found_handler(_, exc: ResourceNotFound):
        return _error_response(404, "not_found", str(exc))

    @app.exception_handler(ModelNotRegistered)
    async def model_not_registered_handler(_, exc: ModelNotRegistered):
        return _error_response(422, "model_not_registered", str(exc))

    @app.exception_handler(OpenRouterGatewayError)
    async def openrouter_gateway_error_handler(_, exc: OpenRouterGatewayError):
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

    @app.get("/api/v1/health")
    def health() -> dict[str, object]:
        model_catalog.refresh_health()
        active_corpus_configured = (
            active_settings.retrieval_mode == "local_corpus"
        )
        return {
            "status": "ok",
            "iteration": 3,
            "iteration_status": (
                "local_runtime_with_active_corpus"
                if active_corpus_configured
                else "local_fixture_runtime_active_corpus_required"
            ),
            "formal_exit_blocked": not active_corpus_configured,
            "runtime": (
                f"{active_settings.model_mode}_with_"
                f"{active_settings.identity_mode}_{active_settings.storage_mode}"
            ),
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
                "humanizer_guard": True,
                "active_corpus_configured": active_corpus_configured,
                "production_retrieval": False,
                "local_corpus_retrieval": (
                    active_settings.retrieval_mode == "local_corpus"
                ),
                "cross_course": active_settings.cross_course_enabled,
                "mock_vertical_slice": (
                    active_settings.identity_mode == "mock"
                    and active_settings.model_mode == "mock"
                    and active_settings.storage_mode == "sqlite_mock"
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
        return {
            "contract_version": registry.contract_version,
            "runtime": active_settings.retrieval_mode,
            "courses": [
                {
                    "course_id": course.course_id,
                    "display_name": course.display_name,
                    "aliases": list(course.aliases),
                    "is_open": course.is_open,
                    "mock_available": course.fixture_available,
                }
                for course in registry.records
            ],
        }

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
                session.cancel()

        session = WorkflowStreamSession(enqueue_event)

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
            except asyncio.CancelledError:
                session.cancel()
                raise
            finally:
                session.cancel()
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
    if isinstance(exc, OpenRouterGatewayError | ByokGatewayError):
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
