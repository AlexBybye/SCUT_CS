import { describe, expect, it } from "vitest";
import {
  ACCENT_ATTR_VALUE,
  ACCENT_LABELS,
  ACCENT_STORAGE_KEY,
  DEFAULT_ACCENT,
  DEFAULT_THEME_MODE,
  THEME_ATTR_VALUE,
  THEME_MODE_LABELS,
  THEME_MODE_STORAGE_KEY,
  isAccentTheme,
  parseAccentTheme,
  parseThemeMode,
  readStoredAccent,
  readStoredThemeMode,
  resolveTheme,
  writeStoredAccent,
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

describe("强调色（品牌色）偏好", () => {
  it("解析只接受 indigo / vermilion，其余回退默认靛青", () => {
    expect(parseAccentTheme("indigo")).toBe("indigo");
    expect(parseAccentTheme("vermilion")).toBe("vermilion");
    expect(parseAccentTheme("VERMILION")).toBe("vermilion");
    expect(parseAccentTheme("blue")).toBe(DEFAULT_ACCENT);
    expect(parseAccentTheme("")).toBe(DEFAULT_ACCENT);
    expect(parseAccentTheme(null)).toBe(DEFAULT_ACCENT);
    expect(parseAccentTheme(undefined)).toBe(DEFAULT_ACCENT);
  });

  it("isAccentTheme 仅识别两个品牌色", () => {
    expect(isAccentTheme("indigo")).toBe(true);
    expect(isAccentTheme("vermilion")).toBe(true);
    expect(isAccentTheme("indigo ")).toBe(false);
    expect(isAccentTheme("Indigo")).toBe(false);
  });

  it("localStorage 读写强调色，键名独立于明暗模式", () => {
    const storage = fakeStorage();
    writeStoredAccent("vermilion", storage);
    expect(storage.getItem(ACCENT_STORAGE_KEY)).toBe("vermilion");
    expect(readStoredAccent(storage)).toBe("vermilion");
    // 强调色存储与明暗模式互不影响。
    expect(storage.getItem(THEME_MODE_STORAGE_KEY)).toBeNull();
  });

  it("存储脏数据与不可用存储回退默认靛青", () => {
    expect(readStoredAccent(fakeStorage({ [ACCENT_STORAGE_KEY]: "purple" }))).toBe(
      DEFAULT_ACCENT,
    );
    expect(readStoredAccent(null)).toBe(DEFAULT_ACCENT);
    expect(() => writeStoredAccent("indigo", null)).not.toThrow();
  });

  it("强调色有展示名与 data-accent 属性映射", () => {
    expect(ACCENT_LABELS.indigo).toBe("靛青");
    expect(ACCENT_LABELS.vermilion).toBe("朱砂");
    expect(ACCENT_ATTR_VALUE.indigo).toBe("indigo");
    expect(ACCENT_ATTR_VALUE.vermilion).toBe("vermilion");
  });
});
