"""Small, deterministic state reducer for the phase-two agent loop.

This module deliberately does not call a model or execute tools.  It owns the
state-machine rules that every future execution adapter must obey, so the
existing one-shot runtime can remain a compatible fallback while the loop is
introduced incrementally.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal


ActionKind = Literal[
    "retrieve",
    "retrieve_with_query_rewrite",
    "ask_clarification",
    "generate_answer",
    "finish",
]
EventKind = Literal[
    "decision_produced",
    "action_rejected",
    "observation_recorded",
    "budget_crossed",
    "clarification_requested",
    "run_finished",
]
TerminalStatus = Literal["running", "finished", "budget_exhausted", "rejected"]

ACTION_KINDS: frozenset[ActionKind] = frozenset(
    {
        "retrieve",
        "retrieve_with_query_rewrite",
        "ask_clarification",
        "generate_answer",
        "finish",
    }
)


@dataclass(frozen=True, slots=True)
class AgentBudget:
    max_steps: int = 4
    max_retrieval_rounds: int = 2
    max_query_rewrite: int = 1
    max_same_action_retries: int = 1
    max_guard_retries: int = 1

    def __post_init__(self) -> None:
        if any(
            isinstance(value, bool) or value < 0
            for value in (
                self.max_steps,
                self.max_retrieval_rounds,
                self.max_query_rewrite,
                self.max_same_action_retries,
                self.max_guard_retries,
            )
        ):
            raise ValueError("agent budget values must be non-negative integers")
        if self.max_steps < 1:
            raise ValueError("agent max_steps must be positive")


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

    if kind == "clarification_requested":
        return replace(state, status="finished")

    if kind == "budget_crossed":
        reason = event.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("budget_crossed requires a reason")
        return replace(state, status="budget_exhausted", budget_reason=reason)

    status = event.get("status")
    if status not in {"finished", "rejected", "budget_exhausted"}:
        raise ValueError("run_finished requires a terminal status")
    return replace(state, status=status)


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
    if action in {"retrieve", "retrieve_with_query_rewrite"}:
        rounds = state.retrieval_rounds + 1
        if rounds > limits.max_retrieval_rounds:
            return replace(state, status="budget_exhausted", budget_reason="max_retrieval_rounds")
        rewrites = state.query_rewrites + (action == "retrieve_with_query_rewrite")
        if rewrites > limits.max_query_rewrite:
            return replace(state, status="budget_exhausted", budget_reason="max_query_rewrite")
        return replace(state, retrieval_rounds=rounds, query_rewrites=rewrites)
    return state
