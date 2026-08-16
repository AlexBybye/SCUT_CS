import { describe, expect, it } from "vitest";
import type {
  ByokCredentialStatus,
  ByokProviderCatalogItem,
  ModelCatalogItem,
} from "../contracts";
import {
  configuredByokModelOptions,
  initialModelSelectionKey,
  modelKey,
  modelsForRuntime,
} from "../modelSelection";

const mockModel: ModelCatalogItem = {
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

const platformModel: ModelCatalogItem = {
  provider_id: "openrouter",
  model_id: "google/gemma-4-26b-a4b-it:free",
  company: "Google",
  display_name: "Gemma 4 26B A4B",
  model_source: "platform_default",
  billing_label: "platform_daily_free_quota",
  availability_status: "available",
  context_length: 262_144,
  input_modalities: ["text"],
  supports_structured_outputs: true,
  is_preview: false,
  user_selectable: true,
  last_checked_at: "2026-08-16T00:00:00Z",
};

describe("initialModelSelectionKey", () => {
  it("真实平台目录可用时保持空值，要求用户显式选择", () => {
    expect(
      initialModelSelectionKey(
        { real_platform_default_available: true },
        [platformModel],
        mockModel,
      ),
    ).toBe("");
  });

  it("Mock 模式明确保留可选 Mock 默认路径", () => {
    expect(
      initialModelSelectionKey(
        { real_platform_default_available: false },
        [platformModel, mockModel],
        mockModel,
      ),
    ).toBe(modelKey(mockModel));
  });
});

describe("modelsForRuntime", () => {
  it("does not invent a Mock option when configured platform health fails", () => {
    const unhealthy = { ...platformModel, user_selectable: false };
    expect(
      modelsForRuntime(
        { platform_credential_configured: true },
        [unhealthy],
        mockModel,
        true,
      ),
    ).toEqual([unhealthy]);
  });

  it("adds the explicit Mock path only for a server without platform credentials", () => {
    expect(
      modelsForRuntime(
        { platform_credential_configured: false },
        [],
        mockModel,
        true,
      ),
    ).toEqual([mockModel]);
  });

  it("模型目录请求失败时关闭请求路径，不凭空生成 Mock", () => {
    expect(
      modelsForRuntime(
        { platform_credential_configured: false },
        [],
        mockModel,
        false,
      ),
    ).toEqual([]);
  });
});

const byokProviders: ByokProviderCatalogItem[] = [
  {
    provider_id: "openrouter",
    company: "OpenRouter",
    display_name: "OpenRouter",
    enabled: true,
    models_confirmed: true,
    models: [
      {
        model_id: "deepseek/deepseek-v4-flash-0731",
        company: "DeepSeek",
        display_name: "DeepSeek V4 Flash",
      },
    ],
    custom_base_url_allowed: false,
    endpoint_policy: "fixed_provider_endpoint",
  },
  {
    provider_id: "siliconflow",
    company: "SiliconFlow",
    display_name: "硅基流动",
    enabled: false,
    models_confirmed: true,
    models: [
      {
        model_id: "Pro/zai-org/GLM-4.7",
        company: "Z.ai",
        display_name: "GLM-4.7 Pro",
      },
    ],
    custom_base_url_allowed: false,
    endpoint_policy: "fixed_provider_endpoint",
  },
];

const byokStatuses: ByokCredentialStatus[] = [
  {
    provider_id: "openrouter",
    model_id: "deepseek/deepseek-v4-flash-0731",
    configured: true,
    masked_key: "sk-or-****1234",
    expires_at: "2026-08-20T08:00:00Z",
  },
  {
    provider_id: "siliconflow",
    model_id: "Pro/zai-org/GLM-4.7",
    configured: true,
    masked_key: "sk-****5678",
    expires_at: "2026-08-20T08:00:00Z",
  },
];

describe("configuredByokModelOptions", () => {
  it("仅为 enabled 且本会话已配置的供应商生成固定 user_key 模型", () => {
    expect(configuredByokModelOptions(byokProviders, byokStatuses)).toEqual([
      expect.objectContaining({
        provider_id: "openrouter",
        model_id: "deepseek/deepseek-v4-flash-0731",
        model_source: "user_key",
        company: "OpenRouter",
        display_name: "DeepSeek · DeepSeek V4 Flash",
        user_selectable: true,
      }),
    ]);
  });

  it("供应商关闭时即使状态声称已配置也不生成模型选项", () => {
    expect(
      configuredByokModelOptions(
        byokProviders.filter((provider) => provider.provider_id === "siliconflow"),
        byokStatuses,
      ),
    ).toEqual([]);
  });

  it("凭据状态的模型 ID 与固定目录不一致时保持关闭", () => {
    expect(
      configuredByokModelOptions(byokProviders, [
        { ...byokStatuses[0]!, model_id: "user-supplied-model" },
      ]),
    ).toEqual([]);
  });
});
