from __future__ import annotations

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from scut_senior_api.adapters.bilibili import BilibiliLinkDiscoveryAdapter
from scut_senior_api.config import Settings
from scut_senior_api.contracts import (
    AnswerBlock,
    AnswerBlockType,
    AnswerStatus,
    EvidenceStatus,
    RunStatus,
    Tone,
    TraceEvent,
    WorkflowRunRequest,
)
from scut_senior_api.main import create_app
from scut_senior_api.ports import GeneratedAnswer, RetrievedSource, UserIdentity
from scut_senior_api.runtime_guards import (
    RuntimeGuardError,
    build_guarded_answer,
    protect_humanizer_output,
)
from scut_senior_api.workflow_focus import build_tone_visible_callout
from scut_senior_api.workflow_stream import WorkflowStreamSession


CONVERSATION_ID = "11111111-1111-1111-1111-111111111111"


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

WORKFLOW_FOCUS_EXPECTATIONS: dict[str, dict[str, object]] = {
    "knowledge_qa": {
        "strategy": "question_concept",
        "topics": ["矩阵", "线性方程组"],
        "keywords": ["矩阵的秩", "初等行变换"],
    },
    "exam_review": {
        "strategy": "syllabus_weak_topics",
        "topics": ["复习大纲", "初等行变换"],
        "keywords": ["初等行变换复习", "矩阵复习"],
    },
    "problem_tutor": {
        "strategy": "problem_main_topic",
        "topics": ["矩阵题主知识点"],
        "keywords": ["矩阵秩题目"],
    },
    "mistake_review": {
        "strategy": "mistake_root_cause",
        "topics": ["矩阵概念错误根因"],
        "keywords": ["矩阵秩错误原因"],
    },
    "temporary_material_reading": {
        "strategy": "material_title_main_topics",
        "topics": ["临时材料主要知识点"],
        "keywords": ["矩阵材料精读"],
    },
}

OBFUSCATED_BILIBILI_URLS = (
    "https://www。bilibili。com/video/BV1unsafe",
    "https://bilibili｡com/video/BV1unsafe",
    "https://www%2Ebilibili%2Ecom/video/BV1unsafe",
    "https://www%E3%80%82bilibili%E3%80%82com/video/BV1unsafe",
    "https%3A%2F%2Fwww%252Ebilibili%252Ecom/video/BV1unsafe",
    "https://www.bili\u034fbili.com/video/BV1unsafe",
    "https://b2\u034f3.tv/BV1unsafe",
    "https://www.bili\u180bbili.com/video/BV1unsafe",
    "https://www.bili\ufe0fbili.com/video/BV1unsafe",
    "https://www.bili\u115fbili.com/video/BV1unsafe",
)


def _request_dict(
    conversation_id: str = CONVERSATION_ID,
    *,
    workflow_type: str = "knowledge_qa",
    knowledge_scope: str = "course_first",
) -> dict[str, object]:
    return {
        "workflow_type": workflow_type,
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
        "workflow_payload": WORKFLOW_PAYLOADS[workflow_type],
    }


def _request(
    *,
    workflow_type: str = "knowledge_qa",
    knowledge_scope: str = "course_first",
) -> WorkflowRunRequest:
    return WorkflowRunRequest.model_validate(
        _request_dict(
            workflow_type=workflow_type,
            knowledge_scope=knowledge_scope,
        )
    )


def _source(
    *,
    course_id: str = "linear_algebra",
    suffix: str = "one",
) -> RetrievedSource:
    return RetrievedSource(
        chunk_id=f"{course_id}:p1:{suffix}",
        course_id=course_id,
        source_id=f"{course_id}-{suffix}",
        source_title=f"{course_id} 审核资料",
        text="矩阵的秩可以由初等行变换求得。",
        locator_type="page",
        locator_start=1,
        locator_end=1,
        question_id=None,
        heading_path=(),
    )


@pytest.mark.parametrize(
    ("answer", "sources", "message"),
    [
        (
            GeneratedAnswer("越界引用 [S999]。", citation_ids=("S999",)),
            [_source()],
            "候选范围",
        ),
        (
            GeneratedAnswer("重复引用 [S1]。", citation_ids=("S1", "S1")),
            [_source()],
            "重复",
        ),
        (
            GeneratedAnswer("跨课程引用 [S2]。", citation_ids=("S2",)),
            [
                _source(suffix="allowed"),
                _source(course_id="probability_theory", suffix="foreign"),
            ],
            "候选范围",
        ),
        (
            GeneratedAnswer(
                "不要返回具体视频 https://www.bilibili.com/video/BV1unsafe 。"
            ),
            [_source()],
            "URL",
        ),
    ],
)
def test_runtime_guard_rejects_untrusted_model_references(
    answer: GeneratedAnswer,
    sources: list[RetrievedSource],
    message: str,
) -> None:
    with pytest.raises(RuntimeGuardError, match=message):
        build_guarded_answer(
            request=_request(),
            answer=answer,
            sources=sources,
            course_ids={"linear_algebra"},
        )


