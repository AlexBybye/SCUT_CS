import { afterEach, describe, expect, it, vi } from "vitest";
import {
  deleteByokCredential,
  deleteConversation,
  getByokCredentials,
  getConversation,
  getMe,
  getPluginRegistry,
  listConversations,
  loadCoursePlugin,
  regenerateWorkflowRun,
  renameConversation,
  runWorkflow,
  saveByokCredential,
  startWorkflowRunStream,
  submitFeedback,
  unloadCoursePlugin,
} from "../api";
import type { PluginRegistry, WorkflowRunResult } from "../contracts";
import { buildWorkflowRequest } from "../workflowRequest";

afterEach(() => {
  vi.unstubAllGlobals();
});

function completedResult(
  workflowRunId: string,
  conversationId: string,
): WorkflowRunResult {
  return {
    workflow_run_id: workflowRunId,
    conversation_id: conversationId,
    message_id: "message-001",
    answer_id: "answer-001",
    run_status: "completed",
    answer_status: "answered",
    workflow_type: "knowledge_qa",
    course_scope: "single",
    course_ids: ["linear_algebra"],
    repository_answer: "矩阵的秩。",
    general_supplement: null,
    answer_blocks: [{ type: "repository", content: "矩阵的秩。" }],
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
}

describe("runWorkflow", () => {
  it("429 时原样抛出后端 detail，且不自动改模型重试", async () => {
    const request = buildWorkflowRequest({
      workflowType: "knowledge_qa",
      courseId: "linear_algebra",
      conversationId: "conversation-001",
      userInput: "请解释矩阵的秩",
      answerMode: "detailed",
      tone: "teaching_assistant",
      knowledgeScope: "course_first",
      includeBilibiliResources: true,
      modelSource: "platform_default",
      providerId: "openrouter",
      modelId: "dots-studio/dots-3-note-preview:free",
      workflowPayload: { question: "请解释矩阵的秩" },
    });
    const exhaustedMessage =
      "今日平台免费额度已用完，第二天再来重试吧！着急请使用你自己的 API Key。";
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ error: { detail: exhaustedMessage } }), {
        status: 429,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(runWorkflow(request)).rejects.toMatchObject({
      message: exhaustedMessage,
      status: 429,
    });
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(init.credentials).toBe("include");
    expect(JSON.parse(String(init.body))).toMatchObject({
      model_source: "platform_default",
      provider_id: "openrouter",
      model_id: "dots-studio/dots-3-note-preview:free",
    });
  });

  it("流式运行使用固定 NDJSON 路由、会话 Cookie 和普通请求字段", async () => {
    const request = buildWorkflowRequest({
      workflowType: "knowledge_qa",
      courseId: "linear_algebra",
      conversationId: "conversation-001",
      userInput: "请解释矩阵的秩",
      answerMode: "detailed",
      tone: "teaching_assistant",
      knowledgeScope: "course_first",
      includeBilibiliResources: true,
      modelSource: "user_key",
      providerId: "deepseek",
      modelId: "deepseek-chat",
      workflowPayload: { question: "请解释矩阵的秩" },
    });
    const terminal = {
      kind: "error",
      workflow_run_id: null,
      sequence: 0,
      error: { code: "fixture_stop", detail: "测试结束。" },
    };
    const fetchMock = vi.fn().mockResolvedValue(new Response(`${JSON.stringify(terminal)}\n`, {
      status: 200,
      headers: { "Content-Type": "application/x-ndjson" },
    }));
    vi.stubGlobal("fetch", fetchMock);

    const state = await startWorkflowRunStream(request).done;

    expect(state).toMatchObject({ phase: "failed", error: { code: "fixture_stop" } });
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/api/v1/workflow-runs/stream");
    expect(init).toMatchObject({ method: "POST", credentials: "include" });
    expect(new Headers(init.headers).get("Accept")).toBe("application/x-ndjson");
    expect(JSON.parse(String(init.body))).toMatchObject({
      model_source: "user_key",
      provider_id: "deepseek",
      model_id: "deepseek-chat",
    });
    expect(String(init.body)).not.toContain("api_key");
  });

  it("保留 auth_required 错误码且携带会话 Cookie", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          error: { code: "auth_required", detail: "请先使用 GitHub 登录。" },
        }),
        { status: 401, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(getMe()).rejects.toMatchObject({
      status: 401,
      code: "auth_required",
      message: "请先使用 GitHub 登录。",
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/me",
      expect.objectContaining({ credentials: "include" }),
    );
  });
});

