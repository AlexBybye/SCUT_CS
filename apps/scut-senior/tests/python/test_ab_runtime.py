from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

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


def test_model_decision_mode_does_not_call_decision_model_on_fixed_path(
    tmp_path: Path,
) -> None:
    app = create_app(
        Settings(
            app_env="test",
            database_path=tmp_path / "ab.db",
            agent_decision_mode="model",
        )
    )
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()

    response = client.post(
        "/api/v1/workflow-runs",
        json=_request(conversation["conversation_id"]),
    )
    assert response.status_code == 201, response.text
    result = response.json()
    model_event = next(
        event
        for event in result["trace"]
        if event["node"] == "mock_model"
    )
    metrics = model_event["result"]
    assert metrics["decision_call_count"] == 0
    assert metrics["answer_call_count"] == 1
    assert metrics["provider_retry_count"] == 0
    assert metrics["guard_retry_count"] == 0
    agent_events = app.state.repository.list_agent_events(result["workflow_run_id"])
    assert [event["kind"] for event in agent_events] == [
        "decision_produced",
        "action_executed",
        "observation_recorded",
        "decision_produced",
        "action_executed",
        "observation_recorded",
        "run_finished",
    ]
    assert [
        event.get("action")
        for event in agent_events
        if event["kind"] == "action_executed"
    ] == ["retrieve", "generate_answer"]


class _SequenceRetrieval:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.source = RetrievedSource(
            chunk_id="linear_algebra:ab:p1",
            course_id="linear_algebra",
            source_id="ab-source",
            source_title="AB 测试资料",
            text="矩阵的秩可以由初等行变换求得。",
            locator_type="page",
            locator_start=1,
            locator_end=1,
            question_id=None,
            heading_path=(),
        )

    def is_course_available(self, course_id: str) -> bool:
        return course_id == "linear_algebra"

    def search(self, course_ids: list[str], query: str) -> RetrievalBatch:
        self.calls.append(query)
        # First run seeds conversation history. The second run has an empty
        # primary query; an invalid model action falls back to the server's
        # expected rewrite action.
        if len(self.calls) == 1:
            return RetrievalBatch((self.source,), "ab-corpus", "ab-pack")
        return RetrievalBatch((), "ab-corpus", "ab-pack")


class _RejectRewriteDecision:
    def __init__(self) -> None:
        self.phases: list[str] = []

    def decide(self, request, state, phase, *, sources=(), history=()):
        self.phases.append(phase)
        return "generate_answer"


def test_rejected_query_rewrite_falls_back_to_server_owned_action(tmp_path: Path) -> None:
    app = create_app(
        Settings(
            app_env="test",
            database_path=tmp_path / "ab-reject.db",
            agent_decision_mode="model",
            retrieval_mode="local_corpus",
        )
    )
    retrieval = _SequenceRetrieval()
    app.state.service.retrieval = retrieval
    decision = _RejectRewriteDecision()
    app.state.service.agent_decision = decision
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    conversation_id = conversation["conversation_id"]

    first = client.post(
        "/api/v1/workflow-runs", json=_request(conversation_id)
    )
    assert first.status_code == 201, first.text
    second_payload = _request(conversation_id)
    second_payload["user_input"] = "再讲一遍"
    second_payload["workflow_payload"] = {"question": "再讲一遍"}
    second = client.post("/api/v1/workflow-runs", json=second_payload)
    assert second.status_code == 201, second.text

    assert len(retrieval.calls) == 3
    assert decision.phases == ["retrieve_with_query_rewrite"]
    model_event = next(
        event for event in second.json()["trace"] if event["node"] == "mock_model"
    )
    assert model_event["result"]["decision_call_count"] == 1
    assert model_event["result"]["action_rejection_count"] == 1
