from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from scut_senior_api.config import Settings
from scut_senior_api.contracts import (
    AnswerBlock,
    AnswerBlockType,
    WorkflowRunRequest,
)
from scut_senior_api.main import (
    MAX_BUFFERED_REQUEST_MESSAGES,
    MAX_REQUEST_BODY_BYTES,
    _RequestBodyLimitMiddleware,
    create_app,
)
from scut_senior_api.ports import GeneratedAnswer, RetrievedSource, UserIdentity
from scut_senior_api.runtime_guards import (
    RuntimeGuardError,
    build_guarded_answer,
    normalize_topics,
    protect_humanizer_output,
)
from scut_senior_api.workflow_stream import WorkflowStreamSession


def _request(conversation_id: str, *, knowledge_scope: str = "course_first") -> dict[str, object]:
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
        "knowledge_scope": knowledge_scope,
        "include_bilibili_resources": False,
        "context_refs": [],
        "attachments": [],
        "workflow_payload": {"question": "请解释矩阵的秩"},
    }


def _source(*, course_id: str = "linear_algebra") -> RetrievedSource:
    return RetrievedSource(
        chunk_id=f"{course_id}:p1:c01",
        course_id=course_id,
        source_id=f"{course_id}-source",
        source_title="审核资料",
        text="矩阵的秩可以由初等行变换求得。",
        locator_type="page",
        locator_start=1,
        locator_end=1,
        question_id=None,
        heading_path=(),
    )


def _validated_request(knowledge_scope: str = "course_first") -> WorkflowRunRequest:
    return WorkflowRunRequest.model_validate(_request("11111111-1111-1111-1111-111111111111", knowledge_scope=knowledge_scope))


@pytest.mark.parametrize(
    "answer",
    [
        GeneratedAnswer("回答 [S999]。", citation_ids=("S999",)),
        GeneratedAnswer("回答 [S1]。", citation_ids=("S1", "S1")),
        GeneratedAnswer(
            "回答。",
            citation_ids=(),
            general_supplement="延伸 https://www.bilibili.com/video/BV1bad",
        ),
    ],
)
def test_citation_guard_rejects_unknown_duplicate_and_bilibili_model_output(
    answer: GeneratedAnswer,
) -> None:
    with pytest.raises(RuntimeGuardError):
        build_guarded_answer(
            request=_validated_request(),
            answer=answer,
            sources=[_source()],
            course_ids={"linear_algebra"},
        )


def test_course_only_never_accepts_a_general_answer_block() -> None:
    with pytest.raises(RuntimeGuardError, match="general"):
        build_guarded_answer(
            request=_validated_request("course_only"),
            answer=GeneratedAnswer(
                repository_answer="资料说明 [S1]。",
                citation_ids=("S1",),
                general_supplement="模型通用补充。",
            ),
            sources=[_source()],
            course_ids={"linear_algebra"},
        )


def test_course_only_drops_uncited_repository_text_instead_of_showing_it() -> None:
    guarded = build_guarded_answer(
        request=_validated_request("course_only"),
        answer=GeneratedAnswer(repository_answer="没有引用支撑的模型正文。"),
        sources=[_source()],
        course_ids={"linear_algebra"},
    )

    assert guarded.blocks == ()
    assert guarded.answer_status.value == "insufficient_evidence"
    assert guarded.evidence_status.value == "insufficient"


def test_topic_normalization_preserves_words_while_cleaning_controls() -> None:
    assert normalize_topics(("  矩阵\x00\n  的秩  ", "ＭＡＴＲＩＸ", "matrix")) == (
        "矩阵 的秩",
        "MATRIX",
    )


@pytest.mark.parametrize(
    "changed",
    [
        "矩阵秩为 4，公式 $A^4=I$，见 [S1]。",
        "矩阵阶为 3，公式 $A^3=I$，见 [S1]。",
        "矩阵秩为 3，公式 $A^2=I$，见 [S1]。",
        "矩阵秩为 3，公式 $A^3=I$，见 [S2]。",
    ],
)
def test_humanizer_falls_back_when_number_term_formula_or_citation_changes(
    changed: str,
) -> None:
    original = [
        AnswerBlock(
            type=AnswerBlockType.REPOSITORY,
            content="矩阵秩为 3，公式 $A^3=I$，见 [S1]。",
        )
    ]
    outcome = protect_humanizer_output(
        original=original,
        candidate=[
            AnswerBlock(type=AnswerBlockType.REPOSITORY, content=changed)
        ],
        protected_terms=("矩阵秩",),
    )

    assert outcome.fallback is True
    assert list(outcome.blocks) == original


