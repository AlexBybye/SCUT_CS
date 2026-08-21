from __future__ import annotations

import base64
import binascii
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from .paths import APP_ROOT


class UnsafeRuntimeConfiguration(RuntimeError):
    """Raised when a mock adapter would accidentally run as production."""


@dataclass(frozen=True, slots=True)
class Settings:
    app_env: Literal["development", "test", "production"] = "development"
    identity_mode: Literal["mock", "github_oauth", "disabled"] = "mock"
    model_mode: Literal["mock", "openrouter_platform", "disabled"] = "mock"
    storage_mode: Literal["sqlite_mock", "sqlite", "disabled"] = "sqlite_mock"
    retrieval_mode: Literal["fixture", "local_corpus"] = "fixture"
    database_path: Path = APP_ROOT / ".local" / "iteration-zero.db"
    corpus_store_path: Path = APP_ROOT / ".local" / "corpus-store"
    cross_course_enabled: bool = False
    bilibili_resources_enabled: bool = True
    openrouter_api_key: str | None = field(default=None, repr=False)
    zhipu_api_key: str | None = field(default=None, repr=False)
    byok_master_key: str | None = field(default=None, repr=False)
    byok_key_version: int = 1
    github_client_id: str | None = None
    github_client_secret: str | None = field(default=None, repr=False)
    github_callback_url: str | None = None
    post_login_redirect_url: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_env=os.getenv("SCUT_SENIOR_APP_ENV", "development"),
            identity_mode=os.getenv("SCUT_SENIOR_IDENTITY_MODE", "mock"),
            model_mode=os.getenv("SCUT_SENIOR_MODEL_MODE", "mock"),
            storage_mode=os.getenv("SCUT_SENIOR_STORAGE_MODE", "sqlite_mock"),
            retrieval_mode=os.getenv("SCUT_SENIOR_RETRIEVAL_MODE", "fixture"),
            database_path=Path(
                os.getenv(
                    "SCUT_SENIOR_DATABASE_PATH",
                    str(APP_ROOT / ".local" / "iteration-zero.db"),
                )
            ),
            corpus_store_path=Path(
                os.getenv(
                    "SCUT_SENIOR_CORPUS_STORE_PATH",
                    str(APP_ROOT / ".local" / "corpus-store"),
                )
            ),
            cross_course_enabled=_env_bool("SCUT_SENIOR_CROSS_COURSE_ENABLED", False),
            bilibili_resources_enabled=_env_bool(
                "SCUT_SENIOR_BILIBILI_RESOURCES_ENABLED", True
            ),
            openrouter_api_key=os.getenv("SCUT_SENIOR_OPENROUTER_API_KEY"),
            zhipu_api_key=os.getenv("SCUT_SENIOR_ZHIPU_API_KEY"),
            byok_master_key=os.getenv("SCUT_SENIOR_BYOK_MASTER_KEY"),
            byok_key_version=_env_positive_int(
                "SCUT_SENIOR_BYOK_KEY_VERSION", 1
            ),
            github_client_id=os.getenv("SCUT_SENIOR_GITHUB_CLIENT_ID"),
            github_client_secret=os.getenv("SCUT_SENIOR_GITHUB_CLIENT_SECRET"),
            github_callback_url=os.getenv("SCUT_SENIOR_GITHUB_CALLBACK_URL"),
            post_login_redirect_url=os.getenv(
                "SCUT_SENIOR_POST_LOGIN_REDIRECT_URL"
            ),
        )

    def assert_safe(self) -> None:
        if self.app_env not in {"development", "test", "production"}:
            raise UnsafeRuntimeConfiguration(f"unknown app environment: {self.app_env}")
        if self.identity_mode == "disabled" or self.storage_mode == "disabled":
            raise UnsafeRuntimeConfiguration(
                "identity and storage require explicit mock or production adapters"
            )
        if self.identity_mode == "mock" and self.storage_mode != "sqlite_mock":
            raise UnsafeRuntimeConfiguration(
                "mock identity requires the explicit sqlite_mock storage adapter"
            )
        if self.identity_mode == "github_oauth":
            if self.storage_mode != "sqlite":
                raise UnsafeRuntimeConfiguration(
                    "github_oauth requires the sqlite storage adapter"
                )
            required_oauth_values = {
                "SCUT_SENIOR_GITHUB_CLIENT_ID": self.github_client_id,
                "SCUT_SENIOR_GITHUB_CLIENT_SECRET": self.github_client_secret,
                "SCUT_SENIOR_GITHUB_CALLBACK_URL": self.github_callback_url,
                "SCUT_SENIOR_POST_LOGIN_REDIRECT_URL": self.post_login_redirect_url,
            }
            missing = [
                name
                for name, value in required_oauth_values.items()
                if not value or not value.strip()
            ]
            if missing:
                raise UnsafeRuntimeConfiguration(
                    "github_oauth requires server-side OAuth configuration: "
                    + ", ".join(missing)
                )
            _assert_https_url(
                "SCUT_SENIOR_GITHUB_CALLBACK_URL", self.github_callback_url or ""
            )
            _assert_https_url(
                "SCUT_SENIOR_POST_LOGIN_REDIRECT_URL",
                self.post_login_redirect_url or "",
            )
        elif self.identity_mode != "mock":
            raise UnsafeRuntimeConfiguration(
                f"unknown identity mode: {self.identity_mode}"
            )
        if self.storage_mode not in {"sqlite_mock", "sqlite"}:
            raise UnsafeRuntimeConfiguration(
                f"unknown storage mode: {self.storage_mode}"
            )
        if self.retrieval_mode not in {"fixture", "local_corpus"}:
            raise UnsafeRuntimeConfiguration(
                "retrieval adapter must be explicit fixture or local_corpus"
            )
        if (
            self.retrieval_mode == "local_corpus"
            and not self.corpus_store_path.is_absolute()
        ):
            raise UnsafeRuntimeConfiguration(
                "local_corpus requires an absolute SCUT_SENIOR_CORPUS_STORE_PATH"
            )
        if self.model_mode not in {"mock", "openrouter_platform"}:
            raise UnsafeRuntimeConfiguration(
                "the model adapter must be explicit mock or openrouter_platform"
            )
        platform_key_configured = bool(
            (self.openrouter_api_key and self.openrouter_api_key.strip())
            or (self.zhipu_api_key and self.zhipu_api_key.strip())
        )
        if self.model_mode == "openrouter_platform" and not platform_key_configured:
            raise UnsafeRuntimeConfiguration(
                "openrouter_platform requires SCUT_SENIOR_OPENROUTER_API_KEY "
                "or SCUT_SENIOR_ZHIPU_API_KEY"
            )
        # Test keeps a narrow exception for injected, non-network HTTP transports.
        # Any runnable development or production profile must authenticate users
        # before it can spend the shared server-side platform credentials
        # (OpenRouter and/or Zhipu bigmodel).
        if self.model_mode == "openrouter_platform" and self.app_env != "test":
            if self.identity_mode != "github_oauth" or self.storage_mode != "sqlite":
                raise UnsafeRuntimeConfiguration(
                    "openrouter_platform requires github_oauth identity and sqlite "
                    "storage outside test"
                )
        master_key = self.byok_master_key_bytes()
        if master_key is not None and self.app_env != "test":
            if self.identity_mode != "github_oauth" or self.storage_mode != "sqlite":
                raise UnsafeRuntimeConfiguration(
                    "BYOK master key requires github_oauth identity and sqlite "
                    "storage outside test"
                )
        if self.app_env == "production":
            raise UnsafeRuntimeConfiguration(
                "the partial iteration 1 runtime refuses production startup until "
                "production retrieval, HTTPS deployment, and recovery are validated"
            )

    def byok_master_key_bytes(self) -> bytes | None:
        """Decode the server-only AES-256 key without exposing it in repr/logs."""

        encoded = self.byok_master_key
        if encoded is None or encoded == "":
            return None
        if encoded != encoded.strip():
            raise UnsafeRuntimeConfiguration(
                "SCUT_SENIOR_BYOK_MASTER_KEY must be strict base64 without whitespace"
            )
        try:
            decoded = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError):
            raise UnsafeRuntimeConfiguration(
                "SCUT_SENIOR_BYOK_MASTER_KEY must be valid base64"
            ) from None
        if len(decoded) != 32:
            raise UnsafeRuntimeConfiguration(
                "SCUT_SENIOR_BYOK_MASTER_KEY must decode to exactly 32 bytes"
            )
        if isinstance(self.byok_key_version, bool) or self.byok_key_version < 1:
            raise UnsafeRuntimeConfiguration(
                "SCUT_SENIOR_BYOK_KEY_VERSION must be a positive integer"
            )
        return decoded


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_positive_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError:
        raise UnsafeRuntimeConfiguration(f"{name} must be a positive integer") from None
    if parsed < 1:
        raise UnsafeRuntimeConfiguration(f"{name} must be a positive integer")
    return parsed


def _assert_https_url(name: str, value: str) -> None:
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.fragment:
        raise UnsafeRuntimeConfiguration(
            f"{name} must be a fixed HTTPS URL without a fragment"
        )
