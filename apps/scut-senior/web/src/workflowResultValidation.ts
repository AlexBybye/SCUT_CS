import type {
  Citation,
  ConversationDetail,
  ExternalResource,
  TraceEvent,
  TraceSafeResult,
  WorkflowAttempt,
  WorkflowRunResult,
} from "./contracts";

const ERROR_CODE_PATTERN = /^[a-z][a-z0-9_]{0,99}$/;
const WORKFLOW_TYPES = new Set([
  "knowledge_qa",
  "exam_review",
  "problem_tutor",
  "mistake_review",
  "temporary_material_reading",
]);
const COURSE_SCOPES = new Set(["single", "cross"]);
const KNOWLEDGE_SCOPES = new Set(["course_only", "course_first"]);
const MODEL_SOURCES = new Set(["platform_default", "user_key"]);
const ANSWER_STATUSES = new Set([
  "answered",
  "partial",
  "insufficient_evidence",
  "needs_clarification",
  "refused",
  "error",
]);
const EVIDENCE_STATUSES = new Set([
  "sufficient",
  "partial",
  "insufficient",
  "not_evaluated",
]);
const TERMINAL_RUN_STATUSES = new Set(["completed", "interrupted", "failed"]);
const TRACE_STATUSES = new Set(["started", "completed", "failed", "skipped"]);
const ANSWER_BLOCK_TYPES = new Set([
  "repository",
  "user_material",
  "general",
  "personalized_analysis",
]);
const LOCATOR_TYPES = new Set(["page", "slide", "heading", "question", "none"]);

const TRACE_RESULT_FIELDS = new Set<keyof TraceSafeResult>([
  "workflow_type",
  "course_scope",
  "course_ids",
  "knowledge_scope",
  "auth_mode",
  "agent_preset_id",
  "agent_preset_version",
  "mode",
  "hit_count",
  "sources",
  "rewritten_query",
  "candidate_order",
  "reranked_order",
  "evidence_status",
  "used_general_knowledge",
  "model_source",
  "provider_id",
  "model_id",
  "billing_label",
  "availability_status",
  "real_model_called",
  "cache_hit",
  "retry_count",
  "failure_code",
  "degradation_code",
  "catalog_version",
  "fixture_only",
  "normalized_topics",
  "unreviewed_search_returned",
  "review_path",
  "sample_years",
  "reason_code",
  "candidate_count",
  "accepted_count",
  "external_resources_separate",
  "stored",
  "adapter",
]);
const TRACE_EVENT_FIELDS = new Set([
  "event_id",
  "sequence",
  "node",
  "status",
  "duration_ms",
  "result",
]);
const TRACE_SOURCE_FIELDS = new Set(["course_id", "title", "locator"]);
const ANSWER_BLOCK_FIELDS = new Set(["type", "content"]);
const CITATION_FIELDS = new Set([
  "citation_id",
  "chunk_id",
  "course_id",
  "course_title",
  "source_id",
  "source_title",
  "locator_type",
  "locator_start",
  "locator_end",
  "question_id",
  "heading_path",
]);
const EXTERNAL_RESOURCE_FIELDS = new Set([
  "resource_id",
  "course_id",
  "platform",
  "resource_type",
  "title",
  "url",
  "matched_topic",
  "review_status",
  "catalog_version",
  "query_keywords",
  "generated_at",
  "evidence_role",
]);
const MODEL_FIELDS = new Set(["provider_id", "model_id", "billing_label", "mock_only"]);
const WORKFLOW_RESULT_FIELDS = new Set([
  "workflow_run_id",
  "conversation_id",
  "message_id",
  "answer_id",
  "run_status",
  "answer_status",
  "workflow_type",
  "course_scope",
  "course_ids",
  "repository_answer",
  "general_supplement",
  "answer_blocks",
  "workflow_output",
  "evidence_status",
  "citations",
  "related_topics",
  "related_questions",
  "external_resources",
  "trace",
  "coverage_gaps",
  "corpus_version",
  "course_pack_version",
  "workflow_version",
  "model_source",
  "model",
  "availability_status",
]);
const WORKFLOW_ATTEMPT_FIELDS = new Set([
  "workflow_run_id",
  "attempt_group_id",
  "regenerated_from_run_id",
  "request",
  "result",
  "created_at",
  "updated_at",
  "expires_at",
]);
const CONVERSATION_DETAIL_FIELDS = new Set([
  "conversation_id",
  "user_id",
  "course_id",
  "title",
  "created_at",
  "updated_at",
  "expires_at",
  "mock_only",
  "runs",
]);

