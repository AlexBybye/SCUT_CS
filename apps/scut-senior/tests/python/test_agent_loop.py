from __future__ import annotations

import pytest

from scut_senior_api.agent_loop import (
    AgentBudget,
    AgentState,
    record_action_result,
    record_guard_retry,
    reduce_agent_event,
)


def event(kind: str, **payload: object) -> dict[str, object]:
    return {"kind": kind, **payload}


def test_reducer_counts_decisions_and_observations() -> None:
    state = reduce_agent_event(
        AgentState(), event("decision_produced", action="retrieve")
    )
    state = record_action_result(state, "retrieve")
    state = reduce_agent_event(state, event("observation_recorded"))
    assert state.step_count == 1
    assert state.retrieval_rounds == 1
    assert state.observation_count == 1


def test_reducer_rejects_unknown_actions_and_late_events() -> None:
    with pytest.raises(ValueError, match="allowlist"):
        reduce_agent_event(
            AgentState(), event("decision_produced", action="delete_database")
        )
    finished = reduce_agent_event(AgentState(), event("run_finished", status="finished"))
    with pytest.raises(ValueError, match="terminal"):
        reduce_agent_event(finished, event("observation_recorded"))


def test_reducer_closes_on_step_and_action_retry_budgets() -> None:
    budget = AgentBudget(max_steps=4, max_same_action_retries=1)
    state = AgentState()
    state = reduce_agent_event(state, event("decision_produced", action="retrieve"), budget=budget)
    state = reduce_agent_event(state, event("decision_produced", action="retrieve"), budget=budget)
    assert state.status == "running"
    state = reduce_agent_event(state, event("decision_produced", action="retrieve"), budget=budget)
    assert state.status == "budget_exhausted"
    assert state.budget_reason == "max_same_action_retries"

    state = AgentState()
    step_budget = AgentBudget(max_steps=2, max_same_action_retries=4)
    state = reduce_agent_event(
        state, event("decision_produced", action="retrieve"), budget=step_budget
    )
    state = reduce_agent_event(
        state, event("decision_produced", action="generate_answer"), budget=step_budget
    )
    state = reduce_agent_event(
        state, event("decision_produced", action="finish"), budget=step_budget
    )
    assert state.status == "budget_exhausted"
    assert state.budget_reason == "max_steps"


def test_retrieve_rewrite_budget_is_separate_from_step_budget() -> None:
    budget = AgentBudget(max_query_rewrite=1)
    state = record_action_result(AgentState(), "retrieve_with_query_rewrite", budget=budget)
    assert state.query_rewrites == 1
    state = record_action_result(state, "retrieve_with_query_rewrite", budget=budget)
    assert state.status == "budget_exhausted"
    assert state.budget_reason == "max_query_rewrite"


def test_guard_retry_budget_is_explicit() -> None:
    budget = AgentBudget(max_guard_retries=1)
    state = record_guard_retry(AgentState(), budget=budget)
    assert state.guard_retries == 1
    state = record_guard_retry(state, budget=budget)
    assert state.status == "budget_exhausted"
    assert state.budget_reason == "max_guard_retries"
