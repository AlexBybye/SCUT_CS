from __future__ import annotations

from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from .adapters.mock import (
    FixtureBilibiliCatalog,
    FixtureRetrievalGateway,
    MockIdentityProvider,
    MockModelGateway,
)
from .adapters.sqlite import SQLiteMockWorkflowRepository
from .config import Settings
from .contracts import (
    ConversationCreate,
    ConversationDetail,
    ConversationSummary,
    WorkflowResult,
    WorkflowRunRequest,
)
from .paths import APP_ROOT
from .ports import CapabilityUnavailable, DisabledCapability
from .registry import CourseRegistry, UnknownCourseError
from .service import ContractConflict, IterationZeroService, ResourceNotFound


def create_app(settings: Settings | None = None) -> FastAPI:
    active_settings = settings or Settings.from_env()
    active_settings.assert_safe()
    registry = CourseRegistry.load()
    identity = MockIdentityProvider()
    retrieval = FixtureRetrievalGateway(registry)
    model = MockModelGateway()
    resources = FixtureBilibiliCatalog()
    repository = SQLiteMockWorkflowRepository(active_settings.database_path)
    service = IterationZeroService(
        settings=active_settings,
        registry=registry,
        identity=identity,
        retrieval=retrieval,
        model=model,
        resources=resources,
        repository=repository,
    )

    app = FastAPI(
        title="SCUT Senior API",
        version="0.1.0",
        description=(
            "Iteration 0 mock contract slice. It does not provide real OAuth, "
            "model inference, or production retrieval."
        ),
    )
    app.state.settings = active_settings
    app.state.registry = registry
    app.state.service = service
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

    @app.exception_handler(UnknownCourseError)
    async def unknown_course_handler(_, exc: UnknownCourseError):
        return _error_response(422, "unknown_course", str(exc))

    @app.exception_handler(ContractConflict)
    async def contract_conflict_handler(_, exc: ContractConflict):
        return _error_response(409, "contract_conflict", str(exc))

    @app.exception_handler(ResourceNotFound)
    async def resource_not_found_handler(_, exc: ResourceNotFound):
        return _error_response(404, "not_found", str(exc))

    @app.get("/api/v1/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "iteration": 0,
            "runtime": "mock_only",
            "capabilities": {
                "github_oauth": False,
                "real_model": False,
                "production_retrieval": False,
                "cross_course": active_settings.cross_course_enabled,
                "mock_vertical_slice": True,
            },
        }

    @app.get("/api/v1/me")
    def me() -> dict[str, object]:
        user = identity.current_user()
        return {
            "user_id": user.user_id,
            "display_name": user.display_name,
            "auth_mode": "mock",
            "is_mock": user.is_mock,
        }

    @app.get("/api/v1/models")
    def models() -> dict[str, object]:
        return {
            "real_platform_default_available": False,
            "byok_available": False,
            "models": [
                {
                    "provider_id": "mock",
                    "model_id": "deterministic-fixture-v1",
                    "model_source": "platform_default",
                    "availability_status": "mock_only",
                    "billing_label": "not_applicable_mock",
                }
            ],
        }

    @app.get("/api/v1/courses")
    def courses() -> dict[str, object]:
        return {
            "contract_version": registry.contract_version,
            "runtime": "mock_only",
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
    def create_conversation(payload: ConversationCreate) -> ConversationSummary:
        return service.create_conversation(payload.course_id)

    @app.get(
        "/api/v1/conversations/{conversation_id}",
        response_model=ConversationDetail,
    )
    def get_conversation(conversation_id: UUID) -> ConversationDetail:
        return service.get_conversation(conversation_id)

    @app.post(
        "/api/v1/workflow-runs", response_model=WorkflowResult, status_code=201
    )
    def run_workflow(payload: WorkflowRunRequest) -> WorkflowResult:
        return service.run(payload)

    @app.get("/api/v1/workflow-runs/{run_id}", response_model=WorkflowResult)
    def get_workflow_run(run_id: UUID) -> WorkflowResult:
        return service.get_run(run_id)

    @app.get("/api/v1/workflow-runs/{run_id}/trace")
    def get_trace(run_id: UUID) -> dict[str, object]:
        result = service.get_run(run_id)
        return {
            "workflow_run_id": str(result.workflow_run_id),
            "trace": [event.model_dump(mode="json") for event in result.trace],
        }

    static_root = APP_ROOT / "web" / "dist"
    if static_root.is_dir():
        app.mount("/", StaticFiles(directory=static_root, html=True), name="web")
    return app


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


app = create_app()

