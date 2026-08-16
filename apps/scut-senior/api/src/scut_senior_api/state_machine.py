from dataclasses import dataclass

from .contracts import RunStatus


class InvalidRunTransition(ValueError):
    pass


_ALLOWED_TRANSITIONS: dict[RunStatus, frozenset[RunStatus]] = {
    RunStatus.CREATED: frozenset({RunStatus.RUNNING, RunStatus.FAILED}),
    RunStatus.RUNNING: frozenset(
        {RunStatus.COMPLETED, RunStatus.INTERRUPTED, RunStatus.FAILED}
    ),
    RunStatus.COMPLETED: frozenset(),
    RunStatus.INTERRUPTED: frozenset(),
    RunStatus.FAILED: frozenset(),
}


@dataclass(slots=True)
class RunStateMachine:
    status: RunStatus = RunStatus.CREATED

    def transition(self, target: RunStatus) -> RunStatus:
        if target not in _ALLOWED_TRANSITIONS[self.status]:
            raise InvalidRunTransition(
                f"invalid run transition: {self.status.value} -> {target.value}"
            )
        self.status = target
        return self.status

