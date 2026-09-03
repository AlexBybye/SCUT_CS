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
import os
import sys
import tempfile
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from .adapters.mock import MockIdentityProvider
from .adapters.openrouter import UrllibJsonHttpClient
from .config import Settings
from .adapters.onnx import OnnxEmbeddingProvider
from .contracts import WorkflowRunRequest, WorkflowType
from .main import create_app
from .paths import APP_ROOT
from .ports import UserIdentity
from .retrieval_eval import (
    DEFAULT_CORPUS_STORE,
    DEFAULT_GOLDEN_ROOT,
    run_retrieval_evaluation,
)

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
    conversation_id: str,
    case: dict[str, object],
    content: str,
    *,
    provider_id: str = "mock",
    model_id: str = "deterministic-fixture-v1",
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
        "provider_id": provider_id,
        "model_id": model_id,
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
    app: Any,
    case: dict[str, object],
    *,
    provider_id: str = "mock",
    model_id: str = "deterministic-fixture-v1",
) -> tuple[str, list[str], dict[str, object]]:
    if case["course_scope"] == "cross":
        return "skipped", ["cross_course_disabled_by_feature_flag"], {}
    conversation = app.state.service.create_conversation(
        _MOCK_USER, str(case["course_id"])
    )
    last_run = None
    for turn in case["turns"]:
        if turn.get("role") != "user":
            continue
        content = str(turn.get("content") or "")
        request = WorkflowRunRequest.model_validate(
            _request_for_case(
                conversation.conversation_id,
                case,
                content,
                provider_id=provider_id,
                model_id=model_id,
            )
        )
        last_run = app.state.service.run(_MOCK_USER, request)
    if last_run is None:
        return "failed", ["用例没有 user 轮次"], {}
    reasons = _check_expected(last_run, case["expected"])
    metrics = _extract_runtime_metrics(last_run)
    return ("passed" if not reasons else "failed"), reasons, metrics


def _extract_runtime_metrics(result: Any) -> dict[str, object]:
    """Expose bounded, comparable runtime counters in evaluation reports.

    The model/provider trace is already a safe aggregate contract. Copy only
    those counters and citation counts here so an evaluation can compare the
    four decision groups without persisting prompts or source text.
    """

    model_event = next(
        (
            event
            for event in reversed(result.trace)
            if event.node in {"mock_model", "openrouter_model", "zhipu_model", "byok_model"}
        ),
        None,
    )
    if model_event is None:
        return {}
    payload = model_event.result.model_dump(exclude_none=True)
    keys = (
        "duration_ms",
        "decision_call_count",
        "answer_call_count",
        "provider_retry_count",
        "guard_retry_count",
        "decision_fallback_count",
        "action_rejection_count",
        "retry_count",
    )
    metrics = {key: payload[key] for key in keys if key in payload}
    metrics["duration_ms"] = model_event.duration_ms
    retrieval_event = next(
        (event for event in result.trace if event.node in {"fixture_retrieval", "local_corpus_retrieval"}),
        None,
    )
    if retrieval_event is not None:
        retrieval_payload = retrieval_event.result.model_dump(exclude_none=True)
        if "hit_count" in retrieval_payload:
            metrics["candidate_count"] = retrieval_payload["hit_count"]
    metrics.update(
        {
            "accepted_citation_count": len(result.citations),
            "answer_char_count": len(result.repository_answer),
        }
    )
    return metrics


def _report_line(
    case: dict[str, object],
    outcome: str,
    reasons: list[str],
    metrics: dict[str, object] | None = None,
) -> dict[str, object]:
    line = {
        "case_id": case["case_id"],
        "category": case["category"],
        "course_id": case.get("course_id"),
        "workflow_type": case["workflow_type"],
        "outcome": outcome,
        "reasons": reasons,
    }
    if metrics:
        line["runtime_metrics"] = metrics
    return line


