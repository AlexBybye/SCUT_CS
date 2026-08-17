from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from scut_senior_api.contracts import (
    AnswerBlockType,
    AnswerMode,
    AnswerStatus,
    Citation,
    CourseScope,
    EvidenceStatus,
    ExternalResource,
    HelpLevel,
    KnowledgeScope,
    ModelSource,
    ModelCredentialStatus,
    RunStatus,
    Tone,
    TraceEvent,
    TraceEventStatus,
    WorkflowRunRequest,
    WorkflowType,
)


@pytest.mark.parametrize(
    "overrides",
    [
        {"configured": True, "masked_key": None},
        {"configured": True, "expires_at": None},
        {"configured": False, "masked_key": "••••••••"},
        {"configured": False, "expires_at": datetime(2026, 8, 23, tzinfo=UTC)},
        {"model_id": "deepseek-v4-flash"},
    ],
)
def test_model_credential_status_enforces_fixed_safe_metadata(
    overrides: dict[str, object],
) -> None:
    payload: dict[str, object] = {
        "provider_id": "openrouter",
        "model_id": "deepseek/deepseek-v4-flash-0731",
        "configured": True,
        "masked_key": "••••••••",
        "expires_at": datetime(2026, 8, 23, tzinfo=UTC),
    }
    payload.update(overrides)

    with pytest.raises(ValidationError):
        ModelCredentialStatus.model_validate(payload)


CONTRACT_ROOT = Path(__file__).resolve().parents[2] / "packages" / "contracts" / "v1"


def test_shared_enum_asset_matches_executable_pydantic_enums() -> None:
    payload = json.loads((CONTRACT_ROOT / "enums.json").read_text(encoding="utf-8"))
    enum_types = {
        "workflow_type": WorkflowType,
        "answer_mode": AnswerMode,
        "tone": Tone,
        "knowledge_scope": KnowledgeScope,
        "course_scope": CourseScope,
        "model_source": ModelSource,
        "run_status": RunStatus,
        "answer_status": AnswerStatus,
        "evidence_status": EvidenceStatus,
        "answer_block_type": AnswerBlockType,
        "trace_event_status": TraceEventStatus,
        "help_level": HelpLevel,
    }

    for contract_name, enum_type in enum_types.items():
        assert payload[contract_name] == [member.value for member in enum_type]


def base_request() -> dict[str, object]:
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
    ("workflow_type", "payload"),
    [
        ("knowledge_qa", {"question": "什么是秩？"}),
        (
            "exam_review",
            {
                "syllabus": None,
                "exam_date": None,
                "available_hours": 8,
                "goals": ["复习矩阵"],
                "weak_topics": [],
            },
        ),
        (
            "problem_tutor",
            {
                "problem": "求矩阵的秩",
                "user_answer": None,
                "help_level": "step_by_step",
                "problem_source": None,
            },
        ),
        (
            "mistake_review",
            {
                "problem": "求矩阵的秩",
                "original_answer": "秩为 1",
                "reference_answer": None,
                "review_focus": "方法",
            },
        ),
        (
            "temporary_material_reading",
            {
                "material_title": "矩阵课程说明",
                "material_text": "矩阵课程临时说明",
                "reading_goal": "解释",
            },
        ),
    ],
)
def test_all_workflow_payloads_are_explicitly_typed(
    workflow_type: str, payload: dict[str, object]
) -> None:
    request = base_request()
    request["workflow_type"] = workflow_type
    request["workflow_payload"] = payload

    parsed = WorkflowRunRequest.model_validate(request)

    assert parsed.workflow_type.value == workflow_type


@pytest.mark.parametrize(
    ("workflow_type", "payload"),
    [
        (
            "exam_review",
            {"syllabus": "X" * 20_001, "goals": [], "weak_topics": []},
        ),
        (
            "exam_review",
            {"goals": ["X" * 4_001], "weak_topics": []},
        ),
        (
            "exam_review",
            {"goals": ["目标"] * 33, "weak_topics": []},
        ),
        (
            "exam_review",
            {"goals": [], "weak_topics": ["X" * 501]},
        ),
        (
            "problem_tutor",
            {
                "problem": "题目",
                "user_answer": "X" * 40_001,
                "help_level": "step_by_step",
            },
        ),
        (
            "problem_tutor",
            {
                "problem": "题目",
                "help_level": "step_by_step",
                "problem_source": "X" * 2_001,
            },
        ),
        (
            "mistake_review",
            {
                "problem": "题目",
                "original_answer": "错答",
                "reference_answer": "X" * 40_001,
            },
        ),
        (
            "mistake_review",
            {
                "problem": "题目",
                "original_answer": "错答",
                "review_focus": "X" * 4_001,
            },
        ),
        (
            "temporary_material_reading",
            {"material_text": "材料", "reading_goal": "X" * 4_001},
        ),
    ],
)
def test_all_provider_prompt_fields_and_lists_are_bounded(
    workflow_type: str,
    payload: dict[str, object],
) -> None:
    request = base_request()
    request["workflow_type"] = workflow_type
    request["workflow_payload"] = payload

    with pytest.raises(ValidationError):
        WorkflowRunRequest.model_validate(request)


def test_payload_cannot_silently_switch_workflow() -> None:
    request = base_request()
    request["workflow_type"] = "exam_review"

    with pytest.raises(ValidationError, match="workflow_payload"):
        WorkflowRunRequest.model_validate(request)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("workflow_type", "unknown_workflow"),
        ("answer_mode", "compare"),
        ("tone", "formal"),
        ("knowledge_scope", "everything"),
        ("model_source", "arbitrary_url"),
    ],
)
def test_unknown_enums_are_rejected(field: str, value: str) -> None:
    request = base_request()
    request[field] = value

    with pytest.raises(ValidationError):
        WorkflowRunRequest.model_validate(request)


