from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Mapping

import pytest
from fastapi.testclient import TestClient

from scut_senior_api.adapters.zhipu import ZHIPU_CHAT_COMPLETIONS_URL
from scut_senior_api.adapters.zhipu_health import ZhipuPlatformHealthChecker
from scut_senior_api.config import Settings
from scut_senior_api.main import create_app
from scut_senior_api.model_catalog import ModelHealthResult


class HttpResponse:
    def __init__(self, status_code: int, body: bytes):
        self.status_code = status_code
        self.body = body


class RecordingHttpClient:
    def __init__(self, response: HttpResponse):
        self.response = response
        self.calls: list[dict[str, object]] = []

    def post_json(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        payload: Mapping[str, object],
        timeout_seconds: float,
    ) -> HttpResponse:
        self.calls.append(
            {
                "url": url,
                "headers": dict(headers),
                "payload": dict(payload),
                "timeout_seconds": timeout_seconds,
            }
        )
        return self.response


class HealthyCatalogChecker:
    checked_at = datetime(2026, 8, 16, 0, 0, tzinfo=UTC)

    def check(self, model_ids):
        return {
            model_id: ModelHealthResult("available", self.checked_at)
            for model_id in model_ids
        }


def _success_response() -> HttpResponse:
    structured = {
        "repository_answer": "矩阵的秩表示线性无关行或列的最大数量。[S1]",
        "related_topics": ["矩阵", "线性无关"],
        "related_questions": ["如何用初等变换求秩？"],
        "bilibili_search_keywords": ["矩阵的秩", "初等行变换"],
    }
    return HttpResponse(
        200, json.dumps({"choices": [{"message": {"content": json.dumps(structured, ensure_ascii=False)}}]}).encode()
    )


def _settings(tmp_path: Path, *, api_key: str = "server-only-zhipu-secret") -> Settings:
    return Settings(
        app_env="test",
        model_mode="openrouter_platform",
        database_path=tmp_path / "zhipu.db",
        zhipu_api_key=api_key,
    )


def _workflow_request(
    conversation_id: str, model_id: str = "glm-4.7-flash"
) -> dict[str, object]:
    return {
        "workflow_type": "knowledge_qa",
        "course_scope": "single",
        "course_id": "linear_algebra",
        "allowed_course_ids": [],
        "conversation_id": conversation_id,
        "model_source": "platform_default",
        "provider_id": "zhipu",
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


def _client_with_conversation(
    tmp_path: Path, http_client: RecordingHttpClient, *, api_key: str = "server-only-zhipu-secret"
) -> tuple[TestClient, str]:
    client = TestClient(
        create_app(
            _settings(tmp_path, api_key=api_key),
            zhipu_http_client=http_client,
            zhipu_health_checker=HealthyCatalogChecker(),
        )
    )
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    )
    assert conversation.status_code == 201
    return client, conversation.json()["conversation_id"]


ZHIPU_MODEL_FIXTURES = [
    {
        "model_id": "glm-4.7-flash",
        "display_name": "GLM-4.7-Flash",
        "context_length": 200_000,
        "input_modalities": ["text"],
        "supports_structured_outputs": True,
    },
    {
        "model_id": "glm-4-flash-250414",
        "display_name": "GLM-4-Flash-250414",
        "context_length": 128_000,
        "input_modalities": ["text"],
        "supports_structured_outputs": True,
    },
    {
        "model_id": "glm-4.6v-flash",
        "display_name": "GLM-4.6V-Flash",
        "context_length": 128_000,
        "input_modalities": ["text", "image", "video"],
        "supports_structured_outputs": False,
    },
]


