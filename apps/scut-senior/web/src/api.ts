import type {
  AuthUser,
  ByokCredentialStatus,
  ByokProviderId,
  ConversationDetail,
  ConversationSummary,
  Course,
  ModelCatalog,
  WorkflowAttempt,
  WorkflowRunRequest,
  WorkflowRunResult,
} from "./contracts";

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
  return apiRequest<WorkflowRunResult>("/api/v1/workflow-runs", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function getConversation(conversationId: string): Promise<ConversationDetail> {
  return apiRequest<ConversationDetail>(
    `/api/v1/conversations/${encodeURIComponent(conversationId)}`,
  );
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
  return apiRequest<WorkflowAttempt>(
    `/api/v1/workflow-runs/${encodeURIComponent(workflowRunId)}/regenerate`,
    { method: "POST" },
  );
}

export async function getWorkflowRun(workflowRunId: string): Promise<WorkflowRunResult> {
  return apiRequest<WorkflowRunResult>(
    `/api/v1/workflow-runs/${encodeURIComponent(workflowRunId)}`,
  );
}
