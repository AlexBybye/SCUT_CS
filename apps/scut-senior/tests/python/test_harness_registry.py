from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from scut_senior_api.adapters.mock import FixtureRetrievalGateway
from scut_senior_api.config import Settings
from scut_senior_api.course_availability import derive_course_runtime_availability
from scut_senior_api.contracts import WorkflowRunRequest, WorkflowType
from scut_senior_api.harness_registry import (
    AGENT_PRESETS,
    CONTROLLED_TOOL_CATALOG,
    HARNESS_REGISTRY,
    MAINTAINER_SKILLS,
    AgentPreset,
    ControlledTool,
    ControlledToolMetadata,
    HarnessRegistry,
    MaintainerSkillMetadata,
    MaterialConversionSkillStatus,
    derive_course_plugin_states,
)
from scut_senior_api.main import create_app
from scut_senior_api.registry import CourseRegistry
from scut_senior_api.workflow_focus import (
    FocusStrategy,
    build_workflow_focus,
)

EXPECTED_FOCUS_BY_WORKFLOW = {
    WorkflowType.KNOWLEDGE_QA: FocusStrategy.QUESTION_CONCEPT,
    WorkflowType.EXAM_REVIEW: FocusStrategy.SYLLABUS_WEAK_TOPICS,
    WorkflowType.PROBLEM_TUTOR: FocusStrategy.PROBLEM_MAIN_TOPIC,
    WorkflowType.MISTAKE_REVIEW: FocusStrategy.MISTAKE_ROOT_CAUSE,
    WorkflowType.TEMPORARY_MATERIAL_READING: FocusStrategy.MATERIAL_TITLE_MAIN_TOPICS,
}

WORKFLOW_PAYLOADS: dict[str, dict[str, object]] = {
    "knowledge_qa": {"question": "请解释矩阵的秩"},
    "exam_review": {
        "syllabus": "矩阵与线性方程组",
        "exam_date": None,
        "available_hours": 4,
        "goals": ["复习矩阵的秩"],
        "weak_topics": ["初等行变换"],
    },
    "problem_tutor": {
        "problem": "求一个矩阵的秩",
        "user_answer": None,
        "help_level": "step_by_step",
        "problem_source": None,
    },
    "mistake_review": {
        "problem": "求一个矩阵的秩",
        "original_answer": "秩等于矩阵的行数",
        "reference_answer": None,
        "review_focus": "定位概念错误",
    },
    "temporary_material_reading": {
        "material_title": "矩阵秩复习说明",
        "material_text": "初等行变换不改变矩阵的秩。",
        "reading_goal": "理解矩阵秩",
    },
}


def _request_dict(
    conversation_id: str,
    *,
    workflow_type: str = "knowledge_qa",
    model_id: str = "deterministic-fixture-v1",
) -> dict[str, object]:
    return {
        "workflow_type": workflow_type,
        "course_scope": "single",
        "course_id": "linear_algebra",
        "allowed_course_ids": [],
        "conversation_id": conversation_id,
        "model_source": "platform_default",
        "provider_id": "mock" if model_id == "deterministic-fixture-v1" else "openrouter",
        "model_id": model_id,
        "user_input": "请解释矩阵的秩",
        "answer_mode": "detailed",
        "tone": "teaching_assistant",
        "knowledge_scope": "course_first",
        "include_bilibili_resources": False,
        "context_refs": [],
        "attachments": [],
        "workflow_payload": WORKFLOW_PAYLOADS[workflow_type],
    }


def _preset(workflow_type: WorkflowType) -> AgentPreset:
    preset = HARNESS_REGISTRY.resolve_preset(workflow_type)
    assert preset is not None
    return preset


def _registry_with(presets: list[AgentPreset]) -> HarnessRegistry:
    return HarnessRegistry(
        version="test-registry-v1",
        presets=presets,
        tools=CONTROLLED_TOOL_CATALOG,
        skills=MAINTAINER_SKILLS,
    )


