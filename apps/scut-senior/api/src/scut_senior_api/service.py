from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from time import perf_counter
from uuid import UUID, uuid4

from .auth import AuthRequired, AuthenticatedPrincipal, utc_now
from .agent_loop import (
    AgentDecisionGateway,
    AgentBudget,
    AgentState,
    RuleBasedAgentDecision,
    choose_next_action,
    reduce_agent_event,
)
from .adapters.bilibili import derive_question_keywords, normalize_keywords
from .adapters.exam_facts import ExamFactsUnavailable
from .byok_catalog import (
    ByokModelNotRegistered,
    ByokProviderDisabled,
    ByokProviderNotRegistered,
)
from .config import Settings
from .contracts import (
    AccountDeletionSummary,
    AccountExport,
    AccountExportConversation,
    AccountExportContribution,
    AccountExportMaterial,
    AccountExportRun,
    AnswerBlock,
    AnswerBlockType,
    AnswerStatus,
    Citation,
    ContributionDraftSubmit,
    ContributionPreview,
    ContributionPreviewRequest,
    ContributionRecord,
    ContributionState,
    ContributionSubmit,
    ConversationDetail,
    ConversationSummary,
    CourseScope,
    EvidenceStatus,
    ExamReviewPayload,
    ExternalResource,
    FeedbackCreate,
    FeedbackRecord,
    KnowledgeScope,
    MaintainerContributionExport,
    MaintainerContributionTransition,
    ModelMetadata,
    ModelSource,
    RunStatus,
    TemporaryMaterialCreate,
    TemporaryMaterialDetail,
    TemporaryMaterialRecord,
    TraceEvent,
    TraceEventStatus,
    TraceSafeResult,
    WorkflowAttempt,
    WorkflowResult,
    WorkflowRunRequest,
    WorkflowType,
)
from .contributions import (
    build_contribution_preview,
    derive_proposed_repo_path,
    derive_proposed_source_id,
    normalize_contribution_markdown,
    resolve_transition_target,
    states_allowed_for_target,
    validate_contribution_transition,
    validate_github_pr_url,
    ContributionTransitionError,
)
from .exam_review import (
    ExamReviewPlan,
    build_exam_review_plan,
    compose_retrieval_query,
    render_exam_review_appendix,
)
from .harness_registry import HARNESS_REGISTRY
from .model_catalog import ModelCatalog, ModelCatalogEntry
from .model_credentials import ModelCredentialError, ModelCredentialManager
from .ports import (
    CapabilityUnavailable,
    ConversationTurn,
    ExternalResourceDiscovery,
    GeneratedAnswer,
    HumanizerGateway,
    ModelGateway,
    RetrievalBatch,
    RetrievalGateway,
    RetrievedSource,
    UserKeyModelGateway,
    UserIdentity,
    WorkflowRepository,
)
from .registry import CourseRegistry, UnknownCourseError
from .runtime_guards import (
    GuardedAnswer,
    RuntimeGuardError,
    build_guarded_answer,
    normalize_topics,
    protect_humanizer_output,
)
from .state_machine import RunStateMachine
from .workflow_stream import StreamingTrace, WorkflowStreamSession
from .workflow_focus import build_workflow_focus, enforce_tone_visible_callout


class ResourceNotFound(LookupError):
    pass


def _parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("stored timestamps must be timezone-aware")
    return parsed


class ContractConflict(ValueError):
    pass


RequestIdentity = UserIdentity | AuthenticatedPrincipal


