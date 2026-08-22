import type {
  AnswerBlock,
  AnswerBlockType,
  TraceEvent,
  WorkflowRunResult,
  WorkflowStreamError,
  WorkflowStreamEvent,
} from "./contracts";
import {
  WorkflowStreamProtocolError,
  validateTraceEvent,
  validateWorkflowRunResult,
} from "./workflowResultValidation";

export { WorkflowStreamProtocolError } from "./workflowResultValidation";

const STREAM_KINDS = new Set(["trace", "answer_delta", "result", "error"]);
const ANSWER_BLOCK_TYPES = new Set<AnswerBlockType>([
  "repository",
  "user_material",
  "general",
  "personalized_analysis",
]);
const ERROR_CODE_PATTERN = /^[a-z][a-z0-9_]{0,99}$/;
const EVENT_FIELDS = new Set([
  "kind",
  "workflow_run_id",
  "sequence",
  "trace_event",
  "answer_delta",
  "result",
  "error",
]);
const ANSWER_DELTA_FIELDS = new Set(["block_index", "type", "delta"]);
const STREAM_ERROR_FIELDS = new Set(["code", "detail"]);

function assertOnlyKeys(
  value: Record<string, unknown>,
  allowed: ReadonlySet<string>,
  label: string,
): void {
  const unknown = Object.keys(value).find((key) => !allowed.has(key));
  if (unknown) throw new WorkflowStreamProtocolError(`unknown ${label} field: ${unknown}`);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function validateEvent(value: unknown, expectedConversationId?: string): WorkflowStreamEvent {
  if (!isRecord(value) || typeof value.kind !== "string" || !STREAM_KINDS.has(value.kind)) {
    throw new WorkflowStreamProtocolError("unknown Workflow stream event kind");
  }
  assertOnlyKeys(value, EVENT_FIELDS, "Workflow stream event");
  if (typeof value.sequence !== "number" || !Number.isInteger(value.sequence) || value.sequence < 0) {
    throw new WorkflowStreamProtocolError("invalid Workflow stream sequence");
  }
  const runId = value.workflow_run_id;
  if (value.kind !== "error" && typeof runId !== "string") {
    throw new WorkflowStreamProtocolError("non-error stream events require workflow_run_id");
  }
  if (value.kind === "error" && runId !== null && typeof runId !== "string") {
    throw new WorkflowStreamProtocolError("error workflow_run_id must be a string or null");
  }
  const payloadKeys = ["trace_event", "answer_delta", "result", "error"] as const;
  const present = payloadKeys.filter((key) => value[key] !== undefined);
  const expected = value.kind === "trace"
    ? "trace_event"
    : value.kind === "answer_delta"
      ? "answer_delta"
      : value.kind;
  if (present.length !== 1 || present[0] !== expected) {
    throw new WorkflowStreamProtocolError("stream event payload does not match kind");
  }
  if (value.kind === "trace") {
    validateTraceEvent(value.trace_event);
  } else if (value.kind === "answer_delta") {
    const delta = value.answer_delta;
    if (!isRecord(delta)) throw new WorkflowStreamProtocolError("invalid answer delta");
    assertOnlyKeys(delta, ANSWER_DELTA_FIELDS, "answer delta");
    if (typeof delta.block_index !== "number" || !Number.isInteger(delta.block_index) || delta.block_index < 0
      || typeof delta.delta !== "string" || !delta.delta || delta.delta.length > 4_000
      || typeof delta.type !== "string" || !ANSWER_BLOCK_TYPES.has(delta.type as AnswerBlockType)) {
      throw new WorkflowStreamProtocolError("invalid answer delta");
    }
  } else if (value.kind === "error") {
    if (!isRecord(value.error)) throw new WorkflowStreamProtocolError("invalid stream error");
    assertOnlyKeys(value.error, STREAM_ERROR_FIELDS, "stream error");
    if (typeof value.error.code !== "string" || !ERROR_CODE_PATTERN.test(value.error.code)
      || typeof value.error.detail !== "string" || !value.error.detail || value.error.detail.length > 500) {
      throw new WorkflowStreamProtocolError("invalid stream error");
    }
  } else {
    validateWorkflowRunResult(value.result, {
      expectedRunId: runId as string,
      expectedConversationId,
    });
  }
  return value as unknown as WorkflowStreamEvent;
}

export async function* parseWorkflowNdjson(
  stream: ReadableStream<Uint8Array>,
  options: { expectedConversationId?: string } = {},
): AsyncGenerator<WorkflowStreamEvent> {
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  try {
    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value ?? new Uint8Array(), { stream: !done });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";
      for (const line of lines) {
        const trimmed = line.replace(/\r$/, "").trim();
        if (!trimmed) continue;
        let parsed: unknown;
        try {
          parsed = JSON.parse(trimmed);
        } catch {
          throw new WorkflowStreamProtocolError("invalid NDJSON event");
        }
        yield validateEvent(parsed, options.expectedConversationId);
      }
      if (done) break;
    }
    const tail = buffer.trim();
    if (tail) {
      let parsed: unknown;
      try {
        parsed = JSON.parse(tail);
      } catch {
        throw new WorkflowStreamProtocolError("invalid final NDJSON event");
      }
      yield validateEvent(parsed, options.expectedConversationId);
    }
  } catch (error) {
    try {
      await reader.cancel("Workflow stream protocol failed");
    } catch {
      // The outer AbortController still closes a fetch-backed response body.
    }
    throw error;
  } finally {
    reader.releaseLock();
  }
}

