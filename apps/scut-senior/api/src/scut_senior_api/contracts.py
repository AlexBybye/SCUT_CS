from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Annotated, Any, Literal
from urllib.parse import parse_qs, urlsplit
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    RootModel,
    SecretStr,
    field_validator,
    model_serializer,
    model_validator,
)


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class WorkflowType(StrEnum):
    KNOWLEDGE_QA = "knowledge_qa"
    EXAM_REVIEW = "exam_review"
    PROBLEM_TUTOR = "problem_tutor"
    MISTAKE_REVIEW = "mistake_review"
    TEMPORARY_MATERIAL_READING = "temporary_material_reading"


class AnswerMode(StrEnum):
    CONCISE = "concise"
    DETAILED = "detailed"
    EXAMPLE = "example"
    STEP_BY_STEP = "step_by_step"


class Tone(StrEnum):
    TEACHING_ASSISTANT = "teaching_assistant"
    STUDY_PARTNER = "study_partner"
    SENIOR_STUDENT = "senior_student"


class KnowledgeScope(StrEnum):
    COURSE_ONLY = "course_only"
    COURSE_FIRST = "course_first"


class CourseScope(StrEnum):
    SINGLE = "single"
    CROSS = "cross"


class ModelSource(StrEnum):
    PLATFORM_DEFAULT = "platform_default"
    USER_KEY = "user_key"