def run_evaluation(
    cases_path: Path,
    runner_path: Path | None,
    report_path: Path,
    *,
    provider_id: str = "mock",
    model_id: str = "deterministic-fixture-v1",
    local_corpus: bool = False,
    pace_seconds: float = 0.0,
    case_retries: int = 0,
    agent_decision_mode: str = "rule",
) -> dict[str, object]:
    if agent_decision_mode not in {"rule", "model"}:
        raise ValueError("agent_decision_mode must be 'rule' or 'model'")
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

    real_model = provider_id != "mock"
    with tempfile.TemporaryDirectory(prefix="scut-senior-eval-") as tmp:
        settings = Settings(
            app_env="test",
            database_path=Path(tmp) / "eval.db",
            model_mode=(
                "openrouter_platform" if real_model else "mock"
            ),
            retrieval_mode=(
                "local_corpus" if (local_corpus or real_model) else "fixture"
            ),
            agent_decision_mode=agent_decision_mode,
            openrouter_api_key=os.getenv("SCUT_SENIOR_OPENROUTER_API_KEY"),
            zhipu_api_key=os.getenv("SCUT_SENIOR_ZHIPU_API_KEY"),
        )
        app = create_app(
            settings,
            # create_app installs FailClosedJsonHttpClient for platform HTTP
            # when app_env="test"; a real-model evaluation must override with
            # the genuine transport or every upstream call fails closed.
            **(
                {
                    "zhipu_http_client": UrllibJsonHttpClient(),
                    "model_http_client": UrllibJsonHttpClient(),
                }
                if real_model
                else {}
            ),
        )
        lines: list[dict[str, object]] = []
        for index, case in enumerate(cases["cases"]):
            if index and pace_seconds > 0:
                # free-tier platform channels throttle per-account bursts;
                # pacing keeps a real-model sweep under the RPM ceiling
                time.sleep(pace_seconds)
            metrics: dict[str, object] = {}
            try:
                outcome, reasons, metrics = _run_case(
                    app, case, provider_id=provider_id, model_id=model_id
                )
                attempt = 0
                # free-tier upstreams fail with transient throttling (429 /
                # zhipu 1305); retry only those failures, never real verdicts
                while (
                    case_retries > 0
                    and attempt < case_retries
                    and outcome == "failed"
                    and any("GatewayError" in str(r) for r in reasons)
                ):
                    attempt += 1
                    time.sleep(max(pace_seconds, 20.0))
                    outcome, reasons, metrics = _run_case(
                        app, case, provider_id=provider_id, model_id=model_id
                    )
            except Exception as exc:  # noqa: BLE001 - report any pipeline failure
                outcome, reasons = "failed", [f"{type(exc).__name__}: {exc}"]
            lines.append(_report_line(case, outcome, reasons, metrics))

    by_course: dict[str, Counter[str]] = {}
    for line in lines:
        key = str(line["course_id"] or "cross_course")
        by_course.setdefault(key, Counter())["total"] += 1
        by_course[key][str(line["outcome"])] += 1
    summary = Counter(line["outcome"] for line in lines)
    fixture_only = not real_model and not local_corpus
    report: dict[str, object] = {
        "runner_id": RUNNER_ID,
        "contract_version": CONTRACT_VERSION,
        "fixture_only": fixture_only,
        "provider_id": provider_id if not fixture_only else "mock",
        "model_id": model_id if not fixture_only else "deterministic-fixture-v1",
        "retrieval_mode": "local_corpus" if (local_corpus or real_model) else "fixture",
        "agent_decision_mode": agent_decision_mode,
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
        help="evaluation cases.json path (required unless --retrieval-only)",
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
    parser.add_argument(
        "--retrieval-only",
        action="store_true",
        help="run the PLAN-2 golden-set retrieval baseline instead of the "
        "pipeline case sweep; writes recall@5/recall@20/MRR/noise-rate per course",
    )
    parser.add_argument(
        "--golden",
        type=Path,
        default=DEFAULT_GOLDEN_ROOT,
        help="golden set directory for --retrieval-only "
        "(default resources/evaluation/retrieval-golden)",
    )
    parser.add_argument(
        "--corpus-store",
        type=Path,
        default=DEFAULT_CORPUS_STORE,
        help="active local corpus store for --retrieval-only "
        "(default .local/corpus-store)",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=1.0,
        help="retrieval min_score floor for --retrieval-only (default 1.0)",
    )
    parser.add_argument(
        "--hybrid",
        action="store_true",
        help="enable the local ONNX dense leg and rule rerank for retrieval-only",
    )
    parser.add_argument(
        "--onnx-model-dir",
        type=Path,
        help="local bge-small-zh-v1.5 directory for --hybrid (default .local/models/...)",
    )
    parser.add_argument(
        "--provider",
        default="mock",
        help="platform provider id for real-model runs (e.g. zhipu); "
        "default mock keeps the deterministic fixture model",
    )
    parser.add_argument(
        "--model",
        default="deterministic-fixture-v1",
        help="platform model id for real-model runs (e.g. glm-4.7-flash)",
    )
    parser.add_argument(
        "--fixture-corpus",
        action="store_true",
        help="force fixture retrieval even when a real model is selected; "
        "real-model runs default to the local active corpus store",
    )
    parser.add_argument(
        "--pace-seconds",
        type=float,
        default=0.0,
        help="sleep between cases (real-model sweeps on free-tier channels "
        "should use 10-20s to stay under per-account RPM limits)",
    )
    parser.add_argument(
        "--agent-decision-mode",
        choices=("rule", "model"),
        default="rule",
        help="bounded Action decision mode for AB comparisons; default rule",
    )
    return parser


def _run_retrieval_only(args: argparse.Namespace) -> int:
    try:
        embedding = None
        if args.hybrid:
            model_dir = args.onnx_model_dir or (
                APP_ROOT / ".local" / "models" / "bge-small-zh-v1.5"
            )
            embedding = OnnxEmbeddingProvider(model_dir)
        report = run_retrieval_evaluation(
            args.golden,
            args.report,
            store_root=args.corpus_store,
            min_score=args.min_score,
            embedding=embedding,
        )
    except ValueError as exc:
        print(f"retrieval evaluation failed: {exc}", file=sys.stderr)
        return 2
    summary = report["summary"]
    print(
        f"retrieval eval: {summary['entry_count']} entries, "
        f"recall@5={summary['recall_at_5']}, recall@20={summary['recall_at_20']}, "
        f"mrr={summary['mrr']}, noise_rate={summary['noise_rate']} -> {args.report}"
    )
    for course, course_report in report["by_course"].items():
        print(
            f"  [{course}] entries={course_report['entry_count']} "
            f"recall@5={course_report['recall_at_5']} "
            f"recall@20={course_report['recall_at_20']} "
            f"mrr={course_report['mrr']} noise_rate={course_report['noise_rate']}"
        )
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.retrieval_only:
        return _run_retrieval_only(args)
    if args.cases is None:
        print("--cases is required unless --retrieval-only is set", file=sys.stderr)
        return 2
    if args.provider != "mock" and not (
        os.getenv("SCUT_SENIOR_ZHIPU_API_KEY")
        or os.getenv("SCUT_SENIOR_OPENROUTER_API_KEY")
    ):
        print(
            "真实模型评测需要 SCUT_SENIOR_ZHIPU_API_KEY 或 "
            "SCUT_SENIOR_OPENROUTER_API_KEY 环境变量。",
            file=sys.stderr,
        )
        return 2
    report = run_evaluation(
        args.cases,
        args.runner,
        args.report,
        provider_id=args.provider,
        model_id=args.model,
        local_corpus=not args.fixture_corpus if args.provider != "mock" else False,
        pace_seconds=args.pace_seconds,
        case_retries=2 if args.provider != "mock" else 0,
        agent_decision_mode=args.agent_decision_mode,
    )
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
