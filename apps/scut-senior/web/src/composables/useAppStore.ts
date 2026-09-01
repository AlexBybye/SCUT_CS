import { computed, reactive, ref, watch } from "vue";
import {
  ApiError,
  createConversation,
  deleteByokCredential,
  deleteConversation,
  getByokCredentials,
  getMe,
  getAccountPreferences,
  saveAccountPreferences,
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
  cancelWorkflowRun,
  previewExamReviewPlan,
  recordExamReviewPlanDecision,
  type ExamReviewPlanPreview,
} from "../api";
import {
  isCurrentByokCatalogVersion,
  mergeByokProvidersForDisplay,
} from "../byokCatalog";
import { canManageByokCredentials } from "../byokSession";
import {
  parseAnswerMode,
  parseTone,
  readStoredAnswerMode,
  readStoredTone,
  writeStoredAnswerMode,
  writeStoredTone,
} from "../assistantPreference";
import type {
  AnswerMode,
  AuthUser,
  ByokCredentialStatus,
  ByokProviderCatalogItem,
  ByokProviderId,
  ConversationDetail,
  ConversationSummary,
  Course,
  HelpLevel,
  KnowledgeScope,
  ModelCatalog,
  ModelCatalogItem,
  RetrievalMode,
  Tone,
  WorkflowAttempt,
  WorkflowRunRequest,
  WorkflowRunResult,
  WorkflowType,
} from "../contracts";
import {
  courseSelectionError,
  selectSelectableCourseId,
} from "../courseAvailability";
import {
  configuredByokModelOptions,
  initialModelSelectionKey,
  modelKey,
  modelsForRuntime,
} from "../modelSelection";
import { createRequestEpoch } from "../requestEpoch";
import {
  applyAccent,
  applyThemeMode,
  readStoredAccent,
  readStoredThemeMode,
  writeStoredAccent,
  writeStoredThemeMode,
  type AccentTheme,
  type ThemeMode,
} from "../themePreference";
import { buildWorkflowRequest } from "../workflowRequest";
import { buildRoutedWorkflowPayload, routeWorkflow } from "../workflowRouter";
import { selectConversationAttempt } from "../workflowResultValidation";
import {
  createInitialWorkflowStreamState,
  type WorkflowStreamHandle,
  type WorkflowStreamState,
} from "../workflowStream";
import {
  FAIL_CLOSED_MODEL_CATALOG,
  ITERATION_ZERO_MOCK_MODEL,
  emptyByokKeyDrafts,
  splitList,
  toMessage,
  workflowCopy,
} from "../appConfig";
import { createLatestSaveQueue } from "../latestSaveQueue";

export type InspectorTab = "attempts" | "credentials" | "plugins";
export type AccountTab = "credentials" | "plugins" | "assistant";

