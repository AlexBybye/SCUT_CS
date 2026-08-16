import json
from copy import deepcopy
from uuid import uuid4

import pytest
from jsonschema import Draft202012Validator

from scut_senior_api.export_contracts import check_schema_files, render_schema_files


def test_committed_workflow_schemas_match_executable_pydantic_contracts() -> None:
    assert check_schema_files() == []


def test_workflow_result_schema_requires_the_complete_plan_v1_surface() -> None:
    schema = json.loads(render_schema_files()["workflow-result.schema.json"])

    assert set(schema["required"]) == {
        "workflow_run_id",
        "conversation_id",
        "message_id",
        "answer_id",
        "run_status",
        "answer_status",
        "workflow_type",
        "course_scope",
        "course_ids",
        "repository_answer",
        "general_supplement",
        "answer_blocks",
        "workflow_output",
        "evidence_status",
        "citations",
        "related_topics",
        "related_questions",
        "external_resources",
        "coverage_gaps",
        "trace",
        "corpus_version",
        "course_pack_version",
        "workflow_version",
        "model_source",
        "model",
        "availability_status",
    }


def valid_request() -> dict[str, object]:
    return {
        "workflow_type": "knowledge_qa",
        "course_scope": "single",
        "course_id": "linear_algebra",
        "allowed_course_ids": [],
        "conversation_id": str(uuid4()),
        "model_source": "platform_default",
        "provider_id": "mock",
        "model_id": "deterministic-fixture-v1",
        "user_input": "矩阵的秩是什么？",
        "answer_mode": "concise",
        "tone": "teaching_assistant",
        "knowledge_scope": "course_first",
        "include_bilibili_resources": True,
        "context_refs": [],
        "attachments": [],
        "workflow_payload": {"question": "矩阵的秩是什么？"},
    }


@pytest.mark.parametrize(
    "mutations",
    [
        {"workflow_type": "exam_review"},
        {"allowed_course_ids": ["linear_algebra"]},
        {"attachments": [{"name": "disabled.png"}]},
        {
            "course_scope": "cross",
            "course_id": "linear_algebra",
            "allowed_course_ids": ["linear_algebra", "probability_theory"],
        },
        {
            "course_scope": "cross",
            "course_id": None,
            "allowed_course_ids": ["linear_algebra", "linear_algebra"],
        },
    ],
)
def test_exported_request_schema_rejects_pydantic_cross_field_violations(
    mutations: dict[str, object]
) -> None:
    schema = json.loads(render_schema_files()["workflow-request.schema.json"])
    payload = deepcopy(valid_request())
    payload.update(mutations)

    assert list(Draft202012Validator(schema).iter_errors(payload))


def test_exported_request_schema_accepts_the_valid_mock_request() -> None:
    schema = json.loads(render_schema_files()["workflow-request.schema.json"])

    Draft202012Validator(schema).validate(valid_request())


def test_exported_citation_schema_rejects_precision_when_locator_is_none() -> None:
    schema = json.loads(render_schema_files()["workflow-result.schema.json"])
    citation_schema = schema["$defs"]["Citation"]
    payload = {
        "citation_id": "S1",
        "chunk_id": "source:none:c01",
        "course_id": "linear_algebra",
        "course_title": "线性代数",
        "source_id": "source",
        "source_title": "无稳定定位的合成资料",
        "locator_type": "none",
        "locator_start": "伪造章节",
        "locator_end": None,
        "question_id": None,
        "heading_path": [],
    }

    assert list(Draft202012Validator(citation_schema).iter_errors(payload))
