from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

from scut_senior_worker.corpus_validator import parse_markdown, validate_corpus

from ..contracts import AnswerMode, Tone, WorkflowRunRequest
from ..paths import FIXTURE_ROOT
from ..ports import (
    ConversationTurn,
    GeneratedAnswer,
    RetrievalBatch,
    RetrievedSource,
    UserIdentity,
)
from ..registry import CourseRegistry
from ..workflow_focus import (
    FocusStrategy,
    build_tone_visible_callout,
    build_workflow_focus,
)


_TONE_FIXTURE_NOTES: dict[Tone, str] = {
    Tone.TEACHING_ASSISTANT: "（Mock 助教口径：依据先摆齐，结论才给分。）",
    Tone.SENIOR_STUDENT: "（Mock 学长口径：主线就一条，卡住回定义，稳的。）",
    Tone.STUDY_PARTNER: "（Mock 学妹口径：这一步可别偷懒哦～自己先算一遍，我再帮你对答案！）",
}


_FIXTURE_FOCUS_OUTPUTS: dict[
    FocusStrategy, tuple[tuple[str, ...], tuple[str, ...]]
] = {
    FocusStrategy.QUESTION_CONCEPT: (
        ("矩阵", "线性方程组"),
        ("矩阵的秩", "初等行变换"),
    ),
    FocusStrategy.SYLLABUS_WEAK_TOPICS: (
        ("复习大纲", "初等行变换"),
        ("初等行变换复习", "矩阵复习"),
    ),
    FocusStrategy.PROBLEM_MAIN_TOPIC: (
        ("矩阵题主知识点",),
        ("矩阵秩题目",),
    ),
    FocusStrategy.MISTAKE_ROOT_CAUSE: (
        ("矩阵概念错误根因",),
        ("矩阵秩错误原因",),
    ),
    FocusStrategy.MATERIAL_TITLE_MAIN_TOPICS: (
        ("临时材料主要知识点",),
        ("矩阵材料精读",),
    ),
}


class MockIdentityProvider:
    def current_user(self) -> UserIdentity:
        return UserIdentity(
            user_id="mock-user-iteration-0",
            display_name="Iteration 0 Mock User",
            is_mock=True,
        )


class FixtureContractViolation(RuntimeError):
    pass


class FixtureRetrievalGateway:
    """Reads only synthetic passed fixtures; it never scans real course materials."""

    def __init__(
        self,
        registry: CourseRegistry,
        knowledge_root: Path | None = None,
    ):
        self.registry = registry
        self.knowledge_root = knowledge_root or FIXTURE_ROOT / "corpus"
        self.manifest_path = self.knowledge_root / "manifest.csv"

    def is_course_available(self, course_id: str) -> bool:
        return self.registry.get(course_id).fixture_available

    def search(self, course_ids: list[str], query: str) -> RetrievalBatch:
        del query  # Fixture retrieval proves filtering/contracts, not ranking quality.
        if not course_ids or len(course_ids) != len(set(course_ids)):
            raise FixtureContractViolation(
                "synthetic fixture retrieval requires a non-empty unique course set"
            )
        if not self.manifest_path.exists():
            return RetrievalBatch((), "fixture-corpus-v1")
        report = validate_corpus(self.manifest_path, self.knowledge_root)
        if report.errors:
            raise FixtureContractViolation(
                "synthetic corpus fixture failed validation: " + "; ".join(report.errors)
            )
        results: list[RetrievedSource] = []
        for record in report.searchable_sources:
            course_id = record["course_id"]
            if course_id not in course_ids:
                continue
            markdown_path = self.knowledge_root / record["output_md"]
            parsed = parse_markdown(markdown_path)
            results.append(_source_from_validated_fixture(parsed.body, record, parsed))
        return RetrievalBatch(tuple(results[:5]), "fixture-corpus-v1")


class MockModelGateway:
    provider_id = "mock"
    model_id = "deterministic-fixture-v1"

    def generate(
        self,
        request: WorkflowRunRequest,
        sources: list[RetrievedSource],
        history: tuple[ConversationTurn, ...] = (),
        *,
        cancel_check: Callable[[], bool] | None = None,
    ) -> GeneratedAnswer:
        workflow_focus = build_workflow_focus(request)
        control_note = (
            f"Fixture 已接收回答方式 `{request.answer_mode.value}` 与表达风格 "
            f"`{request.tone.value}`。"
        )
        history_note = (
            f"\n\n（Mock 已接收 {len(history)} 条历史消息作为多轮上下文。）"
            if history
            else ""
        )
        related_topics, search_keywords = _FIXTURE_FOCUS_OUTPUTS[
            workflow_focus.focus_strategy
        ]
        if not sources:
            return GeneratedAnswer(
                repository_answer=_render_fixture_answer(
                    answer_mode=request.answer_mode,
                    tone=request.tone,
                    source_title="无可用 passed Fixture",
                    preview=(
                        "没有读取到合成课程片段；这只表示契约测试资料不足，"
                        "不代表真实课程资料结论。"
                    ),
                    workflow_type=request.workflow_type.value,
                    control_note=control_note,
                    history_note=history_note,
                ),
                related_topics=related_topics,
                bilibili_search_keywords=search_keywords,
            )
        source = sources[0]
        preview = re.sub(r"\s+", " ", source.text).strip()[:180]
        answer = _render_fixture_answer(
            answer_mode=request.answer_mode,
            tone=request.tone,
            source_title=source.source_title,
            preview=preview,
            workflow_type=request.workflow_type.value,
            control_note=control_note,
            history_note=history_note,
        )
        return GeneratedAnswer(
            repository_answer=answer,
            related_topics=related_topics,
            related_questions=("如何判断矩阵的秩？",),
            bilibili_search_keywords=search_keywords,
            # The deterministic fixture explicitly selects its request-local
            # candidates. The service no longer turns every retrieval hit into
            # a citation on the model's behalf.
            citation_ids=tuple(
                f"S{index}" for index in range(1, len(sources) + 1)
            ),
        )


