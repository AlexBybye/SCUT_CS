from pathlib import Path

import pytest

from scut_senior_api.vector_index import build_candidate_vectors
from scut_senior_api.vector_store import VectorStore
from scut_senior_worker.corpus_builder import _candidate_directory
from test_local_corpus_retrieval import _build_store


class _FakeEmbedder:
    model_id = "bge-small-zh-v1.5"
    dimensions = 2

    def embed(self, texts):
        return [[1.0, 0.0] if "密码" in text else [0.0, 1.0] for text in texts]


def test_build_candidate_vectors_writes_course_scoped_sqlite_files(tmp_path: Path) -> None:
    store, version, _ = _build_store(tmp_path, embedding_model_id="bge-small-zh-v1.5")
    candidate = _candidate_directory(store.resolve(), version)
    (store / "active.json").unlink()

    count = build_candidate_vectors(candidate, _FakeEmbedder(), batch_size=1)

    assert count == 2
    vector_store = VectorStore(
        candidate / "vectors" / "information_security_intro.db",
        dimensions=2,
        model_id="bge-small-zh-v1.5",
    )
    try:
        assert vector_store.search([1.0, 0.0], k=2)[0][1].startswith(
            "security-reviewed-001:h-密码学基础"
        )
    finally:
        vector_store.close()


class _FailingSecondBatchEmbedder(_FakeEmbedder):
    def __init__(self) -> None:
        self.calls = 0

    def embed(self, texts):
        self.calls += 1
        if self.calls == 2:
            raise RuntimeError("simulated embedding interruption")
        return super().embed(texts)


def test_vector_build_leaves_no_partial_files_when_embedding_fails(tmp_path: Path) -> None:
    store, version, _ = _build_store(tmp_path, embedding_model_id="bge-small-zh-v1.5")
    candidate = _candidate_directory(store.resolve(), version)
    (store / "active.json").unlink()

    with pytest.raises(RuntimeError, match="simulated embedding interruption"):
        build_candidate_vectors(candidate, _FailingSecondBatchEmbedder(), batch_size=1)

    assert not (candidate / "vectors").exists()
    assert not list(candidate.glob(".vectors-*"))


def test_vector_build_rejects_active_candidate(tmp_path: Path) -> None:
    store, version, _ = _build_store(tmp_path, embedding_model_id="bge-small-zh-v1.5")
    candidate = _candidate_directory(store.resolve(), version)
    (store / "active.json").unlink()
    (store / "active.json").write_text(
        '{"active_corpus_version": "' + version + '"}', encoding="utf-8"
    )

    with pytest.raises(ValueError, match="active corpus"):
        build_candidate_vectors(candidate, _FakeEmbedder())
