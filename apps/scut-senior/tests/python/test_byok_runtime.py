from __future__ import annotations

import base64
import json
import sqlite3
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event
from urllib.error import URLError

import pytest
from fastapi.testclient import TestClient

from scut_senior_api.adapters.openrouter import HttpResponse
from scut_senior_api.agent_loop import AgentBudget
from scut_senior_api.auth import GitHubUserProfile, SESSION_COOKIE_NAME
from scut_senior_api.config import Settings
from scut_senior_api.contracts import RunStatus, WorkflowRunRequest
from scut_senior_api.main import create_app
from scut_senior_api.ports import GeneratedAnswer, RetrievalBatch, RetrievedSource
from scut_senior_api.workflow_stream import WorkflowStreamSession


MASTER_KEY = base64.b64encode(b"B" * 32).decode("ascii")
ROUTES = (
    (
        "openrouter",
        "deepseek/deepseek-v4-flash-0731",
        "https://openrouter.ai/api/v1",
        "https://openrouter.ai/api/v1/chat/completions",
    ),
    (
        "deepseek",
        "deepseek-v4-flash",
        "https://api.deepseek.com",
        "https://api.deepseek.com/chat/completions",
    ),
    (
        "siliconflow",
        "Pro/zai-org/GLM-4.7",
        "https://api.siliconflow.cn/v1",
        "https://api.siliconflow.cn/v1/chat/completions",
    ),
    (
        "zhipu",
        "glm-5.2",
        "https://open.bigmodel.cn/api/paas/v4",
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    ),
)
ROUTE_CONFIG = {
    provider_id: (model_id, base_url)
    for provider_id, model_id, base_url, _ in ROUTES
}


def credential_payload(
    provider_id: str,
    api_key: str,
    *,
    model_id: str | None = None,
    base_url: str | None = None,
) -> dict[str, str]:
    default_model, default_base_url = ROUTE_CONFIG.get(
        provider_id, ("custom-model", "https://models.example.com/v1")
    )
    return {
        "display_name": provider_id.replace("-", " ").title(),
        "base_url": base_url or default_base_url,
        "model_id": model_id or default_model,
        "protocol": "openai_chat_completions",
        "api_key": api_key,
    }


class RecordingHttpClient:
    def __init__(
        self,
        response: HttpResponse | None = None,
        callback: Callable[[], HttpResponse] | None = None,
    ):
        self.response = response or success_response()
        self.callback = callback
        self.calls: list[dict[str, object]] = []

    def post_json(self, url, *, headers, payload, timeout_seconds):
        self.calls.append(
            {
                "url": url,
                "headers": dict(headers),
                "payload": dict(payload),
                "timeout_seconds": timeout_seconds,
            }
        )
        return self.callback() if self.callback is not None else self.response


def success_response() -> HttpResponse:
    structured = {
        "repository_answer": "矩阵秩是线性无关方向的数量。[S1]",
        "related_topics": ["初等行变换"],
        "related_questions": ["如何计算秩？"],
        "bilibili_search_keywords": ["矩阵的秩"],
    }
    return HttpResponse(
        200,
        json.dumps(
            {"choices": [{"message": {"content": json.dumps(structured)}}]}
        ).encode(),
    )


def settings(
    database_path: Path, *, agent_decision_mode: str = "rule"
) -> Settings:
    return Settings(
        app_env="test",
        identity_mode="github_oauth",
        storage_mode="sqlite",
        database_path=database_path,
        github_client_id="client",
        github_client_secret="secret",
        github_callback_url="https://testserver/api/v1/auth/github/callback",
        post_login_redirect_url="https://testserver/",
        byok_master_key=MASTER_KEY,
        byok_key_version=3,
        agent_decision_mode=agent_decision_mode,
    )