def _render_fixture_answer(
    *,
    answer_mode: AnswerMode,
    tone: Tone,
    source_title: str,
    preview: str,
    workflow_type: str,
    control_note: str,
    history_note: str,
) -> str:
    """Make the local fixture visibly exercise the selected presentation mode.

    This remains deterministic test data, not a claim that a real model has
    semantically followed the same contract.
    """

    tone_callout = build_tone_visible_callout(tone)
    context = (
        "这是迭代 0 的确定性 Mock 回答，仅用于验证契约、来源与持久化链路。\n\n"
        f"{_TONE_FIXTURE_NOTES[tone]}\n\n"
        f"已从合成 Fixture《{source_title}》读取：{preview}\n\n"
        f"本次结构化输入类型为 `{workflow_type}`；"
        "尚未调用真实模型，也未运行生产检索。"
    )
    if answer_mode == AnswerMode.CONCISE:
        return (
            "## 结论\n\n"
            f"{context}\n\n"
            f"{tone_callout}\n\n"
            "## 要点\n\n"
            f"- {control_note}{history_note}"
        )
    if answer_mode == AnswerMode.DETAILED:
        return (
            "## 结论\n\n"
            f"{context}\n\n"
            f"{tone_callout}\n\n"
            "## 原理与依据\n\n"
            f"{control_note}\n\n"
            "## 易错点或适用边界\n\n"
            f"这只是合成 Fixture，不代表真实课程资料结论。{history_note}"
        )
    if answer_mode == AnswerMode.EXAMPLE:
        return (
            "## 结论\n\n"
            f"{context}\n\n"
            f"{tone_callout}\n\n"
            "## 例子\n\n"
            f"已知条件：合成 Fixture《{source_title}》。\n\n"
            f"操作或计算：读取其片段“{preview}”。\n\n"
            "得到的结果：该片段只用于验证本地链路。\n\n"
            "## 从例子得到的判断\n\n"
            f"{control_note}{history_note}"
        )
    return (
        "## 步骤\n\n"
        "1. **目的：** 确认本地 Fixture 是否可读取。\n"
        f"   **操作或判断：** 读取《{source_title}》。\n"
        "   **本步结果：** 已得到合成资料片段。\n\n"
        "2. **目的：** 保持回答的证据边界。\n"
        "   **操作或判断：** 仅把片段用于 Runtime 链路验证。\n"
        "   **本步结果：** 不把 Fixture 表述为真实课程结论。\n\n"
        f"{tone_callout}\n\n"
        "## 结论\n\n"
        f"{context}\n\n{control_note}{history_note}"
    )


def _source_from_validated_fixture(body: str, record: dict[str, object], parsed) -> RetrievedSource:
    headings = [heading.text for heading in parsed.headings]
    locator_type = str(record["locator_type"] or "heading")
    locator_start: int | str | None
    if locator_type == "page":
        locator_start = record.get("first_page")
    elif locator_type == "slide":
        locator_start = record.get("first_slide")
    elif locator_type == "heading" and headings:
        locator_start = headings[0]
    else:
        locator_start = None
    text = re.sub(r"<!--.*?-->", " ", body, flags=re.DOTALL)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE).strip()
    source_id = str(record["source_id"])
    ordinal = "c01"
    locator_token = (
        f"p{locator_start}"
        if locator_type == "page"
        else f"s{locator_start}"
        if locator_type == "slide"
        else "heading"
    )
    return RetrievedSource(
        chunk_id=f"{source_id}:{locator_token}:{ordinal}",
        course_id=str(record["course_id"]),
        source_id=source_id,
        source_title=str(record["source_title"]),
        text=text,
        locator_type=locator_type,
        locator_start=locator_start,
        locator_end=locator_start,
        question_id=(
            str(record["first_question"])
            if locator_type != "none" and record.get("first_question") is not None
            else None
        ),
        heading_path=tuple(headings[:3]) if locator_type != "none" else (),
    )
