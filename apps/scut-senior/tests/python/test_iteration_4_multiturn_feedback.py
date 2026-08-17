from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from scut_senior_api.config import Settings
from scut_senior_api.main import create_app


def workflow_request(conversation_id: str) -> dict[str, object]:
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


def _app_client(tmp_path: Path) -> tuple[object, TestClient]:
    settings = Settings(app_env="test", database_path=tmp_path / "slice.db")
    app = create_app(settings)
    return app, TestClient(app)


def _run(client: TestClient, conversation_id: str) -> dict[str, object]:
    response = client.post(
        "/api/v1/workflow-runs", json=workflow_request(conversation_id)
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_second_run_receives_prior_turns_as_model_history(tmp_path: Path) -> None:
    _, client = _app_client(tmp_path)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    conversation_id = conversation["conversation_id"]

    first = _run(client, conversation_id)
    assert "历史消息" not in first["repository_answer"]

    second = _run(client, conversation_id)
    # The first completed attempt contributes one user turn and one assistant
    # turn; the deterministic Mock reports how many turns it received.
    assert "已接收 2 条历史消息" in second["repository_answer"]
    assert second["run_status"] == "completed"
    # History must never change the bound course or workflow.
    assert second["course_ids"] == ["linear_algebra"]
    assert second["workflow_type"] == "knowledge_qa"


def test_feedback_submit_list_and_ownership(tmp_path: Path) -> None:
    _, client = _app_client(tmp_path)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    result = _run(client, conversation["conversation_id"])
    run_id = result["workflow_run_id"]

    created = client.post(
        "/api/v1/feedback",
        json={
            "run_id": run_id,
            "feedback_type": "knowledge_error",
            "note": "  第三行有误  ",
        },
    )
    assert created.status_code == 201, created.text
    record = created.json()
    assert record["feedback_type"] == "knowledge_error"
    assert record["note"] == "第三行有误"
    assert record["course_id"] == "linear_algebra"
    assert record["workflow_type"] == "knowledge_qa"
    assert record["answer_status"] == "answered"
    assert record["run_id"] == run_id

    listed = client.get("/api/v1/feedback")
    assert listed.status_code == 200
    assert [item["feedback_id"] for item in listed.json()] == [record["feedback_id"]]

    # Feedback on an unknown run must not silently attach to anything.
    missing = client.post(
        "/api/v1/feedback",
        json={"run_id": str(uuid4()), "feedback_type": "helpful"},
    )
    assert missing.status_code == 404

    # Invalid feedback type and overlong note are rejected by the contract.
    invalid = client.post(
        "/api/v1/feedback",
        json={"run_id": run_id, "feedback_type": "spam"},
    )
    assert invalid.status_code == 422

    blank_note = client.post(
        "/api/v1/feedback",
        json={"run_id": run_id, "feedback_type": "not_helpful", "note": "   "},
    )
    assert blank_note.status_code == 201
    assert blank_note.json()["note"] is None
