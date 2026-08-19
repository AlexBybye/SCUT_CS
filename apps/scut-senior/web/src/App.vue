<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import {
  ApiError,
  createConversation,
  deleteByokCredential,
  deleteConversation,
  getByokCredentials,
  getMe,
  getConversation,
  getCourses,
  getModels,
  githubLoginUrl,
  listConversations,
  logout,
  regenerateWorkflowRun,
  renameConversation,
  saveByokCredential,
  startWorkflowRunStream,
} from "./api";
import WorkflowResult from "./components/WorkflowResult.vue";
import {
  FROZEN_BYOK_PROVIDERS,
  isCurrentByokCatalogVersion,
  mergeByokProvidersForDisplay,
} from "./byokCatalog";
import { canManageByokCredentials } from "./byokSession";
import {
  ANSWER_MODES,
  HELP_LEVELS,
  TONES,
  WORKFLOW_TYPES,
  type AuthUser,
  type AnswerMode,
  type ByokCredentialStatus,
  type ByokProviderCatalogItem,
  type ByokProviderId,
  type ConversationDetail,
  type ConversationSummary,
  type Course,
  type HelpLevel,
  type KnowledgeScope,
  type ModelCatalog,
  type ModelCatalogItem,
  type Tone,
  type WorkflowAttempt,
  type WorkflowRunRequest,
  type WorkflowRunResult,
  type WorkflowType,
} from "./contracts";
import {
  configuredByokModelOptions,
  initialModelSelectionKey,
  modelKey,
  modelsForRuntime,
} from "./modelSelection";
import { createRequestEpoch } from "./requestEpoch";
import { buildWorkflowRequest } from "./workflowRequest";
import { selectConversationAttempt } from "./workflowResultValidation";
import {
  createInitialWorkflowStreamState,
  type WorkflowStreamHandle,
  type WorkflowStreamState,
} from "./workflowStream";

const ITERATION_ZERO_MOCK_MODEL: ModelCatalogItem = {
  provider_id: "mock",
  model_id: "deterministic-fixture-v1",
  company: "本地 Mock",
  display_name: "Deterministic Fixture V1",
  model_source: "platform_default",
  billing_label: "not_applicable_mock",
  availability_status: "mock_only",
  context_length: 0,
  input_modalities: ["text"],
  supports_structured_outputs: true,
  is_preview: false,
  user_selectable: true,
  last_checked_at: null,
};

const FAIL_CLOSED_MODEL_CATALOG: ModelCatalog = {
  catalog_version: "model-catalog-unavailable",
  platform_credential_configured: false,
  real_platform_default_available: false,
  health_checked_at: null,
  byok_available: false,
  byok_catalog_version: "byok-models-v4-fail-closed",
  byok_providers: FROZEN_BYOK_PROVIDERS,
  quota_notice: "模型目录尚未加载；平台与 BYOK 模型请求均保持关闭。",
  quota_exhausted_message:
    "今日平台免费额度已用完，第二天再来重试吧！着急请使用你自己的 API Key。",
  models: [],
};

function emptyByokKeyDrafts(): Record<ByokProviderId, string> {
  return { openrouter: "", deepseek: "", siliconflow: "", zhipu: "" };
}

const workflowCopy: Record<
  WorkflowType,
  { label: string; description: string; inputLabel: string; placeholder: string }
> = {
  knowledge_qa: {
    label: "知识答疑",
    description: "解释课程概念、原理、差异和常见误区。",
    inputLabel: "课程问题",
    placeholder: "例如：为什么矩阵可逆等价于行列式不为 0？",
  },
  exam_review: {
    label: "备考复习",
    description: "结合大纲、目标和薄弱点整理复习请求。",
    inputLabel: "复习请求",
    placeholder: "例如：请按剩余时间整理一份线性代数复习重点。",
  },
  problem_tutor: {
    label: "题目辅导",
    description: "按指定帮助层级分析文本题目。",
    inputLabel: "题干",
    placeholder: "粘贴题目文本。",
  },
  mistake_review: {
    label: "错题复盘",
    description: "定位错误原因并给出下次检查动作。",
    inputLabel: "原题",
    placeholder: "粘贴需要复盘的题目。",
  },
  temporary_material_reading: {
    label: "临时材料精读",
    description: "读取本次会话中的临时文本或 Markdown。",
    inputLabel: "临时材料",
    placeholder: "粘贴需要精读的文本或 Markdown。",
  },
};

const answerModeLabels: Record<AnswerMode, string> = {
  concise: "简短",
  detailed: "详细",
  example: "举例",
  step_by_step: "分步骤",
};

const toneLabels: Record<Tone, string> = {
  teaching_assistant: "助教式",
  study_partner: "复习搭子",
  senior_student: "学长聊天",
};

const helpLevelLabels: Record<HelpLevel, string> = {
  concept: "只讲知识点",
  approach: "给出思路",
  step_by_step: "分步骤提示",
  full_explanation: "完整讲解",
  answer_analysis: "分析我的答案",
};

const courses = ref<Course[]>([]);
const modelCatalog = ref<ModelCatalog>(FAIL_CLOSED_MODEL_CATALOG);
const modelCatalogLoadSucceeded = ref(false);
const selectedCourseId = ref("");
const selectedModelKey = ref("");
const workflowType = ref<WorkflowType>("knowledge_qa");
const answerMode = ref<AnswerMode>("detailed");
const tone = ref<Tone>("teaching_assistant");
const knowledgeScope = ref<KnowledgeScope>("course_first");
const includeBilibiliResources = ref(true);
const userInput = ref("");

const syllabus = ref("");
const examDate = ref("");
const availableHours = ref<number | undefined>();
const goalsText = ref("");
const weakTopicsText = ref("");
const userAnswer = ref("");
const helpLevel = ref<HelpLevel>("step_by_step");
const problemSource = ref("");
const originalAnswer = ref("");
const referenceAnswer = ref("");
const reviewFocus = ref("");
const materialTitle = ref("");
const readingGoal = ref("");

const conversationId = ref("");
const conversationHistory = ref<ConversationSummary[]>([]);
const conversationSnapshot = ref<ConversationDetail | null>(null);
const selectedAttemptId = ref("");
const result = ref<WorkflowRunResult | null>(null);
const isLoadingCourses = ref(true);
const isLoadingModels = ref(true);
const isLoadingHistory = ref(false);
const loadingConversationId = ref("");
const editingConversationId = ref("");
const conversationTitleDraft = ref("");
const renamingConversationId = ref("");
const deleteConfirmId = ref("");
const deletingConversationId = ref("");
const isRegenerating = ref(false);
const isRunning = ref(false);
const canCancelWorkflow = ref(false);
const workflowStreamState = ref<WorkflowStreamState | null>(null);
const isReloading = ref(false);
const errorMessage = ref("");
const noticeMessage = ref("");
const modelCatalogMessage = ref("");
const currentUser = ref<AuthUser | null>(null);
const isLoadingAuth = ref(true);
const authMessage = ref("");
const historyMessage = ref("");
const historyMessageIsError = ref(false);
const byokCredentialStatuses = ref<ByokCredentialStatus[]>([]);
const byokKeyDrafts = ref<Record<ByokProviderId, string>>(emptyByokKeyDrafts());
const isLoadingByokCredentials = ref(false);
const savingByokProviderId = ref<ByokProviderId | "">("");
const deletingByokProviderId = ref<ByokProviderId | "">("");
const byokMessage = ref("");
const byokMessageIsError = ref(false);
const privateRequestEpoch = createRequestEpoch();
let conversationLoadSequence = 0;
let isApplyingHistoryCourse = false;
let activeWorkflowStream: WorkflowStreamHandle | null = null;