export type WorkflowStreamPhase = "idle" | "running" | "completed" | "interrupted" | "failed";

export interface WorkflowStreamState {
  phase: WorkflowStreamPhase;
  workflowRunId: string | null;
  lastSequence: number;
  traceEvents: TraceEvent[];
  answerBlocks: AnswerBlock[];
  result: WorkflowRunResult | null;
  error: WorkflowStreamError | null;
}

export function createInitialWorkflowStreamState(): WorkflowStreamState {
  return {
    phase: "idle",
    workflowRunId: null,
    lastSequence: -1,
    traceEvents: [],
    answerBlocks: [],
    result: null,
    error: null,
  };
}

function ensureRun(state: WorkflowStreamState, event: WorkflowStreamEvent): string | null {
  const runId = event.workflow_run_id;
  if (runId === null) {
    if (event.kind !== "error") {
      throw new WorkflowStreamProtocolError("missing workflow run id");
    }
    if (state.workflowRunId !== null) {
      throw new WorkflowStreamProtocolError("run-bound error is missing workflow run id");
    }
    return null;
  }
  if (state.workflowRunId && state.workflowRunId !== runId) {
    throw new WorkflowStreamProtocolError("event belongs to another run");
  }
  return runId;
}

export function reduceWorkflowStreamEvent(
  state: WorkflowStreamState,
  event: WorkflowStreamEvent,
): WorkflowStreamState {
  if (["completed", "interrupted", "failed"].includes(state.phase)) {
    throw new WorkflowStreamProtocolError("cannot accept events after terminal state");
  }
  const runId = ensureRun(state, event);
  if (event.sequence !== state.lastSequence + 1) {
    throw new WorkflowStreamProtocolError("Workflow stream sequence is not contiguous");
  }
  const next: WorkflowStreamState = {
    ...state,
    phase: state.phase === "idle" ? "running" : state.phase,
    workflowRunId: runId ?? state.workflowRunId,
    lastSequence: event.sequence,
    traceEvents: [...state.traceEvents],
    answerBlocks: state.answerBlocks.map((block) => ({ ...block })),
  };
  if (event.kind === "trace" && event.trace_event) {
    if (event.trace_event.sequence !== next.traceEvents.length) {
      throw new WorkflowStreamProtocolError("Trace sequence is not contiguous");
    }
    if (next.traceEvents.some((traceEvent) => traceEvent.event_id === event.trace_event?.event_id)) {
      throw new WorkflowStreamProtocolError("duplicate Trace event id");
    }
    next.traceEvents.push(event.trace_event);
  } else if (event.kind === "answer_delta" && event.answer_delta) {
    const { block_index: index, type, delta } = event.answer_delta;
    if (index > next.answerBlocks.length) {
      throw new WorkflowStreamProtocolError("answer delta skipped a block index");
    }
    if (index === next.answerBlocks.length) next.answerBlocks.push({ type, content: "" });
    if (next.answerBlocks[index]?.type !== type) {
      throw new WorkflowStreamProtocolError("answer delta changed block type");
    }
    next.answerBlocks[index]!.content += delta;
  } else if (event.kind === "result" && event.result) {
    if (JSON.stringify(next.answerBlocks) !== JSON.stringify(event.result.answer_blocks)) {
      throw new WorkflowStreamProtocolError(
        "terminal result answer blocks do not match streamed deltas",
      );
    }
    if (JSON.stringify(next.traceEvents) !== JSON.stringify(event.result.trace)) {
      throw new WorkflowStreamProtocolError(
        "terminal result Trace does not match streamed Trace events",
      );
    }
    next.result = event.result;
    next.phase = event.result.run_status === "completed"
      ? "completed"
      : event.result.run_status === "interrupted" ? "interrupted" : "failed";
  } else if (event.kind === "error" && event.error) {
    next.error = event.error;
    next.phase = event.error.code === "client_interrupted" || event.error.code === "stream_interrupted"
      ? "interrupted" : "failed";
  }
  return next;
}

