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
    # Iteration 7.5 follow-up (registered improvement candidate, implemented
    # 2026-08-23): lexical relevance floor for local-corpus retrieval.
    # PLAN-2 阶段一 步骤 2 upgrades the floor to a BM25F score threshold;
    # candidates scoring below it are dropped so incidental n-gram collisions
    # cannot reach the citation guard. Recalibrated from the P0 golden set.
    retrieval_min_score: float = 1.0
    # PLAN-2 阶段一 步骤 3: the dense leg is enabled by default and uses a
    # CPU-only ONNX model when its model directory and vectors are available.
    # Missing local assets degrade to BM25F without a network call.
    dense_retrieval_enabled: bool = True
    onnx_embedding_model_path: Path | None = APP_ROOT / ".local" / "models" / "bge-small-zh-v1.5"
    onnx_embedding_model_id: str = "bge-small-zh-v1.5"
    onnx_embedding_dimensions: int = 512
    onnx_embedding_max_length: int = 512
    database_path: Path = APP_ROOT / ".local" / "iteration-zero.db"
    corpus_store_path: Path = APP_ROOT / ".local" / "corpus-store"
    # Enabled for the local fixture profile so the shipped cross-course UI is
    # immediately testable; production deployments can explicitly disable it.
    cross_course_enabled: bool = True
    bilibili_resources_enabled: bool = True
    # Iteration 5 (SOP §10): deterministic exam-review planning. The flag
    # only gates the plan node, appendix and past-exam-first retrieval query;
    # turning it off restores the pre-iteration-5 exam_review behaviour.
    exam_review_plan_enabled: bool = True
    # Phase-two agent progress events are opt-in for old NDJSON clients.
    agent_event_stream_enabled: bool = False
    # Iteration 7.5 (SOP §12A Group B): in-process periodic cleanup scheduler.
    # Decision gate confirmed form = in-process daemon thread for single-host
    # deployment; disabling restores startup/access-triggered cleanup only.
    maintenance_scheduler_enabled: bool = True
    maintenance_interval_seconds: int = 3600
    openrouter_api_key: str | None = field(default=None, repr=False)
    zhipu_api_key: str | None = field(default=None, repr=False)
    byok_master_key: str | None = field(default=None, repr=False)
    byok_key_version: int = 1
    github_client_id: str | None = None
    github_client_secret: str | None = field(default=None, repr=False)
    github_callback_url: str | None = None
    post_login_redirect_url: str | None = None
    maintainer_github_user_ids: tuple[int, ...] = ()
    maintainer_github_logins: tuple[str, ...] = ()

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_env=os.getenv("SCUT_SENIOR_APP_ENV", "development"),
            identity_mode=os.getenv("SCUT_SENIOR_IDENTITY_MODE", "mock"),
            model_mode=os.getenv("SCUT_SENIOR_MODEL_MODE", "mock"),
            storage_mode=os.getenv("SCUT_SENIOR_STORAGE_MODE", "sqlite_mock"),
            # The running application uses the activated corpus by default;
            # fixture retrieval remains available for isolated tests via an
            # explicit Settings(retrieval_mode="fixture") or environment override.
            retrieval_mode=os.getenv("SCUT_SENIOR_RETRIEVAL_MODE", "local_corpus"),
            retrieval_min_score=_env_positive_float(
                "SCUT_SENIOR_RETRIEVAL_MIN_SCORE", 1.0
            ),
            dense_retrieval_enabled=_env_bool(
                "SCUT_SENIOR_DENSE_RETRIEVAL_ENABLED", True
            ),
            onnx_embedding_model_path=(
                Path(value)
                if (value := os.getenv("SCUT_SENIOR_ONNX_MODEL_PATH"))
                else APP_ROOT / ".local" / "models" / "bge-small-zh-v1.5"
            ),
            onnx_embedding_model_id=os.getenv(
                "SCUT_SENIOR_ONNX_MODEL_ID", "bge-small-zh-v1.5"
            ),
            onnx_embedding_dimensions=_env_positive_int(
                "SCUT_SENIOR_ONNX_EMBEDDING_DIMENSIONS", 512
            ),
            onnx_embedding_max_length=_env_positive_int(
                "SCUT_SENIOR_ONNX_MAX_LENGTH", 512
            ),
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
            cross_course_enabled=_env_bool("SCUT_SENIOR_CROSS_COURSE_ENABLED", True),
            bilibili_resources_enabled=_env_bool(
                "SCUT_SENIOR_BILIBILI_RESOURCES_ENABLED", True
            ),
            exam_review_plan_enabled=_env_bool(
                "SCUT_SENIOR_EXAM_REVIEW_PLAN_ENABLED", True
            ),
            agent_event_stream_enabled=_env_bool(
                "SCUT_SENIOR_AGENT_EVENT_STREAM_ENABLED", False
            ),
            maintenance_scheduler_enabled=_env_bool(
                "SCUT_SENIOR_MAINTENANCE_SCHEDULER_ENABLED", True
            ),
            maintenance_interval_seconds=_env_positive_int(
                "SCUT_SENIOR_MAINTENANCE_INTERVAL_SECONDS", 3600
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
            maintainer_github_user_ids=tuple(
                int(value.strip())
                for value in os.getenv("SCUT_SENIOR_MAINTAINER_GITHUB_USER_IDS", "").split(",")
                if value.strip().isdigit()
            ),
            maintainer_github_logins=tuple(
                value.strip()
                for value in os.getenv("SCUT_SENIOR_MAINTAINER_GITHUB_LOGINS", "").split(",")
                if value.strip()
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
        if isinstance(self.maintenance_interval_seconds, bool) or (
            self.maintenance_interval_seconds < 1
        ):
            raise UnsafeRuntimeConfiguration(
                "SCUT_SENIOR_MAINTENANCE_INTERVAL_SECONDS must be a positive integer"
            )
        if self.retrieval_mode not in {"fixture", "local_corpus"}:
            raise UnsafeRuntimeConfiguration(
                "retrieval adapter must be explicit fixture or local_corpus"
            )
        if isinstance(self.dense_retrieval_enabled, bool) is False:
            raise UnsafeRuntimeConfiguration(
                "SCUT_SENIOR_DENSE_RETRIEVAL_ENABLED must be boolean"
            )
        if isinstance(self.agent_event_stream_enabled, bool) is False:
            raise UnsafeRuntimeConfiguration(
                "SCUT_SENIOR_AGENT_EVENT_STREAM_ENABLED must be boolean"
            )
        if self.dense_retrieval_enabled and self.retrieval_mode == "local_corpus":
            if self.onnx_embedding_model_path is None:
                raise UnsafeRuntimeConfiguration(
                    "dense retrieval requires SCUT_SENIOR_ONNX_MODEL_PATH"
                )
            if not self.onnx_embedding_model_id.strip():
                raise UnsafeRuntimeConfiguration(
                    "dense retrieval requires SCUT_SENIOR_ONNX_MODEL_ID"
                )
        if isinstance(self.onnx_embedding_dimensions, bool) or self.onnx_embedding_dimensions < 1:
            raise UnsafeRuntimeConfiguration(
                "SCUT_SENIOR_ONNX_EMBEDDING_DIMENSIONS must be a positive integer"
            )
        if isinstance(self.onnx_embedding_max_length, bool) or self.onnx_embedding_max_length < 8:
            raise UnsafeRuntimeConfiguration(
                "SCUT_SENIOR_ONNX_MAX_LENGTH must be an integer >= 8"
            )
        if isinstance(self.retrieval_min_score, bool) or not (
            isinstance(self.retrieval_min_score, (int, float))
            and self.retrieval_min_score >= 0
        ):
            raise UnsafeRuntimeConfiguration(
                "SCUT_SENIOR_RETRIEVAL_MIN_SCORE must be a non-negative number"
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


def _env_positive_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        parsed = float(value)
    except ValueError:
        raise UnsafeRuntimeConfiguration(f"{name} must be a number") from None
    if parsed < 0:
        raise UnsafeRuntimeConfiguration(f"{name} must be non-negative")
    return parsed


def _assert_https_url(name: str, value: str) -> None:
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.fragment:
        raise UnsafeRuntimeConfiguration(
            f"{name} must be a fixed HTTPS URL without a fragment"
        )
