import pytest

from scut_senior_api.byok_catalog import BYOK_CATALOG_VERSION, ByokProviderCatalog
from scut_senior_api.model_credentials import (
    ModelCredentialError,
    normalize_base_url,
    normalize_connection_id,
)


def test_byok_catalog_advertises_dynamic_connections_without_global_entries() -> None:
    disabled = ByokProviderCatalog().public_payload()
    enabled = ByokProviderCatalog(runtime_enabled=True).public_payload()

    assert disabled == {
        "catalog_version": BYOK_CATALOG_VERSION,
        "enabled": False,
        "providers": [],
    }
    assert enabled == {
        "catalog_version": "byok-connections-v1",
        "enabled": True,
        "providers": [],
    }


@pytest.mark.parametrize("value", ["my-provider", "deepseek", "p2"])
def test_connection_id_accepts_stable_user_defined_routes(value: str) -> None:
    assert normalize_connection_id(value) == value


@pytest.mark.parametrize(
    "value",
    ["", "OpenRouter", "two words", "https://provider.test", "-bad", "bad_underscore"],
)
def test_connection_id_rejects_ambiguous_or_url_like_values(value: str) -> None:
    with pytest.raises(ModelCredentialError) as caught:
        normalize_connection_id(value)
    assert caught.value.code == "invalid_byok_connection_id"


def test_base_url_normalizes_a_public_https_provider() -> None:
    assert normalize_base_url(" https://API.example.com:8443/v1/ ") == (
        "https://api.example.com:8443/v1"
    )
    assert normalize_base_url("https://[2606:4700:4700::1111]:8443/v1/") == (
        "https://[2606:4700:4700::1111]:8443/v1"
    )


@pytest.mark.parametrize(
    "value",
    [
        "http://api.example.com/v1",
        "https://user:pass@example.com/v1",
        "https://example.com/v1?key=secret",
        "https://invalid host.example/v1",
        "https://intranet/v1",
        "https://localhost/v1",
        "https://service。localhost/v1",
        "https://127.0.0.1/v1",
        "https://169.254.169.254/latest",
        "https://10.0.0.2/v1",
    ],
)
def test_base_url_rejects_unsafe_server_side_destinations(value: str) -> None:
    with pytest.raises(ModelCredentialError) as caught:
        normalize_base_url(value)
    assert caught.value.code == "invalid_byok_base_url"
