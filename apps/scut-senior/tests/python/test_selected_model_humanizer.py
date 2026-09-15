from __future__ import annotations

import json
import pytest

from scut_senior_api.adapters.humanizer import HumanizerResponseError, RewriteTask
from scut_senior_api.adapters.openrouter import HttpResponse
from scut_senior_api.contracts import AnswerBlock
from test_zhipu_platform import _client_with_conversation as zhipu_client, _workflow_request as zhipu_request
from test_openrouter_models import _client_with_conversation as router_client, _workflow_request as router_request
from test_byok_runtime import authenticated_app, credential_payload, workflow_request


class RewriteHttp:
    def __init__(self, failure=None):
        self.calls = []
        self.failure = failure

    def post_json(self, url, *, headers, payload, timeout_seconds, cancel_check=None):
        self.calls.append((url, headers, payload, timeout_seconds))
        if len(self.calls) == 1:
            content = "这句话的表达有一点绕，我们接下来把关键思路整理清楚，方便后续逐步检查和复习，见 [S1]。"
        else:
            if self.failure == "timeout":
                raise TimeoutError("fixture timeout")
            if self.failure == "provider":
                return HttpResponse(503, b"{}")
            if self.failure == "once_invalid" and len(self.calls) == 2:
                content = "not json"
            else:
                blocks = json.loads(payload["messages"][1]["content"])
                blocks[0]["content"] = blocks[0]["content"].replace("这句话的表达有一点绕", "这句话说得有点绕")
                if self.failure == "guard":
                    blocks[0]["content"] += " [S99]"
                content = json.dumps({"blocks": blocks}, ensure_ascii=False)
        return HttpResponse(200, json.dumps({"choices": [{"finish_reason": "stop", "message": {"content": content}}]}, ensure_ascii=False).encode())


@pytest.mark.parametrize("route", ["zhipu", "openrouter", "byok"])
@pytest.mark.parametrize("tone", ["study_partner", "senior_student", "teaching_assistant"])
def test_reuses_selected_model_and_credentials_with_persona(tmp_path, route, tone):
    http = RewriteHttp()
    if route == "zhipu":
        client, conversation = zhipu_client(tmp_path, http)
        payload = zhipu_request(conversation)
    elif route == "openrouter":
        client, conversation = router_client(tmp_path, http)
        payload = router_request(conversation, "google/gemma-4-26b-a4b-it:free")
    else:
        _, client, _, conversation = authenticated_app(tmp_path, http)
        response = client.put("/api/v1/model-credentials/deepseek", json=credential_payload("deepseek", "sk-private-fixture"))
        assert response.status_code == 200
        payload = workflow_request(conversation, "deepseek", "deepseek-v4-flash")
    assert client.get("/api/v1/health").json()["capabilities"]["humanizer_configured"]
    payload.update(tone=tone, persona_enhancement="humanized")
    response = client.post("/api/v1/workflow-runs/stream", json=payload)
    events = [json.loads(line) for line in response.text.splitlines()]
    assert response.status_code == 200
    result = events[-1]["result"]
    assert result["persona_enhancement_outcome"] == "applied"
    assert len(http.calls) == 2
    first, second = http.calls
    assert first[0] == second[0]
    assert first[1]["Authorization"] == second[1]["Authorization"]
    assert first[2]["model"] == second[2]["model"] == payload["model_id"]
    assert 0 < second[3] <= 45
    assert second[2]["max_tokens"] <= first[2]["max_tokens"]
    prompt = second[2]["messages"][0]["content"]
    assert "humanizer-zh 忠实润色内核" in prompt
    assert {"study_partner": "当前人格：学妹", "senior_student": "当前人格：学长", "teaching_assistant": "当前人格：助教"}[tone] in prompt
    assert "[S1]" not in second[2]["messages"][1]["content"]
    restored = client.get(f"/api/v1/conversations/{conversation}").json()["runs"][-1]
    assert restored["result"]["persona_enhancement_outcome"] == "applied"
    assert restored["request"]["persona_enhancement"] == "humanized"


@pytest.mark.parametrize("failure", ["timeout", "provider", "guard"])
def test_rewrite_failure_preserves_successful_answer(tmp_path, failure):
    http = RewriteHttp(failure)
    client, conversation = zhipu_client(tmp_path, http)
    payload = {**zhipu_request(conversation), "persona_enhancement": "humanized"}
    response = client.post("/api/v1/workflow-runs/stream", json=payload)
    events = [json.loads(line) for line in response.text.splitlines()]
    assert sum(event["kind"] in {"result", "error"} for event in events) == 1
    result = events[-1]["result"]
    assert result["run_status"] == "completed"
    assert result["persona_enhancement_outcome"] == "fallback_" + failure
    assert "这句话的表达有一点绕" in result["answer_blocks"][0]["content"]


def test_standard_keeps_single_provider_call(tmp_path):
    http = RewriteHttp()
    client, conversation = zhipu_client(tmp_path, http)
    response = client.post("/api/v1/workflow-runs", json=zhipu_request(conversation))
    assert response.status_code == 201
    assert response.json()["persona_enhancement_outcome"] == "not_requested"
    assert len(http.calls) == 1


def test_invalid_rewrite_response_retries_same_model_once(tmp_path):
    http = RewriteHttp("once_invalid")
    client, conversation = zhipu_client(tmp_path, http)
    payload = {**zhipu_request(conversation), "persona_enhancement": "humanized"}
    result = client.post("/api/v1/workflow-runs", json=payload).json()
    assert result["persona_enhancement_outcome"] == "applied"
    assert len(http.calls) == 3
    assert http.calls[1][2]["model"] == http.calls[2][2]["model"] == payload["model_id"]


@pytest.mark.parametrize(
    "content",
    [
        '```json\n{"blocks":[{"type":"repository","content":"润色后"}]}\n```',
        '结果如下：\n{"blocks":[{"type":"repository","content":"润色后"}]}',
        '[{"type":"repository","content":"润色后"}]',
    ],
)
def test_rewrite_parser_accepts_presentation_only_json_wrappers(content):
    task = RewriteTask([AnswerBlock(type="repository", content="原文")], "instructions")
    body = json.dumps(
        {"choices": [{"finish_reason": "stop", "message": {"content": content}}]},
        ensure_ascii=False,
    ).encode()
    assert task.parse(body)[0].content == "润色后"


def test_rewrite_parser_reports_truncated_completion():
    task = RewriteTask([AnswerBlock(type="repository", content="原文")], "instructions")
    body = json.dumps(
        {"choices": [{"finish_reason": "length", "message": {"content": "{}"}}]}
    ).encode()
    with pytest.raises(HumanizerResponseError) as error:
        task.parse(body)
    assert error.value.code == "humanizer_incomplete_response"
