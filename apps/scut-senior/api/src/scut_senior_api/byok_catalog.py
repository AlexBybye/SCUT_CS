from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum


BYOK_CATALOG_VERSION = "byok-models-v4"


class ByokProviderId(StrEnum):
    OPENROUTER = "openrouter"
    DEEPSEEK = "deepseek"
    SILICONFLOW = "siliconflow"
    ZHIPU = "zhipu"


class EndpointPolicy(StrEnum):
    FIXED_PROVIDER_ENDPOINT = "fixed_provider_endpoint"


class ByokProviderNotRegistered(ValueError):
    pass


class ByokModelNotRegistered(ValueError):
    pass


class ByokProviderDisabled(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ByokModelEntry:
    model_id: str
    company: str
    display_name: str

    def as_public_dict(self) -> dict[str, str]:
        return {
            "model_id": self.model_id,
            "company": self.company,
            "display_name": self.display_name,
        }


@dataclass(frozen=True, slots=True)
class ByokProviderEntry:
    """Fixed provider/model metadata plus a runtime-derived availability gate."""

    provider_id: ByokProviderId
    company: str
    display_name: str
    endpoint_policy: EndpointPolicy
    models: tuple[ByokModelEntry, ...]
    enabled: bool = False
    models_confirmed: bool = True
    custom_base_url_allowed: bool = False

    def as_public_dict(self) -> dict[str, object]:
        return {
            "provider_id": self.provider_id.value,
            "company": self.company,
            "display_name": self.display_name,
            "enabled": self.enabled,
            "models_confirmed": self.models_confirmed,
            "models": [model.as_public_dict() for model in self.models],
            "custom_base_url_allowed": self.custom_base_url_allowed,
            "endpoint_policy": self.endpoint_policy.value,
        }


_BYOK_PROVIDER_ENTRIES = (
    ByokProviderEntry(
        provider_id=ByokProviderId.OPENROUTER,
        company="OpenRouter",
        display_name="OpenRouter",
        endpoint_policy=EndpointPolicy.FIXED_PROVIDER_ENDPOINT,
        models=(
            ByokModelEntry(
                model_id="deepseek/deepseek-v4-flash-0731",
                company="DeepSeek",
                display_name="DeepSeek V4 Flash 0731",
            ),
        ),
    ),
    ByokProviderEntry(
        provider_id=ByokProviderId.DEEPSEEK,
        company="DeepSeek",
        display_name="DeepSeek",
        endpoint_policy=EndpointPolicy.FIXED_PROVIDER_ENDPOINT,
        models=(
            ByokModelEntry(
                model_id="deepseek-v4-flash",
                company="DeepSeek",
                display_name="DeepSeek V4 Flash",
            ),
        ),
    ),
    ByokProviderEntry(
        provider_id=ByokProviderId.SILICONFLOW,
        company="SiliconFlow",
        display_name="硅基流动",
        endpoint_policy=EndpointPolicy.FIXED_PROVIDER_ENDPOINT,
        models=(
            ByokModelEntry(
                model_id="Pro/zai-org/GLM-4.7",
                company="Z.ai",
                display_name="GLM-4.7 Pro",
            ),
        ),
    ),
    ByokProviderEntry(
        provider_id=ByokProviderId.ZHIPU,
        company="Zhipu AI",
        display_name="智谱 AI",
        endpoint_policy=EndpointPolicy.FIXED_PROVIDER_ENDPOINT,
        models=(
            ByokModelEntry(
                model_id="glm-5.2",
                company="Zhipu AI",
                display_name="GLM-5.2",
            ),
        ),
    ),
)


class ByokProviderCatalog:
    """Strict four-provider whitelist with one fixed model per provider."""

    def __init__(self, *, runtime_enabled: bool = False) -> None:
        self.entries = tuple(
            replace(
                entry,
                enabled=runtime_enabled,
            )
            for entry in _BYOK_PROVIDER_ENTRIES
        )
        self._by_provider_id = {
            entry.provider_id.value: entry for entry in self.entries
        }

    def resolve_provider(self, provider_id: str) -> ByokProviderEntry:
        entry = self._by_provider_id.get(provider_id)
        if entry is None:
            raise ByokProviderNotRegistered("BYOK provider is not registered")
        return entry

    def require_enabled(self, provider_id: str) -> ByokProviderEntry:
        entry = self.resolve_provider(provider_id)
        if not entry.enabled:
            raise ByokProviderDisabled("BYOK provider is disabled")
        return entry

    def resolve_model(self, provider_id: str, model_id: str) -> ByokModelEntry:
        entry = self.resolve_provider(provider_id)
        model = next(
            (model for model in entry.models if model.model_id == model_id),
            None,
        )
        if model is None:
            raise ByokModelNotRegistered("BYOK model is not registered")
        return model

    def public_payload(self) -> dict[str, object]:
        return {
            "catalog_version": BYOK_CATALOG_VERSION,
            "enabled": any(entry.enabled for entry in self.entries),
            "providers": [entry.as_public_dict() for entry in self.entries],
        }
