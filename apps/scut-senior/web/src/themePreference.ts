/**
 * 助手设置 · 外观主题偏好
 *
 * 三档滑块的取值与存储约定（后续作为用户设置字段，与 API Key 一同存服务器）：
 *   0 = Auto（跟随系统明暗，默认）
 *   1 = 恒亮色（太阳）
 *   2 = 恒暗色（月亮）
 *
 * 当前仅持久化到浏览器 localStorage；解析对脏数据宽容（非法值一律回退默认），
 * 保证换设备、清缓存或手改数据时页面不会进入未定义状态。
 */

export type ThemeMode = 0 | 1 | 2;
export type ResolvedTheme = "light" | "dark";

export const DEFAULT_THEME_MODE: ThemeMode = 0;

/** localStorage 键名：一旦上线就不再改动，避免丢用户已保存的偏好。 */
export const THEME_MODE_STORAGE_KEY = "scut_senior_assistant_theme_mode";

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

export function isThemeMode(value: unknown): value is ThemeMode {
  return value === 0 || value === 1 || value === 2;
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
