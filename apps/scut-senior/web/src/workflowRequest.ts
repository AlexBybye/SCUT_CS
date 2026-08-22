import type {
  AnswerMode,
  KnowledgeScope,
  ModelSource,
  Tone,
  WorkflowPayloadMap,
  WorkflowRunRequest,
  WorkflowType,
} from "./contracts";

export interface BuildWorkflowRequestInput<T extends WorkflowType> {
  workflowType: T;
  courseId: string;
  conversationId: string;
  userInput: string;
  answerMode: AnswerMode;
  tone: Tone;
  knowledgeScope: KnowledgeScope;
  includeBilibiliResources: boolean;
  modelSource: ModelSource;
  providerId: string;
  modelId: string;
  workflowPayload: WorkflowPayloadMap[T];
}

function optionalText(value: string | undefined): string | undefined {
  const normalized = value?.trim();
  return normalized ? normalized : undefined;
}

function normalizeList(values: string[]): string[] {
  const seen = new Set<string>();
  return values
    .map((value) => value.trim())
    .filter((value) => {
      if (!value || seen.has(value)) return false;
      seen.add(value);
      return true;
    });
}

export function normalizeWorkflowPayload<T extends WorkflowType>(
  workflowType: T,
  payload: WorkflowPayloadMap[T],
): WorkflowPayloadMap[T] {
  switch (workflowType) {
    case "knowledge_qa": {
      const value = payload as WorkflowPayloadMap["knowledge_qa"];
      return { question: value.question.trim() } as WorkflowPayloadMap[T];
    }
    case "exam_review": {
      const value = payload as WorkflowPayloadMap["exam_review"];
      return {
        ...(optionalText(value.syllabus) ? { syllabus: optionalText(value.syllabus) } : {}),
        ...(optionalText(value.exam_date) ? { exam_date: optionalText(value.exam_date) } : {}),
        ...(typeof value.available_hours === "number" && value.available_hours > 0
          ? { available_hours: value.available_hours }
          : {}),
        goals: normalizeList(value.goals),
        weak_topics: normalizeList(value.weak_topics),
      } as WorkflowPayloadMap[T];
    }
    case "problem_tutor": {
      const value = payload as WorkflowPayloadMap["problem_tutor"];
      return {
        problem: value.problem.trim(),
        ...(optionalText(value.user_answer) ? { user_answer: optionalText(value.user_answer) } : {}),
        help_level: value.help_level,
        ...(optionalText(value.problem_source)
          ? { problem_source: optionalText(value.problem_source) }
          : {}),
      } as WorkflowPayloadMap[T];
    }
    case "mistake_review": {
      const value = payload as WorkflowPayloadMap["mistake_review"];
      return {
        problem: value.problem.trim(),
        original_answer: value.original_answer.trim(),
        ...(optionalText(value.reference_answer)
          ? { reference_answer: optionalText(value.reference_answer) }
          : {}),
        ...(optionalText(value.review_focus)
          ? { review_focus: optionalText(value.review_focus) }
          : {}),
      } as WorkflowPayloadMap[T];
    }
    case "temporary_material_reading": {
      const value = payload as WorkflowPayloadMap["temporary_material_reading"];
      return {
        ...(optionalText(value.material_title)
          ? { material_title: optionalText(value.material_title) }
          : {}),
        material_text: value.material_text.trim(),
        ...(optionalText(value.reading_goal)
          ? { reading_goal: optionalText(value.reading_goal) }
          : {}),
      } as WorkflowPayloadMap[T];
    }
    default:
      throw new Error(`不支持的 workflow_type: ${String(workflowType)}`);
  }
}

export function buildWorkflowRequest<T extends WorkflowType>(
  input: BuildWorkflowRequestInput<T>,
): WorkflowRunRequest<T> {
  const courseId = input.courseId.trim();
  const conversationId = input.conversationId.trim();
  const userInput = input.userInput.trim();
  const providerId = input.providerId.trim();
  const modelId = input.modelId.trim();

  if (!courseId || !conversationId || !userInput || !providerId || !modelId) {
    throw new Error("课程、会话、请求内容和模型不能为空");
  }

  const normalizedPayload = normalizeWorkflowPayload(
    input.workflowType,
    input.workflowPayload,
  );

  return {
    workflow_type: input.workflowType,
    course_scope: "single",
    course_id: courseId,
    allowed_course_ids: [],
    conversation_id: conversationId,
    model_source: input.modelSource,
    provider_id: providerId,
    model_id: modelId,
    // 备考复习没有独立问题字段：后端把外层 user_input 当作本次复习提问，
    // 用于检索聚焦与计划排序；其余 workflow 仍以类型化 payload 字段为准。
    user_input: userInput,
    answer_mode: input.answerMode,
    tone: input.tone,
    knowledge_scope: input.knowledgeScope,
    include_bilibili_resources:
      input.knowledgeScope === "course_first" && input.includeBilibiliResources,
    context_refs: [],
    attachments: [],
    workflow_payload: normalizedPayload,
  };
}
