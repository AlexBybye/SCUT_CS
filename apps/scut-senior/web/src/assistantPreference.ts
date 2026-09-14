import { ANSWER_MODES, PERSONA_ENHANCEMENTS, TONES, type AnswerMode, type PersonaEnhancement, type Tone } from "./contracts";

export const DEFAULT_ANSWER_MODE: AnswerMode = "detailed";
export const DEFAULT_TONE: Tone = "study_partner";
export const ANSWER_MODE_STORAGE_KEY = "scut_senior_assistant_answer_mode";
export const TONE_STORAGE_KEY = "scut_senior_assistant_tone";
export const DEFAULT_PERSONA_ENHANCEMENT: PersonaEnhancement = "standard";
export const PERSONA_ENHANCEMENT_STORAGE_KEY = "scut_senior_persona_enhancement";

type StorageLike = Pick<Storage, "getItem" | "setItem">;

function defaultStorage(): StorageLike | null {
  try {
    return typeof localStorage === "undefined" ? null : localStorage;
  } catch {
    return null;
  }
}

export function parseAnswerMode(value: unknown): AnswerMode {
  return typeof value === "string" && ANSWER_MODES.includes(value as AnswerMode)
    ? (value as AnswerMode)
    : DEFAULT_ANSWER_MODE;
}

export function parseTone(value: unknown): Tone {
  return typeof value === "string" && TONES.includes(value as Tone)
    ? (value as Tone)
    : DEFAULT_TONE;
}

export function parsePersonaEnhancement(value: unknown): PersonaEnhancement {
  return typeof value === "string" && PERSONA_ENHANCEMENTS.includes(value as PersonaEnhancement)
    ? (value as PersonaEnhancement)
    : DEFAULT_PERSONA_ENHANCEMENT;
}

export function readStoredAnswerMode(
  storage: StorageLike | null = defaultStorage(),
): AnswerMode {
  if (!storage) return DEFAULT_ANSWER_MODE;
  try {
    return parseAnswerMode(storage.getItem(ANSWER_MODE_STORAGE_KEY));
  } catch {
    return DEFAULT_ANSWER_MODE;
  }
}

export function readStoredTone(storage: StorageLike | null = defaultStorage()): Tone {
  if (!storage) return DEFAULT_TONE;
  try {
    return parseTone(storage.getItem(TONE_STORAGE_KEY));
  } catch {
    return DEFAULT_TONE;
  }
}

export function readStoredPersonaEnhancement(
  storage: StorageLike | null = defaultStorage(),
): PersonaEnhancement {
  if (!storage) return DEFAULT_PERSONA_ENHANCEMENT;
  try {
    return parsePersonaEnhancement(storage.getItem(PERSONA_ENHANCEMENT_STORAGE_KEY));
  } catch {
    return DEFAULT_PERSONA_ENHANCEMENT;
  }
}

export function writeStoredAnswerMode(
  mode: AnswerMode,
  storage: StorageLike | null = defaultStorage(),
): void {
  try {
    storage?.setItem(ANSWER_MODE_STORAGE_KEY, mode);
  } catch {
    // 浏览器拒绝持久化时保留当前会话内设置。
  }
}

export function writeStoredTone(
  tone: Tone,
  storage: StorageLike | null = defaultStorage(),
): void {
  try {
    storage?.setItem(TONE_STORAGE_KEY, tone);
  } catch {
    // 浏览器拒绝持久化时保留当前会话内设置。
  }
}

export function writeStoredPersonaEnhancement(
  value: PersonaEnhancement,
  storage: StorageLike | null = defaultStorage(),
): void {
  try {
    storage?.setItem(PERSONA_ENHANCEMENT_STORAGE_KEY, value);
  } catch {
    // 浏览器拒绝持久化时保留当前会话内设置。
  }
}
