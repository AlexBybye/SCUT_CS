from __future__ import annotations

from time import perf_counter
from uuid import UUID, uuid4

from .auth import AuthRequired, AuthenticatedPrincipal
from .byok_catalog import (
    ByokModelNotRegistered,
    ByokProviderDisabled,
    ByokProviderNotRegistered,
)
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
    WorkflowAttempt,
    WorkflowResult,
    WorkflowRunRequest,
)
from .model_catalog import ModelCatalog, ModelCatalogEntry
from .model_credentials import ModelCredentialError, ModelCredentialManager
from .ports import (
    CapabilityUnavailable,
    ExternalResourceDiscovery,
    ModelGateway,
    RetrievalGateway,
    UserKeyModelGateway,
    UserIdentity,
    WorkflowRepository,
)
from .registry import CourseRegistry, UnknownCourseError
from .state_machine import RunStateMachine


class ResourceNotFound(LookupError):
    pass


class ContractConflict(ValueError):
    pass


RequestIdentity = UserIdentity | AuthenticatedPrincipal


class IterationZeroService:
    def __init__(
        self,
        settings: Settings,
        registry: CourseRegistry,
        retrieval: RetrievalGateway,
        model: ModelGateway,
        resources: ExternalResourceDiscovery,
        repository: WorkflowRepository,
        model_catalog: ModelCatalog,
        credential_manager: ModelCredentialManager,
        byok_model: UserKeyModelGateway,
    ):
        self.settings = settings
        self.registry = registry
        self.retrieval = retrieval
        self.model = model
        self.resources = resources
        self.repository = repository
        self.model_catalog = model_catalog
        self.credential_manager = credential_manager
        self.byok_model = byok_model

    def create_conversation(
        self, user: RequestIdentity, course_id_or_alias: str
    ) -> ConversationSummary:
        course = self.registry.resolve(course_id_or_alias)
        if not course.fixture_available:
            raise CapabilityUnavailable(
                "course",
                f"{course.course_id} is closed and has no iteration-0 fixture",
            )
        return self.repository.create_conversation(
            str(user.user_id), course.course_id, course.display_name
        )

    def list_conversations(
        self, user: RequestIdentity
    ) -> list[ConversationSummary]:
        return self.repository.list_conversations(str(user.user_id))

    def get_conversation(
        self, user: RequestIdentity, conversation_id: UUID
    ) -> ConversationDetail:
        conversation = self.repository.get_conversation(str(user.user_id), conversation_id)
        if conversation is None:
            raise ResourceNotFound("conversation not found")
        return conversation

    def rename_conversation(
        self, user: RequestIdentity, conversation_id: UUID, title: str
    ) -> ConversationSummary:
        conversation = self.repository.rename_conversation(
            str(user.user_id), conversation_id, title
        )
        if conversation is None:
            raise ResourceNotFound("conversation not found")
        return conversation

    def delete_conversation(
        self, user: RequestIdentity, conversation_id: UUID
    ) -> None:
        if not self.repository.delete_conversation(
            str(user.user_id), conversation_id
        ):
            raise ResourceNotFound("conversation not found")

    def get_run(self, user: RequestIdentity, run_id: UUID) -> WorkflowResult:
        result = self.repository.get_run(str(user.user_id), run_id)
        if result is None:
            raise ResourceNotFound("workflow run not found")
        return result

    def run(self, user: RequestIdentity, request: WorkflowRunRequest) -> WorkflowResult:
        return self._run(user, request)

    def regenerate(
        self, user: RequestIdentity, run_id: UUID
    ) -> WorkflowAttempt:
        previous = self.repository.get_attempt(str(user.user_id), run_id)
        if previous is None:
            raise ResourceNotFound("workflow run not found")
        result = self._run(
            user,
            previous.request.model_copy(deep=True),
            attempt_group_id=previous.attempt_group_id,
            regenerated_from_run_id=previous.workflow_run_id,
        )
        attempt = self.repository.get_attempt(
            str(user.user_id), result.workflow_run_id
        )
        if attempt is None:
            raise RuntimeError("regenerated attempt was not persisted")
        return attempt

    def _run(
        self,
        user: RequestIdentity,
        request: WorkflowRunRequest,
        *,
        attempt_group_id: UUID | None = None,
        regenerated_from_run_id: UUID | None = None,
    ) -> WorkflowResult:
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
        model_entry: ModelCatalogEntry | None = None
        use_user_key = request.model_source == ModelSource.USER_KEY
        if not use_user_key:
            if self.settings.model_mode == "mock":
                if (
                    request.provider_id != "mock"
                    or request.model_id != "deterministic-fixture-v1"
                ):
                    raise CapabilityUnavailable(
                        "model",
                        "no real platform model is configured; use the explicit iteration-0 mock",
                    )
                model_provider_id = "mock"
                model_id = "deterministic-fixture-v1"
                billing_label = "not_applicable_mock"
                availability_status = "mock_only"
                mock_only = True
            else:
                model_entry = self.model_catalog.resolve(
                    request.provider_id,
                    request.model_id,
                    request.model_source,
                )
                model_provider_id = model_entry.provider_id
                model_id = model_entry.model_id
                billing_label = model_entry.billing_label
                availability_status = model_entry.availability_status
                mock_only = False
        else:
            if not isinstance(user, AuthenticatedPrincipal) or user.is_mock:
                raise AuthRequired()
            try:
                provider = self.model_catalog.byok_catalog.require_enabled(
                    request.provider_id
                )
                selected_model = self.model_catalog.byok_catalog.resolve_model(
                    request.provider_id, request.model_id
                )
            except ByokProviderNotRegistered:
                raise ModelCredentialError(
                    status_code=422,
                    code="byok_provider_not_registered",
                    detail="该 BYOK 供应商未登记。",
                ) from None
            except ByokProviderDisabled:
                raise ModelCredentialError(
                    status_code=503,
                    code="byok_provider_disabled",
                    detail="该 BYOK 供应商当前未启用。",
                ) from None
            except ByokModelNotRegistered:
                raise ModelCredentialError(
                    status_code=422,
                    code="byok_model_not_registered",
                    detail="该 BYOK 模型未登记。",
                ) from None
            model_provider_id = provider.provider_id.value
            model_id = selected_model.model_id
            billing_label = "user_provider_billing"
            availability_status = "user_key_enabled"
            mock_only = False

        conversation = self.repository.get_conversation(
            str(user.user_id), request.conversation_id
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
        run_id = uuid4()
        message_id = uuid4()
        answer_id = uuid4()

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
            node="identity",
            result={"auth_mode": "mock" if user.is_mock else "github_oauth"},
        )

        started = perf_counter()
        try:
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
        except Exception:
            self._persist_failed_attempt(
                user=user,
                request=request,
                course_id=course.course_id,
                machine=machine,
                trace=trace,
                failure_node="fixture_retrieval",
                duration_ms=_elapsed_ms(started),
                run_id=run_id,
                message_id=message_id,
                answer_id=answer_id,
                model_provider_id=model_provider_id,
                model_id=model_id,
                billing_label=billing_label,
                mock_only=mock_only,
                attempt_group_id=attempt_group_id,
                regenerated_from_run_id=regenerated_from_run_id,
            )
            raise
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
        api_key: str | None = None
        try:
            if use_user_key:
                assert isinstance(user, AuthenticatedPrincipal)
                api_key = self.credential_manager.load_api_key(
                    user, request.provider_id
                )
                generated = self.byok_model.generate(
                    api_key=api_key,
                    request=request,
                    sources=sources,
                )
            else:
                generated = self.model.generate(request, sources)
        except AuthRequired:
            raise
        except Exception:
            self._persist_failed_attempt(
                user=user,
                request=request,
                course_id=course.course_id,
                machine=machine,
                trace=trace,
                failure_node="byok_model" if use_user_key else (
                    "mock_model" if mock_only else "openrouter_model"
                ),
                duration_ms=_elapsed_ms(started),
                run_id=run_id,
                message_id=message_id,
                answer_id=answer_id,
                model_provider_id=model_provider_id,
                model_id=model_id,
                billing_label=billing_label,
                mock_only=mock_only,
                attempt_group_id=attempt_group_id,
                regenerated_from_run_id=regenerated_from_run_id,
            )
            raise
        finally:
            api_key = None
        _append_trace(
            trace,
            node=(
                "byok_model"
                if use_user_key
                else "mock_model" if mock_only else "openrouter_model"
            ),
            duration_ms=_elapsed_ms(started),
            result={
                "model_source": request.model_source.value,
                "provider_id": model_provider_id,
                "model_id": model_id,
                "billing_label": billing_label,
                "availability_status": availability_status,
                "real_model_called": not mock_only,
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
            and self.settings.bilibili_resources_enabled
        ):
            focused_keywords = generated.bilibili_search_keywords
            if focused_keywords:
                started = perf_counter()
                try:
                    external_resources = self.resources.discover(
                        course_id=course.course_id,
                        course_title=course.display_name,
                        keywords=tuple(focused_keywords),
                    )
                except Exception:
                    external_resources = []
                    _append_trace(
                        trace,
                        node="bilibili_link_discovery",
                        status=TraceEventStatus.FAILED,
                        duration_ms=_elapsed_ms(started),
                        result={
                            "failure_code": "bilibili_link_discovery_failed",
                            "external_resources_separate": True,
                        },
                    )
                else:
                    normalized_topics = (
                        external_resources[0].query_keywords
                        if external_resources
                        else []
                    )
                    _append_trace(
                        trace,
                        node="bilibili_link_discovery",
                        duration_ms=_elapsed_ms(started),
                        result={
                            "hit_count": len(external_resources),
                            "normalized_topics": normalized_topics,
                            "unreviewed_search_returned": bool(external_resources),
                            "external_resources_separate": True,
                        },
                    )
            else:
                external_resources = []
                _append_trace(
                    trace,
                    node="bilibili_link_discovery",
                    status=TraceEventStatus.SKIPPED,
                    result={
                        "reason_code": "no_focused_topic",
                        "external_resources_separate": True,
                    },
                )
        else:
            external_resources = []
            _append_trace(
                trace,
                node="bilibili_link_discovery",
                status=TraceEventStatus.SKIPPED,
                result={
                    "reason_code": "disabled_by_scope_or_configuration",
                    "external_resources_separate": True,
                },
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
        result = WorkflowResult(
            workflow_run_id=run_id,
            conversation_id=request.conversation_id,
            message_id=message_id,
            answer_id=answer_id,
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
                provider_id=model_provider_id,
                model_id=model_id,
                billing_label=billing_label,
                mock_only=mock_only,
            ),
            availability_status=availability_status,
        )

        _append_trace(
            result.trace,
            node="persistence",
            result={"stored": True, "adapter": self.settings.storage_mode},
        )
        self.repository.save_run(
            str(user.user_id),
            request,
            result,
            attempt_group_id=attempt_group_id,
            regenerated_from_run_id=regenerated_from_run_id,
            auth_session_id=(
                user.auth_session_id
                if isinstance(user, AuthenticatedPrincipal)
                else None
            ),
        )
        return result

    def _persist_failed_attempt(
        self,
        *,
        user: RequestIdentity,
        request: WorkflowRunRequest,
        course_id: str,
        machine: RunStateMachine,
        trace: list[TraceEvent],
        failure_node: str,
        duration_ms: int,
        run_id: UUID,
        message_id: UUID,
        answer_id: UUID,
        model_provider_id: str,
        model_id: str,
        billing_label: str,
        mock_only: bool,
        attempt_group_id: UUID | None,
        regenerated_from_run_id: UUID | None,
    ) -> None:
        machine.transition(RunStatus.FAILED)
        _append_trace(
            trace,
            node=failure_node,
            status=TraceEventStatus.FAILED,
            duration_ms=duration_ms,
            result={
                "failure_code": "workflow_execution_failed",
                "model_source": request.model_source.value,
                "provider_id": model_provider_id,
                "model_id": model_id,
                "billing_label": billing_label,
                "availability_status": "execution_failed",
            },
        )
        result = WorkflowResult(
            workflow_run_id=run_id,
            conversation_id=request.conversation_id,
            message_id=message_id,
            answer_id=answer_id,
            run_status=machine.status,
            answer_status=AnswerStatus.ERROR,
            workflow_type=request.workflow_type,
            course_scope=request.course_scope,
            course_ids=[course_id],
            repository_answer=None,
            general_supplement=None,
            answer_blocks=[],
            workflow_output={
                "contract_only": True,
                "payload_type": request.workflow_type.value,
                "failure_code": "workflow_execution_failed",
            },
            evidence_status=EvidenceStatus.NOT_EVALUATED,
            citations=[],
            related_topics=[],
            related_questions=[],
            external_resources=[],
            coverage_gaps=["本次同步执行失败，未生成回答。"],
            trace=trace,
            corpus_version="fixture-corpus-v1",
            course_pack_version=None,
            workflow_version="workflow-contract-v1",
            model_source=request.model_source,
            model=ModelMetadata(
                provider_id=model_provider_id,
                model_id=model_id,
                billing_label=billing_label,
                mock_only=mock_only,
            ),
            availability_status="execution_failed",
        )
        _append_trace(
            result.trace,
            node="persistence",
            result={"stored": True, "adapter": self.settings.storage_mode},
        )
        self.repository.save_run(
            str(user.user_id),
            request,
            result,
            attempt_group_id=attempt_group_id,
            regenerated_from_run_id=regenerated_from_run_id,
            auth_session_id=(
                user.auth_session_id
                if isinstance(user, AuthenticatedPrincipal)
                else None
            ),
        )


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
