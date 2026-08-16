import pytest

from scut_senior_api.contracts import RunStatus
from scut_senior_api.state_machine import InvalidRunTransition, RunStateMachine


def test_run_state_machine_accepts_normal_completion() -> None:
    machine = RunStateMachine()

    machine.transition(RunStatus.RUNNING)
    machine.transition(RunStatus.COMPLETED)

    assert machine.status == RunStatus.COMPLETED


@pytest.mark.parametrize(
    ("start", "target"),
    [
        (RunStatus.CREATED, RunStatus.COMPLETED),
        (RunStatus.COMPLETED, RunStatus.RUNNING),
        (RunStatus.FAILED, RunStatus.RUNNING),
    ],
)
def test_run_state_machine_rejects_invalid_transitions(
    start: RunStatus, target: RunStatus
) -> None:
    machine = RunStateMachine(status=start)

    with pytest.raises(InvalidRunTransition):
        machine.transition(target)

