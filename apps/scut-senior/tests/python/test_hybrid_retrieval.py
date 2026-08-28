from __future__ import annotations

from pathlib import Path

import pytest

from scut_senior_api.adapters.local_corpus import LocalCorpusRetrievalGateway
from scut_senior_api.vector_store import VectorStore
from scut_senior_worker.corpus_builder import _candidate_directory
from test_local_corpus_retrieval import COURSE_ID, _build_store

CHUNK_PASSWORD = "security-reviewed-001:h-密码学基础:c01"
CHUNK_ACCESS = "security-reviewed-001:h-access-control:c01"

EMBEDDING_MODEL = "test-embed-v1"


class _ControlledEmbedder:
    model_id = EMBEDDING_MODEL
    dimensions = 2

    def __init__(self, query_vector: list[float]):
        self._query_vector = query_vector

    def embed(self, texts):
        return [list(self._query_vector) for _ in texts]


def _write_vectors(store: Path, version: str, *, model_id: str) -> None:
    candidate = _candidate_directory(store.resolve(), version)
    vector_file = candidate / "vectors" / f"{COURSE_ID}.db"
    vector_file.parent.mkdir(parents=True, exist_ok=True)
    store_obj = VectorStore(vector_file, dimensions=2, model_id=model_id)
    store_obj.upsert(CHUNK_PASSWORD, COURSE_ID, [1.0, 0.0])
    store_obj.upsert(CHUNK_ACCESS, COURSE_ID, [0.0, 1.0])
    store_obj.close()


def test_dense_leg_surfaces_a_chunk_the_lexical_leg_misses(tmp_path: Path) -> None:
    store, version, _ = _build_store(
        tmp_path, embedding_model_id=EMBEDDING_MODEL
    )
    _write_vectors(store, version, model_id=EMBEDDING_MODEL)
    gateway = LocalCorpusRetrievalGateway(
        store, embedding=_ControlledEmbedder([1.0, 0.0])
    )

    # "数学归纳法" matches neither chunk lexically, but the dense leg maps it
    # to the [1.0, 0.0] vector, which is the 密码学基础 chunk.
    batch = gateway.search([COURSE_ID], "数学归纳法")
    assert [source.chunk_id for source in batch.sources] == [CHUNK_PASSWORD]


def test_dense_leg_supplements_but_cannot_displace_exact_lexical_match(
    tmp_path: Path,
) -> None:
    store, version, _ = _build_store(
        tmp_path, embedding_model_id=EMBEDDING_MODEL
    )
    _write_vectors(store, version, model_id=EMBEDDING_MODEL)
    gateway = LocalCorpusRetrievalGateway(
        store, embedding=_ControlledEmbedder([0.0, 1.0]), limit=2
    )

    batch = gateway.search([COURSE_ID], "对称加密")

    assert [source.chunk_id for source in batch.sources] == [
        CHUNK_PASSWORD,
        CHUNK_ACCESS,
    ]


def test_dense_leg_degrades_to_lexical_when_corpus_has_no_embedding_segment(
    tmp_path: Path,
) -> None:
    store, _, _ = _build_store(tmp_path)  # no embedding segment
    gateway = LocalCorpusRetrievalGateway(
        store, embedding=_ControlledEmbedder([1.0, 0.0])
    )
    batch = gateway.search([COURSE_ID], "对称加密的密钥如何管理")
    assert [source.chunk_id for source in batch.sources] == [CHUNK_PASSWORD]


def test_course_query_expansion_can_reach_english_heading(tmp_path: Path) -> None:
    store, _, _ = _build_store(tmp_path)
    gateway = LocalCorpusRetrievalGateway(store)

    batch = gateway.search([COURSE_ID], "访问控制")

    assert [source.chunk_id for source in batch.sources] == [CHUNK_ACCESS]


def test_dense_leg_fails_closed_on_vector_model_mismatch(tmp_path: Path) -> None:
    store, version, _ = _build_store(
        tmp_path, embedding_model_id=EMBEDDING_MODEL
    )
    _write_vectors(store, version, model_id="other-model-v1")
    gateway = LocalCorpusRetrievalGateway(
        store, embedding=_ControlledEmbedder([1.0, 0.0])
    )
    with pytest.raises(ValueError, match="identity mismatch"):
        gateway.search([COURSE_ID], "数学归纳法")


def test_corpus_version_appends_embedding_segment(tmp_path: Path) -> None:
    plain, plain_version, _ = _build_store(tmp_path / "plain")
    dense, dense_version, _ = _build_store(
        tmp_path / "dense", embedding_model_id=EMBEDDING_MODEL
    )
    assert plain_version not in {dense_version}
    assert dense_version.endswith(f"-e{EMBEDDING_MODEL}")
    assert "embedding_model_id" not in _read_metadata(plain, plain_version)
    assert _read_metadata(dense, dense_version)["embedding_model_id"] == EMBEDDING_MODEL


def _read_metadata(store: Path, version: str) -> dict[str, object]:
    import json

    return json.loads(
        (_candidate_directory(store.resolve(), version) / "metadata.json").read_text(
            encoding="utf-8"
        )
    )