describe("conversation history API", () => {
  it("列表、重命名、删除和重新生成均携带会话 Cookie 并使用固定路由", async () => {
    const summary = {
      conversation_id: "conversation/001",
      user_id: "user-001",
      course_id: "linear_algebra",
      title: "矩阵的秩",
      created_at: "2026-08-16T08:00:00Z",
      updated_at: "2026-08-16T08:00:00Z",
      expires_at: "2026-09-15T08:00:00Z",
      mock_only: true,
    };
    const regeneratedRequest = buildWorkflowRequest({
      workflowType: "knowledge_qa",
      courseId: "linear_algebra",
      conversationId: "conversation/001",
      userInput: "请解释矩阵的秩",
      answerMode: "detailed",
      tone: "teaching_assistant",
      knowledgeScope: "course_first",
      includeBilibiliResources: true,
      modelSource: "platform_default",
      providerId: "mock",
      modelId: "deterministic-fixture-v1",
      workflowPayload: { question: "请解释矩阵的秩" },
    });
    const regenerated = {
      workflow_run_id: "run/002",
      attempt_group_id: "run/001",
      regenerated_from_run_id: "run/001",
      request: regeneratedRequest,
      result: completedResult("run/002", "conversation/001"),
      created_at: "2026-08-16T08:01:00Z",
      updated_at: "2026-08-16T08:01:01Z",
      expires_at: "2026-09-15T08:01:00Z",
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(JSON.stringify([summary]), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ ...summary, title: "矩阵秩复习" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(new Response(null, { status: 204 }))
      .mockResolvedValueOnce(
        new Response(JSON.stringify(regenerated), {
          status: 201,
          headers: { "Content-Type": "application/json" },
        }),
      );
    vi.stubGlobal("fetch", fetchMock);

    await expect(listConversations()).resolves.toEqual([summary]);
    await expect(renameConversation("conversation/001", "矩阵秩复习")).resolves.toMatchObject({
      title: "矩阵秩复习",
    });
    await expect(deleteConversation("conversation/001")).resolves.toBeUndefined();
    await expect(regenerateWorkflowRun("run/001")).resolves.toMatchObject(regenerated);

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "/api/v1/conversations",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "/api/v1/conversations/conversation%2F001",
      expect.objectContaining({
        method: "PATCH",
        credentials: "include",
        body: JSON.stringify({ title: "矩阵秩复习" }),
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "/api/v1/conversations/conversation%2F001",
      expect.objectContaining({ method: "DELETE", credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      4,
      "/api/v1/workflow-runs/run%2F001/regenerate",
      expect.objectContaining({ method: "POST", credentials: "include" }),
    );
  });

  it("rejects cross-run history and an external URL that bypasses the stream", async () => {
    const conversationId = "conversation/001";
    const request = buildWorkflowRequest({
      workflowType: "knowledge_qa",
      courseId: "linear_algebra",
      conversationId,
      userInput: "请解释矩阵的秩",
      answerMode: "detailed",
      tone: "teaching_assistant",
      knowledgeScope: "course_first",
      includeBilibiliResources: true,
      modelSource: "platform_default",
      providerId: "mock",
      modelId: "deterministic-fixture-v1",
      workflowPayload: { question: "请解释矩阵的秩" },
    });
    const result = completedResult("run/002", conversationId);
    const detail = {
      conversation_id: conversationId,
      user_id: "user-001",
      course_id: "linear_algebra",
      title: "矩阵的秩",
      created_at: "2026-08-16T08:00:00Z",
      updated_at: "2026-08-16T08:01:01Z",
      expires_at: "2026-09-15T08:00:00Z",
      mock_only: true,
      runs: [{
        workflow_run_id: "run/001",
        attempt_group_id: "run/001",
        regenerated_from_run_id: null,
        request,
        result,
        created_at: "2026-08-16T08:01:00Z",
        updated_at: "2026-08-16T08:01:01Z",
        expires_at: "2026-09-15T08:01:00Z",
      }],
    };
    const unsafeResult = completedResult("run/001", conversationId);
    unsafeResult.external_resources = [{
      resource_id: null,
      course_id: "linear_algebra",
      platform: "bilibili",
      resource_type: "search",
      title: "伪造入口",
      url: "javascript:alert(1)",
      matched_topic: "矩阵的秩",
      review_status: "unreviewed_live_search",
      catalog_version: null,
      query_keywords: ["矩阵的秩"],
      generated_at: "2026-08-17T00:00:00Z",
      evidence_role: "supplementary_only",
    }];
    const unsafeDetail = {
      ...detail,
      runs: [{ ...detail.runs[0], result: unsafeResult }],
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(detail), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }))
      .mockResolvedValueOnce(new Response(JSON.stringify(unsafeDetail), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(getConversation(conversationId)).rejects.toThrow(/another run/i);
    await expect(getConversation(conversationId)).rejects.toThrow(/fixed anonymous search URL/i);
  });

  it("skips in-flight attempts in history instead of failing the whole conversation", async () => {
    const conversationId = "conversation/001";
    const request = buildWorkflowRequest({
      workflowType: "knowledge_qa",
      courseId: "linear_algebra",
      conversationId,
      userInput: "请解释矩阵的秩",
      answerMode: "detailed",
      tone: "teaching_assistant",
      knowledgeScope: "course_first",
      includeBilibiliResources: true,
      modelSource: "platform_default",
      providerId: "mock",
      modelId: "deterministic-fixture-v1",
      workflowPayload: { question: "请解释矩阵的秩" },
    });
    const runningResult = completedResult("run/001", conversationId);
    runningResult.run_status = "running";
    runningResult.answer_status = "partial";
    const detail = {
      conversation_id: conversationId,
      user_id: "user-001",
      course_id: "linear_algebra",
      title: "矩阵的秩",
      created_at: "2026-08-16T08:00:00Z",
      updated_at: "2026-08-16T08:01:01Z",
      expires_at: "2026-09-15T08:00:00Z",
      mock_only: true,
      runs: [
        {
          workflow_run_id: "run/001",
          attempt_group_id: "run/001",
          regenerated_from_run_id: null,
          request,
          result: runningResult,
          created_at: "2026-08-16T08:01:00Z",
          updated_at: "2026-08-16T08:01:01Z",
          expires_at: "2026-09-15T08:01:00Z",
        },
        {
          workflow_run_id: "run/002",
          attempt_group_id: "run/002",
          regenerated_from_run_id: null,
          request,
          result: completedResult("run/002", conversationId),
          created_at: "2026-08-16T08:02:00Z",
          updated_at: "2026-08-16T08:02:01Z",
          expires_at: "2026-09-15T08:02:00Z",
        },
      ],
    };
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(detail), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }));
    vi.stubGlobal("fetch", fetchMock);

    // 运行中（running）的尝试被跳过，会话仍能正常加载已完成的那条。
    const conversation = await getConversation(conversationId);
    expect(conversation.runs).toHaveLength(1);
    expect(conversation.runs[0]?.workflow_run_id).toBe("run/002");
  });
});

describe("plugin registry API", () => {
  it("读取只读插件注册表并保持契约字段", async () => {
    const registry: PluginRegistry = {
      registry_version: "harness-registry-v1",
      retrieval_mode: "fixture",
      agent_presets: [
        {
          preset_id: "preset_knowledge_qa",
          preset_version: "v1",
          display_name: "知识点问答",
          workflow_type: "knowledge_qa",
          focus_strategy: "question_concept",
          allowed_tools: ["course_retrieval", "evidence_location"],
          required_input_modalities: ["text"],
          requires_structured_outputs: true,
        },
      ],
      controlled_tools: [
        {
          tool_id: "course_retrieval",
          display_name: "课程检索",
          description: "服务端编排的课程范围检索。",
          model_callable: false,
        },
      ],
      maintainer_skills: [
        {
          skill_id: "material_conversion",
          display_name: "资料 Markdown 转换",
          version: "v1",
          description: "契约元数据。",
          status: "contract_only",
          human_review_required: true,
          can_mark_passed_or_active: false,
        },
      ],
      courses: [
        {
          course_id: "cpp",
          display_name: "C++（上及下）",
          state: "registered",
          loaded: true,
          usable: false,
          category: "no_data",
          enabled_workflows: [],
        },
      ],
    };
    const fetchMock = vi.fn().mockResolvedValueOnce(
      new Response(JSON.stringify(registry), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(getPluginRegistry()).resolves.toEqual(registry);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/plugin-registry",
      expect.objectContaining({ credentials: "include" }),
    );
  });
});

describe("course plugin mutation API", () => {
  it("装载使用精确编码后的 POST 路由并携带会话 Cookie", async () => {
    const courseId = "linear algebra/2026";
    const response = { course_id: courseId, loaded: true };
    const fetchMock = vi.fn().mockResolvedValueOnce(
      new Response(JSON.stringify(response), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(loadCoursePlugin(courseId)).resolves.toEqual(response);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/plugin-registry/courses/linear%20algebra%2F2026/load",
      expect.objectContaining({ method: "POST", credentials: "include" }),
    );
  });

  it("卸载使用精确编码后的 POST 路由并携带会话 Cookie", async () => {
    const courseId = "linear algebra/2026";
    const response = { course_id: courseId, loaded: false };
    const fetchMock = vi.fn().mockResolvedValueOnce(
      new Response(JSON.stringify(response), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(unloadCoursePlugin(courseId)).resolves.toEqual(response);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/plugin-registry/courses/linear%20algebra%2F2026/unload",
      expect.objectContaining({ method: "POST", credentials: "include" }),
    );
  });

  it("装载与卸载均保留后端错误详情、状态码和错误码", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            error: { code: "method_not_allowed", detail: "Method Not Allowed" },
          }),
          { status: 405, headers: { "Content-Type": "application/json" } },
        ),
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            error: { code: "auth_required", detail: "请先使用 GitHub 登录。" },
          }),
          { status: 401, headers: { "Content-Type": "application/json" } },
        ),
      );
    vi.stubGlobal("fetch", fetchMock);

    await expect(loadCoursePlugin("linear_algebra")).rejects.toMatchObject({
      message: "Method Not Allowed",
      status: 405,
      code: "method_not_allowed",
    });
    await expect(unloadCoursePlugin("linear_algebra")).rejects.toMatchObject({
      message: "请先使用 GitHub 登录。",
      status: 401,
      code: "auth_required",
    });
  });
});