def authenticated_app(
    tmp_path: Path,
    http_client: RecordingHttpClient | None,
    *,
    agent_decision_mode: str = "rule",
) -> tuple[object, TestClient, str, str]:
    app = create_app(
        settings(
            tmp_path / "byok-runtime.db",
            agent_decision_mode=agent_decision_mode,
        ),
        byok_http_client=http_client,
    )
    repository = app.state.repository
    user_id = repository.upsert_github_user(GitHubUserProfile(1001, "student"))
    session = repository.issue_session(user_id)
    client = TestClient(app, base_url="https://testserver")
    client.cookies.set(SESSION_COOKIE_NAME, session.token, path="/")
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    )
    assert conversation.status_code == 201
    return app, client, session.token, conversation.json()["conversation_id"]


def workflow_request(
    conversation_id: str, provider_id: str, model_id: str
) -> dict[str, object]:
    return {
        "workflow_type": "knowledge_qa",
        "course_scope": "single",
        "course_id": "linear_algebra",
        "allowed_course_ids": [],
        "conversation_id": conversation_id,
        "model_source": "user_key",
        "provider_id": provider_id,
        "model_id": model_id,
        "user_input": "请解释矩阵的秩",
        "answer_mode": "detailed",
        "tone": "teaching_assistant",
        "knowledge_scope": "course_first",
        "include_bilibili_resources": False,
        "context_refs": [],
        "attachments": [],
        "workflow_payload": {"question": "请解释矩阵的秩"},
    }


@pytest.mark.parametrize(
    ("provider_id", "model_id", "base_url", "endpoint"), ROUTES
)
def test_custom_byok_connections_use_the_saved_endpoint_and_model(
    tmp_path: Path,
    provider_id: str,
    model_id: str,
    base_url: str,
    endpoint: str,
) -> None:
    http = RecordingHttpClient()
    app, client, _, conversation_id = authenticated_app(tmp_path, http)
    api_key = f"sk-{provider_id}-private"
    assert client.put(
        f"/api/v1/model-credentials/{provider_id}",
        json=credential_payload(
            provider_id, api_key, model_id=model_id, base_url=base_url
        ),
    ).status_code == 200

    response = client.post(
        "/api/v1/workflow-runs",
        json=workflow_request(conversation_id, provider_id, model_id),
    )

    assert response.status_code == 201, response.text
    assert len(http.calls) == 1
    call = http.calls[0]
    assert call["url"] == endpoint
    assert call["headers"]["Authorization"] == f"Bearer {api_key}"
    assert call["payload"]["model"] == model_id
    assert 0 < call["timeout_seconds"] <= 120.0
    direct_deepseek = provider_id == "deepseek"
    assert call["payload"]["max_tokens"] == (
        8192 if direct_deepseek else 12288
    )
    assert call["payload"]["temperature"] == 0.2
    if direct_deepseek:
        assert call["payload"]["reasoning_effort"] == "low"
    else:
        assert "reasoning_effort" not in call["payload"]
    assert "models" not in call["payload"]
    assert "fallbacks" not in call["payload"]
    assert "base_url" not in call["payload"]
    assert "provider" not in call["payload"]
    assert "response_format" not in call["payload"]
    assert api_key not in json.dumps(call["payload"], ensure_ascii=False)

    result = response.json()
    assert result["model_source"] == "user_key"
    assert result["model"] == {
        "provider_id": provider_id,
        "model_id": model_id,
        "billing_label": "user_provider_billing",
        "mock_only": False,
    }
    assert result["availability_status"] == "user_key_enabled"
    assert api_key not in response.text
    with sqlite3.connect(app.state.settings.database_path) as connection:
        persisted = "|".join(
            str(value)
            for row in connection.execute(
                "SELECT request_json, result_json FROM workflow_runs"
            )
            for value in row
        )
    assert api_key not in persisted