def test_zhipu_only_configuration_marks_all_fixed_zhipu_models_available(
    tmp_path: Path,
) -> None:
    app = create_app(
        _settings(tmp_path),
        zhipu_health_checker=HealthyCatalogChecker(),
    )
    client = TestClient(app)

    response = client.get("/api/v1/models")

    assert response.status_code == 200
    body = response.json()
    assert body["platform_credential_configured"] is True
    assert body["real_platform_default_available"] is True
    zhipu_models = [
        item for item in body["models"] if item["provider_id"] == "zhipu"
    ]
    openrouter_models = [
        item for item in body["models"] if item["provider_id"] == "openrouter"
    ]
    assert len(zhipu_models) == 3
    assert len(openrouter_models) == 3
    for actual, expected in zip(zhipu_models, ZHIPU_MODEL_FIXTURES, strict=True):
        assert actual["company"] == "Zhipu AI"
        assert actual["display_name"] == expected["display_name"]
        assert actual["context_length"] == expected["context_length"]
        assert actual["input_modalities"] == expected["input_modalities"]
        assert (
            actual["supports_structured_outputs"]
            == expected["supports_structured_outputs"]
        )
        assert actual["is_preview"] is False
        assert actual["user_selectable"] is True
        assert actual["availability_status"] == "available"
    assert all(not item["user_selectable"] for item in openrouter_models)
    assert all(
        item["availability_status"] == "platform_credential_not_configured"
        for item in openrouter_models
    )


def test_zhipu_workflow_posts_to_zhipu_endpoint_with_server_key(
    tmp_path: Path,
) -> None:
    http_client = RecordingHttpClient(_success_response())
    client, conversation_id = _client_with_conversation(tmp_path, http_client)

    response = client.post(
        "/api/v1/workflow-runs",
        json=_workflow_request(conversation_id),
    )

    assert response.status_code == 201, response.text
    assert len(http_client.calls) == 1
    call = http_client.calls[0]
    assert call["url"] == ZHIPU_CHAT_COMPLETIONS_URL
    assert call["headers"]["Authorization"] == "Bearer server-only-zhipu-secret"
    assert call["payload"]["model"] == "glm-4.7-flash"
    assert "server-only-zhipu-secret" not in response.text

    result = response.json()
    assert result["model"]["provider_id"] == "zhipu"
    assert result["model"]["model_id"] == "glm-4.7-flash"
    zhipu_event = next(
        event for event in result["trace"] if event["node"] == "zhipu_model"
    )
    assert zhipu_event["result"]["real_model_called"] is True


def test_zhipu_alternate_model_is_routable_and_posts_correct_model_id(
    tmp_path: Path,
) -> None:
    http_client = RecordingHttpClient(_success_response())
    client, conversation_id = _client_with_conversation(tmp_path, http_client)

    response = client.post(
        "/api/v1/workflow-runs",
        json=_workflow_request(conversation_id, model_id="glm-4-flash-250414"),
    )

    assert response.status_code == 201, response.text
    assert len(http_client.calls) == 1
    assert http_client.calls[0]["payload"]["model"] == "glm-4-flash-250414"
    result = response.json()
    assert result["model"]["model_id"] == "glm-4-flash-250414"


def test_zhipu_unregistered_model_is_rejected_before_upstream_call(
    tmp_path: Path,
) -> None:
    http_client = RecordingHttpClient(_success_response())
    client, conversation_id = _client_with_conversation(tmp_path, http_client)
    request = _workflow_request(conversation_id)
    request["model_id"] = "glm-4.7-air"

    response = client.post("/api/v1/workflow-runs", json=request)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "model_not_registered"
    assert len(http_client.calls) == 0


def test_zhipu_429_throttle_surfaces_model_overload_message(tmp_path: Path) -> None:
    http_client = RecordingHttpClient(
        HttpResponse(
            429,
            json.dumps(
                {"error": {"code": "1305", "message": "该模型当前访问量过大"}}
            ).encode(),
        )
    )
    client, conversation_id = _client_with_conversation(tmp_path, http_client)

    response = client.post(
        "/api/v1/workflow-runs",
        json=_workflow_request(conversation_id),
    )

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "platform_rate_limited"
    assert response.json()["error"]["detail"] == "该模型当前访问量过大，请稍后再试。"
    assert "1305" not in response.text
    assert len(http_client.calls) == 1


