import { renderToString } from "@vue/server-renderer";
import { createSSRApp, h } from "vue";
import { describe, expect, it } from "vitest";
import WorkflowResult from "../components/WorkflowResult.vue";
import type { ConversationDetail, WorkflowRunResult } from "../contracts";
import { selectConversationAttempt } from "../workflowResultValidation";

function workflowResult(coverageGaps: string[]): WorkflowRunResult {
  return {
    workflow_run_id: "run-coverage-gaps",
    conversation_id: "conversation-001",
    message_id: "message-001",
    answer_id: "answer-001",
    run_status: "completed",
    answer_status: "insufficient_evidence",
    workflow_type: "knowledge_qa",
    course_scope: "single",
    course_ids: ["linear_algebra"],
    repository_answer: null,
    general_supplement: null,
    answer_blocks: [],
    workflow_output: {},
    evidence_status: "insufficient",
    citations: [],
    related_topics: [],
    related_questions: [],
    external_resources: [],
    trace: [],
    coverage_gaps: coverageGaps,
    corpus_version: "fixture-corpus-v1",
    course_pack_version: null,
    workflow_version: "workflow-contract-v1",
    model_source: "platform_default",
    model: {
      provider_id: "mock",
      model_id: "deterministic-fixture-v1",
      billing_label: "not_applicable_mock",
      mock_only: true,
    },
    availability_status: "mock_only",
  };
}

async function renderResult(result: WorkflowRunResult): Promise<string> {
  return renderToString(createSSRApp({
    render: () => h(WorkflowResult, {
      result,
      isRunning: false,
      streamState: null,
    }),
  }));
}

describe("WorkflowResult coverage gaps", () => {
  it("renders every backend coverage gap under a dedicated heading", async () => {
    const html = await renderResult(workflowResult([
      "本次课程资料候选不足。",
      "无引用的课程资料正文未进入结果。",
    ]));

    expect(html).toContain("资料覆盖说明");
    expect(html).toContain("<li>本次课程资料候选不足。</li>");
    expect(html).toContain("<li>无引用的课程资料正文未进入结果。</li>");
  });

  it("omits the coverage section when the backend reports no gap", async () => {
    const html = await renderResult(workflowResult([]));

    expect(html).not.toContain("资料覆盖说明");
  });

  it("shows evidence status independently when there is no repository answer block", async () => {
    const result = workflowResult([]);
    result.answer_blocks = [{ type: "general", content: "这里只能提供通用知识补充。" }];
    result.general_supplement = "这里只能提供通用知识补充。";

    const html = await renderResult(result);

    expect(html).toContain("证据状态：insufficient");
    expect(html).toContain("通用知识补充");
    expect(html).not.toContain("课程资料回答");
  });

  it("renders the iteration-5 exam review plan panel only for valid plans", async () => {
    const withPlan = workflowResult([]);
    withPlan.workflow_type = "exam_review";
    withPlan.workflow_output = {
      runtime_version: "workflow-runtime-v1",
      payload_type: "exam_review",
      exam_review: {
        plan_version: "exam-review-plan-v1",
        path: "without_syllabus",
        priority_order: ["past_exam", "course_material"],
        scope_statement: "未提供大纲：不是官方考试范围，也不构成考试重点预测。",
        evidence_boundary: "统计只来自已审核语料。",
        ai_sample_policy: "样题均为 AI 生成、非历年真题。",
        knowledge_points: [
          {
            topic: "填空题",
            layer: 2,
            heading_path: ["一、填空题"],
            material_locations: [
              { source_id: "s1", source_title: "2023 期末 A 卷", locator_type: "page", locator_start: 1 },
            ],
            questions: [
              { question_id: "Q1", source_id: "s1", source_title: "2023 期末 A 卷", year: 2023, locator_type: "page", locator_start: 1 },
            ],
            objective_count: 1,
            weak_topic_matched: false,
            order_reasons: [],
          },
        ],
        past_exam_stats: {
          question_count: 2,
          source_count: 1,
          year_count: 1,
          sample_years: [2023],
          year_coverage: [{ year: 2023, count: 2 }],
          type_distribution: [{ key: "filling_blank", label: "填空题", count: 2 }],
        },
        review_suggestions: ["先从历年题题组开始。"],
        uncovered_items: [],
      },
    };
    const html = await renderResult(withPlan);
    expect(html).toContain("备考复习计划（系统生成）");
    expect(html).toContain("历年题优先");
    expect(html).toContain("不构成考试重点预测");
    expect(html).toContain("2023：2 题");

    const withoutPlan = workflowResult([]);
    withoutPlan.workflow_type = "knowledge_qa";
    const plainHtml = await renderResult(withoutPlan);
    expect(plainHtml).not.toContain("备考复习计划（系统生成）");

    const brokenPlan = workflowResult([]);
    brokenPlan.workflow_type = "exam_review";
    brokenPlan.workflow_output = { exam_review: { path: "nonsense" } };
    const brokenHtml = await renderResult(brokenPlan);
    expect(brokenHtml).not.toContain("备考复习计划（系统生成）");
  });
});

describe("history attempt selection", () => {
  it("does not silently replace a missing preferred run with an older attempt", () => {
    const conversation = {
      runs: [{ workflow_run_id: "run-old" }],
    } as unknown as ConversationDetail;

    expect(() => selectConversationAttempt(conversation, "run-just-finished")).toThrow(
      /未包含刚完成的运行 run-just-finished/,
    );
    expect(selectConversationAttempt(conversation)?.workflow_run_id).toBe("run-old");
  });
});
