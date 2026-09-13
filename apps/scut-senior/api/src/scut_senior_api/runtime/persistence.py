"""Persistence boundary for workflow attempts.

The component intentionally does not decide result status, construct a result,
or emit traces.  The runtime controls those semantics; this boundary only
persists an already constructed result and retains the authenticated-session
rollback rule.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from ..auth import AuthRequired
from ..contracts import WorkflowResult, WorkflowRunRequest
from ..ports import WorkflowRepository


@dataclass(frozen=True, slots=True)
class RunPersistence:
    repository: WorkflowRepository

    def save(
        self,
        *,
        user_id: str,
        auth_session_id: UUID | None,
        request: WorkflowRunRequest,
        result: WorkflowResult,
        attempt_group_id: UUID | None,
        regenerated_from_run_id: UUID | None,
    ) -> None:
        try:
            self.repository.save_run(
                user_id,
                request,
                result,
                attempt_group_id=attempt_group_id,
                regenerated_from_run_id=regenerated_from_run_id,
                auth_session_id=auth_session_id,
            )
        except AuthRequired:
            self.repository.discard_nonterminal_run(user_id, result.workflow_run_id)
            raise