const selectedCourse = computed(() =>
  courses.value.find((course) => course.course_id === selectedCourseId.value),
);
const activeWorkflow = computed(() => workflowCopy[workflowType.value]);
const byokCatalogIsCurrent = computed(
  () =>
    modelCatalogLoadSucceeded.value &&
    isCurrentByokCatalogVersion(modelCatalog.value.byok_catalog_version) &&
    Array.isArray(modelCatalog.value.byok_providers),
);
const byokProvidersForDisplay = computed<ByokProviderCatalogItem[]>(() =>
  mergeByokProvidersForDisplay(
    byokCatalogIsCurrent.value ? modelCatalog.value.byok_providers : [],
  ),
);
const byokRuntimeAvailable = computed(
  () => byokCatalogIsCurrent.value && modelCatalog.value.byok_available,
);
const modelsForSelection = computed<ModelCatalogItem[]>(() => [
  ...modelsForRuntime(
    modelCatalog.value,
    modelCatalog.value.models,
    ITERATION_ZERO_MOCK_MODEL,
    modelCatalogLoadSucceeded.value,
  ),
  ...configuredByokModelOptions(
    byokRuntimeAvailable.value ? byokProvidersForDisplay.value : [],
    byokCredentialStatuses.value,
  ),
]);
const selectedModel = computed(() =>
  modelsForSelection.value.find((model) => modelKey(model) === selectedModelKey.value),
);
const selectedModelIsMock = computed(
  () =>
    selectedModel.value?.availability_status === "mock_only" ||
    selectedModel.value?.provider_id === "mock",
);
const attempts = computed<WorkflowAttempt[]>(() => conversationSnapshot.value?.runs ?? []);
const latestAttempt = computed<WorkflowAttempt | null>(
  () => attempts.value[attempts.value.length - 1] ?? null,
);
const historyIsBusy = computed(
  () =>
    isLoadingHistory.value ||
    Boolean(loadingConversationId.value) ||
    Boolean(renamingConversationId.value) ||
    Boolean(deletingConversationId.value) ||
    isRegenerating.value ||
    isRunning.value ||
    isReloading.value,
);
const byokIsBusy = computed(
  () =>
    isLoadingByokCredentials.value ||
    Boolean(savingByokProviderId.value) ||
    Boolean(deletingByokProviderId.value),
);
const runtimeNoticeTitle = computed(() =>
  selectedModelIsMock.value
    ? "迭代 0 Mock，不是正式 OAuth / 模型 / 检索"
    : "显式模型选择，不会自动切换模型或 BYOK",
);
const runtimeNoticeDetail = computed(() => {
  if (selectedModelIsMock.value) {
    return "当前页面保留 Mock 持久化路径；未伪装成真实平台默认模型。";
  }
  if (!isLoadingModels.value && !modelCatalogLoadSucceeded.value) {
    return "模型目录加载失败，平台、Mock 与 BYOK 请求均已关闭。";
  }
  if (!isLoadingModels.value && !selectedModel.value) {
    return "请先从平台目录中选择一个模型；页面不会替你预选。";
  }
  if (!modelCatalog.value.real_platform_default_available) {
    return "正式平台默认池不可用；本次只使用你明确选中的可用模型。";
  }
  return "请求会携带当前模型来源、供应商和模型 ID。";
});

function modelOptionLabel(model: ModelCatalogItem): string {
  const suffixes = [
    model.billing_label === "platform_daily_free_quota" ? "平台每日免费" : "",
    model.is_preview ? "Preview" : "",
    model.user_selectable ? "" : "不可选",
  ].filter(Boolean);
  return `${model.company} · ${model.display_name}${suffixes.length ? ` / ${suffixes.join(" / ")}` : ""}`;
}

function billingLabel(model: ModelCatalogItem): string {
  const labels: Record<string, string> = {
    not_applicable_mock: "不产生真实模型费用",
    platform_daily_free_quota: "平台每日免费额度",
    user_free_quota: "用户账户免费额度",
    promotional: "促销额度",
    paid: "付费",
    unknown: "计费状态待核验",
    user_key: "使用你的供应商账户，额度／费用由供应商决定",
  };
  return labels[model.billing_label] ?? model.billing_label;
}

function availabilityLabel(model: ModelCatalogItem): string {
  const labels: Record<string, string> = {
    available: "可用",
    mock_only: "仅本地 Mock",
    platform_credential_not_configured: "平台凭据尚未配置",
    health_check_required: "等待模型健康检查",
    health_check_failed: "模型健康检查失败",
    model_unavailable: "模型已不在上游目录",
    pricing_or_terms_changed: "免费条款或价格已变化",
    structured_outputs_unavailable: "结构化输出能力不可用",
    platform_daily_quota_exhausted: "今日平台额度已用完",
    provider_rate_limited: "供应商暂时限流",
    unavailable: "不可用",
  };
  return labels[model.availability_status] ?? model.availability_status;
}

