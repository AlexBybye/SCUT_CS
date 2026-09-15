import { shallowRef } from "vue";
import type { WorkflowType } from "./contracts";

export interface ContentHandoff {
  user_id: string;
  course_id: string;
  title: string;
  content: string;
  run_id?: string;
  workflow_type?: WorkflowType;
  citation_metadata?: Record<string, unknown>[];
  corpus_metadata?: Record<string, unknown>;
}

// Only attribution preference is persisted. Contribution bodies stay in memory.
const emailMemory = new Map<string, string>();
const emailKey = (userId: string) => `scut-senior:contributor-email:${encodeURIComponent(userId)}`;
export const contentHandoff = shallowRef<ContentHandoff | null>(null);

export function isValidContributorEmail(value: string): boolean {
  return value.trim().length <= 254 && /^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(value.trim());
}

export function readContributorEmail(userId: string): string {
  if (!userId) return "";
  if (emailMemory.has(userId)) return emailMemory.get(userId)!;
  try {
    const value = sessionStorage.getItem(emailKey(userId)) ?? "";
    return isValidContributorEmail(value) ? value.trim() : "";
  } catch { return ""; }
}

export function saveContributorEmail(userId: string, email: string): void {
  if (!userId || !isValidContributorEmail(email)) throw new Error("请填写有效的 GitHub 关联邮箱。");
  const value = email.trim();
  emailMemory.set(userId, value);
  try { sessionStorage.setItem(emailKey(userId), value); } catch { /* Session-only fallback. */ }
}

export function writeContentHandoff(value: ContentHandoff): void {
  contentHandoff.value = { ...value };
}

export function readContentHandoff(userId: string): ContentHandoff | null {
  return contentHandoff.value?.user_id === userId ? contentHandoff.value : null;
}

export function clearContentHandoff(userId?: string): void {
  if (!userId || contentHandoff.value?.user_id === userId) contentHandoff.value = null;
}
