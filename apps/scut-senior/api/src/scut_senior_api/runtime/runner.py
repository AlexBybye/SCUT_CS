"""Small execution boundary between public service methods and one run."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from ..contracts import WorkflowResult, WorkflowRunRequest
from ..workflow_stream import WorkflowStreamSession


@dataclass(frozen=True, slots=True)
class WorkflowRunner:
    """Dispatch a run while preserving the public facade's construction API.

    The callable is deliberately narrow: orchestration state is request-local
    inside the execution method and never stored on the service singleton.
    """

    execute: Callable[..., WorkflowResult]

    def run(
        self,
        user: object,
        request: WorkflowRunRequest,
        *,
        attempt_group_id: UUID | None = None,
        regenerated_from_run_id: UUID | None = None,
        stream_session: WorkflowStreamSession | None = None,
    ) -> WorkflowResult:
        return self.execute(
            user,
            request,
            attempt_group_id=attempt_group_id,
            regenerated_from_run_id=regenerated_from_run_id,
            stream_session=stream_session,
        )
