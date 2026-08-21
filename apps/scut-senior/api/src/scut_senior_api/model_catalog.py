from __future__ import annotations

from collections.abc import Callable, Collection, Mapping
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from threading import Lock
from time import monotonic
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from .byok_catalog import BYOK_CATALOG_VERSION, ByokProviderCatalog
from .contracts import ModelSource


CATALOG_VERSION = "platform-free-v3"
PLATFORM_BILLING_LABEL = "platform_daily_free_quota"
MODEL_HEALTH_TTL = timedelta(minutes=5)
PLATFORM_QUOTA_NOTICE = (
    "平台免费额度由所有用户共享、每日刷新但有限，"
    "并受各上游供应商（OpenRouter、智谱 bigmodel）的每分钟额度及可用性限制。"
)
PLATFORM_DAILY_QUOTA_EXHAUSTED_MESSAGE = (
    "今日平台免费额度已用完，第二天再来重试吧！"
    "着急请使用你自己的 API Key。"
)

ModelAvailabilityStatus = Literal[
    "available",
    "platform_credential_not_configured",
    "health_check_required",
    "health_check_failed",
    "model_unavailable",
    "pricing_or_terms_changed",
    "structured_outputs_unavailable",
]


@dataclass(frozen=True, slots=True)
class ModelHealthResult:
    availability_status: ModelAvailabilityStatus
    checked_at: datetime
    # This is descriptive metadata, not a Workflow admission requirement.
    # Legacy health-check implementations can omit it and remain compatible.
    supports_structured_outputs: bool | None = None


class ModelHealthChecker(Protocol):
    def check(
        self, model_ids: Collection[str]
    ) -> Mapping[str, ModelHealthResult]: ...


Clock = Callable[[], datetime]
MonotonicClock = Callable[[], float]


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class ModelCatalogEntry:
    provider_id: str
    model_id: str
    company: str
    display_name: str
    model_source: ModelSource
    billing_label: str
    availability_status: ModelAvailabilityStatus
    context_length: int
    input_modalities: tuple[str, ...]
    supports_structured_outputs: bool
    is_preview: bool
    user_selectable: bool
    last_checked_at: datetime | None = None

    def as_public_dict(self) -> dict[str, object]:
        return {
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "company": self.company,
            "display_name": self.display_name,
            "model_source": self.model_source.value,
            "billing_label": self.billing_label,
            "availability_status": self.availability_status,
            "context_length": self.context_length,
            "input_modalities": list(self.input_modalities),
            "supports_structured_outputs": self.supports_structured_outputs,
            "is_preview": self.is_preview,
            "user_selectable": self.user_selectable,
            "last_checked_at": (
                self.last_checked_at.isoformat() if self.last_checked_at else None
            ),
        }


class ModelNotRegistered(ValueError):
    pass


class PublicModelCatalogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: Literal["openrouter", "zhipu"]
    model_id: str
    company: str
    display_name: str
    model_source: Literal["platform_default"]
    billing_label: Literal["platform_daily_free_quota"]
    availability_status: ModelAvailabilityStatus
    context_length: int = Field(gt=0)
    input_modalities: list[Literal["text", "image", "video"]]
    supports_structured_outputs: bool
    is_preview: bool
    user_selectable: bool
    last_checked_at: datetime | None


class PublicByokModelEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_id: Literal[
        "deepseek/deepseek-v4-flash-0731",
        "deepseek-v4-flash",
        "Pro/zai-org/GLM-4.7",
        "glm-5.2",
    ]
    company: Literal["DeepSeek", "Z.ai", "Zhipu AI"]
    display_name: str


class PublicByokProviderEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: Literal["openrouter", "deepseek", "siliconflow", "zhipu"]
    company: Literal["OpenRouter", "DeepSeek", "SiliconFlow", "Zhipu AI"]
    display_name: str
    enabled: bool
    models_confirmed: Literal[True]
    models: list[PublicByokModelEntry] = Field(min_length=1, max_length=1)
    custom_base_url_allowed: Literal[False]
    endpoint_policy: Literal["fixed_provider_endpoint"]


class ModelCatalogResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    catalog_version: Literal["platform-free-v3"]
    platform_credential_configured: bool
    real_platform_default_available: bool
    health_checked_at: datetime | None
    byok_available: bool
    byok_catalog_version: Literal["byok-models-v4"]
    byok_providers: list[PublicByokProviderEntry]
    quota_notice: str
    quota_exhausted_message: str
    models: list[PublicModelCatalogEntry]


