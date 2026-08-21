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
