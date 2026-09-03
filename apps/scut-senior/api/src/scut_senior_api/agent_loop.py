"""Small, deterministic state reducer for the phase-two agent loop.

This module deliberately does not call a model or execute tools.  It owns the
state-machine rules that every future execution adapter must obey, so the
existing one-shot runtime can remain a compatible fallback while the loop is
introduced incrementally.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal, Protocol

from .ports import ConversationTurn, GeneratedAnswer, ModelGateway, RetrievedSource
from .contracts import WorkflowRunRequest


ActionKind = Literal[
    "retrieve",
    "retrieve_with_query_rewrite",
    "ask_clarification",
    "generate_answer",
    "finish",
]

# Workflow is the hard boundary. Agent may choose a next step only from the
# actions the selected workflow exposes; it never chooses a new workflow.
WORKFLOW_ACTIONS: dict[str, frozenset[ActionKind]] = {
    # The compatibility runtime has real execution semantics only for these
    # three actions.  ``finish`` and ``ask_clarification`` remain part of the
    # historical event vocabulary, but are intentionally not exposed to the
    # model until a corresponding executor and persistence contract exist.
    "knowledge_qa": frozenset({"retrieve", "retrieve_with_query_rewrite", "generate_answer"}),
    "exam_review": frozenset({"retrieve", "retrieve_with_query_rewrite", "generate_answer"}),
    "problem_tutor": frozenset({"retrieve", "retrieve_with_query_rewrite", "generate_answer"}),
    "mistake_review": frozenset({"retrieve", "retrieve_with_query_rewrite", "generate_answer"}),
    "temporary_material_reading": frozenset({"retrieve", "generate_answer"}),
}
EventKind = Literal[
    "decision_produced",
    "action_rejected",
    "observation_recorded",
    "budget_crossed",
    "clarification_requested",
    "run_finished",
    "action_executed",
    "guard_retry_recorded",
]
TerminalStatus = Literal[
    "running",
    "finished",
    "budget_exhausted",
    "rejected",
    "interrupted",
    "timed_out",
    "failed",
]

ACTION_KINDS: frozenset[ActionKind] = frozenset(
    {
        "retrieve",
        "retrieve_with_query_rewrite",
        "ask_clarification",
        "generate_answer",
        "finish",
    }
)


def action_allowed_for_workflow(workflow_type: str, action: ActionKind) -> bool:
    """Return whether an Agent action stays inside the selected Workflow."""
    return action in WORKFLOW_ACTIONS.get(workflow_type, frozenset())


class AgentDecisionGateway(Protocol):
    def decide(
        self,
        request: WorkflowRunRequest,
        state: "AgentState",
        phase: str,
        *,
        sources: list[RetrievedSource] | tuple[RetrievedSource, ...] = (),
        history: tuple[ConversationTurn, ...] = (),
    ) -> ActionKind: ...


class RuleBasedAgentDecision:
    """Deterministic fallback used when the model decision experiment is off."""

    def decide(self, request, state, phase, *, sources=(), history=()) -> ActionKind:
        return choose_next_action(state, phase=phase, workflow_type=request.workflow_type.value)


def parse_model_action(raw: str, *, workflow_type: str) -> ActionKind | None:
    """Parse a model's single-action response and apply the Workflow allowlist."""
    normalized = raw.strip().lower().replace("`", "")
    aliases: dict[str, ActionKind] = {
        "retrieve": "retrieve",
        "retrieve_with_query_rewrite": "retrieve_with_query_rewrite",
        "query_rewrite": "retrieve_with_query_rewrite",
        "ask_clarification": "ask_clarification",
        "generate_answer": "generate_answer",
        "finish": "finish",
    }
    # Fail closed: accept a single token only. Explanatory model prose must
    # never accidentally turn a mention of an Action into an executable one.
    token = normalized.strip(" .,;:：")
    action = aliases.get(token)
    if action is None:
        return None
    return action if action_allowed_for_workflow(workflow_type, action) else None


class ModelAgentDecision:
    """Model-backed Action adapter with fail-closed Workflow validation.

    The adapter is intentionally separate from answer generation. Providers
    that cannot return a clean action fall back to the deterministic policy;
    an unallowlisted action is never executed.
    """

    def __init__(self, model: ModelGateway, fallback: AgentDecisionGateway | None = None):
        self.model = model
        self.fallback = fallback or RuleBasedAgentDecision()
        self.last_used_fallback = False

    def decide(self, request, state, phase, *, sources=(), history=()) -> ActionKind:
        self.last_used_fallback = False
        allowed = (
            "retrieve_with_query_rewrite, generate_answer"
            if phase == "post_retrieval"
            else "retrieve, retrieve_with_query_rewrite, generate_answer"
        )
        decision_request = request.model_copy(
            update={
                "user_input": (
                    "只输出一个允许的 Action 名称，不要解释。"
                    f"允许值：{allowed}。"
                    f"当前 Workflow={request.workflow_type.value}，阶段={phase}，"
                    f"已检索轮次={state.retrieval_rounds}，已有证据数={len(sources)}。"
                )
            }
        )
        try:
            compact_decision = getattr(self.model, "decide_action", None)
            if callable(compact_decision):
                raw = compact_decision(
                    request,
                    state,
                    phase,
                    sources=tuple(sources),
                    history=history,
                )
            else:
                generated: GeneratedAnswer = self.model.generate(
                    decision_request, list(sources), history
                )
                raw = generated.repository_answer
            parsed = parse_model_action(
                raw, workflow_type=request.workflow_type.value
            )
            if parsed is not None:
                return parsed
        except Exception:
            self.last_used_fallback = True
        else:
            self.last_used_fallback = True
        return self.fallback.decide(request, state, phase, sources=sources, history=history)