def test_byok_model_mode_uses_one_compact_action_call_then_one_answer_call(
    tmp_path: Path,
) -> None:
    responses = [
        HttpResponse(
            200,
            json.dumps(
                {"choices": [{"message": {"content": "generate_answer"}}]}
            ).encode(),
        ),
        success_response(),
    ]
    http = RecordingHttpClient(callback=lambda: responses.pop(0))
    app, client, _, conversation_id = authenticated_app(
        tmp_path,
        http,
        agent_decision_mode="model",
    )
    key = "sk-deepseek-action-private"
    assert client.put(
        "/api/v1/model-credentials/deepseek",
        json=credential_payload("deepseek", key),
    ).status_code == 200

    payload = workflow_request(
        conversation_id, "deepseek", "deepseek-v4-flash"
    )
    payload.update(
        {
            "workflow_type": "exam_review",
            "user_input": "结合历年卷，帮我总结一份复习大纲",
            "workflow_payload": {
                "syllabus": "行列式、矩阵、秩、方程组、特征值和二次型",
                "exam_date": "2026-08-29",
                "available_hours": 12,
                "goals": ["90+"],
                "weak_topics": ["公式记不住"],
            },
        }
    )
    response = client.post("/api/v1/workflow-runs", json=payload)

    assert response.status_code == 201, response.text
    assert len(http.calls) == 2
    action_call, answer_call = http.calls
    assert action_call["url"] == "https://api.deepseek.com/chat/completions"
    assert action_call["payload"]["max_tokens"] == 256
    assert action_call["payload"]["temperature"] == 0
    assert action_call["payload"]["model"] == "deepseek-v4-flash"
    assert action_call["payload"]["reasoning_effort"] == "low"
    action_body = json.dumps(action_call["payload"], ensure_ascii=False)
    assert "课程资料候选" not in action_body
    assert key not in action_body
    assert answer_call["payload"]["max_tokens"] == 8192
    assert answer_call["payload"]["temperature"] == 0.2
    assert answer_call["payload"]["reasoning_effort"] == "low"

    result = response.json()
    metrics = next(
        event["result"]
        for event in result["trace"]
        if event["node"] == "byok_model"
    )
    assert metrics["decision_call_count"] == 1
    assert metrics["model_action_accepted_count"] == 1
    assert metrics["decision_fallback_count"] == 0
    assert metrics["action_rejection_count"] == 0
    assert metrics["answer_call_count"] == 1
    assert key not in response.text


def test_openrouter_hosted_deepseek_does_not_receive_direct_deepseek_profile(
    tmp_path: Path,
) -> None:
    responses = [
        HttpResponse(
            200,
            json.dumps(
                {"choices": [{"message": {"content": "generate_answer"}}]}
            ).encode(),
        ),
        success_response(),
    ]
    http = RecordingHttpClient(callback=lambda: responses.pop(0))
    _, client, _, conversation_id = authenticated_app(
        tmp_path,
        http,
        agent_decision_mode="model",
    )
    key = "sk-openrouter-action-private"
    assert client.put(
        "/api/v1/model-credentials/openrouter",
        json=credential_payload("openrouter", key),
    ).status_code == 200

    response = client.post(
        "/api/v1/workflow-runs",
        json=workflow_request(
            conversation_id,
            "openrouter",
            "deepseek/deepseek-v4-flash-0731",
        ),
    )

    assert response.status_code == 201, response.text
    assert len(http.calls) == 2
    action_call, answer_call = http.calls
    assert action_call["payload"]["max_tokens"] == 512
    assert answer_call["payload"]["max_tokens"] == 12288
    assert "reasoning_effort" not in action_call["payload"]
    assert "reasoning_effort" not in answer_call["payload"]
    assert key not in response.text