@pytest.mark.parametrize("unsafe_url", OBFUSCATED_BILIBILI_URLS)
def test_runtime_guard_rejects_canonicalized_bilibili_urls(
    unsafe_url: str,
) -> None:
    with pytest.raises(RuntimeGuardError, match="URL"):
        build_guarded_answer(
            request=_request(),
            answer=GeneratedAnswer("", general_supplement=f"延伸阅读：{unsafe_url}"),
            sources=[],
            course_ids={"linear_algebra"},
        )


@pytest.mark.parametrize(
    ("workflow_type", "answer", "expected_type"),
    [
        (
            "knowledge_qa",
            GeneratedAnswer("课程资料回答 [S1]。", citation_ids=("S1",)),
            AnswerBlockType.REPOSITORY,
        ),
        (
            "knowledge_qa",
            GeneratedAnswer("", general_supplement="通用知识补充。"),
            AnswerBlockType.GENERAL,
        ),
        (
            "temporary_material_reading",
            GeneratedAnswer("", user_material_answer="临时材料解读。"),
            AnswerBlockType.USER_MATERIAL,
        ),
        (
            "exam_review",
            GeneratedAnswer("", personalized_analysis="个性化复习建议。"),
            AnswerBlockType.PERSONALIZED_ANALYSIS,
        ),
    ],
)
def test_guard_builds_each_answer_block_only_in_an_allowed_workflow(
    workflow_type: str,
    answer: GeneratedAnswer,
    expected_type: AnswerBlockType,
) -> None:
    guarded = build_guarded_answer(
        request=_request(workflow_type=workflow_type),
        answer=answer,
        sources=[_source()],
        course_ids={"linear_algebra"},
    )

    assert [block.type for block in guarded.blocks] == [expected_type]


def test_course_only_rejects_general_answer_even_with_a_valid_course_citation() -> None:
    with pytest.raises(RuntimeGuardError, match="general"):
        build_guarded_answer(
            request=_request(knowledge_scope="course_only"),
            answer=GeneratedAnswer(
                "课程资料回答 [S1]。",
                citation_ids=("S1",),
                general_supplement="不应出现的通用补充。",
            ),
            sources=[_source()],
            course_ids={"linear_algebra"},
        )


def test_course_only_without_a_citation_drops_repository_content() -> None:
    guarded = build_guarded_answer(
        request=_request(knowledge_scope="course_only"),
        answer=GeneratedAnswer("没有任何来源支撑的课程资料结论。"),
        sources=[_source()],
        course_ids={"linear_algebra"},
    )

    assert guarded.blocks == ()
    assert guarded.answer_status == AnswerStatus.INSUFFICIENT_EVIDENCE
    assert guarded.evidence_status == EvidenceStatus.INSUFFICIENT


@pytest.mark.parametrize(
    "candidate_content",
    [
        "矩阵秩为 4，公式 $A^3=I$，见 [S1]。",
        "矩阵秩为 3，公式 $A^2=I$，见 [S1]。",
        "矩阵阶为 3，公式 $A^3=I$，见 [S1]。",
        "矩阵秩为 3，公式 $A^3=I$，见 [S2]。",
    ],
    ids=["number", "formula", "term", "citation"],
)
def test_humanizer_falls_back_on_any_protected_content_change(
    candidate_content: str,
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
            AnswerBlock(
                type=AnswerBlockType.REPOSITORY,
                content=candidate_content,
            )
        ],
        protected_terms=("矩阵秩",),
    )

    assert outcome.applied is False
    assert outcome.fallback is True
    assert outcome.reason == "protected_content_changed"
    assert list(outcome.blocks) == original


@pytest.mark.parametrize(
    ("original_content", "candidate_content"),
    [
        ("公式 A^3=I，见 [S1]。", "公式 B^3=I，见 [S1]。"),
        ("矩阵可逆，见 [S1]。", "矩阵不可逆，见 [S1]。"),
        ("计算 x-y，见 [S1]。", "计算 xy，见 [S1]。"),
        ("代码：\n    return x\n见 [S1]。", "代码：\nreturn x\n见 [S1]。"),
    ],
    ids=["plain_formula", "negation", "operator", "code_indentation"],
)
def test_humanizer_fails_closed_on_unverified_text_change(
    original_content: str,
    candidate_content: str,
) -> None:
    original = [
        AnswerBlock(type=AnswerBlockType.REPOSITORY, content=original_content)
    ]

    outcome = protect_humanizer_output(
        original=original,
        candidate=[
            AnswerBlock(
                type=AnswerBlockType.REPOSITORY,
                content=candidate_content,
            )
        ],
        protected_terms=(),
    )

    assert outcome.applied is False
    assert outcome.fallback is True
    assert outcome.reason == "unverified_text_change"
    assert list(outcome.blocks) == original


