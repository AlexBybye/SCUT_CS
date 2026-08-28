import { describe, expect, it } from "vitest";
import { buildRoutedWorkflowPayload, routeWorkflow } from "../workflowRouter";

describe("routeWorkflow", () => {
  it.each([
    ["为什么矩阵可逆等价于行列式不为零？", "knowledge_qa"],
    ["这道题怎么做？请给我解题过程", "problem_tutor"],
    ["这是一道错题，帮我看看哪里错了", "mistake_review"],
    ["按考试范围制定两周复习计划", "exam_review"],
    ["请精读以下材料并总结：\n# 特征值\n特征值用于描述线性变换。", "temporary_material_reading"],
  ] as const)("把 %s 路由到 %s", (input, expected) => {
    const route = routeWorkflow(input);
    expect(route.workflowType).toBe(expected);
    expect(route.confidence).toBeGreaterThanOrEqual(0.8);
  });

  it("普通陈述稳定回退知识答疑，且暴露较低置信度供界面提示", () => {
    expect(routeWorkflow("矩阵的秩")).toMatchObject({
      workflowType: "knowledge_qa",
      confidence: 0.66,
    });
  });

  it("按路由结果生成类型化字段", () => {
    expect(buildRoutedWorkflowPayload("mistake_review", "判断矩阵是否可逆", {
      syllabus: "",
      examDate: "",
      availableHours: undefined,
      goals: [],
      weakTopics: [],
      userAnswer: "",
      helpLevel: "step_by_step",
      problemSource: "",
      originalAnswer: "只检查了秩",
      referenceAnswer: "",
      reviewFocus: "推理缺口",
      materialTitle: "",
      readingGoal: "",
    })).toEqual({
      problem: "判断矩阵是否可逆",
      original_answer: "只检查了秩",
      reference_answer: "",
      review_focus: "推理缺口",
    });
  });
});
