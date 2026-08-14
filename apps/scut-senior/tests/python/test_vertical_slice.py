from __future__ import annotations

import json
from pathlib import Path
from shutil import copytree

import pytest
from fastapi.testclient import TestClient

from scut_senior_api.adapters.mock import (
    FixtureBilibiliCatalog,
    FixtureContractViolation,
    FixtureRetrievalGateway,
)
from scut_senior_api.config import Settings
from scut_senior_api.main import create_app
from scut_senior_api.paths import FIXTURE_ROOT
from scut_senior_api.ports import RetrievedSource
from scut_senior_api.registry import CourseRegistry


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
        "include_bilibili_resources": True,
        "context_refs": [],
        "attachments": [],
        "workflow_payload": {"question": "请解释矩阵的秩"},
    }


def test_mock_vertical_slice_persists_answer_sources_and_trace(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "vertical-slice.db"
    settings = Settings(app_env="test", database_path=database_path)
    client = TestClient(create_app(settings))

    conversation_response = client.post(
        "/api/v1/conversations", json={"course_id": "线性代数"}
    )
    assert conversation_response.status_code == 201
    conversation = conversation_response.json()

    run_response = client.post(
        "/api/v1/workflow-runs",
        json=workflow_request(conversation["conversation_id"]),
    )
    assert run_response.status_code == 201, run_response.text
    result = run_response.json()
    assert result["run_status"] == "completed"
    assert result["answer_status"] == "answered"
    assert result["evidence_status"] == "sufficient"
    assert result["model"]["mock_only"] is True
    assert result["availability_status"] == "mock_only"
    assert result["citations"]
    assert result["citations"][0]["course_id"] == "linear_algebra"
    assert result["citations"][0]["course_title"] == "线性代数"
    assert result["citations"][0]["source_title"] == "合成线性代数页码题目"
    assert all(resource["platform"] == "bilibili" for resource in result["external_resources"])
    assert all("url" not in citation for citation in result["citations"])
    assert [event["sequence"] for event in result["trace"]] == list(
        range(len(result["trace"]))
    )
    assert result["trace"][-1]["node"] == "persistence"
    assert all("user_id" not in event["result"] for event in result["trace"])
    identity_event = next(
        event for event in result["trace"] if event["node"] == "mock_identity"
    )
    assert identity_event["result"] == {"mode": "mock"}

    restarted_client = TestClient(create_app(settings))
    restored = restarted_client.get(
        f"/api/v1/conversations/{conversation['conversation_id']}"
    )
    assert restored.status_code == 200
    restored_runs = restored.json()["runs"]
    assert len(restored_runs) == 1
    assert restored_runs[0] == result

    restored_run = restarted_client.get(
        f"/api/v1/workflow-runs/{result['workflow_run_id']}"
    )
    assert restored_run.status_code == 200
    assert restored_run.json() == result


def test_course_only_never_returns_bilibili_fixture(tmp_path: Path) -> None:
    client = TestClient(
        create_app(Settings(app_env="test", database_path=tmp_path / "course-only.db"))
    )
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    request = workflow_request(conversation["conversation_id"])
    request["knowledge_scope"] = "course_only"
    request["include_bilibili_resources"] = True

    result = client.post("/api/v1/workflow-runs", json=request)

    assert result.status_code == 201
    assert result.json()["external_resources"] == []
    bilibili_event = next(
        event
        for event in result.json()["trace"]
        if event["node"] == "bilibili_fixture_match"
    )
    assert bilibili_event["status"] == "skipped"


def test_unconfirmed_capabilities_fail_closed(tmp_path: Path) -> None:
    client = TestClient(
        create_app(Settings(app_env="test", database_path=tmp_path / "closed.db"))
    )
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    request = workflow_request(conversation["conversation_id"])
    request["model_source"] = "user_key"
    request["provider_id"] = "unconfirmed-provider"

    result = client.post("/api/v1/workflow-runs", json=request)

    assert result.status_code == 503
    assert result.json()["error"]["capability"] == "user_key"


def test_non_fixture_course_stays_closed(tmp_path: Path) -> None:
    client = TestClient(
        create_app(Settings(app_env="test", database_path=tmp_path / "courses.db"))
    )

    response = client.post(
        "/api/v1/conversations", json={"course_id": "probability_theory"}
    )

    assert response.status_code == 503
    assert response.json()["error"]["capability"] == "course"


def test_mock_retrieval_fails_closed_when_fixture_contract_is_invalid(
    tmp_path: Path,
) -> None:
    broken_root = tmp_path / "corpus"
    copytree(FIXTURE_ROOT / "corpus", broken_root)
    markdown = broken_root / "linear_algebra" / "synthetic-linear-algebra-exam.md"
    markdown.write_text(
        markdown.read_text(encoding="utf-8").replace(
            "title: 合成线性代数页码题目", "title: 与 manifest 不一致"
        ),
        encoding="utf-8",
    )
    gateway = FixtureRetrievalGateway(CourseRegistry.load(), broken_root)

    with pytest.raises(FixtureContractViolation, match="failed validation"):
        gateway.search(["linear_algebra"], "矩阵的秩")


def test_bilibili_runtime_rejects_a_non_fixture_catalog(tmp_path: Path) -> None:
    payload = json.loads(
        (FIXTURE_ROOT / "bilibili" / "catalog.json").read_text(encoding="utf-8")
    )
    payload["fixture_only"] = False
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(FixtureContractViolation, match="failed validation"):
        FixtureBilibiliCatalog(catalog_path)


def test_source_authorization_guard_runs_before_model_call(tmp_path: Path) -> None:
    app = create_app(
        Settings(app_env="test", database_path=tmp_path / "source-guard.db")
    )
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()

    class CrossCourseRetrieval:
        def search(self, course_ids: list[str], query: str) -> list[RetrievedSource]:
            del course_ids, query
            return [
                RetrievedSource(
                    chunk_id="cross-course:p1:c01",
                    course_id="probability_theory",
                    source_id="cross-course",
                    source_title="不应进入模型的越权来源",
                    text="不应发送给模型",
                    locator_type="page",
                    locator_start=1,
                    locator_end=1,
                    question_id=None,
                    heading_path=(),
                )
            ]

    class ModelCallSpy:
        called = False

        def generate(self, request, sources):
            del request, sources
            self.called = True
            raise AssertionError("model must not receive an unauthorized source")

    spy = ModelCallSpy()
    app.state.service.retrieval = CrossCourseRetrieval()
    app.state.service.model = spy

    response = client.post(
        "/api/v1/workflow-runs",
        json=workflow_request(conversation["conversation_id"]),
    )

    assert response.status_code == 409
    assert "source authorization guard" in response.json()["error"]["detail"]
    assert spy.called is False