@pytest.mark.parametrize(
    ("raw_action", "expected_retrieval_calls", "accepted", "fallbacks"),
    [
        ("retrieve_with_query_rewrite", 2, 1, 0),
        ("先检索更多资料再回答", 1, 0, 1),
    ],
)
def test_byok_action_rewrite_and_parse_fallback_remain_bounded(
    tmp_path: Path,
    raw_action: str,
    expected_retrieval_calls: int,
    accepted: int,
    fallbacks: int,
) -> None:
    class CountingRetrieval:
        def __init__(self) -> None:
            self.calls: list[str] = []

        def is_course_available(self, course_id: str) -> bool:
            return course_id == "linear_algebra"

        def search(self, course_ids: list[str], query: str) -> RetrievalBatch:
            assert course_ids == ["linear_algebra"]
            self.calls.append(query)
            ordinal = len(self.calls)
            source = RetrievedSource(
                chunk_id=f"linear_algebra:byok-action:p{ordinal}",
                course_id="linear_algebra",
                source_id=f"byok-action-{ordinal}",
                source_title=f"历年卷资料 {ordinal}",
                text="此处是只允许进入回答调用、不能进入 Action 请求的证据正文。",
                locator_type="page",
                locator_start=ordinal,
                locator_end=ordinal,
                question_id=None,
                heading_path=(),
            )
            return RetrievalBatch((source,), "byok-action-corpus", "byok-action-pack")

    responses = [
        HttpResponse(
            200,
            json.dumps(
                {"choices": [{"message": {"content": raw_action}}]},
                ensure_ascii=False,
            ).encode(),
        ),
        success_response(),
    ]
    http = RecordingHttpClient(callback=lambda: responses.pop(0))
    app, client, _, conversation_id = authenticated_app(
        tmp_path,
        http,
        agent_decision_mode="model",
    )
    retrieval = CountingRetrieval()
    app.state.service.retrieval = retrieval
    key = "sk-bounded-action-private"
    assert client.put(
        "/api/v1/model-credentials/deepseek",
        json=credential_payload("deepseek", key),
    ).status_code == 200

    response = client.post(
        "/api/v1/workflow-runs",
        json=workflow_request(
            conversation_id, "deepseek", "deepseek-v4-flash"
        ),
    )

    assert response.status_code == 201, response.text
    assert len(http.calls) == 2
    assert len(retrieval.calls) == expected_retrieval_calls
    action_body = json.dumps(http.calls[0]["payload"], ensure_ascii=False)
    assert "不能进入 Action 请求" not in action_body
    metrics = next(
        event["result"]
        for event in response.json()["trace"]
        if event["node"] == "byok_model"
    )
    assert metrics["decision_call_count"] == 1
    assert metrics["model_action_accepted_count"] == accepted
    assert metrics["decision_fallback_count"] == fallbacks
    assert metrics["answer_call_count"] == 1
    assert key not in response.text


def test_byok_accepts_a_plain_text_complex_answer_without_retry(tmp_path: Path) -> None:
    plain_text = (
        "先通过初等行变换把矩阵化为阶梯形，再数每一行的首个非零元。"
        "这些主元的个数就是秩；零行不计入。"
    )
    http = RecordingHttpClient(
        HttpResponse(
            200,
            json.dumps(
                {"choices": [{"message": {"content": plain_text}}]},
                ensure_ascii=False,
            ).encode(),
        )
    )
    _, client, _, conversation_id = authenticated_app(tmp_path, http)
    key = "sk-deepseek-plain-text"
    assert client.put(
        "/api/v1/model-credentials/deepseek",
        json=credential_payload("deepseek", key),
    ).status_code == 200

    response = client.post(
        "/api/v1/workflow-runs",
        json=workflow_request(conversation_id, "deepseek", "deepseek-v4-flash"),
    )

    assert response.status_code == 201, response.text
    assert len(http.calls) == 1
    result = response.json()
    assert result["repository_answer"] is None
    general_supplement = result["general_supplement"]
    assert general_supplement.startswith(plain_text)
    assert general_supplement.count(
        "> **助教提示：** 定义、前提、符号先摆齐，少一步都不给分。"
    ) == 1
    assert result["answer_blocks"] == [
        {"type": "general", "content": general_supplement}
    ]
    assert result["citations"] == []
    assert all(event["node"] != "model_output_retry" for event in result["trace"])
    assert key not in response.text


