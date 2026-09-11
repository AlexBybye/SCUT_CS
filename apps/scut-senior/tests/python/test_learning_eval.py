from __future__ import annotations

import itertools
import json
import sqlite3
from fractions import Fraction
from types import SimpleNamespace
from uuid import uuid4

import pytest

from scut_senior_api.contracts import WorkflowRunRequest
from scut_senior_api.eval_runner import _check_expected, _report_line, _request_for_case, _run_case, main
from scut_senior_api.learning_eval import DEFAULT_SUITE, score_ranking


def test_alternative_chunks_do_not_require_redundant_retrieval():
    score = score_ranking([{"chunk_ids": ["answer-a", "answer-b"]}], ["answer-b"])
    assert score["known_evidence_coverage_at_5"] == 1
    assert score["all_evidence_groups_at_5"] == 1


def test_one_topic_cannot_satisfy_an_unrelated_evidence_need():
    score = score_ranking([{"chunk_ids": ["question"]}, {"chunk_ids": ["answer"]}], ["question", "question"])
    assert score["known_evidence_coverage_at_5"] == 0.5
    assert score["all_evidence_groups_at_5"] == 0


def test_unjudged_is_not_noise_or_answer_failure():
    score = score_ranking([{"chunk_ids": ["known"]}], ["new-relevant-candidate", "known"])
    assert score["known_positive_mrr"] == 0.5
    assert score["unjudged_chunk_ids"] == ["new-relevant-candidate"]
    assert "noise_rate" not in score and "answer_accuracy" not in score


def test_reviewed_scenarios_preserve_real_workflow_inputs():
    cases = json.loads((DEFAULT_SUITE.parent / "scenarios.json").read_text(encoding="utf-8"))["cases"]
    assert {case["workflow_type"] for case in cases} == {
        "knowledge_qa", "problem_tutor", "mistake_review", "exam_review", "temporary_material_reading",
    }
    for case in cases:
        for turn in case["turns"]:
            request = WorkflowRunRequest.model_validate(_request_for_case(str(uuid4()), case, turn["content"]))
            if "workflow_payload" in case:
                for key, value in case["workflow_payload"].items():
                    assert request.workflow_payload.model_dump(mode="json")[key] == value
        if case["workflow_type"] == "mistake_review":
            assert "用例未提供" not in case["workflow_payload"]["original_answer"]


def test_unspecified_citation_requirement_does_not_prohibit_citations():
    result = SimpleNamespace(
        answer_status=SimpleNamespace(value="answered"), evidence_status=SimpleNamespace(value="sufficient"),
        answer_blocks=[], citations=[SimpleNamespace(locator_type="page")], workflow_output={},
    )
    assert _check_expected(result, {}) == []
    assert _check_expected(result, {"requires_citation": False})


def test_contract_success_is_not_semantic_success():
    case = {"case_id": "x", "category": "concept", "course_id": "x", "workflow_type": "knowledge_qa", "quality_rubric": {"reference_answer": "correct"}}
    row = _report_line(case, "passed", [], {"answer_call_count": 1, "review_material": {"repository_answer": "wrong"}})
    assert row["outcome"] == "passed"
    assert row["quality_outcome"] == "not_reviewed"
    assert row["review_material"]["repository_answer"] == "wrong"
    assert "review_material" not in row["runtime_metrics"]


def test_knapsack_reference_by_exhaustive_enumeration():
    weights, values = [3, 5, 7, 8, 9], [4, 6, 7, 9, 10]
    feasible = []
    for bits in itertools.product((0, 1), repeat=5):
        if sum(b * w for b, w in zip(bits, weights)) <= 22:
            feasible.append((sum(b * v for b, v in zip(bits, values)), bits))
    optimum = max(v for v, _ in feasible)
    suite = json.loads(DEFAULT_SUITE.read_text(encoding="utf-8"))
    expected = next(e for e in suite["entries"] if e["topic_id"] == "algo-knapsack")["verified_values"]
    assert optimum == expected["maximum_value"]
    assert [[i + 1 for i, bit in enumerate(bits) if bit] for value, bits in feasible if value == optimum] == [expected["selected_items"]]


def test_unbiased_estimator_reference_by_exact_arithmetic():
    weights = [
        [Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)],
        [Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)],
        [Fraction(1, 3)] * 3,
        [Fraction(1, 5), Fraction(2, 5), Fraction(2, 5)],
    ]
    assert all(sum(row) == 1 for row in weights)
    variances = [sum(w * w for w in row) for row in weights]
    assert variances == [Fraction(7, 18), Fraction(3, 8), Fraction(1, 3), Fraction(9, 25)]
    assert variances.index(min(variances)) == 2


def test_sql_references_against_executable_examples():
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE student (id INTEGER, age INTEGER)")
        db.executemany("INSERT INTO student VALUES (?, ?)", [(1, None), (2, 20)])
        assert db.execute("SELECT id FROM student WHERE age = NULL").fetchall() == []
        assert db.execute("SELECT id FROM student WHERE age IS NULL").fetchall() == [(1,)]
        db.execute("CREATE TABLE marks (id INTEGER, score INTEGER)")
        db.executemany("INSERT INTO marks VALUES (?, ?)", [(1, 80), (1, 90), (2, 70), (2, 80)])
        assert db.execute("SELECT id, AVG(score) FROM marks GROUP BY id HAVING AVG(score)>=85").fetchall() == [(1, 85.0)]


def test_sources_and_paraphrases_stay_in_one_split():
    suite = json.loads(DEFAULT_SUITE.read_text(encoding="utf-8"))
    splits = {}
    for entry in suite["entries"]:
        for group in entry["evidence_groups"]:
            for cid in group["chunk_ids"]:
                source = suite["evidence"][cid]["source_id"]
                assert splits.setdefault(source, entry["split"]) == entry["split"]
    assert {e["split"] for e in suite["entries"]} == {"dev", "validation"}


def test_empty_evidence_has_no_artificial_perfect_score():
    with pytest.raises(ValueError):
        score_ranking([], [])


def test_disabled_cross_course_is_explicitly_skipped():
    app = SimpleNamespace(state=SimpleNamespace(service=SimpleNamespace(settings=SimpleNamespace(cross_course_enabled=False))))
    outcome, reasons, metrics = _run_case(app, {"course_scope": "cross"})
    assert outcome == "skipped" and reasons == ["cross_course_disabled_by_feature_flag"]
    assert metrics == {}


def test_default_cli_uses_reviewed_suite_not_legacy_targets(tmp_path, monkeypatch):
    import scut_senior_api.learning_eval as learning
    calls = []

    def run(suite, store, **kwargs):
        calls.append(suite)
        return {"summary": {"queries": 50}}

    monkeypatch.setattr(learning, "run_suite", run)
    report = tmp_path / "report.json"
    assert main(["--retrieval-only", "--report", str(report)]) == 0
    assert calls == [DEFAULT_SUITE]


def test_conflicting_corpus_flags_are_rejected_before_execution(tmp_path):
    assert main(["--report", str(tmp_path / "report.json"), "--local-corpus", "--fixture-corpus"]) == 2
