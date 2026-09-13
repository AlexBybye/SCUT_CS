"""Request-local Agent lifecycle state, independent of workflow business logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Callable
from uuid import UUID

from ..agent_loop import AgentBudget, AgentState, reduce_agent_event
from ..ports import WorkflowRepository
from ..workflow_stream import WorkflowStreamSession


def _default_metrics() -> dict[str, int]:
    return {
        "decision_call_count": 0,
        "model_action_accepted_count": 0,
        "model_action_shadow_count": 0,
        "answer_call_count": 0,
        "provider_retry_count": 0,
        "guard_retry_count": 0,
        "decision_fallback_count": 0,
        "action_rejection_count": 0,
    }


@dataclass(slots=True)
class RunLifecycle:
    """Own one execution's reducer, time budget and optional stream progress."""

    repository: WorkflowRepository
    run_id: UUID
    stream_session: WorkflowStreamSession | None
    agent_events_enabled: bool
    budget: AgentBudget = field(default_factory=AgentBudget)
    started_at: float = field(default_factory=perf_counter)
    state: AgentState = field(default_factory=AgentState)
    metrics: dict[str, int] = field(default_factory=_default_metrics)
    clock: Callable[[], float] = perf_counter

    def optional_model_work_allowed(self) -> bool:
        return (
            self.metrics["answer_call_count"] < self.budget.max_answer_calls
            and self.budget.allows_optional_call(self.elapsed_seconds)
        )

    @property
    def elapsed_seconds(self) -> float:
        return self.clock() - self.started_at

    def reduce(self, kind: str, **payload: object) -> AgentState:
        self.state = reduce_agent_event(
            self.state,
            {"kind": kind, **payload},
            budget=self.budget,
        )
        append_event = getattr(self.repository, "append_agent_event", None)
        if append_event is not None:
            append_event(self.run_id, {"kind": kind, **payload}, self.state.to_dict())
        if self.stream_session is not None and self.agent_events_enabled:
            self.stream_session.emit_agent_event(
                kind,
                action=(
                    payload.get("action")
                    if isinstance(payload.get("action"), str)
                    else None
                ),
                status=(
                    payload.get("status")
                    if isinstance(payload.get("status"), str)
                    else None
                ),
                reason=(
                    payload.get("reason")
                    if isinstance(payload.get("reason"), str)
                    else self.state.budget_reason
                ),
                step_count=self.state.step_count,
                observation_count=self.state.observation_count,
            )
        return self.state

    def record_action(self, action: str) -> AgentState:
        return self.reduce("action_executed", action=action)
