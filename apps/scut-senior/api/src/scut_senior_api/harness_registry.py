from __future__ import annotations

from collections.abc import Collection, Iterable
from dataclasses import dataclass
from enum import StrEnum

from .contracts import WorkflowType
from .workflow_focus import FocusStrategy


HARNESS_REGISTRY_VERSION = "harness-registry-v1"
"""Stable version of the controlled plugin metadata surfaced by this module.

The registry is intentionally immutable: presets, tool metadata and skill
metadata are frozen at import time and validated at construction, so the
runtime can never silently drift from the five WorkflowType values.
"""

PRESET_VERSION = "v1"
"""Version shared by the five initially shipped Agent Presets."""

KNOWN_INPUT_MODALITIES = frozenset({"text", "image", "video"})
"""Modality vocabulary shared with the platform model catalog."""


class ControlledTool(StrEnum):
    COURSE_RETRIEVAL = "course_retrieval"
    EVIDENCE_LOCATION = "evidence_location"
    BILIBILI_ANONYMOUS_SEARCH = "bilibili_anonymous_search"
    TEMPORARY_MATERIAL_READ = "temporary_material_read"


class MaterialConversionSkillStatus(StrEnum):
    CONTRACT_ONLY = "contract_only"


class CourseState(StrEnum):
    """Honest runtime state of one registered course plugin.

    ``active`` means the current RetrievalGateway can actually serve the course
    right now. ``fixture_only`` means only the synthetic fixture corpus covers
    it (usable in fixture mode, never claimed as an active course). ``registered``
    means it is a contract-registered course with neither active nor fixture
    coverage.
    """

    ACTIVE = "active"
    FIXTURE_ONLY = "fixture_only"
    REGISTERED = "registered"


@dataclass(frozen=True, slots=True)
class ControlledToolMetadata:
    tool_id: ControlledTool
    display_name: str
    description: str
    # Current adapters orchestrate tools server-side (retrieval, evidence
    # guards, Bilibili search-link building, temporary material context); the
    # model is never granted direct tool calls, so every tool is non-callable.
    model_callable: bool = False

    def as_public_dict(self) -> dict[str, object]:
        return {
            "tool_id": self.tool_id.value,
            "display_name": self.display_name,
            "description": self.description,
            "model_callable": self.model_callable,
        }


@dataclass(frozen=True, slots=True)
class MaintainerSkillMetadata:
    skill_id: str
    display_name: str
    version: str
    description: str
    status: MaterialConversionSkillStatus = MaterialConversionSkillStatus.CONTRACT_ONLY
    human_review_required: bool = True
    # The offline conversion pipeline defines and validates the contract; it
    # cannot itself decide that content is passed or activate a course.
    can_mark_passed_or_active: bool = False

    def as_public_dict(self) -> dict[str, object]:
        return {
            "skill_id": self.skill_id,
            "display_name": self.display_name,
            "version": self.version,
            "description": self.description,
            "status": self.status.value,
            "human_review_required": self.human_review_required,
            "can_mark_passed_or_active": self.can_mark_passed_or_active,
        }


@dataclass(frozen=True, slots=True)
class AgentPreset:
    """Immutable metadata for one Agent Preset mapped 1:1 to a WorkflowType.

    Deliberately contains no prompt text, directives or anchors: presets
    describe capabilities and routing, never student-visible or model-facing
    instructions.
    """

    preset_id: str
    preset_version: str
    display_name: str
    workflow_type: WorkflowType
    focus_strategy: FocusStrategy
    allowed_tools: tuple[ControlledTool, ...]
    required_input_modalities: tuple[str, ...]
    requires_structured_outputs: bool

    def check_model_compatibility(
        self,
        *,
        input_modalities: Collection[str],
        supports_structured_outputs: bool,
    ) -> str | None:
        """Return a clear reason when a model cannot serve this preset.

        Returns ``None`` when the model satisfies every required modality and
        the structured-output requirement. Fail-closed callers raise a
        capability error on any non-None result.
        """
        available = set(input_modalities)
        missing = tuple(
            modality
            for modality in self.required_input_modalities
            if modality not in available
        )
        if missing:
            return (
                f"preset {self.preset_id} requires input modalities "
                f"{', '.join(missing)} not supported by the selected model"
            )
        if self.requires_structured_outputs and not supports_structured_outputs:
            return (
                f"preset {self.preset_id} requires structured outputs but the "
                "selected model does not support them"
            )
        return None

    def as_public_dict(self) -> dict[str, object]:
        return {
            "preset_id": self.preset_id,
            "preset_version": self.preset_version,
            "display_name": self.display_name,
            "workflow_type": self.workflow_type.value,
            "focus_strategy": self.focus_strategy.value,
            "allowed_tools": [tool.value for tool in self.allowed_tools],
            "required_input_modalities": list(self.required_input_modalities),
            "requires_structured_outputs": self.requires_structured_outputs,
        }


