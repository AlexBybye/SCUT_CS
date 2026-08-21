from __future__ import annotations

import json
from collections.abc import Callable, Collection, Mapping
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Protocol
from urllib.error import HTTPError
from urllib.request import Request

from ..model_catalog import ModelAvailabilityStatus, ModelHealthResult
from .http_security import build_no_redirect_opener
from .openrouter import HttpResponse


OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
OPENROUTER_KEY_STATUS_URL = "https://openrouter.ai/api/v1/auth/key"
MAX_HEALTH_RESPONSE_BYTES = 5_000_000


class JsonHttpReadClient(Protocol):
    def get_json(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        timeout_seconds: float,
    ) -> HttpResponse: ...


class UrllibJsonHttpReadClient:
    def __init__(self) -> None:
        self._opener = build_no_redirect_opener()

    def get_json(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        timeout_seconds: float,
    ) -> HttpResponse:
        request = Request(url, headers=dict(headers), method="GET")
        try:
            with self._opener.open(request, timeout=timeout_seconds) as response:
                return HttpResponse(
                    status_code=response.status,
                    body=response.read(MAX_HEALTH_RESPONSE_BYTES),
                    headers=dict(response.headers.items()),
                )
        except HTTPError as exc:
            return HttpResponse(
                status_code=exc.code,
                body=exc.read(MAX_HEALTH_RESPONSE_BYTES),
                headers=dict(exc.headers.items()) if exc.headers else {},
            )


Clock = Callable[[], datetime]


def utc_now() -> datetime:
    return datetime.now(UTC)


class OpenRouterCatalogHealthChecker:
    """Fail-closed validation of the public OpenRouter model catalog.

    Credential validity is checked only against OpenRouter's fixed key-status URL;
    the project Key is never sent to the public model-list request. A valid secret
    alone is not treated as evidence that a model remains free or supports the
    structured response required by this application.
    """

    def __init__(
        self,
        *,
        api_key: str,
        http_client: JsonHttpReadClient | None = None,
        clock: Clock = utc_now,
        timeout_seconds: float = 10.0,
    ) -> None:
        if not api_key.strip():
            raise ValueError("OpenRouter API key is required for credential health")
        self._api_key = api_key
        self._http_client = http_client or UrllibJsonHttpReadClient()
        self._clock = clock
        self._timeout_seconds = timeout_seconds

    def check(
        self, model_ids: Collection[str]
    ) -> Mapping[str, ModelHealthResult]:
        checked_at = self._clock()
        if checked_at.tzinfo is None or checked_at.utcoffset() is None:
            raise ValueError("health-check clock must be timezone-aware")
        checked_at = checked_at.astimezone(UTC)
        try:
            credential_response = self._http_client.get_json(
                OPENROUTER_KEY_STATUS_URL,
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self._api_key}",
                },
                timeout_seconds=self._timeout_seconds,
            )
            if not _credential_is_valid(credential_response):
                return _same_result(model_ids, "health_check_failed", checked_at)
            response = self._http_client.get_json(
                OPENROUTER_MODELS_URL,
                headers={"Accept": "application/json"},
                timeout_seconds=self._timeout_seconds,
            )
        except (OSError, TimeoutError):
            return _same_result(model_ids, "health_check_failed", checked_at)
        if response.status_code < 200 or response.status_code >= 300:
            return _same_result(model_ids, "health_check_failed", checked_at)

        try:
            payload = json.loads(response.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return _same_result(model_ids, "health_check_failed", checked_at)
        rows = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(rows, list):
            return _same_result(model_ids, "health_check_failed", checked_at)
        by_id = {
            row.get("id"): row
            for row in rows
            if isinstance(row, dict) and isinstance(row.get("id"), str)
        }

        results: dict[str, ModelHealthResult] = {}
        for model_id in model_ids:
            row = by_id.get(model_id)
            if not isinstance(row, dict):
                status = "model_unavailable"
            elif not model_id.endswith(":free") or not _has_zero_price(row):
                status = "pricing_or_terms_changed"
            elif not _supports_structured_outputs(row):
                status = "structured_outputs_unavailable"
            else:
                status = "available"
            results[model_id] = ModelHealthResult(status, checked_at)
        return results


def _same_result(
    model_ids: Collection[str],
    status: ModelAvailabilityStatus,
    checked_at: datetime,
) -> dict[str, ModelHealthResult]:
    return {
        model_id: ModelHealthResult(status, checked_at)
        for model_id in model_ids
    }


def _has_zero_price(row: Mapping[str, object]) -> bool:
    pricing = row.get("pricing")
    if not isinstance(pricing, dict) or not pricing:
        return False
    if "prompt" not in pricing or "completion" not in pricing:
        return False
    return all(_is_zero(value) for value in pricing.values())


def _is_zero(value: object) -> bool:
    if isinstance(value, bool) or value is None:
        return False
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return False
    return parsed.is_finite() and parsed == 0


def _supports_structured_outputs(row: Mapping[str, object]) -> bool:
    supported = row.get("supported_parameters")
    if not isinstance(supported, list):
        return False
    normalized = {str(value).strip().casefold() for value in supported}
    return "structured_outputs" in normalized


def _credential_is_valid(response: HttpResponse) -> bool:
    if response.status_code < 200 or response.status_code >= 300:
        return False
    try:
        payload = json.loads(response.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False
    return isinstance(payload, dict) and isinstance(payload.get("data"), dict)
