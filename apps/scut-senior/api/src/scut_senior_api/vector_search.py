"""Read-only, cached dense-vector search for immutable corpus candidates.

The corpus builder continues to write the compact SQLite ``vectors`` files in
``vector_store.py``.  Online retrieval uses this module to load one immutable
course/version snapshot at a time, then performs exact cosine search with a
NumPy matrix.  Keeping writing and serving separate means cache eviction can
never change a corpus asset or its activation semantics.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
import sqlite3
import threading
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    import numpy as np


@dataclass(frozen=True, slots=True)
class VectorSnapshotKey:
    """Identity of one immutable, course-scoped vector asset."""

    store_root: Path
    corpus_version: str
    course_id: str
    model_id: str
    dimensions: int


@dataclass(frozen=True, slots=True)
class VectorSnapshot:
    """Normalized float32 vectors in a deterministic ``chunk_id`` order."""

    key: VectorSnapshotKey
    chunk_ids: tuple[str, ...]
    matrix: "np.ndarray"
    byte_size: int

    def search_many(
        self, query_vectors: Sequence[Sequence[float]], *, k: int
    ) -> list[list[tuple[float, str]]]:
        """Run exact cosine search for each query with stable tie breaking."""

        if k < 1:
            raise ValueError("vector search k must be positive")
        if not query_vectors:
            return []
        np = _numpy()
        queries = np.asarray(query_vectors, dtype=np.float32)
        if queries.ndim != 2 or queries.shape[1] != self.key.dimensions:
            raise ValueError(
                "query vector dimensions do not match the vector snapshot"
            )
        if not np.isfinite(queries).all():
            raise ValueError("query vectors must contain only finite values")
        norms = np.linalg.vector_norm(queries, axis=1, keepdims=True)
        normalized_queries = np.divide(
            queries,
            norms,
            out=np.zeros_like(queries),
            where=norms != 0.0,
        )
        scores = self.matrix @ normalized_queries.T
        results: list[list[tuple[float, str]]] = []
        for column in range(scores.shape[1]):
            ranked = [
                (float(score), self.chunk_ids[index])
                for index, score in enumerate(scores[:, column])
                if score > 0.0
            ]
            ranked.sort(key=lambda item: (-item[0], item[1]))
            results.append(ranked[:k])
        return results


class VectorSnapshotCache:
    """Per-process, byte-bounded LRU for immutable SQLite vector snapshots."""

    def __init__(self, *, max_bytes: int) -> None:
        if isinstance(max_bytes, bool) or max_bytes < 0:
            raise ValueError("vector snapshot cache max_bytes must be non-negative")
        self.max_bytes = max_bytes
        self._entries: OrderedDict[VectorSnapshotKey, VectorSnapshot] = OrderedDict()
        self._size_bytes = 0
        self._lock = threading.Lock()
        self._loading: dict[VectorSnapshotKey, threading.Event] = {}

    @property
    def size_bytes(self) -> int:
        with self._lock:
            return self._size_bytes

    def get_or_load(self, key: VectorSnapshotKey, vector_file: Path) -> VectorSnapshot:
        """Return a cached snapshot, coordinating simultaneous first loads."""

        while True:
            with self._lock:
                cached = self._entries.get(key)
                if cached is not None:
                    self._entries.move_to_end(key)
                    return cached
                pending = self._loading.get(key)
                if pending is None:
                    pending = threading.Event()
                    self._loading[key] = pending
                    leader = True
                else:
                    leader = False
            if leader:
                break
            pending.wait()

        try:
            snapshot = load_vector_snapshot(key, vector_file)
            with self._lock:
                if snapshot.byte_size <= self.max_bytes:
                    self._entries[key] = snapshot
                    self._size_bytes += snapshot.byte_size
                    self._entries.move_to_end(key)
                    while self._size_bytes > self.max_bytes and self._entries:
                        _, evicted = self._entries.popitem(last=False)
                        self._size_bytes -= evicted.byte_size
            return snapshot
        finally:
            with self._lock:
                event = self._loading.pop(key, None)
                if event is not None:
                    event.set()


def load_vector_snapshot(key: VectorSnapshotKey, vector_file: Path) -> VectorSnapshot:
    """Load and normalize a vector file through SQLite's read-only URI mode."""

    np = _numpy()
    path = vector_file.resolve()
    if not path.is_file():
        raise FileNotFoundError(f"vector file is missing: {path}")
    connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    try:
        metadata = dict(connection.execute("SELECT key, value FROM meta"))
        if metadata.get("model_id") != key.model_id or metadata.get("dimensions") != str(
            key.dimensions
        ):
            raise ValueError(
                "vector store identity mismatch: expected "
                f"{key.model_id}/{key.dimensions}, found "
                f"{metadata.get('model_id')}/{metadata.get('dimensions')}"
            )
        rows = list(
            connection.execute(
                "SELECT chunk_id, course_id, vector FROM vectors ORDER BY chunk_id ASC"
            )
        )
    finally:
        connection.close()

    chunk_ids: list[str] = []
    matrix = np.empty((len(rows), key.dimensions), dtype=np.float32)
    expected_bytes = key.dimensions * 4
    for index, (chunk_id, course_id, payload) in enumerate(rows):
        if not isinstance(chunk_id, str) or not isinstance(course_id, str):
            raise ValueError("vector store has invalid chunk or course identifiers")
        if course_id != key.course_id:
            raise ValueError("vector store contains a source outside its course")
        if not isinstance(payload, bytes) or len(payload) != expected_bytes:
            raise ValueError("vector store has an invalid float32 payload")
        vector = np.frombuffer(payload, dtype="<f4", count=key.dimensions)
        if not np.isfinite(vector).all():
            raise ValueError("vector store contains non-finite values")
        matrix[index] = vector
        chunk_ids.append(chunk_id)
    norms = np.linalg.vector_norm(matrix, axis=1, keepdims=True)
    matrix = np.divide(matrix, norms, out=matrix, where=norms != 0.0)
    matrix.flags.writeable = False
    id_bytes = sum(len(chunk_id.encode("utf-8")) for chunk_id in chunk_ids)
    return VectorSnapshot(
        key=key,
        chunk_ids=tuple(chunk_ids),
        matrix=matrix,
        byte_size=matrix.nbytes + id_bytes,
    )


def _numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - packaging assertion
        raise RuntimeError(
            "matrix vector search requires the optional 'onnx' dependencies"
        ) from exc
    return np
