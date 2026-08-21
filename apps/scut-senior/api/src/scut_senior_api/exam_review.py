"""Iteration 5 deterministic exam-review planner (SOP §10 备考复习).

This module is the backend source of truth for the two evidence-backed
exam-review paths:

- ``with_syllabus``: 用户大纲 > 课程资料 > 历年题 > 允许时的通用知识
- ``without_syllabus``: 历年题 > 课程资料 > 允许时的通用知识

Every statistic is an objective count over already-reviewed corpus facts
(past-exam sources and their question locators). The planner never predicts
pass probability, never claims an official scope, and never turns model text
into corpus facts. Private request inputs (syllabus, weak topics, goals) only
shape ordering and coverage of the caller's own plan; they are never written
into course packs, citations, external resources or Trace.

The module is pure: no I/O, no clock, no randomness. Adapters in
``adapters/exam_facts.py`` supply :class:`ExamCorpusFacts` from either the
active local-corpus course pack or the synthetic fixture corpus.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

PLAN_VERSION = "exam-review-plan-v1"

MAX_KNOWLEDGE_POINTS = 12
MAX_QUESTIONS_PER_GROUP = 8
MAX_SAMPLE_YEARS = 24
MAX_SYLLABUS_ITEMS = 32
MIN_TOPIC_CHARS = 2

_PAST_EXAM_ROLES = frozenset({"past_exam", "past_exam_answer", "practice_exam"})

# Objective question-type labels are read only from reviewed heading text.
# A question whose headings name no type is counted as ``untyped``; the
# planner must not guess types from question bodies.
_QUESTION_TYPE_LABELS: tuple[tuple[str, str], ...] = (
    ("填空", "filling_blank"),
    ("选择", "multiple_choice"),
    ("判断", "true_false"),
    ("计算", "calculation"),
    ("证明", "proof"),
    ("解答", "solution"),
    ("应用", "application"),
    ("综合", "comprehensive"),
    ("作图", "drawing"),
    ("简答", "short_answer"),
)
_UNTYPED_KEY = "untyped"

_SCORE_PAREN_RE = re.compile(r"[（(][^（）()]*[分值][^（）()]*[）)]$")
_HEADING_PREFIX_RE = re.compile(r"^[一二三四五六七八九十0-9]+\s*[、.．:：]?\s*")

# Objective question-type labels are read only from reviewed heading text.
# A question whose headings name no type is counted as ``untyped``; the
# planner must not guess types from question bodies.
_QUESTION_TYPE_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("填空", "filling_blank"),
    ("选择", "multiple_choice"),
    ("判断", "true_false"),
    ("计算", "calculation"),
    ("证明", "proof"),
    ("解答", "solution"),
    ("应用", "application"),
    ("综合", "comprehensive"),
    ("作图", "drawing"),
    ("简答", "short_answer"),
)
_TYPE_LABELS: dict[str, str] = {
    "filling_blank": "填空题",
    "multiple_choice": "选择题",
    "true_false": "判断题",
    "calculation": "计算题",
    "proof": "证明题",
    "solution": "解答题",
    "application": "应用题",
    "comprehensive": "综合题",
    "drawing": "作图题",
    "short_answer": "简答题",
}
_UNTYPED_KEY = "untyped"
_UNTYPED_LABEL = "未标注题型"


class ExamReviewPath(StrEnum):
    WITH_SYLLABUS = "with_syllabus"
    WITHOUT_SYLLABUS = "without_syllabus"


# Evidence priority chains per SOP §10.2. ``general`` is appended only when
# the request's knowledge scope allows marked general supplements.
_PRIORITY_WITH_SYLLABUS = ("user_syllabus", "course_material", "past_exam")
_PRIORITY_WITHOUT_SYLLABUS = ("past_exam", "course_material")
_GENERAL_STEP = "general"


@dataclass(frozen=True, slots=True)
class ExamSourceFact:
    """One reviewed corpus source relevant to exam statistics."""

    source_id: str
    source_title: str
    document_role: str
    year: int | None


@dataclass(frozen=True, slots=True)
class ExamQuestionFact:
    """One reviewed question locator from a past-exam source."""

    question_id: str
    source_id: str
    source_title: str
    year: int | None
    heading_path: tuple[str, ...]
    locator_type: str
    locator_start: int | str | None
    locator_end: int | str | None


@dataclass(frozen=True, slots=True)
class ExamCorpusFacts:
    """Reviewed, version-bound corpus facts used by the planner."""

    course_id: str
    corpus_version: str
    course_pack_version: str | None
    sources: tuple[ExamSourceFact, ...]
    questions: tuple[ExamQuestionFact, ...]
    # Reviewed course-material heading texts (any document role). They give
    # the “课程资料” evidence leg for coverage without touching model output.
    heading_topics: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ExamReviewPlan:
    """Deterministic, bounded plan attached to one exam_review run."""

    plan_version: str
    course_id: str
    path: ExamReviewPath
    priority_order: tuple[str, ...]
    scope_statement: str
    evidence_boundary: str
    ai_sample_policy: str
    knowledge_points: tuple[dict[str, Any], ...]
    past_exam_stats: dict[str, Any]
    review_suggestions: tuple[str, ...]
    uncovered_items: tuple[str, ...]

    def to_output_dict(self) -> dict[str, Any]:
        """Shape placed under ``workflow_output["exam_review"]``."""

        return {
            "plan_version": self.plan_version,
            "path": self.path.value,
            "priority_order": list(self.priority_order),
            "scope_statement": self.scope_statement,
            "evidence_boundary": self.evidence_boundary,
            "ai_sample_policy": self.ai_sample_policy,
            "knowledge_points": [dict(point) for point in self.knowledge_points],
            "past_exam_stats": dict(self.past_exam_stats),
            "review_suggestions": list(self.review_suggestions),
            "uncovered_items": list(self.uncovered_items),
        }


def has_user_syllabus(syllabus: object) -> bool:
    return isinstance(syllabus, str) and bool(syllabus.strip())


def build_exam_review_plan(
    *,
    course_id: str,
    payload_syllabus: str | None,
    payload_weak_topics: list[str],
    payload_available_hours: float | None,
    knowledge_scope_allows_general: bool,
    facts: ExamCorpusFacts | None,
) -> ExamReviewPlan:
    """Build the deterministic plan; ``facts=None`` yields an honest empty plan."""

    with_syllabus = has_user_syllabus(payload_syllabus)
    path = ExamReviewPath.WITH_SYLLABUS if with_syllabus else ExamReviewPath.WITHOUT_SYLLABUS
    priority = list(
        _PRIORITY_WITH_SYLLABUS if with_syllabus else _PRIORITY_WITHOUT_SYLLABUS
    )
    if knowledge_scope_allows_general:
        priority.append(_GENERAL_STEP)

    weak_keys = {
        _normalize_topic(topic)
        for topic in (payload_weak_topics or [])
        if _normalize_topic(topic)
    }

    past_exam_source_ids = {
        source.source_id
        for source in (facts.sources if facts else ())
        if source.document_role in _PAST_EXAM_ROLES
    }
    past_exam_questions = tuple(
        question
        for question in (facts.questions if facts else ())
        if question.source_id in past_exam_source_ids
    )

    stats = _build_past_exam_stats(past_exam_questions)
    material_topics = tuple(facts.heading_topics if facts else ())
    knowledge_points = _build_knowledge_points(
        questions=past_exam_questions,
        all_questions=tuple(facts.questions if facts else ()),
        weak_keys=weak_keys,
        material_topics=material_topics,
    )
    uncovered = (
        _compute_uncovered_syllabus_items(
            payload_syllabus or "",
            knowledge_points,
            material_topics=tuple(facts.heading_topics if facts else ()),
        )
        if with_syllabus
        else ()
    )
    suggestions = _build_review_suggestions(
        path=path,
        knowledge_points=knowledge_points,
        stats=stats,
        weak_count=len(weak_keys),
        available_hours=payload_available_hours,
    )

    if with_syllabus:
        scope_statement = (
            "本次备考复习以你提供的大纲为范围依据，"
            "按“用户大纲 > 课程资料 > 历年题"
            + (" > 标记的通用知识”" if knowledge_scope_allows_general else "”")
            + "的证据顺序组织。"
        )
    else:
        scope_statement = (
            "未提供大纲：以下内容不是官方考试范围，也不构成考试重点预测；"
            "仅按“历年题 > 课程资料"
            + (" > 标记的通用知识”" if knowledge_scope_allows_general else "”")
            + "的客观证据组织。"
        )
    evidence_boundary = (
        "所有统计只来自当前课程已审核语料的客观出现次数，"
        "每条统计都能回到题目来源；资料未覆盖的内容会明确列为未覆盖，不做补造。"
    )
    ai_sample_policy = (
        "模型补充的练习样题均为 AI 生成、非历年真题；"
        "历年真题只包括下方统计与题组中列出且可回查来源的题目。"
    )

    return ExamReviewPlan(
        plan_version=PLAN_VERSION,
        course_id=course_id,
        path=path,
        priority_order=tuple(priority),
        scope_statement=scope_statement,
        evidence_boundary=evidence_boundary,
        ai_sample_policy=ai_sample_policy,
        knowledge_points=knowledge_points,
        past_exam_stats=stats,
        review_suggestions=suggestions,
        uncovered_items=uncovered,
    )


def compose_retrieval_query(
    *,
    syllabus: str | None,
    weak_topics: list[str],
    plan: ExamReviewPlan | None,
) -> str:
    """Compose the deterministic retrieval query for the selected path.

    ``with_syllabus`` keeps the iteration-4 semantics (syllabus first, then
    weak topics). ``without_syllabus`` follows “历年题优先”: weak topics come
    first when present, and objective past-exam topic terms fill the query so
    an empty syllabus no longer means an empty search.
    """

    parts: list[str] = []
    if has_user_syllabus(syllabus):
        parts.append(_clean_text(syllabus or "", 2_500))
    cleaned_weak = _clean_unique_list(weak_topics, limit=8, max_chars=240)
    parts.extend(cleaned_weak)
    if plan is not None and plan.path == ExamReviewPath.WITHOUT_SYLLABUS:
        parts.extend(_plan_topic_terms(plan, limit=5 if not cleaned_weak else 3))
    query = "\n".join(part for part in parts if part)
    return query[:4_500].strip()


def render_exam_review_appendix(plan: ExamReviewPlan) -> str:
    """Render the deterministic student-visible appendix (no model content)."""

    lines: list[str] = ["## 备考复习统计（系统生成）", ""]
    lines.append(f"> 范围与证据说明：{plan.scope_statement}")
    lines.append(f"> 证据边界：{plan.evidence_boundary}")
    lines.append(f"> AI 样题边界：{plan.ai_sample_policy}")
    lines.append("")

    stats = plan.past_exam_stats
    lines.append("### 历年题客观统计")
    lines.append("")
    if stats.get("question_count"):
        sample_years = stats.get("sample_years") or []
        year_text = "、".join(str(year) for year in sample_years) if sample_years else "年份未标注"
        lines.append(
            f"- 样本年份：{year_text}"
            f"（共 {stats.get('year_count', 0)} 个年份、{stats['question_count']} 道题）"
        )
        coverage = stats.get("year_coverage") or []
        if coverage:
            rendered = "、".join(
                f"{item['year']}（{item['count']} 题）" for item in coverage
            )
            lines.append(f"- 年份覆盖：{rendered}")
        distribution = stats.get("type_distribution") or []
        if distribution:
            rendered = "、".join(
                f"{item['label']}（{item['count']} 次）" for item in distribution
            )
            lines.append(f"- 题型分布（客观出现次数）：{rendered}")
        lines.append("- 以上为客观出现次数统计，不输出命题概率，也没有“必考”预测。")
    else:
        lines.append("- 本课程当前已审核语料中没有可统计的历年题；以上统计为空，不编造数据。")
    lines.append("")

    lines.append("### 知识点分层与建议顺序")
    lines.append("")
    if plan.knowledge_points:
        for index, point in enumerate(plan.knowledge_points, start=1):
            locations = point.get("material_locations") or []
            location_text = "；".join(
                f"《{loc['source_title']}》{_locator_label(loc)}" for loc in locations[:3]
            )
            questions = point.get("questions") or []
            question_text = "、".join(
                f"{q['question_id']}（{q['year'] if q.get('year') else '年份未标注'}）"
                for q in questions[:4]
            )
            layer = point.get("layer", 1)
            line = f"{index}. 【第 {layer} 层】{point['topic']}"
            reasons = point.get("order_reasons") or []
            if reasons:
                line += f"（排序依据：{'、'.join(reasons)}）"
            line += f" — 资料位置：{location_text or '当前候选中没有可展示的资料位置'}"
            if question_text:
                line += f"；代表性真题：{question_text}"
            lines.append(line)
    else:
        lines.append("当前语料没有可组织的历年题题组；知识点请以课程资料目录为准。")
    lines.append("")

    lines.append("### 复习建议")
    lines.append("")
    for suggestion in plan.review_suggestions:
        lines.append(f"- {suggestion}")
    lines.append("")

    if plan.uncovered_items:
        lines.append("### 未覆盖内容")
        lines.append("")
        for item in plan.uncovered_items:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines).strip()


def _build_past_exam_stats(
    questions: tuple[ExamQuestionFact, ...],
) -> dict[str, Any]:
    years_counter: dict[int, int] = {}
    type_counter: dict[str, int] = {}
    for question in questions:
        if question.year is not None:
            years_counter[question.year] = years_counter.get(question.year, 0) + 1
        type_key = _question_type_of(question)
        type_counter[type_key] = type_counter.get(type_key, 0) + 1
    year_coverage = [
        {"year": year, "count": count}
        for year, count in sorted(years_counter.items())
    ][:MAX_SAMPLE_YEARS]
    distribution = [
        {"key": key, "label": _TYPE_LABELS.get(key, key), "count": count}
        for key, count in sorted(
            type_counter.items(), key=lambda item: (-item[1], item[0])
        )
        if key != _UNTYPED_KEY
    ]
    if type_counter.get(_UNTYPED_KEY):
        distribution.append(
            {
                "key": _UNTYPED_KEY,
                "label": _UNTYPED_LABEL,
                "count": type_counter[_UNTYPED_KEY],
            }
        )
    return {
        "question_count": len(questions),
        "source_count": len({question.source_id for question in questions}),
        "year_count": len(years_counter),
        "sample_years": sorted(years_counter)[:MAX_SAMPLE_YEARS],
        "year_coverage": year_coverage,
        "type_distribution": distribution,
        "questions": [
            {
                "question_id": question.question_id,
                "source_id": question.source_id,
                "source_title": question.source_title,
                "year": question.year,
                "locator_type": question.locator_type,
                "locator_start": question.locator_start,
                "heading_path": list(question.heading_path),
            }
            for question in questions[:64]
        ],
    }


def _build_knowledge_points(
    *,
    questions: tuple[ExamQuestionFact, ...],
    all_questions: tuple[ExamQuestionFact, ...],
    weak_keys: set[str],
    material_topics: tuple[str, ...],
) -> tuple[dict[str, Any], ...]:
    grouped: dict[str, dict[str, Any]] = {}
    for question in questions:
        topic = _topic_of_question(question)
        if not topic:
            continue
        key = _normalize_topic(topic)
        group = grouped.setdefault(
            key,
            {"topic": topic, "questions": [], "headings": set()},
        )
        group["questions"].append(question)
        for heading in question.heading_path:
            normalized_heading = _normalize_topic(heading)
            if normalized_heading:
                group["headings"].add(heading)

    points: list[dict[str, Any]] = []
    for key, group in grouped.items():
        members = group["questions"]
        head = members[0]
        locations: dict[tuple[str, str, str, Any], dict[str, Any]] = {}
        for member in members:
            location_key = (
                member.source_id,
                member.source_title,
                member.locator_type,
                member.locator_start,
            )
            locations.setdefault(
                location_key,
                {
                    "source_id": member.source_id,
                    "source_title": member.source_title,
                    "locator_type": member.locator_type,
                    "locator_start": member.locator_start,
                },
            )
        ordered = sorted(members, key=_question_sort_key)
        matched_weak = _matches_weak_topic(key, weak_keys)
        group_source_ids = {member.source_id for member in members}
        related_material_hits = sum(
            1
            for question in all_questions
            if question.source_id not in group_source_ids
            and any(
                _normalize_topic(heading) == key
                for heading in question.heading_path
            )
        )
        if any(_normalize_topic(topic) == key for topic in material_topics):
            related_material_hits += 1
        order_reasons: list[str] = []
        if matched_weak:
            order_reasons.append("匹配薄弱点")
        if len(members) > 1:
            order_reasons.append(f"真题客观出现 {len(members)} 次")
        if related_material_hits:
            order_reasons.append("课程资料有对应标题")
        points.append(
            {
                "topic": group["topic"],
                "layer": min(len(head.heading_path) or 1, 3),
                "heading_path": list(head.heading_path)[:3],
                "material_locations": list(locations.values())[:4],
                "questions": [
                    {
                        "question_id": member.question_id,
                        "source_id": member.source_id,
                        "source_title": member.source_title,
                        "year": member.year,
                        "locator_type": member.locator_type,
                        "locator_start": member.locator_start,
                    }
                    for member in ordered[:MAX_QUESTIONS_PER_GROUP]
                ],
                "objective_count": len(members),
                "weak_topic_matched": matched_weak,
                "order_reasons": order_reasons,
            }
        )

    def sort_key(point: dict[str, Any]) -> tuple[int, int, str, str]:
        return (
            0 if point["weak_topic_matched"] else 1,
            -point["objective_count"],
            _normalize_topic("、".join(point["heading_path"]) or point["topic"]),
            point["topic"],
        )

    points.sort(key=sort_key)
    return tuple(points[:MAX_KNOWLEDGE_POINTS])


def _compute_uncovered_syllabus_items(
    syllabus: str,
    knowledge_points: tuple[dict[str, Any], ...],
    *,
    material_topics: tuple[str, ...],
) -> tuple[str, ...]:
    known_topics = {
        _normalize_topic(point["topic"])
        for point in knowledge_points
    }
    for point in knowledge_points:
        for heading in point.get("heading_path") or []:
            known_topics.add(_normalize_topic(str(heading)))
    for topic in material_topics:
        normalized = _normalize_topic(topic)
        if normalized:
            known_topics.add(normalized)
    uncovered: list[str] = []
    seen: set[str] = set()
    for item in _syllabus_items(syllabus):
        key = _normalize_topic(item)
        if not key or key in seen:
            continue
        seen.add(key)
        if not any(
            key in candidate or candidate in key
            for candidate in known_topics
            if candidate
        ):
            uncovered.append(item)
        if len(uncovered) >= MAX_SYLLABUS_ITEMS:
            break
    return tuple(uncovered)


def _build_review_suggestions(
    *,
    path: ExamReviewPath,
    knowledge_points: tuple[dict[str, Any], ...],
    stats: dict[str, Any],
    weak_count: int,
    available_hours: float | None,
) -> tuple[str, ...]:
    suggestions: list[str] = []
    if path == ExamReviewPath.WITH_SYLLABUS:
        suggestions.append(
            "先按你的大纲逐条对照下方知识点与资料位置，再进入题组真题自测。"
        )
    else:
        suggestions.append(
            "没有大纲时，先从历年题题组开始，回到每道题对应的资料位置补齐定义与条件。"
        )
    if knowledge_points:
        suggestions.append(
            f"按建议顺序从「{knowledge_points[0]['topic']}」开始；"
            "每个知识点先读资料位置，再做代表性真题。"
        )
    if weak_count:
        suggestions.append(
            f"你登记了 {weak_count} 个薄弱点，排在前面的匹配知识点建议优先安排两轮。"
        )
    if stats.get("question_count"):
        suggestions.append(
            f"历年题共统计到 {stats['question_count']} 道题，"
            "做完一组就回对答案来源，不要跳过定位。"
        )
    if isinstance(available_hours, (int, float)) and available_hours > 0:
        suggestions.append(
            f"按可投入 {available_hours:g} 小时拆分复习块，给每个知识点留出回查资料的时间。"
        )
    suggestions.append(
        "资料或真题没有覆盖的内容保持诚实标注，不要当作已复习完成。"
    )
    return tuple(suggestions)


def _plan_topic_terms(plan: ExamReviewPlan, *, limit: int) -> list[str]:
    terms: list[str] = []
    seen: set[str] = set()
    for point in plan.knowledge_points:
        term = _clean_text(str(point["topic"]), 60)
        key = term.casefold()
        if not term or key in seen:
            continue
        seen.add(key)
        terms.append(term)
        if len(terms) >= limit:
            break
    return terms


def _question_type_of(question: ExamQuestionFact) -> str:
    for heading in reversed(question.heading_path):
        stripped = _SCORE_PAREN_RE.sub("", heading).strip()
        for keyword, key in _QUESTION_TYPE_KEYWORDS:
            if keyword in stripped:
                return key
    return _UNTYPED_KEY


def _matches_weak_topic(group_key: str, weak_keys: set[str]) -> bool:
    if not group_key or not weak_keys:
        return False
    if group_key in weak_keys:
        return True
    return any(
        (weak in group_key or group_key in weak) and min(len(weak), len(group_key)) >= MIN_TOPIC_CHARS
        for weak in weak_keys
    )


def _topic_of_question(question: ExamQuestionFact) -> str:
    """Pick the most specific reviewed heading as the group topic.

    Pure numbering headings (``第 1 题``、``三、``) carry no topic signal and
    are skipped; the source title (with year/semester noise stripped) is the
    honest fallback. Display text keeps its original case; only matching keys
    are casefolded elsewhere.
    """

    for heading in reversed(question.heading_path):
        # Noise prefixes must be stripped before the numbering pattern,
        # otherwise “2014春…” loses its year to the [0-9]+ rule first.
        candidate = _strip_noise_prefix(heading.strip())
        candidate = _TRAILING_PUNCT_RE.sub("", candidate)
        candidate = _SCORE_PAREN_RE.sub("", candidate)
        candidate = _HEADING_PREFIX_RE.sub("", candidate).strip()
        if not candidate or _GENERIC_TOPIC_RE.match(candidate):
            continue
        if len(candidate) >= MIN_TOPIC_CHARS:
            return candidate[:80]
    title = _clean_text(question.source_title, 80)
    title = _SCORE_PAREN_RE.sub("", _HEADING_PREFIX_RE.sub("", title)).strip() or title
    title = _strip_noise_prefix(title)
    if len(title) >= MIN_TOPIC_CHARS:
        return title
    return _clean_text(question.source_title, 80)


def _strip_noise_prefix(value: str) -> str:
    previous: str | None = None
    stripped = value
    while previous != stripped:
        previous = stripped
        stripped = _NOISE_PREFIX_RE.sub("", stripped).lstrip("—－-–~至 ")
    return stripped


_GENERIC_TOPIC_RE = re.compile(
    r"^(?:第\s*[0-9一二三四五六七八九十百]+\s*(?:部分|章|节|题)?|[0-9]+|题目|试题|试卷|答案"
    r"|（?\s*[0-9]+\s*）?)$"
)
_TRAILING_PUNCT_RE = re.compile(r"[。．.，,；;：:\s]+$")
# Reviewed titles often open with administrative noise (“2023—2024学年第二
# 学期”、“2016春季”)；剥离后剩下的才是可读的主题词。只剥前缀，不改写内容。
_NOISE_PREFIX_RE = re.compile(
    r"^(?:"
    r"(?:19|20)\d{2}\s*[—\-－–~至]?\s*(?:(?:19|20)\d{2})?\s*学年?度?"
    r"|(?:19|20)\d{2}\s*(?:春|秋|春夏|秋冬)?[季级]?"
    r"|\d{4}级"
    r"|第\s*[0-9一二三四五六七八九十]+\s*学期"
    r")\s*"
)


def _question_sort_key(question: ExamQuestionFact) -> tuple[Any, ...]:
    start = question.locator_start
    numeric = start if isinstance(start, int) and not isinstance(start, bool) else None
    return (
        question.year if question.year is not None else 10_000,
        0 if numeric is not None else 1,
        numeric if numeric is not None else 0,
        str(question.question_id),
    )


def _syllabus_items(syllabus: str) -> list[str]:
    cleaned = _clean_text(syllabus, 20_000)
    raw_items: list[str] = []
    for chunk in re.split(r"[\n;；]+", cleaned):
        for piece in chunk.split("、"):
            item = _HEADING_PREFIX_RE.sub("", piece).strip()
            if len(item) >= MIN_TOPIC_CHARS:
                raw_items.append(item[:120])
            if len(raw_items) >= MAX_SYLLABUS_ITEMS:
                return raw_items
    return raw_items


def _locator_label(location: dict[str, Any]) -> str:
    locator_type = location.get("locator_type")
    start = location.get("locator_start")
    if locator_type == "page" and start is not None:
        return f"页码 p{start}"
    if locator_type == "slide" and start is not None:
        return f"幻灯片 s{start}"
    if locator_type == "question":
        return f"题号 {location.get('question_id') or start or ''}".strip()
    if locator_type == "heading":
        return "标题定位"
    return "资料内定位"


def _normalize_topic(value: object) -> str:
    return _clean_text(str(value or ""), 200).casefold()


def _clean_unique_list(
    values: list[str], *, limit: int, max_chars: int
) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values or []:
        item = _clean_text(value, max_chars)
        key = item.casefold()
        if not item or key in seen:
            continue
        seen.add(key)
        cleaned.append(item)
        if len(cleaned) >= limit:
            break
    return cleaned


def _clean_text(value: object, max_length: int) -> str:
    if not isinstance(value, str):
        return ""
    normalized = unicodedata.normalize("NFKC", value)
    without_controls = "".join(
        " " if unicodedata.category(character).startswith("C") else character
        for character in normalized
    )
    return " ".join(without_controls.split())[:max_length].strip()
