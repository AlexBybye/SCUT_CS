"""Execute the SCUT evaluation case set against a service instance.

The runner drives the in-process API service (fixture retrieval and the
deterministic Mock model by default) with every case from ``cases.json``,
validates the expected answer/evidence/citation fields, and writes a JSON
report with per-course aggregation. Outcomes are reported honestly: a case
passes only when the running pipeline actually satisfies its expectations.
Fixture cases document pipeline contracts; the real corpus/model evaluation
is run with the same runner against a live service later.

Usage:
    scut-senior-eval --cases tests/fixtures/evaluation/cases.json \
        --runner tests/fixtures/evaluation/runner.json --report out.json
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from .adapters.mock import MockIdentityProvider
from .config import Settings
from .contracts import WorkflowRunRequest, WorkflowType
from .main import create_app
from .ports import UserIdentity

RUNNER_ID = "scut-senior-eval-v1"
CONTRACT_VERSION = "v1"

_MOCK_USER: UserIdentity = MockIdentityProvider().current_user()

_WORKFLOW_NAMES = {workflow.value for workflow in WorkflowType}


def _payload_for(
    workflow_type: str, content: str, case: dict[str, object]
) -> dict[str, object]:
    if workflow_type == "knowledge_qa":
        return {"question": content}
    if workflow_type == "exam_review":
        # An explicit null ``syllabus`` selects the 无大纲 path; only an
        # absent key falls back to the turn content.
        syllabus = case["syllabus"] if "syllabus" in case else content
        return {
            "syllabus": syllabus,
            "exam_date": None,
            "available_hours": 4,
            "goals": [],
            "weak_topics": list(case.get("weak_topics") or []),
        }
    if workflow_type == "problem_tutor":
        return {
            "problem": content,
            "user_answer": None,
            "help_level": "step_by_step",
            "problem_source": None,
        }
    if workflow_type == "mistake_review":
        return {
            "problem": content,
            "original_answer": "（用例未提供原答案）",
            "reference_answer": None,
            "review_focus": None,
        }
    if workflow_type == "temporary_material_reading":
        return {"material_title": None, "material_text": content, "reading_goal": None}
    raise ValueError(f"unsupported workflow_type: {workflow_type}")


def _request_for_case(
    conversation_id: str, case: dict[str, object], content: str
) -> dict[str, object]:
    workflow_type = str(case["workflow_type"])
    if workflow_type not in _WORKFLOW_NAMES:
        raise ValueError(f"unknown workflow_type in case: {workflow_type}")
    return {
        "workflow_type": workflow_type,
        "course_scope": case["course_scope"],
        "course_id": case.get("course_id"),
        "allowed_course_ids": list(case.get("allowed_course_ids") or []),
        "conversation_id": conversation_id,
        "model_source": "platform_default",
        "provider_id": "mock",
        "model_id": "deterministic-fixture-v1",
        "user_input": content,
        "answer_mode": "detailed",
        "tone": "teaching_assistant",
        "knowledge_scope": case["knowledge_scope"],
        "include_bilibili_resources": False,
        "context_refs": [],
        "attachments": [],
        "workflow_payload": _payload_for(workflow_type, content, case),
    }


def _check_expected(
    result: Any, expected: dict[str, object]
) -> list[str]:
    reasons: list[str] = []
    actual_status = result.answer_status.value
    expected_status = expected.get("answer_status")
    if expected_status is not None and actual_status != expected_status:
        reasons.append(f"answer_status={actual_status} != {expected_status}")
    actual_evidence = result.evidence_status.value
    expected_evidence = expected.get("evidence_status")
    if expected_evidence is not None and actual_evidence != expected_evidence:
        reasons.append(f"evidence_status={actual_evidence} != {expected_evidence}")
    block_types = {block.type for block in result.answer_blocks}
    for block_type in expected.get("required_answer_block_types") or []:
        if block_type not in block_types:
            reasons.append(f"缺少回答块 {block_type}")
    requires_citation = bool(expected.get("requires_citation"))
    if requires_citation and not result.citations:
        reasons.append("requires_citation 但没有任何仓库引用")
    if not requires_citation and result.citations:
        reasons.append("不应有仓库引用但返回了引用")
    allows_general = expected.get("allows_general", True)
    if not allows_general and "general" in block_types:
        reasons.append("allows_general=false 但返回了通用补充块")
    locator_types = {citation.locator_type for citation in result.citations}
    for locator in expected.get("required_locator_types") or []:
        if locator not in locator_types:
            reasons.append(f"引用缺少 locator_type={locator}")
    # Iteration 5: deterministic exam-review plan expectations.
    requires_plan = bool(expected.get("requires_exam_review_plan"))
    exam_output = (result.workflow_output or {}).get("exam_review")
    if requires_plan and not isinstance(exam_output, dict):
        reasons.append("requires_exam_review_plan 但结果没有备考复习计划")
    expected_path = expected.get("review_path")
    if expected_path is not None:
        if not isinstance(exam_output, dict):
            reasons.append(f"review_path={expected_path} 但没有备考复习计划")
        elif exam_output.get("path") != expected_path:
            reasons.append(
                f"review_path={exam_output.get('path')} != {expected_path}"
            )
    return reasons


def _run_case(
    app: Any, case: dict[str, object]
) -> tuple[str, list[str]]:
    if case["course_scope"] == "cross":
        return "skipped", ["cross_course_disabled_by_feature_flag"]
    conversation = app.state.service.create_conversation(
        _MOCK_USER, str(case["course_id"])
    )
    last_run = None
    for turn in case["turns"]:
        if turn.get("role") != "user":
            continue
        content = str(turn.get("content") or "")
        request = WorkflowRunRequest.model_validate(
            _request_for_case(conversation.conversation_id, case, content)
        )
        last_run = app.state.service.run(_MOCK_USER, request)
    if last_run is None:
        return "failed", ["用例没有 user 轮次"]
    reasons = _check_expected(last_run, case["expected"])
    return ("passed" if not reasons else "failed"), reasons


def _report_line(case: dict[str, object], outcome: str, reasons: list[str]) -> dict[str, object]:
    return {
        "case_id": case["case_id"],
        "category": case["category"],
        "course_id": case.get("course_id"),
        "workflow_type": case["workflow_type"],
        "outcome": outcome,
        "reasons": reasons,
    }


def run_evaluation(
    cases_path: Path,
    runner_path: Path | None,
    report_path: Path,
) -> dict[str, object]:
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    runner = (
        json.loads(runner_path.read_text(encoding="utf-8"))
        if runner_path is not None
        else None
    )
    case_by_id = {case["case_id"]: case for case in cases["cases"]}
    if runner is not None and runner.get("fail_on_missing_case"):
        missing = [
            case_id
            for case_id in runner.get("case_ids", [])
            if case_id not in case_by_id
        ]
        if missing:
            raise ValueError(f"runner 引用了缺失的 case: {missing}")

    with tempfile.TemporaryDirectory(prefix="scut-senior-eval-") as tmp:
        app = create_app(
            Settings(app_env="test", database_path=Path(tmp) / "eval.db")
        )
        lines: list[dict[str, object]] = []
        for case in cases["cases"]:
            try:
                outcome, reasons = _run_case(app, case)
            except Exception as exc:  # noqa: BLE001 - report any pipeline failure
                outcome, reasons = "failed", [f"{type(exc).__name__}: {exc}"]
            lines.append(_report_line(case, outcome, reasons))

    by_course: dict[str, Counter[str]] = {}
    for line in lines:
        key = str(line["course_id"] or "cross_course")
        by_course.setdefault(key, Counter())["total"] += 1
        by_course[key][str(line["outcome"])] += 1
    summary = Counter(line["outcome"] for line in lines)
    report: dict[str, object] = {
        "runner_id": RUNNER_ID,
        "contract_version": CONTRACT_VERSION,
        "fixture_only": True,
        "executed_at": datetime.now(UTC).isoformat(),
        "summary": {
            "total": len(lines),
            "passed": summary["passed"],
            "failed": summary["failed"],
            "skipped": summary["skipped"],
        },
        "by_course": {
            course: dict(counts)
            for course, counts in sorted(by_course.items())
        },
        "cases": lines,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cases",
        type=Path,
        required=True,
        help="evaluation cases.json path",
    )
    parser.add_argument(
        "--runner",
        type=Path,
        help="optional runner.json path (validates referenced case ids)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        required=True,
        help="output report.json path",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = run_evaluation(args.cases, args.runner, args.report)
    summary = report["summary"]
    print(
        f"evaluation: {summary['total']} cases, "
        f"{summary['passed']} passed, {summary['failed']} failed, "
        f"{summary['skipped']} skipped -> {args.report}"
    )
    for line in report["cases"]:
        if line["outcome"] != "passed":
            print(
                f"  [{line['outcome']}] {line['case_id']}: "
                + "; ".join(str(reason) for reason in line["reasons"])
            )
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