def test_runtime_retries_the_same_model_once_after_citation_guard_rejection(
    tmp_path: Path,
) -> None:
    app = create_app(Settings(app_env="test", database_path=tmp_path / "retry.db"))
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()

    class ScriptedModel:
        def __init__(self) -> None:
            self.calls = 0

        def generate(self, request, sources, history=()):
            del request, sources, history
            self.calls += 1
            citation_id = "S999" if self.calls == 1 else "S1"
            return GeneratedAnswer(
                repository_answer=f"矩阵秩的回答 [{citation_id}]。",
                citation_ids=(citation_id,),
                related_topics=("矩阵秩",),
            )

    model = ScriptedModel()
    app.state.service.model = model
    response = client.post(
        "/api/v1/workflow-runs",
        json=_request(conversation["conversation_id"]),
    )

    assert response.status_code == 201, response.text
    assert model.calls == 2
    result = response.json()
    assert [item["citation_id"] for item in result["citations"]] == ["S1"]
    retry = next(item for item in result["trace"] if item["node"] == "model_output_retry")
    assert retry["result"] == {
        "retry_count": 1,
        "failure_code": "model_output_guard_rejected",
    }


def test_ndjson_endpoint_uses_one_run_and_omits_null_payload_siblings(
    tmp_path: Path,
) -> None:
    app = create_app(Settings(app_env="test", database_path=tmp_path / "stream.db"))
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()

    response = client.post(
        "/api/v1/workflow-runs/stream",
        json=_request(conversation["conversation_id"]),
    )

    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("application/x-ndjson")
    events = [json.loads(line) for line in response.text.splitlines() if line]
    assert [event["sequence"] for event in events] == list(range(len(events)))
    run_ids = {event["workflow_run_id"] for event in events}
    assert len(run_ids) == 1
    assert events[-1]["kind"] == "result"
    assert events[-1]["result"]["run_status"] == "completed"
    assert events[-1]["result"]["general_supplement"] is None
    assert events[-1]["result"]["course_pack_version"] is None
    payload_key = {
        "trace": "trace_event",
        "answer_delta": "answer_delta",
        "result": "result",
        "error": "error",
    }
    for event in events:
        assert set(event) == {
            "kind",
            "workflow_run_id",
            "sequence",
            payload_key[event["kind"]],
        }


def test_health_reports_iteration_three_without_claiming_active_corpus(
    tmp_path: Path,
) -> None:
    app = create_app(
        Settings(app_env="test", database_path=tmp_path / "health.db")
    )
    response = TestClient(app).get("/api/v1/health")

    assert response.status_code == 200
    health = response.json()
    assert health["iteration"] == 3
    assert health["iteration_status"] == (
        "local_fixture_runtime_active_corpus_required"
    )
    assert health["formal_exit_blocked"] is True
    assert health["capabilities"] | {
        "workflow_runtime": True,
        "workflow_stream_ndjson": True,
        "citation_guard": True,
        "response_style_control": True,
        "humanizer_guard": True,
        "humanizer_configured": False,
        "active_corpus_configured": False,
    } == health["capabilities"]


