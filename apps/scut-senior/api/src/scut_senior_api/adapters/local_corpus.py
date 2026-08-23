from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from scut_senior_worker.corpus_builder import CorpusBuildError, load_active_course

from ..ports import CapabilityUnavailable, RetrievalBatch, RetrievedSource


_WORD_RE = re.compile(r"[a-z0-9_]+(?:[+#][a-z0-9_+#]*)?|[\u3400-\u4dbf\u4e00-\u9fff]+")
_DISABLED_PREFIX = "course is disabled or unavailable:"
_MAX_QUERY_TERMS = 256
# Weighted-overlap relevance floor: drops incidental n-gram collisions
# (a single shared Chinese bigram scores only 2) so weak-noise candidates
# never reach the citation guard; empty result -> honest insufficient_evidence.
_DEFAULT_MIN_SCORE = 6
_MAX_DOCUMENT_TERMS = 4096


class LocalCorpusRetrievalGateway:
    """Deterministic lexical retrieval over one validated active course index."""

    def __init__(
        self,
        store_root: Path,
        *,
        limit: int = 5,
        min_score: int = _DEFAULT_MIN_SCORE,
    ):
        if isinstance(limit, bool) or not 1 <= limit <= 20:
            raise ValueError("local corpus retrieval limit must be between 1 and 20")
        if isinstance(min_score, bool) or not isinstance(min_score, int):
            raise ValueError("local corpus retrieval min score must be an integer")
        if not 1 <= min_score <= 100:
            raise ValueError(
                "local corpus retrieval min score must be between 1 and 100"
            )
        self.store_root = store_root.resolve()
        self.limit = limit
        self.min_score = min_score

    def is_course_available(self, course_id: str) -> bool:
        try:
            load_active_course(self.store_root, course_id)
        except CorpusBuildError as exc:
            if str(exc).startswith(_DISABLED_PREFIX):
                return False
            raise _unavailable() from None
        except (OSError, ValueError, TypeError):
            raise _unavailable() from None
        return True

    def search(self, course_ids: list[str], query: str) -> RetrievalBatch:
        if len(course_ids) != 1 or not course_ids[0]:
            raise CapabilityUnavailable(
                "retrieval",
                "local corpus retrieval requires exactly one explicit course",
            )
        course_id = course_ids[0]
        try:
            index = load_active_course(self.store_root, course_id)
            corpus_version = index["corpus_version"]
            raw_chunks = index["chunks"]
            if not isinstance(corpus_version, str) or not corpus_version:
                raise ValueError("invalid corpus version")
            if not isinstance(raw_chunks, list):
                raise ValueError("invalid chunk collection")
            sources = [_source_from_chunk(chunk, course_id) for chunk in raw_chunks]
            course_pack_version = _load_course_pack_version(
                self.store_root, corpus_version, course_id
            )
        except CorpusBuildError:
            raise _unavailable() from None
        except (json.JSONDecodeError, KeyError, OSError, TypeError, ValueError):
            raise _unavailable() from None

        query_terms = _lexemes(query, max_terms=_MAX_QUERY_TERMS)
        ranked: list[tuple[int, str, RetrievedSource]] = []
        for source in sources:
            score = _score(query, query_terms, source)
            if score >= self.min_score:
                ranked.append((-score, source.chunk_id, source))
        ranked.sort(key=lambda item: (item[0], item[1]))
        return RetrievalBatch(
            tuple(item[2] for item in ranked[: self.limit]),
            corpus_version,
            course_pack_version,
        )


def _source_from_chunk(chunk: Any, expected_course_id: str) -> RetrievedSource:
    if not isinstance(chunk, dict) or chunk.get("course_id") != expected_course_id:
        raise ValueError("course-filtered chunk payload is invalid")
    heading_path = chunk.get("heading_path")
    if not isinstance(heading_path, list) or not all(
        isinstance(heading, str) and heading for heading in heading_path
    ):
        raise ValueError("chunk heading path is invalid")
    required_strings = (
        "chunk_id",
        "source_id",
        "source_title",
        "text",
        "locator_type",
    )
    if any(
        not isinstance(chunk.get(field), str) or not chunk[field]
        for field in required_strings
    ):
        raise ValueError("chunk source payload is invalid")
    question_id = chunk.get("question_id")
    if question_id is not None and not isinstance(question_id, str):
        raise ValueError("chunk question identifier is invalid")
    return RetrievedSource(
        chunk_id=chunk["chunk_id"],
        course_id=expected_course_id,
        source_id=chunk["source_id"],
        source_title=chunk["source_title"],
        text=chunk["text"],
        locator_type=chunk["locator_type"],
        locator_start=chunk.get("locator_start"),
        locator_end=chunk.get("locator_end"),
        question_id=question_id,
        heading_path=tuple(heading_path),
    )


def _load_course_pack_version(
    store_root: Path, corpus_version: str, course_id: str
) -> str:
    candidates_root = (store_root / "candidates").resolve()
    candidate = (candidates_root / corpus_version).resolve()
    candidate.relative_to(candidates_root)
    pack_path = candidate / "course-packs" / f"{course_id}.json"
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    if (
        not isinstance(pack, dict)
        or pack.get("corpus_version") != corpus_version
        or pack.get("course_id") != course_id
        or not isinstance(pack.get("course_pack_version"), str)
        or not pack["course_pack_version"]
    ):
        raise ValueError("course pack version binding is invalid")
    return pack["course_pack_version"]


def _lexemes(value: str, *, max_terms: int = _MAX_DOCUMENT_TERMS) -> frozenset[str]:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    terms: list[str] = []
    seen: set[str] = set()
    for match in _WORD_RE.finditer(normalized):
        token = match.group(0)
        if token[0].isascii():
            candidates = (token,)
        elif len(token) == 1:
            candidates = (token,)
        else:
            candidates = tuple(
                token[index : index + width]
                for width in (2, 3)
                if len(token) >= width
                for index in range(len(token) - width + 1)
            )
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                terms.append(candidate)
                if len(terms) >= max_terms:
                    return frozenset(terms)
    return frozenset(terms)


def _score(
    raw_query: str, query_terms: frozenset[str], source: RetrievedSource
) -> int:
    if not query_terms:
        return 0
    title_terms = _lexemes(source.source_title)
    heading_terms = _lexemes(" ".join(source.heading_path))
    question_terms = _lexemes(source.question_id or "")
    text_terms = _lexemes(source.text)
    score = sum(len(term) for term in query_terms & text_terms)
    score += 4 * sum(len(term) for term in query_terms & title_terms)
    score += 3 * sum(len(term) for term in query_terms & heading_terms)
    score += 3 * sum(len(term) for term in query_terms & question_terms)
    normalized_query = "".join(
        unicodedata.normalize("NFKC", raw_query).casefold().split()
    )
    normalized_text = "".join(
        unicodedata.normalize("NFKC", source.text).casefold().split()
    )
    if normalized_query and normalized_query in normalized_text:
        score += 25
    return score


def _unavailable() -> CapabilityUnavailable:
    return CapabilityUnavailable(
        "retrieval",
        "local corpus is unavailable, invalid, or the requested course is disabled",
    )
