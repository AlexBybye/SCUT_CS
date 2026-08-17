import { describe, expect, it, vi } from "vitest";
import type {
  AnswerBlock,
  WorkflowRunResult,
  WorkflowStreamEvent,
} from "../contracts";
import {
  WorkflowStreamProtocolError,
  createInitialWorkflowStreamState,
  finalizeWorkflowStream,
  parseWorkflowNdjson,
  reduceWorkflowStreamEvent,
  startWorkflowStreamRequest,
} from "../workflowStream";

const encoder = new TextEncoder();

function ndjsonStream(chunks: string[]): ReadableStream<Uint8Array> {
  return new ReadableStream({
    start(controller) {
      for (const chunk of chunks) controller.enqueue(encoder.encode(chunk));
      controller.close();
    },
  });
}

async function collect(
  stream: ReadableStream<Uint8Array>,
): Promise<WorkflowStreamEvent[]> {
  const events: WorkflowStreamEvent[] = [];
  for await (const event of parseWorkflowNdjson(stream)) events.push(event);
  return events;
}

function completedResult(
  workflowRunId = "run-001",
  answerBlocks: AnswerBlock[] = [{ type: "repository", content: "矩阵的秩。" }],
): WorkflowRunResult {
  return {
    workflow_run_id: workflowRunId,
    conversation_id: "conversation-001",
    message_id: "message-001",
    answer_id: "answer-001",
    run_status: "completed",
    answer_status: "answered",
    workflow_type: "knowledge_qa",
    course_scope: "single",
    course_ids: ["linear_algebra"],
    repository_answer: "矩阵的秩。",
    general_supplement: null,
    answer_blocks: answerBlocks,
    workflow_output: {},
    evidence_status: "sufficient",
    citations: [],
    related_topics: [],
    related_questions: [],
    external_resources: [],
    trace: [],
    coverage_gaps: [],
    corpus_version: "fixture-corpus-v1",
    course_pack_version: null,
    workflow_version: "workflow-contract-v1",
    model_source: "platform_default",
    model: {
      provider_id: "mock",
      model_id: "deterministic-fixture-v1",
      billing_label: "not_applicable_mock",
      mock_only: true,
    },
    availability_status: "mock_only",
  };
}

function traceEvent(sequence: number, workflowRunId = "run-001"): WorkflowStreamEvent {
  return {
    kind: "trace",
    workflow_run_id: workflowRunId,
    sequence,
    trace_event: {
      event_id: `event-${sequence}`,
      sequence,
      node: "retrieval",
      status: "completed",
      duration_ms: 2,
      result: { hit_count: 1, evidence_status: "sufficient" },
    },
  };
}

describe("parseWorkflowNdjson", () => {
  it("handles arbitrary UTF-8 chunks, blank lines, CRLF, and a final line without newline", async () => {
    const first = JSON.stringify(traceEvent(1));
    const second = JSON.stringify({
      kind: "answer_delta",
      workflow_run_id: "run-001",
      sequence: 2,
      answer_delta: { block_index: 0, type: "repository", delta: "矩阵" },
    });
    const payload = `\n${first}\r\n${second}`;
    const bytes = encoder.encode(payload);
    const splitInsideChinese = bytes.findIndex((value) => value >= 0x80) + 1;
    const chunks = [
      new TextDecoder().decode(bytes.slice(0, splitInsideChinese)),
      new TextDecoder().decode(bytes.slice(splitInsideChinese)),
    ];

    const events = await collect(ndjsonStream(chunks));

    expect(events).toHaveLength(2);
    expect(events[0]).toMatchObject({ kind: "trace", sequence: 1 });
    expect(events[1]).toMatchObject({
      kind: "answer_delta",
      sequence: 2,
      answer_delta: { delta: "矩阵" },
    });
  });

  it("rejects unknown Trace result fields instead of exposing them to the student UI", async () => {
    const unsafe = JSON.stringify({
      ...traceEvent(1),
      trace_event: {
        ...traceEvent(1).trace_event,
        result: { prompt: "private prompt" },
      },
    });

    await expect(collect(ndjsonStream([`${unsafe}\n`]))).rejects.toThrow(
      /unknown Trace result field/i,
    );
  });
});

