// 迭代 5：备考复习计划（workflow_output.exam_review）的防御式读取。
//
// 该结构由后端确定性生成（exam-review-plan-v1），但前端按不可信数据处理：
// 任何字段缺失或形状不符都直接隐藏面板，绝不让坏数据破坏回答渲染。
// 私有大纲/薄弱点原文不会出现在该结构中；未覆盖条目是唯一的大纲派生回显。

export interface ExamReviewPlanPoint {
  topic: string;
  layer: number;
  heading_path: string[];
  material_locations: Array<{
    source_id: string;
    source_title: string;
    locator_type: string;
    locator_start?: string | number | null;
  }>;
  questions: Array<{
    question_id: string;
    source_id: string;
    source_title: string;
    year?: number | null;
    locator_type: string;
    locator_start?: string | number | null;
  }>;
  objective_count: number;
  weak_topic_matched: boolean;
  order_reasons: string[];
}

export interface ExamReviewPlan {
  plan_version: string;
  path: "with_syllabus" | "without_syllabus";
  priority_order: string[];
  scope_statement: string;
  evidence_boundary: string;
  ai_sample_policy: string;
  knowledge_points: ExamReviewPlanPoint[];
  past_exam_stats: {
    question_count: number;
    source_count: number;
    year_count: number;
    sample_years: number[];
    year_coverage: Array<{ year: number; count: number }>;
    type_distribution: Array<{ key: string; label: string; count: number }>;
    // 语料没有可按知识点归组的标题时的客观题组（按来源归组）。
    question_groups: ExamReviewQuestionGroup[];
  };
  review_suggestions: string[];
  uncovered_items: string[];
}

