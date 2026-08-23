/**
 * 助手设置 · 外观主题偏好
 *
 * 两个正交的偏好轴，各自持久化到浏览器 localStorage：
 *
 * A. 明暗模式（三档滑块）
 *   0 = Auto（跟随系统明暗，默认）
 *   1 = 恒亮色（太阳）
 *   2 = 恒暗色（月亮）
 *
 * B. 强调色（品牌色，两个品牌色之一）
 *   "indigo"（默认，靛青）或 "vermilion"（朱砂）
 *
 * 未来作为用户设置字段与 API Key 一同存到服务器时，复用同一套语义。
 * 解析对脏数据宽容（非法值一律回退默认），保证换设备、清缓存或手改数据时
 * 页面不会进入未定义状态。
 */

export type ThemeMode = 0 | 1 | 2;
export type ResolvedTheme = "light" | "dark";
export type AccentTheme = "indigo" | "vermilion";

export const DEFAULT_THEME_MODE: ThemeMode = 0;
export const DEFAULT_ACCENT: AccentTheme = "indigo";

/** localStorage 键名：一旦上线就不再改动，避免丢用户已保存的偏好。 */
export const THEME_MODE_STORAGE_KEY = "scut_senior_assistant_theme_mode";
export const ACCENT_STORAGE_KEY = "scut_senior_assistant_accent";

/** <html data-theme> 的取值；auto 交还给 CSS 媒体查询，避免首帧闪烁。 */
export const THEME_ATTR_VALUE: Record<ThemeMode, "auto" | "light" | "dark"> = {
  0: "auto",
  1: "light",
  2: "dark",
};

export const THEME_MODE_LABELS: Record<ThemeMode, string> = {
  0: "自动",
  1: "恒亮色",
  2: "恒暗色",
};

/** 强调色展示名（供个人中心的品牌色选择器使用）。 */
export const ACCENT_LABELS: Record<AccentTheme, string> = {
  indigo: "靛青",
  vermilion: "朱砂",
};

/** <html data-accent> 的取值；indigo 缺省时可不写。 */
export const ACCENT_ATTR_VALUE: Record<AccentTheme, string> = {
  indigo: "indigo",
  vermilion: "vermilion",
};

export function isThemeMode(value: unknown): value is ThemeMode {
  return value === 0 || value === 1 || value === 2;
}

export function isAccentTheme(value: unknown): value is AccentTheme {
  return value === "indigo" || value === "vermilion";
}

/** 宽容解析：接受 0/1/2 的数字或字符串，其余一律回退默认 Auto。 */
export function parseThemeMode(value: unknown): ThemeMode {
  if (typeof value === "number") return isThemeMode(value) ? value : DEFAULT_THEME_MODE;
  if (typeof value === "string") {
    const normalized = value.trim();
    if (normalized === "0") return 0;
    if (normalized === "1") return 1;
    if (normalized === "2") return 2;
  }
  return DEFAULT_THEME_MODE;
}

/** 宽容解析：接受 "indigo"/"vermilion"（大小写不敏感），其余回退默认靛青。 */
export function parseAccentTheme(value: unknown): AccentTheme {
  if (typeof value === "string" && isAccentTheme(value.trim().toLowerCase())) {
    return value.trim().toLowerCase() as AccentTheme;
  }
  return DEFAULT_ACCENT;
}

type StorageLike = Pick<Storage, "getItem" | "setItem">;

function defaultStorage(): StorageLike | null {
  try {
    // 隐私模式等场景下访问 localStorage 可能直接抛错。
    return typeof localStorage === "undefined" ? null : localStorage;
  } catch {
    return null;
  }
}

export function readStoredThemeMode(
  storage: StorageLike | null = defaultStorage(),
): ThemeMode {
  if (!storage) return DEFAULT_THEME_MODE;
  try {
    return parseThemeMode(storage.getItem(THEME_MODE_STORAGE_KEY));
  } catch {
    return DEFAULT_THEME_MODE;
  }
}

export function writeStoredThemeMode(
  mode: ThemeMode,
  storage: StorageLike | null = defaultStorage(),
): void {
  if (!storage) return;
  try {
    storage.setItem(THEME_MODE_STORAGE_KEY, String(mode));
  } catch {
    // 写入失败（配额/隐私模式）只影响下次刷新，不影响本次会话内的切换。
  }
}

export function readStoredAccent(
  storage: StorageLike | null = defaultStorage(),
): AccentTheme {
  if (!storage) return DEFAULT_ACCENT;
  try {
    return parseAccentTheme(storage.getItem(ACCENT_STORAGE_KEY));
  } catch {
    return DEFAULT_ACCENT;
  }
}

export function writeStoredAccent(
  accent: AccentTheme,
  storage: StorageLike | null = defaultStorage(),
): void {
  if (!storage) return;
  try {
    storage.setItem(ACCENT_STORAGE_KEY, accent);
  } catch {
    // 写入失败只影响下次刷新，不影响本次会话内的切换。
  }
}

/**
 * 纯函数：Auto 跟随系统深色开关，太阳/月亮固定。
 * 未来服务端同步用户设置时复用同一套语义。
 */
export function resolveTheme(mode: ThemeMode, systemPrefersDark: boolean): ResolvedTheme {
  if (mode === 2) return "dark";
  if (mode === 1) return "light";
  return systemPrefersDark ? "dark" : "light";
}

/** 把偏好落到 <html data-theme> 上；SSR / 测试等无 DOM 环境安全跳过。 */
export function applyThemeMode(mode: ThemeMode): void {
  if (typeof document === "undefined") return;
  document.documentElement.dataset.theme = THEME_ATTR_VALUE[mode];
}

/** 把强调色偏好落到 <html data-accent> 上；无 DOM 环境安全跳过。 */
export function applyAccent(accent: AccentTheme): void {
  if (typeof document === "undefined") return;
  document.documentElement.dataset.accent = ACCENT_ATTR_VALUE[accent];
}