def test_registry_exposes_exactly_five_presets_covering_all_workflow_types() -> None:
    assert len(HARNESS_REGISTRY.presets) == 5
    assert {preset.workflow_type for preset in HARNESS_REGISTRY.presets} == set(
        WorkflowType
    )
    assert len({preset.preset_id for preset in HARNESS_REGISTRY.presets}) == 5
    assert HARNESS_REGISTRY.version == "harness-registry-v1"
    tool_ids = {tool.tool_id for tool in CONTROLLED_TOOL_CATALOG}

    for preset in HARNESS_REGISTRY.presets:
        assert preset.preset_id.startswith("preset_")
        assert preset.preset_version == "v1"
        assert preset.display_name
        assert preset.required_input_modalities == ("text",)
        assert preset.requires_structured_outputs is False
        assert preset.allowed_tools
        assert set(preset.allowed_tools) <= tool_ids
        assert preset.focus_strategy == EXPECTED_FOCUS_BY_WORKFLOW[preset.workflow_type]


def test_preset_focus_strategies_match_the_runtime_focus_builder() -> None:
    for workflow_type in WorkflowType:
        request = WorkflowRunRequest.model_validate(
            _request_dict(
                "11111111-1111-1111-1111-111111111111",
                workflow_type=workflow_type.value,
            )
        )
        assert build_workflow_focus(request).focus_strategy == EXPECTED_FOCUS_BY_WORKFLOW[
            workflow_type
        ]


def test_preset_metadata_never_contains_prompt_text() -> None:
    serialized = json.dumps([preset.as_public_dict() for preset in AGENT_PRESETS])
    for forbidden in ("prompt", "directive", "authoritative_query", "anchor_context"):
        assert forbidden not in serialized


def test_registry_construction_rejects_incomplete_workflow_coverage() -> None:
    with pytest.raises(ValueError, match="cover WorkflowType exactly"):
        _registry_with(list(AGENT_PRESETS)[:4])


def test_registry_construction_rejects_duplicate_workflow_coverage() -> None:
    duplicate = AgentPreset(
        preset_id="preset_knowledge_qa_duplicate",
        preset_version="v1",
        display_name="重复预设",
        workflow_type=WorkflowType.KNOWLEDGE_QA,
        focus_strategy=FocusStrategy.QUESTION_CONCEPT,
        allowed_tools=(ControlledTool.COURSE_RETRIEVAL,),
        required_input_modalities=("text",),
        requires_structured_outputs=False,
    )
    with pytest.raises(ValueError, match="exactly one preset"):
        _registry_with([duplicate, *AGENT_PRESETS])


def test_registry_construction_rejects_unknown_tool_reference() -> None:
    presets = [
        AgentPreset(
            preset_id="preset_with_unknown_tool",
            preset_version="v1",
            display_name="未知工具预设",
            workflow_type=WorkflowType.KNOWLEDGE_QA,
            focus_strategy=FocusStrategy.QUESTION_CONCEPT,
            allowed_tools=(ControlledTool.BILIBILI_ANONYMOUS_SEARCH,),
            required_input_modalities=("text",),
            requires_structured_outputs=False,
        ),
        *AGENT_PRESETS[1:],
    ]
    tools = (
        ControlledToolMetadata(
            tool_id=ControlledTool.COURSE_RETRIEVAL,
            display_name="课程检索",
            description="测试目录",
        ),
    )
    with pytest.raises(ValueError, match="references unknown tools"):
        HarnessRegistry(
            version="test-registry-v1",
            presets=presets,
            tools=tools,
            skills=MAINTAINER_SKILLS,
        )


def test_registry_construction_rejects_unknown_required_modality() -> None:
    presets = [
        AgentPreset(
            preset_id="preset_with_unknown_modality",
            preset_version="v1",
            display_name="未知模态预设",
            workflow_type=WorkflowType.KNOWLEDGE_QA,
            focus_strategy=FocusStrategy.QUESTION_CONCEPT,
            allowed_tools=(ControlledTool.COURSE_RETRIEVAL,),
            required_input_modalities=("haptic",),
            requires_structured_outputs=False,
        ),
        *AGENT_PRESETS[1:],
    ]
    with pytest.raises(ValueError, match="unknown modalities"):
        _registry_with(presets)


def test_model_compatibility_requires_text_modality_but_not_structured_outputs() -> None:
    preset = _preset(WorkflowType.KNOWLEDGE_QA)

    assert (
        preset.check_model_compatibility(
            input_modalities=("text",),
            supports_structured_outputs=True,
        )
        is None
    )
    missing_modality = preset.check_model_compatibility(
        input_modalities=("image",),
        supports_structured_outputs=True,
    )
    assert missing_modality is not None
    assert "text" in missing_modality
    assert "preset_knowledge_qa" in missing_modality

    structured_output_optional = preset.check_model_compatibility(
        input_modalities=("text",),
        supports_structured_outputs=False,
    )
    assert structured_output_optional is None