class HarnessRegistry:
    """Immutable registry validating exact WorkflowType coverage at creation.

    Construction fails closed unless the presets cover WorkflowType exactly
    (no missing, no duplicate), every referenced tool exists in the tool
    catalog, and every required modality is a known modality.
    """

    def __init__(
        self,
        *,
        version: str,
        presets: Iterable[AgentPreset],
        tools: Iterable[ControlledToolMetadata],
        skills: Iterable[MaintainerSkillMetadata],
    ):
        if not version or not version.strip():
            raise ValueError("harness registry requires a non-empty version")
        self.version = version
        self.presets = tuple(presets)
        self.tools = tuple(tools)
        self.skills = tuple(skills)
        self._validate()

    def _validate(self) -> None:
        tool_ids = {tool.tool_id for tool in self.tools}
        if len(tool_ids) != len(self.tools):
            raise ValueError("harness registry tool catalog contains duplicate ids")
        preset_ids = {preset.preset_id for preset in self.presets}
        if len(preset_ids) != len(self.presets):
            raise ValueError("harness registry contains duplicate preset ids")
        workflow_types = [preset.workflow_type for preset in self.presets]
        if len(set(workflow_types)) != len(workflow_types):
            duplicates = sorted(
                type_.value
                for type_ in set(workflow_types)
                if workflow_types.count(type_) > 1
            )
            raise ValueError(
                "agent presets must map each workflow_type to exactly one preset: "
                + ", ".join(duplicates)
            )
        if set(workflow_types) != set(WorkflowType):
            missing = sorted(
                type_.value for type_ in set(WorkflowType) - set(workflow_types)
            )
            extra = sorted(
                type_.value for type_ in set(workflow_types) - set(WorkflowType)
            )
            raise ValueError(
                "agent presets must cover WorkflowType exactly: "
                f"missing={missing or 'none'} extra={extra or 'none'}"
            )
        for preset in self.presets:
            unknown_tools = [
                tool.value
                for tool in preset.allowed_tools
                if tool not in tool_ids
            ]
            if unknown_tools:
                raise ValueError(
                    f"preset {preset.preset_id} references unknown tools: "
                    + ", ".join(unknown_tools)
                )
            unknown_modalities = [
                modality
                for modality in preset.required_input_modalities
                if modality not in KNOWN_INPUT_MODALITIES
            ]
            if unknown_modalities:
                raise ValueError(
                    f"preset {preset.preset_id} requires unknown modalities: "
                    + ", ".join(unknown_modalities)
                )
        skill_ids = {skill.skill_id for skill in self.skills}
        if len(skill_ids) != len(self.skills):
            raise ValueError("harness registry contains duplicate skill ids")

    def resolve_preset(self, workflow_type: WorkflowType) -> AgentPreset:
        for preset in self.presets:
            if preset.workflow_type == workflow_type:
                return preset
        raise ValueError(
            f"no agent preset registered for workflow_type={workflow_type.value}"
        )


CONTROLLED_TOOL_CATALOG = (
    ControlledToolMetadata(
        tool_id=ControlledTool.COURSE_RETRIEVAL,
        display_name="课程检索",
        description=(
            "课程范围内确定性词法检索，只返回当前课程已审核资料（本地语料或"
            "合成 Fixture），服务端编排，模型不能直接调用。"
        ),
    ),
    ControlledToolMetadata(
        tool_id=ControlledTool.EVIDENCE_LOCATION,
        display_name="证据定位",
        description=(
            "引用 Guard 只接受本次候选来源的定位（页码/幻灯片/标题/题目），"
            "模型不能自行声明证据位置或跨课程引用。"
        ),
    ),
    ControlledToolMetadata(
        tool_id=ControlledTool.BILIBILI_ANONYMOUS_SEARCH,
        display_name="Bilibili 匿名搜索",
        description=(
            "模型只提供 0～3 个聚焦检索词，服务端生成一条固定匿名搜索 URL；"
            "不抓取页面、不维护视频目录、不返回视频直链。"
        ),
    ),
    ControlledToolMetadata(
        tool_id=ControlledTool.TEMPORARY_MATERIAL_READ,
        display_name="临时材料读取",
        description=(
            "读取请求携带的临时材料文本（material_text）作为本次上下文，"
            "不落库、不读取外部文件。"
        ),
    ),
)

MAINTAINER_SKILLS = (
    MaintainerSkillMetadata(
        skill_id="material_conversion",
        display_name="资料 Markdown 转换",
        version="v1",
        description=(
            "维护者在离线 pipeline 中把学科资料转换为带 frontmatter 的 "
            "Markdown 并通过 manifest 校验。本注册表只定义契约元数据："
            "Runtime 不执行转换，转换也不能把资料标记为 passed 或 active。"
        ),
        status=MaterialConversionSkillStatus.CONTRACT_ONLY,
        human_review_required=True,
        can_mark_passed_or_active=False,
    ),
)