def test_course_only_forces_external_resources_off() -> None:
    request = base_request()
    request["knowledge_scope"] = "course_only"
    request["include_bilibili_resources"] = True

    parsed = WorkflowRunRequest.model_validate(request)

    assert parsed.knowledge_scope == KnowledgeScope.COURSE_ONLY
    assert parsed.include_bilibili_resources is False


def test_bilibili_search_resource_requires_a_fixed_anonymous_search_link() -> None:
    resource = ExternalResource.model_validate(
        {
            "resource_id": None,
            "course_id": "linear_algebra",
            "platform": "bilibili",
            "resource_type": "search",
            "title": "在哔哩哔哩搜索：矩阵的秩",
            "url": "https://search.bilibili.com/all?keyword=%E7%9F%A9%E9%98%B5%E7%9A%84%E7%A7%A9",
            "matched_topic": "矩阵的秩",
            "review_status": "unreviewed_live_search",
            "catalog_version": None,
            "query_keywords": ["矩阵的秩"],
            "generated_at": "2026-08-15T12:00:00Z",
            "evidence_role": "supplementary_only",
        }
    )

    assert resource.resource_id is None
    assert resource.review_status == "unreviewed_live_search"
    assert resource.query_keywords == ["矩阵的秩"]


def test_bilibili_workflow_resource_rejects_video_direct_links() -> None:
    with pytest.raises(ValidationError):
        ExternalResource.model_validate(
            {
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
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("resource_id", "model-invented-id"),
        ("review_status", "reviewed"),
        ("catalog_version", "catalog-v1"),
        ("query_keywords", []),
        ("query_keywords", ["别的关键词"]),
        ("url", "https://evil.example/all?keyword=rank"),
        ("url", "https://search.bilibili.com/all?order=click"),
    ],
)
def test_bilibili_search_resource_rejects_model_urls_or_reviewed_metadata(
    field: str, value: object
) -> None:
    payload: dict[str, object] = {
        "resource_id": None,
        "course_id": "linear_algebra",
        "platform": "bilibili",
        "resource_type": "search",
        "title": "在哔哩哔哩搜索：线性代数 矩阵的秩",
        "url": "https://search.bilibili.com/all?keyword=rank",
        "matched_topic": "矩阵的秩",
        "review_status": "unreviewed_live_search",
        "catalog_version": None,
        "query_keywords": ["矩阵的秩"],
        "generated_at": "2026-08-15T12:00:00Z",
        "evidence_role": "supplementary_only",
    }
    payload[field] = value

    with pytest.raises(ValidationError):
        ExternalResource.model_validate(payload)


def test_cross_scope_requires_explicit_course_set() -> None:
    request = base_request()
    request.update(
        {
            "course_scope": "cross",
            "course_id": None,
            "allowed_course_ids": ["linear_algebra"],
        }
    )

    with pytest.raises(ValidationError, match="at least two"):
        WorkflowRunRequest.model_validate(request)


def test_cross_scope_rejects_duplicate_course_ids() -> None:
    request = base_request()
    request.update(
        {
            "course_scope": "cross",
            "course_id": None,
            "allowed_course_ids": [
                "linear_algebra",
                "probability_theory",
                "probability_theory",
            ],
        }
    )

    with pytest.raises(ValidationError, match="duplicate courses"):
        WorkflowRunRequest.model_validate(request)


def test_iteration_zero_rejects_attachments() -> None:
    request = base_request()
    request["attachments"] = [{"name": "question.png"}]

    with pytest.raises(ValidationError, match="attachments are disabled"):
        WorkflowRunRequest.model_validate(request)


@pytest.mark.parametrize("unsafe_field", ["token", "prompt", "stack", "internal_path"])
def test_student_trace_rejects_non_whitelisted_fields(unsafe_field: str) -> None:
    event = {
        "event_id": "trace-1",
        "sequence": 0,
        "node": "mock_model",
        "status": "completed",
        "duration_ms": 0,
        "result": {unsafe_field: "must-not-leak"},
    }

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        TraceEvent.model_validate(event)


def test_citation_allows_explicit_missing_locator_without_inventing_one() -> None:
    citation = Citation.model_validate(
        {
            "citation_id": "S1",
            "chunk_id": "source:none:c01",
            "course_id": "linear_algebra",
            "course_title": "线性代数",
            "source_id": "source",
            "source_title": "无稳定定位的合成资料",
            "locator_type": "none",
            "locator_start": None,
            "locator_end": None,
            "question_id": None,
            "heading_path": [],
        }
    )

    assert citation.locator_type == "none"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("locator_start", "普通章节"),
        ("question_id", "Q1"),
        ("heading_path", ["普通章节"]),
    ],
)
def test_missing_locator_rejects_fabricated_precision(
    field: str, value: object
) -> None:
    payload: dict[str, object] = {
        "citation_id": "S1",
        "chunk_id": "source:none:c01",
        "course_id": "linear_algebra",
        "course_title": "线性代数",
        "source_id": "source",
        "source_title": "无稳定定位的合成资料",
        "locator_type": "none",
        "locator_start": None,
        "locator_end": None,
        "question_id": None,
        "heading_path": [],
    }
    payload[field] = value

    with pytest.raises(ValidationError, match="forbids precise locator"):
        Citation.model_validate(payload)