function createAppStore() {
  const courses = ref<Course[]>([]);
  const retrievalMode = ref<RetrievalMode | null>(null);
  const modelCatalog = ref<ModelCatalog>(FAIL_CLOSED_MODEL_CATALOG);
  const modelCatalogLoadSucceeded = ref(false);
  const selectedCourseId = ref("");
  const selectedModelKey = ref("");
  const answerMode = ref<AnswerMode>(readStoredAnswerMode());
  const tone = ref<Tone>(readStoredTone());
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
  const pendingExamPlan = ref<ExamReviewPlanPreview | null>(null);
  const isPreviewingExamPlan = ref(false);

  const lastWorkflowType = ref<WorkflowType>("knowledge_qa");
  const workflowOverride = ref<WorkflowType | null>(null);
  const routeDecision = computed(() => routeWorkflow(userInput.value, lastWorkflowType.value));
  const workflowType = computed<WorkflowType>({
    get: () => workflowOverride.value ?? routeDecision.value.workflowType,
    set: (value) => {
      workflowOverride.value = value;
    },
  });

  const railOpen = ref(
    typeof window === "undefined" || window.innerWidth >= 1024,
  );
  // 窄屏下检查器是浮层，默认展开会盖住记录区；宽屏是常驻第三列，默认展开。
  const inspectorOpen = ref(
    typeof window === "undefined" || window.innerWidth >= 1280,
  );
  const inspectorTab = ref<InspectorTab>("attempts");
  const drawerOpen = ref(false);

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
  // 账户偏好保存请求串行化并合并：多个 watcher 连续触发时只关心最新快照。
  const preferenceSaveQueue = createLatestSaveQueue();

  const selectedCourse = computed(() =>
    courses.value.find((course) => course.course_id === selectedCourseId.value),
  );
  const hasSelectableCourse = computed(() => courses.value.some((course) => course.selectable));
  const activeWorkflow = computed(() => workflowCopy[workflowType.value]);
  const workflowRouteIsManual = computed(() => workflowOverride.value !== null);
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

  // 左轨按课程分文件夹；每个文件夹下是该课程的全部会话（含多次回答尝试）。
  const historyFolders = computed(() => {
    const order: string[] = [];
    const groups = new Map<string, ConversationSummary[]>();
    for (const conversation of conversationHistory.value) {
      const courseId = conversation.course_id || "__uncategorized__";
      if (!groups.has(courseId)) {
        groups.set(courseId, []);
        order.push(courseId);
      }
      groups.get(courseId)!.push(conversation);
    }
    return order.map((courseId) => ({
      courseId,
      label: courseId === "__uncategorized__" ? "未分类" : courseName(courseId),
      conversations: groups.get(courseId)!,
    }));
  });

  const openFolderIds = ref<string[]>([]);
  const accountMenuOpen = ref(false);
  const accountTab = ref<AccountTab>("credentials");
  // 外观主题偏好（0 Auto / 1 恒亮 / 2 恒暗）：设备级设置，登出不清除；
  // 当前存 localStorage，后续作为用户设置字段与 API Key 一同同步到服务器。
  const themeMode = ref<ThemeMode>(readStoredThemeMode());
  applyThemeMode(themeMode.value);
  watch(themeMode, (mode) => {
    writeStoredThemeMode(mode);
    applyThemeMode(mode);
    persistAccountPreferences();
  });

  // 强调色（品牌色）偏好：靛青 / 朱砂。设备级设置，登出不清除。
  const accentTheme = ref<AccentTheme>(readStoredAccent());
  applyAccent(accentTheme.value);
  watch(accentTheme, (accent) => {
    writeStoredAccent(accent);
    applyAccent(accent);
    persistAccountPreferences();
  });

  watch(answerMode, (mode) => {
    writeStoredAnswerMode(mode);
    persistAccountPreferences();
  });
  watch(tone, (nextTone) => {
    writeStoredTone(nextTone);
    persistAccountPreferences();
  });

  // 个人中心偏好：随 GitHub 账号跨设备同步（服务端 user_preferences）。
  // 主题在本地仍作为即时缓存（登出/未登录可用），登录后再与账号同步。
  let suppressPreferenceSave = false;
  const PREFERENCE_KEYS = {
    themeMode: "theme_mode",
    accentTheme: "accent_theme",
    answerMode: "answer_mode",
    tone: "tone",
  } as const;

  function buildPreferenceSnapshot(): Record<string, string> {
    return {
      [PREFERENCE_KEYS.themeMode]: String(themeMode.value),
      [PREFERENCE_KEYS.accentTheme]: accentTheme.value,
      [PREFERENCE_KEYS.answerMode]: answerMode.value,
      [PREFERENCE_KEYS.tone]: tone.value,
    };
  }

  function persistAccountPreferences(): void {
    if (suppressPreferenceSave) return;
    const user = currentUser.value;
    if (!user || user.is_mock) return;
    // 保存请求串行化并合并：只提交最新快照；旧请求完成后发现序号过期会补发
    // 最新快照，保证服务端收敛。失败非阻断，保留 localStorage 即时体验。
    preferenceSaveQueue.submit(async () => {
      await saveAccountPreferences(buildPreferenceSnapshot());
    });
  }

  async function loadAccountPreferences(): Promise<void> {
    const user = currentUser.value;
    if (!user || user.is_mock) return;
    try {
      const { preferences } = await getAccountPreferences();
      suppressPreferenceSave = true;
      if (preferences[PREFERENCE_KEYS.themeMode] !== undefined) {
        const parsed = Number(preferences[PREFERENCE_KEYS.themeMode]);
        if (Number.isFinite(parsed)) setThemeMode(parsed);
      }
      if (preferences[PREFERENCE_KEYS.accentTheme] !== undefined) {
        setAccentTheme(preferences[PREFERENCE_KEYS.accentTheme]);
      }
      const answer = preferences[PREFERENCE_KEYS.answerMode];
      if (answer !== undefined) answerMode.value = parseAnswerMode(answer);
      const storedTone = preferences[PREFERENCE_KEYS.tone];
      if (storedTone !== undefined) tone.value = parseTone(storedTone);
    } finally {
      suppressPreferenceSave = false;
    }
  }

  // 一次手动纠正只作用于当前草稿；发送后输入下一条内容时重新启用自动路由。
  watch(userInput, (value, previous) => {
    if (!previous.trim() && value.trim()) workflowOverride.value = null;
  });

  function folderIsOpen(courseId: string): boolean {
    return openFolderIds.value.includes(courseId);
  }

  function toggleFolder(courseId: string): void {
    openFolderIds.value = folderIsOpen(courseId)
      ? openFolderIds.value.filter((id) => id !== courseId)
      : [...openFolderIds.value, courseId];
  }

  function revealFolderFor(courseId: string): void {
    if (courseId && !folderIsOpen(courseId)) {
      openFolderIds.value = [...openFolderIds.value, courseId];
    }
  }

  function startNewConversationInCourse(courseId: string): void {
    isApplyingHistoryCourse = true;
    selectedCourseId.value = courseId;
    isApplyingHistoryCourse = false;
    revealFolderFor(courseId);
    startNewConversation();
  }

  function githubAvatarUrl(): string {
    const login = currentUser.value?.github_login;
    return login ? `https://github.com/${login}.png?size=96` : "";
  }

  function openAccountTab(tab: AccountTab): void {
    accountTab.value = tab;
  }

  // 收口主题档位写入：滑块拖动与键盘都走这里，非法值被夹回 0..2。
  function setThemeMode(mode: number): void {
    themeMode.value = Math.min(2, Math.max(0, Math.round(mode))) as ThemeMode;
  }

  // 收口强调色写入：非法值回退默认靛青。
  function setAccentTheme(accent: unknown): void {
    accentTheme.value =
      accent === "vermilion" || accent === "indigo" ? accent : "indigo";
  }

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
  const activeAttempt = computed<WorkflowAttempt | null>(
    () =>
      attempts.value.find((attempt) => attempt.workflow_run_id === selectedAttemptId.value) ??
      null,
  );
  const activeAttemptIndex = computed(() =>
    attempts.value.findIndex((attempt) => attempt.workflow_run_id === selectedAttemptId.value),
  );
  const displayedAnswerMode = computed<AnswerMode | null>(() =>
    activeAttempt.value?.request.answer_mode ?? (isRunning.value ? answerMode.value : null),
  );
  const displayedTone = computed<Tone | null>(() =>
    activeAttempt.value?.request.tone ?? (isRunning.value ? tone.value : null),
  );
  // 会话内所有已完成回答，按顺序渲染成连续对话（不再按"第 N 次"切分）。
  const completedTurns = computed(() =>
    (conversationSnapshot.value?.runs ?? []).map((run) => ({
      id: run.workflow_run_id,
      ask: run.request.user_input,
      result: run.result,
      answerMode: run.request.answer_mode,
      tone: run.request.tone,
    })),
  );
  // 记录区展示的提问：优先取选中尝试的请求，其次取正在输入的草稿。
  const transcriptAsk = computed(() => {
    if (activeAttempt.value) return activeAttempt.value.request.user_input;
    if (isRunning.value) return userInput.value;
    return "";
  });
  const transcriptHasContent = computed(
    () => Boolean(result.value) || Boolean(workflowStreamState.value) || isRunning.value,
  );
  // 只有这三个 Workflow 带专属字段；其余进抽屉只为输出偏好。
  const workflowHasExtraFields = computed(() =>
    ["exam_review", "problem_tutor", "mistake_review", "temporary_material_reading"].includes(
      workflowType.value,
    ),
  );
  const canSubmitWorkflow = computed(
    () =>
      !isRunning.value &&
      !isLoadingCourses.value &&
      !isLoadingModels.value &&
      Boolean(currentUser.value) &&
      Boolean(selectedCourse.value?.selectable) &&
      Boolean(selectedModel.value?.user_selectable),
  );
  const runtimeNoticeTitle = computed(() =>
    selectedModelIsMock.value
      ? "迭代 0 Mock，不是正式 OAuth / 模型 / 检索"
      : "模型由服务端目录自动选取，不会自动切换模型或 BYOK",
  );
  const runtimeNoticeDetail = computed(() => {
    if (selectedModelIsMock.value) {
      return "当前页面保留 Mock 持久化路径；未伪装成真实平台默认模型。";
    }
    if (!isLoadingModels.value && !modelCatalogLoadSucceeded.value) {
      return "模型目录加载失败，平台、Mock 与 BYOK 请求均已关闭。";
    }
    if (!modelCatalog.value.real_platform_default_available) {
      return "正式平台默认池不可用；本次使用服务端选中的可用模型。";
    }
    return "请求会携带当前模型来源、供应商和模型 ID。";
  });

  function courseName(courseId: string): string {
    return courses.value.find((course) => course.course_id === courseId)?.display_name ?? courseId;
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
    const status = byokCredentialStatus(provider.provider_id);
    // 后端契约：未配置的供应商 writable=false（没有可管理的既有凭据），
    // 但此时恰恰允许首次保存。因此只有「已配置且当前会话只读」才禁止保存。
    const writableForSave = status === null || !status.configured || status.writable;
    return Boolean(
      byokRuntimeAvailable.value &&
        canManageByokCredentials(currentUser.value) &&
        provider.enabled &&
        writableForSave &&
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

  function openInspector(tab: InspectorTab): void {
    inspectorTab.value = tab;
    inspectorOpen.value = true;
  }

  // Enter 提交，Shift+Enter 换行：与 composer 的对话预期一致。
  function onComposerKeydown(event: KeyboardEvent): void {
    if (event.key !== "Enter" || event.shiftKey || event.isComposing) return;
    event.preventDefault();
    if (canSubmitWorkflow.value) void submitWorkflow();
  }

  function setHistoryMessage(message: string, isError = false): void {
    historyMessage.value = message;
    historyMessageIsError.value = isError;
  }

  // 尽力通知服务端打断运行。显式取消、切换会话、离开页面都走这里；
  // 纯网络断开不会触发（运行在服务端继续完成，稍后重新读取可取回结果）。
  function requestServerCancel(): void {
    const runId = workflowStreamState.value?.workflowRunId;
    if (!runId) return;
    void cancelWorkflowRun(runId).catch(() => {
      // 服务端取消失败（如网络又断了）不阻塞本地断开；运行可能后台完成。
    });
  }

  function abortActiveWorkflow(detail: string): void {
    if (activeWorkflowStream && !activeWorkflowStream.signal.aborted) {
      requestServerCancel();
      activeWorkflowStream.abort(detail);
    }
    canCancelWorkflow.value = false;
  }

  function clearActiveConversation(): void {
    abortActiveWorkflow("当前会话已切换，运行已取消。");
    stopNetworkRecovery();
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
    revealFolderFor(conversation.course_id);

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

    const selectedWorkflow = workflowType.value;
    return buildWorkflowRequest({
      ...common,
      workflowType: selectedWorkflow,
      workflowPayload: buildRoutedWorkflowPayload(selectedWorkflow, userInput.value, {
        syllabus: syllabus.value,
        examDate: examDate.value,
        availableHours: availableHours.value,
        goals: splitList(goalsText.value),
        weakTopics: splitList(weakTopicsText.value),
        userAnswer: userAnswer.value,
        helpLevel: helpLevel.value,
        problemSource: problemSource.value,
        originalAnswer: originalAnswer.value,
        referenceAnswer: referenceAnswer.value,
        reviewFocus: reviewFocus.value,
        materialTitle: materialTitle.value,
        readingGoal: readingGoal.value,
      }),
    });
  }

  function validateForm(): string | null {
    if (!currentUser.value) return "请先使用 GitHub 登录。";
    if (!selectedCourseId.value) return "请先选择课程。";
    if (!selectedCourse.value?.selectable) return courseSelectionError(selectedCourse.value);
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
        loadAccountPreferences(),
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
      const catalog = await getCourses();
      courses.value = catalog.courses;
      retrievalMode.value = catalog.retrieval_mode;
      selectedCourseId.value = selectSelectableCourseId(
        courses.value,
        selectedCourseId.value,
      );
    } catch (error) {
      applyAuthFailure(error);
      errorMessage.value = toMessage(error);
    } finally {
      isLoadingCourses.value = false;
    }
  }

  function onPluginChanged(): void {
    // 插件装载/卸载后，课程列表与各课程插件状态需与个人中心同步刷新。
    void loadCourses();
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

  // 断网/协议中断后的自动取回：流断了但服务端仍在跑，轮询会话直到拿到
  // 终态或超时，避免学生必须手动刷新整个网页才能看到结果。
  let networkRecoveryTimer: number | null = null;

  function stopNetworkRecovery(): void {
    if (networkRecoveryTimer !== null) {
      window.clearInterval(networkRecoveryTimer);
      networkRecoveryTimer = null;
    }
  }

  function scheduleNetworkRecovery(targetConversationId: string): void {
    stopNetworkRecovery();
    let tries = 0;
    networkRecoveryTimer = window.setInterval(() => {
      tries += 1;
      if (
        tries > 12 ||
        conversationId.value !== targetConversationId ||
        isRunning.value
      ) {
        // 已超时（约 60 秒）、会话已切换或用户已发起新运行：停止轮询。
        if (tries > 12 || conversationId.value !== targetConversationId) {
          stopNetworkRecovery();
        }
        return;
      }
      void loadConversationFromHistory(targetConversationId, "", false).catch(() => {});
    }, 5_000);
    window.setTimeout(() => stopNetworkRecovery(), 70_000);
  }

  async function submitWorkflow(): Promise<void> {
    // 发送即收起「更多选项」抽屉：无论校验是否通过都收起，不做任何条件判断。
    drawerOpen.value = false;
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
      lastWorkflowType.value = request.workflow_type;
      if (request.workflow_type === "exam_review" && !pendingExamPlan.value) {
        isPreviewingExamPlan.value = true;
        try {
          pendingExamPlan.value = await previewExamReviewPlan(request);
          noticeMessage.value = "复习计划已生成，请确认后开始运行。";
        } finally {
          isPreviewingExamPlan.value = false;
          isRunning.value = false;
        }
        return;
      }
      if (request.workflow_type === "exam_review" && pendingExamPlan.value) {
        await recordExamReviewPlanDecision(
          activeConversationId,
          "confirmed",
          pendingExamPlan.value.plan,
        );
      }
      // 请求已构建完成即视为发送受理：清空主输入框，
      // 「更多选项」等抽屉配置保持不变，方便连发不同问题。
      userInput.value = "";
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
        } else if (
          streamError?.code === "stream_request_failed" ||
          streamError?.code === "stream_protocol_error"
        ) {
          // 网络/协议中断：断线不再取消运行，服务端会继续执行并保存终态。
          // 自动轮询取回结果，学生无需手动刷新整个网页。
          errorMessage.value = streamError?.detail ?? "流式连接中断，请检查网络后重试。";
          scheduleNetworkRecovery(activeConversationId);
        } else {
          errorMessage.value = streamError?.detail ?? "流式运行未返回最终结果。";
        }
        return;
      }

      result.value = workflowResult;
      pendingExamPlan.value = null;
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
    // 显式取消：先通知服务端打断运行（断线已不再自动等于取消），再本地断开。
    abortActiveWorkflow("已取消本次运行。");
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

  return reactive({
    // 运行时与课程
    courses,
    retrievalMode,
    modelCatalog,
    modelCatalogLoadSucceeded,
    selectedCourseId,
    selectedModelKey,
    workflowType,
    routeDecision,
    workflowRouteIsManual,
    answerMode,
    tone,
    knowledgeScope,
    includeBilibiliResources,
    userInput,
    // 抽屉字段
    syllabus,
    examDate,
    availableHours,
    goalsText,
    weakTopicsText,
    userAnswer,
    helpLevel,
    problemSource,
    originalAnswer,
    referenceAnswer,
    reviewFocus,
    materialTitle,
    readingGoal,
    // UI 状态
    railOpen,
    inspectorOpen,
    inspectorTab,
    drawerOpen,
    accountMenuOpen,
    accountTab,
    themeMode,
    accentTheme,
    openFolderIds,
    // 会话
    conversationId,
    conversationHistory,
    conversationSnapshot,
    selectedAttemptId,
    result,
    isLoadingCourses,
    isLoadingModels,
    isLoadingHistory,
    loadingConversationId,
    editingConversationId,
    conversationTitleDraft,
    renamingConversationId,
    deleteConfirmId,
    deletingConversationId,
    isRegenerating,
    isRunning,
    pendingExamPlan,
    isPreviewingExamPlan,
    rejectExamPlan: async () => {
      if (!pendingExamPlan.value || !conversationId.value) return;
      await recordExamReviewPlanDecision(conversationId.value, "rejected", pendingExamPlan.value.plan);
      pendingExamPlan.value = null;
      noticeMessage.value = "已放弃本次复习计划。";
    },
    canCancelWorkflow,
    workflowStreamState,
    isReloading,
    errorMessage,
    noticeMessage,
    modelCatalogMessage,
    currentUser,
    isLoadingAuth,
    authMessage,
    historyMessage,
    historyMessageIsError,
    // BYOK
    byokCredentialStatuses,
    byokKeyDrafts,
    isLoadingByokCredentials,
    savingByokProviderId,
    deletingByokProviderId,
    byokMessage,
    byokMessageIsError,
    // 计算属性
    selectedCourse,
    hasSelectableCourse,
    activeWorkflow,
    byokCatalogIsCurrent,
    byokProvidersForDisplay,
    byokRuntimeAvailable,
    modelsForSelection,
    selectedModel,
    selectedModelIsMock,
    attempts,
    latestAttempt,
    historyFolders,
    historyIsBusy,
    byokIsBusy,
    activeAttempt,
    activeAttemptIndex,
    displayedAnswerMode,
    displayedTone,
    completedTurns,
    transcriptAsk,
    transcriptHasContent,
    workflowHasExtraFields,
    canSubmitWorkflow,
    runtimeNoticeTitle,
    runtimeNoticeDetail,
    // 动作
    folderIsOpen,
    toggleFolder,
    revealFolderFor,
    startNewConversationInCourse,
    githubAvatarUrl,
    openAccountTab,
    setThemeMode,
    setAccentTheme,
    courseName,
    byokCredentialStatus,
    byokProviderDisabledReason,
    canSaveByokCredential,
    canDeleteByokCredential,
    byokCredentialWritable,
    clearUnavailableByokSelection,
    openInspector,
    onComposerKeydown,
    startNewConversation,
    beginRename,
    cancelRename,
    beginDelete,
    cancelDelete,
    loadConversationFromHistory,
    saveConversationTitle,
    confirmDeleteConversation,
    regenerateLatestAttempt,
    submitWorkflow,
    cancelWorkflow,
    reloadConversation,
    submitByokCredential,
    removeByokCredential,
    startGithubLogin,
    signOut,
    loadAuth,
    loadCourses,
    onPluginChanged,
    loadModels,
    abortActiveWorkflow,
  });
}

let storeInstance: ReturnType<typeof createAppStore> | null = null;

export function useAppStore() {
  if (!storeInstance) storeInstance = createAppStore();
  return storeInstance;
}
