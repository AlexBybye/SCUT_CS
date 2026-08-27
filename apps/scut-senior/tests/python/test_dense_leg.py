from __future__ import annotations

import pytest

from scut_senior_api.embedding import DeterministicHashEmbeddingProvider
from scut_senior_api.fusion import DEFAULT_RRF_K, reciprocal_rank_fusion
from scut_senior_api.vector_store import VectorStore


def test_hash_embedding_is_deterministic_and_unit_norm() -> None:
    provider = DeterministicHashEmbeddingProvider(dimensions=32)
    first = provider.embed(["对称加密"])[0]
    second = provider.embed(["对称加密"])[0]
    assert first == second
    norm = sum(value * value for value in first) ** 0.5
    assert abs(norm - 1.0) < 1e-9


def test_hash_embedding_rejects_bad_dimensions() -> None:
    for bad in (0, -1, True, 2.5):
        with pytest.raises(ValueError):
            DeterministicHashEmbeddingProvider(dimensions=bad)


def test_vector_store_search_and_course_filter(tmp_path) -> None:
    store = VectorStore(tmp_path / "vectors.db", dimensions=3, model_id="test-v1")
    store.upsert("a", "course1", [1.0, 0.0, 0.0])
    store.upsert("b", "course1", [0.0, 1.0, 0.0])
    store.upsert("c", "course2", [1.0, 0.0, 0.0])

    results = store.search([1.0, 0.0, 0.0], k=10)
    # "a" and "c" tie at cosine 1.0 -> ascending chunk_id; "b" is orthogonal
    # (cosine 0) and is dropped by the >0 filter.
    assert [chunk_id for _, chunk_id in results] == ["a", "c"]

    filtered = store.search([1.0, 0.0, 0.0], k=10, course_ids=["course2"])
    assert [chunk_id for _, chunk_id in filtered] == ["c"]


def test_vector_store_rejects_dimension_mismatch(tmp_path) -> None:
    store = VectorStore(tmp_path / "vectors.db", dimensions=2, model_id="test-v1")
    with pytest.raises(ValueError):
        store.upsert("a", "course1", [1.0, 0.0, 0.0])
    with pytest.raises(ValueError):
        store.search([1.0, 0.0, 0.0], k=5)


def test_rrf_fusion_fuses_ranks_and_breaks_ties() -> None:
    fused = reciprocal_rank_fusion(
        [["a", "b", "c"], ["b", "a", "d"]], top_n=10
    )
    # a: 1/61 + 1/62 == b: 1/62 + 1/61 (tie -> ascending id); c == d (1/63).
    assert fused == ["a", "b", "c", "d"]


def test_rrf_fusion_uses_default_k_and_limits_top_n() -> None:
    fused = reciprocal_rank_fusion([["a", "b", "c"]], top_n=2)
    assert fused == ["a", "b"]
    assert DEFAULT_RRF_K == 60


def test_rrf_fusion_validates_parameters() -> None:
    with pytest.raises(ValueError):
        reciprocal_rank_fusion([["a"]], k=0, top_n=1)
    with pytest.raises(ValueError):
        reciprocal_rank_fusion([["a"]], top_n=-1)