def choose_next_action(
    state: "AgentState", *, phase: str, workflow_type: str = "knowledge_qa"
) -> ActionKind:
    """Select one bounded action for the compatibility runtime path.

    This is deliberately a small policy, not a second planner: retrieval is
    admitted once, then generation owns the final step. A future model-backed
    decision adapter can feed the same allowlist and reducer events.
    """
    if phase == "retrieve" and state.retrieval_rounds == 0:
        action = "retrieve"
        if not action_allowed_for_workflow(workflow_type, action):
            raise ValueError("workflow does not allow retrieval")
        return action
    if phase == "retrieve_with_query_rewrite":
        action = "retrieve_with_query_rewrite"
        if not action_allowed_for_workflow(workflow_type, action):
            raise ValueError("workflow does not allow query rewrite retrieval")
        return action
    if phase == "generate":
        action = "generate_answer"
        if not action_allowed_for_workflow(workflow_type, action):
            raise ValueError("workflow does not allow answer generation")
        return action
    if phase == "post_retrieval":
        action = "generate_answer"
        if not action_allowed_for_workflow(workflow_type, action):
            raise ValueError("workflow does not allow answer generation")
        return action
    raise ValueError("unknown agent compatibility phase")


@dataclass(frozen=True, slots=True)
class AgentBudget:
    max_steps: int = 5
    max_retrieval_rounds: int = 2
    max_query_rewrite: int = 1
    max_same_action_retries: int = 1
    max_guard_retries: int = 1
    max_answer_calls: int = 2
    max_runtime_seconds: int = 120
    soft_runtime_ratio: float = 0.75

    def __post_init__(self) -> None:
        if any(
            isinstance(value, bool) or value < 0
            for value in (
                self.max_steps,
                self.max_retrieval_rounds,
                self.max_query_rewrite,
                self.max_same_action_retries,
                self.max_guard_retries,
                self.max_answer_calls,
                self.max_runtime_seconds,
            )
        ):
            raise ValueError("agent budget values must be non-negative integers")
        if self.max_steps < 1:
            raise ValueError("agent max_steps must be positive")
        if self.max_answer_calls < 1:
            raise ValueError("agent max_answer_calls must be positive")
        if self.max_runtime_seconds < 1:
            raise ValueError("agent max_runtime_seconds must be positive")
        if not 0 < self.soft_runtime_ratio < 1:
            raise ValueError("agent soft_runtime_ratio must be between zero and one")

    @property
    def soft_runtime_seconds(self) -> float:
        return self.max_runtime_seconds * self.soft_runtime_ratio

    def allows_optional_call(self, elapsed_seconds: float) -> bool:
        """Admit optional model work only when it can finish before soft cutoff.

        Provider responses are not streamed through the Agent reducer, so the
        loop cannot observe an in-flight 75% token/time crossing. Once control
        returns after the 75% mark, optional follow-up work is no longer
        admitted; the 120-second hard limit remains unchanged.
        """

        return 0 <= elapsed_seconds < self.soft_runtime_seconds


@dataclass(frozen=True, slots=True)
class AgentState:
    status: TerminalStatus = "running"
    step_count: int = 0
    retrieval_rounds: int = 0
    query_rewrites: int = 0
    same_action_retries: int = 0
    guard_retries: int = 0
    last_action: ActionKind | None = None
    rejection_count: int = 0
    observation_count: int = 0
    budget_reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "step_count": self.step_count,
            "retrieval_rounds": self.retrieval_rounds,
            "query_rewrites": self.query_rewrites,
            "same_action_retries": self.same_action_retries,
            "guard_retries": self.guard_retries,
            "last_action": self.last_action,
            "rejection_count": self.rejection_count,
            "observation_count": self.observation_count,
            "budget_reason": self.budget_reason,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "AgentState":
        fields = cls().to_dict()
        unknown = set(payload) - set(fields)
        if unknown:
            raise ValueError("unknown agent state fields")
        values = {key: payload.get(key, default) for key, default in fields.items()}
        if values["status"] not in {
            "running", "finished", "budget_exhausted", "rejected",
            "interrupted", "timed_out", "failed",
        }:
            raise ValueError("invalid agent state status")
        for key in (
            "step_count",
            "retrieval_rounds",
            "query_rewrites",
            "same_action_retries",
            "guard_retries",
            "rejection_count",
            "observation_count",
        ):
            if isinstance(values[key], bool) or not isinstance(values[key], int) or values[key] < 0:
                raise ValueError("invalid agent state counter")
        action = values["last_action"]
        if action is not None and action not in ACTION_KINDS:
            raise ValueError("invalid agent state action")
        reason = values["budget_reason"]
        if reason is not None and not isinstance(reason, str):
            raise ValueError("invalid agent state budget reason")
        return cls(**values)  # type: ignore[arg-type]


