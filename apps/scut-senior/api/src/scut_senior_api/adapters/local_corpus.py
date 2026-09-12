from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Sequence

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
from ..embedding import EmbeddingProvider
from ..fusion import reciprocal_rank_fusion
from ..ports import CapabilityUnavailable, RetrievalBatch, RetrievedSource
from ..query_variants import build_query_variants
from ..retrieval_anchors import find_exact_anchor_matches
from ..rule_rerank import protected_rrf_rerank, rule_rerank
from ..vector_store import VectorStore
from ..vector_search import VectorSnapshotCache, VectorSnapshotKey


_DISABLED_PREFIX = "course is disabled or unavailable:"
# BM25F relevance floor (PLAN-2 阶段一 步骤 2): drops incidental n-gram
# collisions so weak-noise candidates never reach the citation guard; an empty
# result -> honest insufficient_evidence. Recalibrated from the P0 golden set
# (see retrieval_eval.py), no longer the iteration-1 integer weighted-overlap 6.
_DEFAULT_MIN_SCORE = 1.0


@dataclass(frozen=True, slots=True)
class _CourseSearchInput:
    course_id: str
    corpus_version: str
    course_pack_version: str
    sources: tuple[RetrievedSource, ...]


class LocalCorpusRetrievalGateway:
    """Deterministic lexical retrieval over one validated active course index."""

    def __init__(
        self,
        store_root: Path,
        *,
        limit: int = 5,
        min_score: float = _DEFAULT_MIN_SCORE,
        embedding: EmbeddingProvider | None = None,
        vector_search_engine: Literal["scalar", "matrix"] = "matrix",
        vector_snapshot_cache_bytes: int = 256 * 1024 * 1024,
        ranking_strategy: Literal["lexical_first_v1", "protected_rrf_v1"] = (
            "lexical_first_v1"
        ),
    ):
        if isinstance(limit, bool) or not 1 <= limit <= 20:
            raise ValueError("local corpus retrieval limit must be between 1 and 20")
        if isinstance(min_score, bool) or not isinstance(min_score, (int, float)):
            raise ValueError("local corpus retrieval min score must be a number")
        if min_score < 0:
            raise ValueError("local corpus retrieval min score must be >= 0")
        if vector_search_engine not in {"scalar", "matrix"}:
            raise ValueError("vector search engine must be scalar or matrix")
        if ranking_strategy not in {"lexical_first_v1", "protected_rrf_v1"}:
            raise ValueError(
                "ranking strategy must be lexical_first_v1 or protected_rrf_v1"
            )
        self.store_root = store_root.resolve()
        self.limit = limit
        self.min_score = float(min_score)
        # Optional dense leg (PLAN-2 阶段一 步骤 3). ``None`` keeps the gateway
        # lexical-only; the dense leg is only exercised when a provider is wired
        # AND the corpus carries a matching ``-e{model}`` version segment.
        self.embedding = embedding
        self.vector_search_engine = vector_search_engine
        self.ranking_strategy = ranking_strategy
        self._vector_snapshots = VectorSnapshotCache(
            max_bytes=vector_snapshot_cache_bytes
        )
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

    def _load_active_course(
        self, course_id: str, *, pointer: dict[str, Any] | None = None
    ) -> dict[str, Any]:
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
        pointer = pointer if pointer is not None else _load_active(self.store_root)
        if pointer["course_switches"].get(course) is not True:
            raise CorpusBuildError(f"course is disabled or unavailable: {course}")
        candidate = _candidate_directory(
            self.store_root.resolve(), pointer["active_corpus_version"]
        )
        pointer_key = _active_pointer_key(pointer)
        with self._cache_lock:
            validated = (
                self._validated_candidate
                if pointer_key == self._validated_pointer_key
                else None
            )
        if validated is None:
            # Dense identity is checked when the vector file is opened below;
            # keep that explicit ValueError visible to callers. Full candidate
            # validation (including vector completeness) remains available to
            # the corpus build/activation gates.
            validate_candidate(candidate, check_vectors=False)
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
        if (
            not course_ids
            or len(course_ids) != len(set(course_ids))
            or any(not course_id for course_id in course_ids)
        ):
            raise CapabilityUnavailable(
                "retrieval",
                "local corpus retrieval requires a non-empty unique course set",
            )
        try:
            pointer = _load_active(self.store_root)
            pointer_key = _active_pointer_key(pointer)
            inputs = [
                self._prepare_course_input(course_id, pointer=pointer)
                for course_id in course_ids
            ]
        except CorpusBuildError:
            raise _unavailable() from None
        except (json.JSONDecodeError, KeyError, OSError, TypeError, ValueError):
            raise _unavailable() from None

        corpus_versions = {item.corpus_version for item in inputs}
        if len(corpus_versions) != 1:
            raise _unavailable()
        variants_by_course = {
            item.course_id: build_query_variants(item.course_id, query)
            for item in inputs
        }
        vectors_by_query = self._embed_request_variants(variants_by_course.values())
        batches = [
            self._search_course(
                item,
                query,
                variants_by_course[item.course_id],
                vectors_by_query,
            )
            for item in inputs
        ]
        # A result must never combine chunks from before and after an activation
        # or course-switch update. Cached vector matrices remain safe because
        # this pointer check still occurs on every request.
        if _active_pointer_key(_load_active(self.store_root)) != pointer_key:
            raise CapabilityUnavailable(
                "retrieval", "active corpus changed while retrieval was running"
            )
        merged = _round_robin_sources(batches, limit=self.limit)
        return RetrievalBatch(
            tuple(merged),
            inputs[0].corpus_version,
            inputs[0].course_pack_version,
        )

    def _prepare_course_input(
        self, course_id: str, *, pointer: dict[str, Any]
    ) -> _CourseSearchInput:
        course_index = self._load_active_course(course_id, pointer=pointer)
        corpus_version = course_index["corpus_version"]
        raw_chunks = course_index["chunks"]
        if not isinstance(corpus_version, str) or not corpus_version:
            raise ValueError("invalid corpus version")
        if not isinstance(raw_chunks, list):
            raise ValueError("invalid chunk collection")
        sources = tuple(_source_from_chunk(chunk, course_id) for chunk in raw_chunks)
        return _CourseSearchInput(
            course_id=course_id,
            corpus_version=corpus_version,
            course_pack_version=_load_course_pack_version(
                self.store_root, corpus_version, course_id
            ),
            sources=sources,
        )

    def _embed_request_variants(
        self, variants_by_course: Sequence[tuple[str, ...]]
    ) -> dict[str, list[float]]:
        if self.embedding is None:
            return {}
        unique_queries = tuple(
            dict.fromkeys(
                variant for variants in variants_by_course for variant in variants
            )
        )
        if not unique_queries:
            return {}
        vectors = self.embedding.embed(unique_queries)
        if len(vectors) != len(unique_queries):
            raise ValueError("embedding provider returned an unexpected query batch")
        normalized: dict[str, list[float]] = {}
        for query, vector in zip(unique_queries, vectors):
            if len(vector) != self.embedding.dimensions:
                raise ValueError("embedding provider returned an invalid query vector")
            normalized[query] = list(vector)
        return normalized

    def _search_course(
        self,
        item: _CourseSearchInput,
        query: str,
        query_variants: tuple[str, ...],
        vectors_by_query: dict[str, list[float]],
    ) -> list[RetrievedSource]:
        sources = list(item.sources)
        bm25f_index = self._load_index(item.course_id, item.corpus_version, sources)
        source_by_id = {source.chunk_id: source for source in sources}
        lexical_lists = [
            [
                chunk_id
                for score, chunk_id in bm25f_index.score(variant)
                if score >= self.min_score
            ][:50]
            for variant in query_variants
        ]
        lexical_ranked = (
            reciprocal_rank_fusion(lexical_lists, top_n=50)
            if len(lexical_lists) > 1
            else lexical_lists[0]
        )
        dense_ranked = (
            self._dense_chunk_ids(
                item.course_id,
                item.corpus_version,
                [vectors_by_query[variant] for variant in query_variants],
            )
            if self.embedding is not None
            else []
        )
        if self.ranking_strategy == "protected_rrf_v1":
            protected_ids = {
                match.chunk_id for match in find_exact_anchor_matches(query, sources)
            }
            selected_ids = protected_rrf_rerank(
                lexical_ranked,
                dense_ranked,
                protected_ids=protected_ids,
                limit=self.limit,
            )
        else:
            selected_ids = rule_rerank(
                lexical_ranked,
                dense_ranked,
                protected_ids=bm25f_index.exact_match_ids(query),
                limit=self.limit,
            )
        return [
            source_by_id[chunk_id]
            for chunk_id in selected_ids
            if chunk_id in source_by_id
        ]

    def _dense_chunk_ids(
        self,
        course_id: str,
        corpus_version: str,
        query_vectors: Sequence[Sequence[float]],
    ) -> list[str]:
        """Return the dense leg's top-50 chunk ids for the course, or ``[]`` to
        degrade to lexical-only (no dense vectors built for this corpus)."""
        assert self.embedding is not None
        candidate = _candidate_directory(self.store_root, corpus_version)
        metadata = _read_json(candidate / "metadata.json")
        expected = metadata.get("embedding_model_id")
        if expected is None:
            # Lexical-only corpus: it must not silently adopt dense vectors.
            return []
        if expected != self.embedding.model_id:
            raise ValueError(
                "dense leg model mismatch: corpus "
                f"{corpus_version!r} was built with embedding {expected!r} but "
                f"the configured provider is {self.embedding.model_id!r}"
            )
        vector_file = candidate / "vectors" / f"{course_id}.db"
        if not vector_file.exists():
            return []
        if self.vector_search_engine == "scalar":
            store = VectorStore(
                vector_file,
                dimensions=self.embedding.dimensions,
                model_id=self.embedding.model_id,
            )
            try:
                dense_lists = [
                    [
                        chunk_id
                        for _, chunk_id in store.search(
                            query_vector, k=50, course_ids=[course_id]
                        )
                    ]
                    for query_vector in query_vectors
                ]
            finally:
                store.close()
        else:
            snapshot = self._vector_snapshots.get_or_load(
                VectorSnapshotKey(
                    store_root=self.store_root,
                    corpus_version=corpus_version,
                    course_id=course_id,
                    model_id=self.embedding.model_id,
                    dimensions=self.embedding.dimensions,
                ),
                vector_file,
            )
            dense_lists = [
                [chunk_id for _, chunk_id in ranked]
                for ranked in snapshot.search_many(query_vectors, k=50)
            ]
        return (
            reciprocal_rank_fusion(dense_lists, top_n=50)
            if len(dense_lists) > 1
            else dense_lists[0]
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


def _active_pointer_key(pointer: dict[str, Any]) -> bytes:
    return hashlib.sha256(
        json.dumps(pointer, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).digest()


def _round_robin_sources(
    batches: Sequence[Sequence[RetrievedSource]], *, limit: int
) -> list[RetrievedSource]:
    """Preserve the existing cross-course fairness rule after shared encoding."""

    merged: list[RetrievedSource] = []
    for index in range(max((len(batch) for batch in batches), default=0)):
        for batch in batches:
            if index < len(batch):
                merged.append(batch[index])
                if len(merged) >= limit:
                    return merged
    return merged


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