def test_byok_provider_timeout_is_capped_by_remaining_agent_runtime(
    tmp_path: Path,
) -> None:
    from scut_senior_api.adapters.byok import OpenAICompatibleByokGateway

    http = RecordingHttpClient()
    app, client, token, conversation_id = authenticated_app(tmp_path, http)
    key = "sk-deepseek-runtime-cap"
    assert client.put(
        "/api/v1/model-credentials/deepseek",
        json=credential_payload("deepseek", key),
    ).status_code == 200
    principal = app.state.repository.authenticate_session(token)
    assert principal is not None
    connection = app.state.service.credential_manager.get_connection(
        principal, "deepseek", "deepseek-v4-flash"
    )
    request = WorkflowRunRequest.model_validate(
        workflow_request(conversation_id, "deepseek", "deepseek-v4-flash")
    )

    OpenAICompatibleByokGateway(http_client=http).generate(
        api_key=key,
        connection=connection,
        request=request,
        sources=[],
        timeout_seconds=37.5,
    )

    assert http.calls[-1]["timeout_seconds"] == 37.5


def test_cancel_during_key_load_prevents_the_first_byok_provider_call(
    tmp_path: Path,
) -> None:
    key_load_entered = Event()
    release_key_load = Event()

    class BlockingCredentialManager:
        def __init__(self, delegate):
            self.get_connection = delegate.get_connection

        def load_api_key(self, principal, provider_id):
            del principal, provider_id
            key_load_entered.set()
            if not release_key_load.wait(timeout=2):
                raise TimeoutError("test key load was not released")
            return "sk-private-must-not-be-used"

    class RecordingByokModel:
        def __init__(self) -> None:
            self.calls = 0

        def generate(self, *, api_key, connection, request, sources, history=(), cancel_check=None):
            del api_key, connection, request, sources, history, cancel_check
            self.calls += 1
            return GeneratedAnswer(repository_answer="不得调用供应商。")

    app, client, token, conversation_id = authenticated_app(tmp_path, None)
    assert client.put(
        "/api/v1/model-credentials/openrouter",
        json=credential_payload("openrouter", "sk-blocking"),
    ).status_code == 200
    principal = app.state.repository.authenticate_session(token)
    assert principal is not None
    model = RecordingByokModel()
    app.state.service.credential_manager = BlockingCredentialManager(
        app.state.service.credential_manager
    )
    app.state.service.byok_model = model
    request = WorkflowRunRequest.model_validate(
        workflow_request(
            conversation_id,
            "openrouter",
            "deepseek/deepseek-v4-flash-0731",
        )
    )
    session = WorkflowStreamSession(lambda _: None)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            app.state.service.run_stream,
            principal,
            request,
            session,
        )
        try:
            assert key_load_entered.wait(timeout=1)
            session.cancel()
        finally:
            release_key_load.set()
        result = future.result(timeout=2)

    assert model.calls == 0
    assert result.run_status == RunStatus.INTERRUPTED
    restored = client.get(f"/api/v1/workflow-runs/{result.workflow_run_id}")
    assert restored.status_code == 200
    assert restored.json()["run_status"] == "interrupted"


