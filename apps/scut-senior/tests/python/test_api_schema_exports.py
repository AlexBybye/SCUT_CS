import json
from copy import deepcopy
from uuid import uuid4

import pytest
from jsonschema import Draft202012Validator

from scut_senior_api.export_contracts import check_schema_files, render_schema_files


def test_committed_workflow_schemas_match_executable_pydantic_contracts() -> None:
    assert check_schema_files() == []


def test_model_catalog_schema_freezes_health_and_credential_fields() -> None:
    schema = json.loads(render_schema_files()["model-catalog.schema.json"])

    assert {
        "catalog_version",
        "platform_credential_configured",
        "real_platform_default_available",
        "health_checked_at",
        "byok_available",
        "byok_catalog_version",
        "byok_providers",
        "quota_notice",
        "quota_exhausted_message",
        "models",
    } == set(schema["required"])
    model_entry = schema["$defs"]["PublicModelCatalogEntry"]
    assert "last_checked_at" in model_entry["required"]
    assert "health_check_required" in str(
        model_entry["properties"]["availability_status"]
    )


def test_model_credential_schemas_never_expose_ciphertext_or_plaintext_status() -> None:
    rendered = render_schema_files()
    status = json.loads(rendered["model-credential-list.schema.json"])
    upsert = json.loads(rendered["model-credential-upsert.schema.json"])

    status_entry = status["$defs"]["ModelCredentialStatus"]
    assert set(status_entry["required"]) == {
        "provider_id",
        "model_id",
        "configured",
        "masked_key",
        "expires_at",
        "writable",
        "source",
        "updated_at",
    }
    serialized = json.dumps(status, ensure_ascii=False)
    assert "ciphertext" not in serialized
    assert "nonce" not in serialized
    assert upsert["properties"]["api_key"]["format"] == "password"
    assert upsert["properties"]["api_key"]["writeOnly"] is True
    assert set(upsert["properties"]) == {"api_key"}


def test_conversation_schema_exposes_linked_attempts_instead_of_bare_results() -> None:
    schema = json.loads(render_schema_files()["conversation-detail.schema.json"])

    assert schema["properties"]["runs"]["items"] == {
        "$ref": "#/$defs/WorkflowAttempt"
    }
    assert {
        "workflow_run_id",
        "attempt_group_id",
        "regenerated_from_run_id",
        "request",
        "result",
        "created_at",
        "updated_at",
        "expires_at",
    } == set(schema["$defs"]["WorkflowAttempt"]["required"])


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


def test_exported_bilibili_search_schema_rejects_non_bilibili_url() -> None:
    schema = json.loads(render_schema_files()["workflow-result.schema.json"])
    resource_schema = schema["$defs"]["ExternalResource"]
    payload = {
        "resource_id": None,
        "course_id": "linear_algebra",
        "platform": "bilibili",
        "resource_type": "search",
        "title": "在哔哩哔哩搜索：矩阵的秩",
        "url": "https://evil.example/all?keyword=rank",
        "matched_topic": "矩阵的秩",
        "review_status": "unreviewed_live_search",
        "catalog_version": None,
        "query_keywords": ["矩阵的秩"],
        "generated_at": "2026-08-15T12:00:00Z",
        "evidence_role": "supplementary_only",
    }

    assert list(Draft202012Validator(resource_schema).iter_errors(payload))


def test_exported_workflow_resource_schema_rejects_video_direct_link() -> None:
    schema = json.loads(render_schema_files()["workflow-result.schema.json"])
    resource_schema = schema["$defs"]["ExternalResource"]
    payload = {
        "resource_id": "reviewed-1",
        "course_id": "linear_algebra",
        "platform": "bilibili",
        "resource_type": "video",
        "title": "具体视频",
        "url": "https://www.bilibili.com/video/BV1FIXTURE01",
        "matched_topic": "矩阵的秩",
        "review_status": "reviewed",
        "catalog_version": "fixture-v1",
        "query_keywords": ["矩阵的秩"],
        "generated_at": None,
        "evidence_role": "supplementary_only",
    }

    assert list(Draft202012Validator(resource_schema).iter_errors(payload))