class RunStatus(StrEnum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    FAILED = "failed"


class AnswerStatus(StrEnum):
    ANSWERED = "answered"
    PARTIAL = "partial"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    NEEDS_CLARIFICATION = "needs_clarification"
    REFUSED = "refused"
    ERROR = "error"


class EvidenceStatus(StrEnum):
    SUFFICIENT = "sufficient"
    PARTIAL = "partial"
    INSUFFICIENT = "insufficient"
    NOT_EVALUATED = "not_evaluated"


class AnswerBlockType(StrEnum):
    REPOSITORY = "repository"
    USER_MATERIAL = "user_material"
    GENERAL = "general"
    PERSONALIZED_ANALYSIS = "personalized_analysis"


class TraceEventStatus(StrEnum):
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class HelpLevel(StrEnum):
    CONCEPT = "concept"
    APPROACH = "approach"
    STEP_BY_STEP = "step_by_step"
    FULL_EXPLANATION = "full_explanation"
    ANSWER_ANALYSIS = "answer_analysis"


class KnowledgeQaPayload(ContractModel):
    question: Annotated[str, Field(min_length=1, max_length=20_000)]


class ExamReviewPayload(ContractModel):
    syllabus: Annotated[str | None, Field(max_length=20_000)] = None
    exam_date: date | None = None
    available_hours: Annotated[float | None, Field(gt=0, le=10_000)] = None
    goals: Annotated[
        list[Annotated[str, Field(max_length=4_000)]],
        Field(max_length=32),
    ]
    weak_topics: Annotated[
        list[Annotated[str, Field(max_length=500)]],
        Field(max_length=64),
    ]


class ProblemTutorPayload(ContractModel):
    problem: Annotated[str, Field(min_length=1, max_length=40_000)]
    user_answer: Annotated[str | None, Field(max_length=40_000)] = None
    help_level: HelpLevel
    problem_source: Annotated[str | None, Field(max_length=2_000)] = None


class MistakeReviewPayload(ContractModel):
    problem: Annotated[str, Field(min_length=1, max_length=40_000)]
    original_answer: Annotated[str, Field(min_length=1, max_length=40_000)]
    reference_answer: Annotated[str | None, Field(max_length=40_000)] = None
    review_focus: Annotated[str | None, Field(max_length=4_000)] = None


class TemporaryMaterialReadingPayload(ContractModel):
    material_title: Annotated[str | None, Field(max_length=200)] = None
    material_text: Annotated[str, Field(min_length=1, max_length=100_000)]
    reading_goal: Annotated[str | None, Field(max_length=4_000)] = None


WorkflowPayload = (
    KnowledgeQaPayload
    | ExamReviewPayload
    | ProblemTutorPayload
    | MistakeReviewPayload
    | TemporaryMaterialReadingPayload
)


class WorkflowRunRequest(ContractModel):
    workflow_type: WorkflowType
    course_scope: CourseScope
    course_id: str | None = None
    allowed_course_ids: list[str]
    conversation_id: UUID
    model_source: ModelSource
    provider_id: Annotated[str, Field(min_length=1, max_length=100)]
    model_id: Annotated[str, Field(min_length=1, max_length=100)]
    user_input: Annotated[str, Field(min_length=1, max_length=100_000)]
    answer_mode: AnswerMode
    tone: Tone
    knowledge_scope: KnowledgeScope
    include_bilibili_resources: bool
    context_refs: list[str]
    attachments: list[dict[str, Any]]
    workflow_payload: WorkflowPayload

    @model_validator(mode="after")
    def enforce_v1_invariants(self) -> "WorkflowRunRequest":
        payload_by_workflow: dict[WorkflowType, type[ContractModel]] = {
            WorkflowType.KNOWLEDGE_QA: KnowledgeQaPayload,
            WorkflowType.EXAM_REVIEW: ExamReviewPayload,
            WorkflowType.PROBLEM_TUTOR: ProblemTutorPayload,
            WorkflowType.MISTAKE_REVIEW: MistakeReviewPayload,
            WorkflowType.TEMPORARY_MATERIAL_READING: TemporaryMaterialReadingPayload,
        }
        expected = payload_by_workflow[self.workflow_type]
        if not isinstance(self.workflow_payload, expected):
            raise ValueError(
                f"workflow_payload must match workflow_type={self.workflow_type.value}"
            )
        if self.course_scope == CourseScope.SINGLE:
            if not self.course_id:
                raise ValueError("single course scope requires course_id")
            if self.allowed_course_ids:
                raise ValueError("single course scope forbids allowed_course_ids")
        else:
            if self.course_id is not None:
                raise ValueError("cross course scope requires course_id to be null")
            if len(set(self.allowed_course_ids)) != len(self.allowed_course_ids):
                raise ValueError("cross course scope forbids duplicate courses")
            if len(set(self.allowed_course_ids)) < 2:
                raise ValueError("cross course scope requires at least two explicit courses")
        if self.attachments:
            raise ValueError("attachments are disabled in iteration 0")
        if self.knowledge_scope == KnowledgeScope.COURSE_ONLY:
            self.include_bilibili_resources = False
        return self


class ConversationCreate(ContractModel):
    course_id: Annotated[str, Field(min_length=1, max_length=100)]


class ConversationRename(ContractModel):
    title: Annotated[str, Field(min_length=1, max_length=100)]

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("conversation title must not be blank")
        return normalized


class ModelCredentialUpsert(ContractModel):
    api_key: Annotated[SecretStr, Field(min_length=1, max_length=8192)]


class ModelCredentialStatus(ContractModel):
    provider_id: Literal["openrouter", "deepseek", "siliconflow", "zhipu"]
    model_id: Literal[
        "deepseek/deepseek-v4-flash-0731",
        "deepseek-v4-flash",
        "Pro/zai-org/GLM-4.7",
        "glm-5.2",
    ]
    configured: bool
    masked_key: Literal["••••••••"] | None
    expires_at: datetime | None

    @model_validator(mode="after")
    def enforce_configuration_metadata(self) -> "ModelCredentialStatus":
        expected_model = {
            "openrouter": "deepseek/deepseek-v4-flash-0731",
            "deepseek": "deepseek-v4-flash",
            "siliconflow": "Pro/zai-org/GLM-4.7",
            "zhipu": "glm-5.2",
        }[self.provider_id]
        if self.model_id != expected_model:
            raise ValueError("credential provider and model must match the fixed catalog")
        if self.configured and (
            self.masked_key is None or self.expires_at is None
        ):
            raise ValueError(
                "configured credentials require masked_key and expires_at"
            )
        if not self.configured and (
            self.masked_key is not None or self.expires_at is not None
        ):
            raise ValueError(
                "unconfigured credentials cannot expose key metadata"
            )
        return self


class ModelCredentialStatusList(RootModel[list[ModelCredentialStatus]]):
    pass


class ConversationSummary(ContractModel):
    conversation_id: UUID
    user_id: str
    course_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    mock_only: Literal[True] = True


class AnswerBlock(ContractModel):
    type: AnswerBlockType
    content: str


class Citation(ContractModel):
    citation_id: str
    chunk_id: str
    course_id: str
    course_title: str
    source_id: str
    source_title: str
    locator_type: Literal["page", "slide", "heading", "question", "none"]
    locator_start: int | str | None = None
    locator_end: int | str | None = None
    question_id: str | None = None
    heading_path: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def enforce_locator_invariants(self) -> "Citation":
        if any(not heading.strip() for heading in self.heading_path):
            raise ValueError("heading_path entries must be non-empty")
        if self.locator_end is not None and self.locator_start is None:
            raise ValueError("locator_end requires locator_start")
        if self.locator_type == "none":
            if (
                self.locator_start is not None
                or self.locator_end is not None
                or self.question_id is not None
                or self.heading_path
            ):
                raise ValueError("locator_type=none forbids precise locator metadata")
            return self
        if self.locator_type in {"page", "slide"}:
            start = self.locator_start
            end = self.locator_end
            if isinstance(start, bool) or not isinstance(start, int) or start < 1:
                raise ValueError("page and slide locators require a positive integer start")
            if end is not None and (
                isinstance(end, bool) or not isinstance(end, int) or end < start
            ):
                raise ValueError("page and slide locator end must be an integer >= start")
        elif self.locator_type == "heading":
            has_start = isinstance(self.locator_start, str) and bool(
                self.locator_start.strip()
            )
            if not has_start and not self.heading_path:
                raise ValueError("heading locator requires a heading")
        elif self.locator_type == "question":
            has_question = bool(self.question_id and self.question_id.strip())
            has_start = isinstance(self.locator_start, str) and bool(
                self.locator_start.strip()
            )
            if not has_question and not has_start:
                raise ValueError("question locator requires a question identifier")
        return self


class ExternalResource(ContractModel):
    resource_id: None
    course_id: str
    platform: Literal["bilibili"]
    resource_type: Literal["search"]
    title: str
    url: HttpUrl
    matched_topic: str
    review_status: Literal["unreviewed_live_search"]
    catalog_version: None
    query_keywords: list[Annotated[str, Field(min_length=1, max_length=32)]] = Field(
        min_length=1, max_length=3
    )
    generated_at: datetime
    evidence_role: Literal["supplementary_only"]

    @model_validator(mode="after")
    def enforce_bilibili_resource_invariants(self) -> "ExternalResource":
        parsed = urlsplit(str(self.url))
        query = parse_qs(parsed.query, keep_blank_values=True)
        if (
            self.generated_at.utcoffset() is None
            or parsed.scheme != "https"
            or parsed.hostname != "search.bilibili.com"
            or parsed.username is not None
            or parsed.password is not None
            or parsed.port is not None
            or parsed.path != "/all"
            or bool(parsed.fragment)
            or set(query) != {"keyword"}
            or len(query["keyword"]) != 1
            or not query["keyword"][0].strip()
            or query["keyword"][0] != " ".join(self.query_keywords)
        ):
            raise ValueError(
                "Bilibili resources require one fixed anonymous search URL"
            )
        return self


class TraceSourceSummary(ContractModel):
    course_id: str
    title: str
    locator: int | str | None = None


TraceCode = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]{0,99}$")]