_OPENROUTER_PLATFORM_MODELS = (
    ModelCatalogEntry(
        provider_id="openrouter",
        model_id="google/gemma-4-26b-a4b-it:free",
        company="Google",
        display_name="Gemma 4 26B A4B",
        model_source=ModelSource.PLATFORM_DEFAULT,
        billing_label=PLATFORM_BILLING_LABEL,
        availability_status="platform_credential_not_configured",
        context_length=262_144,
        input_modalities=("text", "image", "video"),
        supports_structured_outputs=True,
        is_preview=False,
        user_selectable=False,
    ),
    ModelCatalogEntry(
        provider_id="openrouter",
        model_id="dots-studio/dots-3-note-preview:free",
        company="Dots Studio",
        display_name="Dots3 Note Preview",
        model_source=ModelSource.PLATFORM_DEFAULT,
        billing_label=PLATFORM_BILLING_LABEL,
        availability_status="platform_credential_not_configured",
        context_length=512_000,
        input_modalities=("text", "image"),
        supports_structured_outputs=True,
        is_preview=True,
        user_selectable=False,
    ),
    ModelCatalogEntry(
        provider_id="openrouter",
        model_id="nvidia/nemotron-3-super-120b-a12b:free",
        company="NVIDIA",
        display_name="Nemotron 3 Super 120B A12B",
        model_source=ModelSource.PLATFORM_DEFAULT,
        billing_label=PLATFORM_BILLING_LABEL,
        availability_status="platform_credential_not_configured",
        context_length=262_144,
        input_modalities=("text",),
        supports_structured_outputs=True,
        is_preview=False,
        user_selectable=False,
    ),
)


_ZHIPU_PLATFORM_MODELS = (
    ModelCatalogEntry(
        provider_id="zhipu",
        model_id="glm-4.7-flash",
        company="Zhipu AI",
        display_name="GLM-4.7-Flash",
        model_source=ModelSource.PLATFORM_DEFAULT,
        billing_label=PLATFORM_BILLING_LABEL,
        availability_status="platform_credential_not_configured",
        context_length=200_000,
        input_modalities=("text",),
        supports_structured_outputs=True,
        is_preview=False,
        user_selectable=False,
    ),
    ModelCatalogEntry(
        provider_id="zhipu",
        model_id="glm-4-flash-250414",
        company="Zhipu AI",
        display_name="GLM-4-Flash-250414",
        model_source=ModelSource.PLATFORM_DEFAULT,
        billing_label=PLATFORM_BILLING_LABEL,
        availability_status="platform_credential_not_configured",
        context_length=128_000,
        input_modalities=("text",),
        supports_structured_outputs=True,
        is_preview=False,
        user_selectable=False,
    ),
    ModelCatalogEntry(
        provider_id="zhipu",
        model_id="glm-4.6v-flash",
        company="Zhipu AI",
        display_name="GLM-4.6V-Flash",
        model_source=ModelSource.PLATFORM_DEFAULT,
        billing_label=PLATFORM_BILLING_LABEL,
        availability_status="platform_credential_not_configured",
        context_length=128_000,
        input_modalities=("text", "image", "video"),
        supports_structured_outputs=False,
        is_preview=False,
        user_selectable=False,
    ),
)


