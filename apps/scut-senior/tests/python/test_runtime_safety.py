from pathlib import Path

import pytest

from scut_senior_api.config import Settings, UnsafeRuntimeConfiguration
from scut_senior_api.main import create_app


def test_dense_retrieval_is_enabled_by_default() -> None:
    settings = Settings()
    assert settings.dense_retrieval_enabled is True
    assert settings.onnx_embedding_model_id == "bge-small-zh-v1.5"
    assert settings.onnx_embedding_dimensions == 512


def test_dense_retrieval_requires_onnx_model_path(tmp_path: Path) -> None:
    settings = Settings(
        app_env="test",
        retrieval_mode="local_corpus",
        dense_retrieval_enabled=True,
        onnx_embedding_model_path=None,
        corpus_store_path=tmp_path,
    )
    with pytest.raises(UnsafeRuntimeConfiguration, match="ONNX_MODEL_PATH"):
        settings.assert_safe()


def test_dense_retrieval_requires_onnx_model_id(tmp_path: Path) -> None:
    settings = Settings(
        app_env="test",
        retrieval_mode="local_corpus",
        dense_retrieval_enabled=True,
        onnx_embedding_model_path=tmp_path,
        onnx_embedding_model_id="",
        corpus_store_path=tmp_path,
    )
    with pytest.raises(UnsafeRuntimeConfiguration, match="ONNX_MODEL_ID"):
        settings.assert_safe()


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


def test_github_oauth_requires_sqlite_https_and_all_server_secrets(tmp_path: Path) -> None:
    incomplete = Settings(
        app_env="test",
        identity_mode="github_oauth",
        storage_mode="sqlite",
        database_path=tmp_path / "missing.db",
    )
    with pytest.raises(UnsafeRuntimeConfiguration, match="GITHUB_CLIENT_ID"):
        create_app(incomplete)

    insecure = Settings(
        app_env="test",
        identity_mode="github_oauth",
        storage_mode="sqlite",
        database_path=tmp_path / "insecure.db",
        github_client_id="client-id",
        github_client_secret="secret",
        github_callback_url="http://localhost/api/v1/auth/github/callback",
        post_login_redirect_url="https://frontend.test/",
    )
    with pytest.raises(UnsafeRuntimeConfiguration, match="fixed HTTPS"):
        create_app(insecure)


def test_oauth_and_platform_secrets_are_absent_from_settings_repr(tmp_path: Path) -> None:
    settings = Settings(
        app_env="test",
        identity_mode="github_oauth",
        storage_mode="sqlite",
        model_mode="openrouter_platform",
        database_path=tmp_path / "safe.db",
        openrouter_api_key="platform-secret-value",
        zhipu_api_key="zhipu-secret-value",
        github_client_id="public-client-id",
        github_client_secret="oauth-secret-value",
        github_callback_url="https://testserver/api/v1/auth/github/callback",
        post_login_redirect_url="https://frontend.test/",
    )

    rendered = repr(settings)
    assert "platform-secret-value" not in rendered
    assert "zhipu-secret-value" not in rendered
    assert "oauth-secret-value" not in rendered


def test_development_openrouter_requires_authenticated_sqlite_runtime(
    tmp_path: Path,
) -> None:
    settings = Settings(
        app_env="development",
        identity_mode="mock",
        model_mode="openrouter_platform",
        storage_mode="sqlite_mock",
        database_path=tmp_path / "anonymous-platform.db",
        openrouter_api_key="server-only-secret",
    )

    with pytest.raises(
        UnsafeRuntimeConfiguration,
        match="requires github_oauth identity and sqlite storage outside test",
    ):
        create_app(settings)

    assert not settings.database_path.exists()


def test_development_openrouter_accepts_authenticated_sqlite_configuration(
    tmp_path: Path,
) -> None:
    settings = Settings(
        app_env="development",
        identity_mode="github_oauth",
        model_mode="openrouter_platform",
        storage_mode="sqlite",
        database_path=tmp_path / "authenticated-platform.db",
        openrouter_api_key="server-only-secret",
        github_client_id="public-client-id",
        github_client_secret="oauth-secret",
        github_callback_url="https://app.example/api/v1/auth/github/callback",
        post_login_redirect_url="https://app.example/",
    )

    settings.assert_safe()


def test_test_environment_keeps_mock_openrouter_override_for_stubbed_calls(
    tmp_path: Path,
) -> None:
    settings = Settings(
        app_env="test",
        identity_mode="mock",
        model_mode="openrouter_platform",
        storage_mode="sqlite_mock",
        database_path=tmp_path / "stubbed-platform.db",
        openrouter_api_key="test-only-stub-secret",
    )

    settings.assert_safe()


def test_production_profile_refuses_any_mock_adapter(tmp_path: Path) -> None:
    settings = Settings(
        app_env="production",
        identity_mode="github_oauth",
        storage_mode="sqlite",
        model_mode="mock",
        database_path=tmp_path / "production.db",
        github_client_id="public-client-id",
        github_client_secret="secret",
        github_callback_url="https://app.example/api/v1/auth/github/callback",
        post_login_redirect_url="https://app.example/",
    )

    with pytest.raises(UnsafeRuntimeConfiguration, match="refuses production"):
        create_app(settings)


def test_production_stays_fail_closed_even_with_identity_and_model_secrets(
    tmp_path: Path,
) -> None:
    settings = Settings(
        app_env="production",
        identity_mode="github_oauth",
        storage_mode="sqlite",
        model_mode="openrouter_platform",
        database_path=tmp_path / "still-closed.db",
        openrouter_api_key="platform-secret",
        github_client_id="public-client-id",
        github_client_secret="oauth-secret",
        github_callback_url="https://app.example/api/v1/auth/github/callback",
        post_login_redirect_url="https://app.example/",
    )

    with pytest.raises(UnsafeRuntimeConfiguration, match="refuses production"):
        create_app(settings)