def test_identical_humanizer_output_is_no_change_not_applied() -> None:
    original = [
        AnswerBlock(
            type=AnswerBlockType.REPOSITORY,
            content="矩阵可逆，见 [S1]。",
        )
    ]

    outcome = protect_humanizer_output(
        original=original,
        candidate=[block.model_copy(deep=True) for block in original],
        protected_terms=("矩阵",),
    )

    assert outcome.applied is False
    assert outcome.fallback is False
    assert outcome.reason == "no_change"


@pytest.mark.parametrize(
    "unsafe_url",
    [
        "https://www.bilibili.com/video/BV1unsafe",
        "//www.bilibili.com/video/BV1unsafe",
        "bilibili.com/video/BV1unsafe",
        "b23.tv/BV1unsafe",
        "https://search.bilibili.com/all?keyword=矩阵",
        *OBFUSCATED_BILIBILI_URLS,
    ],
)
def test_humanizer_cannot_inject_a_bilibili_link(unsafe_url: str) -> None:
    original = [
        AnswerBlock(
            type=AnswerBlockType.REPOSITORY,
            content="矩阵秩为 3，见 [S1]。",
        )
    ]

    outcome = protect_humanizer_output(
        original=original,
        candidate=[
            AnswerBlock(
                type=AnswerBlockType.REPOSITORY,
                content=f"矩阵秩为 3，见 [S1]。\n{unsafe_url}",
            )
        ],
        protected_terms=("矩阵秩",),
    )

    assert outcome.fallback is True
    assert outcome.reason == "unsafe_link_added"
    assert list(outcome.blocks) == original


def test_runtime_rejects_in_place_humanizer_mutation(tmp_path: Path) -> None:
    class ScriptedModel:
        def generate(self, request, sources, history=()):
            del request, sources, history
            return GeneratedAnswer(
                repository_answer="矩阵可逆，见 [S1]。",
                related_topics=("矩阵",),
                citation_ids=("S1",),
            )

    class InPlaceMutatingHumanizer:
        def humanize(self, *, blocks, protected_terms):
            del protected_terms
            blocks[0].content = blocks[0].content.replace("可逆", "不可逆")
            return blocks

    app = create_app(
        Settings(app_env="test", database_path=tmp_path / "mutating-humanizer.db"),
        humanizer=InPlaceMutatingHumanizer(),
    )
    app.state.service.model = ScriptedModel()
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()

    response = client.post(
        "/api/v1/workflow-runs",
        json=_request_dict(conversation["conversation_id"]),
    )

    assert response.status_code == 201, response.text
    result = response.json()
    assert result["answer_blocks"][0]["type"] == "repository"
    assert result["answer_blocks"][0]["content"].startswith("矩阵可逆，见 [S1]。")
    assert result["answer_blocks"][0]["content"].count(
        build_tone_visible_callout(Tone.TEACHING_ASSISTANT)
    ) == 1
    humanizer_event = next(
        event for event in result["trace"] if event["node"] == "humanizer"
    )
    assert humanizer_event["result"] == {
        "reason_code": "humanizer_protected_fallback",
        "degradation_code": "humanizer_unverified_text_change",
    }


def test_runtime_enforces_the_selected_visible_tone_contract(tmp_path: Path) -> None:
    class ScriptedModel:
        def generate(self, request, sources, history=()):
            del request, sources, history
            return GeneratedAnswer(
                repository_answer=(
                    "## 结论\n\n矩阵的秩可由主元个数判断 [S1]。\n\n"
                    "## 要点\n\n- 非零行的数量给出秩。"
                ),
                citation_ids=("S1",),
            )

    app = create_app(
        Settings(app_env="test", database_path=tmp_path / "tone-contract.db")
    )
    app.state.service.model = ScriptedModel()
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    request_payload = _request_dict(conversation["conversation_id"])
    request_payload["answer_mode"] = "concise"
    request_payload["tone"] = "study_partner"

    response = client.post("/api/v1/workflow-runs", json=request_payload)

    assert response.status_code == 201, response.text
    content = response.json()["answer_blocks"][0]["content"]
    callout = build_tone_visible_callout(Tone.STUDY_PARTNER)
    assert content.count(callout) == 1
    assert content.index("## 结论") < content.index(callout) < content.index("## 要点")