class ModelCatalog:
    def __init__(
        self,
        *,
        openrouter_credential_configured: bool = False,
        zhipu_credential_configured: bool = False,
        byok_runtime_enabled: bool = False,
        openrouter_health_checker: ModelHealthChecker | None = None,
        zhipu_health_checker: ModelHealthChecker | None = None,
        clock: Clock = utc_now,
        monotonic_clock: MonotonicClock = monotonic,
        health_ttl: timedelta = MODEL_HEALTH_TTL,
    ):
        self._credential_configured = {
            "openrouter": openrouter_credential_configured,
            "zhipu": zhipu_credential_configured,
        }
        self._health_checkers = {
            "openrouter": openrouter_health_checker,
            "zhipu": zhipu_health_checker,
        }
        self.platform_credential_configured = any(
            self._credential_configured.values()
        )
        self._clock = clock
        self._monotonic_clock = monotonic_clock
        self._health_ttl = health_ttl
        self._health_checked_at: datetime | None = None
        self._health_checked_monotonic: float | None = None
        self._health_refreshing = False
        self._health_lock = Lock()
        self.byok_catalog = ByokProviderCatalog(
            runtime_enabled=byok_runtime_enabled
        )
        self.entries = tuple(
            replace(
                entry,
                availability_status=(
                    "health_check_required"
                    if self._credential_configured[entry.provider_id]
                    else "platform_credential_not_configured"
                ),
                user_selectable=False,
                last_checked_at=None,
            )
            for entry in (*_OPENROUTER_PLATFORM_MODELS, *_ZHIPU_PLATFORM_MODELS)
        )
        self._rebuild_index()

    @property
    def health_checked_at(self) -> datetime | None:
        return self._health_checked_at

    @property
    def real_platform_default_available(self) -> bool:
        return any(entry.user_selectable for entry in self.entries)

    def _rebuild_index(self) -> None:
        self._by_key = {
            (entry.provider_id, entry.model_id, entry.model_source): entry
            for entry in self.entries
        }

    def refresh_health(self, *, force: bool = False) -> None:
        if not self.platform_credential_configured:
            return
        now = self._clock()
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("model catalog clock must be timezone-aware")
        now = now.astimezone(UTC)
        now_monotonic = self._monotonic_clock()
        with self._health_lock:
            if (
                not force
                and self._health_checked_monotonic is not None
                and now_monotonic - self._health_checked_monotonic
                < self._health_ttl.total_seconds()
            ):
                return
            if self._health_refreshing:
                return
            self._health_refreshing = True
            model_ids_by_provider = {
                provider_id: [entry.model_id for entry in self.entries
                              if entry.provider_id == provider_id]
                for provider_id, configured in self._credential_configured.items()
                if configured
            }
            self.entries = tuple(
                replace(
                    entry,
                    availability_status=(
                        "health_check_required"
                        if self._credential_configured[entry.provider_id]
                        else "platform_credential_not_configured"
                    ),
                    user_selectable=False,
                )
                for entry in self.entries
            )
            self._rebuild_index()
        checked: dict[str, ModelHealthResult] = {}
        for provider_id in model_ids_by_provider:
            checker = self._health_checkers[provider_id]
            model_ids = model_ids_by_provider[provider_id]
            if checker is None:
                checked.update(
                    {
                        model_id: ModelHealthResult(
                            availability_status="health_check_failed",
                            checked_at=now,
                        )
                        for model_id in model_ids
                    }
                )
                continue
            try:
                checked.update(checker.check(model_ids))
            except Exception:
                checked.update(
                    {
                        model_id: ModelHealthResult(
                            availability_status="health_check_failed",
                            checked_at=now,
                        )
                        for model_id in model_ids
                    }
                )
        try:
            refreshed: list[ModelCatalogEntry] = []
            check_times: list[datetime] = []
            for entry in self.entries:
                if not self._credential_configured[entry.provider_id]:
                    refreshed.append(entry)
                    continue
                result = checked.get(entry.model_id)
                if result is None:
                    result = ModelHealthResult("model_unavailable", now)
                availability_status = result.availability_status
                # A pre-relaxation health checker can still report this legacy
                # status. Structured JSON is now optional, so it must not make
                # an otherwise callable free model disappear from the catalog.
                if availability_status == "structured_outputs_unavailable":
                    availability_status = "available"
                    supports_structured_outputs = False
                elif result.supports_structured_outputs is None:
                    supports_structured_outputs = entry.supports_structured_outputs
                else:
                    supports_structured_outputs = result.supports_structured_outputs
                checked_at = result.checked_at
                if checked_at.tzinfo is None or checked_at.utcoffset() is None:
                    raise ValueError("model health timestamps must be timezone-aware")
                checked_at = checked_at.astimezone(UTC)
                check_times.append(checked_at)
                refreshed.append(
                    replace(
                        entry,
                        availability_status=availability_status,
                        supports_structured_outputs=supports_structured_outputs,
                        user_selectable=availability_status == "available",
                        last_checked_at=checked_at,
                    )
                )
        except Exception:
            refreshed = [
                replace(
                    entry,
                    availability_status="health_check_failed",
                    user_selectable=False,
                    last_checked_at=now,
                )
                if self._credential_configured[entry.provider_id]
                else entry
                for entry in self.entries
            ]
            check_times = [now]
        with self._health_lock:
            self.entries = tuple(refreshed)
            self._health_checked_at = max(check_times, default=now)
            self._health_checked_monotonic = self._monotonic_clock()
            self._rebuild_index()
            self._health_refreshing = False

    def resolve(
        self,
        provider_id: str,
        model_id: str,
        model_source: ModelSource,
    ) -> ModelCatalogEntry:
        self.refresh_health()
        entry = self._by_key.get((provider_id, model_id, model_source))
        if entry is None or not entry.user_selectable:
            raise ModelNotRegistered("所选模型未在当前可用的平台目录中登记。")
        return entry

    def public_payload(self) -> dict[str, object]:
        self.refresh_health()
        byok_payload = self.byok_catalog.public_payload()
        return {
            "catalog_version": CATALOG_VERSION,
            "platform_credential_configured": self.platform_credential_configured,
            "real_platform_default_available": self.real_platform_default_available,
            "health_checked_at": (
                self._health_checked_at.isoformat()
                if self._health_checked_at is not None
                else None
            ),
            "byok_available": bool(byok_payload["enabled"]),
            "byok_catalog_version": BYOK_CATALOG_VERSION,
            "byok_providers": byok_payload["providers"],
            "quota_notice": PLATFORM_QUOTA_NOTICE,
            "quota_exhausted_message": PLATFORM_DAILY_QUOTA_EXHAUSTED_MESSAGE,
            "models": [entry.as_public_dict() for entry in self.entries],
        }
