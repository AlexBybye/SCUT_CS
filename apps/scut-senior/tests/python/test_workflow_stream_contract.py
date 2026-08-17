import json
from copy import deepcopy
from uuid import UUID, uuid4

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from scut_senior_api.contracts import (
    TraceEvent,
    TraceEventStatus,
    WorkflowStreamError,
    WorkflowStreamEvent,
)
from scut_senior_api.export_contracts import render_schema_files


def exported_stream_schema() -> dict[str, object]:
    schema = json.loads(render_schema_files()["workflow-stream-event.schema.json"])
    Draft202012Validator.check_schema(schema)
    return schema


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


def valid_trace_stream_payload() -> dict[str, object]:
    return WorkflowStreamEvent(
        kind="trace",
        workflow_run_id=uuid4(),
        sequence=0,
        trace_event=safe_trace(),
    ).model_dump(mode="json")


def valid_result_payload(workflow_run_id: UUID, run_status: str) -> dict[str, object]:
    return {
        "workflow_run_id": str(workflow_run_id),
        "conversation_id": str(uuid4()),
        "message_id": str(uuid4()),
        "answer_id": str(uuid4()),
        "run_status": run_status,
        "answer_status": "answered",
        "workflow_type": "knowledge_qa",
        "course_scope": "single",
        "course_ids": ["linear_algebra"],
        "repository_answer": "矩阵的秩是其线性无关行或列的最大数量。",
        "general_supplement": None,
        "answer_blocks": [],
        "workflow_output": {},
        "evidence_status": "not_evaluated",
        "citations": [],
        "related_topics": [],
        "related_questions": [],
        "external_resources": [],
        "coverage_gaps": [],
        "trace": [],
        "corpus_version": "fixture-only",
        "course_pack_version": None,
        "workflow_version": "iteration-3",
        "model_source": "platform_default",
        "model": {
            "provider_id": "mock",
            "model_id": "deterministic-fixture-v1",
            "billing_label": "mock_only",
            "mock_only": True,
        },
        "availability_status": "mock_only",
    }


@pytest.mark.parametrize(
    "mutation",
    [
        {"trace_event": None},
        {
            "answer_delta": {
                "block_index": 0,
                "type": "repository",
                "delta": "额外 payload",
            }
        },
        {"kind": "answer_delta"},
    ],
)
def test_exported_stream_schema_rejects_kind_payload_mismatches(
    mutation: dict[str, object],
) -> None:
    validator = Draft202012Validator(exported_stream_schema())
    payload = valid_trace_stream_payload()
    payload.update(mutation)

    assert list(validator.iter_errors(payload))


def test_exported_stream_schema_requires_the_matching_payload_field() -> None:
    validator = Draft202012Validator(exported_stream_schema())
    payload = valid_trace_stream_payload()
    payload.pop("trace_event")

    assert list(validator.iter_errors(payload))


def test_exported_stream_schema_accepts_trace_and_answer_delta_events() -> None:
    validator = Draft202012Validator(exported_stream_schema())
    validator.validate(valid_trace_stream_payload())
    validator.validate(
        {
            "kind": "answer_delta",
            "workflow_run_id": str(uuid4()),
            "sequence": 1,
            "trace_event": None,
            "answer_delta": {
                "block_index": 0,
                "type": "repository",
                "delta": "矩阵的秩",
            },
            "result": None,
            "error": None,
        }
    )


def test_exported_stream_schema_requires_non_error_run_id() -> None:
    validator = Draft202012Validator(exported_stream_schema())
    payload = valid_trace_stream_payload()
    payload["workflow_run_id"] = None

    assert list(validator.iter_errors(payload))

    error_payload = {
        "kind": "error",
        "workflow_run_id": None,
        "sequence": 0,
        "trace_event": None,
        "answer_delta": None,
        "result": None,
        "error": {
            "code": "workflow_start_failed",
            "detail": "本次运行未能启动。",
        },
    }
    validator.validate(error_payload)


@pytest.mark.parametrize("run_status", ["completed", "interrupted", "failed"])
def test_exported_stream_schema_accepts_terminal_results(run_status: str) -> None:
    validator = Draft202012Validator(exported_stream_schema())
    run_id = uuid4()
    payload = {
        "kind": "result",
        "workflow_run_id": str(run_id),
        "sequence": 1,
        "trace_event": None,
        "answer_delta": None,
        "result": valid_result_payload(run_id, run_status),
        "error": None,
    }

    validator.validate(payload)


@pytest.mark.parametrize("run_status", ["created", "running"])
def test_exported_stream_schema_rejects_non_terminal_results(run_status: str) -> None:
    validator = Draft202012Validator(exported_stream_schema())
    run_id = uuid4()
    payload = {
        "kind": "result",
        "workflow_run_id": str(run_id),
        "sequence": 1,
        "trace_event": None,
        "answer_delta": None,
        "result": valid_result_payload(run_id, "completed"),
        "error": None,
    }
    invalid = deepcopy(payload)
    invalid["result"]["run_status"] = run_status

    assert list(validator.iter_errors(invalid))
