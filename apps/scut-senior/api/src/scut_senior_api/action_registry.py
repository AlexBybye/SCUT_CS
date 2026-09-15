"""Reviewed, fixed action catalogue for the bounded Layer 2 loop.

The catalogue owns declarative admission only. Executors and observation
serializers remain ordinary reviewed code and are never loaded from config.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ActionKind = Literal[
    "retrieve", "retrieve_with_query_rewrite", "ask_clarification",
    "generate_answer", "finish",
]


@dataclass(frozen=True, slots=True)
class ActionPolicy:
    name: ActionKind
    workflows: frozenset[str]
    phases: frozenset[str]
    executable: bool = True


class ActionRegistry:
    def __init__(self, policies: tuple[ActionPolicy, ...]):
        names = [policy.name for policy in policies]
        if len(names) != len(set(names)):
            raise ValueError("duplicate action policy")
        self._policies = {policy.name: policy for policy in policies}

    @property
    def action_kinds(self) -> frozenset[ActionKind]:
        return frozenset(self._policies)

    def allowed_actions(self, workflow: str, phase: str) -> tuple[ActionKind, ...]:
        return tuple(
            policy.name for policy in self._policies.values()
            if policy.executable and workflow in policy.workflows and phase in policy.phases
        )

    def admits(self, workflow: str, action: str, phase: str | None = None) -> bool:
        policy = self._policies.get(action)  # type: ignore[arg-type]
        return bool(policy and policy.executable and workflow in policy.workflows
                    and (phase is None or phase in policy.phases))


_COURSE_WORKFLOWS = frozenset({
    "knowledge_qa", "exam_review", "problem_tutor", "mistake_review",
})
_ALL_WORKFLOWS = _COURSE_WORKFLOWS | {"temporary_material_reading"}

ACTION_REGISTRY = ActionRegistry((
    ActionPolicy("retrieve", _ALL_WORKFLOWS, frozenset({"retrieve"})),
    ActionPolicy("retrieve_with_query_rewrite", _COURSE_WORKFLOWS,
                 frozenset({"retrieve_with_query_rewrite", "post_retrieval"})),
    ActionPolicy("generate_answer", _ALL_WORKFLOWS,
                 frozenset({"generate", "post_retrieval"})),
    # Historical event vocabulary. No executor or persistence contract exists.
    ActionPolicy("ask_clarification", _ALL_WORKFLOWS, frozenset(), executable=False),
    ActionPolicy("finish", _ALL_WORKFLOWS, frozenset(), executable=False),
))