def test_model_suggestions_cannot_leak_bilibili_urls_or_text_into_trace(
    tmp_path: Path,
) -> None:
    private_topic_marker = "错答正文私人标记不应写入Trace"

    class ScriptedModel:
        def generate(self, request, sources, history=()):
            del request, sources, history
            return GeneratedAnswer(
                repository_answer="矩阵秩回答 [S1]。",
                citation_ids=("S1",),
                related_topics=(
                    "https://www。bilibili。com/video/BV1leak",
                    "伪造来源 [S999]",
                    private_topic_marker,
                ),
                related_questions=("去看 b23.tv/BV1leak", "如何计算矩阵秩？"),
            )

    app = create_app(
        Settings(app_env="test", database_path=tmp_path / "suggestion-guard.db")
    )
    app.state.service.model = ScriptedModel()
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()

    response = client.post(
        "/api/v1/workflow-runs",
        json=_request_dict(conversation["conversation_id"]),
    )

    assert response.status_code == 201, response.text
    result = response.json()
    assert result["related_topics"] == [private_topic_marker]
    assert result["related_questions"] == ["如何计算矩阵秩?"]
    assert "BV1leak" not in response.text
    assert "b23.tv" not in response.text.casefold()
    normalization = next(
        event
        for event in result["trace"]
        if event["node"] == "knowledge_point_normalization"
    )
    assert normalization["result"] == {
        "reason_code": "question_concept",
        "candidate_count": 3,
        "accepted_count": 1,
    }
    assert private_topic_marker not in json.dumps(
        result["trace"], ensure_ascii=False
    )


def _trace_event() -> TraceEvent:
    return TraceEvent(
        event_id="event-1",
        sequence=0,
        node="request_validation",
        status="completed",
        duration_ms=0,
        result={},
    )


def test_stream_session_orders_events_and_allows_exactly_one_terminal_event() -> None:
    events = []
    session = WorkflowStreamSession(events.append)

    session.emit_trace(_trace_event())
    session.emit_answer_blocks(
        [
            AnswerBlock(
                type=AnswerBlockType.REPOSITORY,
                content="甲" * 2_001,
            )
        ]
    )
    session.emit_error("workflow_execution_failed", "本次运行失败，请稍后重试。")
    session.emit_error("workflow_execution_failed", "不得生成第二个终态。")

    assert [event.sequence for event in events] == [0, 1, 2, 3]
    assert {event.workflow_run_id for event in events} == {session.workflow_run_id}
    assert [event.kind for event in events] == [
        "trace",
        "answer_delta",
        "answer_delta",
        "error",
    ]
    assert session.terminal_emitted is True
    with pytest.raises(RuntimeError, match="terminal"):
        session.emit_trace(_trace_event())


def test_stream_session_marks_transport_failure_as_cancelled() -> None:
    def closed_transport(_: object) -> None:
        raise RuntimeError("client disconnected")

    session = WorkflowStreamSession(closed_transport)

    session.emit_trace(_trace_event())

    assert session.cancelled is True
    assert session.terminal_emitted is False


def test_stream_lifecycle_claims_linearize_steps_and_terminal_state() -> None:
    cancelled = WorkflowStreamSession(lambda _: None)

    assert cancelled.try_claim_step_start() is True
    cancelled.cancel()
    assert cancelled.cancelled is True
    assert cancelled.try_claim_step_start() is False
    assert cancelled.try_claim_terminal() is False

    completed = WorkflowStreamSession(lambda _: None)
    assert completed.try_claim_terminal() is True
    completed.cancel()
    assert completed.cancelled is False
    assert completed.try_claim_step_start() is False
    assert completed.try_claim_terminal() is False


def _mock_user() -> UserIdentity:
    return UserIdentity(
        user_id="mock-user-iteration-0",
        display_name="Iteration 0 Mock User",
        is_mock=True,
    )


def test_cancelled_stream_is_persisted_as_an_interrupted_terminal_result(
    tmp_path: Path,
) -> None:
    app = create_app(Settings(app_env="test", database_path=tmp_path / "cancel.db"))
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    request = WorkflowRunRequest.model_validate(
        _request_dict(conversation["conversation_id"])
    )
    events = []
    session = WorkflowStreamSession(events.append)
    session.cancel()

    result = app.state.service.run_stream(_mock_user(), request, session)

    assert result.run_status.value == "interrupted"
    assert events[-1].kind == "result"
    assert events[-1].workflow_run_id == result.workflow_run_id
    restored = client.get(f"/api/v1/workflow-runs/{result.workflow_run_id}")
    assert restored.status_code == 200
    assert restored.json() == result.model_dump(mode="json")


