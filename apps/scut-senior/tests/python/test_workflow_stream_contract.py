from uuid import uuid4

import pytest
from pydantic import ValidationError

from scut_senior_api.contracts import (
    TraceEvent,
    TraceEventStatus,
    WorkflowStreamError,
    WorkflowStreamEvent,
)
from scut_senior_api.export_contracts import render_schema_files


def safe_trace() -> TraceEvent:
    return TraceEvent(
        event_id=str(uuid4()),
        sequence=0,
        node="request_validation",
        status=TraceEventStatus.COMPLETED,
        duration_ms=0,
        result={"workflow_type": "knowledge_qa"},
    )


def test_trace_stream_event_requires_one_matching_payload_and_run_id() -> None:
    run_id = uuid4()
    event = WorkflowStreamEvent(
        kind="trace",
        workflow_run_id=run_id,
        sequence=0,
        trace_event=safe_trace(),
    )

    assert event.workflow_run_id == run_id
    assert event.trace_event is not None

    with pytest.raises(ValidationError, match="exactly the payload"):
        WorkflowStreamEvent(
            kind="trace",
            workflow_run_id=run_id,
            sequence=0,
            trace_event=safe_trace(),
            error=WorkflowStreamError(code="unexpected_error", detail="failed"),
        )

    with pytest.raises(ValidationError, match="require workflow_run_id"):
        WorkflowStreamEvent(
            kind="trace",
            workflow_run_id=None,
            sequence=0,
            trace_event=safe_trace(),
        )


def test_pre_run_stream_error_is_safe_and_may_have_no_run_id() -> None:
    event = WorkflowStreamEvent(
        kind="error",
        workflow_run_id=None,
        sequence=0,
        error=WorkflowStreamError(
            code="workflow_start_failed",
            detail="本次运行未能启动。",
        ),
    )

    dumped = event.model_dump(mode="json")
    assert dumped["error"] == {
        "code": "workflow_start_failed",
        "detail": "本次运行未能启动。",
    }
    assert "traceback" not in str(dumped).casefold()


def test_stream_event_schema_is_exported() -> None:
    schema = render_schema_files()["workflow-stream-event.schema.json"]

    assert '"WorkflowStreamEvent"' in schema
    assert '"answer_delta"' in schema
