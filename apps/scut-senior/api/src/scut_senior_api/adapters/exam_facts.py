"""Corpus-fact providers for the deterministic exam-review planner.

Two adapters supply ``ExamCorpusFacts``:

- ``LocalCorpusExamFactsProvider`` reads the validated active course pack
  (question index plus per-source year/document role) through the same
  active-pointer binding the retrieval gateway uses.
- ``FixtureExamFactsProvider`` derives the same shape from the synthetic
  passed fixture corpus only; it never scans real course materials.

Both providers are read-only. They never receive user payload data, never
write course packs, and never contact a model or BYOK gateway: course-pack
construction stays an offline worker concern (SOP §10.2 课程包构建不使用普通
用户 BYOK).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scut_senior_worker.corpus_builder import (
    CorpusBuildError,
    _candidate_directory,
    load_active_course,
)
from scut_senior_worker.corpus_validator import parse_markdown, validate_corpus

from ..exam_review import (
    ExamCorpusFacts,
    ExamQuestionFact,
    ExamSourceFact,
)
from ..paths import FIXTURE_ROOT


class ExamFactsUnavailable(LookupError):
    """Raised when reviewed exam facts cannot be served for a course."""


def _coerce_year(value: Any) -> int | None:
    """Normalize reviewed year values to ``int | None``.

    The manifest contract stores years as strings; blank/unknown stays
    ``None``. Anything non-numeric is treated as unknown, never guessed.
    """

    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip()
    return int(text) if text.isdigit() else None


class LocalCorpusExamFactsProvider:
    """Load exam facts from the validated active course pack."""

    def __init__(self, store_root: Path):
        self.store_root = store_root.resolve()

    def load(self, course_id: str) -> ExamCorpusFacts:
        try:
            index = load_active_course(self.store_root, course_id)
            corpus_version = index["corpus_version"]
            if not isinstance(corpus_version, str) or not corpus_version:
                raise ValueError("invalid corpus version")
            pack = self._load_pack(corpus_version, course_id)
        except CorpusBuildError as exc:
            raise ExamFactsUnavailable(str(exc)) from None
        except (KeyError, OSError, TypeError, ValueError) as exc:
            raise ExamFactsUnavailable(
                f"active course pack is unavailable for {course_id}: {exc}"
            ) from None
        return _facts_from_pack_payload(course_id, corpus_version, pack)

    def _load_pack(self, corpus_version: str, course_id: str) -> dict[str, Any]:
        candidates_root = (self.store_root / "candidates").resolve()
        candidate = _candidate_directory(self.store_root, corpus_version)
        pack_path = candidate / "course-packs" / f"{course_id}.json"
        # Defence in depth alongside _candidate_directory's own traversal check.
        pack_path.resolve().relative_to(candidates_root)
        return json.loads(pack_path.read_text(encoding="utf-8"))


class FixtureExamFactsProvider:
    """Load exam facts from the synthetic passed fixture corpus."""

    def __init__(self, knowledge_root: Path | None = None):
        self.knowledge_root = knowledge_root or FIXTURE_ROOT / "corpus"
        self.manifest_path = self.knowledge_root / "manifest.csv"

    def load(self, course_id: str) -> ExamCorpusFacts:
        if not self.manifest_path.exists():
            raise ExamFactsUnavailable("fixture corpus manifest is missing")
        from scut_senior_worker.corpus_builder import _chunk_document

        report = validate_corpus(self.manifest_path, self.knowledge_root)
        if report.errors:
            raise ExamFactsUnavailable(
                "synthetic corpus fixture failed validation: "
                + "; ".join(report.errors[:3])
            )
        sources: list[ExamSourceFact] = []
        questions: list[ExamQuestionFact] = []
        heading_topics: list[str] = []
        matched_course = False
        for record in report.searchable_sources:
            if record["course_id"] != course_id:
                continue
            matched_course = True
            sources.append(
                ExamSourceFact(
                    source_id=str(record["source_id"]),
                    source_title=str(record["source_title"]),
                    document_role=str(record.get("document_role") or ""),
                    year=_coerce_year(record.get("year")),
                )
            )
            markdown_path = self.knowledge_root / str(record["output_md"])
            try:
                parsed = parse_markdown(markdown_path)
            except (OSError, ValueError) as exc:
                raise ExamFactsUnavailable(str(exc)) from None
            heading_topics.extend(heading.text for heading in parsed.headings)
            if record.get("document_role") not in {
                "past_exam",
                "past_exam_answer",
                "practice_exam",
            }:
                continue
            # Reuse the corpus chunker so per-question heading stacks stay
            # identical to what the active course pack records.
            chunks = _chunk_document(
                parsed=parsed,
                source={
                    "course_id": record["course_id"],
                    "document_role": record.get("document_role") or "",
                    "locator_type": record.get("locator_type") or "none",
                    "output_md": record["output_md"],
                    "source_id": record["source_id"],
                    "source_title": record["source_title"],
                    "year": record.get("year"),
                },
                markdown_path=markdown_path,
                knowledge_root=self.knowledge_root,
                max_chunk_chars=1200,
            )
            seen_questions: set[str] = set()
            for chunk in chunks:
                question_id = chunk.get("question_id")
                if (
                    question_id is None
                    or question_id in seen_questions
                    or not isinstance(question_id, str)
                ):
                    continue
                seen_questions.add(question_id)
                questions.append(
                    ExamQuestionFact(
                        question_id=question_id,
                        source_id=str(record["source_id"]),
                        source_title=str(record["source_title"]),
                        year=_coerce_year(record.get("year")),
                        heading_path=tuple(chunk.get("heading_path") or ()),
                        locator_type=str(chunk.get("locator_type") or "none"),
                        locator_start=chunk.get("locator_start"),
                        locator_end=chunk.get("locator_end"),
                    )
                )
        if not matched_course:
            # Fail closed: a course without any reviewed fixture source must
            # not silently serve an "empty corpus" plan.
            raise ExamFactsUnavailable(
                f"no reviewed fixture sources for course {course_id}"
            )
        return ExamCorpusFacts(
            course_id=course_id,
            corpus_version="fixture-corpus-v1",
            course_pack_version=None,
            sources=tuple(sources),
            questions=tuple(questions),
            heading_topics=_dedupe(heading_topics),
        )


def _facts_from_pack_payload(
    course_id: str,
    corpus_version: str,
    pack: dict[str, Any],
) -> ExamCorpusFacts:
    if (
        not isinstance(pack, dict)
        or pack.get("course_id") != course_id
        or pack.get("corpus_version") != corpus_version
    ):
        raise ExamFactsUnavailable("course pack identity binding is invalid")
    raw_sources = pack.get("sources")
    raw_questions = pack.get("questions")
    if not isinstance(raw_sources, list) or not isinstance(raw_questions, list):
        raise ExamFactsUnavailable("course pack facts payload is invalid")
    source_year: dict[str, int | None] = {}
    sources: list[ExamSourceFact] = []
    for source in raw_sources:
        if not isinstance(source, dict) or not isinstance(source.get("source_id"), str):
            raise ExamFactsUnavailable("course pack source record is invalid")
        year = _coerce_year(source.get("year"))
        source_year[source["source_id"]] = year
        sources.append(
            ExamSourceFact(
                source_id=source["source_id"],
                source_title=str(source.get("source_title") or ""),
                document_role=str(source.get("document_role") or ""),
                year=year,
            )
        )
    questions: list[ExamQuestionFact] = []
    for question in raw_questions:
        if not isinstance(question, dict):
            raise ExamFactsUnavailable("course pack question record is invalid")
        question_id = question.get("question_id")
        source_id = question.get("source_id")
        if not isinstance(question_id, str) or not isinstance(source_id, str):
            raise ExamFactsUnavailable("course pack question record is invalid")
        heading_path = question.get("heading_path")
        if not isinstance(heading_path, list) or not all(
            isinstance(heading, str) for heading in heading_path
        ):
            raise ExamFactsUnavailable("course pack question heading path is invalid")
        questions.append(
            ExamQuestionFact(
                question_id=question_id,
                source_id=source_id,
                source_title=str(question.get("source_title") or ""),
                year=source_year.get(source_id),
                heading_path=tuple(heading_path),
                locator_type=str(question.get("locator_type") or "none"),
                locator_start=question.get("locator_start"),
                locator_end=question.get("locator_end"),
            )
        )
    heading_topics = [
        str(heading.get("heading_path")[-1])
        for heading in pack.get("heading_index", [])
        if isinstance(heading, dict)
        and isinstance(heading.get("heading_path"), list)
        and heading.get("heading_path")
        and isinstance(heading["heading_path"][-1], str)
    ]
    return ExamCorpusFacts(
        course_id=course_id,
        corpus_version=corpus_version,
        course_pack_version=(
            pack["course_pack_version"]
            if isinstance(pack.get("course_pack_version"), str)
            else None
        ),
        sources=tuple(sources),
        questions=tuple(questions),
        heading_topics=_dedupe(heading_topics),
    )


def _dedupe(values: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        key = value.strip()
        if not key or key.casefold() in seen:
            continue
        seen.add(key.casefold())
        unique.append(key)
    return tuple(unique)
