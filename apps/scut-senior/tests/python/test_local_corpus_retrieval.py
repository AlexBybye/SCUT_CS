from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from scut_senior_api.adapters.local_corpus import LocalCorpusRetrievalGateway
from scut_senior_api.config import Settings
from scut_senior_api.main import create_app
from scut_senior_api.paths import CONTRACT_ROOT
from scut_senior_api.ports import CapabilityUnavailable, RetrievalBatch
from scut_senior_worker.corpus_builder import (
    activate_candidate,
    build_candidate,
    set_course_enabled,
)
from scut_senior_worker.corpus_validator import MANIFEST_HEADERS


COURSE_ID = "information_security_intro"


def _git(repository: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _build_store(
    tmp_path: Path, *, enabled: bool = True
) -> tuple[Path, str, str]:
    repository = tmp_path / "repository"
    knowledge = repository / "knowledge"
    markdown = knowledge / COURSE_ID / "security.md"
    markdown.parent.mkdir(parents=True)
    markdown.write_text(
        """---
source_id: security-reviewed-001
course_id: information_security_intro
title: 信息安全审核资料
original_file: 学科资料/信息安全/复习资料.docx
document_role: review_outline
year:
locator_type: heading
---

# 密码学基础

对称加密使用同一把密钥完成加密与解密，密钥管理是重要边界。
共同边界用于验证同分候选的稳定排序。

# Access Control

The principle of least privilege limits each account to required permissions.
共同边界用于验证同分候选的稳定排序。
""",
        encoding="utf-8",
    )
    row = {
        "source_id": "security-reviewed-001",
        "course": COURSE_ID,
        "title": "信息安全审核资料",
        "original_path": "学科资料/信息安全/复习资料.docx",
        "format": "docx",
        "document_role": "review_outline",
        "year": "",
        "output_md": f"{COURSE_ID}/security.md",
        "locator_type": "heading",
        "method": "synthetic-test",
        "ocr_used": "false",
        "ocr_confidence": "",
        "ocr_warning": "",
        "status": "passed",
        "reviewer": "Klosure",
        "notes": "synthetic API retrieval fixture",
    }
    with (knowledge / "manifest.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_HEADERS)
        writer.writeheader()
        writer.writerow(row)

    contracts = repository / "apps/scut-senior/packages/contracts/v1"
    contracts.mkdir(parents=True)
    (contracts / "courses.json").write_bytes(
        (CONTRACT_ROOT / "courses.json").read_bytes()
    )
    worker_input = repository / "apps/scut-senior/worker"
    worker_input.mkdir(parents=True)
    (worker_input / "BUILD_INPUT").write_text(
        "synthetic fixed worker input\n", encoding="utf-8"
    )

    _git(repository, "init", "-b", "master")
    _git(repository, "config", "user.name", "Corpus API Test")
    _git(repository, "config", "user.email", "corpus-api@example.invalid")
    _git(
        repository,
        "add",
        "knowledge",
        "apps/scut-senior/worker",
        "apps/scut-senior/packages/contracts/v1",
    )
    _git(repository, "commit", "-m", "fixed reviewed corpus")
    commit = _git(repository, "rev-parse", "HEAD")
    store = tmp_path / "store"
    candidate = build_candidate(
        manifest_path=knowledge / "manifest.csv",
        knowledge_root=knowledge,
        store_root=store,
        source_commit=commit,
        repository_root=repository,
        max_chunk_chars=200,
    )
    activate_candidate(
        store,
        candidate.corpus_version,
        repository_root=repository,
        trusted_master_ref="refs/heads/master",
    )
    if enabled:
        set_course_enabled(store, COURSE_ID, enabled=True)
    return (
        store,
        candidate.corpus_version,
        candidate.metadata["course_pack_versions"][COURSE_ID],
    )


def _workflow_request(conversation_id: str, query: str) -> dict[str, object]:
    return {
        "workflow_type": "knowledge_qa",
        "course_scope": "single",
        "course_id": COURSE_ID,
        "allowed_course_ids": [],
        "conversation_id": conversation_id,
        "model_source": "platform_default",
        "provider_id": "mock",
        "model_id": "deterministic-fixture-v1",
        "user_input": query,
        "answer_mode": "detailed",
        "tone": "teaching_assistant",
        "knowledge_scope": "course_only",
        "include_bilibili_resources": False,
        "context_refs": [],
        "attachments": [],
        "workflow_payload": {"question": query},
    }


def test_local_gateway_ranks_chinese_and_english_deterministically(
    tmp_path: Path,
) -> None:
    store, version, pack_version = _build_store(tmp_path)
    gateway = LocalCorpusRetrievalGateway(store)

    chinese = gateway.search([COURSE_ID], "对称加密的密钥如何管理")
    english = gateway.search([COURSE_ID], "explain least privilege access control")

    assert chinese.corpus_version == version
    assert chinese.course_pack_version == pack_version
    assert chinese.sources[0].heading_path == ("密码学基础",)
    assert english.sources[0].heading_path == ("Access Control",)
    assert all(
        source.course_id == COURSE_ID
        for source in chinese.sources + english.sources
    )
    assert gateway.search([COURSE_ID], "对称加密").sources == gateway.search(
        [COURSE_ID], "对称加密"
    ).sources
    tied = gateway.search([COURSE_ID], "共同边界").sources
    assert len(tied) == 2
    assert [source.chunk_id for source in tied] == sorted(
        source.chunk_id for source in tied
    )


def test_local_gateway_hard_filters_one_course_and_fails_closed(
    tmp_path: Path,
) -> None:
    store, _, _ = _build_store(tmp_path, enabled=False)
    gateway = LocalCorpusRetrievalGateway(store)

    assert gateway.is_course_available(COURSE_ID) is False
    with pytest.raises(CapabilityUnavailable):
        gateway.search([COURSE_ID], "密码学")
    with pytest.raises(CapabilityUnavailable, match="exactly one"):
        gateway.search([COURSE_ID, "cpp"], "密码学")

    (store / "active.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(CapabilityUnavailable):
        gateway.is_course_available(COURSE_ID)
    with pytest.raises(CapabilityUnavailable):
        gateway.search([COURSE_ID], "密码学")


def test_local_gateway_rejects_a_tampered_course_pack_version(
    tmp_path: Path,
) -> None:
    store, version, _ = _build_store(tmp_path)
    pack_path = (
        store
        / "candidates"
        / version
        / "course-packs"
        / f"{COURSE_ID}.json"
    )
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    pack["course_pack_version"] = "course-pack-tampered"
    pack_path.write_text(json.dumps(pack), encoding="utf-8")

    gateway = LocalCorpusRetrievalGateway(store)
    with pytest.raises(CapabilityUnavailable):
        gateway.search([COURSE_ID], "密码学")


def test_explicit_local_mode_uses_only_active_validated_payload_for_s1(
    tmp_path: Path,
) -> None:
    store, version, pack_version = _build_store(tmp_path)
    app = create_app(
        Settings(
            app_env="test",
            retrieval_mode="local_corpus",
            corpus_store_path=store,
            database_path=tmp_path / "local-corpus.db",
            bilibili_resources_enabled=False,
        )
    )
    client = TestClient(app)
    conversation_response = client.post(
        "/api/v1/conversations", json={"course_id": COURSE_ID}
    )
    assert conversation_response.status_code == 201
    conversation_id = conversation_response.json()["conversation_id"]

    response = client.post(
        "/api/v1/workflow-runs",
        json=_workflow_request(conversation_id, "对称加密与密钥管理"),
    )

    assert response.status_code == 201, response.text
    result = response.json()
    assert result["corpus_version"] == version
    assert result["course_pack_version"] == pack_version
    assert result["citations"][0] == {
        "citation_id": "S1",
        "chunk_id": "security-reviewed-001:h-密码学基础:c01",
        "course_id": COURSE_ID,
        "course_title": "信息安全导论",
        "source_id": "security-reviewed-001",
        "source_title": "信息安全审核资料",
        "locator_type": "heading",
        "locator_start": None,
        "locator_end": None,
        "question_id": None,
        "heading_path": ["密码学基础"],
    }
    assert result["workflow_output"]["source_candidate_ids"] == [
        citation["citation_id"] for citation in result["citations"]
    ]
    assert all(
        citation["course_id"] == COURSE_ID for citation in result["citations"]
    )
    retrieval_event = next(
        event for event in result["trace"] if event["node"] == "local_corpus_retrieval"
    )
    assert retrieval_event["result"]["candidate_order"] == result[
        "workflow_output"
    ]["source_candidate_ids"]


def test_local_mode_does_not_fall_back_when_active_is_missing(tmp_path: Path) -> None:
    store = tmp_path / "missing-store"
    client = TestClient(
        create_app(
            Settings(
                app_env="test",
                retrieval_mode="local_corpus",
                corpus_store_path=store,
                database_path=tmp_path / "missing-active.db",
            )
        )
    )

    response = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    )

    assert response.status_code == 503
    assert response.json()["error"]["capability"] == "retrieval"


def test_local_mode_rejects_an_unversioned_course_pack_before_model_call(
    tmp_path: Path,
) -> None:
    app = create_app(
        Settings(
            app_env="test",
            retrieval_mode="local_corpus",
            corpus_store_path=tmp_path / "unused-store",
            database_path=tmp_path / "unversioned-pack.db",
        )
    )

    class UnversionedRetrieval:
        def is_course_available(self, course_id: str) -> bool:
            return course_id == COURSE_ID

        def search(self, course_ids: list[str], query: str) -> RetrievalBatch:
            del course_ids, query
            return RetrievalBatch((), "corpus-test", None)

    class ModelCallSpy:
        called = False

        def generate(self, request, sources, history=()):
            del request, sources, history
            self.called = True
            raise AssertionError("model must not receive an unversioned local batch")

    retrieval = UnversionedRetrieval()
    model = ModelCallSpy()
    app.state.service.retrieval = retrieval
    app.state.service.model = model
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": COURSE_ID}
    ).json()

    response = client.post(
        "/api/v1/workflow-runs",
        json=_workflow_request(conversation["conversation_id"], "密码学"),
    )

    assert response.status_code == 409
    assert "course pack version" in response.json()["error"]["detail"]
    assert model.called is False