export class WorkflowStreamProtocolError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "WorkflowStreamProtocolError";
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function hasOwn(value: Record<string, unknown>, key: string): boolean {
  return Object.prototype.hasOwnProperty.call(value, key);
}

function assertOnlyKeys(
  value: Record<string, unknown>,
  allowed: ReadonlySet<string>,
  label: string,
): void {
  const unknown = Object.keys(value).find((key) => !allowed.has(key));
  if (unknown) throw new WorkflowStreamProtocolError(`unknown ${label} field: ${unknown}`);
}

function assertRequiredKeys(
  value: Record<string, unknown>,
  required: ReadonlySet<string>,
  label: string,
): void {
  const missing = [...required].find((key) => !hasOwn(value, key));
  if (missing) throw new WorkflowStreamProtocolError(`missing ${label} field: ${missing}`);
}

function assertString(value: unknown, label: string): asserts value is string {
  if (typeof value !== "string") {
    throw new WorkflowStreamProtocolError(`invalid ${label}`);
  }
}

function assertNullableString(value: unknown, label: string): void {
  if (value !== null && typeof value !== "string") {
    throw new WorkflowStreamProtocolError(`invalid ${label}`);
  }
}

function assertStringArray(value: unknown, label: string): asserts value is string[] {
  if (!Array.isArray(value) || !value.every((item) => typeof item === "string")) {
    throw new WorkflowStreamProtocolError(`invalid ${label}`);
  }
}

function assertEnum(value: unknown, allowed: ReadonlySet<string>, label: string): void {
  if (typeof value !== "string" || !allowed.has(value)) {
    throw new WorkflowStreamProtocolError(`invalid ${label}`);
  }
}

function assertNullableEnum(
  value: unknown,
  allowed: ReadonlySet<string>,
  label: string,
): void {
  if (value !== null && (typeof value !== "string" || !allowed.has(value))) {
    throw new WorkflowStreamProtocolError(`invalid ${label}`);
  }
}

function assertNonNegativeInteger(value: unknown, label: string): void {
  if (typeof value !== "number" || !Number.isInteger(value) || value < 0) {
    throw new WorkflowStreamProtocolError(`invalid ${label}`);
  }
}

function assertNullableStringArray(value: unknown, label: string): void {
  if (value !== null) assertStringArray(value, label);
}