def test_api_rejects_an_oversized_body_before_json_or_workflow_parsing(
    tmp_path: Path,
) -> None:
    app = create_app(Settings(app_env="test", database_path=tmp_path / "body-limit.db"))
    client = TestClient(app)
    oversized = b'{"padding":"' + (b"x" * MAX_REQUEST_BODY_BYTES) + b'"}'

    response = client.post(
        "/api/v1/workflow-runs",
        content=oversized,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 413
    assert response.json() == {
        "error": {
            "code": "request_body_too_large",
            "detail": "请求内容过大，请缩短后重试。",
        }
    }
    assert response.headers["cache-control"] == "private, no-store"


def test_api_rejects_an_oversized_multichunk_body_without_content_length(
    tmp_path: Path,
) -> None:
    app = create_app(
        Settings(app_env="test", database_path=tmp_path / "chunked-body-limit.db")
    )
    chunks = [
        {
            "type": "http.request",
            "body": b"x" * (MAX_REQUEST_BODY_BYTES // 2),
            "more_body": True,
        },
        {
            "type": "http.request",
            "body": b"x" * (MAX_REQUEST_BODY_BYTES // 2),
            "more_body": True,
        },
        {"type": "http.request", "body": b"x", "more_body": False},
    ]
    sent = []

    async def receive():
        return chunks.pop(0)

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/workflow-runs",
        "raw_path": b"/api/v1/workflow-runs",
        "query_string": b"",
        "headers": [(b"content-type", b"application/json")],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }

    asyncio.run(app(scope, receive, send))

    response_start = next(
        message for message in sent if message["type"] == "http.response.start"
    )
    response_body = b"".join(
        message.get("body", b"")
        for message in sent
        if message["type"] == "http.response.body"
    )
    assert response_start["status"] == 413
    assert json.loads(response_body) == {
        "error": {
            "code": "request_body_too_large",
            "detail": "请求内容过大，请缩短后重试。",
        }
    }
    assert chunks == []


def test_body_limit_bounds_buffering_for_excessive_empty_request_chunks() -> None:
    request_chunk_count = 0
    sent = []

    async def unexpected_downstream(scope, receive, send):
        raise AssertionError("excessively fragmented body reached the application")

    middleware = _RequestBodyLimitMiddleware(
        unexpected_downstream,
        max_body_bytes=MAX_REQUEST_BODY_BYTES,
    )

    async def receive():
        nonlocal request_chunk_count
        request_chunk_count += 1
        return {"type": "http.request", "body": b"", "more_body": True}

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/workflow-runs",
        "raw_path": b"/api/v1/workflow-runs",
        "query_string": b"",
        "headers": [(b"content-type", b"application/json")],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }

    asyncio.run(middleware(scope, receive, send))

    response_start = next(
        message for message in sent if message["type"] == "http.response.start"
    )
    assert response_start["status"] == 413
    assert request_chunk_count == MAX_BUFFERED_REQUEST_MESSAGES + 1


def test_api_accepts_maximum_chinese_user_input_and_material_text(
    tmp_path: Path,
) -> None:
    app = create_app(
        Settings(app_env="test", database_path=tmp_path / "large-valid-body.db")
    )
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    request = _request(conversation["conversation_id"])
    request.update(
        {
            "workflow_type": "temporary_material_reading",
            "user_input": "问" * 100_000,
            "workflow_payload": {
                "material_title": "矩阵材料",
                "material_text": "矩" * 100_000,
                "reading_goal": None,
            },
        }
    )

    response = client.post("/api/v1/workflow-runs", json=request)

    assert response.status_code == 201, response.text


def test_invalid_multiple_bilibili_entries_degrade_without_blocking_answer(
    tmp_path: Path,
) -> None:
    app = create_app(Settings(app_env="test", database_path=tmp_path / "bili.db"))
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    original = app.state.service.resources

    class InvalidDiscovery:
        def discover(self, **kwargs):
            one = original.discover(**kwargs)
            return one + one

    app.state.service.resources = InvalidDiscovery()
    request = _request(conversation["conversation_id"])
    request["include_bilibili_resources"] = True
    response = client.post("/api/v1/workflow-runs", json=request)

    assert response.status_code == 201, response.text
    assert response.json()["external_resources"] == []
    event = next(
        item
        for item in response.json()["trace"]
        if item["node"] == "bilibili_link_discovery"
    )
    assert event["status"] == "failed"


def test_pre_cancelled_stream_persists_an_interrupted_run(tmp_path: Path) -> None:
    app = create_app(
        Settings(app_env="test", database_path=tmp_path / "interrupted.db")
    )
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    events = []
    session = WorkflowStreamSession(events.append)
    session.cancel()

    result = app.state.service.run_stream(
        UserIdentity(
            user_id="mock-user-iteration-0",
            display_name="Iteration 0 Mock User",
            is_mock=True,
        ),
        WorkflowRunRequest.model_validate(_request(conversation["conversation_id"])),
        session,
    )

    assert result.run_status.value == "interrupted"
    assert events[-1].kind == "result"
    restored = client.get(f"/api/v1/workflow-runs/{result.workflow_run_id}")
    assert restored.status_code == 200
    assert restored.json()["run_status"] == "interrupted"
