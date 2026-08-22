from __future__ import annotations

import json
from pathlib import Path

from scut_senior_api.eval_runner import main, run_evaluation

CASES = Path(__file__).parents[1] / "fixtures" / "evaluation" / "cases.json"
RUNNER = Path(__file__).parents[1] / "fixtures" / "evaluation" / "runner.json"


def test_eval_runner_executes_all_cases_and_reports_per_course(tmp_path: Path) -> None:
    report_path = tmp_path / "report.json"
    report = run_evaluation(CASES, RUNNER, report_path)

    assert report["runner_id"] == "scut-senior-eval-v1"
    assert report["contract_version"] == "v1"
    summary = report["summary"]
    assert summary["total"] == 12
    assert summary["passed"] + summary["failed"] + summary["skipped"] == 12
    assert len(report["cases"]) == 12
    assert {line["outcome"] for line in report["cases"]} <= {
        "passed",
        "failed",
        "skipped",
    }
    # cross-course is disabled by its feature flag; it must be skipped, not run.
    cross = next(
        line for line in report["cases"] if line["case_id"] == "cross-course-scope-001"
    )
    assert cross["outcome"] == "skipped"
    assert "cross_course" in report["by_course"]
    assert report["by_course"]["linear_algebra"]["total"] == 11
    assert report_path.read_text(encoding="utf-8").strip()

    persisted = json.loads(report_path.read_text(encoding="utf-8"))
    assert persisted["cases"] == report["cases"]


def test_eval_fixture_covers_all_five_workflows_and_passes_the_fixture_contract() -> None:
    """The five Workflow types each complete a full run under fixture+mock.

    The three new workflow-specific cases assert the answered/repository/page
    contract the deterministic Mock can honestly satisfy; cases that require
    real corpus locators or model behavior keep failing instead of faking.
    """
    report_path = Path("/tmp/scut-eval-five-workflows.json")
    report = run_evaluation(CASES, RUNNER, report_path)

    covered = {line["workflow_type"] for line in report["cases"]}
    assert covered == {
        "knowledge_qa",
        "exam_review",
        "problem_tutor",
        "mistake_review",
        "temporary_material_reading",
    }
    for case_id in (
        "exam-review-fixture-001",
        "mistake-review-fixture-001",
        "temporary-material-fixture-001",
    ):
        line = next(item for item in report["cases"] if item["case_id"] == case_id)
        assert line["outcome"] == "passed", line


def test_eval_runner_cli_writes_report_and_exit_code_reflects_failures(
    tmp_path: Path,
) -> None:
    report_path = tmp_path / "report.json"
    exit_code = main(
        [
            "--cases",
            str(CASES),
            "--runner",
            str(RUNNER),
            "--report",
            str(report_path),
        ]
    )
    # The deterministic Mock only covers the answered/repository/page contract;
    # the remaining expectations require the real corpus locators and model
    # behavior, so an honest fixture run still reports failures (exit 1).
    assert exit_code == 1
    assert report_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["total"] == 12
    assert report["summary"]["failed"] >= 1


def test_eval_runner_fails_when_runner_references_a_missing_case(tmp_path: Path) -> None:
    runner_path = tmp_path / "runner.json"
    runner_path.write_text(
        json.dumps(
            {
                "fixture_only": True,
                "contract_version": "v1",
                "runner_id": "missing-case",
                "execution_mode": "mock",
                "case_file": "cases.json",
                "case_ids": ["does-not-exist-001"],
                "group_by": ["course_id", "category"],
                "fail_on_missing_case": True,
            }
        ),
        encoding="utf-8",
    )
    try:
        run_evaluation(CASES, runner_path, tmp_path / "report.json")
    except ValueError as exc:
        assert "does-not-exist-001" in str(exc)
    else:
        raise AssertionError("missing case must fail the evaluation")
