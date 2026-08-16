import type {
  Conversation,
  Course,
  WorkflowRunRequest,
  WorkflowRunResult,
} from "./contracts";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
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
  });

  if (!response.ok) {
    let detail = `请求失败 (${response.status})`;
    try {
      const body = (await response.json()) as {
        detail?: string;
        message?: string;
        error?: { detail?: string };
      };
      detail = body.error?.detail || body.detail || body.message || detail;
    } catch {
      // Preserve the status-based message when an error body is not JSON.
    }
    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as T;
}

export async function getCourses(): Promise<Course[]> {
  const body = await apiRequest<Course[] | { courses: Course[] }>("/api/v1/courses");
  return Array.isArray(body) ? body : body.courses;
}

export async function createConversation(courseId: string): Promise<Conversation> {
  return apiRequest<Conversation>("/api/v1/conversations", {
    method: "POST",
    body: JSON.stringify({ course_id: courseId }),
  });
}

export async function runWorkflow(
  request: WorkflowRunRequest,
): Promise<WorkflowRunResult> {
  return apiRequest<WorkflowRunResult>("/api/v1/workflow-runs", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function getConversation(conversationId: string): Promise<Conversation> {
  return apiRequest<Conversation>(`/api/v1/conversations/${encodeURIComponent(conversationId)}`);
}

export async function getWorkflowRun(workflowRunId: string): Promise<WorkflowRunResult> {
  return apiRequest<WorkflowRunResult>(
    `/api/v1/workflow-runs/${encodeURIComponent(workflowRunId)}`,
  );
}
