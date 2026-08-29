import { describe, expect, it } from "vitest";

import type { Course } from "../contracts";
import {
  courseAvailabilitySummary,
  courseOptionLabel,
  courseRuntimeDescription,
  courseSelectionError,
  selectSelectableCourseId,
} from "../courseAvailability";

const fixtureCourse: Course = {
  course_id: "linear_algebra",
  display_name: "线性代数",
  aliases: ["线性代数与解析几何"],
  is_open: false,
  mock_available: true,
  retrieval_availability: "fixture",
  retrieval_available: true,
  plugin_loaded: true,
  selectable: true,
  usable: true,
  category: "enabled",
};

const localCorpusCourse: Course = {
  course_id: "information_security_intro",
  display_name: "信息安全导论",
  aliases: ["信安导论"],
  is_open: false,
  mock_available: false,
  retrieval_availability: "local_corpus",
  retrieval_available: true,
  plugin_loaded: true,
  selectable: true,
  usable: true,
  category: "enabled",
};

const unavailableCourse: Course = {
  course_id: "cpp",
  display_name: "C++（上及下）",
  aliases: ["C++"],
  is_open: false,
  mock_available: false,
  retrieval_availability: "unavailable",
  retrieval_available: false,
  plugin_loaded: true,
  selectable: false,
  usable: false,
  category: "no_data",
};

describe("course runtime availability", () => {
  it("保留当前可选课，否则默认首门实际可选课程", () => {
    expect(
      selectSelectableCourseId(
        [unavailableCourse, localCorpusCourse, fixtureCourse],
        unavailableCourse.course_id,
      ),
    ).toBe(localCorpusCourse.course_id);
    expect(
      selectSelectableCourseId(
        [unavailableCourse, localCorpusCourse, fixtureCourse],
        fixtureCourse.course_id,
      ),
    ).toBe(fixtureCourse.course_id);
    expect(selectSelectableCourseId([unavailableCourse], "")).toBe("");
  });

  it("区分 Fixture、已激活本地语料和不可用课程", () => {
    expect(courseAvailabilitySummary(fixtureCourse)).toBe("合成 Fixture · 当前可用");
    expect(courseAvailabilitySummary(localCorpusCourse)).toBe("已激活本地课程语料 · 当前可用");
    expect(courseAvailabilitySummary(unavailableCourse)).toBe("无本地语料数据");
    expect(courseOptionLabel(localCorpusCourse)).toContain("已激活本地课程语料");
    expect(courseSelectionError(unavailableCourse)).toBe("该课程资料当前未激活或不可用。");
  });

  it("按实际检索模式说明课程边界，不把本地语料说成 Fixture", () => {
    expect(courseRuntimeDescription("fixture")).toContain("合成 Fixture");
    expect(courseRuntimeDescription("local_corpus")).toContain("已激活的本地课程语料");
  });
});
