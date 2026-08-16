from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Mapping

import pytest
from fastapi.testclient import TestClient

from scut_senior_api.adapters.openrouter import HttpResponse, _quota_reset_at
from scut_senior_api.config import Settings, UnsafeRuntimeConfiguration
from scut_senior_api.byok_catalog import BYOK_CATALOG_VERSION
from scut_senior_api.main import create_app
from scut_senior_api.model_catalog import (
    CATALOG_VERSION,
    ModelHealthResult,
    PLATFORM_DAILY_QUOTA_EXHAUSTED_MESSAGE,
)


MODEL_FIXTURES = [
    {
        "model_id": "google/gemma-4-26b-a4b-it:free",
        "company": "Google",
        "display_name": "Gemma 4 26B A4B",
        "context_length": 262_144,
        "input_modalities": ["text", "image", "video"],
        "is_preview": False,
    },
    {
        "model_id": "dots-studio/dots-3-note-preview:free",
        "company": "Dots Studio",
        "display_name": "Dots3 Note Preview",
        "context_length": 512_000,
        "input_modalities": ["text", "image"],
        "is_preview": True,
    },
    {
        "model_id": "nvidia/nemotron-3-super-120b-a12b:free",
        "company": "NVIDIA",
        "display_name": "Nemotron 3 Super 120B A12B",
        "context_length": 262_144,
        "input_modalities": ["text"],
        "is_preview": False,
    },
]


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


def _settings(tmp_path: Path, *, api_key: str = "server-only-secret") -> Settings:
    return Settings(
        app_env="test",
        model_mode="openrouter_platform",
        database_path=tmp_path / "openrouter.db",
        openrouter_api_key=api_key,
    )


def _workflow_request(conversation_id: str, model_id: str) -> dict[str, object]:
    return {
        "workflow_type": "knowledge_qa",
        "course_scope": "single",
        "course_id": "linear_algebra",
        "allowed_course_ids": [],
        "conversation_id": conversation_id,
        "model_source": "platform_default",
        "provider_id": "openrouter",
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


def _success_response() -> HttpResponse:
    structured = {
        "repository_answer": "矩阵的秩表示线性无关行或列的最大数量。[S1]",
        "related_topics": ["矩阵", "线性无关"],
        "related_questions": ["如何用初等变换求秩？"],
        "bilibili_search_keywords": ["矩阵的秩", "初等行变换"],
    }
    return HttpResponse(
        status_code=200,
        body=json.dumps(
            {"choices": [{"message": {"content": json.dumps(structured)}}]}
        ).encode(),
    )


def _client_with_conversation(
    tmp_path: Path, http_client: RecordingHttpClient, *, api_key: str = "server-only-secret"
) -> tuple[TestClient, str]:
    client = TestClient(
        create_app(
            _settings(tmp_path, api_key=api_key),
            model_http_client=http_client,
            model_health_checker=HealthyCatalogChecker(),
        )
    )
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    )
    assert conversation.status_code == 201
    return client, conversation.json()["conversation_id"]


def test_model_catalog_returns_only_the_three_fixed_openrouter_entries(
    tmp_path: Path,
) -> None:
    client = TestClient(
        create_app(Settings(app_env="test", database_path=tmp_path / "catalog.db"))
    )

    response = client.get("/api/v1/models")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "catalog_version",
        "platform_credential_configured",
        "real_platform_default_available",
        "health_checked_at",
        "byok_available",
        "byok_catalog_version",
        "byok_providers",
        "quota_notice",
        "quota_exhausted_message",
        "models",
    }
    assert body["catalog_version"] == CATALOG_VERSION
    assert body["platform_credential_configured"] is False
    assert body["real_platform_default_available"] is False
    assert body["health_checked_at"] is None
    assert body["byok_available"] is False
    assert body["byok_catalog_version"] == BYOK_CATALOG_VERSION
    assert [item["provider_id"] for item in body["byok_providers"]] == [
        "openrouter",
        "deepseek",
        "siliconflow",
        "zhipu",
    ]
    assert all(item["enabled"] is False for item in body["byok_providers"])
    assert all(
        item["models_confirmed"] is True for item in body["byok_providers"]
    )
    assert [item["models"][0]["model_id"] for item in body["byok_providers"]] == [
        "deepseek/deepseek-v4-flash-0731",
        "deepseek-v4-flash",
        "Pro/zai-org/GLM-4.7",
        "glm-5.2",
    ]
    assert all(len(item["models"]) == 1 for item in body["byok_providers"])
    assert body["quota_notice"]
    assert body["quota_exhausted_message"] == PLATFORM_DAILY_QUOTA_EXHAUSTED_MESSAGE
    assert len(body["models"]) == 3

    for actual, expected in zip(body["models"], MODEL_FIXTURES, strict=True):
        for key, value in expected.items():
            assert actual[key] == value
        assert actual["provider_id"] == "openrouter"
        assert actual["model_source"] == "platform_default"
        assert actual["billing_label"] == "platform_daily_free_quota"
        assert actual["availability_status"] == "platform_credential_not_configured"
        assert actual["supports_structured_outputs"] is True
        assert actual["user_selectable"] is False
        assert actual["last_checked_at"] is None


