"""Single-file vector storage for the dense retrieval leg.

PLAN-2 阶段一 步骤 3 stores dense embeddings in one local file (no Qdrant, no
separate service). This implementation uses a single SQLite database through
the stdlib ``sqlite3`` module and brute-force cosine similarity, which is
adequate at the 24k-chunk corpus scale. The file lives under the candidate
directory so it inherits the activate/rollback version gate for free; a
``sqlite-vec`` / ``lance`` ANN engine is the documented upgrade path if scale
ever demands it (PLAN-2 §6 pins the single-file shape, not a specific engine).
"""

from __future__ import annotations

import math
import sqlite3
import struct
from pathlib import Path
from typing import Iterable, Sequence


class VectorStore:
    """One flat, version-bound table of fp32 vectors keyed by chunk_id."""

    def __init__(self, path: Path, *, dimensions: int, model_id: str):
        if not isinstance(dimensions, int) or isinstance(dimensions, bool) or dimensions < 1:
            raise ValueError("vector dimensions must be a positive integer")
        if not model_id or not isinstance(model_id, str):
            raise ValueError("vector model_id must be a non-empty string")
        self.path = path.resolve()
        self.dimensions = dimensions
        self.model_id = model_id
        self._connection = sqlite3.connect(str(self.path))
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS vectors ("
            " chunk_id TEXT PRIMARY KEY,"
            " course_id TEXT NOT NULL,"
            " vector BLOB NOT NULL"
            ")"
        )

    def upsert(
        self, chunk_id: str, course_id: str, vector: Sequence[float]
    ) -> None:
        values = list(vector)
        if len(values) != self.dimensions:
            raise ValueError(
                f"vector dimension {len(values)} != store dimension {self.dimensions}"
            )
        payload = struct.pack(f"{self.dimensions}f", *values)
        self._connection.execute(
            "INSERT OR REPLACE INTO vectors (chunk_id, course_id, vector) "
            "VALUES (?, ?, ?)",
            (chunk_id, course_id, payload),
        )
        self._connection.commit()

    def bulk_upsert(self, records: Iterable[tuple[str, str, Sequence[float]]]) -> None:
        for chunk_id, course_id, vector in records:
            self.upsert(chunk_id, course_id, vector)

    def search(
        self,
        query_vector: Sequence[float],
        *,
        k: int,
        course_ids: Sequence[str] | None = None,
    ) -> list[tuple[float, str]]:
        """Return ``(cosine_similarity, chunk_id)`` for the top-k vectors,
        ordered by descending similarity then ascending chunk_id."""
        query = list(query_vector)
        if len(query) != self.dimensions:
            raise ValueError(
                f"query dimension {len(query)} != store dimension {self.dimensions}"
            )
        allowed = set(course_ids) if course_ids is not None else None
        scored: list[tuple[float, str]] = []
        for chunk_id, course_id, payload in self._connection.execute(
            "SELECT chunk_id, course_id, vector FROM vectors"
        ):
            if allowed is not None and course_id not in allowed:
                continue
            vector = list(
                struct.unpack(f"{len(payload) // 4}f", payload)
            )
            similarity = _cosine(query, vector)
            if similarity > 0.0:
                scored.append((similarity, chunk_id))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return scored[:k]

    def close(self) -> None:
        self._connection.close()


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or not left:
        return 0.0
    dot = 0.0
    left_norm = 0.0
    right_norm = 0.0
    for a, b in zip(left, right):
        dot += a * b
        left_norm += a * a
        right_norm += b * b
    denominator = math.sqrt(left_norm) * math.sqrt(right_norm)
    if denominator == 0.0:
        return 0.0
    return dot / denominator
