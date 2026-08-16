import { describe, expect, it } from "vitest";
import type { ByokProviderCatalogItem } from "../contracts";
import {
  BYOK_CATALOG_VERSION,
  FROZEN_BYOK_PROVIDERS,
  isCurrentByokCatalogVersion,
  mergeByokProvidersForDisplay,
} from "../byokCatalog";

describe("frozen BYOK display catalog", () => {
  it("fail-closed fallback 始终只展示四家固定供应商与唯一模型", () => {
    expect(
      FROZEN_BYOK_PROVIDERS.map((provider) => ({
        provider_id: provider.provider_id,
        enabled: provider.enabled,
        model_id: provider.models[0]?.model_id,
        custom_base_url_allowed: provider.custom_base_url_allowed,
      })),
    ).toEqual([
      {
        provider_id: "openrouter",
        enabled: false,
        model_id: "deepseek/deepseek-v4-flash-0731",
        custom_base_url_allowed: false,
      },
      {
        provider_id: "deepseek",
        enabled: false,
        model_id: "deepseek-v4-flash",
        custom_base_url_allowed: false,
      },
      {
        provider_id: "siliconflow",
        enabled: false,
        model_id: "Pro/zai-org/GLM-4.7",
        custom_base_url_allowed: false,
      },
      {
        provider_id: "zhipu",
        enabled: false,
        model_id: "glm-5.2",
        custom_base_url_allowed: false,
      },
    ]);
  });

  it("仅用服务端同 ID 条目覆盖启用状态，缺失条目继续禁用展示", () => {
    const serverOpenRouter = { ...FROZEN_BYOK_PROVIDERS[0]!, enabled: true };
    const displayed = mergeByokProvidersForDisplay([serverOpenRouter]);

    expect(displayed).toHaveLength(4);
    expect(displayed[0]?.enabled).toBe(true);
    expect(displayed.slice(1).every((provider) => !provider.enabled)).toBe(true);
  });

  it("拒绝同 ID 下篡改模型、URL 策略或额外字段的旧目录", () => {
    const frozen = FROZEN_BYOK_PROVIDERS[0]!;
    const candidates = [
      {
        ...frozen,
        enabled: true,
        models: [{ ...frozen.models[0]!, model_id: "user-controlled-model" }],
      },
      { ...frozen, enabled: true, custom_base_url_allowed: true },
      { ...frozen, enabled: true, base_url: "https://evil.invalid/v1" },
    ] as unknown as ByokProviderCatalogItem[];

    for (const candidate of candidates) {
      expect(mergeByokProvidersForDisplay([candidate])[0]).toEqual(frozen);
      expect(mergeByokProvidersForDisplay([candidate])[0]?.enabled).toBe(false);
    }
  });

  it("只信任当前 v4 目录版本", () => {
    expect(isCurrentByokCatalogVersion(BYOK_CATALOG_VERSION)).toBe(true);
    expect(isCurrentByokCatalogVersion("byok-models-v3")).toBe(false);
    expect(isCurrentByokCatalogVersion("byok-models-v4-fail-closed")).toBe(false);
  });
});
