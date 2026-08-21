import { ApiError } from "./api";
import { FROZEN_BYOK_PROVIDERS } from "./byokCatalog";
import type {
  AnswerMode,
  ByokProviderId,
  HelpLevel,
  ModelCatalog,
  ModelCatalogItem,
  Tone,
  WorkflowType,
} from "./contracts";

export const ITERATION_ZERO_MOCK_MODEL: ModelCatalogItem = {
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

export const FAIL_CLOSED_MODEL_CATALOG: ModelCatalog = {
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

export function emptyByokKeyDrafts(): Record<ByokProviderId, string> {
  return { openrouter: "", deepseek: "", siliconflow: "", zhipu: "" };
}

export const workflowCopy: Record<
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

export const answerModeLabels: Record<AnswerMode, string> = {
  concise: "简短",
  detailed: "详细",
  example: "举例",
  step_by_step: "分步骤",
};

export const toneLabels: Record<Tone, string> = {
  teaching_assistant: "助教式",
  study_partner: "复习搭子",
  senior_student: "学长聊天",
};

export const helpLevelLabels: Record<HelpLevel, string> = {
  concept: "只讲知识点",
  approach: "给出思路",
  step_by_step: "分步骤提示",
  full_explanation: "完整讲解",
  answer_analysis: "分析我的答案",
};

export function modelOptionLabel(model: ModelCatalogItem): string {
  const suffixes = [
    model.billing_label === "platform_daily_free_quota" ? "平台每日免费" : "",
    model.is_preview ? "Preview" : "",
    model.user_selectable ? "" : "不可选",
  ].filter(Boolean);
  return `${model.company} · ${model.display_name}${suffixes.length ? ` / ${suffixes.join(" / ")}` : ""}`;
}

export function billingLabel(model: ModelCatalogItem): string {
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

export function availabilityLabel(model: ModelCatalogItem): string {
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

export function splitList(value: string): string[] {
  return value
    .split(/[，,\n]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

export function toMessage(error: unknown): string {
  if (error instanceof ApiError && error.status === 429) return error.message;
  return error instanceof Error ? error.message : "请求失败，请检查 API 服务是否运行。";
}

export function formatHistoryTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}
