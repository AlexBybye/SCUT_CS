from __future__ import annotations

from collections.abc import Callable, Collection, Mapping
from datetime import UTC, datetime

from ..model_catalog import ModelHealthResult


Clock = Callable[[], datetime]


def utc_now() -> datetime:
    return datetime.now(UTC)


class ZhipuPlatformHealthChecker:
    """Fail-closed declaration of the fixed Zhipu free models.

    Unlike OpenRouter's community ``:free`` variants, these first-party Zhipu
    bigmodel offerings have documented, stable free status; Zhipu exposes no
    public "list models with zero price" or "key status" endpoint equivalent to
    OpenRouter's to re-verify at runtime. The health check therefore reduces to
    a fail-closed credential declaration: a fixed model is reported
    ``available`` only when a non-empty server key is supplied, and any unknown
    model id is reported ``model_unavailable``.

    ``supports_structured_outputs`` mirrors each model's documented capability
    (glm-4.6v-flash does not declare structured output, so it reports False and
    must not be silently upgraded by a generic declaration).
    """

    _MODEL_IDS = frozenset(
        {"glm-4.7-flash", "glm-4-flash-250414", "glm-4.6v-flash"}
    )
    _STRUCTURED_OUTPUT_MODELS = frozenset({"glm-4.7-flash", "glm-4-flash-250414"})

    def __init__(self, *, api_key: str, clock: Clock = utc_now) -> None:
        if not api_key.strip():
            raise ValueError("Zhipu API key is required for credential health")
        self._api_key = api_key
        self._clock = clock

    def check(
        self, model_ids: Collection[str]
    ) -> Mapping[str, ModelHealthResult]:
        checked_at = self._clock()
        if checked_at.tzinfo is None or checked_at.utcoffset() is None:
            raise ValueError("health-check clock must be timezone-aware")
        checked_at = checked_at.astimezone(UTC)
        return {
            model_id: ModelHealthResult(
                (
                    "available"
                    if model_id in self._MODEL_IDS
                    else "model_unavailable"
                ),
                checked_at,
                supports_structured_outputs=(
                    model_id in self._STRUCTURED_OUTPUT_MODELS
                ),
            )
            for model_id in model_ids
        }
