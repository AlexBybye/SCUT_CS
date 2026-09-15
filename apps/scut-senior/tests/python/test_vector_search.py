from __future__ import annotations

from pathlib import Path

import pytest

from scut_senior_api.vector_search import (
    VectorSnapshotCache,
    VectorSnapshotKey,
    load_vector_snapshot,
)
from scut_senior_api.vector_store import VectorStore


def _write_store(path: Path) -> None:
    store = VectorStore(path, dimensions=2, model_id="test-embed-v1")
    try:
        store.bulk_upsert(
            (
                ("chunk-b", "course-a", [0.0, 2.0]),
                ("chunk-a", "course-a", [2.0, 0.0]),
                ("chunk-zero", "course-a", [0.0, 0.0]),
            )
        )
    finally:
        store.close()


def _key(tmp_path: Path) -> VectorSnapshotKey:
    return VectorSnapshotKey(
        store_root=tmp_path,
        corpus_version="corpus-v1",
        course_id="course-a",
        model_id="test-embed-v1",
        dimensions=2,
    )


def test_snapshot_uses_read_only_vectors_and_stable_cosine_ranking(tmp_path: Path) -> None:
    vector_file = tmp_path / "course-a.db"
    _write_store(vector_file)

    snapshot = load_vector_snapshot(_key(tmp_path), vector_file)

    assert snapshot.matrix.flags.writeable is False
    assert snapshot.search_many([[1.0, 0.0], [0.0, 1.0]], k=2) == [
        [(1.0, "chunk-a")],
        [(1.0, "chunk-b")],
    ]


def test_snapshot_cache_reuses_an_immutable_loaded_asset(tmp_path: Path) -> None:
    vector_file = tmp_path / "course-a.db"
    _write_store(vector_file)
    cache = VectorSnapshotCache(max_bytes=1024 * 1024)
    key = _key(tmp_path)

    first = cache.get_or_load(key, vector_file)
    vector_file.unlink()
    second = cache.get_or_load(key, vector_file)

    assert second is first
    assert cache.size_bytes == first.byte_size


def test_snapshot_rejects_a_course_mismatch_in_a_course_scoped_file(tmp_path: Path) -> None:
    vector_file = tmp_path / "course-a.db"
    store = VectorStore(vector_file, dimensions=2, model_id="test-embed-v1")
    try:
        store.upsert("chunk-a", "course-b", [1.0, 0.0])
    finally:
        store.close()

    with pytest.raises(ValueError, match="outside its course"):
        load_vector_snapshot(_key(tmp_path), vector_file)
