import { describe, expect, it } from "vitest";
import { canManageByokCredentials } from "../byokSession";

describe("canManageByokCredentials", () => {
  it("只允许真实 GitHub 身份管理 BYOK", () => {
    expect(canManageByokCredentials({ is_mock: false })).toBe(true);
    expect(canManageByokCredentials({ is_mock: true })).toBe(false);
    expect(canManageByokCredentials(null)).toBe(false);
  });
});
