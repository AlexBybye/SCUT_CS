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

function ndjsonStream(chunks: Array<string | Uint8Array>): ReadableStream<Uint8Array> {
  return new ReadableStream({
    start(controller) {
      for (const chunk of chunks) {
        controller.enqueue(typeof chunk === "string" ? encoder.encode(chunk) : chunk);
      }
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
    const first = JSON.stringify(traceEvent(0));
    const second = JSON.stringify({
      kind: "answer_delta",
      workflow_run_id: "run-001",
      sequence: 1,
      answer_delta: { block_index: 0, type: "repository", delta: "矩阵" },
    });
    const payload = `\n${first}\r\n${second}`;
    const bytes = encoder.encode(payload);
    const splitInsideChinese = bytes.findIndex((value) => value >= 0x80) + 1;
    const chunks = [bytes.slice(0, splitInsideChinese), bytes.slice(splitInsideChinese)];

    const events = await collect(ndjsonStream(chunks));

    expect(events).toHaveLength(2);
    expect(events[0]).toMatchObject({ kind: "trace", sequence: 0 });
    expect(events[1]).toMatchObject({
      kind: "answer_delta",
      sequence: 1,
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

  it("rejects unknown nested Trace fields and invalid values under otherwise safe keys", async () => {
    const nestedUnsafe = {
      ...traceEvent(0),
      trace_event: {
        ...traceEvent(0).trace_event,
        result: {
          sources: [{
            course_id: "linear_algebra",
            title: "线性代数讲义",
            prompt: "private prompt",
          }],
        },
      },
    };
    const wrongType = {
      ...traceEvent(0),
      trace_event: {
        ...traceEvent(0).trace_event,
        result: { hit_count: "1" },
      },
    };

    await expect(collect(ndjsonStream([`${JSON.stringify(nestedUnsafe)}\n`]))).rejects.toThrow(
      /unknown Trace source field: prompt/i,
    );
    await expect(collect(ndjsonStream([`${JSON.stringify(wrongType)}\n`]))).rejects.toThrow(
      /invalid Trace hit_count/i,
    );
  });

  it("strictly rejects explicit null payload siblings; the endpoint must serialize exclude_none", async () => {
    const pydanticDefault = JSON.stringify({
      ...traceEvent(1),
      answer_delta: null,
      result: null,
      error: null,
    });

    await expect(collect(ndjsonStream([`${pydanticDefault}\n`]))).rejects.toThrow(
      /payload does not match kind/i,
    );
  });

  it("rejects a concrete Bilibili video URL in the terminal result", async () => {
    const unsafeResult = completedResult();
    unsafeResult.external_resources = [{
      resource_id: null,
      course_id: "linear_algebra",
      platform: "bilibili",
      resource_type: "search",
      title: "不应显示的具体视频",
      url: "https://www.bilibili.com/video/BV1unsafe",
      matched_topic: "矩阵的秩",
      review_status: "unreviewed_live_search",
      catalog_version: null,
      query_keywords: ["矩阵的秩"],
      generated_at: "2026-08-17T00:00:00Z",
      evidence_role: "supplementary_only",
    }];
    const event: WorkflowStreamEvent = {
      kind: "result",
      workflow_run_id: "run-001",
      sequence: 1,
      result: unsafeResult,
    };

    await expect(collect(ndjsonStream([`${JSON.stringify(event)}\n`]))).rejects.toThrow(
      /fixed anonymous search URL/i,
    );
  });

  it("rejects missing, unknown, and malformed terminal result fields", async () => {
    const missingEvidence = { ...completedResult() } as Record<string, unknown>;
    delete missingEvidence.evidence_status;
    const unknownResult = { ...completedResult(), debug_payload: { prompt: "private" } };
    const malformedCitation = { ...completedResult(), citations: [null] };

    for (const [result, message] of [
      [missingEvidence, /missing Workflow result field: evidence_status/i],
      [unknownResult, /unknown Workflow result field: debug_payload/i],
      [malformedCitation, /invalid result citation/i],
    ] as const) {
      const event = {
        kind: "result",
        workflow_run_id: "run-001",
        sequence: 0,
        result,
      };
      await expect(collect(ndjsonStream([`${JSON.stringify(event)}\n`]))).rejects.toThrow(message);
    }
  });

  it("binds a terminal stream result to the requested conversation", async () => {
    const result = completedResult();
    result.conversation_id = "conversation-002";
    const event = {
      kind: "result",
      workflow_run_id: "run-001",
      sequence: 0,
      result,
    };

    const consume = async () => {
      const events: WorkflowStreamEvent[] = [];
      for await (const item of parseWorkflowNdjson(
        ndjsonStream([`${JSON.stringify(event)}\n`]),
        { expectedConversationId: "conversation-001" },
      )) events.push(item);
      return events;
    };
    await expect(consume()).rejects.toThrow(/another conversation/i);
  });
});

describe("reduceWorkflowStreamEvent", () => {
  it("accumulates same-run Trace and answer deltas with contiguous sequences", () => {
    let state = createInitialWorkflowStreamState();
    state = reduceWorkflowStreamEvent(state, traceEvent(0));
    state = reduceWorkflowStreamEvent(state, {
      kind: "answer_delta",
      workflow_run_id: "run-001",
      sequence: 1,
      answer_delta: { block_index: 0, type: "repository", delta: "矩阵" },
    });
    state = reduceWorkflowStreamEvent(state, {
      kind: "answer_delta",
      workflow_run_id: "run-001",
      sequence: 2,
      answer_delta: { block_index: 0, type: "repository", delta: "的秩。" },
    });

    expect(state.phase).toBe("running");
    expect(state.workflowRunId).toBe("run-001");
    expect(state.lastSequence).toBe(2);
    expect(state.traceEvents).toHaveLength(1);
    expect(state.answerBlocks).toEqual([{ type: "repository", content: "矩阵的秩。" }]);

    const terminalResult = completedResult();
    terminalResult.trace = [traceEvent(0).trace_event!];
    state = reduceWorkflowStreamEvent(state, {
      kind: "result",
      workflow_run_id: "run-001",
      sequence: 3,
      result: terminalResult,
    });
    expect(state.phase).toBe("completed");
    expect(state.result?.workflow_run_id).toBe("run-001");
  });

  it.each([
    ["duplicate", traceEvent(0), traceEvent(0)],
    ["gap", traceEvent(0), traceEvent(2)],
    ["cross run", traceEvent(0), traceEvent(1, "run-002")],
  ])("rejects %s events", (_label, first, rejected) => {
    const state = reduceWorkflowStreamEvent(createInitialWorkflowStreamState(), first);
    expect(() => reduceWorkflowStreamEvent(state, rejected)).toThrow(
      WorkflowStreamProtocolError,
    );
  });

  it("rejects an error event that claims a different run", () => {
    const state = reduceWorkflowStreamEvent(createInitialWorkflowStreamState(), traceEvent(0));
    expect(() => reduceWorkflowStreamEvent(state, {
      kind: "error",
      workflow_run_id: "run-002",
      sequence: 1,
      error: { code: "runtime_failed", detail: "运行失败。" },
    })).toThrow(/another run/i);
  });

  it("rejects a null-run error after the stream has bound itself to a run", () => {
    const state = reduceWorkflowStreamEvent(createInitialWorkflowStreamState(), traceEvent(0));
    expect(() => reduceWorkflowStreamEvent(state, {
      kind: "error",
      workflow_run_id: null,
      sequence: 1,
      error: { code: "runtime_failed", detail: "运行失败。" },
    })).toThrow(/missing workflow run id/i);
  });

  it("rejects non-contiguous or duplicate Trace identities inside contiguous wire events", () => {
    const state = reduceWorkflowStreamEvent(createInitialWorkflowStreamState(), traceEvent(0));
    const wrongTraceSequence = traceEvent(1);
    wrongTraceSequence.trace_event!.sequence = 2;
    expect(() => reduceWorkflowStreamEvent(state, wrongTraceSequence)).toThrow(
      /Trace sequence is not contiguous/i,
    );

    const duplicateTraceId = traceEvent(1);
    duplicateTraceId.trace_event!.event_id = traceEvent(0).trace_event!.event_id;
    expect(() => reduceWorkflowStreamEvent(state, duplicateTraceId)).toThrow(
      /duplicate Trace event id/i,
    );
  });

  it("rejects any event after a terminal result", () => {
    const emptyResult = completedResult("run-001", []);
    emptyResult.repository_answer = null;
    const terminal = reduceWorkflowStreamEvent(createInitialWorkflowStreamState(), {
      kind: "result",
      workflow_run_id: "run-001",
      sequence: 0,
      result: emptyResult,
    });

    expect(() => reduceWorkflowStreamEvent(terminal, traceEvent(1))).toThrow(
      /terminal/i,
    );
  });

  it("rejects a terminal snapshot that differs from streamed content", () => {
    let state = reduceWorkflowStreamEvent(createInitialWorkflowStreamState(), {
      kind: "answer_delta",
      workflow_run_id: "run-001",
      sequence: 0,
      answer_delta: { block_index: 0, type: "repository", delta: "流式回答" },
    });
    const mismatched = completedResult("run-001", [
      { type: "repository", content: "不同的终态回答" },
    ]);

    expect(() => reduceWorkflowStreamEvent(state, {
      kind: "result",
      workflow_run_id: "run-001",
      sequence: 1,
      result: mismatched,
    })).toThrow(/do not match streamed deltas/i);
  });

  it("rejects answer deltas that skip block indexes", () => {
    expect(() => reduceWorkflowStreamEvent(createInitialWorkflowStreamState(), {
      kind: "answer_delta",
      workflow_run_id: "run-001",
      sequence: 0,
      answer_delta: { block_index: 1, type: "general", delta: "补充" },
    })).toThrow(/skipped a block index/i);
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
      ...completedResult("run-001", []),
      repository_answer: null,
      run_status: "interrupted" as const,
      answer_status: "partial" as const,
    };
    const interrupted = reduceWorkflowStreamEvent(createInitialWorkflowStreamState(), {
      kind: "result",
      workflow_run_id: "run-001",
      sequence: 0,
      result: interruptedResult,
    });
    expect(interrupted.phase).toBe("interrupted");
  });

  it("marks a stream that closes before a terminal event as interrupted", () => {
    const running = reduceWorkflowStreamEvent(createInitialWorkflowStreamState(), traceEvent(0));
    expect(finalizeWorkflowStream(running)).toMatchObject({
      phase: "interrupted",
      error: { code: "stream_interrupted" },
    });
  });
});

describe("startWorkflowStreamRequest", () => {
  it("publishes incremental states and keeps the terminal result on the same run", async () => {
    const firstTrace = traceEvent(0);
    const terminalResult = completedResult();
    terminalResult.trace = [firstTrace.trace_event!];
    const events: WorkflowStreamEvent[] = [
      firstTrace,
      {
        kind: "answer_delta",
        workflow_run_id: "run-001",
        sequence: 1,
        answer_delta: { block_index: 0, type: "repository", delta: "矩阵的秩。" },
      },
      {
        kind: "result",
        workflow_run_id: "run-001",
        sequence: 2,
        result: terminalResult,
      },
    ];
    const body = events.map((event) => JSON.stringify(event)).join("\n") + "\n";
    const fetchImpl = vi.fn().mockResolvedValue(new Response(body, {
      status: 200,
      headers: { "Content-Type": "application/x-ndjson" },
    }));
    const onEvent = vi.fn();

    const state = await startWorkflowStreamRequest(
      "/api/v1/workflow-runs/stream",
      { method: "POST" },
      { fetchImpl, onEvent },
    ).done;

    expect(onEvent).toHaveBeenCalledTimes(3);
    expect(onEvent.mock.calls[1]?.[1]).toMatchObject({
      phase: "running",
      answerBlocks: [{ type: "repository", content: "矩阵的秩。" }],
    });
    expect(state).toMatchObject({
      phase: "completed",
      workflowRunId: "run-001",
      result: { workflow_run_id: "run-001" },
    });
  });

  it("keeps a bounded JSON HTTP error without retrying", async () => {
    const exhaustedMessage =
      "今日平台免费额度已用完，第二天再来重试吧！着急请使用你自己的 API Key。";
    const fetchImpl = vi.fn().mockResolvedValue(new Response(JSON.stringify({
      error: { code: "platform_daily_quota_exhausted", detail: exhaustedMessage },
    }), {
      status: 429,
      headers: { "Content-Type": "application/json" },
    }));

    const state = await startWorkflowStreamRequest(
      "/api/v1/workflow-runs/stream",
      { method: "POST" },
      { fetchImpl },
    ).done;

    expect(fetchImpl).toHaveBeenCalledTimes(1);
    expect(state).toMatchObject({
      phase: "failed",
      error: {
        code: "platform_daily_quota_exhausted",
        detail: exhaustedMessage,
      },
    });
  });

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

  it("actively cancels the response body and aborts fetch after a protocol error", async () => {
    const cancel = vi.fn();
    const body = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(encoder.encode('{"kind":"unknown"}\n'));
      },
      cancel,
    });
    const fetchImpl = vi.fn().mockResolvedValue(new Response(body, { status: 200 }));

    const handle = startWorkflowStreamRequest(
      "/api/v1/workflow-runs/stream",
      { method: "POST" },
      { fetchImpl },
    );
    const state = await handle.done;

    expect(state).toMatchObject({
      phase: "failed",
      error: { code: "stream_protocol_error" },
    });
    expect(cancel).toHaveBeenCalledTimes(1);
    expect(handle.signal.aborted).toBe(true);
  });

  it("maps a real network failure to a friendly message and keeps the run recoverable", async () => {
    const fetchImpl = vi.fn().mockRejectedValue(new TypeError("Failed to fetch"));

    const state = await startWorkflowStreamRequest(
      "/api/v1/workflow-runs/stream",
      { method: "POST" },
      { fetchImpl },
    ).done;

    expect(fetchImpl).toHaveBeenCalledTimes(1);
    expect(state).toMatchObject({
      phase: "failed",
      error: { code: "stream_request_failed" },
    });
    // 不再暴露原始 “Failed to fetch”，而是告诉学生运行会在服务端继续。
    expect(state.error?.detail).toContain("网络连接中断");
    expect(state.error?.detail).toContain("重新读取");
  });
});
