import { describe, expect, it } from "vitest";
import {
  ANSWER_MODE_STORAGE_KEY,
  DEFAULT_ANSWER_MODE,
  DEFAULT_PERSONA_ENHANCEMENT,
  DEFAULT_TONE,
  TONE_STORAGE_KEY,
  PERSONA_ENHANCEMENT_STORAGE_KEY,
  parseAnswerMode,
  parseTone,
  parsePersonaEnhancement,
  readStoredAnswerMode,
  readStoredTone,
  readStoredPersonaEnhancement,
  writeStoredAnswerMode,
  writeStoredTone,
  writeStoredPersonaEnhancement,
} from "../assistantPreference";

function memoryStorage(initial: Record<string, string> = {}) {
  const values = new Map(Object.entries(initial));
  return {
    getItem: (key: string) => values.get(key) ?? null,
    setItem: (key: string, value: string) => values.set(key, value),
  };
}

describe("assistantPreference", () => {
  it("非法或缺失的持久化值回退默认偏好", () => {
    expect(parseAnswerMode("unknown")).toBe(DEFAULT_ANSWER_MODE);
    expect(parseTone(null)).toBe(DEFAULT_TONE);
    expect(parsePersonaEnhancement("unknown")).toBe(DEFAULT_PERSONA_ENHANCEMENT);
    expect(readStoredAnswerMode(memoryStorage())).toBe(DEFAULT_ANSWER_MODE);
    expect(readStoredTone(memoryStorage())).toBe(DEFAULT_TONE);
    expect(readStoredPersonaEnhancement(memoryStorage())).toBe(DEFAULT_PERSONA_ENHANCEMENT);
  });

  it("读取并写入回答方式和表达风格", () => {
    const storage = memoryStorage({
      [ANSWER_MODE_STORAGE_KEY]: "concise",
      [TONE_STORAGE_KEY]: "senior_student",
      [PERSONA_ENHANCEMENT_STORAGE_KEY]: "humanized",
    });
    expect(readStoredAnswerMode(storage)).toBe("concise");
    expect(readStoredTone(storage)).toBe("senior_student");
    expect(readStoredPersonaEnhancement(storage)).toBe("humanized");

    writeStoredAnswerMode("step_by_step", storage);
    writeStoredTone("teaching_assistant", storage);
    writeStoredPersonaEnhancement("standard", storage);
    expect(readStoredAnswerMode(storage)).toBe("step_by_step");
    expect(readStoredTone(storage)).toBe("teaching_assistant");
    expect(readStoredPersonaEnhancement(storage)).toBe("standard");
  });
});
