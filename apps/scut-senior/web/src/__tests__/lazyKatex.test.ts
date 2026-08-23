// @vitest-environment node

import { renderToString } from "@vue/server-renderer";
import { createSSRApp, defineAsyncComponent, h } from "vue";
import { describe, expect, it } from "vitest";

import type { WorkflowRunResult } from "../contracts";

// 迭代 7.5：KaTeX 按需加载的回归闸。这里不做模块 mock——前三个用例经 Vite 的
// ?raw glob 读取真实源码，断言「入口图不再静态引用 KaTeX、回答视图经动态
// import 引入、KaTeX CSS 与其唯一 JS 消费方同块」；最后一个用例走真实动态
// import，证明异步块解析后渲染结果与拆包前完全一致。
const topLevelSources = import.meta.glob<string>("../*.{ts,vue}", {
  query: "?raw",
  import: "default",
  eager: true,
});
const componentSources = import.meta.glob<string>("../components/*.vue", {
  query: "?raw",
  import: "default",
  eager: true,
});

function readSource(relativePath: string): string {
  const source = topLevelSources[`../${relativePath}`]
    ?? componentSources[`../components/${relativePath}`];
  if (source === undefined) {
    throw new Error(`未找到源文件：${relativePath}`);
  }
  return source;
}

function workflowResultWithMath(): WorkflowRunResult {
  const result: WorkflowRunResult = {
    workflow_run_id: "run-lazy-katex",
    conversation_id: "conversation-lazy-katex",
    message_id: "message-lazy-katex",
    answer_id: "answer-lazy-katex",
    run_status: "completed",
    answer_status: "answered",
    workflow_type: "knowledge_qa",
    course_scope: "single",
    course_ids: ["linear_algebra"],
    repository_answer: null,
    general_supplement: null,
    answer_blocks: [
      {
        type: "repository",
        content: "结论：勾股定理 $a^2+b^2=c^2$。\n\n$$\\int_0^1 x^2\\,dx = \\frac{1}{3}$$",
      },
    ],
    workflow_output: {},
    evidence_status: "sufficient",
    citations: [],
    related_topics: [],
    related_questions: [],
    external_resources: [],
    trace: [],
    coverage_gaps: [],
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
  return result;
}

describe("KaTeX route-level lazy loading", () => {
  it("keeps KaTeX out of the always-loaded entry graph", () => {
    // 入口与应用壳不得引入任何 KaTeX 模块（静态、动态或 require 均算）；
    // 注释里提到 KaTeX 不违规，守卫针对的是真实的模块引用。
    const entrySources = [
      readSource("main.ts"),
      readSource("App.vue"),
      readSource("TranscriptPanel.vue"),
    ];
    for (const source of entrySources) {
      expect(source).not.toMatch(/import\s[^;\n]*["']katex/i);
      expect(source).not.toMatch(/import\s*\(\s*["']katex/i);
      expect(source).not.toMatch(/require\(\s*["']katex/i);
    }
  });

  it("resolves the math-rendering view through a dynamic import", () => {
    const panel = readSource("TranscriptPanel.vue");

    // 静态默认导入会把 WorkflowResult（连同其 KaTeX 依赖树）拉回主包。
    expect(panel).not.toMatch(/import\s+WorkflowResult\s+from/);
    expect(panel).toMatch(
      /defineAsyncComponent\(\s*\(\)\s*=>\s*import\("\.\/WorkflowResult\.vue"\)\s*\)/,
    );
  });

  it("co-locates the KaTeX stylesheet with its only JS consumer", () => {
    const markdown = readSource("markdown.ts");

    expect(markdown).toMatch(/import\s+katex\s+from\s+"katex"/);
    expect(markdown).toMatch(/import\s+"katex\/dist\/katex\.min\.css"/);
  });

  it("renders identical math once the lazy chunk resolves", async () => {
    const LazyWorkflowResult = defineAsyncComponent(
      () => import("../components/WorkflowResult.vue"),
    );

    const html = await renderToString(createSSRApp({
      render: () => h(LazyWorkflowResult, {
        result: workflowResultWithMath(),
        isRunning: false,
        streamState: null,
      }),
    }));

    // 组件整体解析成功 + 数学渲染输出与拆包前完全一致。
    expect(html).toContain("回答、来源与 Trace");
    expect(html).toContain("katex-display");
    expect(html).toMatch(/class="katex"/);
    expect(html).toContain("结论：勾股定理");
  });
});