def test_course_plugin_states_report_fixture_coverage_without_claiming_active() -> None:
    registry = CourseRegistry.load()
    gateway = FixtureRetrievalGateway(registry)

    states = derive_course_plugin_states(registry, gateway, retrieval_mode="fixture")

    by_id = {state.course_id: state for state in states}
    assert len(by_id) == 55
    assert by_id["linear_algebra"].state.value == "fixture_only"
    assert by_id["linear_algebra"].enabled_workflows == ()
    assert by_id["cpp"].state.value == "registered"
    assert by_id["cpp"].enabled_workflows == ()
    assert all(
        state.state.value == "registered" and state.enabled_workflows == ()
        for course_id, state in by_id.items()
        if course_id != "linear_algebra"
    )


def test_course_plugin_states_mark_only_verified_local_corpus_active() -> None:
    registry = CourseRegistry.load()

    class ActiveLocalCorpusGateway:
        def is_course_available(self, course_id: str) -> bool:
            return course_id == "linear_algebra"

    states = derive_course_plugin_states(
        registry, ActiveLocalCorpusGateway(), retrieval_mode="local_corpus"
    )

    by_id = {state.course_id: state for state in states}
    assert by_id["linear_algebra"].state.value == "active"
    assert [workflow.value for workflow in by_id["linear_algebra"].enabled_workflows] == [
        workflow.value for workflow in WorkflowType
    ]
    assert by_id["cpp"].state.value == "registered"
    assert by_id["cpp"].enabled_workflows == ()


def test_course_plugin_states_fail_closed_without_gateway_availability() -> None:
    registry = CourseRegistry.load()

    class UnavailableGateway:
        def is_course_available(self, course_id: str) -> bool:
            del course_id
            raise RuntimeError("local corpus store is missing")

    states = derive_course_plugin_states(
        registry, UnavailableGateway(), retrieval_mode="local_corpus"
    )
    by_id = {state.course_id: state for state in states}
    assert by_id["linear_algebra"].state.value == "fixture_only"
    assert by_id["cpp"].state.value == "registered"
    assert all(state.enabled_workflows == () for state in states)


def test_course_runtime_availability_fails_closed_when_plugin_state_cannot_be_read() -> None:
    registry = CourseRegistry.load()
    gateway = FixtureRetrievalGateway(registry)

    class BrokenPluginRepository:
        def is_course_plugin_loaded(self, course_id: str) -> bool:
            del course_id
            raise RuntimeError("plugin state store is unavailable")

    states = derive_course_runtime_availability(
        registry,
        gateway,
        BrokenPluginRepository(),  # type: ignore[arg-type]
        retrieval_mode="fixture",
    )
    linear_algebra = next(
        state for state in states if state.course.course_id == "linear_algebra"
    )

    assert linear_algebra.retrieval_availability == "fixture"
    assert linear_algebra.retrieval_available is True
    assert linear_algebra.plugin_loaded is False
    assert linear_algebra.selectable is False


def test_courses_endpoint_exposes_runtime_selection_gates(tmp_path: Path) -> None:
    app = create_app(Settings(app_env="test", database_path=tmp_path / "courses.db"))
    client = TestClient(app)

    response = client.get("/api/v1/courses")

    assert response.status_code == 200
    body = response.json()
    assert body["contract_version"] == "v1"
    assert body["retrieval_mode"] == "fixture"
    assert body["runtime"] == "fixture"
    courses = {course["course_id"]: course for course in body["courses"]}
    assert courses["linear_algebra"] == {
        "course_id": "linear_algebra",
        "display_name": "线性代数",
        "aliases": ["线性代数与解析几何", "线代解几"],
        "is_open": False,
        "mock_available": True,
        "retrieval_availability": "fixture",
        "retrieval_available": True,
        "plugin_loaded": True,
        "selectable": True,
    }
    assert courses["cpp"]["mock_available"] is False
    assert courses["cpp"]["retrieval_availability"] == "unavailable"
    assert courses["cpp"]["retrieval_available"] is False
    assert courses["cpp"]["plugin_loaded"] is True
    assert courses["cpp"]["selectable"] is False

    app.state.repository.set_course_plugin_loaded("linear_algebra", False)
    after_unload = client.get("/api/v1/courses").json()
    linear_algebra = next(
        course
        for course in after_unload["courses"]
        if course["course_id"] == "linear_algebra"
    )
    assert linear_algebra["retrieval_available"] is True
    assert linear_algebra["plugin_loaded"] is False
    assert linear_algebra["selectable"] is False