function assertTraceResult(value: unknown): asserts value is TraceSafeResult {
  if (!isRecord(value)) throw new WorkflowStreamProtocolError("invalid Trace result");
  assertOnlyKeys(value, TRACE_RESULT_FIELDS, "Trace result");

  const enumFields: Array<[keyof TraceSafeResult, ReadonlySet<string>]> = [
    ["workflow_type", WORKFLOW_TYPES],
    ["course_scope", COURSE_SCOPES],
    ["knowledge_scope", KNOWLEDGE_SCOPES],
    ["auth_mode", new Set(["mock", "github_oauth"])],
    ["mode", new Set(["mock", "synthetic_fixture_only"])],
    ["evidence_status", EVIDENCE_STATUSES],
    ["model_source", MODEL_SOURCES],
    ["adapter", new Set(["sqlite_mock", "sqlite"])],
  ];
  for (const [field, allowed] of enumFields) {
    if (hasOwn(value, field)) assertNullableEnum(value[field], allowed, `Trace ${field}`);
  }

  const stringFields: Array<keyof TraceSafeResult> = [
    "rewritten_query",
    "provider_id",
    "model_id",
    "catalog_version",
    "agent_preset_id",
    "agent_preset_version",
  ];
  for (const field of stringFields) {
    if (hasOwn(value, field)) assertNullableString(value[field], `Trace ${field}`);
  }

  const codeFields: Array<keyof TraceSafeResult> = [
    "billing_label",
    "availability_status",
    "failure_code",
    "degradation_code",
    "review_path",
    "reason_code",
  ];
  for (const field of codeFields) {
    const fieldValue = value[field];
    if (hasOwn(value, field) && fieldValue !== null
      && (typeof fieldValue !== "string" || !ERROR_CODE_PATTERN.test(fieldValue))) {
      throw new WorkflowStreamProtocolError(`invalid Trace ${field}`);
    }
  }

  const arrayFields: Array<keyof TraceSafeResult> = [
    "course_ids",
    "candidate_order",
    "reranked_order",
    "normalized_topics",
  ];
  for (const field of arrayFields) {
    if (hasOwn(value, field)) assertNullableStringArray(value[field], `Trace ${field}`);
  }

  const booleanFields: Array<keyof TraceSafeResult> = [
    "used_general_knowledge",
    "real_model_called",
    "cache_hit",
    "fixture_only",
    "unreviewed_search_returned",
    "external_resources_separate",
    "stored",
  ];
  for (const field of booleanFields) {
    const fieldValue = value[field];
    if (hasOwn(value, field) && fieldValue !== null && typeof fieldValue !== "boolean") {
      throw new WorkflowStreamProtocolError(`invalid Trace ${field}`);
    }
  }

  const integerFields: Array<keyof TraceSafeResult> = [
    "hit_count",
    "retry_count",
    "candidate_count",
    "accepted_count",
  ];
  for (const field of integerFields) {
    const fieldValue = value[field];
    if (hasOwn(value, field) && fieldValue !== null) {
      assertNonNegativeInteger(fieldValue, `Trace ${field}`);
    }
  }

  // Iteration 5: objective past-exam sample years (positive integers).
  if (hasOwn(value, "sample_years") && value.sample_years !== null) {
    const years = value.sample_years;
    if (!Array.isArray(years)) {
      throw new WorkflowStreamProtocolError("invalid Trace sample_years");
    }
    for (const year of years) {
      assertNonNegativeInteger(year, "Trace sample_years");
      if (year < 1) throw new WorkflowStreamProtocolError("invalid Trace sample_years");
    }
  }

  if (hasOwn(value, "sources") && value.sources !== null) {
    if (!Array.isArray(value.sources)) {
      throw new WorkflowStreamProtocolError("invalid Trace sources");
    }
    for (const source of value.sources) {
      if (!isRecord(source)) throw new WorkflowStreamProtocolError("invalid Trace source");
      assertOnlyKeys(source, TRACE_SOURCE_FIELDS, "Trace source");
      if (!hasOwn(source, "course_id") || !hasOwn(source, "title")) {
        throw new WorkflowStreamProtocolError("missing Trace source identity");
      }
      assertString(source.course_id, "Trace source course_id");
      assertString(source.title, "Trace source title");
      if (hasOwn(source, "locator") && source.locator !== null
        && typeof source.locator !== "string"
        && (typeof source.locator !== "number" || !Number.isInteger(source.locator))) {
        throw new WorkflowStreamProtocolError("invalid Trace source locator");
      }
    }
  }
}

export function validateTraceEvent(value: unknown): TraceEvent {
  if (!isRecord(value)) throw new WorkflowStreamProtocolError("invalid Trace event");
  assertOnlyKeys(value, TRACE_EVENT_FIELDS, "Trace event");
  assertRequiredKeys(value, TRACE_EVENT_FIELDS, "Trace event");
  if (typeof value.event_id !== "string" || !value.event_id
    || typeof value.node !== "string" || !ERROR_CODE_PATTERN.test(value.node)) {
    throw new WorkflowStreamProtocolError("invalid Trace event identity");
  }
  assertNonNegativeInteger(value.sequence, "Trace event sequence");
  assertEnum(value.status, TRACE_STATUSES, "Trace event status");
  assertNonNegativeInteger(value.duration_ms, "Trace event duration");
  assertTraceResult(value.result);
  return value as unknown as TraceEvent;
}

