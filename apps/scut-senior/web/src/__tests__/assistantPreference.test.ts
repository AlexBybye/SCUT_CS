import { describe, expect, it } from "vitest";
import {
  ANSWER_MODE_STORAGE_KEY,
  DEFAULT_ANSWER_MODE,
  DEFAULT_TONE,
  TONE_STORAGE_KEY,
  parseAnswerMode,
  parseTone,
  readStoredAnswerMode,
  readStoredTone,
  writeStoredAnswerMode,
  writeStoredTone,
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
    expect(readStoredAnswerMode(memoryStorage())).toBe(DEFAULT_ANSWER_MODE);
    expect(readStoredTone(memoryStorage())).toBe(DEFAULT_TONE);
  });

  it("读取并写入回答方式和表达风格", () => {
    const storage = memoryStorage({
      [ANSWER_MODE_STORAGE_KEY]: "concise",
      [TONE_STORAGE_KEY]: "senior_student",
    });
    expect(readStoredAnswerMode(storage)).toBe("concise");
    expect(readStoredTone(storage)).toBe("senior_student");

    writeStoredAnswerMode("step_by_step", storage);
    writeStoredTone("teaching_assistant", storage);
    expect(readStoredAnswerMode(storage)).toBe("step_by_step");
    expect(readStoredTone(storage)).toBe("teaching_assistant");
  });
});
