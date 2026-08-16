from pathlib import Path

import pytest

from scut_senior_api.config import Settings, UnsafeRuntimeConfiguration
from scut_senior_api.main import create_app


def test_production_refuses_mock_adapters(tmp_path: Path) -> None:
    settings = Settings(app_env="production", database_path=tmp_path / "unsafe.db")

    with pytest.raises(UnsafeRuntimeConfiguration, match="refuses production"):
        create_app(settings)


def test_disabled_modes_do_not_silently_construct_mock_adapters(tmp_path: Path) -> None:
    settings = Settings(
        app_env="development",
        identity_mode="disabled",
        model_mode="disabled",
        storage_mode="disabled",
        database_path=tmp_path / "disabled.db",
    )

    with pytest.raises(UnsafeRuntimeConfiguration, match="explicit mock"):
        create_app(settings)
