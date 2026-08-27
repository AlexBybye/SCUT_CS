from __future__ import annotations

import json
from pathlib import Path

import pytest

from scut_senior_api import retrieval_eval
from scut_senior_api.eval_runner import main
from scut_senior_api.retrieval_eval import (
    DEFAULT_GOLDEN_ROOT,
    GoldenEntry,
    _mrr,
    _noise_rate,
    _recall_at,
    load_golden_set,
    run_retrieval_evaluation,
    validate_golden_references,
)
from test_local_corpus_retrieval import COURSE_ID, _build_store

CHUNK_PASSWORD = "security-reviewed-001:h-密码学基础:c01"
CHUNK_ACCESS = "security-reviewed-001:h-access-control:c01"


def _write_golden(
    root: Path,
    course_id: str = COURSE_ID,
    entries: list[dict[str, object]] | None = None,
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{course_id}.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "retrieval-golden-v1",
                "course_id": course_id,
                "entries": entries
                if entries is not None
                else [
                    {
                        "query": "对称加密的密钥如何管理",
                        "expected_chunk_ids": [CHUNK_PASSWORD],
                        "note": "题目 chunk",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def test_load_golden_set_accepts_a_valid_file(tmp_path: Path) -> None:
    _write_golden(tmp_path)
    entries = load_golden_set(tmp_path)
    assert entries == [
        GoldenEntry(
            course_id=COURSE_ID,
            query="对称加密的密钥如何管理",
            expected_chunk_ids=(CHUNK_PASSWORD,),
            note="题目 chunk",
        )
    ]


def test_load_golden_set_rejects_unknown_fields(tmp_path: Path) -> None:
    path = _write_golden(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["surprise"] = True
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError, match="unknown golden set fields"):
        load_golden_set(tmp_path)


def test_load_golden_set_rejects_empty_expected_chunks(tmp_path: Path) -> None:
    _write_golden(
        tmp_path,
        entries=[{"query": "空命中集", "expected_chunk_ids": []}],
    )
    with pytest.raises(ValueError, match="expected_chunk_ids"):
        load_golden_set(tmp_path)


def test_load_golden_set_rejects_duplicate_chunk_ids(tmp_path: Path) -> None:
    _write_golden(
        tmp_path,
        entries=[
            {
                "query": "重复引用",
                "expected_chunk_ids": [CHUNK_PASSWORD, CHUNK_PASSWORD],
            }
        ],
    )
    with pytest.raises(ValueError, match="must be unique"):
        load_golden_set(tmp_path)


def test_load_golden_set_rejects_empty_root(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="no course files"):
        load_golden_set(tmp_path)


def test_metric_helpers_are_deterministic() -> None:
    expected = ("a", "b")
    top = ("a", "x", "b", "y")
    assert _recall_at(expected, top, 2) == 0.5
    assert _recall_at(expected, top, 20) == 1.0
    assert _mrr(expected, top) == 1.0
    assert _mrr(("z",), top) == 0.0
    assert _noise_rate(expected, top) == 0.5
    assert _noise_rate(expected, ()) == 0.0


def test_validate_golden_references_detects_a_missing_chunk(tmp_path: Path) -> None:
    store, _, _ = _build_store(tmp_path)
    entries = [
        GoldenEntry(COURSE_ID, "query", (CHUNK_PASSWORD, "ghost-chunk:c01"))
    ]
    missing = validate_golden_references(store, entries)
    assert missing == [f"{COURSE_ID}: ghost-chunk:c01"]


def test_run_retrieval_evaluation_reports_per_course_metrics(tmp_path: Path) -> None:
    store, version, _ = _build_store(tmp_path)
    golden = tmp_path / "golden"
    _write_golden(
        golden,
        entries=[
            {
                "query": "对称加密的密钥如何管理",
                "expected_chunk_ids": [CHUNK_PASSWORD],
            },
            {
                "query": "explain least privilege access control",
                "expected_chunk_ids": [CHUNK_ACCESS],
            },
        ],
    )
    report_path = tmp_path / "report.json"
    report = run_retrieval_evaluation(
        golden, report_path, store_root=store, min_score=6
    )

    assert report["runner_id"] == "scut-senior-retrieval-eval-v1"
    assert report["corpus_version"] == version
    assert report["summary"]["entry_count"] == 2
    assert report["summary"]["recall_at_5"] == 1.0
    assert report["summary"]["recall_at_20"] == 1.0
    assert report["summary"]["mrr"] == 1.0
    assert report["summary"]["noise_rate"] == 0.0
    assert set(report["by_course"]) == {COURSE_ID}
    assert report["by_course"][COURSE_ID]["entry_count"] == 2
    assert report_path.read_text(encoding="utf-8").strip()


def test_run_retrieval_evaluation_fails_closed_on_missing_reference(
    tmp_path: Path,
) -> None:
    store, _, _ = _build_store(tmp_path)
    golden = tmp_path / "golden"
    _write_golden(
        golden,
        entries=[
            {
                "query": "对称加密的密钥如何管理",
                "expected_chunk_ids": ["does-not-exist:c01"],
            }
        ],
    )
    with pytest.raises(ValueError, match="do not exist in the active corpus"):
        run_retrieval_evaluation(
            golden, tmp_path / "report.json", store_root=store
        )


def test_eval_runner_retrieval_only_cli_writes_report(tmp_path: Path) -> None:
    store, _, _ = _build_store(tmp_path)
    golden = tmp_path / "golden"
    _write_golden(golden)
    report_path = tmp_path / "report.json"
    exit_code = main(
        [
            "--retrieval-only",
            "--golden",
            str(golden),
            "--corpus-store",
            str(store),
            "--report",
            str(report_path),
        ]
    )
    assert exit_code == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["entry_count"] == 1
    assert report["summary"]["recall_at_5"] == 1.0


def test_eval_runner_retrieval_only_cli_requires_report_or_cases() -> None:
    with pytest.raises(SystemExit):
        main(["--retrieval-only"])


def test_retrieval_eval_default_golden_root_is_under_resources() -> None:
    assert DEFAULT_GOLDEN_ROOT.name == "retrieval-golden"
    assert "resources" in DEFAULT_GOLDEN_ROOT.parts


def test_retrieval_eval_module_exposes_schema_versions() -> None:
    assert retrieval_eval.GOLDEN_SCHEMA_VERSION == "retrieval-golden-v1"
    assert retrieval_eval.EVAL_SCHEMA_VERSION == "retrieval-eval-v1"