def test_plugin_registry_endpoint_reports_honest_metadata(tmp_path: Path) -> None:
    client = TestClient(
        create_app(Settings(app_env="test", database_path=tmp_path / "plugin.db"))
    )

    response = client.get("/api/v1/plugin-registry")

    assert response.status_code == 200
    body = response.json()
    assert body["registry_version"] == "harness-registry-v1"
    assert len(body["agent_presets"]) == 5
    assert {preset["workflow_type"] for preset in body["agent_presets"]} == {
        workflow.value for workflow in WorkflowType
    }
    assert all(
        preset["required_input_modalities"] == ["text"]
        and preset["requires_structured_outputs"] is False
        for preset in body["agent_presets"]
    )
    assert len(body["controlled_tools"]) == 4
    assert all(tool["model_callable"] is False for tool in body["controlled_tools"])
    assert [tool["tool_id"] for tool in body["controlled_tools"]] == [
        "course_retrieval",
        "evidence_location",
        "bilibili_anonymous_search",
        "temporary_material_read",
    ]

    assert body["maintainer_skills"] == []

    courses = {course["course_id"]: course for course in body["courses"]}
    assert len(courses) == 55
    assert courses["linear_algebra"]["state"] == "fixture_only"
    assert courses["linear_algebra"]["enabled_workflows"] == []
    assert courses["cpp"]["state"] == "registered"
    assert courses["cpp"]["enabled_workflows"] == []

    serialized = json.dumps(body)
    for forbidden in ("prompt", "directive", "authoritative_query", "anchor_context"):
        assert forbidden not in serialized


def test_request_validation_trace_includes_preset_identity(tmp_path: Path) -> None:
    client = TestClient(
        create_app(Settings(app_env="test", database_path=tmp_path / "trace.db"))
    )
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "线性代数"}
    ).json()

    response = client.post(
        "/api/v1/workflow-runs",
        json=_request_dict(conversation["conversation_id"]),
    )

    assert response.status_code == 201, response.text
    result = response.json()
    assert result["run_status"] == "completed"
    validation = next(
        event
        for event in result["trace"]
        if event["node"] == "request_validation"
    )
    assert validation["result"] == {
        "workflow_type": "knowledge_qa",
        "course_scope": "single",
        "course_ids": ["linear_algebra"],
        "knowledge_scope": "course_first",
        "agent_preset_id": "preset_knowledge_qa",
        "agent_preset_version": "v1",
    }

    restored = client.get(f"/api/v1/workflow-runs/{result['workflow_run_id']}")
    assert restored.status_code == 200
    restored_validation = next(
        event
        for event in restored.json()["trace"]
        if event["node"] == "request_validation"
    )
    assert restored_validation["result"]["agent_preset_id"] == "preset_knowledge_qa"
    assert restored_validation["result"]["agent_preset_version"] == "v1"


def test_real_platform_model_missing_modality_fails_closed(tmp_path: Path) -> None:
    app = create_app(
        Settings(
            app_env="test",
            model_mode="openrouter_platform",
            database_path=tmp_path / "compat.db",
            openrouter_api_key="server-only-secret",
        )
    )
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()

    class IncompatibleModelEntry:
        provider_id = "openrouter"
        model_id = "google/gemma-4-26b-a4b-it:free"
        billing_label = "platform_daily_free_quota"
        availability_status = "available"
        input_modalities = ("image",)
        supports_structured_outputs = True

    class StubModelCatalog:
        byok_catalog = None

        def resolve(self, provider_id: str, model_id: str, model_source):
            del provider_id, model_id, model_source
            return IncompatibleModelEntry()

    app.state.service.model_catalog = StubModelCatalog()

    response = client.post(
        "/api/v1/workflow-runs",
        json=_request_dict(
            conversation["conversation_id"],
            model_id="google/gemma-4-26b-a4b-it:free",
        ),
    )

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "capability_unavailable"
    assert error["capability"] == "model"
    assert "preset_knowledge_qa" in error["detail"]
    assert "text" in error["detail"]