describe("reduceWorkflowStreamEvent", () => {
  it("accumulates same-run Trace and answer deltas with strictly increasing sequences", () => {
    let state = createInitialWorkflowStreamState();
    state = reduceWorkflowStreamEvent(state, traceEvent(1));
    state = reduceWorkflowStreamEvent(state, {
      kind: "answer_delta",
      workflow_run_id: "run-001",
      sequence: 2,
      answer_delta: { block_index: 0, type: "repository", delta: "矩阵" },
    });
    state = reduceWorkflowStreamEvent(state, {
      kind: "answer_delta",
      workflow_run_id: "run-001",
      sequence: 4,
      answer_delta: { block_index: 0, type: "repository", delta: "的秩。" },
    });

    expect(state.phase).toBe("running");
    expect(state.workflowRunId).toBe("run-001");
    expect(state.lastSequence).toBe(4);
    expect(state.traceEvents).toHaveLength(1);
    expect(state.answerBlocks).toEqual([{ type: "repository", content: "矩阵的秩。" }]);

    state = reduceWorkflowStreamEvent(state, {
      kind: "result",
      workflow_run_id: "run-001",
      sequence: 5,
      result: completedResult(),
    });
    expect(state.phase).toBe("completed");
    expect(state.result?.workflow_run_id).toBe("run-001");
  });

  it.each([
    ["duplicate", traceEvent(2), traceEvent(2)],
    ["out of order", traceEvent(3), traceEvent(2)],
    ["cross run", traceEvent(1), traceEvent(2, "run-002")],
  ])("rejects %s events", (_label, first, rejected) => {
    const state = reduceWorkflowStreamEvent(createInitialWorkflowStreamState(), first);
    expect(() => reduceWorkflowStreamEvent(state, rejected)).toThrow(
      WorkflowStreamProtocolError,
    );
  });

  it("rejects any event after a terminal result", () => {
    const terminal = reduceWorkflowStreamEvent(createInitialWorkflowStreamState(), {
      kind: "result",
      workflow_run_id: "run-001",
      sequence: 1,
      result: completedResult(),
    });

    expect(() => reduceWorkflowStreamEvent(terminal, traceEvent(2))).toThrow(
      /terminal/i,
    );
  });

  it("represents protocol error events and interrupted results as distinct terminal states", () => {
    const failed = reduceWorkflowStreamEvent(createInitialWorkflowStreamState(), {
      kind: "error",
      workflow_run_id: null,
      sequence: 0,
      error: { code: "auth_required", detail: "请先登录。" },
    });
    expect(failed).toMatchObject({
      phase: "failed",
      error: { code: "auth_required", detail: "请先登录。" },
    });

    const interruptedResult = {
      ...completedResult(),
      run_status: "interrupted" as const,
      answer_status: "partial" as const,
    };
    const interrupted = reduceWorkflowStreamEvent(createInitialWorkflowStreamState(), {
      kind: "result",
      workflow_run_id: "run-001",
      sequence: 1,
      result: interruptedResult,
    });
    expect(interrupted.phase).toBe("interrupted");
  });

  it("marks a stream that closes before a terminal event as interrupted", () => {
    const running = reduceWorkflowStreamEvent(createInitialWorkflowStreamState(), traceEvent(1));
    expect(finalizeWorkflowStream(running)).toMatchObject({
      phase: "interrupted",
      error: { code: "stream_interrupted" },
    });
  });
});

describe("startWorkflowStreamRequest", () => {
  it("exposes AbortController cancellation and resolves an interrupted state", async () => {
    const fetchImpl = vi.fn(
      (_input: RequestInfo | URL, init?: RequestInit) =>
        new Promise<Response>((_resolve, reject) => {
          init?.signal?.addEventListener("abort", () => {
            reject(new DOMException("aborted", "AbortError"));
          });
        }),
    );
    const handle = startWorkflowStreamRequest(
      "/api/v1/workflow-runs/stream",
      { method: "POST" },
      { fetchImpl },
    );

    handle.abort("用户取消了本次运行。");
    const state = await handle.done;

    expect(fetchImpl).toHaveBeenCalledTimes(1);
    expect(handle.signal.aborted).toBe(true);
    expect(state).toMatchObject({
      phase: "interrupted",
      error: { code: "client_interrupted", detail: "用户取消了本次运行。" },
    });
  });
});
