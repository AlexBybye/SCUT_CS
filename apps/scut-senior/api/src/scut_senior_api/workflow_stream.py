from __future__ import annotations

from collections.abc import Callable
from threading import Lock
from uuid import UUID, uuid4

from .contracts import (
    AgentStreamEvent,
    AnswerBlock,
    AnswerDelta,
    TraceEvent,
    WorkflowResult,
    WorkflowStreamError,
    WorkflowStreamEvent,
)


StreamEventSink = Callable[[WorkflowStreamEvent], None]


class WorkflowStreamSession:
    """Request-local stream ordering and cooperative cancellation state."""

    def __init__(
        self,
        sink: StreamEventSink,
        *,
        workflow_run_id: UUID | None = None,
    ) -> None:
        self.workflow_run_id = workflow_run_id or uuid4()
        self._sink = sink
        self._lifecycle_lock = Lock()
        self._cancel_requested = False
        self._terminal_claimed = False
        self._sequence_lock = Lock()
        self._next_sequence = 0
        self._terminal_emitted = False

    @property
    def cancelled(self) -> bool:
        with self._lifecycle_lock:
            return self._cancel_requested

    @property
    def terminal_emitted(self) -> bool:
        with self._sequence_lock:
            return self._terminal_emitted

    def cancel(self) -> None:
        # This lock is never held for the duration of a synchronous provider
        # call, so a disconnect can always record cancellation immediately.
        # A terminal claim that linearized first is already final and wins.
        with self._lifecycle_lock:
            if not self._terminal_claimed:
                self._cancel_requested = True

    def try_claim_step_start(self) -> bool:
        """Linearize admission of one external/runtime step.

        Cancellation that wins this short lock prevents the step. If admission
        wins, a later cancellation marks the step as already in flight; the
        service must observe it after return and persist ``interrupted``.
        """

        with self._lifecycle_lock:
            return not self._cancel_requested and not self._terminal_claimed

    def try_claim_terminal(self) -> bool:
        """Atomically choose a non-interrupted terminal result over cancellation."""

        with self._lifecycle_lock:
            if self._cancel_requested or self._terminal_claimed:
                return False
            self._terminal_claimed = True
            return True

    def emit_trace(self, event: TraceEvent) -> None:
        self._emit(
            WorkflowStreamEvent(
                kind="trace",
                workflow_run_id=self.workflow_run_id,
                sequence=self._take_sequence(),
                trace_event=event,
            )
        )

    def emit_answer_blocks(self, blocks: list[AnswerBlock]) -> None:
        for block_index, block in enumerate(blocks):
            # Keep each wire event comfortably under AnswerDelta.max_length.
            for offset in range(0, len(block.content), 2_000):
                delta = block.content[offset : offset + 2_000]
                if not delta:
                    continue
                self._emit(
                    WorkflowStreamEvent(
                        kind="answer_delta",
                        workflow_run_id=self.workflow_run_id,
                        sequence=self._take_sequence(),
                        answer_delta=AnswerDelta(
                            block_index=block_index,
                            type=block.type,
                            delta=delta,
                        ),
                    )
                )

    def emit_agent_event(
        self,
        event_kind: str,
        *,
        action: str | None = None,
        status: str | None = None,
        reason: str | None = None,
        step_count: int | None = None,
        observation_count: int | None = None,
    ) -> None:
        """Emit optional phase-two progress without exposing private evidence."""
        self._emit(
            WorkflowStreamEvent(
                kind="agent",
                workflow_run_id=self.workflow_run_id,
                sequence=self._take_sequence(),
                agent_event=AgentStreamEvent(
                    event_kind=event_kind,
                    action=action,
                    status=status,
                    reason=reason,
                    step_count=step_count,
                    observation_count=observation_count,
                ),
            )
        )

    def emit_result(self, result: WorkflowResult) -> None:
        if result.workflow_run_id != self.workflow_run_id:
            raise ValueError("stream result belongs to another workflow run")
        with self._sequence_lock:
            if self._terminal_emitted:
                return
            sequence = self._next_sequence
            self._next_sequence += 1
            self._terminal_emitted = True
        self._emit(
            WorkflowStreamEvent(
                kind="result",
                workflow_run_id=self.workflow_run_id,
                sequence=sequence,
                result=result,
            )
        )

    def emit_error(self, code: str, detail: str) -> None:
        with self._sequence_lock:
            if self._terminal_emitted:
                return
            sequence = self._next_sequence
            self._next_sequence += 1
            self._terminal_emitted = True
        self._emit(
            WorkflowStreamEvent(
                kind="error",
                workflow_run_id=self.workflow_run_id,
                sequence=sequence,
                error=WorkflowStreamError(code=code, detail=detail),
            )
        )

    def _take_sequence(self) -> int:
        with self._sequence_lock:
            if self._terminal_emitted:
                raise RuntimeError("cannot emit stream events after a terminal event")
            sequence = self._next_sequence
            self._next_sequence += 1
            return sequence

    def _emit(self, event: WorkflowStreamEvent) -> None:
        try:
            self._sink(event)
        except Exception:
            # A closed client transport must not turn a successfully guarded
            # run into a new error. The service observes cancellation at its
            # deterministic node boundaries and persists interrupted state.
            self.cancel()


class StreamingTrace(list[TraceEvent]):
    """Trace list that mirrors each real append into the same run stream."""

    def __init__(self, session: WorkflowStreamSession | None) -> None:
        super().__init__()
        self._session = session

    def append(self, event: TraceEvent) -> None:
        super().append(event)
        if self._session is not None:
            self._session.emit_trace(event)

    def append_without_emit(self, event: TraceEvent) -> None:
        super().append(event)

    def emit_appended(self, event: TraceEvent) -> None:
        if self._session is not None:
            self._session.emit_trace(event)