def test_mock_platform_models_skip_preset_capability_gate(tmp_path: Path) -> None:
    app = create_app(Settings(app_env="test", database_path=tmp_path / "mock.db"))
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()

    # The mock adapter is not in the model catalog, so the mock path must never
    # consult preset compatibility and must remain fully usable.
    response = client.post(
        "/api/v1/workflow-runs",
        json=_request_dict(conversation["conversation_id"]),
    )

    assert response.status_code == 201, response.text
    assert response.json()["model"]["mock_only"] is True


def test_maintainer_skills_are_empty_after_removing_the_conversion_entry() -> None:
    assert MAINTAINER_SKILLS == ()


def test_course_plugin_load_unload_persists_and_gates_runtime(tmp_path: Path) -> None:
    from fastapi.testclient import TestClient

    from scut_senior_api.auth import GitHubUserProfile, SESSION_COOKIE_NAME

    plugin_settings = Settings(
        app_env="test",
        identity_mode="github_oauth",
        storage_mode="sqlite",
        database_path=tmp_path / "plugin.db",
        github_client_id="client",
        github_client_secret="secret",
        github_callback_url="https://testserver/api/v1/auth/github/callback",
        post_login_redirect_url="https://testserver/",
    )
    app = create_app(plugin_settings)
    client = TestClient(app, base_url="https://testserver")

    # Load/unload requires a real GitHub login.
    assert (
        client.post("/api/v1/plugin-registry/courses/linear_algebra/unload").status_code
        == 401
    )

    repository = app.state.repository
    user_id = repository.upsert_github_user(GitHubUserProfile(9001, "maintainer"))
    session = repository.issue_session(user_id)
    client.cookies.set(SESSION_COOKIE_NAME, session.token, path="/")

    existing = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    )
    assert existing.status_code == 201, existing.text
    existing_conversation_id = existing.json()["conversation_id"]

    unloaded = client.post(
        "/api/v1/plugin-registry/courses/linear_algebra/unload"
    )
    assert unloaded.status_code == 200, unloaded.text
    assert unloaded.json() == {"course_id": "linear_algebra", "loaded": False}

    body = client.get("/api/v1/plugin-registry").json()
    course = next(
        item for item in body["courses"] if item["course_id"] == "linear_algebra"
    )
    assert course["loaded"] is False
    assert course["state"] == "fixture_only"
    assert course["enabled_workflows"] == []

    # An unloaded plugin blocks workflow runs for conversations that already
    # existed before the unload, proving this is a runtime gate rather than UI
    # state or only a new-conversation check.
    blocked_run = client.post(
        "/api/v1/workflow-runs",
        json=_request_dict(existing_conversation_id),
    )
    assert blocked_run.status_code == 503, blocked_run.text
    blocked_error = blocked_run.json()["error"]
    assert blocked_error["code"] == "capability_unavailable"
    assert blocked_error["capability"] == "course"

    # New conversations are blocked too.
    blocked = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    )
    assert blocked.status_code == 503
    assert blocked.json()["error"]["code"] == "capability_unavailable"

    # Loading restores the same pre-existing conversation as well.
    loaded = client.post("/api/v1/plugin-registry/courses/linear_algebra/load")
    assert loaded.status_code == 200
    assert loaded.json() == {"course_id": "linear_algebra", "loaded": True}

    resumed_run = client.post(
        "/api/v1/workflow-runs",
        json=_request_dict(existing_conversation_id),
    )
    assert resumed_run.status_code == 201, resumed_run.text
    assert resumed_run.json()["run_status"] == "completed"

    # The loaded state also survives a restart.
    restarted = create_app(Settings(app_env="test", database_path=tmp_path / "plugin.db"))
    assert restarted.state.repository.is_course_plugin_loaded("linear_algebra") is True
    created = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    )
    assert created.status_code == 201, created.text

    # Unknown course ids fail closed.
    unknown = client.post("/api/v1/plugin-registry/courses/not-a-course/load")
    assert unknown.status_code == 422
    assert unknown.json()["error"]["code"] == "unknown_course"