def test_disconnect_while_model_is_blocked_finishes_as_interrupted_after_return(
    tmp_path: Path,
) -> None:
    model_entered = Event()
    release_model = Event()

    class BlockingModel:
        def generate(self, request, sources, history=()):
            del request, sources, history
            model_entered.set()
            if not release_model.wait(timeout=2):
                raise TimeoutError("test model was not released")
            return GeneratedAnswer(
                repository_answer="不得作为完成回答保存。[S1]",
                citation_ids=("S1",),
            )

    app = create_app(Settings(app_env="test", database_path=tmp_path / "blocked.db"))
    app.state.service.model = BlockingModel()
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    request = WorkflowRunRequest.model_validate(
        _request_dict(conversation["conversation_id"])
    )
    events = []
    session = WorkflowStreamSession(events.append)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            app.state.service.run_stream,
            _mock_user(),
            request,
            session,
        )
        try:
            assert model_entered.wait(timeout=1)
            session.cancel()
        finally:
            release_model.set()
        result = future.result(timeout=2)

    assert result.run_status == RunStatus.INTERRUPTED
    assert result.answer_blocks == []
    assert all(event.kind != "answer_delta" for event in events)
    assert events[-1].kind == "result"
    assert events[-1].result is not None
    assert events[-1].result.run_status == RunStatus.INTERRUPTED
    restored = client.get(f"/api/v1/workflow-runs/{result.workflow_run_id}")
    assert restored.status_code == 200
    assert restored.json()["run_status"] == "interrupted"


def test_closing_the_stream_route_keeps_the_run_completing_in_background(
    tmp_path: Path,
) -> None:
    # 静默断线（网络波动/关页）≠ 用户取消：运行继续到完成并持久化终态，
    # 用户稍后重新读取会话即可拿到结果，而不是被打成 interrupted。
    model_entered = Event()
    release_model = Event()

    class BlockingModel:
        def generate(self, request, sources, history=()):
            del request, sources, history
            model_entered.set()
            if not release_model.wait(timeout=2):
                raise TimeoutError("test model was not released")
            return GeneratedAnswer(
                repository_answer="关闭路由后仍应在后台完成并保存。[S1]",
                citation_ids=("S1",),
            )

    app = create_app(
        Settings(app_env="test", database_path=tmp_path / "route-disconnect.db")
    )
    app.state.service.model = BlockingModel()
    conversation = app.state.service.create_conversation(
        _mock_user(), "linear_algebra"
    )
    request = WorkflowRunRequest.model_validate(
        _request_dict(conversation.conversation_id)
    )
    route = next(
        route
        for route in app.routes
        if getattr(route, "path", None) == "/api/v1/workflow-runs/stream"
    )

    async def close_route_and_wait_for_history() -> None:
        response = await route.endpoint(payload=request, user=_mock_user())
        iterator = response.body_iterator
        first_chunk = await anext(iterator)
        first_event = json.loads(first_chunk)
        run_id = UUID(first_event["workflow_run_id"])
        assert await asyncio.to_thread(model_entered.wait, 1)

        await iterator.aclose()
        release_model.set()

        for _ in range(100):
            restored = app.state.repository.get_run(
                "mock-user-iteration-0", run_id
            )
            if restored is not None and restored.run_status == RunStatus.COMPLETED:
                assert restored.workflow_run_id == run_id
                assert "[S1]" in restored.repository_answer
                return
            await asyncio.sleep(0.01)
        raise AssertionError("closed stream route did not persist completed run")

    try:
        asyncio.run(close_route_and_wait_for_history())
    finally:
        release_model.set()


def test_cancel_endpoint_interrupts_an_active_streamed_run(
    tmp_path: Path,
) -> None:
    model_entered = Event()
    release_model = Event()

    class BlockingModel:
        def generate(self, request, sources, history=()):
            del request, sources, history
            model_entered.set()
            if not release_model.wait(timeout=2):
                raise TimeoutError("test model was not released")
            return GeneratedAnswer(
                repository_answer="显式取消后不得保存为完成。[S1]",
                citation_ids=("S1",),
            )

    app = create_app(
        Settings(app_env="test", database_path=tmp_path / "explicit-cancel.db")
    )
    app.state.service.model = BlockingModel()
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    request = WorkflowRunRequest.model_validate(
        _request_dict(conversation["conversation_id"])
    )
    route = next(
        route
        for route in app.routes
        if getattr(route, "path", None) == "/api/v1/workflow-runs/stream"
    )

    async def cancel_while_model_blocked() -> None:
        response = await route.endpoint(payload=request, user=_mock_user())
        iterator = response.body_iterator
        first_chunk = await anext(iterator)
        run_id = UUID(json.loads(first_chunk)["workflow_run_id"])
        assert await asyncio.to_thread(model_entered.wait, 1)

        cancel_response = await asyncio.to_thread(
            client.post, f"/api/v1/workflow-runs/{run_id}/cancel"
        )
        assert cancel_response.status_code == 200
        assert cancel_response.json() == {"cancel_requested": True}
        release_model.set()

        for _ in range(100):
            restored = app.state.repository.get_run(
                "mock-user-iteration-0", run_id
            )
            if restored is not None and restored.run_status == RunStatus.INTERRUPTED:
                assert restored.answer_blocks == []
                return
            await asyncio.sleep(0.01)
        raise AssertionError("explicit cancel did not persist interrupted")

    try:
        asyncio.run(cancel_while_model_blocked())
    finally:
        release_model.set()


