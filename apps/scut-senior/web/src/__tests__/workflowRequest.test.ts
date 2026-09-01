import { describe, expect, it } from "vitest";
import { buildWorkflowRequest } from "../workflowRequest";

const common = {
  courseId: "linear_algebra",
  conversationId: "conversation-001",
  userInput: "  请解释矩阵的秩  ",
  answerMode: "detailed" as const,
  tone: "teaching_assistant" as const,
  knowledgeScope: "course_first" as const,
  includeBilibiliResources: true,
  modelSource: "platform_default" as const,
  providerId: "mock",
  modelId: "deterministic-fixture-v1",
};

const selectableModels = [
  {
    modelSource: "platform_default" as const,
    providerId: "openrouter",
    modelId: "google/gemma-4-26b-a4b-it:free",
  },
  {
    modelSource: "platform_default" as const,
    providerId: "openrouter",
    modelId: "dots-studio/dots-3-note-preview:free",
  },
  {
    modelSource: "platform_default" as const,
    providerId: "openrouter",
    modelId: "nvidia/nemotron-3-super-120b-a12b:free",
  },
];

describe("buildWorkflowRequest", () => {
  it("构造固定的迭代 0 外层请求字段", () => {
    const request = buildWorkflowRequest({
      ...common,
      workflowType: "knowledge_qa",
      workflowPayload: { question: "矩阵的秩" },
    });

    expect(request).toMatchObject({
      workflow_type: "knowledge_qa",
      course_scope: "single",
      course_id: "linear_algebra",
      allowed_course_ids: [],
      conversation_id: "conversation-001",
      model_source: "platform_default",
      provider_id: "mock",
      model_id: "deterministic-fixture-v1",
      user_input: "请解释矩阵的秩",
      answer_mode: "detailed",
      tone: "teaching_assistant",
      knowledge_scope: "course_first",
      include_bilibili_resources: true,
      context_refs: [],
      attachments: [],
    });
  });

  it("course_only 时强制关闭 Bilibili 资源", () => {
    const request = buildWorkflowRequest({
      ...common,
      knowledgeScope: "course_only",
      includeBilibiliResources: true,
      workflowType: "knowledge_qa",
      workflowPayload: { question: "矩阵的秩" },
    });

    expect(request.include_bilibili_resources).toBe(false);
  });

  it.each(selectableModels)(
    "把显式选择的 $modelId 写入请求，而不是硬编码单一模型",
    (selection) => {
      const request = buildWorkflowRequest({
        ...common,
        ...selection,
        workflowType: "knowledge_qa",
        workflowPayload: { question: "矩阵的秩" },
      });

      expect(request).toMatchObject({
        model_source: selection.modelSource,
        provider_id: selection.providerId,
        model_id: selection.modelId,
      });
    },
  );

  it("构造 knowledge_qa payload", () => {
    const request = buildWorkflowRequest({
      ...common,
      workflowType: "knowledge_qa",
      workflowPayload: { question: "  矩阵为什么可逆？  " },
    });

    expect(request.workflow_payload).toEqual({ question: "矩阵为什么可逆？" });
  });

  it("构造 exam_review payload 并省略空可选字段", () => {
    const request = buildWorkflowRequest({
      ...common,
      userInput: "  制定两周复习安排  ",
      workflowType: "exam_review",
      workflowPayload: {
        syllabus: "  第一章到第五章  ",
        exam_date: "",
        available_hours: 12,
        goals: [" 通过考试 ", "制定两周复习安排", "", "掌握矩阵"],
        weak_topics: ["特征值", "  二次型  "],
      },
    });

    // 外层 user_input 原样进入请求（后端把它当作复习提问），
    // 不再被塞进 goals；payload 的 goals 保持去重后的原列表。
    expect(request.user_input).toBe("制定两周复习安排");
    expect(request.workflow_payload).toEqual({
      syllabus: "第一章到第五章",
      available_hours: 12,
      goals: ["通过考试", "制定两周复习安排", "掌握矩阵"],
      weak_topics: ["特征值", "二次型"],
    });
  });

  it("构造 problem_tutor payload", () => {
    const request = buildWorkflowRequest({
      ...common,
      workflowType: "problem_tutor",
      workflowPayload: {
        problem: "  求矩阵 A 的秩  ",
        user_answer: "  我做到了第二步  ",
        help_level: "step_by_step",
        problem_source: "  2023 期末 A 卷  ",
      },
    });

    expect(request.workflow_payload).toEqual({
      problem: "求矩阵 A 的秩",
      user_answer: "我做到了第二步",
      help_level: "step_by_step",
      problem_source: "2023 期末 A 卷",
    });
  });

  it("构造 mistake_review payload", () => {
    const request = buildWorkflowRequest({
      ...common,
      workflowType: "mistake_review",
      workflowPayload: {
        problem: "  判断矩阵是否可逆  ",
        original_answer: "  我只检查了行列式  ",
        reference_answer: "  还需说明等价条件  ",
        review_focus: "  找出推理缺口  ",
      },
    });

    expect(request.workflow_payload).toEqual({
      problem: "判断矩阵是否可逆",
      original_answer: "我只检查了行列式",
      reference_answer: "还需说明等价条件",
      review_focus: "找出推理缺口",
    });
  });

  it("跨课程请求只提交去重后的显式课程集合", () => {
    const request = buildWorkflowRequest({
      ...common,
      courseIds: [" linear_algebra ", "probability_theory", "linear_algebra"],
      workflowType: "knowledge_qa",
      workflowPayload: { question: "矩阵与概率" },
    });

    expect(request.course_scope).toBe("cross");
    expect(request.course_id).toBeNull();
    expect(request.allowed_course_ids).toEqual(["linear_algebra", "probability_theory"]);
  });

  it("跨课程只允许 knowledge_qa 和 problem_tutor", () => {
    expect(() => buildWorkflowRequest({
      ...common,
      courseIds: ["linear_algebra", "probability_theory"],
      workflowType: "exam_review",
      workflowPayload: { goals: [], weak_topics: [] },
    })).toThrow("当前仅知识问答和题目辅导支持跨课程检索");
  });

  it("单门集合自动保持单课程请求语义", () => {
    const request = buildWorkflowRequest({
      ...common,
      courseIds: ["linear_algebra", "linear_algebra"],
      workflowType: "knowledge_qa",
      workflowPayload: { question: "秩" },
    });
    expect(request.course_scope).toBe("single");
    expect(request.course_id).toBe("linear_algebra");
    expect(request.allowed_course_ids).toEqual([]);
  });

  it("构造 temporary_material_reading payload", () => {
    const request = buildWorkflowRequest({
      ...common,
      workflowType: "temporary_material_reading",
      workflowPayload: {
        material_title: "  线性代数考试范围  ",
        material_text: "  本次考试覆盖矩阵与向量空间。  ",
        reading_goal: "  提取考试范围  ",
      },
    });

    expect(request.workflow_payload).toEqual({
      material_title: "线性代数考试范围",
      material_text: "本次考试覆盖矩阵与向量空间。",
      reading_goal: "提取考试范围",
    });
  });
});