function validateAnswerBlocks(value: unknown): void {
  if (!Array.isArray(value)) throw new WorkflowStreamProtocolError("invalid result answer blocks");
  for (const block of value) {
    if (!isRecord(block)) throw new WorkflowStreamProtocolError("invalid result answer block");
    assertOnlyKeys(block, ANSWER_BLOCK_FIELDS, "answer block");
    assertRequiredKeys(block, ANSWER_BLOCK_FIELDS, "answer block");
    assertEnum(block.type, ANSWER_BLOCK_TYPES, "answer block type");
    assertString(block.content, "answer block content");
  }
}

function validateCitation(value: unknown, courseIds: ReadonlySet<string>): Citation {
  if (!isRecord(value)) throw new WorkflowStreamProtocolError("invalid result citation");
  assertOnlyKeys(value, CITATION_FIELDS, "citation");
  for (const field of [
    "citation_id",
    "chunk_id",
    "course_id",
    "course_title",
    "source_id",
    "source_title",
    "locator_type",
  ]) {
    if (!hasOwn(value, field)) {
      throw new WorkflowStreamProtocolError(`missing citation field: ${field}`);
    }
  }
  for (const field of [
    "citation_id",
    "chunk_id",
    "course_id",
    "course_title",
    "source_id",
    "source_title",
  ]) {
    assertString(value[field], `citation ${field}`);
  }
  assertEnum(value.locator_type, LOCATOR_TYPES, "citation locator_type");
  if (!courseIds.has(value.course_id as string)) {
    throw new WorkflowStreamProtocolError("citation belongs to another course");
  }

  for (const field of ["locator_start", "locator_end"] as const) {
    const locator = value[field];
    if (hasOwn(value, field) && locator !== null && typeof locator !== "string"
      && (typeof locator !== "number" || !Number.isInteger(locator))) {
      throw new WorkflowStreamProtocolError(`invalid citation ${field}`);
    }
  }
  if (hasOwn(value, "question_id")) {
    assertNullableString(value.question_id, "citation question_id");
  }
  if (hasOwn(value, "heading_path")) {
    assertStringArray(value.heading_path, "citation heading_path");
    if (value.heading_path.some((heading) => !heading.trim())) {
      throw new WorkflowStreamProtocolError("citation heading_path entries must be non-empty");
    }
  }

  const start = value.locator_start;
  const end = value.locator_end;
  if (end !== undefined && end !== null && (start === undefined || start === null)) {
    throw new WorkflowStreamProtocolError("citation locator_end requires locator_start");
  }
  if (value.locator_type === "none") {
    if ((start !== undefined && start !== null) || (end !== undefined && end !== null)
      || (value.question_id !== undefined && value.question_id !== null)
      || (Array.isArray(value.heading_path) && value.heading_path.length > 0)) {
      throw new WorkflowStreamProtocolError("locator_type=none forbids precise locator metadata");
    }
  } else if (value.locator_type === "page" || value.locator_type === "slide") {
    if (typeof start !== "number" || !Number.isInteger(start) || start < 1
      || (end !== undefined && end !== null
        && (typeof end !== "number" || !Number.isInteger(end) || end < start))) {
      throw new WorkflowStreamProtocolError("invalid page or slide citation locator");
    }
  } else if (value.locator_type === "heading") {
    const hasStart = typeof start === "string" && Boolean(start.trim());
    const hasPath = Array.isArray(value.heading_path) && value.heading_path.length > 0;
    if (!hasStart && !hasPath) {
      throw new WorkflowStreamProtocolError("heading citation requires a heading");
    }
  } else if (value.locator_type === "question") {
    const hasStart = typeof start === "string" && Boolean(start.trim());
    const hasQuestion = typeof value.question_id === "string" && Boolean(value.question_id.trim());
    if (!hasStart && !hasQuestion) {
      throw new WorkflowStreamProtocolError("question citation requires an identifier");
    }
  }
  return value as unknown as Citation;
}

