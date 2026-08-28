from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable

from .contracts import (
    AnswerBlock,
    AnswerBlockType,
    AnswerStatus,
    EvidenceStatus,
    KnowledgeScope,
    WorkflowRunRequest,
    WorkflowType,
)
from .ports import GeneratedAnswer, RetrievedSource
from .url_safety import contains_url_like_text


_CITATION_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:\[|【)S(\d+)(?:\]|】)"
)
_NUMBER_RE = re.compile(
    r"(?<![A-Za-z0-9_])[-+]?(?:\d+(?:\.\d+)?|\.\d+)"
    r"(?:[eE][-+]?\d+)?(?:%|[a-zA-Z]+)?"
)
_FORMULA_RE = re.compile(
    r"(```[\s\S]*?```|`[^`]+`|\$\$[\s\S]*?\$\$|\$[^$\n]+\$|"
    r"\\\([^\n]+?\\\)|\\\[[\s\S]+?\\\]|"
    r"\\begin\{[^{}]+\}[\s\S]*?\\end\{[^{}]+\})"
)


class RuntimeGuardError(ValueError):
    """A model output failed a deterministic, request-local safety guard."""


@dataclass(frozen=True, slots=True)
class GuardedAnswer:
    blocks: tuple[AnswerBlock, ...]
    citation_ids: tuple[str, ...]
    evidence_status: EvidenceStatus
    answer_status: AnswerStatus
    coverage_gaps: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class HumanizerOutcome:
    blocks: tuple[AnswerBlock, ...]
    applied: bool
    fallback: bool
    reason: str | None = None


def normalize_topics(values: Iterable[str], *, max_items: int = 8) -> tuple[str, ...]:
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str):
            continue
        text = unicodedata.normalize("NFKC", value)
        text = "".join(
            " " if unicodedata.category(char).startswith("C") else char
            for char in text
        )
        text = " ".join(text.split()).strip()
        # Topics/questions are still model-controlled result fields. Never let
        # them bypass the answer/citation boundary with a URL or a source marker
        # that was not resolved by the citation guard.
        if contains_url_like_text(text) or _CITATION_RE.search(text):
            continue
        text = text[:64].strip()
        if not text or text.casefold() in seen:
            continue
        seen.add(text.casefold())
        normalized.append(text)
        if len(normalized) >= max_items:
            break
    return tuple(normalized)


def validate_model_citations(
    *,
    answer: GeneratedAnswer,
    sources: list[RetrievedSource],
    course_ids: set[str],
) -> tuple[tuple[str, ...], tuple[RetrievedSource, ...]]:
    """Resolve only explicit, unique S-number citations from this request."""

    declared = tuple(answer.citation_ids)
    if len(set(declared)) != len(declared):
        raise RuntimeGuardError("模型返回了重复的引用编号。")
    source_by_id = {f"S{index}": source for index, source in enumerate(sources, 1)}
    if len(source_by_id) != len(sources):
        raise RuntimeGuardError("本次检索候选编号不唯一。")
    for citation_id in declared:
        if not re.fullmatch(r"S[1-9][0-9]*", citation_id):
            raise RuntimeGuardError("模型返回了格式非法的引用编号。")
        source = source_by_id.get(citation_id)
        if source is None or source.course_id not in course_ids:
            raise RuntimeGuardError("模型引用了不属于本次候选范围的来源。")

    mentioned = tuple(f"S{number}" for number in _CITATION_RE.findall(answer.repository_answer))
    unknown_mentions = [citation_id for citation_id in mentioned if citation_id not in source_by_id]
    if unknown_mentions:
        raise RuntimeGuardError("回答正文包含未知的引用编号。")
    if mentioned and any(citation_id not in declared for citation_id in mentioned):
        raise RuntimeGuardError("回答正文引用了未声明的候选来源。")

    for text in (
        answer.general_supplement,
        answer.user_material_answer,
        answer.personalized_analysis,
    ):
        if _CITATION_RE.search(text):
            raise RuntimeGuardError("非仓库回答块不得携带仓库引用编号。")
    for text in (
        answer.repository_answer,
        answer.general_supplement,
        answer.user_material_answer,
        answer.personalized_analysis,
    ):
        if contains_url_like_text(text):
            raise RuntimeGuardError("回答不得返回 URL。")

    if declared and not answer.repository_answer.strip():
        raise RuntimeGuardError("课程引用必须对应 repository 回答块。")

    selected = tuple(source_by_id[citation_id] for citation_id in declared)
    return declared, selected


