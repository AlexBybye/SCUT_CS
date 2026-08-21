import { describe, expect, it } from "vitest";
import {
  examReviewPathLabel,
  locatorLabel,
  parseExamReviewPlan,
  priorityStepLabel,
} from "../examReviewPlan";

const validPlan = {
  plan_version: "exam-review-plan-v1",
  path: "without_syllabus",
  priority_order: ["past_exam", "course_material", "general"],
  scope_statement: "未提供大纲：不构成考试重点预测。",
  evidence_boundary: "统计只来自已审核语料。",
  ai_sample_policy: "样题均为 AI 生成、非历年真题。",
  knowledge_points: [
    {
      topic: "填空题",
      layer: 2,
      heading_path: ["2023 期末 A 卷", "一、填空题"],
      material_locations: [
        {
          source_id: "s1",
          source_title: "2023 期末 A 卷",
          locator_type: "page",
          locator_start: 1,
        },
      ],
      questions: [
        {
          question_id: "Q1",
          source_id: "s1",
          source_title: "2023 期末 A 卷",
          year: 2023,
          locator_type: "page",
          locator_start: 1,
        },
      ],
      objective_count: 1,
      weak_topic_matched: false,
      order_reasons: [],
    },
  ],
  past_exam_stats: {
    question_count: 1,
    source_count: 1,
    year_count: 1,
    sample_years: [2023],
    year_coverage: [{ year: 2023, count: 1 }],
    type_distribution: [{ key: "filling_blank", label: "填空题", count: 1 }],
  },
  review_suggestions: ["先从历年题题组开始。"],
  uncovered_items: [],
};

describe("parseExamReviewPlan", () => {
  it("accepts a well-formed backend plan", () => {
    const plan = parseExamReviewPlan(validPlan);
    expect(plan).not.toBeNull();
    expect(plan?.path).toBe("without_syllabus");
    expect(plan?.knowledge_points).toHaveLength(1);
    expect(plan?.past_exam_stats.sample_years).toEqual([2023]);
  });

  it("returns null for missing, non-object or wrong-path payloads", () => {
    expect(parseExamReviewPlan(null)).toBeNull();
    expect(parseExamReviewPlan(undefined)).toBeNull();
    expect(parseExamReviewPlan("nope")).toBeNull();
    expect(parseExamReviewPlan({})).toBeNull();
    expect(parseExamReviewPlan({ ...validPlan, path: "surprise" })).toBeNull();
  });

  it("drops malformed knowledge points instead of crashing", () => {
    const plan = parseExamReviewPlan({
      ...validPlan,
      knowledge_points: [null, { topic: "" }, { nope: true }, validPlan.knowledge_points[0]],
    });
    expect(plan?.knowledge_points).toHaveLength(1);
    expect(plan?.knowledge_points[0]?.topic).toBe("填空题");
  });

  it("coerces broken stats fields to safe defaults", () => {
    const plan = parseExamReviewPlan({
      ...validPlan,
      past_exam_stats: {
        question_count: "many",
        sample_years: ["2023", 2023, null],
        year_coverage: "nope",
        type_distribution: [{ label: 3, count: "x" }],
      },
    });
    expect(plan?.past_exam_stats.question_count).toBe(0);
    expect(plan?.past_exam_stats.sample_years).toEqual([2023]);
    expect(plan?.past_exam_stats.year_coverage).toEqual([]);
    expect(plan?.past_exam_stats.type_distribution).toEqual([]);
  });
});

describe("labels", () => {
  it("maps paths, priority steps and locators to student-readable text", () => {
    expect(examReviewPathLabel("with_syllabus")).toContain("用户大纲优先");
    expect(examReviewPathLabel("without_syllabus")).toContain("历年题优先");
    expect(priorityStepLabel("user_syllabus")).toBe("用户大纲");
    expect(priorityStepLabel("past_exam")).toBe("历年题");
    expect(priorityStepLabel("unknown_step")).toBe("unknown_step");
    expect(locatorLabel("page", 3)).toBe("页码 p3");
    expect(locatorLabel("heading", null)).toBe("标题定位");
    expect(locatorLabel("none", null)).toBe("资料内定位");
  });
});