function validateExternalResources(
  value: unknown,
  courseIds: ReadonlySet<string>,
): ExternalResource[] {
  if (!Array.isArray(value) || value.length > 1) {
    throw new WorkflowStreamProtocolError("invalid external resources");
  }
  for (const resource of value) {
    if (!isRecord(resource)) {
      throw new WorkflowStreamProtocolError("invalid Bilibili search resource");
    }
    assertOnlyKeys(resource, EXTERNAL_RESOURCE_FIELDS, "external resource");
    assertRequiredKeys(resource, EXTERNAL_RESOURCE_FIELDS, "external resource");
    if (resource.resource_id !== null
      || resource.catalog_version !== null
      || resource.platform !== "bilibili"
      || resource.resource_type !== "search"
      || resource.review_status !== "unreviewed_live_search"
      || resource.evidence_role !== "supplementary_only") {
      throw new WorkflowStreamProtocolError("invalid Bilibili search resource");
    }
    for (const field of ["course_id", "title", "url", "matched_topic", "generated_at"]) {
      assertString(resource[field], `external resource ${field}`);
    }
    if (!courseIds.has(resource.course_id as string)) {
      throw new WorkflowStreamProtocolError("external resource belongs to another course");
    }
    assertStringArray(resource.query_keywords, "external resource query_keywords");
    if (resource.query_keywords.length < 1 || resource.query_keywords.length > 3
      || resource.query_keywords.some((keyword) => !keyword || keyword.length > 32)) {
      throw new WorkflowStreamProtocolError("invalid Bilibili search keywords");
    }
    if (!/(?:Z|[+-]\d{2}:\d{2})$/.test(resource.generated_at as string)
      || Number.isNaN(Date.parse(resource.generated_at as string))) {
      throw new WorkflowStreamProtocolError("invalid external resource generated_at");
    }

    let url: URL;
    try {
      url = new URL(resource.url as string);
    } catch {
      throw new WorkflowStreamProtocolError("invalid Bilibili search URL");
    }
    const queryKeys = [...url.searchParams.keys()];
    if (url.protocol !== "https:"
      || url.hostname !== "search.bilibili.com"
      || url.username
      || url.password
      || url.port
      || url.pathname !== "/all"
      || url.hash
      || queryKeys.length !== 1
      || queryKeys[0] !== "keyword"
      || url.searchParams.get("keyword") !== resource.query_keywords.join(" ")) {
      throw new WorkflowStreamProtocolError(
        "Bilibili resource is not a fixed anonymous search URL",
      );
    }
  }
  return value as ExternalResource[];
}

