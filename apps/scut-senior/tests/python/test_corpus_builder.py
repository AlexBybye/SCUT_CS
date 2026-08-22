from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

import pytest

from scut_senior_worker.corpus_builder import (
    CorpusBuildError,
    activate_candidate,
    build_candidate,
    load_active_course,
    rollback_active,
    set_course_enabled,
    validate_candidate,
)
from scut_senior_worker.corpus_validator import MANIFEST_HEADERS


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _row(
    *,
    source_id: str,
    output_md: str,
    title: str,
    status: str,
    locator_type: str = "page",
) -> dict[str, str]:
    return {
        "source_id": source_id,
        "course": "linear_algebra",
        "title": title,
        "original_path": f"学科资料/线性代数/{source_id}.pdf",
        "format": "pdf",
        "document_role": "past_exam",
        "year": "2023",
        "output_md": output_md,
        "locator_type": locator_type,
        "method": "synthetic",
        "ocr_used": "false",
        "ocr_confidence": "",
        "ocr_warning": "",
        "status": status,
        "reviewer": "reviewer" if status == "passed" else "",
        "notes": "fixture",
    }


def _write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def _commit(repo: Path, message: str) -> str:
    _git(
        repo,
        "add",
        "apps/scut-senior/knowledge",
        "apps/scut-senior/worker",
        "apps/scut-senior/packages/contracts/v1",
    )
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture()
def fixed_repo(tmp_path: Path) -> tuple[Path, Path, str]:
    repo = tmp_path / "repo"
    knowledge = repo / "apps" / "scut-senior" / "knowledge"
    document = knowledge / "linear_algebra" / "exam.md"
    asset = document.parent / "assets" / "exam" / "p1.png"
    asset.parent.mkdir(parents=True)
    asset.write_bytes(b"synthetic-png")
    document.write_text(
        """---
source_id: exam
course_id: linear_algebra
title: 合成试卷
original_file: 学科资料/线性代数/exam.pdf
document_role: past_exam
year: 2023
locator_type: page
---

<!-- page: 1 -->

# 第一章

导言。

<!-- question: 2023-A-Q1 -->

## 第一题

题干内容。![](assets/exam/p1.png)

<!-- page: 2 -->

续页内容。
""",
        encoding="utf-8",
    )
    # The pending path intentionally does not exist: a build must not open it.
    _write_manifest(
        knowledge / "manifest.csv",
        [
            _row(
                source_id="exam",
                output_md="linear_algebra/exam.md",
                title="合成试卷",
                status="passed",
            ),
            _row(
                source_id="pending-missing",
                output_md="pending/does-not-exist.md",
                title="待审不存在资料",
                status="pending",
            ),
        ],
    )
    worker_source = (
        repo
        / "apps"
        / "scut-senior"
        / "worker"
        / "src"
        / "scut_senior_worker"
        / "corpus_builder.py"
    )
    worker_source.parent.mkdir(parents=True)
    worker_source.write_text("# fixed builder fixture\n", encoding="utf-8")
    courses = (
        repo
        / "apps"
        / "scut-senior"
        / "packages"
        / "contracts"
        / "v1"
        / "courses.json"
    )
    courses.parent.mkdir(parents=True)
    courses.write_text(
        json.dumps(
            {
                "contract_version": "v1",
                "courses": [
                    {
                        "course_id": "linear_algebra",
                        "display_name": "线性代数",
                        "aliases": [],
                        "repository_paths": ["学科资料/线性代数"],
                        "is_open": False,
                        "fixture_available": True,
                    }
                ],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    _git(repo, "init", "-b", "master")
    _git(repo, "config", "user.name", "Corpus Test")
    _git(repo, "config", "user.email", "corpus@example.invalid")
    commit = _commit(repo, "initial corpus")
    return repo, knowledge, commit


def _build(repo: Path, knowledge: Path, commit: str, store: Path):
    return build_candidate(
        manifest_path=knowledge / "manifest.csv",
        knowledge_root=knowledge,
        store_root=store,
        source_commit=commit,
        repository_root=repo,
        max_chunk_chars=200,
    )


def test_build_reads_only_passed_and_preserves_locator_context(
    fixed_repo: tuple[Path, Path, str], tmp_path: Path
) -> None:
    repo, knowledge, commit = fixed_repo
    result = _build(repo, knowledge, commit, tmp_path / "store")

    assert validate_candidate(result.candidate_path)["ok"] is True
    metadata = json.loads(
        (result.candidate_path / "metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["source_commit"] == commit
    assert metadata["source_count"] == 1
    assert metadata["available_courses"] == ["linear_algebra"]
    assert "pending/does-not-exist.md" not in metadata["read_paths"]
    assert metadata["read_paths"] == [
        "linear_algebra/assets/exam/p1.png",
        "linear_algebra/exam.md",
        "manifest.csv",
    ]

    course = json.loads(
        (result.candidate_path / "courses" / "linear_algebra.json").read_text(
            encoding="utf-8"
        )
    )
    question_chunks = [
        chunk for chunk in course["chunks"] if chunk["question_id"] == "2023-A-Q1"
    ]
    assert [chunk["locator_start"] for chunk in question_chunks] == [1, 2]
    assert all(chunk["heading_path"] == ["第一章", "第一题"] for chunk in question_chunks)
    assert question_chunks[0]["assets"] == [
        "assets/linear_algebra/assets/exam/p1.png"
    ]
    assert (
        result.candidate_path
        / "assets"
        / "linear_algebra"
        / "assets"
        / "exam"
        / "p1.png"
    ).read_bytes() == b"synthetic-png"
    assert question_chunks[0]["chunk_id"].startswith("exam:p1:q-2023-a-q1:c")
    assert course["questions"][0]["locator_start"] == 1
    assert course["questions"][0]["locator_end"] == 2


def test_prose_respects_max_chars_and_fenced_exception_is_recorded(
    fixed_repo: tuple[Path, Path, str], tmp_path: Path
) -> None:
    repo, knowledge, _commit_id = fixed_repo
    document = knowledge / "linear_algebra" / "exam.md"
    document.write_text(
        document.read_text(encoding="utf-8")
        + "\n<!-- page: 3 -->\n\n## 长文本\n\n"
        + ("这是需要确定性切分的普通长句。" * 80)
        + "\n\n```text\n"
        + ("x" * 500)
        + "\n```\n",
        encoding="utf-8",
    )
    commit = _commit(repo, "long text corpus")
    result = _build(repo, knowledge, commit, tmp_path / "store")
    course = json.loads(
        (result.candidate_path / "courses" / "linear_algebra.json").read_text(
            encoding="utf-8"
        )
    )
    oversized = [chunk for chunk in course["chunks"] if len(chunk["text"]) > 200]

    assert len(oversized) == 1
    assert oversized[0]["text"].startswith("```text\n")
    assert oversized[0]["text"].endswith("\n```")
    assert all(
        len(chunk["text"]) <= 200 or chunk in oversized
        for chunk in course["chunks"]
    )
    assert result.metadata["oversize_fenced_chunk_count"] == 1


def test_candidate_validation_requires_copied_assets(
    fixed_repo: tuple[Path, Path, str], tmp_path: Path
) -> None:
    repo, knowledge, commit = fixed_repo
    result = _build(repo, knowledge, commit, tmp_path / "store")
    copied_asset = (
        result.candidate_path
        / "assets"
        / "linear_algebra"
        / "assets"
        / "exam"
        / "p1.png"
    )
    copied_asset.unlink()

    with pytest.raises(CorpusBuildError, match="missing copied asset"):
        validate_candidate(result.candidate_path)


def test_candidate_validation_binds_directory_name_and_fails_closed_for_malformed_json(
    fixed_repo: tuple[Path, Path, str], tmp_path: Path
) -> None:
    repo, knowledge, commit = fixed_repo
    result = _build(repo, knowledge, commit, tmp_path / "store")
    metadata_path = result.candidate_path / "metadata.json"
    index_path = result.candidate_path / "courses" / "linear_algebra.json"
    pack_path = result.candidate_path / "course-packs" / "linear_algebra.json"
    metadata_text = metadata_path.read_text(encoding="utf-8")
    index_text = index_path.read_text(encoding="utf-8")
    pack_text = pack_path.read_text(encoding="utf-8")

    malformed_metadata = json.loads(metadata_text)
    malformed_metadata["course_pack_versions"] = []
    metadata_path.write_text(json.dumps(malformed_metadata), encoding="utf-8")
    with pytest.raises(CorpusBuildError, match="course_pack_versions"):
        validate_candidate(result.candidate_path)

    metadata_path.write_text(metadata_text, encoding="utf-8")
    malformed_index = json.loads(index_text)
    malformed_index["chunks"][0]["source_id"] = []
    index_path.write_text(json.dumps(malformed_index), encoding="utf-8")
    with pytest.raises(CorpusBuildError, match="failed closed"):
        validate_candidate(result.candidate_path)

    index_path.write_text(index_text, encoding="utf-8")
    pack_path.write_text(pack_text, encoding="utf-8")
    forged_path = result.candidate_path.with_name("forged-candidate")
    result.candidate_path.rename(forged_path)
    with pytest.raises(CorpusBuildError, match="directory name"):
        validate_candidate(forged_path)


def test_same_fixed_inputs_produce_identical_course_artifacts(
    fixed_repo: tuple[Path, Path, str], tmp_path: Path
) -> None:
    repo, knowledge, commit = fixed_repo
    first = _build(repo, knowledge, commit, tmp_path / "one")
    second = _build(repo, knowledge, commit, tmp_path / "two")

    assert first.corpus_version == second.corpus_version
    assert (first.candidate_path / "courses" / "linear_algebra.json").read_bytes() == (
        second.candidate_path / "courses" / "linear_algebra.json"
    ).read_bytes()
    assert (first.candidate_path / "course-packs" / "linear_algebra.json").read_bytes() == (
        second.candidate_path / "course-packs" / "linear_algebra.json"
    ).read_bytes()


def test_activation_is_separate_course_is_fail_closed_and_rollback_is_reproducible(
    fixed_repo: tuple[Path, Path, str], tmp_path: Path
) -> None:
    repo, knowledge, first_commit = fixed_repo
    store = tmp_path / "store"
    first = _build(repo, knowledge, first_commit, store)
    pointer = activate_candidate(
        store,
        first.corpus_version,
        repository_root=repo,
        trusted_master_ref="refs/heads/master",
    )
    assert pointer["course_switches"] == {"linear_algebra": False}
    assert pointer["source_commit"] == first_commit
    assert pointer["trusted_master_ref"] == "refs/heads/master"
    active_path = store / "active.json"
    active_text = active_path.read_text(encoding="utf-8")
    tampered_pointer = json.loads(active_text)
    tampered_pointer["source_commit"] = "a" * 40
    active_path.write_text(json.dumps(tampered_pointer), encoding="utf-8")
    with pytest.raises(CorpusBuildError, match="source_commit binding mismatch"):
        activate_candidate(
            store,
            first.corpus_version,
            repository_root=repo,
            trusted_master_ref="refs/heads/master",
        )
    active_path.write_text(active_text, encoding="utf-8")
    with pytest.raises(CorpusBuildError, match="enabled must be a boolean"):
        set_course_enabled(store, "linear_algebra", enabled="true")  # type: ignore[arg-type]
    with pytest.raises(CorpusBuildError, match="disabled"):
        load_active_course(store, "linear_algebra")
    set_course_enabled(store, "linear_algebra", enabled=True)
    assert load_active_course(store, "linear_algebra")["source_commit"] == first_commit

    document = knowledge / "linear_algebra" / "exam.md"
    document.write_text(
        document.read_text(encoding="utf-8") + "\n新增审核后段落。\n",
        encoding="utf-8",
    )
    second_commit = _commit(repo, "second corpus")
    second = _build(repo, knowledge, second_commit, store)

    course_path = second.candidate_path / "courses" / "linear_algebra.json"
    original = course_path.read_text(encoding="utf-8")
    corrupted = json.loads(original)
    corrupted["chunks"][0]["source_title"] = "伪造标题"
    course_path.write_text(json.dumps(corrupted, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(CorpusBuildError, match="source_title mismatch"):
        activate_candidate(
            store,
            second.corpus_version,
            repository_root=repo,
            trusted_master_ref="refs/heads/master",
        )
    assert load_active_course(store, "linear_algebra")["source_commit"] == first_commit

    course_path.write_text(original, encoding="utf-8")
    activated = activate_candidate(
        store,
        second.corpus_version,
        repository_root=repo,
        trusted_master_ref="refs/heads/master",
    )
    assert activated["previous_corpus_version"] == first.corpus_version
    assert activated["course_switches"]["linear_algebra"] is True
    rolled_back = rollback_active(
        store,
        repository_root=repo,
        trusted_master_ref="refs/heads/master",
    )
    assert rolled_back["active_corpus_version"] == first.corpus_version
    assert rolled_back["previous_corpus_version"] == second.corpus_version
    assert load_active_course(store, "linear_algebra")["source_commit"] == first_commit


def test_build_rejects_non_fixed_or_dirty_knowledge_checkout(
    fixed_repo: tuple[Path, Path, str], tmp_path: Path
) -> None:
    repo, knowledge, commit = fixed_repo
    with pytest.raises(CorpusBuildError, match="does not match"):
        _build(repo, knowledge, "a" * 40, tmp_path / "wrong")

    (knowledge / "untracked.md").write_text("not reviewed", encoding="utf-8")
    with pytest.raises(CorpusBuildError, match="candidate inputs have"):
        _build(repo, knowledge, commit, tmp_path / "dirty")

    (knowledge / "untracked.md").unlink()
    worker = (
        repo
        / "apps"
        / "scut-senior"
        / "worker"
        / "src"
        / "scut_senior_worker"
        / "corpus_builder.py"
    )
    worker.write_text("# dirty builder fixture\n", encoding="utf-8")
    with pytest.raises(CorpusBuildError, match="candidate inputs have"):
        _build(repo, knowledge, commit, tmp_path / "dirty-worker")

    worker.write_text("# fixed builder fixture\n", encoding="utf-8")
    courses = (
        repo
        / "apps"
        / "scut-senior"
        / "packages"
        / "contracts"
        / "v1"
        / "courses.json"
    )
    courses.write_text(courses.read_text(encoding="utf-8") + " ", encoding="utf-8")
    with pytest.raises(CorpusBuildError, match="candidate inputs have"):
        _build(repo, knowledge, commit, tmp_path / "dirty-contracts")


def test_activation_rejects_candidate_not_merged_to_trusted_master(
    fixed_repo: tuple[Path, Path, str], tmp_path: Path
) -> None:
    repo, knowledge, _master_commit = fixed_repo
    _git(repo, "switch", "-c", "candidate-topic")
    document = knowledge / "linear_algebra" / "exam.md"
    document.write_text(
        document.read_text(encoding="utf-8") + "\n仅在迭代分支的内容。\n",
        encoding="utf-8",
    )
    topic_commit = _commit(repo, "unmerged corpus candidate")
    store = tmp_path / "store"
    candidate = _build(repo, knowledge, topic_commit, store)

    with pytest.raises(CorpusBuildError, match="not merged into trusted master"):
        activate_candidate(
            store,
            candidate.corpus_version,
            repository_root=repo,
            trusted_master_ref="refs/heads/master",
        )
    assert not (store / "active.json").exists()


def test_manifest_without_passed_source_fails_without_creating_candidate(
    fixed_repo: tuple[Path, Path, str], tmp_path: Path
) -> None:
    repo, knowledge, _commit_id = fixed_repo
    rows = [
        _row(
            source_id="pending-missing",
            output_md="pending/does-not-exist.md",
            title="待审不存在资料",
            status="pending",
        )
    ]
    _write_manifest(knowledge / "manifest.csv", rows)
    commit = _commit(repo, "pending only")
    store = tmp_path / "store"
    with pytest.raises(CorpusBuildError, match="no valid passed"):
        _build(repo, knowledge, commit, store)
    assert not (store / "active.json").exists()
    assert not (store / "candidates").exists()