def test_cancel_endpoint_404_for_unknown_or_foreign_run(
    tmp_path: Path,
) -> None:
    app = create_app(Settings(app_env="test", database_path=tmp_path / "cancel404.db"))
    client = TestClient(app)

    response = client.post(
        "/api/v1/workflow-runs/00000000-0000-0000-0000-000000000000/cancel"
    )
    assert response.status_code == 404


def test_cancellation_wins_when_blocked_retrieval_returns_an_error(
    tmp_path: Path,
) -> None:
    retrieval_entered = Event()
    release_retrieval = Event()

    class BlockingFailureRetrieval:
        def is_course_available(self, course_id: str) -> bool:
            return course_id == "linear_algebra"

        def search(self, course_ids, query):
            del course_ids, query
            retrieval_entered.set()
            if not release_retrieval.wait(timeout=2):
                raise TimeoutError("test retrieval was not released")
            raise RuntimeError("retrieval failed after cancellation")

    class ModelMustNotRun:
        def generate(self, request, sources, history=()):
            del request, sources, history
            raise AssertionError("model must not run after cancelled retrieval")

    app = create_app(
        Settings(app_env="test", database_path=tmp_path / "cancel-retrieval.db")
    )
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    app.state.service.retrieval = BlockingFailureRetrieval()
    app.state.service.model = ModelMustNotRun()
    request = WorkflowRunRequest.model_validate(
        _request_dict(conversation["conversation_id"])
    )
    session = WorkflowStreamSession(lambda _: None)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            app.state.service.run_stream,
            _mock_user(),
            request,
            session,
        )
        try:
            assert retrieval_entered.wait(timeout=1)
            session.cancel()
        finally:
            release_retrieval.set()
        result = future.result(timeout=2)

    assert result.run_status == RunStatus.INTERRUPTED
    assert all(event.node != "workflow_execution_failed" for event in result.trace)
    restored = client.get(f"/api/v1/workflow-runs/{result.workflow_run_id}")
    assert restored.status_code == 200
    assert restored.json()["run_status"] == "interrupted"


@pytest.mark.parametrize(
    "model_error",
    [RuntimeError("provider unavailable"), TimeoutError("provider timeout")],
    ids=["non_retryable_failure", "retryable_timeout"],
)
def test_cancellation_wins_model_failure_and_prevents_retry(
    tmp_path: Path,
    model_error: Exception,
) -> None:
    model_entered = Event()
    release_model = Event()

    class BlockingFailureModel:
        def __init__(self) -> None:
            self.calls = 0

        def generate(self, request, sources, history=()):
            del request, sources, history
            self.calls += 1
            model_entered.set()
            if not release_model.wait(timeout=2):
                raise TimeoutError("test model was not released")
            raise model_error

    app = create_app(
        Settings(app_env="test", database_path=tmp_path / "cancel-error.db")
    )
    model = BlockingFailureModel()
    app.state.service.model = model
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    request = WorkflowRunRequest.model_validate(
        _request_dict(conversation["conversation_id"])
    )
    session = WorkflowStreamSession(lambda _: None)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            app.state.service.run_stream,
            _mock_user(),
            request,
            session,
        )
        try:
            assert model_entered.wait(timeout=1)
            session.cancel()
        finally:
            release_model.set()
        result = future.result(timeout=2)

    assert model.calls == 1
    assert result.run_status == RunStatus.INTERRUPTED
    assert all(event.node != "model_output_retry" for event in result.trace)
    restored = client.get(f"/api/v1/workflow-runs/{result.workflow_run_id}")
    assert restored.status_code == 200
    assert restored.json()["run_status"] == "interrupted"


def _ndjson_events(response_text: str) -> list[dict[str, object]]:
    return [json.loads(line) for line in response_text.splitlines() if line]


