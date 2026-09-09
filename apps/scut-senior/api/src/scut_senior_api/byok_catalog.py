from __future__ import annotations


BYOK_CATALOG_VERSION = "byok-connections-v1"


class ByokProviderCatalog:
    """Advertise the custom-connection BYOK capability.

    Provider profiles are user-owned records and therefore do not belong in
    the process-wide model catalog. Authenticated users obtain their own
    redacted connections from ``/api/v1/model-credentials``.
    """

    def __init__(self, *, runtime_enabled: bool = False) -> None:
        self.runtime_enabled = runtime_enabled
        self.entries: tuple[()] = ()

    def public_payload(self) -> dict[str, object]:
        return {
            "catalog_version": BYOK_CATALOG_VERSION,
            "enabled": self.runtime_enabled,
            "providers": [],
        }
