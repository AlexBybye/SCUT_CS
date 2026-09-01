import type {
  AuthUser,
  ByokCredentialStatus,
  ByokProviderId,
  ContributionConfirmations,
  ContributionPreview,
  ContributionRecord,
  MaintainerContributionDetail,
  ConversationDetail,
  ConversationSummary,
  CourseCatalog,
  FeedbackRecord,
  FeedbackType,
  ModelCatalog,
  PluginRegistry,
  TemporaryMaterialDetail,
  TemporaryMaterialRecord,
  WorkflowAttempt,
  WorkflowRunRequest,
  WorkflowRunResult,
} from "./contracts";

export interface ExamReviewPlanPreview {
  confirmation_required: true;
  plan: Record<string, unknown>;
  retrieval_query: string;
}
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

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers,
      credentials: "include",
    });
  } catch {
    // 网络层失败（断网/隧道中断）：不把浏览器英文原文（Failed to fetch）
    // 抛给上层，统一转成可行动的中文 ApiError。
    throw new ApiError(
      "网络连接失败，请检查网络后重试；已提交的运行若在服务端继续，稍后重新读取即可看到结果。",
      0,
      "network_error",
    );
  }

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

export async function getCourses(): Promise<CourseCatalog> {
  return apiRequest<CourseCatalog>("/api/v1/courses");
}

export async function getModels(): Promise<ModelCatalog> {
  return apiRequest<ModelCatalog>("/api/v1/models");
}

export async function getPluginRegistry(): Promise<PluginRegistry> {
  return apiRequest<PluginRegistry>("/api/v1/plugin-registry");
}

export async function loadCoursePlugin(courseId: string): Promise<{ course_id: string; loaded: boolean }> {
  return apiRequest<{ course_id: string; loaded: boolean }>(
    `/api/v1/plugin-registry/courses/${encodeURIComponent(courseId)}/load`,
    { method: "POST" },
  );
}

export async function unloadCoursePlugin(courseId: string): Promise<{ course_id: string; loaded: boolean }> {
  return apiRequest<{ course_id: string; loaded: boolean }>(
    `/api/v1/plugin-registry/courses/${encodeURIComponent(courseId)}/unload`,
    { method: "POST" },
  );
}

export async function getAccountPreferences(): Promise<{ preferences: Record<string, string> }> {
  return apiRequest<{ preferences: Record<string, string> }>("/api/v1/account/preferences");
}

