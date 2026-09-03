import { describe, expect, it } from "vitest";
import {
  BYOK_CATALOG_VERSION,
  isCurrentByokCatalogVersion,
} from "../byokCatalog";

describe("BYOK connection capability version", () => {
  it("只信任当前自定义连接协议版本", () => {
    expect(BYOK_CATALOG_VERSION).toBe("byok-connections-v1");
    expect(isCurrentByokCatalogVersion(BYOK_CATALOG_VERSION)).toBe(true);
    expect(isCurrentByokCatalogVersion("byok-models-v4")).toBe(false);
    expect(isCurrentByokCatalogVersion("byok-connections-v2")).toBe(false);
  });
});