export interface ExamReviewQuestionGroup {
  source_id: string;
  source_title: string;
  year?: number | null;
  question_count: number;
  questions: Array<{ question_id: string; year?: number | null }>;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function asString(value: unknown): string {
  return typeof value === "string" ? value : "";
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

function asNumber(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}

function asYearList(value: unknown): number[] {
  return Array.isArray(value)
    ? value.filter((item): item is number => typeof item === "number" && Number.isInteger(item))
    : [];
}

function asPoints(value: unknown): ExamReviewPlanPoint[] {
  if (!Array.isArray(value)) return [];
  const points: ExamReviewPlanPoint[] = [];
  for (const raw of value) {
    if (!isRecord(raw) || typeof raw.topic !== "string" || !raw.topic) continue;
    const locations: ExamReviewPlanPoint["material_locations"] = [];
    if (Array.isArray(raw.material_locations)) {
      for (const loc of raw.material_locations) {
        if (!isRecord(loc) || typeof loc.source_title !== "string") continue;
        locations.push({
          source_id: asString(loc.source_id),
          source_title: loc.source_title,
          locator_type: asString(loc.locator_type),
          locator_start:
            typeof loc.locator_start === "string" || typeof loc.locator_start === "number"
              ? loc.locator_start
              : null,
        });
      }
    }
    const questions: ExamReviewPlanPoint["questions"] = [];
    if (Array.isArray(raw.questions)) {
      for (const question of raw.questions) {
        if (!isRecord(question) || typeof question.question_id !== "string") continue;
        questions.push({
          question_id: question.question_id,
          source_id: asString(question.source_id),
          source_title: asString(question.source_title),
          year:
            typeof question.year === "number" && Number.isInteger(question.year)
              ? question.year
              : null,
          locator_type: asString(question.locator_type),
          locator_start:
            typeof question.locator_start === "string" || typeof question.locator_start === "number"
              ? question.locator_start
              : null,
        });
      }
    }
    points.push({
      topic: raw.topic,
      layer: typeof raw.layer === "number" ? raw.layer : 1,
      heading_path: asStringArray(raw.heading_path),
      material_locations: locations,
      questions,
      objective_count: asNumber(raw.objective_count),
      weak_topic_matched: raw.weak_topic_matched === true,
      order_reasons: asStringArray(raw.order_reasons),
    });
  }
  return points;
}

function asStats(value: unknown): ExamReviewPlan["past_exam_stats"] {
  const raw = isRecord(value) ? value : {};
  const coverage: ExamReviewPlan["past_exam_stats"]["year_coverage"] = [];
  if (Array.isArray(raw.year_coverage)) {
    for (const item of raw.year_coverage) {
      if (
        isRecord(item) &&
        typeof item.year === "number" &&
        typeof item.count === "number"
      ) {
        coverage.push({ year: item.year, count: item.count });
      }
    }
  }
  const distribution: ExamReviewPlan["past_exam_stats"]["type_distribution"] = [];
  if (Array.isArray(raw.type_distribution)) {
    for (const item of raw.type_distribution) {
      if (
        isRecord(item) &&
        typeof item.label === "string" &&
        typeof item.count === "number"
      ) {
        distribution.push({
          key: asString(item.key),
          label: item.label,
          count: item.count,
        });
      }
    }
  }
  const questionGroups: ExamReviewPlan["past_exam_stats"]["question_groups"] = [];
  if (Array.isArray(raw.question_groups)) {
    for (const item of raw.question_groups) {
      // 没有可读来源标题的题组无法回查，直接丢弃。
      if (!isRecord(item) || typeof item.source_title !== "string" || !item.source_title) {
        continue;
      }
      const questions: ExamReviewQuestionGroup["questions"] = [];
      if (Array.isArray(item.questions)) {
        for (const question of item.questions) {
          if (!isRecord(question) || typeof question.question_id !== "string") continue;
          questions.push({
            question_id: question.question_id,
            year:
              typeof question.year === "number" && Number.isInteger(question.year)
                ? question.year
                : null,
          });
        }
      }
      questionGroups.push({
        source_id: asString(item.source_id),
        source_title: item.source_title,
        year:
          typeof item.year === "number" && Number.isInteger(item.year) ? item.year : null,
        question_count: asNumber(item.question_count),
        questions,
      });
    }
  }
  return {
    question_count: asNumber(raw.question_count),
    source_count: asNumber(raw.source_count),
    year_count: asNumber(raw.year_count),
    sample_years: asYearList(raw.sample_years),
    year_coverage: coverage,
    type_distribution: distribution,
    question_groups: questionGroups,
  };
}

/**
 * 读取 workflow_output.exam_review；形状不符返回 null（面板隐藏）。
 */
export function parseExamReviewPlan(value: unknown): ExamReviewPlan | null {
  if (!isRecord(value)) return null;
  const path = value.path;
  if (path !== "with_syllabus" && path !== "without_syllabus") return null;
  return {
    plan_version: asString(value.plan_version) || "exam-review-plan-v1",
    path,
    priority_order: asStringArray(value.priority_order),
    scope_statement: asString(value.scope_statement),
    evidence_boundary: asString(value.evidence_boundary),
    ai_sample_policy: asString(value.ai_sample_policy),
    knowledge_points: asPoints(value.knowledge_points),
    past_exam_stats: asStats(value.past_exam_stats),
    review_suggestions: asStringArray(value.review_suggestions),
    uncovered_items: asStringArray(value.uncovered_items),
  };
}

export function examReviewPathLabel(path: ExamReviewPlan["path"]): string {
  return path === "with_syllabus" ? "有大纲路径（用户大纲优先）" : "无大纲路径（历年题优先）";
}

export function priorityStepLabel(step: string): string {
  const labels: Record<string, string> = {
    user_syllabus: "用户大纲",
    course_material: "课程资料",
    past_exam: "历年题",
    general: "标记的通用知识",
  };
  return labels[step] ?? step;
}

export function locatorLabel(locator_type: string, locator_start: string | number | null | undefined): string {
  if (locator_type === "page" && locator_start != null) return `页码 p${locator_start}`;
  if (locator_type === "slide" && locator_start != null) return `幻灯片 s${locator_start}`;
  if (locator_type === "heading") return "标题定位";
  if (locator_start != null) return `定位 ${locator_start}`;
  return "资料内定位";
}