class TraceSafeResult(ContractModel):
    """Student-visible Trace fields; unknown keys fail closed."""

    workflow_type: WorkflowType | None = None
    course_scope: CourseScope | None = None
    course_ids: list[str] | None = None
    knowledge_scope: KnowledgeScope | None = None
    auth_mode: Literal["mock", "github_oauth"] | None = None
    mode: Literal["mock", "synthetic_fixture_only"] | None = None
    hit_count: Annotated[int | None, Field(ge=0)] = None
    sources: list[TraceSourceSummary] | None = None
    rewritten_query: str | None = None
    candidate_order: list[str] | None = None
    reranked_order: list[str] | None = None
    evidence_status: EvidenceStatus | None = None
    used_general_knowledge: bool | None = None
    model_source: ModelSource | None = None
    provider_id: str | None = None
    model_id: str | None = None
    billing_label: TraceCode | None = None
    availability_status: TraceCode | None = None
    real_model_called: bool | None = None
    cache_hit: bool | None = None
    retry_count: Annotated[int | None, Field(ge=0)] = None
    failure_code: TraceCode | None = None
    degradation_code: TraceCode | None = None
    catalog_version: str | None = None
    fixture_only: bool | None = None
    normalized_topics: list[str] | None = None
    unreviewed_search_returned: bool | None = None
    reason_code: TraceCode | None = None
    candidate_count: Annotated[int | None, Field(ge=0)] = None
    accepted_count: Annotated[int | None, Field(ge=0)] = None
    external_resources_separate: bool | None = None
    stored: bool | None = None
    adapter: Literal["sqlite_mock", "sqlite"] | None = None

    @model_serializer(mode="wrap")
    def serialize_only_present_safe_fields(self, handler: Any) -> dict[str, Any]:
        return {key: value for key, value in handler(self).items() if value is not None}


class TraceEvent(ContractModel):
    event_id: str
    sequence: Annotated[int, Field(ge=0)]
    node: TraceCode
    status: TraceEventStatus
    duration_ms: Annotated[int, Field(ge=0)]
    result: TraceSafeResult