export function validateWorkflowRunResult(
  value: unknown,
  options: { expectedRunId?: string; expectedConversationId?: string } = {},
): WorkflowRunResult {
  if (!isRecord(value)) throw new WorkflowStreamProtocolError("invalid Workflow result");
  assertOnlyKeys(value, WORKFLOW_RESULT_FIELDS, "Workflow result");
  assertRequiredKeys(value, WORKFLOW_RESULT_FIELDS, "Workflow result");

  for (const field of [
    "workflow_run_id",
    "conversation_id",
    "message_id",
    "answer_id",
    "corpus_version",
    "workflow_version",
    "availability_status",
  ]) {
    assertString(value[field], `Workflow result ${field}`);
  }
  if (options.expectedRunId !== undefined && value.workflow_run_id !== options.expectedRunId) {
    throw new WorkflowStreamProtocolError("stream result belongs to another run");
  }
  if (options.expectedConversationId !== undefined
    && value.conversation_id !== options.expectedConversationId) {
    throw new WorkflowStreamProtocolError("Workflow result belongs to another conversation");
  }
  assertEnum(value.run_status, TERMINAL_RUN_STATUSES, "Workflow result run_status");
  assertEnum(value.answer_status, ANSWER_STATUSES, "Workflow result answer_status");
  assertEnum(value.workflow_type, WORKFLOW_TYPES, "Workflow result workflow_type");
  assertEnum(value.course_scope, COURSE_SCOPES, "Workflow result course_scope");
  assertStringArray(value.course_ids, "Workflow result course_ids");
  assertNullableString(value.repository_answer, "Workflow result repository_answer");
  assertNullableString(value.general_supplement, "Workflow result general_supplement");
  assertNullableString(value.course_pack_version, "Workflow result course_pack_version");
  validateAnswerBlocks(value.answer_blocks);
  if (!isRecord(value.workflow_output)) {
    throw new WorkflowStreamProtocolError("invalid Workflow result workflow_output");
  }
  assertEnum(value.evidence_status, EVIDENCE_STATUSES, "Workflow result evidence_status");
  assertEnum(value.model_source, MODEL_SOURCES, "Workflow result model_source");

  const courseIds = new Set(value.course_ids);
  if (!Array.isArray(value.citations)) {
    throw new WorkflowStreamProtocolError("invalid result citations");
  }
  const citationIds = new Set<string>();
  for (const rawCitation of value.citations) {
    const citation = validateCitation(rawCitation, courseIds);
    if (citationIds.has(citation.citation_id)) {
      throw new WorkflowStreamProtocolError("duplicate result citation id");
    }
    citationIds.add(citation.citation_id);
  }

  for (const field of ["related_topics", "related_questions", "coverage_gaps"]) {
    assertStringArray(value[field], `Workflow result ${field}`);
  }
  validateExternalResources(value.external_resources, courseIds);

  if (!Array.isArray(value.trace)) throw new WorkflowStreamProtocolError("invalid result Trace");
  const traceIds = new Set<string>();
  value.trace.forEach((rawEvent, index) => {
    const event = validateTraceEvent(rawEvent);
    if (event.sequence !== index) {
      throw new WorkflowStreamProtocolError("result Trace sequence is not contiguous");
    }
    if (traceIds.has(event.event_id)) {
      throw new WorkflowStreamProtocolError("duplicate result Trace event id");
    }
    traceIds.add(event.event_id);
  });

  if (!isRecord(value.model)) throw new WorkflowStreamProtocolError("invalid result model");
  assertOnlyKeys(value.model, MODEL_FIELDS, "model metadata");
  assertRequiredKeys(value.model, MODEL_FIELDS, "model metadata");
  assertString(value.model.provider_id, "model provider_id");
  assertString(value.model.model_id, "model model_id");
  assertString(value.model.billing_label, "model billing_label");
  if (typeof value.model.mock_only !== "boolean") {
    throw new WorkflowStreamProtocolError("invalid model mock_only");
  }
  return value as unknown as WorkflowRunResult;
}

function assertTimestamp(value: unknown, label: string): void {
  if (typeof value !== "string" || Number.isNaN(Date.parse(value))) {
    throw new WorkflowStreamProtocolError(`invalid ${label}`);
  }
}