def build_guarded_answer(
    *,
    request: WorkflowRunRequest,
    answer: GeneratedAnswer,
    sources: list[RetrievedSource],
    course_ids: set[str],
) -> GuardedAnswer:
    citation_ids, selected_sources = validate_model_citations(
        answer=answer, sources=sources, course_ids=course_ids
    )
    blocks: list[AnswerBlock] = []
    repository_answer = answer.repository_answer.strip()
    uncited_repository_answer = repository_answer if not citation_ids else ""
    # A provider is no longer required to manufacture a full JSON envelope.
    # In course-first mode, a useful answer without a request-local source is
    # still useful as explicitly non-repository guidance.  In course-only mode
    # it remains hidden so the UI never presents an uncited statement as a
    # course-material conclusion.
    repository_answer_dropped = bool(
        uncited_repository_answer
        and request.knowledge_scope == KnowledgeScope.COURSE_ONLY
    )
    if repository_answer and citation_ids:
        blocks.append(
            AnswerBlock(type=AnswerBlockType.REPOSITORY, content=repository_answer)
        )
    user_material_answer = answer.user_material_answer.strip()
    if (
        uncited_repository_answer
        and request.knowledge_scope != KnowledgeScope.COURSE_ONLY
        and request.workflow_type == WorkflowType.TEMPORARY_MATERIAL_READING
    ):
        user_material_answer = _join_answer_text(
            uncited_repository_answer, user_material_answer
        )
    if user_material_answer:
        if request.workflow_type != WorkflowType.TEMPORARY_MATERIAL_READING:
            raise RuntimeGuardError("user_material 回答块只能用于临时材料 Workflow。")
        blocks.append(
            AnswerBlock(
                type=AnswerBlockType.USER_MATERIAL,
                content=user_material_answer,
            )
        )
    general_supplement = answer.general_supplement.strip()
    if (
        uncited_repository_answer
        and request.knowledge_scope != KnowledgeScope.COURSE_ONLY
        and request.workflow_type != WorkflowType.TEMPORARY_MATERIAL_READING
    ):
        general_supplement = _join_answer_text(
            uncited_repository_answer, general_supplement
        )
    if general_supplement:
        if request.knowledge_scope == KnowledgeScope.COURSE_ONLY:
            raise RuntimeGuardError("仅课程资料模式不得生成 general 回答块。")
        blocks.append(
            AnswerBlock(type=AnswerBlockType.GENERAL, content=general_supplement)
        )
    if answer.personalized_analysis.strip():
        if request.workflow_type not in {
            WorkflowType.EXAM_REVIEW,
            WorkflowType.PROBLEM_TUTOR,
            WorkflowType.MISTAKE_REVIEW,
        }:
            raise RuntimeGuardError("当前 Workflow 不允许 personalized_analysis 回答块。")
        blocks.append(
            AnswerBlock(
                type=AnswerBlockType.PERSONALIZED_ANALYSIS,
                content=answer.personalized_analysis.strip(),
            )
        )
    if not blocks and not repository_answer_dropped:
        raise RuntimeGuardError("模型没有返回可展示的回答块。")

    if citation_ids:
        evidence_status = EvidenceStatus.SUFFICIENT
        answer_status = AnswerStatus.ANSWERED
        gaps: tuple[str, ...] = ()
    elif request.knowledge_scope == KnowledgeScope.COURSE_ONLY:
        evidence_status = EvidenceStatus.INSUFFICIENT
        answer_status = AnswerStatus.INSUFFICIENT_EVIDENCE
        gaps = (
            "本次课程资料候选不足，已停止补充通用知识，未展示无引用的课程资料正文。",
        )
    elif any(block.type == AnswerBlockType.USER_MATERIAL for block in blocks):
        evidence_status = EvidenceStatus.PARTIAL
        answer_status = AnswerStatus.PARTIAL
        gaps = ("本次回答主要基于用户提供的临时材料，未匹配到课程资料引用。",)
    else:
        evidence_status = EvidenceStatus.INSUFFICIENT
        answer_status = AnswerStatus.PARTIAL
        gaps = (
            "本次回答没有可回查的课程资料候选；无引用内容已作为通用补充展示，未作为课程资料结论。",
        )
    # Keep this explicit so an unused local cannot accidentally become a future
    # citation source without passing through the guard above.
    del selected_sources
    return GuardedAnswer(tuple(blocks), citation_ids, evidence_status, answer_status, gaps)


def _join_answer_text(*parts: str) -> str:
    """Join non-empty answer sections without duplicating identical text."""

    joined: list[str] = []
    for part in parts:
        text = part.strip()
        if text and text not in joined:
            joined.append(text)
    return "\n\n".join(joined)


def _protected_fingerprint(text: str, protected_terms: tuple[str, ...]) -> tuple[str, ...]:
    values: list[str] = []
    values.extend(match.group(0) for match in _FORMULA_RE.finditer(text))
    values.extend(match.group(0) for match in _CITATION_RE.finditer(text))
    values.extend(match.group(0) for match in _NUMBER_RE.finditer(text))
    for term in protected_terms:
        if term:
            values.extend(f"term:{term}" for _ in range(text.count(term)))
    return tuple(values)


def protect_humanizer_output(
    *,
    original: list[AnswerBlock],
    candidate: list[AnswerBlock],
    protected_terms: tuple[str, ...],
) -> HumanizerOutcome:
    if len(original) != len(candidate):
        return HumanizerOutcome(tuple(original), False, True, "block_count_changed")
    for before, after in zip(original, candidate, strict=True):
        if before.type != after.type:
            return HumanizerOutcome(tuple(original), False, True, "block_type_changed")
        if contains_url_like_text(after.content):
            return HumanizerOutcome(tuple(original), False, True, "unsafe_link_added")
        if _protected_fingerprint(before.content, protected_terms) != _protected_fingerprint(
            after.content, protected_terms
        ):
            return HumanizerOutcome(
                tuple(original), False, True, "protected_content_changed"
            )
        # This iteration has no semantic-equivalence verifier. Fail closed on
        # every remaining rewrite instead of treating an undetected fact or
        # negation change as safe humanization.
        if before.content != after.content:
            return HumanizerOutcome(
                tuple(original), False, True, "unverified_text_change"
            )
    return HumanizerOutcome(tuple(candidate), False, False, "no_change")
