from __future__ import annotations

from time import perf_counter
from uuid import UUID, uuid4

from .config import Settings
from .contracts import (
    AnswerBlock,
    AnswerBlockType,
    AnswerStatus,
    Citation,
    ConversationDetail,
    ConversationSummary,
    CourseScope,
    EvidenceStatus,
    KnowledgeScope,
    ModelMetadata,
    ModelSource,
    RunStatus,
    TraceEvent,
    TraceEventStatus,
    TraceSafeResult,
    WorkflowResult,
    WorkflowRunRequest,
)
from .ports import (
    CapabilityUnavailable,
    ExternalResourceCatalog,
    IdentityProvider,
    ModelGateway,
    RetrievalGateway,
    WorkflowRepository,
)
from .registry import CourseRegistry, UnknownCourseError
from .state_machine import RunStateMachine


class ResourceNotFound(LookupError):
    pass


class ContractConflict(ValueError):
    pass


class IterationZeroService:
    def __init__(
        self,
        settings: Settings,
        registry: CourseRegistry,
        identity: IdentityProvider,
        retrieval: RetrievalGateway,
        model: ModelGateway,
        resources: ExternalResourceCatalog,
        repository: WorkflowRepository,
    ):
        self.settings = settings
        self.registry = registry
        self.identity = identity
        self.retrieval = retrieval
        self.model = model
        self.resources = resources
        self.repository = repository

    def create_conversation(self, course_id_or_alias: str) -> ConversationSummary:
        user = self.identity.current_user()
        course = self.registry.resolve(course_id_or_alias)
        if not course.fixture_available:
            raise CapabilityUnavailable(
                "course",
                f"{course.course_id} is closed and has no iteration-0 fixture",
            )
        return self.repository.create_conversation(user.user_id, course.course_id)

    def get_conversation(self, conversation_id: UUID) -> ConversationDetail:
        user = self.identity.current_user()
        conversation = self.repository.get_conversation(user.user_id, conversation_id)
        if conversation is None:
            raise ResourceNotFound("conversation not found")
        return conversation

    def get_run(self, run_id: UUID) -> WorkflowResult:
        user = self.identity.current_user()
        result = self.repository.get_run(user.user_id, run_id)
        if result is None:
            raise ResourceNotFound("workflow run not found")
        return result

    def run(self, request: WorkflowRunRequest) -> WorkflowResult:
        if request.course_scope == CourseScope.CROSS:
            if not self.settings.cross_course_enabled:
                raise CapabilityUnavailable(
                    "cross_course",
                    "cross-course execution is disabled pending its decision gate",
                )
            raise CapabilityUnavailable(
                "cross_course",
                "iteration 0 freezes the contract but has no cross-course runtime",
            )
        if request.model_source != ModelSource.PLATFORM_DEFAULT:
            raise CapabilityUnavailable(
                "user_key", "BYOK is disabled until iteration 1"
            )
        if request.provider_id != "mock" or request.model_id != "deterministic-fixture-v1":
            raise CapabilityUnavailable(
                "model",
                "no real platform model is configured; use the explicit iteration-0 mock",
            )

        user = self.identity.current_user()
        conversation = self.repository.get_conversation(
            user.user_id, request.conversation_id
        )
        if conversation is None:
            raise ResourceNotFound("conversation not found")

        try:
            course = self.registry.get(request.course_id or "")
        except UnknownCourseError as exc:
            raise ContractConflict(str(exc)) from exc
        if request.course_id != course.course_id:
            raise ContractConflict("workflow request must use the canonical course_id")
        if conversation.course_id != course.course_id:
            raise ContractConflict(
                "workflow course does not match the bound conversation course"
            )
        if not course.fixture_available:
            raise CapabilityUnavailable(
                "course", f"{course.course_id} has no iteration-0 fixture"
            )

        machine = RunStateMachine()
        machine.transition(RunStatus.RUNNING)
        trace: list[TraceEvent] = []

        _append_trace(
            trace,
            node="request_validation",
            result={
                "workflow_type": request.workflow_type.value,
                "course_scope": request.course_scope.value,
                "course_ids": [course.course_id],
                "knowledge_scope": request.knowledge_scope.value,
            },
        )
        _append_trace(
            trace,
            node="mock_identity",
            result={"mode": "mock"},
        )

        started = perf_counter()
        sources = self.retrieval.search([course.course_id], request.user_input)
        invalid_source_ids = [
            source.chunk_id
            for source in sources
            if source.course_id != course.course_id
        ]
        if invalid_source_ids:
            raise ContractConflict(
                "source authorization guard rejected a source outside the conversation course"
            )
        _append_trace(
            trace,
            node="fixture_retrieval",
            duration_ms=_elapsed_ms(started),
            result={
                "mode": "synthetic_fixture_only",
                "hit_count": len(sources),
                "sources": [
                    {
                        "course_id": source.course_id,
                        "title": source.source_title,
                        "locator": source.locator_start,
                    }
                    for source in sources
                ],
            },
        )
        _append_trace(
            trace,
            node="source_authorization_guard",
            result={
                "candidate_count": len(sources),
                "accepted_count": len(sources),
            },
        )

        started = perf_counter()
        generated = self.model.generate(request, sources)
        _append_trace(
            trace,
            node="mock_model",
            duration_ms=_elapsed_ms(started),
            result={
                "provider_id": "mock",
                "model_id": "deterministic-fixture-v1",
                "real_model_called": False,
            },
        )

        citations = [
            Citation(
                citation_id=f"S{index}",
                chunk_id=source.chunk_id,
                course_id=source.course_id,
                course_title=self.registry.get(source.course_id).display_name,
                source_id=source.source_id,
                source_title=source.source_title,
                locator_type=source.locator_type,
                locator_start=source.locator_start,
                locator_end=source.locator_end,
                question_id=source.question_id,
                heading_path=list(source.heading_path),
            )
            for index, source in enumerate(sources, start=1)
        ]

        if (
            request.include_bilibili_resources
            and request.knowledge_scope != KnowledgeScope.COURSE_ONLY
            and self.settings.bilibili_catalog_enabled
        ):
            started = perf_counter()
            external_resources = self.resources.match(
                course.course_id, request.user_input, limit=3
            )
            _append_trace(
                trace,
                node="bilibili_fixture_match",
                duration_ms=_elapsed_ms(started),
                result={
                    "catalog_version": self.resources.catalog_version,
                    "hit_count": len(external_resources),
                    "fixture_only": True,
                },
            )
        else:
            external_resources = []
            _append_trace(
                trace,
                node="bilibili_fixture_match",
                status=TraceEventStatus.SKIPPED,
                result={"reason_code": "disabled_by_scope_or_configuration"},
            )

        _append_trace(
            trace,
            node="citation_guard",
            result={
                "candidate_count": len(citations),
                "accepted_count": len(citations),
                "external_resources_separate": True,
            },
        )

        machine.transition(RunStatus.COMPLETED)
        has_evidence = bool(citations)
        run_id = uuid4()
        result = WorkflowResult(
            workflow_run_id=run_id,
            conversation_id=request.conversation_id,
            message_id=uuid4(),
            answer_id=uuid4(),
            run_status=machine.status,
            answer_status=(
                AnswerStatus.ANSWERED
                if has_evidence
                else AnswerStatus.INSUFFICIENT_EVIDENCE
            ),
            workflow_type=request.workflow_type,
            course_scope=request.course_scope,
            course_ids=[course.course_id],
            repository_answer=generated.repository_answer,
            general_supplement=None,
            answer_blocks=[
                AnswerBlock(
                    type=AnswerBlockType.REPOSITORY,
                    content=generated.repository_answer,
                )
            ],
            workflow_output={
                "contract_only": True,
                "payload_type": request.workflow_type.value,
            },
            evidence_status=(
                EvidenceStatus.SUFFICIENT
                if has_evidence
                else EvidenceStatus.INSUFFICIENT
            ),
            citations=citations,
            related_topics=list(generated.related_topics),
            related_questions=list(generated.related_questions),
            external_resources=external_resources,
            coverage_gaps=(
                []
                if has_evidence
                else ["没有匹配到合成 passed Fixture；未尝试真实课程资料"]
            ),
            trace=trace,
            corpus_version="fixture-corpus-v1",
            course_pack_version=None,
            workflow_version="workflow-contract-v1",
            model_source=request.model_source,
            model=ModelMetadata(
                provider_id="mock",
                model_id="deterministic-fixture-v1",
                billing_label="not_applicable_mock",
                mock_only=True,
            ),
            availability_status="mock_only",
        )

        # First commit proves the answer/source/trace payload is durable. The
        # second upsert records the persistence event produced by that commit.
        self.repository.save_run(user.user_id, request, result)
        _append_trace(
            result.trace,
            node="persistence",
            result={"stored": True, "adapter": "sqlite_mock"},
        )
        self.repository.save_run(user.user_id, request, result)
        return result


def _append_trace(
    trace: list[TraceEvent],
    *,
    node: str,
    result: TraceSafeResult | dict[str, object],
    status: TraceEventStatus = TraceEventStatus.COMPLETED,
    duration_ms: int = 0,
) -> None:
    trace.append(
        TraceEvent(
            event_id=str(uuid4()),
            sequence=len(trace),
            node=node,
            status=status,
            duration_ms=max(duration_ms, 0),
            result=result,
        )
    )


def _elapsed_ms(started: float) -> int:
    return max(int((perf_counter() - started) * 1000), 0)
