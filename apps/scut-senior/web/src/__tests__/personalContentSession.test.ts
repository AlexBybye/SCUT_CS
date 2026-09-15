import { afterEach, describe, expect, it, vi } from "vitest";
import { clearContentHandoff, isValidContributorEmail, readContentHandoff, readContributorEmail, saveContributorEmail, writeContentHandoff } from "../personalContentSession";

afterEach(() => { vi.unstubAllGlobals(); clearContentHandoff(); });
describe("contributor attribution session", () => {
  it("accepts GitHub noreply and rejects malformed or header-injection addresses", () => {
    expect(isValidContributorEmail("12345+student@users.noreply.github.com")).toBe(true);
    for (const value of ["", "student", "student@example", "s@example.com\r\nBcc:x@y.com", "<s@example.com>"]) {
      expect(isValidContributorEmail(value)).toBe(false);
    }
  });
  it("keeps users isolated and survives unavailable storage", () => {
    vi.stubGlobal("sessionStorage", { getItem() { throw new Error("blocked"); }, setItem() { throw new Error("blocked"); } });
    saveContributorEmail("user-a", " student@example.com ");
    expect(readContributorEmail("user-a")).toBe("student@example.com");
    expect(readContributorEmail("user-b")).toBe("");
    expect(() => saveContributorEmail("user-a", "invalid")).toThrow();
  });
  it("does not restore corrupted persisted data", () => {
    vi.stubGlobal("sessionStorage", { getItem: () => "{broken-json-or-invalid-email}" });
    expect(readContributorEmail("corrupt-user")).toBe("");
  });
});
describe("contribution handoff", () => {
  it("does not persist full content or expose another user's body", () => {
    const setItem = vi.fn();
    vi.stubGlobal("sessionStorage", { setItem });
    writeContentHandoff({ user_id: "a", course_id: "os", title: "笔记", content: "private body" });
    expect(readContentHandoff("b")).toBeNull();
    expect(readContentHandoff("a")?.content).toBe("private body");
    clearContentHandoff("b");
    expect(readContentHandoff("a")).not.toBeNull();
    clearContentHandoff("a");
    expect(readContentHandoff("a")).toBeNull();
    expect(setItem).not.toHaveBeenCalled();
  });
});