def test_arbitrary_byok_model_is_rejected_before_decryption_or_http(
    tmp_path: Path,
) -> None:
    http = RecordingHttpClient()
    app, client, _, conversation_id = authenticated_app(tmp_path, http)
    assert client.put(
        "/api/v1/model-credentials/zhipu",
        json=credential_payload("zhipu", "sk-zhipu"),
    ).status_code == 200
    payload = workflow_request(conversation_id, "zhipu", "glm-5.3")
    response = client.post("/api/v1/workflow-runs", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "byok_model_not_registered"
    assert http.calls == []
    with sqlite3.connect(app.state.settings.database_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM workflow_runs"
        ).fetchone()[0] == 0


@pytest.mark.parametrize(
    ("api_key", "private_marker"),
    [
        ("sk-good\r\nX-Evil: 1", "X-Evil"),
        ("sk-good\x00nul-private-marker", "nul-private-marker"),
    ],
)
def test_control_characters_are_rejected_before_storage_or_provider_http(
    tmp_path: Path,
    api_key: str,
    private_marker: str,
) -> None:
    http = RecordingHttpClient()
    app, client, _, conversation_id = authenticated_app(tmp_path, http)

    saved = client.put(
        "/api/v1/model-credentials/openrouter",
        json=credential_payload("openrouter", api_key),
    )

    assert saved.status_code == 422
    assert saved.json()["error"]["code"] == "invalid_model_credential"
    assert private_marker not in saved.text
    with sqlite3.connect(app.state.settings.database_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM model_credentials"
        ).fetchone()[0] == 0

    attempted = client.post(
        "/api/v1/workflow-runs",
        json=workflow_request(
            conversation_id,
            "openrouter",
            "deepseek/deepseek-v4-flash-0731",
        ),
    )
    assert attempted.status_code == 409
    assert attempted.json()["error"]["code"] == "model_credential_not_configured"
    assert http.calls == []


def test_missing_key_and_upstream_failure_persist_sanitized_failed_attempts(
    tmp_path: Path,
) -> None:
    private_body = "upstream-private-body"
    http = RecordingHttpClient(HttpResponse(500, private_body.encode()))
    app, client, _, conversation_id = authenticated_app(tmp_path, http)
    request = workflow_request(
        conversation_id, "openrouter", "deepseek/deepseek-v4-flash-0731"
    )

    missing = client.post("/api/v1/workflow-runs", json=request)
    assert missing.status_code == 409
    assert missing.json()["error"]["code"] == "model_credential_not_configured"

    api_key = "sk-upstream-secret"
    assert client.put(
        "/api/v1/model-credentials/openrouter",
        json=credential_payload("openrouter", api_key),
    ).status_code == 200
    failed = client.post("/api/v1/workflow-runs", json=request)
    assert failed.status_code == 502
    assert failed.json()["error"]["code"] == "byok_provider_unavailable"
    assert len(http.calls) == 1
    assert private_body not in failed.text
    assert api_key not in failed.text

    history = client.get(f"/api/v1/conversations/{conversation_id}").json()
    # A missing connection is rejected before a workflow run is created. Only
    # the actual upstream attempt is persisted as a failed run.
    assert len(history["runs"]) == 1
    for attempt in history["runs"]:
        result = attempt["result"]
        assert result["run_status"] == "failed"
        assert result["answer_status"] == "error"
        assert result["repository_answer"] is None
        assert result["citations"] == []
        assert result["external_resources"] == []
        failed_event = next(
            event for event in result["trace"] if event["status"] == "failed"
        )
        assert failed_event["result"]["failure_code"] == "workflow_execution_failed"
        assert failed_event["result"]["decision_call_count"] == 0
        assert failed_event["result"]["answer_call_count"] == 1
    serialized = json.dumps(history, ensure_ascii=False)
    assert api_key not in serialized
    assert private_body not in serialized
    with sqlite3.connect(app.state.settings.database_path) as connection:
        database_payload = "|".join(
            str(value)
            for row in connection.execute(
                "SELECT request_json, result_json FROM workflow_runs"
            )
            for value in row
        )
    assert api_key not in database_payload
    assert private_body not in database_payload


@pytest.mark.parametrize(
    ("upstream_status", "expected_status", "expected_code"),
    [
        (401, 422, "byok_provider_authentication_failed"),
        (402, 402, "byok_provider_credit_unavailable"),
        (429, 429, "byok_provider_rate_limited"),
        (408, 504, "byok_provider_timeout"),
        (504, 504, "byok_provider_timeout"),
    ],
)
def test_user_key_permission_credit_and_rate_errors_are_safe(
    tmp_path: Path,
    upstream_status: int,
    expected_status: int,
    expected_code: str,
) -> None:
    private_body = "provider-account-private-diagnostic"
    key = "sk-provider-private"
    http = RecordingHttpClient(HttpResponse(upstream_status, private_body.encode()))
    _, client, _, conversation_id = authenticated_app(tmp_path, http)
    assert client.put(
        "/api/v1/model-credentials/zhipu",
        json=credential_payload("zhipu", key),
    ).status_code == 200

    response = client.post(
        "/api/v1/workflow-runs",
        json=workflow_request(conversation_id, "zhipu", "glm-5.2"),
    )

    assert response.status_code == expected_status
    assert response.json()["error"]["code"] == expected_code
    assert len(http.calls) == (2 if expected_code == "byok_provider_timeout" else 1)
    assert key not in response.text
    assert private_body not in response.text


@pytest.mark.parametrize(
    "failure",
    [
        TimeoutError("private provider timeout"),
        URLError(TimeoutError("private wrapped provider timeout")),
    ],
    ids=["direct", "urllib_wrapped"],
)
def test_byok_transport_timeout_retries_the_same_route_and_key_once(
    tmp_path: Path,
    failure: OSError,
) -> None:
    attempts = 0

    def timeout_then_succeed() -> HttpResponse:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise failure
        return success_response()

    http = RecordingHttpClient(callback=timeout_then_succeed)
    _, client, _, conversation_id = authenticated_app(tmp_path, http)
    key = "sk-private-retry"
    assert client.put(
        "/api/v1/model-credentials/deepseek",
        json=credential_payload("deepseek", key),
    ).status_code == 200

    response = client.post(
        "/api/v1/workflow-runs",
        json=workflow_request(conversation_id, "deepseek", "deepseek-v4-flash"),
    )

    assert response.status_code == 201, response.text
    assert len(http.calls) == 2
    assert {call["url"] for call in http.calls} == {
        "https://api.deepseek.com/chat/completions"
    }
    assert {call["payload"]["model"] for call in http.calls} == {
        "deepseek-v4-flash"
    }
    assert {call["headers"]["Authorization"] for call in http.calls} == {
        f"Bearer {key}"
    }
    retry = next(
        event
        for event in response.json()["trace"]
        if event["node"] == "model_output_retry"
    )
    assert retry["result"] == {
        "retry_count": 1,
        "failure_code": "model_output_retryable_failure",
    }
    assert key not in response.text


def test_byok_invalid_response_retries_the_same_route_and_key_once(
    tmp_path: Path,
) -> None:
    attempts = 0

    def invalid_then_succeed() -> HttpResponse:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return HttpResponse(200, b"{invalid-json")
        return success_response()

    http = RecordingHttpClient(callback=invalid_then_succeed)
    _, client, _, conversation_id = authenticated_app(tmp_path, http)
    key = "sk-private-invalid-retry"
    assert client.put(
        "/api/v1/model-credentials/zhipu",
        json=credential_payload("zhipu", key),
    ).status_code == 200

    response = client.post(
        "/api/v1/workflow-runs",
        json=workflow_request(conversation_id, "zhipu", "glm-5.2"),
    )

    assert response.status_code == 201, response.text
    assert len(http.calls) == 2
    assert {call["url"] for call in http.calls} == {
        "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    }
    assert {call["payload"]["model"] for call in http.calls} == {"glm-5.2"}
    assert {call["headers"]["Authorization"] for call in http.calls} == {
        f"Bearer {key}"
    }
    assert key not in response.text


def test_byok_invalid_response_does_not_retry_past_soft_runtime_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    http = RecordingHttpClient(HttpResponse(200, b"{invalid-json"))
    _, client, _, conversation_id = authenticated_app(tmp_path, http)
    key = "sk-private-soft-runtime"
    assert client.put(
        "/api/v1/model-credentials/deepseek",
        json=credential_payload("deepseek", key),
    ).status_code == 200
    monkeypatch.setattr(
        AgentBudget,
        "allows_optional_call",
        lambda self, elapsed_seconds: False,
    )

    response = client.post(
        "/api/v1/workflow-runs",
        json=workflow_request(
            conversation_id, "deepseek", "deepseek-v4-flash"
        ),
    )

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "byok_provider_invalid_response"
    assert len(http.calls) == 1
    assert key not in response.text


@pytest.mark.parametrize("upstream_succeeds", [True, False])
def test_logout_during_provider_call_prevents_late_success_or_failed_history(
    tmp_path: Path, upstream_succeeds: bool
) -> None:
    http = RecordingHttpClient()
    app, client, token, conversation_id = authenticated_app(tmp_path, http)
    assert client.put(
        "/api/v1/model-credentials/deepseek",
        json=credential_payload("deepseek", "sk-race"),
    ).status_code == 200

    def revoke_during_call() -> HttpResponse:
        assert app.state.repository.revoke_session(token) is True
        return success_response() if upstream_succeeds else HttpResponse(500, b"private")

    http.callback = revoke_during_call
    response = client.post(
        "/api/v1/workflow-runs",
        json=workflow_request(conversation_id, "deepseek", "deepseek-v4-flash"),
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "auth_required"
    with sqlite3.connect(app.state.settings.database_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM workflow_runs"
        ).fetchone()[0] == 0
        # Cross-device BYOK: the key is per-account, so revoking this session
        # must NOT clear the user's saved credential.
        assert connection.execute(
            "SELECT COUNT(*) FROM model_credentials"
        ).fetchone()[0] == 1


def test_test_profile_without_injected_byok_transport_fails_closed(
    tmp_path: Path,
) -> None:
    app, client, _, conversation_id = authenticated_app(tmp_path, None)
    key = "sk-no-network"
    assert client.put(
        "/api/v1/model-credentials/openrouter",
        json=credential_payload("openrouter", key),
    ).status_code == 200

    response = client.post(
        "/api/v1/workflow-runs",
        json=workflow_request(
            conversation_id,
            "openrouter",
            "deepseek/deepseek-v4-flash-0731",
        ),
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "byok_provider_unavailable"
    assert key not in response.text


def test_padded_key_is_rejected_consistently_on_save_and_generate(tmp_path: Path) -> None:
    """The shared validator must reject a padded paste on both paths."""
    from scut_senior_api.adapters.byok import ByokGatewayError, OpenAICompatibleByokGateway
    from scut_senior_api.credentials import validate_user_api_key

    for padded in ("  sk-padded", "sk-padded  ", "sk pa dded", "\tsk-tab"):
        with pytest.raises(ValueError):
            validate_user_api_key(padded)

    http = RecordingHttpClient()
    app, client, _, conversation_id = authenticated_app(tmp_path, http)

    saved = client.put(
        "/api/v1/model-credentials/openrouter",
        json=credential_payload("openrouter", "  sk-padded"),
    )
    assert saved.status_code == 422
    assert saved.json()["error"]["code"] == "invalid_model_credential"

    gateway = OpenAICompatibleByokGateway(http_client=http)
    request = WorkflowRunRequest.model_validate(
        workflow_request(conversation_id, "openrouter", "deepseek/deepseek-v4-flash-0731")
    )
    with pytest.raises(ByokGatewayError) as exc_info:
        from scut_senior_api.ports import StoredModelCredential
        from datetime import UTC, datetime
        from uuid import uuid4

        connection = StoredModelCredential(
            user_id=uuid4(),
            provider_id="openrouter",
            display_name="OpenRouter",
            base_url="https://openrouter.ai/api/v1",
            model_id="deepseek/deepseek-v4-flash-0731",
            protocol="openai_chat_completions",
            ciphertext=b"x" * 17,
            nonce=b"x" * 12,
            algorithm="AES-256-GCM",
            key_version=1,
            expires_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        gateway.generate(
            api_key="sk-padded ",
            connection=connection,
            request=request,
            sources=[],
        )
    assert exc_info.value.status_code == 422
    assert exc_info.value.code == "invalid_model_credential"
    assert http.calls == []
