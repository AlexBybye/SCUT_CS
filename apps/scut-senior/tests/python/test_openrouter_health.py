from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Mapping

from scut_senior_api.adapters.openrouter import HttpResponse
from scut_senior_api.adapters.openrouter_health import (
    OPENROUTER_KEY_STATUS_URL,
    OPENROUTER_MODELS_URL,
    OpenRouterCatalogHealthChecker,
)
from scut_senior_api.model_catalog import ModelCatalog, ModelHealthResult


MODEL_IDS = (
    "google/gemma-4-26b-a4b-it:free",
    "dots-studio/dots-3-note-preview:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
)


class RecordingReadClient:
    def __init__(
        self,
        response: HttpResponse,
        credential_response: HttpResponse | None = None,
    ):
        self.response = response
        self.credential_response = credential_response or HttpResponse(
            200, b'{"data":{"label":"test-key"}}'
        )
        self.calls: list[dict[str, object]] = []

    def get_json(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        timeout_seconds: float,
    ) -> HttpResponse:
        self.calls.append(
            {
                "url": url,
                "headers": dict(headers),
                "timeout_seconds": timeout_seconds,
            }
        )
        return (
            self.credential_response
            if url == OPENROUTER_KEY_STATUS_URL
            else self.response
        )


def model_row(
    model_id: str,
    *,
    prompt: str = "0",
    completion: str = "0.000",
    request: str = "0",
    supported_parameters: list[str] | None = None,
) -> dict[str, object]:
    return {
        "id": model_id,
        "pricing": {
            "prompt": prompt,
            "completion": completion,
            "request": request,
        },
        "supported_parameters": (
            supported_parameters
            if supported_parameters is not None
            else ["structured_outputs", "response_format"]
        ),
    }


def test_health_checker_requires_model_presence_zero_price_and_structured_output() -> None:
    checked_at = datetime(2026, 8, 16, 2, 30, tzinfo=UTC)
    client = RecordingReadClient(
        HttpResponse(
            200,
            json.dumps(
                {
                    "data": [
                        model_row(MODEL_IDS[0]),
                        model_row(MODEL_IDS[1], request="0.000001"),
                        model_row(
                            MODEL_IDS[2], supported_parameters=["response_format"]
                        ),
                    ]
                }
            ).encode(),
        )
    )
    checker = OpenRouterCatalogHealthChecker(
        api_key="server-health-secret",
        http_client=client,
        clock=lambda: checked_at,
    )

    results = checker.check((*MODEL_IDS, "missing/model:free"))

    assert results[MODEL_IDS[0]].availability_status == "available"
    assert results[MODEL_IDS[1]].availability_status == "pricing_or_terms_changed"
    assert (
        results[MODEL_IDS[2]].availability_status
        == "structured_outputs_unavailable"
    )
    assert results["missing/model:free"].availability_status == "model_unavailable"
    assert all(result.checked_at == checked_at for result in results.values())
    assert client.calls == [
        {
            "url": OPENROUTER_KEY_STATUS_URL,
            "headers": {
                "Accept": "application/json",
                "Authorization": "Bearer server-health-secret",
            },
            "timeout_seconds": 10.0,
        },
        {
            "url": OPENROUTER_MODELS_URL,
            "headers": {"Accept": "application/json"},
            "timeout_seconds": 10.0,
        }
    ]


def test_health_checker_fails_closed_without_exposing_upstream_body() -> None:
    checker = OpenRouterCatalogHealthChecker(
        api_key="server-health-secret",
        http_client=RecordingReadClient(
            HttpResponse(200, b'{"data":[]}'),
            credential_response=HttpResponse(
                401, b"upstream-private-diagnostic"
            ),
        ),
        clock=lambda: datetime(2026, 8, 16, tzinfo=UTC),
    )

    results = checker.check(MODEL_IDS)

    assert {
        result.availability_status for result in results.values()
    } == {"health_check_failed"}


class CountingChecker:
    def __init__(self, clock):
        self.clock = clock
        self.calls = 0

    def check(self, model_ids):
        self.calls += 1
        return {
            model_id: ModelHealthResult("available", self.clock())
            for model_id in model_ids
        }


def test_catalog_is_unselectable_until_health_check_and_caches_fresh_result() -> None:
    current = [datetime(2026, 8, 16, 3, 0, tzinfo=UTC)]
    ticks = [100.0]
    checker = CountingChecker(lambda: current[0])
    catalog = ModelCatalog(
        platform_credential_configured=True,
        health_checker=checker,
        clock=lambda: current[0],
        monotonic_clock=lambda: ticks[0],
        health_ttl=timedelta(minutes=5),
    )
    assert all(not entry.user_selectable for entry in catalog.entries)
    assert all(
        entry.availability_status == "health_check_required"
        for entry in catalog.entries
    )

    first = catalog.public_payload()
    second = catalog.public_payload()

    assert checker.calls == 1
    assert first["real_platform_default_available"] is True
    assert second["health_checked_at"] == "2026-08-16T03:00:00+00:00"
    assert all(entry.user_selectable for entry in catalog.entries)

    current[0] += timedelta(minutes=6)
    ticks[0] += 360
    catalog.public_payload()
    assert checker.calls == 2


def test_catalog_does_not_claim_structured_output_support_when_health_rejects_it() -> None:
    checked_at = datetime(2026, 8, 16, 3, 0, tzinfo=UTC)

    class NoStructuredOutputChecker:
        def check(self, model_ids):
            return {
                model_id: ModelHealthResult(
                    "structured_outputs_unavailable", checked_at
                )
                for model_id in model_ids
            }

    catalog = ModelCatalog(
        platform_credential_configured=True,
        health_checker=NoStructuredOutputChecker(),
        clock=lambda: checked_at,
    )
    payload = catalog.public_payload()

    assert payload["real_platform_default_available"] is False
    assert all(model["user_selectable"] is False for model in payload["models"])
    assert all(
        model["supports_structured_outputs"] is False
        for model in payload["models"]
    )
