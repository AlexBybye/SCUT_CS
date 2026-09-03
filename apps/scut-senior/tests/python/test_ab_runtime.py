from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import scut_senior_api.service as service_module
from scut_senior_api.agent_loop import AgentBudget, ModelAgentDecision
from scut_senior_api.config import Settings
from scut_senior_api.main import create_app
from scut_senior_api.ports import RetrievalBatch, RetrievedSource


def _request(conversation_id: str) -> dict[str, object]:
    return {
        "workflow_type": "knowledge_qa",
        "course_scope": "single",
        "course_id": "linear_algebra",
        "allowed_course_ids": [],
        "conversation_id": conversation_id,
        "model_source": "platform_default",
        "provider_id": "mock",
        "model_id": "deterministic-fixture-v1",
        "user_input": "请解释矩阵的秩",
        "answer_mode": "detailed",
        "tone": "teaching_assistant",
        "knowledge_scope": "course_first",
        "include_bilibili_resources": False,
        "context_refs": [],
        "attachments": [],
        "workflow_payload": {"question": "请解释矩阵的秩"},
    }


def _exam_request(conversation_id: str) -> dict[str, object]:
    request = _request(conversation_id)
    request.update(
        {
            "workflow_type": "exam_review",
            "user_input": "结合历年卷，帮我总结一份线性代数复习大纲",
            "workflow_payload": {
                "syllabus": "行列式、矩阵、秩、方程组、特征值与二次型",
                "exam_date": "2026-09-29",
                "available_hours": 12,
                "goals": ["90+", "公式记忆"],
                "weak_topics": ["特征值", "二次型"],
            },
        }
    )
    return request


class _SequenceRetrieval:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def is_course_available(self, course_id: str) -> bool:
        return course_id == "linear_algebra"

    def search(self, course_ids: list[str], query: str) -> RetrievalBatch:
        self.calls.append(query)
        ordinal = len(self.calls)
        source = RetrievedSource(
            chunk_id=f"linear_algebra:ab:p{ordinal}",
            course_id="linear_algebra",
            source_id=f"ab-source-{ordinal}",
            source_title=f"AB 测试资料 {ordinal}",
            text="矩阵的秩可以由初等行变换求得。",
            locator_type="page",
            locator_start=ordinal,
            locator_end=ordinal,
            question_id=None,
            heading_path=(),
        )
        return RetrievalBatch((source,), "ab-corpus", "ab-pack")


class _ActionModel:
    def __init__(self, action: str) -> None:
        self.action = action
        self.calls: list[dict[str, object]] = []

    def decide_action(self, request, state, phase, *, sources=(), history=()):
        self.calls.append(
            {
                "question": request.user_input,
                "phase": phase,
                "source_count": len(sources),
                "history_count": len(history),
            }
        )
        return self.action


def _model_mode_app(tmp_path: Path, name: str):
    app = create_app(
        Settings(
            app_env="test",
            database_path=tmp_path / name,
            agent_decision_mode="model",
        )
    )
    retrieval = _SequenceRetrieval()
    app.state.service.retrieval = retrieval
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    return app, client, conversation["conversation_id"], retrieval


def _metrics(result: dict[str, object]) -> dict[str, object]:
    return next(
        event["result"]
        for event in result["trace"]
        if event["node"] == "mock_model"
    )


def test_normal_success_accepts_model_generate_action_without_second_retrieval(
    tmp_path: Path,
) -> None:
    app, client, conversation_id, retrieval = _model_mode_app(
        tmp_path, "ab-generate.db"
    )
    action_model = _ActionModel("generate_answer")
    app.state.service.agent_decision = ModelAgentDecision(action_model)

    response = client.post("/api/v1/workflow-runs", json=_request(conversation_id))

    assert response.status_code == 201, response.text
    result = response.json()
    assert len(retrieval.calls) == 1
    assert action_model.calls == [
        {
            "question": "请解释矩阵的秩",
            "phase": "post_retrieval",
            "source_count": 1,
            "history_count": 0,
        }
    ]
    metrics = _metrics(result)
    assert metrics["decision_call_count"] == 1
    assert metrics["model_action_accepted_count"] == 1
    assert metrics["decision_fallback_count"] == 0
    assert metrics["action_rejection_count"] == 0
    assert all(event["node"] != "agent_query_rewrite" for event in result["trace"])
    events = app.state.repository.list_agent_events(result["workflow_run_id"])
    model_decision = next(
        event for event in events if event.get("phase") == "post_retrieval"
    )
    assert model_decision["decision_source"] == "model"
    assert model_decision["action"] == "generate_answer"
    model_index = events.index(model_decision)
    assert [event["kind"] for event in events[model_index : model_index + 3]] == [
        "decision_produced",
        "action_executed",
        "observation_recorded",
    ]
    assert events[model_index + 1]["action"] == "generate_answer"