def test_stream_endpoint_uses_one_run_and_restores_the_terminal_history(
    tmp_path: Path,
) -> None:
    app = create_app(Settings(app_env="test", database_path=tmp_path / "stream.db"))
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()

    response = client.post(
        "/api/v1/workflow-runs/stream",
        json=_request_dict(conversation["conversation_id"]),
    )

    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("application/x-ndjson")
    events = _ndjson_events(response.text)
    assert [event["sequence"] for event in events] == list(range(len(events)))
    run_ids = {event["workflow_run_id"] for event in events}
    assert len(run_ids) == 1
    assert events[-1]["kind"] == "result"
    terminal_result = events[-1]["result"]
    assert isinstance(terminal_result, dict)
    assert terminal_result["run_status"] == "completed"
    assert terminal_result["workflow_run_id"] == next(iter(run_ids))

    streamed_blocks: dict[int, str] = {}
    for event in events:
        if event["kind"] != "answer_delta":
            continue
        delta = event["answer_delta"]
        assert isinstance(delta, dict)
        block_index = delta["block_index"]
        assert isinstance(block_index, int)
        streamed_blocks[block_index] = (
            streamed_blocks.get(block_index, "") + str(delta["delta"])
        )
    assert [streamed_blocks[index] for index in sorted(streamed_blocks)] == [
        block["content"] for block in terminal_result["answer_blocks"]
    ]

    restored = client.get(
        f"/api/v1/workflow-runs/{terminal_result['workflow_run_id']}"
    )
    assert restored.status_code == 200
    assert restored.json() == terminal_result


@pytest.mark.parametrize("invalid_result", ["empty", "multiple", "malformed"])
def test_invalid_bilibili_adapter_output_degrades_without_blocking_the_answer(
    tmp_path: Path,
    invalid_result: str,
) -> None:
    app = create_app(
        Settings(app_env="test", database_path=tmp_path / f"bili-{invalid_result}.db")
    )
    valid_adapter = BilibiliLinkDiscoveryAdapter()

    class InvalidDiscovery:
        def discover(self, **kwargs: object) -> list[object]:
            if invalid_result == "empty":
                return []
            if invalid_result == "malformed":
                return [object()]
            resources = valid_adapter.discover(**kwargs)  # type: ignore[arg-type]
            return [*resources, *resources]

    app.state.service.resources = InvalidDiscovery()
    client = TestClient(app, raise_server_exceptions=False)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    request = _request_dict(conversation["conversation_id"])
    request["include_bilibili_resources"] = True

    response = client.post("/api/v1/workflow-runs", json=request)

    assert response.status_code == 201, response.text
    result = response.json()
    assert result["run_status"] == "completed"
    assert result["answer_blocks"]
    assert result["external_resources"] == []
    event = next(
        item for item in result["trace"] if item["node"] == "bilibili_link_discovery"
    )
    assert event["status"] == "failed"


def test_transient_model_failure_retries_the_same_gateway_instance_once(
    tmp_path: Path,
) -> None:
    app = create_app(Settings(app_env="test", database_path=tmp_path / "retry.db"))

    class TransientThenSuccessModel:
        def __init__(self) -> None:
            self.calls = 0

        def generate(self, request, sources, history=()):
            del request, sources, history
            self.calls += 1
            if self.calls == 1:
                raise TimeoutError("temporary upstream timeout")
            return GeneratedAnswer(
                "同一模型重试后的回答 [S1]。",
                citation_ids=("S1",),
            )

    model = TransientThenSuccessModel()
    app.state.service.model = model
    client = TestClient(app, raise_server_exceptions=False)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()

    response = client.post(
        "/api/v1/workflow-runs",
        json=_request_dict(conversation["conversation_id"]),
    )

    assert response.status_code == 201, response.text
    assert model.calls == 2
    result = response.json()
    assert result["run_status"] == "completed"
    assert result["model"]["provider_id"] == "mock"
    assert any(event["node"] == "model_output_retry" for event in result["trace"])


def test_running_and_terminal_state_are_observable_for_the_same_stream_run(
    tmp_path: Path,
) -> None:
    app = create_app(Settings(app_env="test", database_path=tmp_path / "running.db"))
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    request = WorkflowRunRequest.model_validate(
        _request_dict(conversation["conversation_id"])
    )

    class BlockingModel:
        def __init__(self) -> None:
            self.started = Event()
            self.release = Event()

        def generate(self, request, sources, history=()):
            del request, sources, history
            self.started.set()
            assert self.release.wait(timeout=5), "test did not release the model"
            return GeneratedAnswer("阻塞结束后的回答 [S1]。", citation_ids=("S1",))

    model = BlockingModel()
    app.state.service.model = model
    session = WorkflowStreamSession(lambda _: None)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            app.state.service.run_stream,
            _mock_user(),
            request,
            session,
        )
        assert model.started.wait(timeout=5), "model call did not start"
        running = app.state.repository.get_run(
            "mock-user-iteration-0", session.workflow_run_id
        )
        model.release.set()
        completed = future.result(timeout=5)

    assert running is not None
    assert running.run_status == RunStatus.RUNNING
    assert running.workflow_run_id == session.workflow_run_id
    restored = app.state.repository.get_run(
        "mock-user-iteration-0", session.workflow_run_id
    )
    assert restored is not None
    assert restored.run_status == RunStatus.COMPLETED
    assert restored.model_dump(mode="json") == completed.model_dump(mode="json")


