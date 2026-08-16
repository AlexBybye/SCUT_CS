from __future__ import annotations

from copy import deepcopy
import csv
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from scut_senior_worker.corpus_validator import LOCATOR_TYPES, MANIFEST_STATUSES


APP_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = APP_ROOT / "packages" / "contracts" / "v1"
FIXTURE_ROOT = APP_ROOT / "tests" / "fixtures"

EXPECTED_COURSE_IDS = [
    "engineering_math_analysis_1",
    "engineering_math_analysis_2",
    "linear_algebra",
    "probability_theory",
    "cpp",
    "discrete_mathematics",
    "english",
    "computer_science_intro",
    "information_security_intro",
    "university_physics_3_1",
]
EXPECTED_EVALUATION_CATEGORIES = {
    "course_knowledge",
    "past_paper_question",
    "sparse_general_supplement",
    "insufficient_evidence",
    "multi_turn_followup",
    "cross_course_scope",
    "source_marking",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_courses_registry_has_frozen_order_shape_and_closed_switches() -> None:
    payload = _load_json(CONTRACT_ROOT / "courses.json")

    assert set(payload) == {"contract_version", "courses"}
    assert payload["contract_version"] == "v1"
    assert [course["course_id"] for course in payload["courses"]] == EXPECTED_COURSE_IDS
    assert all(course["is_open"] is False for course in payload["courses"])
    assert [
        course["course_id"]
        for course in payload["courses"]
        if course["fixture_available"]
    ] == ["linear_algebra"]
    assert next(
        course for course in payload["courses"] if course["course_id"] == "information_security_intro"
    )["display_name"] == "信息安全导论"
    assert all(course["repository_paths"] for course in payload["courses"])


def test_shared_enums_are_exact() -> None:
    payload = _load_json(CONTRACT_ROOT / "enums.json")

    assert payload["contract_version"] == "v1"
    assert payload["workflow_type"] == [
        "knowledge_qa",
        "exam_review",
        "problem_tutor",
        "mistake_review",
        "temporary_material_reading",
    ]
    assert payload["answer_mode"] == ["concise", "detailed", "example", "step_by_step"]
    assert payload["tone"] == ["teaching_assistant", "study_partner", "senior_student"]
    assert payload["knowledge_scope"] == ["course_only", "course_first"]
    assert payload["course_scope"] == ["single", "cross"]
    assert payload["model_source"] == ["platform_default", "user_key"]
    assert payload["run_status"] == [
        "created",
        "running",
        "completed",
        "interrupted",
        "failed",
    ]
    assert payload["answer_status"] == [
        "answered",
        "partial",
        "insufficient_evidence",
        "needs_clarification",
        "refused",
        "error",
    ]
    assert payload["evidence_status"] == [
        "sufficient",
        "partial",
        "insufficient",
        "not_evaluated",
    ]
    assert payload["answer_block_type"] == [
        "repository",
        "user_material",
        "general",
        "personalized_analysis",
    ]
    assert payload["trace_event_status"] == [
        "started",
        "completed",
        "failed",
        "skipped",
    ]
    assert payload["help_level"] == [
        "concept",
        "approach",
        "step_by_step",
        "full_explanation",
        "answer_analysis",
    ]
    assert set(payload["manifest_status"]) == MANIFEST_STATUSES
    assert set(payload["locator_type"]) == LOCATOR_TYPES - {""}
    assert payload["bilibili_review_status"] == ["unreviewed_live_search"]


def test_evaluation_schemas_validate_exactly_seven_fixture_categories() -> None:
    case_schema = _load_json(CONTRACT_ROOT / "schemas" / "evaluation-case.schema.json")
    runner_schema = _load_json(
        CONTRACT_ROOT / "schemas" / "evaluation-runner.schema.json"
    )
    Draft202012Validator.check_schema(case_schema)
    Draft202012Validator.check_schema(runner_schema)

    case_payload = _load_json(FIXTURE_ROOT / "evaluation" / "cases.json")
    runner_payload = _load_json(FIXTURE_ROOT / "evaluation" / "runner.json")
    validator = Draft202012Validator(case_schema)
    for case in case_payload["cases"]:
        validator.validate(case)
    Draft202012Validator(runner_schema).validate(runner_payload)

    assert case_payload["fixture_only"] is True
    assert len(case_payload["cases"]) == 7
    assert {case["category"] for case in case_payload["cases"]} == EXPECTED_EVALUATION_CATEGORIES
    assert runner_payload["case_ids"] == [
        case["case_id"] for case in case_payload["cases"]
    ]
    referenced_course_ids: set[str] = set()
    for case in case_payload["cases"]:
        if case["course_scope"] == "single":
            assert isinstance(case["course_id"], str)
            assert case["allowed_course_ids"] == []
            referenced_course_ids.add(case["course_id"])
        else:
            assert case["course_id"] is None
            assert len(case["allowed_course_ids"]) >= 2
            referenced_course_ids.update(case["allowed_course_ids"])
    assert referenced_course_ids.issubset(EXPECTED_COURSE_IDS)

    invalid_single = deepcopy(case_payload["cases"][0])
    invalid_single["allowed_course_ids"] = [invalid_single["course_id"]]
    assert list(validator.iter_errors(invalid_single))

    invalid_cross = deepcopy(
        next(case for case in case_payload["cases"] if case["course_scope"] == "cross")
    )
    invalid_cross["course_id"] = "linear_algebra"
    assert list(validator.iter_errors(invalid_cross))


def test_corpus_fixture_is_synthetic_and_has_only_passed_and_pending() -> None:
    manifest_path = FIXTURE_ROOT / "corpus" / "manifest.csv"
    with manifest_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert {row["course"] for row in rows} == {"linear_algebra", "线性代数"}
    assert {row["status"] for row in rows} == {"passed", "pending"}
    assert all(row["notes"] == "fixture_only" for row in rows)
    assert all(not row["original_path"].startswith("学科资料/") for row in rows)
    assert all(row["output_md"].startswith("linear_algebra/") for row in rows)


def test_contract_readme_uses_plan_request_result_and_payload_names() -> None:
    text = (CONTRACT_ROOT / "README.md").read_text(encoding="utf-8")

    for required_name in (
        "provider_id",
        "model_id",
        "include_bilibili_resources",
        "context_refs",
        "attachments[]",
        "workflow_run_id",
        "workflow_output",
        "trace[]",
        "available_hours",
        "help_level",
        "original_answer",
        "material_text",
    ):
        assert required_name in text
    assert "request_id" not in text
    assert "trace_events[]" not in text
    assert "`type` 表示 `answer_block_type`" in text
    assert "`course_id=null`" in text
    assert "`document_role` 与 `year` 不确定时允许留空" in text
