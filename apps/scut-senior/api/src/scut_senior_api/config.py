from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .paths import APP_ROOT


class UnsafeRuntimeConfiguration(RuntimeError):
    """Raised when a mock adapter would accidentally run as production."""


@dataclass(frozen=True, slots=True)
class Settings:
    app_env: Literal["development", "test", "production"] = "development"
    identity_mode: Literal["mock", "disabled"] = "mock"
    model_mode: Literal["mock", "disabled"] = "mock"
    storage_mode: Literal["sqlite_mock", "disabled"] = "sqlite_mock"
    database_path: Path = APP_ROOT / ".local" / "iteration-zero.db"
    cross_course_enabled: bool = False
    bilibili_catalog_enabled: bool = True

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_env=os.getenv("SCUT_SENIOR_APP_ENV", "development"),
            identity_mode=os.getenv("SCUT_SENIOR_IDENTITY_MODE", "mock"),
            model_mode=os.getenv("SCUT_SENIOR_MODEL_MODE", "mock"),
            storage_mode=os.getenv("SCUT_SENIOR_STORAGE_MODE", "sqlite_mock"),
            database_path=Path(
                os.getenv(
                    "SCUT_SENIOR_DATABASE_PATH",
                    str(APP_ROOT / ".local" / "iteration-zero.db"),
                )
            ),
            cross_course_enabled=_env_bool("SCUT_SENIOR_CROSS_COURSE_ENABLED", False),
            bilibili_catalog_enabled=_env_bool(
                "SCUT_SENIOR_BILIBILI_FIXTURE_ENABLED", True
            ),
        )

    def assert_safe(self) -> None:
        if self.app_env not in {"development", "test", "production"}:
            raise UnsafeRuntimeConfiguration(f"unknown app environment: {self.app_env}")
        if self.app_env == "production":
            raise UnsafeRuntimeConfiguration(
                "iteration 0 has no production adapters and refuses production startup"
            )
        active_modes = (self.identity_mode, self.model_mode, self.storage_mode)
        if active_modes != ("mock", "mock", "sqlite_mock"):
            raise UnsafeRuntimeConfiguration(
                "iteration 0 can run only with its explicit mock identity, model, and storage"
            )


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
