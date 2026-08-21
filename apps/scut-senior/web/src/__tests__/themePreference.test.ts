import { describe, expect, it } from "vitest";
import {
  DEFAULT_THEME_MODE,
  THEME_ATTR_VALUE,
  THEME_MODE_LABELS,
  THEME_MODE_STORAGE_KEY,
  parseThemeMode,
  readStoredThemeMode,
  resolveTheme,
  writeStoredThemeMode,
} from "../themePreference";

function fakeStorage(initial: Record<string, string> = {}) {
  const map = new Map(Object.entries(initial));
  return {
    getItem: (key: string) => map.get(key) ?? null,
    setItem: (key: string, value: string) => {
      map.set(key, value);
    },
  };
}

describe("parseThemeMode", () => {
  it("接受 0/1/2 的数字与字符串", () => {
    expect(parseThemeMode(0)).toBe(0);
    expect(parseThemeMode(1)).toBe(1);
    expect(parseThemeMode(2)).toBe(2);
    expect(parseThemeMode("0")).toBe(0);
    expect(parseThemeMode("1")).toBe(1);
    expect(parseThemeMode("2")).toBe(2);
    expect(parseThemeMode(" 2 ")).toBe(2);
  });

  it("脏数据一律回退默认 Auto", () => {
    expect(parseThemeMode("3")).toBe(DEFAULT_THEME_MODE);
    expect(parseThemeMode("auto")).toBe(DEFAULT_THEME_MODE);
    expect(parseThemeMode("")).toBe(DEFAULT_THEME_MODE);
    expect(parseThemeMode(null)).toBe(DEFAULT_THEME_MODE);
    expect(parseThemeMode(undefined)).toBe(DEFAULT_THEME_MODE);
    expect(parseThemeMode(1.5)).toBe(DEFAULT_THEME_MODE);
    expect(parseThemeMode({})).toBe(DEFAULT_THEME_MODE);
  });
});

describe("localStorage 读写", () => {
  it("键名固定且值为字符串化的档位", () => {
    const storage = fakeStorage();
    writeStoredThemeMode(2, storage);
    expect(storage.getItem(THEME_MODE_STORAGE_KEY)).toBe("2");
    expect(readStoredThemeMode(storage)).toBe(2);
  });

  it("空存储与不可用存储回退默认 Auto", () => {
    expect(readStoredThemeMode(fakeStorage())).toBe(DEFAULT_THEME_MODE);
    expect(readStoredThemeMode(null)).toBe(DEFAULT_THEME_MODE);
  });

  it("存储里的非法值不致命，回退默认", () => {
    expect(readStoredThemeMode(fakeStorage({ [THEME_MODE_STORAGE_KEY]: "9" }))).toBe(0);
    expect(readStoredThemeMode(fakeStorage({ [THEME_MODE_STORAGE_KEY]: "dark" }))).toBe(0);
  });

  it("写 null 存储是安全空操作", () => {
    expect(() => writeStoredThemeMode(1, null)).not.toThrow();
  });
});

describe("resolveTheme", () => {
  it("太阳恒亮、月亮恒暗，与系统无关", () => {
    expect(resolveTheme(1, true)).toBe("light");
    expect(resolveTheme(1, false)).toBe("light");
    expect(resolveTheme(2, false)).toBe("dark");
    expect(resolveTheme(2, true)).toBe("dark");
  });

  it("Auto 跟随系统深色开关", () => {
    expect(resolveTheme(0, true)).toBe("dark");
    expect(resolveTheme(0, false)).toBe("light");
  });
});

describe("展示与 DOM 映射", () => {
  it("三档都有文案标签", () => {
    expect(Object.keys(THEME_MODE_LABELS).sort()).toEqual(["0", "1", "2"]);
    expect(THEME_MODE_LABELS[0]).toBe("自动");
  });

  it("data-theme 属性值：auto 交还媒体查询，明暗显式锁定", () => {
    expect(THEME_ATTR_VALUE[0]).toBe("auto");
    expect(THEME_ATTR_VALUE[1]).toBe("light");
    expect(THEME_ATTR_VALUE[2]).toBe("dark");
  });
});