@dataclass(frozen=True, slots=True)
class ExamReviewPlanContext:
    """One request-local deterministic exam-review plan and its query."""

    plan: "ExamReviewPlan"
    retrieval_query: str


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
        humanizer: HumanizerGateway | None = None,
        zhipu_model: ModelGateway | None = None,
        exam_facts: object | None = None,
        agent_decision: AgentDecisionGateway | None = None,
    ):
        self.settings = settings
        self.registry = registry
        self.retrieval = retrieval
        self.model = model
        self.zhipu_model = zhipu_model
        self.resources = resources
        self.repository = repository
        self.model_catalog = model_catalog
        self.credential_manager = credential_manager
        self.byok_model = byok_model
        self.humanizer = humanizer
        # Optional iteration-5 exam-review facts provider (fixture or local
        # corpus). ``None`` keeps the pre-iteration-5 behaviour exactly.
        self.exam_facts = exam_facts
        self.agent_decision = agent_decision or RuleBasedAgentDecision()

    def create_conversation(
        self, user: RequestIdentity, course_id_or_alias: str
    ) -> ConversationSummary:
        course = self.registry.resolve(course_id_or_alias)
        if not self._course_available(course.course_id):
            raise CapabilityUnavailable(
                "course",
                f"{course.course_id} is not enabled for the configured retrieval mode",
            )
        return self.repository.create_conversation(
            str(user.user_id), course.course_id, course.display_name
        )

    def preview_exam_review_plan(
        self, user: RequestIdentity, request: WorkflowRunRequest
    ) -> dict[str, object]:
        """Build a user-owned deterministic plan before spending model budget."""
        if request.workflow_type is not WorkflowType.EXAM_REVIEW:
            raise ContractConflict("exam review plan preview requires exam_review workflow")
        conversation = self.repository.get_conversation(
            str(user.user_id), request.conversation_id
        )
        if conversation is None:
            raise ResourceNotFound("conversation not found")
        course = self.registry.get(request.course_id or "")
        if conversation.course_id != course.course_id:
            raise ContractConflict("workflow course does not match the bound conversation course")
        if not self._course_available(course.course_id):
            raise CapabilityUnavailable("course", "course is unavailable")
        context = self._plan_exam_review(request, course, [])
        if context is None:
            raise CapabilityUnavailable("exam_review_plan", "exam review plan is unavailable")
        return {
            "confirmation_required": True,
            "plan": context.plan.to_output_dict(),
            "retrieval_query": context.retrieval_query,
        }

    def load_course_plugin(
        self, user: RequestIdentity, course_id_or_alias: str
    ) -> str:
        course = self.registry.resolve(course_id_or_alias)
        # A course the retrieval adapter cannot serve must not become "loaded":
        # that is exactly the fork that made the plugin panel and the course
        # list disagree (loaded but no data). Fail closed instead.
        if not self._retrieval_course_available(course.course_id):
            raise CapabilityUnavailable(
                "course", "该课程无本地语料数据，无法装载。"
            )
        self.repository.set_course_plugin_loaded(
            course.course_id, True, str(user.user_id)
        )
        return course.course_id

    def unload_course_plugin(
        self, user: RequestIdentity, course_id_or_alias: str
    ) -> str:
        course = self.registry.resolve(course_id_or_alias)
        self.repository.set_course_plugin_loaded(
            course.course_id, False, str(user.user_id)
        )
        return course.course_id

    def _course_available(self, course_id: str) -> bool:
        """A course is usable only when its plugin is loaded AND retrieval serves it."""
        if not self.repository.is_course_plugin_loaded(course_id):
            return False
        return self._retrieval_course_available(course_id)

    def _retrieval_course_available(self, course_id: str) -> bool:
        check = getattr(self.retrieval, "is_course_available", None)
        if callable(check):
            return bool(check(course_id))
        if self.settings.retrieval_mode == "fixture":
            # Compatibility is limited to injected legacy test doubles. An
            # explicit local corpus must always prove active-course state.
            return self.registry.get(course_id).fixture_available
        raise CapabilityUnavailable(
            "retrieval", "local corpus adapter cannot verify active course state"
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

    def submit_feedback(
        self, user: RequestIdentity, payload: FeedbackCreate
    ) -> FeedbackRecord:
        result = self.get_run(user, payload.run_id)
        now = utc_now()
        record = FeedbackRecord(
            feedback_id=uuid4(),
            user_id=str(user.user_id),
            run_id=payload.run_id,
            conversation_id=result.conversation_id,
            course_id=result.course_ids[0] if result.course_ids else "",
            workflow_type=result.workflow_type,
            feedback_type=payload.feedback_type,
            note=payload.note,
            answer_status=result.answer_status,
            created_at=now,
            expires_at=now + FEEDBACK_TTL,
        )
        self.repository.save_feedback(str(user.user_id), record)
        return record

    def list_feedback(self, user: RequestIdentity) -> list[FeedbackRecord]:
        return self.repository.list_feedback(str(user.user_id))

    # ------------------------------------------------------------------
    # 迭代 7（SOP §12）：临时材料精读治理与贡献待处理队列。
    # 临时材料只属于当前用户、只在会话内联合检索，默认不进入公共索引、
    # 课程包或跨用户缓存；GitHub App 决策门未确认，提交一律进入维护者
    # 待处理队列，不实现也不冒充自动 PR。
    # ------------------------------------------------------------------

    def _require_contribution_capable_repository(self):
        repository = self.repository
        save_material = getattr(repository, "save_temporary_material", None)
        if save_material is None or not callable(save_material):
            raise CapabilityUnavailable(
                "temporary_materials",
                "the configured storage adapter does not support iteration-7 "
                "temporary materials yet",
            )
        return repository

    def _resolve_material_course(self, course_id: str):
        try:
            course = self.registry.get(course_id)
        except UnknownCourseError as exc:
            raise ContractConflict(str(exc)) from exc
        return course

    def save_temporary_material(
        self,
        user: RequestIdentity,
        payload: TemporaryMaterialCreate,
    ) -> TemporaryMaterialDetail:
        course = self._resolve_material_course(payload.course_id)
        if not self._course_available(course.course_id):
            raise CapabilityUnavailable(
                "course",
                f"{course.course_id} is not enabled for the configured retrieval mode",
            )
        conversation = self.repository.get_conversation(
            str(user.user_id), payload.conversation_id
        )
        if conversation is None:
            raise ResourceNotFound("conversation not found")
        if conversation.course_id != course.course_id:
            raise ContractConflict(
                "temporary material course does not match the bound conversation course"
            )
        repository = self._require_contribution_capable_repository()
        material = repository.save_temporary_material(
            user_id=str(user.user_id),
            conversation_id=payload.conversation_id,
            course_id=course.course_id,
            title=payload.title,
            content=payload.content,
        )
        assert isinstance(material, TemporaryMaterialDetail)
        return material

    def list_temporary_materials(
        self, user: RequestIdentity
    ) -> list[TemporaryMaterialRecord]:
        self._require_contribution_capable_repository()
        return list(self.repository.list_temporary_materials(str(user.user_id)))

    def get_temporary_material(
        self,
        user: RequestIdentity,
        material_id: UUID,
    ) -> TemporaryMaterialDetail:
        self._require_contribution_capable_repository()
        record = self.repository.get_temporary_material(
            str(user.user_id), material_id, include_content=True
        )
        if record is None or not isinstance(record, TemporaryMaterialDetail):
            raise ResourceNotFound("temporary material not found")
        return record

    def delete_temporary_material(
        self, user: RequestIdentity, material_id: UUID
    ) -> None:
        self._require_contribution_capable_repository()
        deleted = self.repository.delete_temporary_material(
            str(user.user_id), material_id
        )
        if not deleted:
            raise ResourceNotFound("temporary material not found")

    def build_contribution_preview(
        self,
        user: RequestIdentity,
        payload: ContributionPreviewRequest,
    ) -> ContributionPreview:
        """确定性转换预览：不落库、不调用模型、不改变原始内容。"""

        course = self._resolve_material_course(payload.course_id)
        preview = build_contribution_preview(
            course_id=payload.course_id,
            title=payload.title,
            content=payload.content,
        )
        return preview.model_copy(
            update={
                "proposed_repo_path": derive_proposed_repo_path(
                    course.repository_paths,
                    course_id=course.course_id,
                    title=payload.title,
                    content=payload.content,
                )
            }
        )

    def submit_contribution(
        self,
        user: RequestIdentity,
        payload: ContributionSubmit,
    ) -> ContributionRecord:
        """从已保存的临时材料创建贡献（add file 语义，落点为学科资料）。

        GitHub App 未确认：`as_draft=False` 直接进入维护者待处理队列
        （submitted），绝不创建 PR，也不使用用户 OAuth token 冒充自动 PR。
        """

        course = self._resolve_material_course(payload.course_id)
        repository = self._require_contribution_capable_repository()
        material = repository.get_temporary_material(
            str(user.user_id), payload.material_id, include_content=True
        )
        if material is None or not isinstance(material, TemporaryMaterialDetail):
            raise ResourceNotFound("temporary material not found")
        if material.course_id != payload.course_id:
            raise ContractConflict(
                "contribution course must match the temporary material course"
            )
        title = (
            payload.title
            or material.title
            or (
                normalize_contribution_markdown(material.content)
                .split("\n", 1)[0]
                .lstrip("#")
                .strip()
                or f"{course.display_name} 贡献"
            )
        )
        state = (
            ContributionState.DRAFT if payload.as_draft else ContributionState.SUBMITTED
        )
        return repository.create_contribution(
            user_id=str(user.user_id),
            material_id=payload.material_id,
            course_id=material.course_id,
            proposed_source_id=derive_proposed_source_id(
                material.course_id,
                normalize_contribution_markdown(material.content),
            ),
            proposed_repo_path=derive_proposed_repo_path(
                course.repository_paths,
                course_id=course.course_id,
                title=title,
                content=material.content,
            ),
            title=title[:200],
            content_snapshot=material.content,
            state=state,
        )

    def submit_contribution_draft(
        self,
        user: RequestIdentity,
        contribution_id: UUID,
        payload: ContributionDraftSubmit,
    ) -> ContributionRecord:
        """把草稿推进到 submitted（进入待处理队列），需要完整确认。"""

        repository = self._require_contribution_capable_repository()
        current = repository.get_contribution(str(user.user_id), contribution_id)
        if current is None:
            raise ResourceNotFound("contribution not found")
        validate_contribution_transition(current.state, action="submit")
        return repository.transition_contribution(
            contribution_id,
            from_states=frozenset({ContributionState.DRAFT}),
            target_state=ContributionState.SUBMITTED,
            pr_url=None,
            note=None,
        )  # type: ignore[return-value]

    def list_contributions(self, user: RequestIdentity) -> list[ContributionRecord]:
        self._require_contribution_capable_repository()
        return list(self.repository.list_contributions(str(user.user_id)))

    def get_contribution(
        self, user: RequestIdentity, contribution_id: UUID
    ) -> ContributionRecord:
        self._require_contribution_capable_repository()
        record = self.repository.get_contribution(str(user.user_id), contribution_id)
        if record is None:
            raise ResourceNotFound("contribution not found")
        return record

    def maintainer_transition_contribution(
        self,
        contribution_id: UUID,
        payload: MaintainerContributionTransition,
    ) -> ContributionRecord:
        """维护者队列推进：只改状态与人工填写的 PR 链接，永不自动合并仓库。"""

        repository = self._require_contribution_capable_repository()
        target_state = resolve_transition_target(payload.action)
        pr_url: str | None = None
        if target_state == ContributionState.PR_OPEN:
            if payload.pr_url is None:
                raise ContractConflict("mark_pr_open requires a PR link")
            pr_url = validate_github_pr_url(str(payload.pr_url))
        elif payload.pr_url is not None:
            raise ContractConflict(
                "pr_url is only accepted with the mark_pr_open action"
            )
        allowed = states_allowed_for_target(target_state)
        record = repository.transition_contribution(
            contribution_id,
            from_states=allowed,
            target_state=target_state,
            pr_url=pr_url,
            note=payload.note,
        )
        if record is None:
            raise ContractConflict(
                "contribution is not in a state that accepts this transition"
            )
        return record

    def list_maintainer_queue(
        self, state: ContributionState | None = None
    ) -> list[ContributionRecord]:
        self._require_contribution_capable_repository()
        return list(self.repository.list_maintainer_queue(state))

    def maintainer_export_contribution(
        self, contribution_id: UUID
    ) -> MaintainerContributionExport:
        """维护者导出包：一次人工 add file 操作所需的路径、内容与命令。

        应用不写工作树、不执行 git；推送与 PR 永远由维护者人工完成。
        """

        repository = self._require_contribution_capable_repository()
        fetched = repository.get_contribution_with_payload(contribution_id)
        if fetched is None:
            raise ResourceNotFound("contribution not found")
        record, content = fetched
        if not content:
            raise ContractConflict(
                "该贡献的待审副本已到期清理，无法导出。"
            )
        repo_path = record.proposed_repo_path or derive_proposed_repo_path(
            self.registry.get(record.course_id).repository_paths,
            course_id=record.course_id,
            title=record.title,
            content=content,
        )
        filename = repo_path.rsplit("/", 1)[-1]
        branch = f"contribution-{record.contribution_id.hex[:8]}"
        directory = repo_path.rsplit("/", 1)[0]
        suggested_commands = [
            f"git checkout -b {branch}",
            f"mkdir -p '{directory}'",
            f"# 将导出的内容写入：{repo_path}",
            f"git add '{repo_path}'",
            f"git commit -m '资料贡献：{record.title}（{record.course_id}）'",
            f"git push -u origin {branch}",
            "# 在 GitHub 上发起 PR 后，回队列执行 mark_pr_open 并填入 PR 链接",
        ]
        return MaintainerContributionExport(
            contribution_id=record.contribution_id,
            state=record.state,
            course_id=record.course_id,
            title=record.title,
            repo_path=repo_path,
            filename=filename,
            content_snapshot=content,
            char_count=len(content),
            suggested_branch=branch,
            suggested_commands=suggested_commands,
        )

    def delete_account(self, user: AuthenticatedPrincipal) -> AccountDeletionSummary:
        """注销：物理删除本人全部私有数据并封锁再次登录（§16 待确认项 3）。"""

        repository = self._require_account_lifecycle_repository()
        try:
            counts = repository.delete_account(str(user.user_id))
        except LookupError as exc:
            raise ResourceNotFound("account not found") from exc
        return AccountDeletionSummary(
            conversations=counts["conversations"],
            workflow_runs=counts["workflow_runs"],
            feedback=counts["feedback"],
            temporary_materials=counts["temporary_materials"],
            contributions=counts["contributions"],
            model_credentials=counts["model_credentials"],
            auth_sessions=counts["auth_sessions"],
            login_blocked=True,
            deleted_at=self.repository_clock(),
        )

    def export_account(self, user: AuthenticatedPrincipal) -> AccountExport:
        """导出本人数据；不含他人资源与任何模型凭据（密文或明文）。"""

        repository = self._require_account_lifecycle_repository()
        try:
            payload = repository.export_account_data(str(user.user_id))
        except LookupError as exc:
            raise ResourceNotFound("account not found") from exc
        conversations = [
            AccountExportConversation(
                conversation_id=UUID(item["conversation_id"]),
                course_id=item["course_id"],
                title=item["title"],
                created_at=_parse_iso(item["created_at"]),
                updated_at=_parse_iso(item["updated_at"]),
                expires_at=_parse_iso(item["expires_at"]),
            )
            for item in payload["conversations"]
        ]
        runs = [
            AccountExportRun(
                workflow_run_id=UUID(item["workflow_run_id"]),
                conversation_id=UUID(item["conversation_id"]),
                workflow_type=item["workflow_type"],
                run_status=item["run_status"],
                answer_status=item["answer_status"],
                request=item["request"],
                result=item["result"],
                created_at=_parse_iso(item["created_at"]),
                expires_at=_parse_iso(item["expires_at"]),
            )
            for item in payload["runs"]
        ]
        contributions = [
            AccountExportContribution(
                contribution_id=UUID(item["contribution_id"]),
                course_id=item["course_id"],
                proposed_source_id=item["proposed_source_id"],
                title=item["title"],
                state=ContributionState(item["state"]),
                pr_url=item["pr_url"] or None,
                char_count=item["char_count"],
                content_snapshot=item["content_snapshot"],
                created_at=_parse_iso(item["created_at"]),
                expires_at=_parse_iso(item["expires_at"]),
            )
            for item in payload["contributions"]
        ]
        materials = [
            AccountExportMaterial(
                material_id=UUID(item["material_id"]),
                conversation_id=UUID(item["conversation_id"]),
                course_id=item["course_id"],
                title=item["title"],
                char_count=item["char_count"],
                created_at=_parse_iso(item["created_at"]),
                expires_at=_parse_iso(item["expires_at"]),
            )
            for item in payload["temporary_materials"]
        ]
        return AccountExport(
            schema_version="scut-senior-account-export-v1",
            github_login=payload["github_login"],
            display_name=payload["display_name"],
            account_created_at=_parse_iso(payload["account_created_at"]),
            exported_at=self.repository_clock(),
            conversations=conversations,
            runs=runs,
            contributions=contributions,
            temporary_materials=materials,
        )

    def _require_account_lifecycle_repository(self):
        repository = self.repository
        if not callable(getattr(repository, "delete_account", None)) or not callable(
            getattr(repository, "export_account_data", None)
        ):
            raise CapabilityUnavailable(
                "account_lifecycle",
                "the configured storage adapter does not support iteration-7.5 "
                "account deletion and export yet",
            )
        return repository

    def repository_clock(self) -> datetime:
        """仓储当前时间（与 TTL 计算同一时钟口径）。"""

        clock = getattr(self.repository, "_clock", None)
        if callable(clock):
            return clock()
        return utc_now()

    def run(self, user: RequestIdentity, request: WorkflowRunRequest) -> WorkflowResult:
        return self._run(user, request)

    def run_stream(
        self,
        user: RequestIdentity,
        request: WorkflowRunRequest,
        session: WorkflowStreamSession,
    ) -> WorkflowResult:
        result = self._run(user, request, stream_session=session)
        if result.run_status == RunStatus.COMPLETED:
            session.emit_answer_blocks(result.answer_blocks)
        session.emit_result(result)
        return result

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
        stream_session: WorkflowStreamSession | None = None,
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
        # Every run is bound to exactly one Agent Preset, resolved 1:1 from the
        # validated workflow_type. The immutable registry covers WorkflowType
        # exactly, so this cannot fail for a contract-valid request.
        preset = HARNESS_REGISTRY.resolve_preset(request.workflow_type)
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
                # The selected real platform model must satisfy the preset's
                # required input modalities. Structured-output metadata is
                # retained for catalog visibility, but current Workflow presets
                # accept ordinary text rather than requiring a JSON envelope.
                compatibility_reason = preset.check_model_compatibility(
                    input_modalities=model_entry.input_modalities,
                    supports_structured_outputs=model_entry.supports_structured_outputs,
                )
                if compatibility_reason is not None:
                    raise CapabilityUnavailable("model", compatibility_reason)
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
            # Apply the same input-modality compatibility check to BYOK. Its
            # structured-output metadata remains descriptive for the current
            # text-capable presets.
            compatibility_reason = preset.check_model_compatibility(
                input_modalities=selected_model.input_modalities,
                supports_structured_outputs=selected_model.supports_structured_outputs,
            )
            if compatibility_reason is not None:
                raise CapabilityUnavailable("model", compatibility_reason)

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
        if not self._course_available(course.course_id):
            raise CapabilityUnavailable(
                "course",
                f"{course.course_id} is not enabled for the configured retrieval mode",
            )

        history = _build_conversation_history(conversation)

        machine = RunStateMachine()
        machine.transition(RunStatus.RUNNING)
        trace: list[TraceEvent] = StreamingTrace(stream_session)
        # Phase two reducer is request-local and deliberately has no wire
        # contract of its own yet. It governs the existing one-shot path while
        # the action/observation stream is introduced incrementally.
        agent_budget = AgentBudget()
        agent_state = AgentState()
        agent_started = perf_counter()

        def reduce_agent(kind: str, **payload: object) -> None:
            nonlocal agent_state
            agent_state = reduce_agent_event(
                agent_state,
                {"kind": kind, **payload},
                budget=agent_budget,
            )
            append_event = getattr(self.repository, "append_agent_event", None)
            if append_event is not None:
                append_event(
                    run_id,
                    {"kind": kind, **payload},
                    agent_state.to_dict(),
                )
            if stream_session is not None and self.settings.agent_event_stream_enabled:
                stream_session.emit_agent_event(
                    kind,
                    action=payload.get("action") if isinstance(payload.get("action"), str) else None,
                    status=payload.get("status") if isinstance(payload.get("status"), str) else None,
                    reason=payload.get("reason") if isinstance(payload.get("reason"), str) else agent_state.budget_reason,
                    step_count=agent_state.step_count,
                    observation_count=agent_state.observation_count,
                )
            if agent_state.status != "running" and kind != "run_finished":
                raise ContractConflict(
                    f"agent loop budget crossed: {agent_state.budget_reason or agent_state.status}"
                )

        def record_agent_action(action: str) -> None:
            reduce_agent("action_executed", action=action)

        run_id = (
            stream_session.workflow_run_id
            if stream_session is not None
            else uuid4()
        )
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
                "agent_preset_id": preset.preset_id,
                "agent_preset_version": preset.preset_version,
            },
        )
        _append_trace(
            trace,
            node="identity",
            result={"auth_mode": "mock" if user.is_mock else "github_oauth"},
        )

        retrieval_node = (
            "local_corpus_retrieval"
            if self.settings.retrieval_mode == "local_corpus"
            else "fixture_retrieval"
        )
        corpus_version = (
            "local-corpus-unavailable"
            if self.settings.retrieval_mode == "local_corpus"
            else "fixture-corpus-v1"
        )
        course_pack_version: str | None = None
        self._persist_running_attempt(
            user=user,
            request=request,
            course_id=course.course_id,
            trace=trace,
            run_id=run_id,
            message_id=message_id,
            answer_id=answer_id,
            model_provider_id=model_provider_id,
            model_id=model_id,
            billing_label=billing_label,
            mock_only=mock_only,
            availability_status=availability_status,
            corpus_version=corpus_version,
            course_pack_version=course_pack_version,
            attempt_group_id=attempt_group_id,
            regenerated_from_run_id=regenerated_from_run_id,
        )
        _append_trace(
            trace,
            node="run_record",
            result={"stored": True, "adapter": self.settings.storage_mode},
        )

        def finish_interrupted() -> WorkflowResult | None:
            if stream_session is not None and stream_session.cancelled:
                mark_agent_terminal("interrupted")
            return self._finish_interrupted_if_requested(
                stream_session=stream_session,
                user=user,
                request=request,
                course_id=course.course_id,
                machine=machine,
                trace=trace,
                run_id=run_id,
                message_id=message_id,
                answer_id=answer_id,
                model_provider_id=model_provider_id,
                model_id=model_id,
                billing_label=billing_label,
                mock_only=mock_only,
                corpus_version=corpus_version,
                course_pack_version=course_pack_version,
                attempt_group_id=attempt_group_id,
                regenerated_from_run_id=regenerated_from_run_id,
            )

        def interrupt_if_step_not_claimed() -> WorkflowResult | None:
            if perf_counter() - agent_started > agent_budget.max_runtime_seconds:
                if agent_state.status == "running":
                    reduce_agent("budget_crossed", reason="max_runtime_seconds")
                raise ContractConflict("agent loop budget crossed: max_runtime_seconds")
            if (
                stream_session is None
                or stream_session.try_claim_step_start()
            ):
                return None
            interrupted_result = finish_interrupted()
            if interrupted_result is None:
                raise RuntimeError(
                    "workflow step admission failed without cancellation"
                )
            return interrupted_result

        def mark_agent_terminal(status: str) -> None:
            if agent_state.status == "running":
                reduce_agent("run_finished", status=status)

        def persist_failed_or_interrupted(
            *, failure_node: str, duration_ms: int
        ) -> WorkflowResult | None:
            interrupted_result = finish_interrupted()
            if interrupted_result is not None:
                return interrupted_result
            if (
                stream_session is not None
                and not stream_session.try_claim_terminal()
            ):
                interrupted_result = finish_interrupted()
                if interrupted_result is not None:
                    return interrupted_result
                raise RuntimeError(
                    "workflow failure terminal claim was already consumed"
                )
            mark_agent_terminal("failed")
            self._persist_failed_attempt(
                user=user,
                request=request,
                course_id=course.course_id,
                machine=machine,
                trace=trace,
                failure_node=failure_node,
                duration_ms=duration_ms,
                run_id=run_id,
                message_id=message_id,
                answer_id=answer_id,
                model_provider_id=model_provider_id,
                model_id=model_id,
                billing_label=billing_label,
                mock_only=mock_only,
                corpus_version=corpus_version,
                course_pack_version=course_pack_version,
                attempt_group_id=attempt_group_id,
                regenerated_from_run_id=regenerated_from_run_id,
            )
            return None

        interrupted = finish_interrupted()
        if interrupted is not None:
            return interrupted

        workflow_focus = build_workflow_focus(request)
        # Iteration 5: deterministic exam-review planning happens before
        # retrieval so the “历年题优先” path can contribute objective topic
        # terms when no syllabus narrows the scope. Any failure degrades to
        # the pre-iteration-5 behaviour without failing the run.
        exam_plan = self._plan_exam_review(request, course, trace)
        retrieval_query = (
            exam_plan.retrieval_query
            if exam_plan is not None
            else workflow_focus.authoritative_query
        )
        reduce_agent(
            "decision_produced", action=self.agent_decision.decide(
                request, agent_state, "retrieve", history=history
            )
        )
        interrupted = interrupt_if_step_not_claimed()
        if interrupted is not None:
            return interrupted
        started = perf_counter()
        try:
            retrieval_batch = self.retrieval.search(
                [course.course_id], retrieval_query
            )
            if (
                isinstance(retrieval_batch, RetrievalBatch)
                and not retrieval_batch.sources
                and history
                and exam_plan is None
                and self.settings.retrieval_mode == "local_corpus"
            ):
                # 迭代 7.5 检索地板的配套修复：追问轮常丢失词面锚点
                #（“把这道题再讲一遍”单独检索得分为噪声级），当前查询空结果时
                # 以最近用户轮次补锚重试一次；不改变课程/范围/工作流语义。
                context_query = _compose_context_carry_query(
                    retrieval_query, history
                )
                if context_query:
                    retry_started = perf_counter()
                    context_batch = self.retrieval.search(
                        [course.course_id], context_query
                    )
                    if isinstance(context_batch, RetrievalBatch) and (
                        context_batch.sources
                    ):
                        reduce_agent(
                            "decision_produced",
                            action=self.agent_decision.decide(
                                request,
                                agent_state,
                                "retrieve_with_query_rewrite",
                                sources=retrieval_batch.sources,
                                history=history,
                            ),
                        )
                        record_agent_action("retrieve_with_query_rewrite")
                        retrieval_batch = context_batch
                        _append_trace(
                            trace,
                            node="retrieval_context_carry",
                            result={
                                "hit_count": 0,
                                "candidate_count": len(retrieval_batch.sources),
                                "rewritten_query": context_query[:200],
                            },
                            duration_ms=_elapsed_ms(retry_started),
                        )
            if not isinstance(retrieval_batch, RetrievalBatch):
                # Keep injected iteration-1 test doubles compatible, but never
                # accept an unversioned result in explicit local-corpus mode.
                if self.settings.retrieval_mode == "local_corpus":
                    raise ContractConflict(
                        "local corpus retrieval returned an unversioned candidate set"
                    )
                sources = list(retrieval_batch)
            else:
                sources = list(retrieval_batch.sources)
                corpus_version = retrieval_batch.corpus_version
                course_pack_version = retrieval_batch.course_pack_version
                if (
                    not isinstance(corpus_version, str)
                    or not corpus_version.strip()
                    or (
                        course_pack_version is not None
                        and (
                            not isinstance(course_pack_version, str)
                            or not course_pack_version.strip()
                        )
                    )
                ):
                    raise ContractConflict(
                        "retrieval returned an invalid corpus version binding"
                    )
                if (
                    self.settings.retrieval_mode == "local_corpus"
                    and course_pack_version is None
                ):
                    raise ContractConflict(
                        "local corpus retrieval returned no course pack version"
                    )
            invalid_source_ids = [
                source.chunk_id
                for source in sources
                if source.course_id != course.course_id
            ]
            if invalid_source_ids:
                raise ContractConflict(
                    "source authorization guard rejected a source outside the conversation course"
                )
            sources = _dedupe_sources(sources)
            record_agent_action("retrieve")
        except Exception:
            interrupted = persist_failed_or_interrupted(
                failure_node=retrieval_node,
                duration_ms=_elapsed_ms(started),
            )
            if interrupted is not None:
                return interrupted
            raise
        _append_trace(
            trace,
            node=retrieval_node,
            duration_ms=_elapsed_ms(started),
            result={
                **(
                    {"mode": "synthetic_fixture_only"}
                    if self.settings.retrieval_mode == "fixture"
                    else {}
                ),
                "hit_count": len(sources),
                "candidate_order": [
                    f"S{index}" for index in range(1, len(sources) + 1)
                ],
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
        reduce_agent("observation_recorded")
        _append_trace(
            trace,
            node="source_authorization_guard",
            result={
                "candidate_count": len(sources),
                "accepted_count": len(sources),
            },
        )
        _append_trace(
            trace,
            node="cache_policy",
            status=TraceEventStatus.SKIPPED,
            result={
                "cache_hit": False,
                "reason_code": "runtime_cache_not_configured",
            },
        )

        interrupted = finish_interrupted()
        if interrupted is not None:
            return interrupted

        started = perf_counter()
        api_key: str | None = None
        retry_count = 0
        model_node = (
            "byok_model"
            if use_user_key
            else "mock_model"
            if mock_only
            else "zhipu_model" if model_provider_id == "zhipu" else "openrouter_model"
        )

        try:
            if use_user_key:
                assert isinstance(user, AuthenticatedPrincipal)
                interrupted = interrupt_if_step_not_claimed()
                if interrupted is not None:
                    return interrupted
                api_key = self.credential_manager.load_api_key(
                    user, request.provider_id
                )
            while True:
                # Admission and cancellation share a short lifecycle lock. A
                # claim that wins is considered in flight; cancel never waits
                # for the synchronous provider call and wins at the next node.
                reduce_agent(
                    "decision_produced",
                    action=self.agent_decision.decide(
                        request,
                        agent_state,
                        "generate",
                        sources=retrieval_batch.sources,
                        history=history,
                    ),
                )
                interrupted = interrupt_if_step_not_claimed()
                if interrupted is not None:
                    return interrupted
                try:
                    if use_user_key:
                        assert api_key is not None
                        # 迭代 7.5：断开/取消时尽力中止上游等待（cancel_check
                        # 由可取消 transport 周期检查；结果被弃置不落库）。
                        cancel_check = (
                            stream_session.cancelled
                            if stream_session is not None
                            else None
                        )
                        generated = self.byok_model.generate(
                            api_key=api_key,
                            request=request,
                            sources=sources,
                            history=history,
                            cancel_check=cancel_check,
                        )
                    else:
                        platform_model = (
                            self.zhipu_model
                            if model_provider_id == "zhipu"
                            and self.zhipu_model is not None
                            else self.model
                        )
                        generated = platform_model.generate(
                            request,
                            sources,
                            history=history,
                            cancel_check=(
                                stream_session.cancelled
                                if stream_session is not None
                                else None
                            ),
                        )
                except Exception as model_error:
                    interrupted = finish_interrupted()
                    if interrupted is not None:
                        return interrupted
                    if (
                        retry_count >= 1
                        or not _is_retryable_model_output_error(model_error)
                    ):
                        raise
                    retry_count += 1
                    _append_trace(
                        trace,
                        node="model_output_retry",
                        result={
                            "retry_count": retry_count,
                            "failure_code": "model_output_retryable_failure",
                        },
                    )
                    interrupted = finish_interrupted()
                    if interrupted is not None:
                        return interrupted
                    continue
                interrupted = finish_interrupted()
                if interrupted is not None:
                    return interrupted
                try:
                    guarded = build_guarded_answer(
                        request=request,
                        answer=generated,
                        sources=sources,
                        course_ids={course.course_id},
                    )
                except RuntimeGuardError:
                    interrupted = finish_interrupted()
                    if interrupted is not None:
                        return interrupted
                    if not sources:
                        # Zero candidates make every citation impossible, so a
                        # guard rejection (hallucinated [S#], out-of-scope block,
                        # or URL) cannot be repaired by regenerating. Degrade to
                        # an honest insufficient-evidence result instead of
                        # failing the run after a long model call.
                        guarded = _empty_candidate_insufficient_evidence()
                        break
                    if retry_count >= 1:
                        interrupted = persist_failed_or_interrupted(
                            failure_node="citation_guard",
                            duration_ms=_elapsed_ms(started),
                        )
                        if interrupted is not None:
                            return interrupted
                        raise
                    reduce_agent("guard_retry_recorded")
                    retry_count += 1
                    _append_trace(
                        trace,
                        node="model_output_retry",
                        result={
                            "retry_count": retry_count,
                            "failure_code": "model_output_guard_rejected",
                        },
                    )
                    interrupted = finish_interrupted()
                    if interrupted is not None:
                        return interrupted
                    continue
                break
        except AuthRequired:
            self.repository.discard_nonterminal_run(str(user.user_id), run_id)
            raise
        except RuntimeGuardError:
            raise
        except Exception:
            interrupted = persist_failed_or_interrupted(
                failure_node=model_node,
                duration_ms=_elapsed_ms(started),
            )
            if interrupted is not None:
                return interrupted
            raise
        finally:
            api_key = None
        _append_trace(
            trace,
            node=model_node,
            duration_ms=_elapsed_ms(started),
            result={
                "model_source": request.model_source.value,
                "provider_id": model_provider_id,
                "model_id": model_id,
                "billing_label": billing_label,
                "availability_status": availability_status,
                "real_model_called": not mock_only,
                "retry_count": retry_count,
            },
        )

        citation_source_map = {
            f"S{index}": source
            for index, source in enumerate(sources, start=1)
        }
        citations = [
            Citation(
                citation_id=citation_id,
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
            for citation_id in guarded.citation_ids
            for source in (citation_source_map[citation_id],)
        ]

        _append_trace(
            trace,
            node="citation_guard",
            result={
                "candidate_count": len(sources),
                "accepted_count": len(citations),
                "evidence_status": guarded.evidence_status.value,
                "external_resources_separate": True,
            },
        )

        related_topics = normalize_topics(generated.related_topics)
        related_questions = normalize_topics(generated.related_questions)
        _append_trace(
            trace,
            node="knowledge_point_normalization",
            result={
                "reason_code": workflow_focus.focus_strategy.value,
                "candidate_count": len(generated.related_topics),
                "accepted_count": len(related_topics),
            },
        )
        protected_terms = normalize_topics(
            (
                *related_topics,
                course.display_name,
                *(source.source_title for source in sources),
                *(
                    heading
                    for source in sources
                    for heading in source.heading_path
                ),
            ),
            max_items=32,
        )
        original_blocks = [block.model_copy(deep=True) for block in guarded.blocks]
        if self.humanizer is None:
            interrupted = finish_interrupted()
            if interrupted is not None:
                return interrupted
            answer_blocks = original_blocks
            _append_trace(
                trace,
                node="response_style_control",
                result={"reason_code": "single_pass_model_prompt"},
            )
        else:
            interrupted = interrupt_if_step_not_claimed()
            if interrupted is not None:
                return interrupted
            try:
                candidate_blocks = self.humanizer.humanize(
                    blocks=[block.model_copy(deep=True) for block in original_blocks],
                    protected_terms=protected_terms,
                )
                humanizer_outcome = protect_humanizer_output(
                    original=original_blocks,
                    candidate=list(candidate_blocks),
                    protected_terms=protected_terms,
                )
            except Exception:
                answer_blocks = original_blocks
                _append_trace(
                    trace,
                    node="humanizer",
                    status=TraceEventStatus.FAILED,
                    result={"degradation_code": "humanizer_gateway_fallback"},
                )
            else:
                answer_blocks = list(humanizer_outcome.blocks)
                _append_trace(
                    trace,
                    node="humanizer",
                    result={
                        "reason_code": (
                            "humanizer_applied"
                            if humanizer_outcome.applied
                            else (
                                "humanizer_protected_fallback"
                                if humanizer_outcome.fallback
                                else "humanizer_no_change"
                            )
                        ),
                        **(
                            {
                                "degradation_code": (
                                    "humanizer_"
                                    + (humanizer_outcome.reason or "fallback")
                                )
                            }
                            if humanizer_outcome.fallback
                            else {}
                        ),
                    },
                )

        answer_blocks = _enforce_primary_answer_tone(answer_blocks, request)

        # Iteration 5: append the deterministic, system-generated exam-review
        # appendix (scope statement, objective past-exam statistics, knowledge
        # point groups, uncovered syllabus items) after the humanizer so the
        # protected deterministic content is never rewritten.
        if exam_plan is not None:
            answer_blocks = _inject_exam_review_appendix(
                answer_blocks, render_exam_review_appendix(exam_plan.plan)
            )

        interrupted = finish_interrupted()
        if interrupted is not None:
            return interrupted

        if (
            request.include_bilibili_resources
            and request.knowledge_scope != KnowledgeScope.COURSE_ONLY
            and self.settings.bilibili_resources_enabled
        ):
            (
                focused_keywords,
                keyword_source,
                keyword_candidate_count,
            ) = _select_bilibili_keywords(
                generated=generated,
                related_topics=related_topics,
                authoritative_query=retrieval_query,
                request_input=request.user_input,
                course_title=course.display_name,
                course_id=course.course_id,
            )
            if focused_keywords:
                interrupted = interrupt_if_step_not_claimed()
                if interrupted is not None:
                    return interrupted
                started = perf_counter()
                try:
                    discovered_resources = self.resources.discover(
                        course_id=course.course_id,
                        course_title=course.display_name,
                        keywords=tuple(focused_keywords),
                    )
                    if len(discovered_resources) != 1:
                        raise ValueError(
                            "Bilibili discovery must return exactly one search entry"
                        )
                    external_resources = [
                        ExternalResource.model_validate(resource)
                        for resource in discovered_resources
                    ]
                    if any(
                        resource.course_id != course.course_id
                        for resource in external_resources
                    ):
                        raise ValueError(
                            "Bilibili discovery returned a cross-course entry"
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
                    _append_trace(
                        trace,
                        node="bilibili_link_discovery",
                        duration_ms=_elapsed_ms(started),
                        result={
                            "reason_code": keyword_source,
                            "hit_count": len(external_resources),
                            "candidate_count": keyword_candidate_count,
                            "accepted_count": len(focused_keywords),
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

        interrupted = finish_interrupted()
        if interrupted is not None:
            return interrupted
        if (
            stream_session is not None
            and not stream_session.try_claim_terminal()
        ):
            interrupted = finish_interrupted()
            if interrupted is not None:
                return interrupted
            raise RuntimeError(
                "workflow completion terminal claim was already consumed"
            )

        mark_agent_terminal("finished")
        machine.transition(RunStatus.COMPLETED)
        repository_answer = _answer_block_content(
            answer_blocks, AnswerBlockType.REPOSITORY
        )
        general_supplement = _answer_block_content(
            answer_blocks, AnswerBlockType.GENERAL
        )
        persistence_event = _append_pending_persistence_trace(
            trace, adapter=self.settings.storage_mode
        )
        result = WorkflowResult(
            workflow_run_id=run_id,
            conversation_id=request.conversation_id,
            message_id=message_id,
            answer_id=answer_id,
            run_status=machine.status,
            answer_status=guarded.answer_status,
            workflow_type=request.workflow_type,
            course_scope=request.course_scope,
            course_ids=[course.course_id],
            repository_answer=repository_answer,
            general_supplement=general_supplement,
            answer_blocks=answer_blocks,
            workflow_output={
                "runtime_version": "workflow-runtime-v1",
                "payload_type": request.workflow_type.value,
                "source_candidate_ids": list(citation_source_map),
                "selected_citation_ids": list(guarded.citation_ids),
                **(
                    {"exam_review": exam_plan.plan.to_output_dict()}
                    if exam_plan is not None
                    else {}
                ),
            },
            evidence_status=guarded.evidence_status,
            citations=citations,
            related_topics=list(related_topics),
            related_questions=list(related_questions),
            external_resources=external_resources,
            coverage_gaps=list(guarded.coverage_gaps),
            trace=trace,
            corpus_version=corpus_version,
            course_pack_version=course_pack_version,
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

        self._save_run_state(
            user=user,
            request=request,
            result=result,
            attempt_group_id=attempt_group_id,
            regenerated_from_run_id=regenerated_from_run_id,
        )
        _emit_confirmed_persistence_trace(trace, persistence_event)
        return result

    def _plan_exam_review(
        self,
        request: WorkflowRunRequest,
        course: object,
        trace: "StreamingTrace | list[TraceEvent]",
    ) -> "ExamReviewPlanContext | None":
        """Build the deterministic exam-review plan, degrading honestly.

        Returns ``None`` (legacy behaviour, no plan node) for every non
        exam_review workflow, when the feature flag is off, or when no facts
        provider is configured. Provider failures emit a skipped Trace event
        and never fail the run.
        """

        if (
            request.workflow_type is not WorkflowType.EXAM_REVIEW
            or not self.settings.exam_review_plan_enabled
            or self.exam_facts is None
        ):
            return None
        typed = request.workflow_payload
        if not isinstance(typed, ExamReviewPayload):  # pragma: no cover - guarded by contract
            return None
        load = getattr(self.exam_facts, "load", None)
        if not callable(load):
            return None
        started = perf_counter()
        try:
            facts = load(course.course_id)
            plan = build_exam_review_plan(
                course_id=course.course_id,
                payload_syllabus=typed.syllabus,
                payload_weak_topics=typed.weak_topics,
                payload_available_hours=typed.available_hours,
                knowledge_scope_allows_general=(
                    request.knowledge_scope != KnowledgeScope.COURSE_ONLY
                ),
                facts=facts,
                # 外层 user_input 是本次复习提问：参与知识点排序与检索聚焦，
                # 但不进入 Trace 或课程包。
                payload_review_question=request.user_input,
            )
        except Exception:
            _append_trace(
                trace,
                node="exam_review_plan",
                status=TraceEventStatus.SKIPPED,
                duration_ms=_elapsed_ms(started),
                result={
                    "degradation_code": "exam_review_facts_unavailable",
                },
            )
            return None
        _append_trace(
            trace,
            node="exam_review_plan",
            duration_ms=_elapsed_ms(started),
            result={
                # Trace stays free of private syllabus/weak-topic content:
                # only the path code and objective corpus counts are safe.
                "review_path": plan.path.value,
                "reason_code": plan.path.value,
                "candidate_count": int(
                    plan.past_exam_stats.get("question_count", 0)
                ),
                "sample_years": list(plan.past_exam_stats.get("sample_years") or []),
            },
        )
        retrieval_query = compose_retrieval_query(
            syllabus=typed.syllabus,
            weak_topics=typed.weak_topics,
            plan=plan,
            review_question=request.user_input,
        )
        return ExamReviewPlanContext(plan=plan, retrieval_query=retrieval_query)

    def _persist_running_attempt(
        self,
        *,
        user: RequestIdentity,
        request: WorkflowRunRequest,
        course_id: str,
        trace: list[TraceEvent],
        run_id: UUID,
        message_id: UUID,
        answer_id: UUID,
        model_provider_id: str,
        model_id: str,
        billing_label: str,
        mock_only: bool,
        availability_status: str,
        corpus_version: str,
        course_pack_version: str | None,
        attempt_group_id: UUID | None,
        regenerated_from_run_id: UUID | None,
    ) -> None:
        """Create the observable run before retrieval or model execution begins."""

        result = WorkflowResult(
            workflow_run_id=run_id,
            conversation_id=request.conversation_id,
            message_id=message_id,
            answer_id=answer_id,
            run_status=RunStatus.RUNNING,
            answer_status=AnswerStatus.PARTIAL,
            workflow_type=request.workflow_type,
            course_scope=request.course_scope,
            course_ids=[course_id],
            repository_answer=None,
            general_supplement=None,
            answer_blocks=[],
            workflow_output={
                "runtime_version": "workflow-runtime-v1",
                "payload_type": request.workflow_type.value,
                "execution_state": "running",
            },
            evidence_status=EvidenceStatus.NOT_EVALUATED,
            citations=[],
            related_topics=[],
            related_questions=[],
            external_resources=[],
            coverage_gaps=["本次运行仍在进行中。"],
            trace=list(trace),
            corpus_version=corpus_version,
            course_pack_version=course_pack_version,
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
        self._save_run_state(
            user=user,
            request=request,
            result=result,
            attempt_group_id=attempt_group_id,
            regenerated_from_run_id=regenerated_from_run_id,
        )

    def _save_run_state(
        self,
        *,
        user: RequestIdentity,
        request: WorkflowRunRequest,
        result: WorkflowResult,
        attempt_group_id: UUID | None,
        regenerated_from_run_id: UUID | None,
    ) -> None:
        try:
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
        except AuthRequired:
            self.repository.discard_nonterminal_run(
                str(user.user_id), result.workflow_run_id
            )
            raise

    def _finish_interrupted_if_requested(
        self,
        *,
        stream_session: WorkflowStreamSession | None,
        user: RequestIdentity,
        request: WorkflowRunRequest,
        course_id: str,
        machine: RunStateMachine,
        trace: list[TraceEvent],
        run_id: UUID,
        message_id: UUID,
        answer_id: UUID,
        model_provider_id: str,
        model_id: str,
        billing_label: str,
        mock_only: bool,
        corpus_version: str,
        course_pack_version: str | None,
        attempt_group_id: UUID | None,
        regenerated_from_run_id: UUID | None,
    ) -> WorkflowResult | None:
        if stream_session is None or not stream_session.cancelled:
            return None
        return self._persist_interrupted_attempt(
            user=user,
            request=request,
            course_id=course_id,
            machine=machine,
            trace=trace,
            run_id=run_id,
            message_id=message_id,
            answer_id=answer_id,
            model_provider_id=model_provider_id,
            model_id=model_id,
            billing_label=billing_label,
            mock_only=mock_only,
            corpus_version=corpus_version,
            course_pack_version=course_pack_version,
            attempt_group_id=attempt_group_id,
            regenerated_from_run_id=regenerated_from_run_id,
        )

    def _persist_interrupted_attempt(
        self,
        *,
        user: RequestIdentity,
        request: WorkflowRunRequest,
        course_id: str,
        machine: RunStateMachine,
        trace: list[TraceEvent],
        run_id: UUID,
        message_id: UUID,
        answer_id: UUID,
        model_provider_id: str,
        model_id: str,
        billing_label: str,
        mock_only: bool,
        corpus_version: str,
        course_pack_version: str | None,
        attempt_group_id: UUID | None,
        regenerated_from_run_id: UUID | None,
    ) -> WorkflowResult:
        machine.transition(RunStatus.INTERRUPTED)
        _append_trace(
            trace,
            node="workflow_interrupted",
            status=TraceEventStatus.FAILED,
            result={"failure_code": "client_interrupted"},
        )
        persistence_event = _append_pending_persistence_trace(
            trace, adapter=self.settings.storage_mode
        )
        result = WorkflowResult(
            workflow_run_id=run_id,
            conversation_id=request.conversation_id,
            message_id=message_id,
            answer_id=answer_id,
            run_status=machine.status,
            answer_status=AnswerStatus.PARTIAL,
            workflow_type=request.workflow_type,
            course_scope=request.course_scope,
            course_ids=[course_id],
            repository_answer=None,
            general_supplement=None,
            answer_blocks=[],
            workflow_output={
                "runtime_version": "workflow-runtime-v1",
                "payload_type": request.workflow_type.value,
                "failure_code": "client_interrupted",
            },
            evidence_status=EvidenceStatus.NOT_EVALUATED,
            citations=[],
            related_topics=[],
            related_questions=[],
            external_resources=[],
            coverage_gaps=["本次运行已中断，未生成完整回答。"],
            trace=trace,
            corpus_version=corpus_version,
            course_pack_version=course_pack_version,
            workflow_version="workflow-contract-v1",
            model_source=request.model_source,
            model=ModelMetadata(
                provider_id=model_provider_id,
                model_id=model_id,
                billing_label=billing_label,
                mock_only=mock_only,
            ),
            availability_status="interrupted",
        )
        self._save_run_state(
            user=user,
            request=request,
            result=result,
            attempt_group_id=attempt_group_id,
            regenerated_from_run_id=regenerated_from_run_id,
        )
        _emit_confirmed_persistence_trace(trace, persistence_event)
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
        corpus_version: str,
        course_pack_version: str | None,
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
        persistence_event = _append_pending_persistence_trace(
            trace, adapter=self.settings.storage_mode
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
                "runtime_version": "workflow-runtime-v1",
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
            corpus_version=corpus_version,
            course_pack_version=course_pack_version,
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
        self._save_run_state(
            user=user,
            request=request,
            result=result,
            attempt_group_id=attempt_group_id,
            regenerated_from_run_id=regenerated_from_run_id,
        )
        _emit_confirmed_persistence_trace(trace, persistence_event)


def _select_bilibili_keywords(
    *,
    generated: GeneratedAnswer,
    related_topics: tuple[str, ...],
    authoritative_query: str,
    request_input: str,
    course_title: str,
    course_id: str,
) -> tuple[tuple[str, ...], str, int]:
    """Choose one safe, course-scoped search query with explicit fallbacks.

    The provider may return ordinary Markdown, in which case it has no
    machine-readable topic fields.  When it does return them, an explicit
    Bilibili query takes precedence and the model's normalized core topics are
    the next-best representation of what it just answered.  The typed current
    question is a reliable last semantic fallback, followed by request/course
    identity values solely to keep the selected live-search option non-empty.
    """

    candidates = (
        (
            "model_bilibili_search_keywords",
            len(generated.bilibili_search_keywords),
            normalize_keywords(generated.bilibili_search_keywords),
        ),
        (
            "model_related_topics",
            len(related_topics),
            normalize_keywords(related_topics),
        ),
        (
            "current_question_keyword_combination",
            1,
            derive_question_keywords(authoritative_query),
        ),
        (
            "request_input_fallback",
            1,
            normalize_keywords((request_input,)),
        ),
        (
            "course_title_fallback",
            1,
            normalize_keywords((course_title,)),
        ),
        (
            "course_id_fallback",
            1,
            normalize_keywords((course_id,)),
        ),
    )
    for source, candidate_count, keywords in candidates:
        if keywords:
            # Bilibili is an external, unreviewed search surface. Keep the
            # course title and the model's focused terms together so a generic
            # topic does not lose the selected course context.
            scoped_keywords = normalize_keywords(
                (course_title, *keywords, *normalize_keywords(related_topics))
            )
            return scoped_keywords, source, candidate_count
    return (), "no_focused_topic", 0


def _append_trace(
    trace: list[TraceEvent],
    *,
    node: str,
    result: TraceSafeResult | dict[str, object],
    status: TraceEventStatus = TraceEventStatus.COMPLETED,
    duration_ms: int = 0,
) -> TraceEvent:
    event = TraceEvent(
        event_id=str(uuid4()),
        sequence=len(trace),
        node=node,
        status=status,
        duration_ms=max(duration_ms, 0),
        result=result,
    )
    trace.append(event)
    return event


def _elapsed_ms(started: float) -> int:
    return max(int((perf_counter() - started) * 1000), 0)


def _append_pending_persistence_trace(
    trace: list[TraceEvent], *, adapter: str
) -> TraceEvent:
    event = TraceEvent(
        event_id=str(uuid4()),
        sequence=len(trace),
        node="persistence",
        status=TraceEventStatus.COMPLETED,
        duration_ms=0,
        result={"stored": True, "adapter": adapter},
    )
    if isinstance(trace, StreamingTrace):
        trace.append_without_emit(event)
    else:
        trace.append(event)
    return event


def _emit_confirmed_persistence_trace(
    trace: list[TraceEvent], event: TraceEvent
) -> None:
    if isinstance(trace, StreamingTrace):
        trace.emit_appended(event)


def _dedupe_sources(sources: list[RetrievedSource]) -> list[RetrievedSource]:
    """Keep the first occurrence of each chunk in the evidence ledger."""
    seen: set[str] = set()
    unique: list[RetrievedSource] = []
    for source in sources:
        chunk_id = getattr(source, "chunk_id", None)
        if not isinstance(chunk_id, str) or not chunk_id:
            unique.append(source)
            continue
        if chunk_id in seen:
            continue
        seen.add(chunk_id)
        unique.append(source)
    return unique


def _answer_block_content(
    blocks: list[AnswerBlock], block_type: AnswerBlockType
) -> str | None:
    for block in blocks:
        if block.type == block_type:
            return block.content
    return None


def _enforce_primary_answer_tone(
    blocks: list[AnswerBlock], request: WorkflowRunRequest
) -> list[AnswerBlock]:
    """Apply the visible tone contract once to the first student-facing block."""

    for index, block in enumerate(blocks):
        if not block.content.strip():
            continue
        normalized = block.model_copy(
            update={
                "content": enforce_tone_visible_callout(
                    block.content,
                    request.tone,
                )
            }
        )
        return [*blocks[:index], normalized, *blocks[index + 1 :]]
    return blocks


def _inject_exam_review_appendix(
    blocks: list[AnswerBlock], appendix: str
) -> list[AnswerBlock]:
    """Append the deterministic exam-review appendix to the repository block.

    The appendix is system-generated corpus statistics; it is never sent
    through the model, the humanizer or the citation guard. Runs without a
    repository block (for example honest insufficient-evidence results) keep
    their answer untouched.
    """

    if not appendix.strip():
        return blocks
    for index, block in enumerate(blocks):
        if block.type != AnswerBlockType.REPOSITORY or not block.content.strip():
            continue
        updated = block.model_copy(update={"content": f"{block.content}\n\n{appendix}"})
        return [*blocks[:index], updated, *blocks[index + 1 :]]
    return blocks


def _empty_candidate_insufficient_evidence() -> GuardedAnswer:
    """Deterministic result when retrieval found no candidates at all.

    Zero sources make every citation impossible, so a guard rejection cannot
    be repaired by regenerating. Return an honest ``insufficient_evidence``
    result instead of failing the run after a long model call.
    """

    return GuardedAnswer(
        blocks=(),
        citation_ids=(),
        evidence_status=EvidenceStatus.INSUFFICIENT,
        answer_status=AnswerStatus.INSUFFICIENT_EVIDENCE,
        coverage_gaps=(
            "本次课程资料候选不足，未找到与问题匹配的可引用资料；已停止补充通用知识。",
        ),
    )


def _is_retryable_model_output_error(error: Exception) -> bool:
    return isinstance(error, TimeoutError) or getattr(error, "code", None) in {
        "platform_model_invalid_response",
        "platform_model_timeout",
        "byok_provider_invalid_response",
        "byok_provider_timeout",
    }


_MAX_HISTORY_TURNS = 6
_MAX_HISTORY_TURN_CHARS = 2_000
_CONTEXT_CARRY_QUERY_CHARS = 1_200
_CONTEXT_CARRY_USER_TURNS = 2


def _compose_context_carry_query(
    current_query: str,
    history: tuple[ConversationTurn, ...],
) -> str:
    """Prepend the most recent user turns so follow-up queries regain anchors.

    Bounded and deterministic: only completed prior user turns (latest two)
    are prepended to the current retrieval query. The combined text is used
    for lexical matching only — it never changes course, scope or workflow.
    """

    prior = [
        turn.content[:400]
        for turn in reversed(history)
        if turn.role == "user" and turn.content.strip()
    ][-_CONTEXT_CARRY_USER_TURNS:]
    if not prior:
        return ""
    combined = " ".join([*reversed(prior), current_query])
    return combined[:_CONTEXT_CARRY_QUERY_CHARS].strip()
FEEDBACK_TTL = timedelta(days=30)


def _build_conversation_history(
    conversation: ConversationDetail,
) -> tuple[ConversationTurn, ...]:
    """Derive bounded multi-turn context from completed prior attempts.

    Only completed attempts become context; the current run is never part of
    its own history. History is server-derived context, not an instruction
    source, and it never changes the current request's course, workflow or
    knowledge scope.
    """

    turns: list[ConversationTurn] = []
    for attempt in conversation.runs:
        if attempt.result.run_status != RunStatus.COMPLETED:
            continue
        user_question = build_workflow_focus(attempt.request).authoritative_query
        assistant_answer = _completed_answer_text(attempt.result)
        if user_question:
            turns.append(
                ConversationTurn(
                    role="user", content=user_question[:_MAX_HISTORY_TURN_CHARS]
                )
            )
        if assistant_answer:
            turns.append(
                ConversationTurn(
                    role="assistant",
                    content=assistant_answer[:_MAX_HISTORY_TURN_CHARS],
                )
            )
        if len(turns) >= _MAX_HISTORY_TURNS * 2:
            break
    return tuple(turns[-(_MAX_HISTORY_TURNS * 2) :])


def _completed_answer_text(result: WorkflowResult) -> str:
    if result.repository_answer:
        return result.repository_answer
    return " ".join(
        block.content for block in result.answer_blocks if block.content
    ).strip()