function splitList(value: string): string[] {
  return value
    .split(/[，,\n]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function toMessage(error: unknown): string {
  if (error instanceof ApiError && error.status === 429) return error.message;
  return error instanceof Error ? error.message : "请求失败，请检查 API 服务是否运行。";
}

function formatHistoryTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function byokCredentialStatus(providerId: ByokProviderId): ByokCredentialStatus | null {
  return (
    byokCredentialStatuses.value.find((status) => status.provider_id === providerId) ?? null
  );
}

function byokProviderDisabledReason(provider: ByokProviderCatalogItem): string {
  if (!modelCatalogLoadSucceeded.value) {
    return "模型目录未加载成功，凭据保存保持关闭。";
  }
  if (!byokCatalogIsCurrent.value) {
    return "BYOK 目录版本不匹配，凭据保存保持关闭。";
  }
  if (currentUser.value?.is_mock) {
    return "BYOK 需要真实 GitHub 登录；Mock 身份只保留入口展示。";
  }
  if (!byokRuntimeAvailable.value || !provider.enabled) {
    return "当前服务端未开启；需先满足会话级加密主密钥等安全运行条件。";
  }
  if (!currentUser.value) return "使用真实 GitHub 身份登录后可管理当前会话凭据。";
  return "";
}

function canSaveByokCredential(provider: ByokProviderCatalogItem): boolean {
  return Boolean(
    byokRuntimeAvailable.value &&
      canManageByokCredentials(currentUser.value) &&
      provider.enabled &&
      byokCredentialStatus(provider.provider_id)?.writable !== false &&
      byokKeyDrafts.value[provider.provider_id].trim() &&
      !byokIsBusy.value,
  );
}

function canDeleteByokCredential(providerId: ByokProviderId): boolean {
  return Boolean(
    canManageByokCredentials(currentUser.value) &&
      byokCredentialStatus(providerId)?.configured &&
      byokCredentialStatus(providerId)?.writable !== false &&
      !byokIsBusy.value,
  );
}

function byokCredentialWritable(providerId: ByokProviderId): boolean {
  const status = byokCredentialStatus(providerId);
  return Boolean(status && status.configured && status.writable);
}

function setByokMessage(message: string, isError = false): void {
  byokMessage.value = message;
  byokMessageIsError.value = isError;
}

function upsertByokCredentialStatus(status: ByokCredentialStatus): void {
  byokCredentialStatuses.value = [
    ...byokCredentialStatuses.value.filter(
      (item) => item.provider_id !== status.provider_id,
    ),
    status,
  ];
}

function clearUnavailableByokSelection(): void {
  if (
    selectedModelKey.value.startsWith("user_key:") &&
    !modelsForSelection.value.some((model) => modelKey(model) === selectedModelKey.value)
  ) {
    selectedModelKey.value = "";
  }
}

function courseName(courseId: string): string {
  return courses.value.find((course) => course.course_id === courseId)?.display_name ?? courseId;
}

function setHistoryMessage(message: string, isError = false): void {
  historyMessage.value = message;
  historyMessageIsError.value = isError;
}

function abortActiveWorkflow(detail: string): void {
  if (activeWorkflowStream && !activeWorkflowStream.signal.aborted) {
    activeWorkflowStream.abort(detail);
  }
  canCancelWorkflow.value = false;
}

function clearActiveConversation(): void {
  abortActiveWorkflow("当前会话已切换，运行已取消。");
  conversationId.value = "";
  conversationSnapshot.value = null;
  selectedAttemptId.value = "";
  result.value = null;
  workflowStreamState.value = null;
  noticeMessage.value = "";
  isRegenerating.value = false;
  isReloading.value = false;
}

function clearPrivateState(): void {
  conversationLoadSequence += 1;
  clearActiveConversation();
  conversationHistory.value = [];
  editingConversationId.value = "";
  conversationTitleDraft.value = "";
  renamingConversationId.value = "";
  deleteConfirmId.value = "";
  deletingConversationId.value = "";
  loadingConversationId.value = "";
  selectedAttemptId.value = "";
  isLoadingHistory.value = false;
  isRegenerating.value = false;
  isRunning.value = false;
  canCancelWorkflow.value = false;
  isReloading.value = false;
  byokCredentialStatuses.value = [];
  byokKeyDrafts.value = emptyByokKeyDrafts();
  isLoadingByokCredentials.value = false;
  savingByokProviderId.value = "";
  deletingByokProviderId.value = "";
  clearUnavailableByokSelection();
  setByokMessage("");
  setHistoryMessage("");
}

function applyAuthFailure(error: unknown): void {
  if (error instanceof ApiError && error.code === "auth_required") {
    privateRequestEpoch.invalidate();
    currentUser.value = null;
    clearPrivateState();
  }
}

function privateRequestIsCurrent(epoch: number, userId: string): boolean {
  return (
    privateRequestEpoch.isCurrent(epoch) &&
    currentUser.value?.user_id === userId
  );
}

function conversationSummary(detail: ConversationDetail): ConversationSummary {
  return {
    conversation_id: detail.conversation_id,
    user_id: detail.user_id,
    course_id: detail.course_id,
    title: detail.title,
    created_at: detail.created_at,
    updated_at: detail.updated_at,
    expires_at: detail.expires_at,
    mock_only: detail.mock_only,
  };
}

function upsertConversationSummary(summary: ConversationSummary): void {
  conversationHistory.value = [
    summary,
    ...conversationHistory.value.filter(
      (item) => item.conversation_id !== summary.conversation_id,
    ),
  ].sort((left, right) => right.updated_at.localeCompare(left.updated_at));
}

function showAttempt(attempt: WorkflowAttempt): void {
  workflowStreamState.value = null;
  selectedAttemptId.value = attempt.workflow_run_id;
  result.value = attempt.result;
}

function applyConversationDetail(
  conversation: ConversationDetail,
  preferredAttemptId = "",
): void {
  const attempt = selectConversationAttempt(conversation, preferredAttemptId);

  isApplyingHistoryCourse = true;
  selectedCourseId.value = conversation.course_id;
  isApplyingHistoryCourse = false;
  conversationId.value = conversation.conversation_id;
  conversationSnapshot.value = conversation;
  upsertConversationSummary(conversationSummary(conversation));

  if (attempt) {
    showAttempt(attempt);
  } else {
    selectedAttemptId.value = "";
    result.value = null;
  }
}

function startNewConversation(): void {
  conversationLoadSequence += 1;
  clearActiveConversation();
  editingConversationId.value = "";
  deleteConfirmId.value = "";
  errorMessage.value = "";
  setHistoryMessage("已切换到新会话，首次运行时创建记录。", false);
}

function beginRename(conversation: ConversationSummary): void {
  editingConversationId.value = conversation.conversation_id;
  conversationTitleDraft.value = conversation.title;
  deleteConfirmId.value = "";
  setHistoryMessage("");
}

function cancelRename(): void {
  editingConversationId.value = "";
  conversationTitleDraft.value = "";
}

function beginDelete(targetConversationId: string): void {
  cancelRename();
  deleteConfirmId.value = targetConversationId;
  setHistoryMessage("");
}

function cancelDelete(): void {
  deleteConfirmId.value = "";
}

function makeRequest(activeConversationId: string): WorkflowRunRequest {
  if (!selectedModel.value?.user_selectable) {
    throw new Error("请选择一个当前可用的模型。");
  }

  const common = {
    courseId: selectedCourseId.value,
    conversationId: activeConversationId,
    userInput: userInput.value,
    answerMode: answerMode.value,
    tone: tone.value,
    knowledgeScope: knowledgeScope.value,
    includeBilibiliResources: includeBilibiliResources.value,
    modelSource: selectedModel.value.model_source,
    providerId: selectedModel.value.provider_id,
    modelId: selectedModel.value.model_id,
  };

  switch (workflowType.value) {
    case "knowledge_qa":
      return buildWorkflowRequest({
        ...common,
        workflowType: "knowledge_qa",
        workflowPayload: { question: userInput.value },
      });
    case "exam_review":
      return buildWorkflowRequest({
        ...common,
        workflowType: "exam_review",
        workflowPayload: {
          syllabus: syllabus.value,
          exam_date: examDate.value,
          available_hours: availableHours.value,
          goals: splitList(goalsText.value),
          weak_topics: splitList(weakTopicsText.value),
        },
      });
    case "problem_tutor":
      return buildWorkflowRequest({
        ...common,
        workflowType: "problem_tutor",
        workflowPayload: {
          problem: userInput.value,
          user_answer: userAnswer.value,
          help_level: helpLevel.value,
          problem_source: problemSource.value,
        },
      });
    case "mistake_review":
      return buildWorkflowRequest({
        ...common,
        workflowType: "mistake_review",
        workflowPayload: {
          problem: userInput.value,
          original_answer: originalAnswer.value,
          reference_answer: referenceAnswer.value,
          review_focus: reviewFocus.value,
        },
      });
    case "temporary_material_reading":
      return buildWorkflowRequest({
        ...common,
        workflowType: "temporary_material_reading",
        workflowPayload: {
          material_title: materialTitle.value,
          material_text: userInput.value,
          reading_goal: readingGoal.value,
        },
      });
  }
}

function validateForm(): string | null {
  if (!currentUser.value) return "请先使用 GitHub 登录。";
  if (!selectedCourseId.value) return "请先选择课程。";
  if (!selectedCourse.value?.mock_available) return "该课程的 Mock Fixture 尚不可用。";
  if (!selectedModel.value?.user_selectable) return "请选择一个当前可用的模型。";
  if (!userInput.value.trim()) return `请填写${activeWorkflow.value.inputLabel}。`;
  if (workflowType.value === "mistake_review" && !originalAnswer.value.trim()) {
    return "错题复盘需要填写原答案。";
  }
  return null;
}

async function loadAuth(): Promise<void> {
  isLoadingAuth.value = true;
  authMessage.value = "";
  const authEpoch = privateRequestEpoch.snapshot();
  try {
    const user = await getMe();
    if (!privateRequestEpoch.isCurrent(authEpoch)) return;
    currentUser.value = user;
    await Promise.all([
      loadHistory(true),
      canManageByokCredentials(user) ? loadByokCredentials() : Promise.resolve(),
    ]);
  } catch (error) {
    if (!privateRequestEpoch.isCurrent(authEpoch)) return;
    currentUser.value = null;
    clearPrivateState();
    if (!(error instanceof ApiError && error.code === "auth_required")) {
      authMessage.value = toMessage(error);
    }
  } finally {
    isLoadingAuth.value = false;
  }
}

async function loadConversationFromHistory(
  targetConversationId: string,
  preferredAttemptId = "",
  announce = true,
): Promise<void> {
  const requestUserId = currentUser.value?.user_id;
  if (!requestUserId) return;
  const requestEpoch = privateRequestEpoch.snapshot();
  const loadSequence = ++conversationLoadSequence;
  loadingConversationId.value = targetConversationId;
  errorMessage.value = "";
  if (announce) setHistoryMessage("");

  try {
    const conversation = await getConversation(targetConversationId);
    if (
      !privateRequestIsCurrent(requestEpoch, requestUserId) ||
      loadSequence !== conversationLoadSequence
    ) {
      return;
    }
    applyConversationDetail(conversation, preferredAttemptId);
    if (announce) {
      setHistoryMessage(
        conversation.runs.length
          ? `已恢复“${conversation.title}”及 ${conversation.runs.length} 次回答。`
          : `已恢复“${conversation.title}”，当前还没有回答。`,
      );
    }
  } catch (error) {
    if (
      !privateRequestIsCurrent(requestEpoch, requestUserId) ||
      loadSequence !== conversationLoadSequence
    ) {
      return;
    }
    applyAuthFailure(error);
    setHistoryMessage(toMessage(error), true);
  } finally {
    if (loadSequence === conversationLoadSequence) loadingConversationId.value = "";
  }
}

async function loadHistory(restoreLatest: boolean): Promise<void> {
  const requestUserId = currentUser.value?.user_id;
  if (!requestUserId) return;
  const requestEpoch = privateRequestEpoch.snapshot();
  isLoadingHistory.value = true;
  setHistoryMessage("");

  try {
    const history = await listConversations();
    if (!privateRequestIsCurrent(requestEpoch, requestUserId)) return;
    conversationHistory.value = history;
    if (restoreLatest && history[0]) {
      await loadConversationFromHistory(history[0].conversation_id, "", false);
    } else if (restoreLatest) {
      clearActiveConversation();
    }
  } catch (error) {
    if (!privateRequestIsCurrent(requestEpoch, requestUserId)) return;
    applyAuthFailure(error);
    setHistoryMessage(toMessage(error), true);
  } finally {
    if (privateRequestIsCurrent(requestEpoch, requestUserId)) {
      isLoadingHistory.value = false;
    }
  }
}

async function loadByokCredentials(): Promise<void> {
  const requestUserId = currentUser.value?.user_id;
  if (!requestUserId || !canManageByokCredentials(currentUser.value)) return;
  const requestEpoch = privateRequestEpoch.snapshot();
  isLoadingByokCredentials.value = true;
  setByokMessage("");

  try {
    const statuses = await getByokCredentials();
    if (!privateRequestIsCurrent(requestEpoch, requestUserId)) return;
    byokCredentialStatuses.value = statuses;
    clearUnavailableByokSelection();
  } catch (error) {
    if (!privateRequestIsCurrent(requestEpoch, requestUserId)) return;
    applyAuthFailure(error);
    if (currentUser.value?.user_id === requestUserId) {
      setByokMessage(toMessage(error), true);
    }
  } finally {
    if (privateRequestIsCurrent(requestEpoch, requestUserId)) {
      isLoadingByokCredentials.value = false;
    }
  }
}

async function submitByokCredential(provider: ByokProviderCatalogItem): Promise<void> {
  const requestUserId = currentUser.value?.user_id;
  if (!requestUserId || !canSaveByokCredential(provider)) return;
  const requestEpoch = privateRequestEpoch.snapshot();
  const providerId = provider.provider_id;
  const apiKey = byokKeyDrafts.value[providerId].trim();
  savingByokProviderId.value = providerId;
  setByokMessage("");

  try {
    const status = await saveByokCredential(providerId, apiKey);
    if (!privateRequestIsCurrent(requestEpoch, requestUserId)) return;
    upsertByokCredentialStatus(status);
    setByokMessage(
      `${provider.display_name} 凭据状态已更新；模型仍需由你显式选择。`,
    );
  } catch (error) {
    if (!privateRequestIsCurrent(requestEpoch, requestUserId)) return;
    applyAuthFailure(error);
    if (currentUser.value?.user_id === requestUserId) {
      setByokMessage(toMessage(error), true);
    }
  } finally {
    if (privateRequestIsCurrent(requestEpoch, requestUserId)) {
      byokKeyDrafts.value[providerId] = "";
      if (savingByokProviderId.value === providerId) savingByokProviderId.value = "";
    }
  }
}

async function removeByokCredential(provider: ByokProviderCatalogItem): Promise<void> {
  const requestUserId = currentUser.value?.user_id;
  const providerId = provider.provider_id;
  if (!requestUserId || !canDeleteByokCredential(providerId)) return;
  const requestEpoch = privateRequestEpoch.snapshot();
  deletingByokProviderId.value = providerId;
  setByokMessage("");

  try {
    await deleteByokCredential(providerId);
    if (!privateRequestIsCurrent(requestEpoch, requestUserId)) return;
    byokCredentialStatuses.value = byokCredentialStatuses.value.filter(
      (status) => status.provider_id !== providerId,
    );
    clearUnavailableByokSelection();
    setByokMessage(`${provider.display_name} 凭据已从当前登录会话删除。`);
  } catch (error) {
    if (!privateRequestIsCurrent(requestEpoch, requestUserId)) return;
    applyAuthFailure(error);
    if (currentUser.value?.user_id === requestUserId) {
      setByokMessage(toMessage(error), true);
    }
  } finally {
    if (privateRequestIsCurrent(requestEpoch, requestUserId)) {
      byokKeyDrafts.value[providerId] = "";
      if (deletingByokProviderId.value === providerId) deletingByokProviderId.value = "";
    }
  }
}

function startGithubLogin(): void {
  window.location.assign(githubLoginUrl());
}

async function signOut(): Promise<void> {
  authMessage.value = "";
  privateRequestEpoch.invalidate();
  currentUser.value = null;
  clearPrivateState();
  try {
    await logout();
  } catch (error) {
    applyAuthFailure(error);
    authMessage.value = toMessage(error);
  }
}

async function loadCourses(): Promise<void> {
  isLoadingCourses.value = true;
  errorMessage.value = "";
  try {
    courses.value = await getCourses();
    const firstMockCourse = courses.value.find((course) => course.mock_available);
    const selectedCourseStillExists = courses.value.some(
      (course) => course.course_id === selectedCourseId.value,
    );
    if (!selectedCourseStillExists) {
      selectedCourseId.value = firstMockCourse?.course_id ?? courses.value[0]?.course_id ?? "";
    }
  } catch (error) {
    applyAuthFailure(error);
    errorMessage.value = toMessage(error);
  } finally {
    isLoadingCourses.value = false;
  }
}

async function loadModels(): Promise<void> {
  isLoadingModels.value = true;
  modelCatalogLoadSucceeded.value = false;
  selectedModelKey.value = "";
  modelCatalogMessage.value = "";
  try {
    modelCatalog.value = await getModels();
    modelCatalogLoadSucceeded.value = true;
  } catch (error) {
    modelCatalog.value = FAIL_CLOSED_MODEL_CATALOG;
    modelCatalogMessage.value = `${toMessage(error)} 模型目录加载失败，模型请求已关闭。`;
  } finally {
    selectedModelKey.value = modelCatalogLoadSucceeded.value
      ? initialModelSelectionKey(
          modelCatalog.value,
          modelsForSelection.value,
          ITERATION_ZERO_MOCK_MODEL,
        )
      : "";
    isLoadingModels.value = false;
  }
}

async function saveConversationTitle(): Promise<void> {
  const targetConversationId = editingConversationId.value;
  const title = conversationTitleDraft.value.trim();
  const requestUserId = currentUser.value?.user_id;
  if (!targetConversationId || !requestUserId) return;
  if (!title) {
    setHistoryMessage("会话名称不能为空。", true);
    return;
  }

  const requestEpoch = privateRequestEpoch.snapshot();
  renamingConversationId.value = targetConversationId;
  setHistoryMessage("");
  try {
    const renamed = await renameConversation(targetConversationId, title);
    if (!privateRequestIsCurrent(requestEpoch, requestUserId)) return;
    upsertConversationSummary(renamed);
    if (conversationSnapshot.value?.conversation_id === targetConversationId) {
      conversationSnapshot.value = {
        ...conversationSnapshot.value,
        title: renamed.title,
        updated_at: renamed.updated_at,
        expires_at: renamed.expires_at,
      };
    }
    cancelRename();
    setHistoryMessage(`已重命名为“${renamed.title}”。`);
  } catch (error) {
    if (!privateRequestIsCurrent(requestEpoch, requestUserId)) return;
    applyAuthFailure(error);
    setHistoryMessage(toMessage(error), true);
  } finally {
    if (
      privateRequestIsCurrent(requestEpoch, requestUserId) &&
      renamingConversationId.value === targetConversationId
    ) {
      renamingConversationId.value = "";
    }
  }
}

async function confirmDeleteConversation(targetConversationId: string): Promise<void> {
  const requestUserId = currentUser.value?.user_id;
  if (!requestUserId) return;
  const requestEpoch = privateRequestEpoch.snapshot();
  deletingConversationId.value = targetConversationId;
  setHistoryMessage("");

  try {
    await deleteConversation(targetConversationId);
    if (!privateRequestIsCurrent(requestEpoch, requestUserId)) return;
    conversationHistory.value = conversationHistory.value.filter(
      (item) => item.conversation_id !== targetConversationId,
    );
    deleteConfirmId.value = "";
    if (conversationId.value === targetConversationId) {
      conversationLoadSequence += 1;
      clearActiveConversation();
      const nextConversation = conversationHistory.value[0];
      if (nextConversation) {
        await loadConversationFromHistory(nextConversation.conversation_id, "", false);
      }
    }
    if (privateRequestIsCurrent(requestEpoch, requestUserId)) {
      setHistoryMessage("会话及其回答记录已删除。", false);
    }
  } catch (error) {
    if (!privateRequestIsCurrent(requestEpoch, requestUserId)) return;
    applyAuthFailure(error);
    setHistoryMessage(toMessage(error), true);
  } finally {
    if (
      privateRequestIsCurrent(requestEpoch, requestUserId) &&
      deletingConversationId.value === targetConversationId
    ) {
      deletingConversationId.value = "";
    }
  }
}

async function regenerateLatestAttempt(): Promise<void> {
  const sourceAttempt = latestAttempt.value;
  const activeConversationId = conversationId.value;
  const requestUserId = currentUser.value?.user_id;
  if (!sourceAttempt || !activeConversationId || !requestUserId) return;
  const requestEpoch = privateRequestEpoch.snapshot();
  isRegenerating.value = true;
  errorMessage.value = "";
  setHistoryMessage("");

  try {
    const regenerated = await regenerateWorkflowRun(sourceAttempt.workflow_run_id);
    if (
      !privateRequestIsCurrent(requestEpoch, requestUserId) ||
      conversationId.value !== activeConversationId ||
      !conversationSnapshot.value
    ) {
      return;
    }
    const retainedAttempts = conversationSnapshot.value.runs.filter(
      (attempt) => attempt.workflow_run_id !== regenerated.workflow_run_id,
    );
    const updatedConversation: ConversationDetail = {
      ...conversationSnapshot.value,
      updated_at: regenerated.updated_at,
      expires_at: regenerated.expires_at,
      runs: [...retainedAttempts, regenerated],
    };
    applyConversationDetail(updatedConversation, regenerated.workflow_run_id);
    noticeMessage.value = "已创建新的回答尝试，旧回答仍保留在历史中。";
    setHistoryMessage(
      `已生成第 ${updatedConversation.runs.length} 次回答；可切换查看旧版本。`,
    );
  } catch (error) {
    if (!privateRequestIsCurrent(requestEpoch, requestUserId)) return;
    applyAuthFailure(error);
    setHistoryMessage(toMessage(error), true);
  } finally {
    if (
      privateRequestIsCurrent(requestEpoch, requestUserId) &&
      conversationId.value === activeConversationId
    ) {
      isRegenerating.value = false;
    }
  }
}

async function submitWorkflow(): Promise<void> {
  errorMessage.value = "";
  noticeMessage.value = "";
  const validationError = validateForm();
  if (validationError) {
    errorMessage.value = validationError;
    return;
  }

  const requestEpoch = privateRequestEpoch.snapshot();
  const requestUserId = currentUser.value!.user_id;
  isRunning.value = true;
  canCancelWorkflow.value = false;
  result.value = null;
  selectedAttemptId.value = "";
  workflowStreamState.value = createInitialWorkflowStreamState();
  try {
    let activeConversationId = conversationId.value;
    if (!activeConversationId) {
      const conversation = await createConversation(selectedCourseId.value);
      if (!privateRequestIsCurrent(requestEpoch, requestUserId)) return;
      activeConversationId = conversation.conversation_id;
      conversationId.value = activeConversationId;
      conversationSnapshot.value = { ...conversation, runs: [] };
      upsertConversationSummary(conversation);
    }

    const request = makeRequest(activeConversationId);
    const streamHandle = startWorkflowRunStream(request, (nextState) => {
      if (
        privateRequestIsCurrent(requestEpoch, requestUserId) &&
        conversationId.value === activeConversationId
      ) {
        workflowStreamState.value = nextState;
        if (nextState.result) result.value = nextState.result;
      }
    });
    activeWorkflowStream = streamHandle;
    canCancelWorkflow.value = true;
    const finalState = await streamHandle.done;
    if (
      activeWorkflowStream === streamHandle
    ) {
      activeWorkflowStream = null;
      canCancelWorkflow.value = false;
    }
    if (
      !privateRequestIsCurrent(requestEpoch, requestUserId) ||
      conversationId.value !== activeConversationId
    ) {
      return;
    }
    workflowStreamState.value = finalState;

    const workflowResult = finalState.result;
    if (!workflowResult) {
      const streamError = finalState.error;
      if (streamError?.code === "auth_required") {
        applyAuthFailure(new ApiError(streamError.detail, 401, streamError.code));
        errorMessage.value = streamError.detail;
      } else if (streamError?.code === "client_interrupted") {
        noticeMessage.value = "已取消本次运行；后端会尽力保存 interrupted 状态，可稍后重新读取会话。";
      } else {
        errorMessage.value = streamError?.detail ?? "流式运行未返回最终结果。";
      }
      return;
    }

    result.value = workflowResult;
    selectedAttemptId.value = workflowResult.workflow_run_id;
    const restoredConversation = await getConversation(activeConversationId);
    if (!privateRequestIsCurrent(requestEpoch, requestUserId)) return;
    applyConversationDetail(restoredConversation, workflowResult.workflow_run_id);
    if (workflowResult.run_status === "completed") {
      noticeMessage.value = selectedModelIsMock.value
        ? "Mock 运行已保存，可以重新读取会话验证持久化。"
        : "运行已保存，可以重新读取会话验证持久化。";
    } else if (workflowResult.run_status === "interrupted") {
      noticeMessage.value = "运行已中断并保存，可在回答尝试中重新查看。";
    } else {
      errorMessage.value = "运行失败状态已保存，请查看安全 Trace 后重试。";
    }
  } catch (error) {
    if (!privateRequestIsCurrent(requestEpoch, requestUserId)) return;
    applyAuthFailure(error);
    errorMessage.value = toMessage(error);
  } finally {
    if (privateRequestIsCurrent(requestEpoch, requestUserId)) {
      isRunning.value = false;
    }
  }
}

function cancelWorkflow(): void {
  if (!activeWorkflowStream || activeWorkflowStream.signal.aborted) return;
  noticeMessage.value = "正在取消本次运行。";
  abortActiveWorkflow("用户取消了本次运行。");
}

async function reloadConversation(): Promise<void> {
  if (!conversationId.value) return;
  errorMessage.value = "";
  noticeMessage.value = "";
  const requestEpoch = privateRequestEpoch.snapshot();
  const requestUserId = currentUser.value?.user_id;
  if (!requestUserId) return;
  const targetConversationId = conversationId.value;
  isReloading.value = true;
  try {
    const conversation = await getConversation(targetConversationId);
    if (
      !privateRequestIsCurrent(requestEpoch, requestUserId) ||
      conversationId.value !== targetConversationId
    ) {
      return;
    }
    applyConversationDetail(conversation);
    noticeMessage.value = "会话已从 GET 接口重新读取。";
  } catch (error) {
    if (!privateRequestIsCurrent(requestEpoch, requestUserId)) return;
    applyAuthFailure(error);
    errorMessage.value = toMessage(error);
  } finally {
    if (
      privateRequestIsCurrent(requestEpoch, requestUserId) &&
      conversationId.value === targetConversationId
    ) {
      isReloading.value = false;
    }
  }
}

watch(knowledgeScope, (scope) => {
  if (scope === "course_only") includeBilibiliResources.value = false;
});

watch(
  selectedCourseId,
  () => {
    if (isApplyingHistoryCourse) return;
    conversationLoadSequence += 1;
    clearActiveConversation();
    editingConversationId.value = "";
    deleteConfirmId.value = "";
  },
  { flush: "sync" },
);

onMounted(() => {
  void loadAuth();
  void loadCourses();
  void loadModels();
});

onBeforeUnmount(() => {
  abortActiveWorkflow("页面已离开，运行已取消。");
});
</script>

<template>
  <div class="app-frame">
    <header class="topbar">
      <a href="#main-content" class="skip-link">跳到主内容</a>
      <div class="brand-lockup">
        <span class="brand-mark" aria-hidden="true">S</span>
        <div>
          <strong>SCUT 老学长</strong>
          <span>课程 Workflow 契约验证</span>
        </div>
      </div>
      <div class="runtime-facts" aria-label="当前模型运行配置">
        <span>provider: {{ selectedModel?.provider_id ?? (isLoadingModels ? "loading" : "not selected") }}</span>
        <span>model: {{ selectedModel?.model_id ?? (isLoadingModels ? "loading" : "not selected") }}</span>
      </div>
      <div class="auth-controls" aria-label="登录状态">
        <span v-if="isLoadingAuth">正在确认登录状态</span>
        <template v-else-if="currentUser">
          <span>
            {{ currentUser.is_mock ? "本地 Mock 身份" : `GitHub · @${currentUser.github_login}` }}
          </span>
          <button v-if="!currentUser.is_mock" type="button" @click="signOut">退出</button>
        </template>
        <button v-else type="button" @click="startGithubLogin">使用 GitHub 登录</button>
      </div>
    </header>

    <p v-if="authMessage" class="auth-message" role="alert">{{ authMessage }}</p>

    <aside class="mock-notice" role="note">
      <strong>{{ runtimeNoticeTitle }}</strong>
      <span>{{ runtimeNoticeDetail }}</span>
    </aside>

    <main id="main-content" class="workspace">
      <aside class="history-shell" aria-labelledby="history-heading">
        <header class="history-header">
          <div>
            <p class="section-kicker">30 天历史</p>
            <h2 id="history-heading">历史会话</h2>
          </div>
          <button
            type="button"
            class="history-new-button"
            :disabled="!currentUser || historyIsBusy"
            @click="startNewConversation"
          >
            新会话
          </button>
        </header>

        <p
          v-if="historyMessage"
          class="history-message"
          :class="historyMessageIsError ? 'history-message-error' : 'history-message-success'"
          :role="historyMessageIsError ? 'alert' : 'status'"
        >
          {{ historyMessage }}
        </p>

        <div v-if="!currentUser" class="history-empty">
          登录后可恢复最近会话和全部回答尝试。
        </div>
        <div v-else-if="isLoadingHistory" class="history-empty" role="status">
          正在读取历史记录。
        </div>
        <div v-else-if="!conversationHistory.length" class="history-empty">
          暂无历史。首次运行后会保留 30 天。
        </div>
        <ul v-else class="history-list" aria-label="历史会话列表">
          <li
            v-for="conversation in conversationHistory"
            :key="conversation.conversation_id"
            :class="{ active: conversationId === conversation.conversation_id }"
          >
            <button
              type="button"
              class="history-select-button"
              :aria-current="conversationId === conversation.conversation_id ? 'page' : undefined"
              :disabled="historyIsBusy"
              @click="loadConversationFromHistory(conversation.conversation_id)"
            >
              <strong>{{ conversation.title }}</strong>
              <span>{{ courseName(conversation.course_id) }}</span>
              <small>
                {{ loadingConversationId === conversation.conversation_id ? "读取中" : formatHistoryTime(conversation.updated_at) }}
              </small>
            </button>

            <form
              v-if="editingConversationId === conversation.conversation_id"
              class="history-rename-form"
              @submit.prevent="saveConversationTitle"
            >
              <label :for="`history-title-${conversation.conversation_id}`">会话名称</label>
              <input
                :id="`history-title-${conversation.conversation_id}`"
                v-model="conversationTitleDraft"
                type="text"
                maxlength="100"
                :disabled="renamingConversationId === conversation.conversation_id"
                required
              />
              <div>
                <button type="submit" :disabled="renamingConversationId === conversation.conversation_id">
                  {{ renamingConversationId === conversation.conversation_id ? "保存中" : "保存" }}
                </button>
                <button type="button" :disabled="Boolean(renamingConversationId)" @click="cancelRename">
                  取消
                </button>
              </div>
            </form>

            <div v-else-if="deleteConfirmId === conversation.conversation_id" class="history-delete-confirm">
              <span>会同时删除全部回答，确定吗？</span>
              <div>
                <button
                  type="button"
                  class="danger-button"
                  :disabled="deletingConversationId === conversation.conversation_id"
                  @click="confirmDeleteConversation(conversation.conversation_id)"
                >
                  {{ deletingConversationId === conversation.conversation_id ? "删除中" : "确认删除" }}
                </button>
                <button type="button" :disabled="Boolean(deletingConversationId)" @click="cancelDelete">
                  取消
                </button>
              </div>
            </div>

            <div v-else class="history-item-actions">
              <button type="button" :disabled="historyIsBusy" @click="beginRename(conversation)">
                重命名
              </button>
              <button type="button" :disabled="historyIsBusy" @click="beginDelete(conversation.conversation_id)">
                删除
              </button>
            </div>
          </li>
        </ul>

        <section v-if="conversationSnapshot" class="attempt-history" aria-labelledby="attempt-heading">
          <div class="attempt-header">
            <div>
              <h3 id="attempt-heading">回答尝试</h3>
              <span>{{ attempts.length }} 次</span>
            </div>
            <button
              type="button"
              :disabled="historyIsBusy || !latestAttempt"
              @click="regenerateLatestAttempt"
            >
              {{ isRegenerating ? "重新生成中" : "重新生成最新回答" }}
            </button>
          </div>
          <p v-if="!attempts.length" class="attempt-empty">当前会话还没有回答。</p>
          <ol v-else class="attempt-list">
            <li v-for="(attempt, index) in attempts" :key="attempt.workflow_run_id">
              <button
                type="button"
                :class="{ active: selectedAttemptId === attempt.workflow_run_id }"
                :aria-current="selectedAttemptId === attempt.workflow_run_id ? 'true' : undefined"
                :disabled="historyIsBusy"
                @click="showAttempt(attempt)"
              >
                <span>
                  <strong>第 {{ index + 1 }} 次</strong>
                  <small v-if="index === attempts.length - 1">最新</small>
                  <small v-else-if="attempt.regenerated_from_run_id">重新生成</small>
                  <small v-else>初始回答</small>
                </span>
                <span>{{ formatHistoryTime(attempt.created_at) }}</span>
                <code>{{ attempt.result.model.model_id }}</code>
              </button>
            </li>
          </ol>
        </section>
      </aside>

      <section class="control-shell" aria-labelledby="control-heading">
        <div class="control-intro">
          <p class="section-kicker">发起一次 Workflow 运行</p>
          <h1 id="control-heading">选择课程与 Workflow</h1>
          <p>正式课程均保持关闭，只有带 Fixture 的课程可用于本轮契约验证。</p>
        </div>

        <section class="byok-panel" aria-labelledby="byok-heading">
          <div class="byok-panel-header">
            <div>
              <h2 id="byok-heading">使用自己的 API Key</h2>
            </div>
            <span class="byok-evidence-badge">本地安全链路已接入</span>
          </div>
          <p class="byok-boundary-note">
            Key 只在密码输入框中短暂存在，保存请求结束即清空；不会写入浏览器存储、URL、历史或模型目录。
            本轮未用真实用户 Key 形成实网调用证据，余额、权限及上游错误以实际调用结果为准。
          </p>
          <p v-if="isLoadingByokCredentials" class="byok-message" role="status">
            正在读取当前登录会话的脱敏凭据状态。
          </p>
          <p
            v-else-if="byokMessage"
            class="byok-message"
            :class="byokMessageIsError ? 'byok-message-error' : 'byok-message-success'"
            :role="byokMessageIsError ? 'alert' : 'status'"
          >
            {{ byokMessage }}
          </p>

          <div class="byok-provider-grid">
            <article
              v-for="provider in byokProvidersForDisplay"
              :key="provider.provider_id"
              class="byok-provider-card"
              :class="{ 'byok-provider-card-disabled': !byokRuntimeAvailable || !provider.enabled }"
            >
              <header class="byok-provider-header">
                <div>
                  <strong>{{ provider.display_name }}</strong>
                  <span>{{ provider.company }}</span>
                </div>
                <span
                  class="byok-provider-state"
                  :class="byokRuntimeAvailable && provider.enabled ? 'status-available' : 'status-closed'"
                >
                  {{ byokRuntimeAvailable && provider.enabled ? "服务端已启用" : "服务端未开启" }}
                </span>
              </header>

              <div v-if="provider.models[0]" class="byok-fixed-model">
                <span>固定模型</span>
                <strong>{{ provider.models[0].company }} · {{ provider.models[0].display_name }}</strong>
                <code>{{ provider.models[0].model_id }}</code>
              </div>

              <div
                v-if="byokCredentialStatus(provider.provider_id)?.configured"
                class="byok-credential-status"
              >
                <strong>当前会话已配置</strong>
                <span>{{ byokCredentialStatus(provider.provider_id)?.masked_key || "Key 已脱敏" }}</span>
                <span v-if="byokCredentialStatus(provider.provider_id)?.expires_at">
                  到期：{{ formatHistoryTime(byokCredentialStatus(provider.provider_id)?.expires_at || "") }}
                </span>
                <span
                  v-if="byokCredentialStatus(provider.provider_id)?.configured && !byokCredentialWritable(provider.provider_id)"
                  class="byok-credential-readonly"
                >
                  只读：当前会话不可替换或删除
                </span>
              </div>

              <p v-if="byokProviderDisabledReason(provider)" class="byok-disabled-reason">
                {{ byokProviderDisabledReason(provider) }}
              </p>

              <form class="byok-credential-form" @submit.prevent="submitByokCredential(provider)">
                <label :for="`byok-key-${provider.provider_id}`">API Key</label>
                <input
                  :id="`byok-key-${provider.provider_id}`"
                  v-model="byokKeyDrafts[provider.provider_id]"
                  type="password"
                  autocomplete="new-password"
                  autocapitalize="none"
                  spellcheck="false"
                  maxlength="512"
                  placeholder="输入后仅提交给本站后端"
                  :disabled="!canManageByokCredentials(currentUser) || !byokRuntimeAvailable || !provider.enabled || byokIsBusy"
                />

                <div class="byok-card-actions">
                  <button
                    type="submit"
                    class="primary-button"
                    :disabled="!canSaveByokCredential(provider)"
                  >
                    {{
                      savingByokProviderId === provider.provider_id
                        ? "保存中"
                        : byokCredentialStatus(provider.provider_id)?.configured
                          ? "替换 Key"
                          : "保存 Key"
                    }}
                  </button>
                  <button
                    v-if="byokCredentialStatus(provider.provider_id)?.configured"
                    type="button"
                    class="secondary-button"
                    :disabled="!canDeleteByokCredential(provider.provider_id)"
                    @click="removeByokCredential(provider)"
                  >
                    {{ deletingByokProviderId === provider.provider_id ? "删除中" : "删除" }}
                  </button>
                </div>
              </form>
            </article>
          </div>
        </section>

        <div v-if="isLoadingCourses" class="inline-state" role="status">正在读取课程注册表。</div>

        <form v-else class="workflow-form" @submit.prevent="submitWorkflow">
          <div class="field-group">
            <label for="course">课程</label>
            <select id="course" v-model="selectedCourseId" :disabled="isRunning || !courses.length">
              <option v-if="!courses.length" value="">暂无课程</option>
              <option
                v-for="course in courses"
                :key="course.course_id"
                :value="course.course_id"
                :disabled="!course.mock_available"
              >
                {{ course.display_name }}{{ course.mock_available ? " / Mock 可用" : " / Mock 未配置" }}
              </option>
            </select>
            <div v-if="selectedCourse" class="course-status">
              <span :class="selectedCourse.mock_available ? 'status-available' : 'status-closed'">
                Mock：{{ selectedCourse.mock_available ? "可用" : "关闭" }}
              </span>
              <span class="status-closed">正式开放：{{ selectedCourse.is_open ? "是" : "否" }}</span>
            </div>
          </div>

          <div class="field-group">
            <label for="model">模型</label>
            <select
              id="model"
              v-model="selectedModelKey"
              :disabled="isRunning || isLoadingModels || !modelCatalogLoadSucceeded"
            >
              <option v-if="isLoadingModels" :value="selectedModelKey">正在读取模型目录</option>
              <option v-else-if="!modelCatalogLoadSucceeded" value="">
                模型目录不可用，模型请求已关闭
              </option>
              <template v-else>
                <option value="" disabled>请选择模型</option>
                <option
                  v-for="model in modelsForSelection"
                  :key="modelKey(model)"
                  :value="modelKey(model)"
                  :disabled="!model.user_selectable"
                >
                  {{ modelOptionLabel(model) }}
                </option>
              </template>
            </select>
            <div v-if="selectedModel" class="model-summary">
              <div class="model-name-line">
                <strong>{{ selectedModel.company }} · {{ selectedModel.display_name }}</strong>
                <span v-if="selectedModel.is_preview" class="preview-badge">Preview</span>
              </div>
              <span>{{ billingLabel(selectedModel) }}</span>
              <span>状态：{{ availabilityLabel(selectedModel) }}</span>
              <span v-if="selectedModel.last_checked_at">
                健康检查：{{ new Date(selectedModel.last_checked_at).toLocaleString("zh-CN") }}
              </span>
            </div>
            <p class="quota-notice" role="note">{{ modelCatalog.quota_notice }}</p>
            <p v-if="modelCatalogMessage" class="model-catalog-message" role="alert">
              {{ modelCatalogMessage }}
            </p>
          </div>

          <fieldset class="field-group">
            <legend>Workflow</legend>
            <div class="workflow-options">
              <label v-for="type in WORKFLOW_TYPES" :key="type" class="workflow-option">
                <input v-model="workflowType" type="radio" name="workflow" :value="type" />
                <span>
                  <strong>{{ workflowCopy[type].label }}</strong>
                  <small>{{ workflowCopy[type].description }}</small>
                </span>
              </label>
            </div>
          </fieldset>

          <div class="field-group">
            <label for="user-input">{{ activeWorkflow.inputLabel }}</label>
            <textarea
              id="user-input"
              v-model="userInput"
              rows="5"
              :placeholder="activeWorkflow.placeholder"
              required
            ></textarea>
          </div>

          <section v-if="workflowType === 'exam_review'" class="workflow-fields" aria-label="备考复习专属字段">
            <div class="field-group full-width">
              <label for="syllabus">考试大纲（可选）</label>
              <textarea id="syllabus" v-model="syllabus" rows="3" placeholder="粘贴大纲或范围说明。"></textarea>
            </div>
            <div class="field-group">
              <label for="exam-date">考试日期（可选）</label>
              <input id="exam-date" v-model="examDate" type="date" />
            </div>
            <div class="field-group">
              <label for="available-hours">可投入小时（可选）</label>
              <input id="available-hours" v-model.number="availableHours" type="number" min="0" step="0.5" />
            </div>
            <div class="field-group">
              <label for="goals">目标</label>
              <input id="goals" v-model="goalsText" type="text" placeholder="逗号或换行分隔" />
            </div>
            <div class="field-group">
              <label for="weak-topics">薄弱知识点</label>
              <input id="weak-topics" v-model="weakTopicsText" type="text" placeholder="逗号或换行分隔" />
            </div>
          </section>

          <section v-if="workflowType === 'problem_tutor'" class="workflow-fields" aria-label="题目辅导专属字段">
            <div class="field-group full-width">
              <label for="user-answer">我的作答（可选）</label>
              <textarea id="user-answer" v-model="userAnswer" rows="3"></textarea>
            </div>
            <div class="field-group">
              <label for="help-level">帮助层级</label>
              <select id="help-level" v-model="helpLevel">
                <option v-for="level in HELP_LEVELS" :key="level" :value="level">{{ helpLevelLabels[level] }}</option>
              </select>
            </div>
            <div class="field-group">
              <label for="problem-source">题目来源（可选）</label>
              <input id="problem-source" v-model="problemSource" type="text" placeholder="例如：2023 期末 A 卷" />
            </div>
          </section>

          <section v-if="workflowType === 'mistake_review'" class="workflow-fields" aria-label="错题复盘专属字段">
            <div class="field-group full-width">
              <label for="original-answer">原答案</label>
              <textarea id="original-answer" v-model="originalAnswer" rows="3" required></textarea>
            </div>
            <div class="field-group">
              <label for="reference-answer">参考答案（可选）</label>
              <textarea id="reference-answer" v-model="referenceAnswer" rows="3"></textarea>
            </div>
            <div class="field-group">
              <label for="review-focus">复盘重点（可选）</label>
              <textarea id="review-focus" v-model="reviewFocus" rows="3"></textarea>
            </div>
          </section>

          <section v-if="workflowType === 'temporary_material_reading'" class="workflow-fields" aria-label="临时材料精读专属字段">
            <div class="field-group">
              <label for="material-title">材料标题（可选）</label>
              <input id="material-title" v-model="materialTitle" type="text" maxlength="200" placeholder="例如：特征值与特征向量复习提纲" />
            </div>
            <div class="field-group full-width">
              <label for="reading-goal">精读目标（可选）</label>
              <input id="reading-goal" v-model="readingGoal" type="text" placeholder="例如：提取考试范围并指出与课程资料的冲突" />
            </div>
          </section>

          <div class="control-grid">
            <div class="field-group">
              <label for="answer-mode">回答方式</label>
              <select id="answer-mode" v-model="answerMode">
                <option v-for="mode in ANSWER_MODES" :key="mode" :value="mode">{{ answerModeLabels[mode] }}</option>
              </select>
            </div>
            <div class="field-group">
              <label for="tone">表达风格</label>
              <select id="tone" v-model="tone">
                <option v-for="item in TONES" :key="item" :value="item">{{ toneLabels[item] }}</option>
              </select>
            </div>
          </div>

          <fieldset class="field-group scope-fieldset">
            <legend>知识范围</legend>
            <label>
              <input v-model="knowledgeScope" type="radio" value="course_first" />
              <span><strong>资料优先</strong><small>允许明确标记的通用补充</small></span>
            </label>
            <label>
              <input v-model="knowledgeScope" type="radio" value="course_only" />
              <span><strong>仅课程资料</strong><small>证据不足时停止猜测</small></span>
            </label>
          </fieldset>

          <label class="checkbox-field" :class="{ disabled: knowledgeScope === 'course_only' }">
            <input
              v-model="includeBilibiliResources"
              type="checkbox"
              :disabled="knowledgeScope === 'course_only'"
            />
            <span>
              <strong>返回 B站延伸学习</strong>
              <small>模型给出聚焦词后只返回匿名搜索链接，不返回具体视频直链。仅课程资料模式强制关闭。</small>
            </span>
          </label>

          <div v-if="errorMessage" class="form-message error-message" role="alert">{{ errorMessage }}</div>
          <div v-if="noticeMessage" class="form-message success-message" role="status">{{ noticeMessage }}</div>

          <div class="form-actions">
            <button
              type="submit"
              class="primary-button"
              :disabled="isRunning || isLoadingCourses || isLoadingModels || !currentUser || !selectedModel?.user_selectable"
            >
              {{ isRunning ? "正在运行" : selectedModelIsMock ? "运行 Mock Workflow" : "运行 Workflow" }}
            </button>
            <button
              v-if="isRunning && canCancelWorkflow"
              type="button"
              class="secondary-button cancel-button"
              @click="cancelWorkflow"
            >
              取消本次运行
            </button>
            <button
              v-else
              type="button"
              class="secondary-button"
              :disabled="!conversationId || isReloading || isRunning"
              @click="reloadConversation"
            >
              {{ isReloading ? "正在读取" : "重新读取会话" }}
            </button>
          </div>

          <dl class="contract-facts">
            <div>
              <dt>course_scope</dt>
              <dd>single</dd>
            </div>
            <div>
              <dt>conversation_id</dt>
              <dd>{{ conversationId || "首次运行时创建" }}</dd>
            </div>
            <div>
              <dt>allowed_course_ids</dt>
              <dd>[]</dd>
            </div>
            <div>
              <dt>model_source</dt>
              <dd>{{ selectedModel?.model_source ?? (isLoadingModels ? "读取中" : "未选择") }}</dd>
            </div>
            <div>
              <dt>catalog_version</dt>
              <dd>{{ modelCatalog.catalog_version }}</dd>
            </div>
          </dl>
        </form>
      </section>

      <WorkflowResult
        :result="result"
        :is-running="isRunning"
        :stream-state="workflowStreamState"
      />
    </main>
  </div>
</template>
