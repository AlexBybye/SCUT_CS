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
    knowledge = repository / "apps" / "scut-senior" / "knowledge"
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
        "preview": "false",
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
        "apps/scut-senior/knowledge",
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


def _count_validations(
    monkeypatch: pytest.MonkeyPatch,
) -> dict[str, int]:
    import scut_senior_api.adapters.local_corpus as local_corpus_module

    calls = {"count": 0}
    real_validate = local_corpus_module.validate_candidate

    def counting_validate(candidate_path):
        calls["count"] += 1
        return real_validate(candidate_path)

    monkeypatch.setattr(local_corpus_module, "validate_candidate", counting_validate)
    return calls


def test_availability_amortizes_candidate_validation_per_pointer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One activated candidate is validated once, not once per request.

    The active corpus candidate is immutable by contract; re-running the whole
    1.2 GB validate_candidate pass on every availability check made each
    /api/v1/courses and /api/v1/plugin-registry request take minutes and
    starved the API threadpool (BYOK saves appeared to do nothing).
    """
    store, _, _ = _build_store(tmp_path)
    calls = _count_validations(monkeypatch)
    gateway = LocalCorpusRetrievalGateway(store)

    assert gateway.is_course_available(COURSE_ID) is True
    assert gateway.is_course_available(COURSE_ID) is True
    assert len(gateway.search([COURSE_ID], "对称加密的密钥如何管理").sources) >= 1
    assert calls["count"] == 1


def test_pointer_change_forces_exactly_one_fresh_validation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Validation runs once per unseen active-pointer value, never per request."""
    store, _, _ = _build_store(tmp_path, enabled=False)
    calls = _count_validations(monkeypatch)
    gateway = LocalCorpusRetrievalGateway(store)

    # A disabled course short-circuits before validation.
    assert gateway.is_course_available(COURSE_ID) is False
    assert calls["count"] == 0

    set_course_enabled(store, COURSE_ID, enabled=True)
    assert gateway.is_course_available(COURSE_ID) is True
    assert gateway.is_course_available(COURSE_ID) is True
    assert gateway.is_course_available(COURSE_ID) is True
    assert calls["count"] == 1

    # Disabling never validates; re-enabling restores the exact previous
    # pointer value over the immutable candidate, so its existing validation
    # is still valid and the value-keyed memoization legitimately hits.
    set_course_enabled(store, COURSE_ID, enabled=False)
    assert gateway.is_course_available(COURSE_ID) is False
    set_course_enabled(store, COURSE_ID, enabled=True)
    assert gateway.is_course_available(COURSE_ID) is True
    assert calls["count"] == 1


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
    catalog = client.get("/api/v1/courses")
    assert catalog.status_code == 200
    courses = {course["course_id"]: course for course in catalog.json()["courses"]}
    assert catalog.json()["retrieval_mode"] == "local_corpus"
    assert courses[COURSE_ID]["mock_available"] is False
    assert courses[COURSE_ID]["retrieval_availability"] == "local_corpus"
    assert courses[COURSE_ID]["retrieval_available"] is True
    assert courses[COURSE_ID]["plugin_loaded"] is True
    assert courses[COURSE_ID]["selectable"] is True
    assert courses["linear_algebra"]["retrieval_availability"] == "unavailable"
    assert courses["linear_algebra"]["selectable"] is False

    health = client.get("/api/v1/health").json()
    assert health["local_corpus_mode_configured"] is True
    assert health["local_corpus_available"] is True
    assert health["local_corpus_retrieval_available_course_count"] == 1
    assert health["selectable_course_count"] == 1
    assert health["formal_exit_blocked"] is False

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
    app = create_app(
        Settings(
            app_env="test",
            retrieval_mode="local_corpus",
            corpus_store_path=store,
            database_path=tmp_path / "missing-active.db",
        )
    )
    client = TestClient(app)

    catalog = client.get("/api/v1/courses")
    assert catalog.status_code == 200
    assert catalog.json()["retrieval_mode"] == "local_corpus"
    assert all(
        course["retrieval_availability"] == "unavailable"
        and course["retrieval_available"] is False
        and course["selectable"] is False
        for course in catalog.json()["courses"]
    )

    health = client.get("/api/v1/health").json()
    assert health["local_corpus_mode_configured"] is True
    assert health["local_corpus_available"] is False
    assert health["local_corpus_retrieval_available_course_count"] == 0
    assert health["selectable_course_count"] == 0
    assert health["formal_exit_blocked"] is True

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


def test_relevance_floor_drops_noise_only_matches(tmp_path: Path) -> None:
    """A single shared Chinese bigram scores ~0.36 — below the default floor.

    The floor (PLAN-2 阶段一 步骤 2: BM25F score threshold) keeps incidental
    n-gram collisions away from the citation guard so the workflow answers with
    an honest insufficient_evidence instead of citing weak-noise candidates.
    """
    store, _, _ = _build_store(tmp_path)
    noise_query = "加密算法体系"  # only "加密" collides -> BM25F score ~0.36

    default_gateway = LocalCorpusRetrievalGateway(store)
    assert default_gateway.min_score == 1.0
    assert default_gateway.search([COURSE_ID], noise_query).sources == ()

    permissive = LocalCorpusRetrievalGateway(store, min_score=0.3)
    assert len(permissive.search([COURSE_ID], noise_query).sources) == 1