def reduce_agent_event(
    state: AgentState, event: dict[str, object], *, budget: AgentBudget | None = None
) -> AgentState:
    """Apply one phase-two event and return the next immutable state.

    The reducer is intentionally strict: malformed or out-of-order events are
    rejected, and a terminal state cannot be changed by later events.
    """

    limits = budget or AgentBudget()
    kind = event.get("kind")
    if kind not in {
        "decision_produced",
        "action_rejected",
        "observation_recorded",
        "budget_crossed",
        "clarification_requested",
        "run_finished",
        "action_executed",
        "guard_retry_recorded",
    }:
        raise ValueError("unknown agent event kind")
    if state.status != "running":
        raise ValueError("agent events cannot follow a terminal state")

    if kind == "decision_produced":
        action = event.get("action")
        if action not in ACTION_KINDS:
            raise ValueError("decision action is not in the allowlist")
        next_steps = state.step_count + 1
        same_retries = (
            state.same_action_retries + 1
            if action == state.last_action
            else 0
        )
        if next_steps > limits.max_steps:
            return replace(
                state,
                status="budget_exhausted",
                budget_reason="max_steps",
            )
        if same_retries > limits.max_same_action_retries:
            return replace(
                state,
                status="budget_exhausted",
                budget_reason="max_same_action_retries",
            )
        return replace(
            state,
            step_count=next_steps,
            last_action=action,
            same_action_retries=same_retries,
        )

    if kind == "action_rejected":
        return replace(state, rejection_count=state.rejection_count + 1)

    if kind == "observation_recorded":
        return replace(state, observation_count=state.observation_count + 1)

    if kind == "action_executed":
        action = event.get("action")
        if action not in ACTION_KINDS:
            raise ValueError("executed action is not in the allowlist")
        return _record_action_result(state, action, limits)

    if kind == "guard_retry_recorded":
        return _record_guard_retry(state, limits)

    if kind == "clarification_requested":
        return replace(state, status="finished")

    if kind == "budget_crossed":
        reason = event.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("budget_crossed requires a reason")
        return replace(state, status="budget_exhausted", budget_reason=reason)

    status = event.get("status")
    if status not in {
        "finished", "rejected", "budget_exhausted", "interrupted", "timed_out", "failed"
    }:
        raise ValueError("run_finished requires a terminal status")
    return replace(state, status=status)


def replay_agent_events(
    events: list[dict[str, object]], *, budget: AgentBudget | None = None
) -> AgentState:
    """Rebuild a run state from its append-only phase-two event log."""
    state = AgentState()
    for event in events:
        state = reduce_agent_event(state, event, budget=budget)
    return state


def record_action_result(
    state: AgentState,
    action: ActionKind,
    *,
    budget: AgentBudget | None = None,
) -> AgentState:
    """Apply deterministic counters after an allowlisted action executes."""

    if action not in ACTION_KINDS:
        raise ValueError("action is not in the allowlist")
    if state.status != "running":
        raise ValueError("cannot execute an action after termination")
    limits = budget or AgentBudget()
    return _record_action_result(state, action, limits)


def _record_action_result(
    state: AgentState, action: ActionKind, limits: AgentBudget
) -> AgentState:
    if action in {"retrieve", "retrieve_with_query_rewrite"}:
        rounds = state.retrieval_rounds + 1
        if rounds > limits.max_retrieval_rounds:
            return replace(state, status="budget_exhausted", budget_reason="max_retrieval_rounds")
        rewrites = state.query_rewrites + (action == "retrieve_with_query_rewrite")
        if rewrites > limits.max_query_rewrite:
            return replace(state, status="budget_exhausted", budget_reason="max_query_rewrite")
        return replace(state, retrieval_rounds=rounds, query_rewrites=rewrites)
    return state


def record_guard_retry(
    state: AgentState, *, budget: AgentBudget | None = None
) -> AgentState:
    """Count one citation/output guard retry without consuming a new action."""

    if state.status != "running":
        raise ValueError("cannot retry a guard after termination")
    limits = budget or AgentBudget()
    return _record_guard_retry(state, limits)


def _record_guard_retry(state: AgentState, limits: AgentBudget) -> AgentState:
    retries = state.guard_retries + 1
    if retries > limits.max_guard_retries:
        return replace(state, status="budget_exhausted", budget_reason="max_guard_retries")
    next_steps = state.step_count + 1
    if next_steps > limits.max_steps:
        return replace(state, status="budget_exhausted", budget_reason="max_steps")
    return replace(state, guard_retries=retries, step_count=next_steps)
