import type {
  AuthUser,
  ByokCredentialStatus,
  ByokProviderId,
  ConversationDetail,
  ConversationSummary,
  Course,
  FeedbackRecord,
  FeedbackType,
  ModelCatalog,
  WorkflowAttempt,
  WorkflowRunRequest,
  WorkflowRunResult,
} from "./contracts";
import {
  startWorkflowStreamRequest,
  type WorkflowStreamHandle,
  type WorkflowStreamState,
} from "./workflowStream";
import {
  validateConversationDetail,
  validateWorkflowAttempt,
  validateWorkflowRunResult,
} from "./workflowResultValidation";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code: string | null = null,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set("Accept", "application/json");
  if (init?.body) headers.set("Content-Type", "application/json");

  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    let detail = `请求失败 (${response.status})`;
    let code: string | null = null;
    try {
      const body = (await response.json()) as {
        detail?: string;
        message?: string;
        error?: { code?: string; detail?: string };
      };
      detail = body.error?.detail || body.detail || body.message || detail;
      code = body.error?.code ?? null;
    } catch {
      // Preserve the status-based message when an error body is not JSON.
    }
    throw new ApiError(detail, response.status, code);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export function githubLoginUrl(): string {
  return `${API_BASE}/api/v1/auth/github/start`;
}

export async function getMe(): Promise<AuthUser> {
  return apiRequest<AuthUser>("/api/v1/me");
}

export async function logout(): Promise<void> {
  await apiRequest<Record<string, never>>("/api/v1/auth/logout", {
    method: "POST",
  });
}

export async function getCourses(): Promise<Course[]> {
  const body = await apiRequest<Course[] | { courses: Course[] }>("/api/v1/courses");
  return Array.isArray(body) ? body : body.courses;
}

export async function getModels(): Promise<ModelCatalog> {
  return apiRequest<ModelCatalog>("/api/v1/models");
}

export async function getByokCredentials(): Promise<ByokCredentialStatus[]> {
  return apiRequest<ByokCredentialStatus[]>("/api/v1/model-credentials");
}

export async function saveByokCredential(
  providerId: ByokProviderId,
  apiKey: string,
): Promise<ByokCredentialStatus> {
  return apiRequest<ByokCredentialStatus>(
    `/api/v1/model-credentials/${encodeURIComponent(providerId)}`,
    {
      method: "PUT",
      body: JSON.stringify({ api_key: apiKey }),
    },
  );
}

export async function deleteByokCredential(providerId: ByokProviderId): Promise<void> {
  await apiRequest<void>(`/api/v1/model-credentials/${encodeURIComponent(providerId)}`, {
    method: "DELETE",
  });
}

export async function createConversation(courseId: string): Promise<ConversationSummary> {
  return apiRequest<ConversationSummary>("/api/v1/conversations", {
    method: "POST",
    body: JSON.stringify({ course_id: courseId }),
  });
}

export async function listConversations(): Promise<ConversationSummary[]> {
  return apiRequest<ConversationSummary[]>("/api/v1/conversations");
}

export async function runWorkflow(
  request: WorkflowRunRequest,
): Promise<WorkflowRunResult> {
  const result = await apiRequest<unknown>("/api/v1/workflow-runs", {
    method: "POST",
    body: JSON.stringify(request),
  });
  return validateWorkflowRunResult(result, {
    expectedConversationId: request.conversation_id,
  });
}

export function startWorkflowRunStream(
  request: WorkflowRunRequest,
  onState?: (state: WorkflowStreamState) => void,
): WorkflowStreamHandle {
  return startWorkflowStreamRequest(
    `${API_BASE}/api/v1/workflow-runs/stream`,
    {
      method: "POST",
      headers: {
        Accept: "application/x-ndjson",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
      credentials: "include",
    },
    {
      onEvent: (_event, state) => onState?.(state),
      expectedConversationId: request.conversation_id,
    },
  );
}

export async function getConversation(conversationId: string): Promise<ConversationDetail> {
  const conversation = await apiRequest<unknown>(
    `/api/v1/conversations/${encodeURIComponent(conversationId)}`,
  );
  return validateConversationDetail(conversation, conversationId);
}

export async function renameConversation(
  conversationId: string,
  title: string,
): Promise<ConversationSummary> {
  return apiRequest<ConversationSummary>(
    `/api/v1/conversations/${encodeURIComponent(conversationId)}`,
    {
      method: "PATCH",
      body: JSON.stringify({ title }),
    },
  );
}

export async function deleteConversation(conversationId: string): Promise<void> {
  await apiRequest<void>(`/api/v1/conversations/${encodeURIComponent(conversationId)}`, {
    method: "DELETE",
  });
}

export async function regenerateWorkflowRun(workflowRunId: string): Promise<WorkflowAttempt> {
  const attempt = await apiRequest<unknown>(
    `/api/v1/workflow-runs/${encodeURIComponent(workflowRunId)}/regenerate`,
    { method: "POST" },
  );
  return validateWorkflowAttempt(attempt, {
    expectedRegeneratedFromRunId: workflowRunId,
  });
}

export async function getWorkflowRun(workflowRunId: string): Promise<WorkflowRunResult> {
  const result = await apiRequest<unknown>(
    `/api/v1/workflow-runs/${encodeURIComponent(workflowRunId)}`,
  );
  return validateWorkflowRunResult(result, { expectedRunId: workflowRunId });
}

export async function submitFeedback(
  runId: string,
  feedbackType: FeedbackType,
  note?: string,
): Promise<FeedbackRecord> {
  return apiRequest<FeedbackRecord>("/api/v1/feedback", {
    method: "POST",
    body: JSON.stringify({ run_id: runId, feedback_type: feedbackType, note: note || null }),
  });
}
