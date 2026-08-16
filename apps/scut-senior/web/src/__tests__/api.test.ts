import { afterEach, describe, expect, it, vi } from "vitest";
import {
  deleteByokCredential,
  deleteConversation,
  getByokCredentials,
  getMe,
  listConversations,
  regenerateWorkflowRun,
  renameConversation,
  runWorkflow,
  saveByokCredential,
} from "../api";
import { buildWorkflowRequest } from "../workflowRequest";

afterEach(() => {
  vi.unstubAllGlobals();
});

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
    const regenerated = {
      workflow_run_id: "run/002",
      attempt_group_id: "run/001",
      regenerated_from_run_id: "run/001",
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
});

describe("BYOK credential API", () => {
  it("查询、保存和删除只走固定凭据路由并携带会话 Cookie", async () => {
    const configured = {
      provider_id: "openrouter",
      model_id: "deepseek/deepseek-v4-flash-0731",
      configured: true,
      masked_key: "sk-or-****1234",
      expires_at: "2026-08-20T08:00:00Z",
    };
    const dummyKey = "test-only-openrouter-key";
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
    await expect(saveByokCredential("openrouter", dummyKey)).resolves.toEqual(configured);
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
        body: JSON.stringify({ api_key: dummyKey }),
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
