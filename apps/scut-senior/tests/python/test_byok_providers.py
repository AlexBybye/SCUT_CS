import json

import pytest

from scut_senior_api.byok_catalog import (
    BYOK_CATALOG_VERSION,
    ByokModelNotRegistered,
    ByokProviderCatalog,
    ByokProviderNotRegistered,
    EndpointPolicy,
)


EXPECTED_PROVIDER_IDS = ("openrouter", "deepseek", "siliconflow", "zhipu")
EXPECTED_PROVIDER_COMPANIES = {
    "openrouter": "OpenRouter",
    "deepseek": "DeepSeek",
    "siliconflow": "SiliconFlow",
    "zhipu": "Zhipu AI",
}
EXPECTED_MODELS = {
    "openrouter": {
        "model_id": "deepseek/deepseek-v4-flash-0731",
        "company": "DeepSeek",
        "display_name": "DeepSeek V4 Flash 0731",
    },
    "deepseek": {
        "model_id": "deepseek-v4-flash",
        "company": "DeepSeek",
        "display_name": "DeepSeek V4 Flash",
    },
    "siliconflow": {
        "model_id": "Pro/zai-org/GLM-4.7",
        "company": "Z.ai",
        "display_name": "GLM-4.7 Pro",
    },
    "zhipu": {
        "model_id": "glm-5.2",
        "company": "Zhipu AI",
        "display_name": "GLM-5.2",
    },
}


def test_byok_catalog_freezes_exact_provider_whitelist_disabled_by_default() -> None:
    catalog = ByokProviderCatalog()
    payload = catalog.public_payload()

    assert payload["catalog_version"] == BYOK_CATALOG_VERSION
    assert payload["enabled"] is False
    assert tuple(
        entry.provider_id.value for entry in catalog.entries
    ) == EXPECTED_PROVIDER_IDS
    assert [provider["provider_id"] for provider in payload["providers"]] == list(
        EXPECTED_PROVIDER_IDS
    )
    assert {
        provider["provider_id"]: provider["company"]
        for provider in payload["providers"]
    } == EXPECTED_PROVIDER_COMPANIES
    assert all(provider["enabled"] is False for provider in payload["providers"])
    assert all(
        provider["models_confirmed"] is True for provider in payload["providers"]
    )
    assert {
        provider["provider_id"]: provider["models"][0]
        for provider in payload["providers"]
    } == EXPECTED_MODELS
    assert all(len(provider["models"]) == 1 for provider in payload["providers"])


def test_runtime_gate_enables_all_four_fixed_providers_together() -> None:
    payload = ByokProviderCatalog(runtime_enabled=True).public_payload()

    assert payload["enabled"] is True
    assert all(provider["enabled"] is True for provider in payload["providers"])


@pytest.mark.parametrize(
    "provider_id",
    [
        "openrouter ",
        "OPENROUTER",
        "https://openrouter.example.invalid",
    ],
)
def test_byok_catalog_rejects_unregistered_or_url_like_provider_ids(
    provider_id: str,
) -> None:
    with pytest.raises(ByokProviderNotRegistered):
        ByokProviderCatalog().resolve_provider(provider_id)


def test_public_metadata_publishes_only_controlled_models_and_no_base_urls() -> None:
    payload = ByokProviderCatalog().public_payload()
    serialized = json.dumps(payload, ensure_ascii=False)

    assert "https://" not in serialized
    assert all(
        "base_url" not in provider
        and provider["custom_base_url_allowed"] is False
        for provider in payload["providers"]
    )


@pytest.mark.parametrize(
    ("provider_id", "model_id"),
    [
        ("openrouter", "deepseek/deepseek-v4-flash-0731"),
        ("deepseek", "deepseek-v4-flash"),
        ("siliconflow", "Pro/zai-org/GLM-4.7"),
        ("zhipu", "glm-5.2"),
    ],
)
def test_byok_catalog_resolves_only_confirmed_models(
    provider_id: str, model_id: str
) -> None:
    model = ByokProviderCatalog().resolve_model(provider_id, model_id)

    assert model.model_id == model_id


@pytest.mark.parametrize(
    ("provider_id", "model_id"),
    [
        ("openrouter", "openai/gpt-4o"),
        ("openrouter", "deepseek/deepseek-v4-flash-0731 "),
        ("deepseek", "DEEPSEEK-V4-FLASH"),
        ("siliconflow", "https://attacker.example.invalid/v1"),
        ("siliconflow", "Pro/zai-org/GLM-4.7-latest"),
        ("zhipu", "glm-5.3"),
    ],
)
def test_byok_catalog_rejects_arbitrary_model_ids(
    provider_id: str, model_id: str
) -> None:
    with pytest.raises(ByokModelNotRegistered):
        ByokProviderCatalog().resolve_model(provider_id, model_id)


@pytest.mark.parametrize("provider_id", EXPECTED_PROVIDER_IDS)
def test_all_providers_publish_only_the_fixed_endpoint_policy(provider_id: str) -> None:
    catalog = ByokProviderCatalog()
    entry = catalog.resolve_provider(provider_id)
    public_entry = next(
        item for item in catalog.public_payload()["providers"]
        if item["provider_id"] == provider_id
    )

    assert entry.endpoint_policy is EndpointPolicy.FIXED_PROVIDER_ENDPOINT
    assert public_entry["endpoint_policy"] == "fixed_provider_endpoint"
    assert set(public_entry) == {
        "provider_id",
        "company",
        "display_name",
        "enabled",
        "models_confirmed",
        "models",
        "custom_base_url_allowed",
        "endpoint_policy",
    }