def test_zhipu_generic_429_keeps_channel_message_and_hides_body(
    tmp_path: Path,
) -> None:
    http_client = RecordingHttpClient(
        HttpResponse(
            429,
            b'{"error":{"code":"9999","message":"upstream-private-secret"}}',
        )
    )
    client, conversation_id = _client_with_conversation(tmp_path, http_client)

    response = client.post(
        "/api/v1/workflow-runs",
        json=_workflow_request(conversation_id),
    )

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "platform_rate_limited"
    assert response.json()["error"]["detail"] == "平台免费通道请求过于频繁，请稍后重试。"
    assert "upstream-private-secret" not in response.text
    assert len(http_client.calls) == 1


def test_zhipu_401_maps_to_authentication_failure_without_leaking_upstream(
    tmp_path: Path,
) -> None:
    upstream_secret = "zhipu-upstream-private-body"
    http_client = RecordingHttpClient(
        HttpResponse(401, upstream_secret.encode())
    )
    client, conversation_id = _client_with_conversation(tmp_path, http_client)

    response = client.post(
        "/api/v1/workflow-runs",
        json=_workflow_request(conversation_id),
    )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "platform_model_authentication_failed"
    assert upstream_secret not in response.text


def test_zhipu_parse_failure_is_retryable_and_fails_closed(tmp_path: Path) -> None:
    class InvalidResponseHttpClient(RecordingHttpClient):
        def post_json(
            self,
            url: str,
            *,
            headers: Mapping[str, str],
            payload: Mapping[str, object],
            timeout_seconds: float,
        ) -> HttpResponse:
            super().post_json(
                url,
                headers=headers,
                payload=payload,
                timeout_seconds=timeout_seconds,
            )
            return HttpResponse(200, b"not-json-at-all")

    http_client = InvalidResponseHttpClient(_success_response())
    client, conversation_id = _client_with_conversation(tmp_path, http_client)

    response = client.post(
        "/api/v1/workflow-runs",
        json=_workflow_request(conversation_id),
    )

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "platform_model_invalid_response"
    assert len(http_client.calls) == 2


def test_zhipu_health_checker_fails_closed_for_empty_key_and_unknown_model() -> None:
    with pytest.raises(ValueError, match="Zhipu API key is required"):
        ZhipuPlatformHealthChecker(api_key="   ")

    checked_at = datetime(2026, 8, 16, tzinfo=UTC)
    checker = ZhipuPlatformHealthChecker(
        api_key="server-health-secret", clock=lambda: checked_at
    )

    results = checker.check(
        ("glm-4.7-flash", "glm-4-flash-250414", "glm-4.6v-flash", "unknown/model")
    )

    assert results["glm-4.7-flash"].availability_status == "available"
    assert results["glm-4.7-flash"].supports_structured_outputs is True
    assert results["glm-4-flash-250414"].availability_status == "available"
    assert results["glm-4-flash-250414"].supports_structured_outputs is True
    assert results["glm-4.6v-flash"].availability_status == "available"
    assert results["glm-4.6v-flash"].supports_structured_outputs is False
    assert results["unknown/model"].availability_status == "model_unavailable"
    assert all(result.checked_at == checked_at for result in results.values())


def test_zhipu_key_alone_satisfies_platform_safety_check(tmp_path: Path) -> None:
    settings = Settings(
        app_env="development",
        identity_mode="github_oauth",
        storage_mode="sqlite",
        model_mode="openrouter_platform",
        database_path=tmp_path / "zhipu-only.db",
        zhipu_api_key="server-only-zhipu-secret",
        github_client_id="public-client-id",
        github_client_secret="oauth-secret",
        github_callback_url="https://app.example/api/v1/auth/github/callback",
        post_login_redirect_url="https://app.example/",
    )

    settings.assert_safe()
