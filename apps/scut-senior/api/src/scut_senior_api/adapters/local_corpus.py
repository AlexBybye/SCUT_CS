from __future__ import annotations

import hashlib
import json
import threading
from pathlib import Path
from typing import Any

from scut_senior_worker.corpus_builder import (
    CorpusBuildError,
    _candidate_directory,
    _load_active,
    _read_json,
    _require_active_candidate_binding,
    _require_version,
    validate_candidate,
)

from ..bm25f import BM25FIndex
from ..ports import CapabilityUnavailable, RetrievalBatch, RetrievedSource


_DISABLED_PREFIX = "course is disabled or unavailable:"
# BM25F relevance floor (PLAN-2 阶段一 步骤 2): drops incidental n-gram
# collisions so weak-noise candidates never reach the citation guard; an empty
# result -> honest insufficient_evidence. Recalibrated from the P0 golden set
# (see retrieval_eval.py), no longer the iteration-1 integer weighted-overlap 6.
_DEFAULT_MIN_SCORE = 1.0


class LocalCorpusRetrievalGateway:
    """Deterministic lexical retrieval over one validated active course index."""

    def __init__(
        self,
        store_root: Path,
        *,
        limit: int = 5,
        min_score: float = _DEFAULT_MIN_SCORE,
    ):
        if isinstance(limit, bool) or not 1 <= limit <= 20:
            raise ValueError("local corpus retrieval limit must be between 1 and 20")
        if isinstance(min_score, bool) or not isinstance(min_score, (int, float)):
            raise ValueError("local corpus retrieval min score must be a number")
        if min_score < 0:
            raise ValueError("local corpus retrieval min score must be >= 0")
        self.store_root = store_root.resolve()
        self.limit = limit
        self.min_score = float(min_score)
        # Full-candidate validation is memoized per active-pointer value (see
        # _load_active_course); these slots are guarded for the FastAPI
        # threadpool, where availability checks run concurrently.
        self._cache_lock = threading.Lock()
        self._validated_pointer_key: bytes | None = None
        self._validated_candidate: Path | None = None
        # BM25F inverted index per course, keyed by corpus_version (candidates
        # are immutable, so a cached index stays valid until activation/rollback
        # moves the pointer to a different version).
        self._index_cache: dict[str, tuple[str, BM25FIndex]] = {}

    def _load_active_course(self, course_id: str) -> dict[str, Any]:
        """``load_active_course`` semantics, amortizing full validation.

        The activated candidate directory is immutable by contract (activation
        and rollback always write a new candidate and a fresh ``active.json``),
        so the expensive whole-candidate ``validate_candidate`` pass only needs
        to run once per active-pointer value. Re-running it on every call made
        each availability check pay O(candidate) cost — with the current
        activated corpus that is seconds per course, which turned every course
        listing into minutes and starved the API threadpool. The memoization
        key is a digest of the parsed pointer itself, so activation, rollback,
        or a course-switch flip forces exactly one fresh validation; malformed
        or missing pointer state keeps failing closed on every call.
        """
        course = _require_version(course_id, "course_id")
        pointer = _load_active(self.store_root)
        if pointer["course_switches"].get(course) is not True:
            raise CorpusBuildError(f"course is disabled or unavailable: {course}")
        candidate = _candidate_directory(
            self.store_root.resolve(), pointer["active_corpus_version"]
        )
        pointer_key = hashlib.sha256(
            json.dumps(pointer, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).digest()
        with self._cache_lock:
            validated = (
                self._validated_candidate
                if pointer_key == self._validated_pointer_key
                else None
            )
        if validated is None:
            validate_candidate(candidate)
            with self._cache_lock:
                self._validated_pointer_key = pointer_key
                self._validated_candidate = candidate
        # The per-call tail (metadata binding + course index read) stays fresh:
        # both are cheap local reads, and the binding check keeps failing closed
        # if metadata and the active pointer ever disagree.
        metadata = _read_json(candidate / "metadata.json")
        _require_active_candidate_binding(pointer, metadata)
        return _read_json(candidate / "courses" / f"{course}.json")

    def is_course_available(self, course_id: str) -> bool:
        try:
            self._load_active_course(course_id)
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
            course_index = self._load_active_course(course_id)
            corpus_version = course_index["corpus_version"]
            raw_chunks = course_index["chunks"]
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

        bm25f_index = self._load_index(course_id, corpus_version, sources)
        source_by_id = {source.chunk_id: source for source in sources}
        selected: list[RetrievedSource] = []
        for score, chunk_id in bm25f_index.score(query):
            if score < self.min_score:
                continue
            source = source_by_id.get(chunk_id)
            if source is None:
                continue
            selected.append(source)
            if len(selected) >= self.limit:
                break
        return RetrievalBatch(
            tuple(selected),
            corpus_version,
            course_pack_version,
        )

    def _load_index(
        self,
        course_id: str,
        corpus_version: str,
        sources: list[RetrievedSource],
    ) -> BM25FIndex:
        with self._cache_lock:
            cached = self._index_cache.get(course_id)
            if cached is not None and cached[0] == corpus_version:
                return cached[1]
        index = BM25FIndex(
            {
                "chunk_id": source.chunk_id,
                "title": source.source_title,
                "heading": " ".join(source.heading_path),
                "question": source.question_id or "",
                "text": source.text,
            }
            for source in sources
        )
        with self._cache_lock:
            self._index_cache[course_id] = (corpus_version, index)
        return index


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


def _unavailable() -> CapabilityUnavailable:
    return CapabilityUnavailable(
        "retrieval",
        "local corpus is unavailable, invalid, or the requested course is disabled",
    )
