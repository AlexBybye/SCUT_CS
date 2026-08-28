import type { HelpLevel, WorkflowPayloadMap, WorkflowType } from "./contracts";

export interface WorkflowRoute {
  workflowType: WorkflowType;
  confidence: number;
  reason: string;
}

export interface WorkflowFieldDraft {
  syllabus: string;
  examDate: string;
  availableHours?: number;
  goals: string[];
  weakTopics: string[];
  userAnswer: string;
  helpLevel: HelpLevel;
  problemSource: string;
  originalAnswer: string;
  referenceAnswer: string;
  reviewFocus: string;
  materialTitle: string;
  readingGoal: string;
}

const MISTAKE_PATTERN = /错题|错在|哪里错|为什么错|复盘|纠错|我的(?:答案|作答)/;
const EXAM_PATTERN = /备考|复习计划|复习安排|历年|考纲|考试范围|考前|考试大纲|薄弱(?:点|知识点)|冲刺/;
const MATERIAL_PATTERN = /精读|阅读(?:一下)?(?:这|以下|这份|下面)|总结(?:一下)?(?:这|以下|这份|下面)|分析(?:一下)?(?:这|以下|这份|下面)(?:段|份)?材料|以下是.{0,8}材料/;
const PROBLEM_PATTERN = /这道题|这题|题目|题干|怎么做|如何求解|求解|证明题|计算题|解题(?:过程|步骤)?/;
const QUESTION_PATTERN = /[?？]|为什么|是什么|什么是|如何理解|解释|区别|原理|含义/;
const MARKDOWN_BLOCK_PATTERN = /(^|\n)#{1,4}\s+\S|(^|\n)(?:[-*]|\d+[.)])\s+\S|```/m;

export function routeWorkflow(
  input: string,
  emptyFallback: WorkflowType = "knowledge_qa",
): WorkflowRoute {
  const text = input.trim();
  if (!text) {
    return { workflowType: emptyFallback, confidence: 0, reason: "等待输入后自动识别" };
  }
  if (MISTAKE_PATTERN.test(text)) {
    return { workflowType: "mistake_review", confidence: 0.96, reason: "识别到错题或纠错意图" };
  }
  if (EXAM_PATTERN.test(text)) {
    return { workflowType: "exam_review", confidence: 0.94, reason: "识别到备考或复习意图" };
  }
  if (MATERIAL_PATTERN.test(text) || (text.length >= 120 && MARKDOWN_BLOCK_PATTERN.test(text))) {
    return {
      workflowType: "temporary_material_reading",
      confidence: MATERIAL_PATTERN.test(text) ? 0.93 : 0.84,
      reason: "识别到临时材料阅读意图",
    };
  }
  if (PROBLEM_PATTERN.test(text)) {
    return { workflowType: "problem_tutor", confidence: 0.91, reason: "识别到题目求解意图" };
  }
  return {
    workflowType: "knowledge_qa",
    confidence: QUESTION_PATTERN.test(text) ? 0.82 : 0.66,
    reason: "按课程知识问题处理",
  };
}

export function buildRoutedWorkflowPayload<T extends WorkflowType>(
  workflowType: T,
  input: string,
  fields: WorkflowFieldDraft,
): WorkflowPayloadMap[T] {
  switch (workflowType) {
    case "knowledge_qa":
      return { question: input } as WorkflowPayloadMap[T];
    case "exam_review":
      return {
        syllabus: fields.syllabus,
        exam_date: fields.examDate,
        available_hours: fields.availableHours,
        goals: fields.goals,
        weak_topics: fields.weakTopics,
      } as WorkflowPayloadMap[T];
    case "problem_tutor":
      return {
        problem: input,
        user_answer: fields.userAnswer,
        help_level: fields.helpLevel,
        problem_source: fields.problemSource,
      } as WorkflowPayloadMap[T];
    case "mistake_review":
      return {
        problem: input,
        original_answer: fields.originalAnswer,
        reference_answer: fields.referenceAnswer,
        review_focus: fields.reviewFocus,
      } as WorkflowPayloadMap[T];
    case "temporary_material_reading":
      return {
        material_title: fields.materialTitle,
        material_text: input,
        reading_goal: fields.readingGoal,
      } as WorkflowPayloadMap[T];
    default:
      throw new Error(`不支持的 workflow_type: ${String(workflowType)}`);
  }
}