export function finalizeWorkflowStream(state: WorkflowStreamState): WorkflowStreamState {
  if (state.phase !== "idle" && state.phase !== "running") return state;
  return {
    ...state,
    phase: "interrupted",
    error: state.error ?? { code: "stream_interrupted", detail: "运行连接已中断。" },
  };
}

export interface WorkflowStreamHandle {
  signal: AbortSignal;
  abort: (detail?: string) => void;
  done: Promise<WorkflowStreamState>;
}

async function safeHttpError(response: Response): Promise<WorkflowStreamError> {
  const fallback: WorkflowStreamError = {
    code: "stream_request_failed",
    detail: `流式请求失败 (${response.status})。`,
  };
  const contentType = response.headers.get("Content-Type") ?? "";
  if (!contentType.toLowerCase().includes("application/json")) return fallback;
  try {
    const body = await response.json() as unknown;
    if (!isRecord(body)) return fallback;
    const nested = isRecord(body.error) ? body.error : null;
    const code = nested?.code;
    const detail = nested?.detail ?? body.detail ?? body.message;
    return {
      code: typeof code === "string" && ERROR_CODE_PATTERN.test(code) ? code : fallback.code,
      detail: typeof detail === "string" && detail.length > 0 && detail.length <= 500
        ? detail
        : fallback.detail,
    };
  } catch {
    return fallback;
  }
}

export function startWorkflowStreamRequest(
  input: RequestInfo | URL,
  init: RequestInit = {},
  options: {
    fetchImpl?: typeof fetch;
    onEvent?: (event: WorkflowStreamEvent, state: WorkflowStreamState) => void;
    expectedConversationId?: string;
  } = {},
): WorkflowStreamHandle {
  const controller = new AbortController();
  const fetchImpl = options.fetchImpl ?? fetch;
  let abortDetail = "运行已取消。";
  const done: Promise<WorkflowStreamState> = (async () => {
    let state = createInitialWorkflowStreamState();
    try {
      const response = await fetchImpl(input, { ...init, signal: controller.signal });
      if (!response.ok) {
        return {
          ...state,
          phase: "failed",
          error: await safeHttpError(response),
        };
      }
      if (!response.body) {
        throw new WorkflowStreamProtocolError("stream response body is missing");
      }
      for await (const event of parseWorkflowNdjson(response.body, {
        expectedConversationId: options.expectedConversationId,
      })) {
        state = reduceWorkflowStreamEvent(state, event);
        options.onEvent?.(event, state);
      }
      return finalizeWorkflowStream(state);
    } catch (error) {
      if (controller.signal.aborted || (error instanceof DOMException && error.name === "AbortError")) {
        return finalizeWorkflowStream({
          ...state,
          phase: "interrupted",
          error: { code: "client_interrupted", detail: abortDetail },
        });
      }
      controller.abort();
      const protocolError = error instanceof WorkflowStreamProtocolError;
      return {
        ...state,
        phase: "failed",
        error: {
          code: protocolError ? "stream_protocol_error" : "stream_request_failed",
          detail: protocolError
            ? error.message
            : // 真实网络错误（Failed to fetch 等）：运行不再因断线被取消，
              // 服务端仍会继续执行并保存终态，稍后重新读取即可取回结果。
              "网络连接中断，请检查网络后重试；本次运行仍会在服务端继续，稍后可点击「重新读取」查看结果。",
        },
      };
    }
  })();
  return {
    signal: controller.signal,
    abort(detail = "运行已取消。") {
      abortDetail = detail;
      controller.abort();
    },
    done,
  };
}