class ModelMetadata(ContractModel):
    provider_id: str
    model_id: str
    billing_label: str
    mock_only: bool


class WorkflowResult(ContractModel):
    workflow_run_id: UUID
    conversation_id: UUID
    message_id: UUID
    answer_id: UUID
    run_status: RunStatus
    answer_status: AnswerStatus
    workflow_type: WorkflowType
    course_scope: CourseScope
    course_ids: list[str]
    repository_answer: str | None
    general_supplement: str | None
    answer_blocks: list[AnswerBlock]
    workflow_output: dict[str, Any]
    evidence_status: EvidenceStatus
    citations: list[Citation]
    related_topics: list[str]
    related_questions: list[str]
    external_resources: list[ExternalResource] = Field(max_length=1)
    coverage_gaps: list[str]
    trace: list[TraceEvent]
    corpus_version: str
    course_pack_version: str | None
    workflow_version: str
    model_source: ModelSource
    model: ModelMetadata
    availability_status: str


class AnswerDelta(ContractModel):
    block_index: Annotated[int, Field(ge=0)]
    type: AnswerBlockType
    delta: Annotated[str, Field(min_length=1, max_length=4_000)]


class WorkflowStreamError(ContractModel):
    code: TraceCode
    detail: Annotated[str, Field(min_length=1, max_length=500)]


class WorkflowStreamEvent(ContractModel):
    """One ordered NDJSON event from a single Workflow Runtime execution."""

    kind: Literal["trace", "answer_delta", "result", "error"]
    workflow_run_id: UUID | None
    sequence: Annotated[int, Field(ge=0)]
    trace_event: TraceEvent | None = None
    answer_delta: AnswerDelta | None = None
    result: WorkflowResult | None = None
    error: WorkflowStreamError | None = None

    @model_validator(mode="after")
    def enforce_exact_event_payload(self) -> "WorkflowStreamEvent":
        payloads = {
            "trace": self.trace_event,
            "answer_delta": self.answer_delta,
            "result": self.result,
            "error": self.error,
        }
        if payloads[self.kind] is None or any(
            value is not None for key, value in payloads.items() if key != self.kind
        ):
            raise ValueError("stream events require exactly the payload matching kind")
        if self.kind != "error" and self.workflow_run_id is None:
            raise ValueError("non-error stream events require workflow_run_id")
        if self.result is not None:
            if self.workflow_run_id != self.result.workflow_run_id:
                raise ValueError("stream result must belong to workflow_run_id")
            if self.result.run_status not in {
                RunStatus.COMPLETED,
                RunStatus.INTERRUPTED,
                RunStatus.FAILED,
            }:
                raise ValueError("stream result must be terminal")
        return self


class WorkflowAttempt(ContractModel):
    workflow_run_id: UUID
    attempt_group_id: UUID
    regenerated_from_run_id: UUID | None
    request: WorkflowRunRequest
    result: WorkflowResult
    created_at: datetime
    updated_at: datetime
    expires_at: datetime

    @model_validator(mode="after")
    def enforce_attempt_links(self) -> "WorkflowAttempt":
        if self.workflow_run_id != self.result.workflow_run_id:
            raise ValueError("attempt workflow_run_id must match result")
        if self.request.conversation_id != self.result.conversation_id:
            raise ValueError("attempt request and result must share a conversation")
        if self.regenerated_from_run_id == self.workflow_run_id:
            raise ValueError("an attempt cannot regenerate itself")
        if self.updated_at < self.created_at:
            raise ValueError("attempt updated_at cannot precede created_at")
        if self.expires_at <= self.created_at:
            raise ValueError("attempt expires_at must follow created_at")
        return self


class ConversationDetail(ConversationSummary):
    runs: list[WorkflowAttempt] = Field(default_factory=list)


class FeedbackType(StrEnum):
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"
    KNOWLEDGE_ERROR = "knowledge_error"
    DID_NOT_ANSWER = "did_not_answer"


class FeedbackCreate(ContractModel):
    run_id: UUID
    feedback_type: FeedbackType
    note: Annotated[str | None, Field(max_length=2_000)] = None

    @field_validator("note")
    @classmethod
    def strip_note(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class FeedbackRecord(ContractModel):
    feedback_id: UUID
    user_id: str
    run_id: UUID
    conversation_id: UUID
    course_id: str
    workflow_type: WorkflowType
    feedback_type: FeedbackType
    note: str | None
    answer_status: AnswerStatus
    created_at: datetime
    expires_at: datetime