export async function saveAccountPreferences(
  preferences: Record<string, string>,
): Promise<{ preferences: Record<string, string> }> {
  return apiRequest<{ preferences: Record<string, string> }>("/api/v1/account/preferences", {
    method: "PUT",
    body: JSON.stringify({ preferences }),
  });
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

export async function previewExamReviewPlan(
  request: WorkflowRunRequest,
): Promise<ExamReviewPlanPreview> {
  return apiRequest<ExamReviewPlanPreview>("/api/v1/exam-review/plan/preview", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function recordExamReviewPlanDecision(
  conversationId: string,
  decision: "confirmed" | "edited" | "rejected",
  plan: Record<string, unknown>,
): Promise<void> {
  await apiRequest<void>("/api/v1/exam-review/plan/decision", {
    method: "POST",
    body: JSON.stringify({ conversation_id: conversationId, decision, plan }),
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

/** 显式取消一次正在流式运行的 workflow（与网络断开相区分）。 */
export async function cancelWorkflowRun(workflowRunId: string): Promise<void> {
  await apiRequest<unknown>(
    `/api/v1/workflow-runs/${encodeURIComponent(workflowRunId)}/cancel`,
    { method: "POST" },
  );
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

// ---------------------------------------------------------------------------
// 迭代 7（SOP §12）：临时材料精读治理与贡献待处理队列。
// ---------------------------------------------------------------------------

export async function saveTemporaryMaterial(payload: {
  conversation_id: string;
  course_id: string;
  title?: string | null;
  content: string;
}): Promise<TemporaryMaterialRecord> {
  return apiRequest<TemporaryMaterialRecord>("/api/v1/temporary-materials", {
    method: "POST",
    body: JSON.stringify({
      conversation_id: payload.conversation_id,
      course_id: payload.course_id,
      title: payload.title || null,
      content: payload.content,
    }),
  });
}

export async function listTemporaryMaterials(): Promise<TemporaryMaterialRecord[]> {
  return apiRequest<TemporaryMaterialRecord[]>("/api/v1/temporary-materials");
}

export async function getTemporaryMaterial(
  materialId: string,
): Promise<TemporaryMaterialDetail> {
  return apiRequest<TemporaryMaterialDetail>(
    `/api/v1/temporary-materials/${encodeURIComponent(materialId)}`,
  );
}

export async function listMaintainerContributions(): Promise<ContributionRecord[]> {
  return apiRequest<ContributionRecord[]>("/api/v1/maintainer/contributions");
}

export async function getMaintainerContribution(contributionId: string): Promise<MaintainerContributionDetail> {
  return apiRequest<MaintainerContributionDetail>(`/api/v1/maintainer/contributions/${encodeURIComponent(contributionId)}`);
}

export async function listMaintainerFeedback(): Promise<FeedbackRecord[]> {
  return apiRequest<FeedbackRecord[]>("/api/v1/maintainer/feedback");
}

export async function transitionMaintainerContribution(
  contributionId: string,
  action: "mark_pr_open" | "merge" | "reject",
  note?: string,
  prUrl?: string,
): Promise<ContributionRecord> {
  return apiRequest<ContributionRecord>(
    `/api/v1/maintainer/contributions/${encodeURIComponent(contributionId)}/transition`,
    { method: "POST", body: JSON.stringify({ action, note: note || null, pr_url: prUrl || null }) },
  );
}

export async function exportMaintainerContribution(contributionId: string): Promise<unknown> {
  return apiRequest<unknown>(
    `/api/v1/maintainer/contributions/${encodeURIComponent(contributionId)}/export`,
  );
}

export async function savePrivateKnowledge(payload: {
  course_id: string;
  title?: string | null;
  content: string;
}): Promise<unknown> {
  return apiRequest<unknown>("/api/v1/private-knowledge", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function deleteTemporaryMaterial(materialId: string): Promise<void> {
  await apiRequest<void>(
    `/api/v1/temporary-materials/${encodeURIComponent(materialId)}`,
    { method: "DELETE" },
  );
}

export async function previewContribution(payload: {
  course_id: string;
  title?: string | null;
  content: string;
}): Promise<ContributionPreview> {
  return apiRequest<ContributionPreview>("/api/v1/contributions/preview", {
    method: "POST",
    body: JSON.stringify({
      course_id: payload.course_id,
      title: payload.title || null,
      content: payload.content,
    }),
  });
}

export async function submitContribution(payload: {
  material_id: string;
  course_id: string;
  title?: string | null;
  as_draft?: boolean;
  confirmations: ContributionConfirmations;
}): Promise<ContributionRecord> {
  return apiRequest<ContributionRecord>("/api/v1/contributions", {
    method: "POST",
    body: JSON.stringify({
      material_id: payload.material_id,
      course_id: payload.course_id,
      title: payload.title || null,
      as_draft: payload.as_draft ?? false,
      confirmations: payload.confirmations,
    }),
  });
}

export async function submitContributionDraft(
  contributionId: string,
  confirmations: ContributionConfirmations,
): Promise<ContributionRecord> {
  return apiRequest<ContributionRecord>(
    `/api/v1/contributions/${encodeURIComponent(contributionId)}/submit`,
    { method: "POST", body: JSON.stringify({ confirmations }) },
  );
}

export async function listContributions(): Promise<ContributionRecord[]> {
  return apiRequest<ContributionRecord[]>("/api/v1/contributions");
}

export async function getContribution(
  contributionId: string,
): Promise<ContributionRecord> {
  return apiRequest<ContributionRecord>(
    `/api/v1/contributions/${encodeURIComponent(contributionId)}`,
  );
}