describe("BYOK credential API", () => {
  it("查询、保存和删除只走固定凭据路由并携带会话 Cookie", async () => {
    const configured = {
      provider_id: "openrouter",
      display_name: "OpenRouter DeepSeek",
      base_url: "https://openrouter.ai/api/v1",
      model_id: "deepseek/deepseek-v4-flash-0731",
      protocol: "openai_chat_completions" as const,
      configured: true,
      masked_key: "sk-or-****1234",
      expires_at: "2026-08-20T08:00:00Z",
      writable: true,
      source: "user_key" as const,
      updated_at: "2026-08-17T08:00:00Z",
    };
    const dummyKey = "test-only-openrouter-key";
    const connectionInput = {
      api_key: dummyKey,
      display_name: configured.display_name,
      base_url: configured.base_url,
      model_id: configured.model_id,
      protocol: configured.protocol,
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(JSON.stringify([configured]), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify(configured), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(getByokCredentials()).resolves.toEqual([configured]);
    await expect(
      saveByokCredential("openrouter", connectionInput),
    ).resolves.toEqual(configured);
    await expect(deleteByokCredential("openrouter")).resolves.toBeUndefined();

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "/api/v1/model-credentials",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "/api/v1/model-credentials/openrouter",
      expect.objectContaining({
        method: "PUT",
        credentials: "include",
        body: JSON.stringify(connectionInput),
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "/api/v1/model-credentials/openrouter",
      expect.objectContaining({ method: "DELETE", credentials: "include" }),
    );

    for (const [url] of fetchMock.mock.calls as [string, RequestInit][]) {
      expect(url).not.toContain(dummyKey);
    }
  });
});

describe("feedback API", () => {
  it("提交反馈只走固定 /api/v1/feedback 路由并携带会话 Cookie 与备注", async () => {
    const record = {
      feedback_id: "feedback-001",
      user_id: "user-1",
      run_id: "11111111-1111-1111-1111-111111111111",
      conversation_id: "22222222-2222-2222-2222-222222222222",
      course_id: "linear_algebra",
      workflow_type: "knowledge_qa",
      feedback_type: "knowledge_error",
      note: "第三行有误",
      answer_status: "answered",
      created_at: "2026-08-17T08:00:00Z",
      expires_at: "2026-09-16T08:00:00Z",
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValue(
        new Response(JSON.stringify(record), {
          status: 201,
          headers: { "Content-Type": "application/json" },
        }),
      );
    vi.stubGlobal("fetch", fetchMock);

    await expect(
      submitFeedback(record.run_id, "knowledge_error", "第三行有误"),
    ).resolves.toEqual(record);

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/feedback",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        body: JSON.stringify({
          run_id: record.run_id,
          feedback_type: "knowledge_error",
          note: "第三行有误",
        }),
      }),
    );
  });
});