export function validateWorkflowAttempt(
  value: unknown,
  options: {
    expectedConversationId?: string;
    expectedRunId?: string;
    expectedRegeneratedFromRunId?: string;
  } = {},
): WorkflowAttempt {
  if (!isRecord(value)) throw new WorkflowStreamProtocolError("invalid Workflow attempt");
  assertOnlyKeys(value, WORKFLOW_ATTEMPT_FIELDS, "Workflow attempt");
  assertRequiredKeys(value, WORKFLOW_ATTEMPT_FIELDS, "Workflow attempt");
  assertString(value.workflow_run_id, "Workflow attempt workflow_run_id");
  assertString(value.attempt_group_id, "Workflow attempt attempt_group_id");
  assertNullableString(value.regenerated_from_run_id, "Workflow attempt regenerated_from_run_id");
  if (options.expectedRunId !== undefined && value.workflow_run_id !== options.expectedRunId) {
    throw new WorkflowStreamProtocolError("Workflow attempt belongs to another run");
  }
  if (options.expectedRegeneratedFromRunId !== undefined
    && value.regenerated_from_run_id !== options.expectedRegeneratedFromRunId) {
    throw new WorkflowStreamProtocolError("regenerated attempt does not reference requested run");
  }
  if (value.regenerated_from_run_id === value.workflow_run_id) {
    throw new WorkflowStreamProtocolError("Workflow attempt cannot regenerate itself");
  }
  if (!isRecord(value.request) || typeof value.request.conversation_id !== "string") {
    throw new WorkflowStreamProtocolError("invalid Workflow attempt request");
  }
  const expectedConversationId = options.expectedConversationId ?? value.request.conversation_id;
  if (value.request.conversation_id !== expectedConversationId) {
    throw new WorkflowStreamProtocolError("Workflow attempt request belongs to another conversation");
  }
  validateWorkflowRunResult(value.result, {
    expectedRunId: value.workflow_run_id,
    expectedConversationId,
  });
  assertTimestamp(value.created_at, "Workflow attempt created_at");
  assertTimestamp(value.updated_at, "Workflow attempt updated_at");
  assertTimestamp(value.expires_at, "Workflow attempt expires_at");
  if (Date.parse(value.updated_at as string) < Date.parse(value.created_at as string)
    || Date.parse(value.expires_at as string) <= Date.parse(value.created_at as string)) {
    throw new WorkflowStreamProtocolError("invalid Workflow attempt timestamp order");
  }
  return value as unknown as WorkflowAttempt;
}

export function validateConversationDetail(
  value: unknown,
  expectedConversationId?: string,
): ConversationDetail {
  if (!isRecord(value)) throw new WorkflowStreamProtocolError("invalid conversation history");
  assertOnlyKeys(value, CONVERSATION_DETAIL_FIELDS, "conversation history");
  assertRequiredKeys(value, CONVERSATION_DETAIL_FIELDS, "conversation history");
  for (const field of ["conversation_id", "user_id", "course_id", "title"]) {
    assertString(value[field], `conversation ${field}`);
  }
  if (expectedConversationId !== undefined && value.conversation_id !== expectedConversationId) {
    throw new WorkflowStreamProtocolError("history response belongs to another conversation");
  }
  assertTimestamp(value.created_at, "conversation created_at");
  assertTimestamp(value.updated_at, "conversation updated_at");
  assertTimestamp(value.expires_at, "conversation expires_at");
  if (typeof value.mock_only !== "boolean" || !Array.isArray(value.runs)) {
    throw new WorkflowStreamProtocolError("invalid conversation history metadata");
  }
  const runIds = new Set<string>();
  const runs: unknown[] = [];
  for (const rawAttempt of value.runs) {
    // 历史详情可能瞬时包含非终态尝试（运行中/崩溃残留的 running/created）：
    // 它们不是合格结果，跳过而不是让整个会话加载失败；终态出现后自会补齐。
    if (
      isRecord(rawAttempt) &&
      isRecord(rawAttempt.result) &&
      typeof rawAttempt.result.run_status === "string" &&
      !TERMINAL_RUN_STATUSES.has(rawAttempt.result.run_status)
    ) {
      continue;
    }
    const attempt = validateWorkflowAttempt(rawAttempt, {
      expectedConversationId: value.conversation_id as string,
    });
    if (runIds.has(attempt.workflow_run_id)) {
      throw new WorkflowStreamProtocolError("duplicate Workflow attempt in history");
    }
    runIds.add(attempt.workflow_run_id);
    runs.push(attempt);
  }
  return { ...value, runs } as unknown as ConversationDetail;
}

export function selectConversationAttempt(
  conversation: ConversationDetail,
  preferredAttemptId = "",
): WorkflowAttempt | undefined {
  if (!preferredAttemptId) return conversation.runs[conversation.runs.length - 1];
  const preferredAttempt = conversation.runs.find(
    (attempt) => attempt.workflow_run_id === preferredAttemptId,
  );
  if (!preferredAttempt) {
    throw new WorkflowStreamProtocolError(
      `历史响应未包含刚完成的运行 ${preferredAttemptId}，已保留当前结果。`,
    );
  }
  return preferredAttempt;
}