def test_terminal_run_cannot_be_overwritten_by_a_later_terminal_state(
    tmp_path: Path,
) -> None:
    app = create_app(Settings(app_env="test", database_path=tmp_path / "terminal.db"))
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    request = WorkflowRunRequest.model_validate(
        _request_dict(conversation["conversation_id"])
    )
    completed = app.state.service.run(_mock_user(), request)
    interrupted = completed.model_copy(
        update={
            "run_status": RunStatus.INTERRUPTED,
            "answer_status": AnswerStatus.PARTIAL,
            "repository_answer": None,
            "general_supplement": None,
            "answer_blocks": [],
            "evidence_status": EvidenceStatus.NOT_EVALUATED,
            "citations": [],
        }
    )

    try:
        app.state.repository.save_run(
            "mock-user-iteration-0",
            request,
            interrupted,
        )
    except ValueError:
        pass

    restored = app.state.repository.get_run(
        "mock-user-iteration-0", completed.workflow_run_id
    )
    assert restored is not None
    assert restored.model_dump(mode="json") == completed.model_dump(mode="json")


def test_all_five_workflows_share_the_same_runtime_pipeline(tmp_path: Path) -> None:
    app = create_app(Settings(app_env="test", database_path=tmp_path / "workflows.db"))
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    results: dict[str, dict[str, object]] = {}

    for workflow_type in WORKFLOW_PAYLOADS:
        request_payload = _request_dict(
            conversation["conversation_id"], workflow_type=workflow_type
        )
        request_payload["include_bilibili_resources"] = True
        response = client.post(
            "/api/v1/workflow-runs",
            json=request_payload,
        )
        assert response.status_code == 201, response.text
        results[workflow_type] = response.json()

    shared_nodes = [
        "request_validation",
        "identity",
        "run_record",
        # Iteration 5: exam_review inserts its deterministic plan node here;
        # the other four workflows keep the exact pre-iteration-5 sequence.
        "fixture_retrieval",
        "source_authorization_guard",
        "cache_policy",
        "mock_model",
        "citation_guard",
        "knowledge_point_normalization",
        "response_style_control",
        "bilibili_link_discovery",
        "persistence",
    ]
    assert len({result["workflow_run_id"] for result in results.values()}) == 5
    for workflow_type, result in results.items():
        expected_focus = WORKFLOW_FOCUS_EXPECTATIONS[workflow_type]
        expected_nodes = (
            [
                *shared_nodes[:3],
                "exam_review_plan",
                *shared_nodes[3:],
            ]
            if workflow_type == "exam_review"
            else shared_nodes
        )
        assert result["workflow_type"] == workflow_type
        assert result["workflow_output"]["runtime_version"] == "workflow-runtime-v1"
        assert result["workflow_output"]["payload_type"] == workflow_type
        assert [event["node"] for event in result["trace"]] == expected_nodes
        focus_event = next(
            event
            for event in result["trace"]
            if event["node"] == "knowledge_point_normalization"
        )
        assert focus_event["result"] == {
            "reason_code": expected_focus["strategy"],
            "candidate_count": len(expected_focus["topics"]),
            "accepted_count": len(expected_focus["topics"]),
        }
        assert result["related_topics"] == expected_focus["topics"]
        cache_event = next(
            event for event in result["trace"] if event["node"] == "cache_policy"
        )
        assert cache_event["status"] == "skipped"
        assert cache_event["result"] == {
            "cache_hit": False,
            "reason_code": "runtime_cache_not_configured",
        }
        assert len(result["external_resources"]) == 1
        assert result["external_resources"][0]["query_keywords"] == expected_focus[
            "keywords"
        ]
        assert result["external_resources"][0]["url"].startswith(
            "https://search.bilibili.com/all?keyword="
        )
        bilibili_event = next(
            event
            for event in result["trace"]
            if event["node"] == "bilibili_link_discovery"
        )
        assert bilibili_event["result"]["reason_code"] == (
            "model_bilibili_search_keywords"
        )
        response_style_event = next(
            event
            for event in result["trace"]
            if event["node"] == "response_style_control"
        )
        assert response_style_event["status"] == "completed"
        assert response_style_event["result"] == {
            "reason_code": "single_pass_model_prompt"
        }
        assert result["run_status"] == "completed"
        assert result["answer_blocks"]