def test_relevance_floor_keeps_anchored_matches(tmp_path: Path) -> None:
    store, _, _ = _build_store(tmp_path)
    gateway = LocalCorpusRetrievalGateway(store)

    anchored = gateway.search([COURSE_ID], "对称加密的密钥如何管理")
    assert anchored.sources
    assert anchored.sources[0].heading_path == ("密码学基础",)


def test_relevance_floor_rejects_out_of_range_values(tmp_path: Path) -> None:
    store, _, _ = _build_store(tmp_path)
    for bad in (-1, -0.1, True, "6"):
        with pytest.raises(ValueError):
            LocalCorpusRetrievalGateway(store, min_score=bad)


def test_settings_rejects_retrieval_min_score_out_of_range() -> None:
    from scut_senior_api.config import UnsafeRuntimeConfiguration

    for bad in (-3, -0.5):
        with pytest.raises(UnsafeRuntimeConfiguration):
            Settings(retrieval_min_score=bad).assert_safe()


def test_context_carry_query_prepends_recent_user_turns() -> None:
    from scut_senior_api.service import ConversationTurn, _compose_context_carry_query

    history = (
        ConversationTurn(role="user", content="解释 2019-2020年度线性代数期末卷A 的第 1 题。"),
        ConversationTurn(role="assistant", content="已根据仓库资料引用该卷第 1 题作答。"),
    )
    combined = _compose_context_carry_query("再用分步骤的方式把这道题重新讲一遍。", history)
    assert "2019-2020年度线性代数期末卷A" in combined
    assert "再用分步骤的方式" in combined
    assert "已根据仓库资料引用" not in combined

    assistant_only = (
        ConversationTurn(role="assistant", content="只有助手轮次时不产生回退查询。"),
    )
    assert (
        _compose_context_carry_query("把这道题再讲一遍。", assistant_only) == ""
    )


def test_exam_review_without_syllabus_anchors_on_plan_paper_titles() -> None:
    from scut_senior_api.exam_review import (
        ExamReviewPath,
        ExamReviewPlan,
        compose_retrieval_query,
    )

    plan = ExamReviewPlan(
        plan_version="exam-review-plan-v2",
        course_id="linear_algebra",
        path=ExamReviewPath.WITHOUT_SYLLABUS,
        priority_order=("past_exams",),
        scope_statement="s",
        evidence_boundary="e",
        ai_sample_policy="a",
        knowledge_points=(
            {
                "topic": "初等行变换",
                "questions": [
                    {
                        "question_id": "linear-algebra-012-Q1",
                        "source_id": "linear-algebra-012",
                        "source_title": "2019-2020年度线性代数期末卷A",
                        "year": 2020,
                    }
                ],
            },
        ),
        past_exam_stats={
            "questions": [
                {
                    "question_id": "linear-algebra-012-Q1",
                    "source_id": "linear-algebra-012",
                    "source_title": "2019-2020年度线性代数期末卷A",
                    "year": 2019,
                }
            ]
        },
        review_suggestions=(),
        uncovered_items=(),
    )
    query = compose_retrieval_query(
        syllabus=None,
        weak_topics=["初等行变换"],
        plan=plan,
        review_question="没有大纲，按历年题带我复习。",
    )
    assert "2019-2020年度线性代数期末卷A" in query


def test_followup_turn_regains_anchor_via_context_carry(tmp_path: Path) -> None:
    """Floor drops the noise-only follow-up query; the context-carry retry
    re-anchors it against the prior user turn so the run still cites."""
    store, version, pack_version = _build_store(tmp_path)
    app = create_app(
        Settings(
            app_env="test",
            retrieval_mode="local_corpus",
            corpus_store_path=store,
            database_path=tmp_path / "context-carry.db",
            bilibili_resources_enabled=False,
        )
    )
    client = TestClient(app)
    conversation_response = client.post(
        "/api/v1/conversations", json={"course_id": COURSE_ID}
    )
    assert conversation_response.status_code == 201
    conversation_id = conversation_response.json()["conversation_id"]

    first = client.post(
        "/api/v1/workflow-runs",
        json=_workflow_request(conversation_id, "对称加密的密钥如何管理"),
    )
    assert first.status_code == 201, first.text
    assert first.json()["citations"]

    followup = client.post(
        "/api/v1/workflow-runs",
        json=_workflow_request(
            conversation_id, "再用分步骤的方式把这道题重新讲一遍。"
        ),
    )
    assert followup.status_code == 201, followup.text
    result = followup.json()
    assert result["run_status"] == "completed"
    carry_event = next(
        event
        for event in result["trace"]
        if event["node"] == "retrieval_context_carry"
    )
    assert carry_event["result"]["hit_count"] == 0
    assert carry_event["result"]["candidate_count"] >= 1
    assert "2019" not in carry_event["result"]["rewritten_query"]
    assert carry_event["result"]["rewritten_query"]
    assert result["citations"]
    assert result["corpus_version"] == version
    assert result["course_pack_version"] == pack_version