def test_openrouter_mode_marks_fixed_catalog_available_without_exposing_key(
    tmp_path: Path,
) -> None:
    secret = "server-secret-must-not-leak"
    app = create_app(
        _settings(tmp_path, api_key=secret),
        model_health_checker=HealthyCatalogChecker(),
    )
    client = TestClient(app)

    response = client.get("/api/v1/models")

    assert response.status_code == 200
    assert response.json()["platform_credential_configured"] is True
    assert response.json()["real_platform_default_available"] is True
    assert all(item["user_selectable"] for item in response.json()["models"])
    assert all(
        item["availability_status"] == "available"
        for item in response.json()["models"]
    )
    assert response.json()["health_checked_at"] == "2026-08-16T00:00:00Z"
    assert all(
        item["last_checked_at"] == "2026-08-16T00:00:00Z"
        for item in response.json()["models"]
    )
    assert secret not in response.text
    assert secret not in repr(app.state.settings)


def test_openrouter_mode_requires_server_environment_key(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SCUT_SENIOR_APP_ENV", "test")
    monkeypatch.setenv("SCUT_SENIOR_MODEL_MODE", "openrouter_platform")
    monkeypatch.setenv("SCUT_SENIOR_DATABASE_PATH", str(tmp_path / "env.db"))
    monkeypatch.delenv("SCUT_SENIOR_OPENROUTER_API_KEY", raising=False)

    with pytest.raises(UnsafeRuntimeConfiguration, match="OPENROUTER_API_KEY"):
        create_app()

    monkeypatch.setenv("SCUT_SENIOR_OPENROUTER_API_KEY", "env-only-secret")
    app = create_app()
    assert app.state.settings.model_mode == "openrouter_platform"
    assert "env-only-secret" not in repr(app.state.settings)


def test_test_profile_defaults_platform_health_and_inference_to_fail_closed(
    tmp_path: Path,
) -> None:
    configured = _settings(tmp_path, api_key="test-server-secret")
    app = create_app(configured)
    client = TestClient(app)

    catalog = client.get("/api/v1/models")
    assert catalog.status_code == 200
    assert catalog.json()["real_platform_default_available"] is False
    assert {
        model["availability_status"] for model in catalog.json()["models"]
    } == {"health_check_failed"}

    # Even if a fake health result says selectable, the absent inference
    # transport is a local fail-closed adapter rather than urllib.
    healthy_app = create_app(
        configured,
        model_health_checker=HealthyCatalogChecker(),
    )
    healthy_client = TestClient(healthy_app)
    conversation = healthy_client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    response = healthy_client.post(
        "/api/v1/workflow-runs",
        json=_workflow_request(
            conversation["conversation_id"],
            "google/gemma-4-26b-a4b-it:free",
        ),
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "platform_model_unavailable"


def test_production_still_refuses_openrouter_with_mock_identity_and_storage(
    tmp_path: Path,
) -> None:
    settings = Settings(
        app_env="production",
        model_mode="openrouter_platform",
        database_path=tmp_path / "production.db",
        openrouter_api_key="secret",
    )

    with pytest.raises(
        UnsafeRuntimeConfiguration,
        match="requires github_oauth identity and sqlite storage outside test",
    ):
        create_app(settings)


def test_unregistered_model_is_rejected_before_any_upstream_call(tmp_path: Path) -> None:
    http_client = RecordingHttpClient(_success_response())
    client, conversation_id = _client_with_conversation(tmp_path, http_client)
    request = _workflow_request(conversation_id, "google/not-registered:free")

    response = client.post("/api/v1/workflow-runs", json=request)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "model_not_registered"
    assert http_client.calls == []


def test_openrouter_uses_one_exact_model_and_requires_structured_parameters(
    tmp_path: Path,
) -> None:
    http_client = RecordingHttpClient(_success_response())
    client, conversation_id = _client_with_conversation(tmp_path, http_client)
    selected_model = "dots-studio/dots-3-note-preview:free"

    response = client.post(
        "/api/v1/workflow-runs",
        json=_workflow_request(conversation_id, selected_model),
    )

    assert response.status_code == 201, response.text
    assert len(http_client.calls) == 1
    call = http_client.calls[0]
    payload = call["payload"]
    assert isinstance(payload, dict)
    assert payload["model"] == selected_model
    assert "models" not in payload
    assert "fallbacks" not in payload
    assert payload["provider"] == {"require_parameters": True}
    assert payload["max_tokens"] == 2048
    assert payload["response_format"]["type"] == "json_schema"
    answer_schema = payload["response_format"]["json_schema"]["schema"]
    assert answer_schema["properties"]["bilibili_search_keywords"] == {
        "type": "array",
        "items": {"type": "string", "maxLength": 32},
        "maxItems": 3,
    }
    assert "bilibili_search_keywords" in answer_schema["required"]
    assert call["headers"]["Authorization"] == "Bearer server-only-secret"
    assert "server-only-secret" not in json.dumps(payload, ensure_ascii=False)

    result = response.json()
    assert result["model_source"] == "platform_default"
    assert result["model"] == {
        "provider_id": "openrouter",
        "model_id": selected_model,
        "billing_label": "platform_daily_free_quota",
        "mock_only": False,
    }
    model_event = next(
        event for event in result["trace"] if event["node"] == "openrouter_model"
    )
    assert model_event["result"]["real_model_called"] is True


def test_openrouter_keywords_create_bilibili_search_without_a_second_model_call(
    tmp_path: Path,
) -> None:
    http_client = RecordingHttpClient(_success_response())
    client, conversation_id = _client_with_conversation(tmp_path, http_client)
    request = _workflow_request(
        conversation_id, "google/gemma-4-26b-a4b-it:free"
    )
    request["include_bilibili_resources"] = True

    response = client.post("/api/v1/workflow-runs", json=request)

    assert response.status_code == 201, response.text
    assert len(http_client.calls) == 1
    search = response.json()["external_resources"][-1]
    assert search["resource_type"] == "search"
    assert search["query_keywords"] == ["矩阵的秩", "初等行变换"]
    assert search["review_status"] == "unreviewed_live_search"


def test_invalid_optional_bilibili_keywords_do_not_create_search_or_lose_answer(
    tmp_path: Path,
) -> None:
    structured = {
        "repository_answer": "矩阵秩的说明。[S1]",
        "related_topics": ["矩阵的秩"],
        "related_questions": [],
        "bilibili_search_keywords": "https://evil.example/not-a-list",
    }
    http_client = RecordingHttpClient(
        HttpResponse(
            status_code=200,
            body=json.dumps(
                {"choices": [{"message": {"content": json.dumps(structured)}}]}
            ).encode(),
        )
    )
    client, conversation_id = _client_with_conversation(tmp_path, http_client)
    request = _workflow_request(
        conversation_id, "google/gemma-4-26b-a4b-it:free"
    )
    request["include_bilibili_resources"] = True

    response = client.post("/api/v1/workflow-runs", json=request)

    assert response.status_code == 201, response.text
    assert response.json()["repository_answer"] == "矩阵秩的说明。[S1]"
    assert response.json()["external_resources"] == []
    assert len(http_client.calls) == 1


def test_daily_quota_429_uses_exact_safe_error_without_fallback_or_leak(
    tmp_path: Path,
) -> None:
    secret = "daily-secret"
    upstream_secret = "upstream-private-response"
    http_client = RecordingHttpClient(
        HttpResponse(
            status_code=429,
            headers={
                "X-RateLimit-Limit": "50",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": "86400",
            },
            body=json.dumps(
                {
                    "error": {
                        "code": 429,
                        "message": upstream_secret,
                        "metadata": {"error_type": "rate_limit_exceeded"},
                    }
                }
            ).encode(),
        )
    )
    client, conversation_id = _client_with_conversation(
        tmp_path, http_client, api_key=secret
    )

    response = client.post(
        "/api/v1/workflow-runs",
        json=_workflow_request(
            conversation_id, "google/gemma-4-26b-a4b-it:free"
        ),
    )

    assert response.status_code == 429
    assert response.json() == {
        "error": {
            "code": "platform_daily_quota_exhausted",
            "detail": PLATFORM_DAILY_QUOTA_EXHAUSTED_MESSAGE,
        }
    }
    assert len(http_client.calls) == 1
    assert secret not in response.text
    assert upstream_secret not in response.text
    payload = http_client.calls[0]["payload"]
    assert "models" not in payload
    assert "fallbacks" not in payload

    latched = client.post(
        "/api/v1/workflow-runs",
        json=_workflow_request(
            conversation_id, "google/gemma-4-26b-a4b-it:free"
        ),
    )
    assert latched.status_code == 429
    assert latched.json()["error"]["code"] == "platform_daily_quota_exhausted"
    assert len(http_client.calls) == 1


@pytest.mark.parametrize(
    ("headers", "metadata", "expected_code", "expected_detail"),
    [
        (
            {
                "X-RateLimit-Limit": "20",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": "60",
            },
            {"error_type": "rate_limit_exceeded"},
            "platform_rate_limited",
            "平台免费通道请求过于频繁，请稍后重试。",
        ),
        (
            {"Retry-After": "10"},
            {"provider_code": "PROVIDER_CAPACITY"},
            "upstream_model_rate_limited",
            "当前模型上游服务繁忙，请稍后重试。",
        ),
        (
            {},
            {"error_type": "daily_quota_exhausted"},
            "platform_rate_limited",
            "平台免费通道请求过于频繁，请稍后重试。",
        ),
    ],
)
def test_non_daily_429_never_claims_the_next_day_or_switches_models(
    tmp_path: Path,
    headers: dict[str, str],
    metadata: dict[str, str],
    expected_code: str,
    expected_detail: str,
) -> None:
    http_client = RecordingHttpClient(
        HttpResponse(
            status_code=429,
            headers=headers,
            body=json.dumps(
                {"error": {"code": 429, "message": "private", "metadata": metadata}}
            ).encode(),
        )
    )
    client, conversation_id = _client_with_conversation(tmp_path, http_client)

    response = client.post(
        "/api/v1/workflow-runs",
        json=_workflow_request(
            conversation_id, "nvidia/nemotron-3-super-120b-a12b:free"
        ),
    )

    assert response.status_code == 429
    assert response.json()["error"] == {
        "code": expected_code,
        "detail": expected_detail,
    }
    assert "第二天" not in response.text
    assert len(http_client.calls) == 1
    assert http_client.calls[0]["payload"]["model"] == (
        "nvidia/nemotron-3-super-120b-a12b:free"
    )


def test_workflow_payload_cannot_supply_a_model_key(tmp_path: Path) -> None:
    secret = "client-supplied-secret"
    http_client = RecordingHttpClient(_success_response())
    client, conversation_id = _client_with_conversation(tmp_path, http_client)
    request = _workflow_request(
        conversation_id, "google/gemma-4-26b-a4b-it:free"
    )
    request["api_key"] = secret

    response = client.post("/api/v1/workflow-runs", json=request)

    assert response.status_code == 422
    assert secret not in response.text
    assert http_client.calls == []


def test_non_rate_limit_upstream_body_and_platform_key_are_not_reflected(
    tmp_path: Path,
) -> None:
    api_key = "platform-secret"
    private_body = "upstream internal response body"
    http_client = RecordingHttpClient(
        HttpResponse(status_code=500, body=private_body.encode())
    )
    client, conversation_id = _client_with_conversation(
        tmp_path, http_client, api_key=api_key
    )

    response = client.post(
        "/api/v1/workflow-runs",
        json=_workflow_request(
            conversation_id, "google/gemma-4-26b-a4b-it:free"
        ),
    )

    assert response.status_code == 503
    assert response.json()["error"] == {
        "code": "platform_model_unavailable",
        "detail": "平台模型服务暂时不可用，请稍后重试。",
    }
    assert api_key not in response.text
    assert private_body not in response.text
    assert len(http_client.calls) == 1
    history = client.get(f"/api/v1/conversations/{conversation_id}").json()
    assert len(history["runs"]) == 1
    failed_result = history["runs"][0]["result"]
    assert failed_result["run_status"] == "failed"
    assert failed_result["answer_status"] == "error"
    assert failed_result["repository_answer"] is None
    serialized = json.dumps(history, ensure_ascii=False)
    assert api_key not in serialized
    assert private_body not in serialized


def test_platform_enforces_twenty_requests_per_minute_before_upstream(
    tmp_path: Path,
) -> None:
    http_client = RecordingHttpClient(_success_response())
    client, conversation_id = _client_with_conversation(tmp_path, http_client)
    payload = _workflow_request(
        conversation_id, "google/gemma-4-26b-a4b-it:free"
    )

    for _ in range(20):
        assert client.post("/api/v1/workflow-runs", json=payload).status_code == 201

    blocked = client.post("/api/v1/workflow-runs", json=payload)
    assert blocked.status_code == 429
    assert blocked.json()["error"] == {
        "code": "platform_rate_limited",
        "detail": "平台免费通道请求过于频繁，请稍后重试。",
    }
    assert len(http_client.calls) == 20


def test_daily_reset_header_cannot_lock_the_process_for_an_unbounded_period() -> None:
    now = datetime(2026, 8, 16, 12, 0, tzinfo=UTC)

    reset_at = _quota_reset_at(
        {"X-RateLimit-Reset": "9999999999999999"},
        now,
    )

    assert reset_at == datetime(2026, 8, 17, 0, 0, tzinfo=UTC)