def test_exam_review_success_reaches_and_accepts_model_action(tmp_path: Path) -> None:
    app, client, conversation_id, retrieval = _model_mode_app(
        tmp_path, "ab-exam-review.db"
    )
    action_model = _ActionModel("generate_answer")
    app.state.service.agent_decision = ModelAgentDecision(action_model)

    response = client.post(
        "/api/v1/workflow-runs", json=_exam_request(conversation_id)
    )

    assert response.status_code == 201, response.text
    result = response.json()
    assert result["workflow_type"] == "exam_review"
    assert len(retrieval.calls) == 1
    assert action_model.calls[0]["phase"] == "post_retrieval"
    metrics = _metrics(result)
    assert metrics["decision_call_count"] == 1
    assert metrics["model_action_accepted_count"] == 1
    assert metrics["decision_fallback_count"] == 0


def test_normal_success_executes_model_selected_query_rewrite(tmp_path: Path) -> None:
    app, client, conversation_id, retrieval = _model_mode_app(
        tmp_path, "ab-rewrite.db"
    )
    action_model = _ActionModel("retrieve_with_query_rewrite")
    app.state.service.agent_decision = ModelAgentDecision(action_model)

    response = client.post("/api/v1/workflow-runs", json=_request(conversation_id))

    assert response.status_code == 201, response.text
    result = response.json()
    assert len(retrieval.calls) == 2
    assert retrieval.calls[1] != retrieval.calls[0]
    assert "线性代数" in retrieval.calls[1]
    rewrite = next(
        event for event in result["trace"] if event["node"] == "agent_query_rewrite"
    )
    assert rewrite["status"] == "completed"
    assert rewrite["result"]["hit_count"] == 1
    assert rewrite["result"]["candidate_count"] == 2
    metrics = _metrics(result)
    assert metrics["decision_call_count"] == 1
    assert metrics["model_action_accepted_count"] == 1
    assert metrics["decision_fallback_count"] == 0
    executed = [
        event.get("action")
        for event in app.state.repository.list_agent_events(
            result["workflow_run_id"]
        )
        if event["kind"] == "action_executed"
    ]
    assert executed == [
        "retrieve",
        "retrieve_with_query_rewrite",
        "generate_answer",
    ]


def test_phase_incompatible_model_action_is_rejected_and_not_attributed(
    tmp_path: Path,
) -> None:
    app, client, conversation_id, retrieval = _model_mode_app(
        tmp_path, "ab-reject.db"
    )
    action_model = _ActionModel("retrieve")
    app.state.service.agent_decision = ModelAgentDecision(action_model)

    response = client.post("/api/v1/workflow-runs", json=_request(conversation_id))

    assert response.status_code == 201, response.text
    result = response.json()
    assert len(retrieval.calls) == 1
    metrics = _metrics(result)
    assert metrics["decision_call_count"] == 1
    assert metrics["model_action_accepted_count"] == 0
    assert metrics["action_rejection_count"] == 1
    assert metrics["decision_fallback_count"] == 0
    events = app.state.repository.list_agent_events(result["workflow_run_id"])
    assert any(event["kind"] == "action_rejected" for event in events)
    decision = next(event for event in events if event.get("phase") == "post_retrieval")
    assert decision["action"] == "generate_answer"
    assert decision["decision_source"] == "rule"


def test_unparseable_model_action_falls_back_and_workflow_completes(
    tmp_path: Path,
) -> None:
    app, client, conversation_id, retrieval = _model_mode_app(
        tmp_path, "ab-fallback.db"
    )
    action_model = _ActionModel("建议 generate_answer，因为证据足够")
    app.state.service.agent_decision = ModelAgentDecision(action_model)

    response = client.post("/api/v1/workflow-runs", json=_request(conversation_id))

    assert response.status_code == 201, response.text
    result = response.json()
    assert result["run_status"] == "completed"
    assert len(retrieval.calls) == 1
    metrics = _metrics(result)
    assert metrics["decision_call_count"] == 1
    assert metrics["model_action_accepted_count"] == 0
    assert metrics["decision_fallback_count"] == 1
    decision = next(
        event
        for event in app.state.repository.list_agent_events(
            result["workflow_run_id"]
        )
        if event.get("phase") == "post_retrieval"
    )
    assert decision["decision_source"] == "rule"


def test_soft_runtime_watermark_skips_optional_model_decision(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    real_budget = AgentBudget
    monkeypatch.setattr(
        service_module,
        "AgentBudget",
        lambda: real_budget(max_runtime_seconds=1, soft_runtime_ratio=1e-12),
    )
    app, client, conversation_id, retrieval = _model_mode_app(
        tmp_path, "ab-soft-limit.db"
    )
    action_model = _ActionModel("retrieve_with_query_rewrite")
    app.state.service.agent_decision = ModelAgentDecision(action_model)

    response = client.post("/api/v1/workflow-runs", json=_request(conversation_id))

    assert response.status_code == 201, response.text
    result = response.json()
    assert len(retrieval.calls) == 1
    assert action_model.calls == []
    metrics = _metrics(result)
    assert metrics["decision_call_count"] == 0
    skipped = next(
        event for event in result["trace"] if event["node"] == "agent_query_rewrite"
    )
    assert skipped["status"] == "skipped"
    assert skipped["result"]["reason_code"] == "runtime_soft_limit"