AGENT_PRESETS = (
    AgentPreset(
        preset_id="preset_knowledge_qa",
        preset_version=PRESET_VERSION,
        display_name="知识点问答",
        workflow_type=WorkflowType.KNOWLEDGE_QA,
        focus_strategy=FocusStrategy.QUESTION_CONCEPT,
        allowed_tools=(
            ControlledTool.COURSE_RETRIEVAL,
            ControlledTool.EVIDENCE_LOCATION,
            ControlledTool.BILIBILI_ANONYMOUS_SEARCH,
        ),
        required_input_modalities=("text",),
        requires_structured_outputs=True,
    ),
    AgentPreset(
        preset_id="preset_exam_review",
        preset_version=PRESET_VERSION,
        display_name="备考复习",
        workflow_type=WorkflowType.EXAM_REVIEW,
        focus_strategy=FocusStrategy.SYLLABUS_WEAK_TOPICS,
        allowed_tools=(
            ControlledTool.COURSE_RETRIEVAL,
            ControlledTool.EVIDENCE_LOCATION,
            ControlledTool.BILIBILI_ANONYMOUS_SEARCH,
        ),
        required_input_modalities=("text",),
        requires_structured_outputs=True,
    ),
    AgentPreset(
        preset_id="preset_problem_tutor",
        preset_version=PRESET_VERSION,
        display_name="题目辅导",
        workflow_type=WorkflowType.PROBLEM_TUTOR,
        focus_strategy=FocusStrategy.PROBLEM_MAIN_TOPIC,
        allowed_tools=(
            ControlledTool.COURSE_RETRIEVAL,
            ControlledTool.EVIDENCE_LOCATION,
            ControlledTool.BILIBILI_ANONYMOUS_SEARCH,
        ),
        required_input_modalities=("text",),
        requires_structured_outputs=True,
    ),
    AgentPreset(
        preset_id="preset_mistake_review",
        preset_version=PRESET_VERSION,
        display_name="错题复盘",
        workflow_type=WorkflowType.MISTAKE_REVIEW,
        focus_strategy=FocusStrategy.MISTAKE_ROOT_CAUSE,
        allowed_tools=(
            ControlledTool.COURSE_RETRIEVAL,
            ControlledTool.EVIDENCE_LOCATION,
            ControlledTool.BILIBILI_ANONYMOUS_SEARCH,
        ),
        required_input_modalities=("text",),
        requires_structured_outputs=True,
    ),
    AgentPreset(
        preset_id="preset_temporary_material_reading",
        preset_version=PRESET_VERSION,
        display_name="临时材料阅读",
        workflow_type=WorkflowType.TEMPORARY_MATERIAL_READING,
        focus_strategy=FocusStrategy.MATERIAL_TITLE_MAIN_TOPICS,
        allowed_tools=(
            ControlledTool.COURSE_RETRIEVAL,
            ControlledTool.EVIDENCE_LOCATION,
            ControlledTool.BILIBILI_ANONYMOUS_SEARCH,
            ControlledTool.TEMPORARY_MATERIAL_READ,
        ),
        required_input_modalities=("text",),
        requires_structured_outputs=True,
    ),
)

HARNESS_REGISTRY = HarnessRegistry(
    version=HARNESS_REGISTRY_VERSION,
    presets=AGENT_PRESETS,
    tools=CONTROLLED_TOOL_CATALOG,
    skills=MAINTAINER_SKILLS,
)


@dataclass(frozen=True, slots=True)
class CoursePluginState:
    course_id: str
    display_name: str
    state: CourseState
    enabled_workflows: tuple[WorkflowType, ...]


def derive_course_plugin_states(
    registry: object,
    retrieval: object,
    *,
    retrieval_mode: str,
) -> tuple[CoursePluginState, ...]:
    """Derive honest course states from CourseRegistry plus gateway availability.

    A course is ``active`` only when the current RetrievalGateway can serve it
    right now. A course with only synthetic fixture coverage is ``fixture_only``;
    everything else is merely ``registered``. Unavailable courses never claim
    enabled workflows.
    """
    states: list[CoursePluginState] = []
    for course in registry.records:
        if _gateway_serves_course(retrieval, course, retrieval_mode):
            state = CourseState.ACTIVE
            enabled_workflows = tuple(WorkflowType)
        elif course.fixture_available:
            state = CourseState.FIXTURE_ONLY
            enabled_workflows = ()
        else:
            state = CourseState.REGISTERED
            enabled_workflows = ()
        states.append(
            CoursePluginState(
                course_id=course.course_id,
                display_name=course.display_name,
                state=state,
                enabled_workflows=enabled_workflows,
            )
        )
    return tuple(states)


def _gateway_serves_course(
    retrieval: object, course: object, retrieval_mode: str
) -> bool:
    check = getattr(retrieval, "is_course_available", None)
    if callable(check):
        try:
            return bool(check(course.course_id))
        except Exception:
            # A broken/unavailable gateway must never claim active courses.
            return False
    # Mirrors the runtime's legacy test-double compatibility: without an
    # availability check only a fixture-available course can be served, and the
    # local corpus adapter must always prove active state itself.
    return retrieval_mode == "fixture" and bool(course.fixture_available)
