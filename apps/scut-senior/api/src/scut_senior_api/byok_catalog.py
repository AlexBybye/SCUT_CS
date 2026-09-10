from __future__ import annotations

BYOK_CATALOG_VERSION = "byok-connections-v1"


class ByokProviderCatalog:
    """Advertise the account-owned custom-connection BYOK capability."""

    def __init__(self, *, runtime_enabled: bool = False) -> None:
        self.runtime_enabled = runtime_enabled
        self.entries: tuple[()] = ()

    def public_payload(self) -> dict[str, object]:
        return {
            "catalog_version": BYOK_CATALOG_VERSION,
            "enabled": self.runtime_enabled,
            "providers": [],
        }
