import type { ByokProviderCatalogItem } from "./contracts";

export const BYOK_CATALOG_VERSION = "byok-models-v4";

export const FROZEN_BYOK_PROVIDERS: ByokProviderCatalogItem[] = [
  {
    provider_id: "openrouter",
    company: "OpenRouter",
    display_name: "OpenRouter",
    enabled: false,
    models_confirmed: true,
    models: [
      {
        model_id: "deepseek/deepseek-v4-flash-0731",
        company: "DeepSeek",
        display_name: "DeepSeek V4 Flash 0731",
      },
    ],
    custom_base_url_allowed: false,
    endpoint_policy: "fixed_provider_endpoint",
  },
  {
    provider_id: "deepseek",
    company: "DeepSeek",
    display_name: "DeepSeek",
    enabled: false,
    models_confirmed: true,
    models: [
      {
        model_id: "deepseek-v4-flash",
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
  {
    provider_id: "zhipu",
    company: "Zhipu AI",
    display_name: "智谱 AI",
    enabled: false,
    models_confirmed: true,
    models: [
      {
        model_id: "glm-5.2",
        company: "Zhipu AI",
        display_name: "GLM-5.2",
      },
    ],
    custom_base_url_allowed: false,
    endpoint_policy: "fixed_provider_endpoint",
  },
];

export function mergeByokProvidersForDisplay(
  serverProviders: readonly ByokProviderCatalogItem[],
): ByokProviderCatalogItem[] {
  return FROZEN_BYOK_PROVIDERS.map((fallback) => {
    const candidate = serverProviders.find(
      (provider) =>
        provider !== null &&
        typeof provider === "object" &&
        provider.provider_id === fallback.provider_id,
    );
    return candidate && providerMatchesFrozenContract(candidate, fallback)
      ? candidate
      : fallback;
  });
}

export function isCurrentByokCatalogVersion(value: string): boolean {
  return value === BYOK_CATALOG_VERSION;
}

function hasExactKeys(value: object, expected: readonly string[]): boolean {
  const keys = Object.keys(value).sort();
  return keys.length === expected.length && keys.every((key, index) => key === expected[index]);
}

function providerMatchesFrozenContract(
  candidate: ByokProviderCatalogItem,
  frozen: ByokProviderCatalogItem,
): boolean {
  const providerKeys = [
    "company",
    "custom_base_url_allowed",
    "display_name",
    "enabled",
    "endpoint_policy",
    "models",
    "models_confirmed",
    "provider_id",
  ].sort();
  const modelKeys = ["company", "display_name", "model_id"].sort();
  const candidateModel = Array.isArray(candidate.models) ? candidate.models[0] : undefined;
  const frozenModel = frozen.models[0];

  return Boolean(
    hasExactKeys(candidate, providerKeys) &&
      typeof candidate.enabled === "boolean" &&
      candidate.provider_id === frozen.provider_id &&
      candidate.company === frozen.company &&
      candidate.display_name === frozen.display_name &&
      candidate.models_confirmed === true &&
      candidate.custom_base_url_allowed === false &&
      candidate.endpoint_policy === "fixed_provider_endpoint" &&
      Array.isArray(candidate.models) &&
      candidate.models.length === 1 &&
      candidateModel &&
      typeof candidateModel === "object" &&
      frozenModel &&
      hasExactKeys(candidateModel, modelKeys) &&
      candidateModel.model_id === frozenModel.model_id &&
      candidateModel.company === frozenModel.company &&
      candidateModel.display_name === frozenModel.display_name,
  );
}
