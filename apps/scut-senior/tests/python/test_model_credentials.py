from __future__ import annotations

import base64
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from scut_senior_api.auth import AuthRequired, GitHubUserProfile, SESSION_COOKIE_NAME
from scut_senior_api.config import Settings, UnsafeRuntimeConfiguration
from scut_senior_api.contracts import ModelCredentialUpsert
from scut_senior_api.credentials import (
    CREDENTIAL_ALGORITHM,
    CredentialCipher,
    CredentialDecryptionError,
)
from scut_senior_api.main import create_app


MASTER_KEY_BYTES = bytes(range(32))
MASTER_KEY_B64 = base64.b64encode(MASTER_KEY_BYTES).decode("ascii")
PROVIDERS = ("openrouter", "deepseek", "siliconflow", "zhipu")


class MutableClock:
    def __init__(self, current: datetime):
        self.current = current

    def __call__(self) -> datetime:
        return self.current

    def advance(self, delta: timedelta) -> None:
        self.current += delta


def byok_settings(database_path: Path, *, master_key: str = MASTER_KEY_B64) -> Settings:
    return Settings(
        app_env="test",
        identity_mode="github_oauth",
        storage_mode="sqlite",
        database_path=database_path,
        github_client_id="test-client-id",
        github_client_secret="test-client-secret",
        github_callback_url="https://testserver/api/v1/auth/github/callback",
        post_login_redirect_url="https://testserver/",
        byok_master_key=master_key,
        byok_key_version=7,
    )


def authenticated_client(
    app, *, github_id: int = 101, login: str = "student"
) -> tuple[TestClient, str]:
    repository = app.state.repository
    user_id = repository.upsert_github_user(GitHubUserProfile(github_id, login))
    session = repository.issue_session(user_id)
    client = TestClient(app, base_url="https://testserver")
    client.cookies.set(SESSION_COOKIE_NAME, session.token, path="/")
    return client, session.token


def test_master_key_is_strict_aes256_base64_and_never_appears_in_repr(
    tmp_path: Path,
) -> None:
    settings = byok_settings(tmp_path / "valid.db")
    settings.assert_safe()

    assert settings.byok_master_key_bytes() == MASTER_KEY_BYTES
    assert MASTER_KEY_B64 not in repr(settings)

    for invalid in ("not-base64", base64.b64encode(b"short").decode(), f" {MASTER_KEY_B64}"):
        with pytest.raises(UnsafeRuntimeConfiguration):
            byok_settings(tmp_path / "invalid.db", master_key=invalid).assert_safe()

    with pytest.raises(UnsafeRuntimeConfiguration, match="github_oauth"):
        Settings(
            app_env="development",
            byok_master_key=MASTER_KEY_B64,
        ).assert_safe()


def test_aesgcm_detects_tampering_and_binds_user_and_provider() -> None:
    from uuid import uuid4

    cipher = CredentialCipher(MASTER_KEY_BYTES, 7)
    user_id = uuid4()
    encrypted = cipher.encrypt(
        "sk-private",
        user_id=user_id,
        provider_id="openrouter",
    )

    assert cipher.decrypt(
        encrypted,
        user_id=user_id,
        provider_id="openrouter",
    ) == "sk-private"
    assert "sk-private" not in repr(encrypted)

    mutated = encrypted.__class__(
        ciphertext=encrypted.ciphertext[:-1]
        + bytes([encrypted.ciphertext[-1] ^ 1]),
        nonce=encrypted.nonce,
        key_version=encrypted.key_version,
        algorithm=encrypted.algorithm,
    )
    for candidate in (
        mutated,
        encrypted.__class__(
            encrypted.ciphertext,
            encrypted.nonce,
            encrypted.key_version + 1,
        ),
    ):
        with pytest.raises(CredentialDecryptionError):
            cipher.decrypt(
                candidate,
                user_id=user_id,
                provider_id="openrouter",
            )
    # Cross-device: the AAD binds user_id + provider_id, not a login session.
    with pytest.raises(CredentialDecryptionError):
        cipher.decrypt(
            encrypted,
            user_id=uuid4(),
            provider_id="openrouter",
        )
    with pytest.raises(CredentialDecryptionError):
        cipher.decrypt(
            encrypted,
            user_id=user_id,
            provider_id="deepseek",
        )


def test_mock_identity_cannot_manage_credentials_even_with_a_test_master_key(
    tmp_path: Path,
) -> None:
    app = create_app(
        Settings(
            app_env="test",
            database_path=tmp_path / "mock.db",
            byok_master_key=MASTER_KEY_B64,
        )
    )
    client = TestClient(app)

    models = client.get("/api/v1/models").json()
    assert models["byok_available"] is False
    assert all(item["enabled"] is False for item in models["byok_providers"])
    for method, url, payload in (
        ("get", "/api/v1/model-credentials", None),
        ("put", "/api/v1/model-credentials/openrouter", {"api_key": "secret"}),
        ("delete", "/api/v1/model-credentials/openrouter", None),
    ):
        response = getattr(client, method)(url, json=payload) if payload else getattr(client, method)(url)
        assert response.status_code == 401
        assert response.headers["cache-control"] == "private, no-store"


def test_crud_returns_only_masked_metadata_and_database_contains_only_aead(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "credentials.db"
    app = create_app(byok_settings(database_path))
    client, token = authenticated_client(app)
    secret = "sk-user-private-value"

    catalog = client.get("/api/v1/models").json()
    assert catalog["byok_available"] is True
    assert [item["provider_id"] for item in catalog["byok_providers"]] == list(PROVIDERS)
    assert all(item["enabled"] is True for item in catalog["byok_providers"])

    initial = client.get("/api/v1/model-credentials")
    assert initial.status_code == 200
    assert initial.headers["cache-control"] == "private, no-store"
    assert [item["provider_id"] for item in initial.json()] == list(PROVIDERS)
    assert all(item["configured"] is False for item in initial.json())
    assert all(item["writable"] is False for item in initial.json())
    assert all(item["source"] == "user_key" for item in initial.json())
    assert all(item["updated_at"] is None for item in initial.json())

    saved = client.put(
        "/api/v1/model-credentials/openrouter",
        json={"api_key": secret},
    )
    assert saved.status_code == 200, saved.text
    assert saved.headers["cache-control"] == "private, no-store"
    assert saved.json() == {
        "provider_id": "openrouter",
        "model_id": "deepseek/deepseek-v4-flash-0731",
        "configured": True,
        "masked_key": "••••••••",
        "expires_at": saved.json()["expires_at"],
        "writable": True,
        "source": "user_key",
        "updated_at": saved.json()["updated_at"],
    }
    assert secret not in saved.text
    assert token not in saved.text

    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            """
            SELECT ciphertext, nonce, algorithm, key_version, expires_at
            FROM model_credentials
            """
        ).fetchone()
        session_expiry = connection.execute(
            "SELECT expires_at FROM auth_sessions"
        ).fetchone()[0]
    assert row is not None
    assert bytes(row["ciphertext"]) != secret.encode()
    assert len(bytes(row["nonce"])) == 12
    assert row["algorithm"] == CREDENTIAL_ALGORITHM
    assert row["key_version"] == 7
    # Per-user credentials expire on a fixed long horizon, not with the session.
    assert row["expires_at"] != session_expiry
    assert datetime.fromisoformat(row["expires_at"]) > datetime.now(UTC)
    assert secret.encode() not in database_path.read_bytes()


def test_replace_restart_same_session_and_new_session_isolation(tmp_path: Path) -> None:
    database_path = tmp_path / "restart.db"
    settings = byok_settings(database_path)
    app = create_app(settings)
    client, token = authenticated_client(app)

    for secret in ("sk-old", "sk-new"):
        response = client.put(
            "/api/v1/model-credentials/deepseek", json={"api_key": secret}
        )
        assert response.status_code == 200
    with sqlite3.connect(database_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM model_credentials"
        ).fetchone()[0] == 1

    restarted = create_app(settings)
    same_session = TestClient(restarted, base_url="https://testserver")
    same_session.cookies.set(SESSION_COOKIE_NAME, token, path="/")
    statuses = same_session.get("/api/v1/model-credentials")
    assert next(
        item for item in statuses.json() if item["provider_id"] == "deepseek"
    )["configured"] is True
    principal = restarted.state.repository.authenticate_session(token)
    assert principal is not None
    assert restarted.state.credential_manager.load_api_key(
        principal, "deepseek"
    ) == "sk-new"

    user_id = principal.user_id
    new_session = restarted.state.repository.issue_session(user_id)
    other_tab = TestClient(restarted, base_url="https://testserver")
    other_tab.cookies.set(SESSION_COOKIE_NAME, new_session.token, path="/")
    # Cross-device: a different session of the same GitHub account sees the key.
    assert next(
        item
        for item in other_tab.get("/api/v1/model-credentials").json()
        if item["provider_id"] == "deepseek"
    )["configured"] is True


def test_logout_delete_expiry_and_restore_physically_remove_credentials(
    tmp_path: Path,
) -> None:
    clock = MutableClock(datetime(2026, 8, 16, 8, 0, tzinfo=UTC))
    database_path = tmp_path / "lifecycle.db"
    settings = byok_settings(database_path)
    app = create_app(settings, clock=clock)
    client, _ = authenticated_client(app)

    assert client.put(
        "/api/v1/model-credentials/siliconflow", json={"api_key": "sk-life"}
    ).status_code == 200
    deleted = client.delete("/api/v1/model-credentials/siliconflow")
    assert deleted.status_code == 204
    assert deleted.headers["cache-control"] == "private, no-store"
    assert client.put(
        "/api/v1/model-credentials/zhipu", json={"api_key": "sk-life-2"}
    ).status_code == 200
    assert client.post("/api/v1/auth/logout").status_code == 200
    with sqlite3.connect(database_path) as connection:
        # Cross-device: the key belongs to the account and survives one logout.
        assert connection.execute(
            "SELECT COUNT(*) FROM model_credentials"
        ).fetchone()[0] == 1

    expiring, _ = authenticated_client(app, github_id=202, login="expiring")
    assert expiring.put(
        "/api/v1/model-credentials/openrouter", json={"api_key": "sk-expire"}
    ).status_code == 200
    clock.advance(timedelta(days=7))
    assert expiring.get("/api/v1/model-credentials").status_code == 401
    with sqlite3.connect(database_path) as connection:
        # Credentials persist per-account even after the session expires.
        assert connection.execute(
            "SELECT COUNT(*) FROM model_credentials"
        ).fetchone()[0] == 2

    fresh, _ = authenticated_client(app, github_id=303, login="backup")
    assert fresh.put(
        "/api/v1/model-credentials/deepseek", json={"api_key": "sk-backup"}
    ).status_code == 200
    backup_path = tmp_path / "backup.db"
    app.state.repository.backup_to(backup_path)
    assert b"sk-backup" not in backup_path.read_bytes()
    restored_path = tmp_path / "restored.db"
    restored = app.state.repository.restore_from_backup(
        backup_path, restored_path, clock=clock
    )
    with restored.connect() as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM auth_sessions"
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM model_credentials"
        ).fetchone()[0] == 3


def test_provider_and_base_url_contract_rejects_secret_without_reflection(
    tmp_path: Path,
) -> None:
    app = create_app(byok_settings(tmp_path / "whitelist.db"))
    client, _ = authenticated_client(app)
    secret = "sk-never-reflect"

    unknown = client.put(
        "/api/v1/model-credentials/not-a-provider", json={"api_key": secret}
    )
    assert unknown.status_code == 422
    assert secret not in unknown.text
    extra = client.put(
        "/api/v1/model-credentials/openrouter",
        json={"api_key": secret, "base_url": "https://evil.invalid/v1"},
    )
    assert extra.status_code == 422
    assert secret not in extra.text
    with sqlite3.connect(app.state.settings.database_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM model_credentials"
        ).fetchone()[0] == 0


def test_stale_principal_is_revalidated_before_credential_write(tmp_path: Path) -> None:
    app = create_app(byok_settings(tmp_path / "stale.db"))
    _, token = authenticated_client(app)
    principal = app.state.repository.authenticate_session(token)
    assert principal is not None
    assert app.state.repository.revoke_session(token) is True

    with pytest.raises(AuthRequired):
        app.state.credential_manager.replace(
            principal,
            "openrouter",
            ModelCredentialUpsert(api_key="sk-too-late"),
        )
    with sqlite3.connect(app.state.settings.database_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM model_credentials"
        ).fetchone()[0] == 0


def test_revoke_after_replace_persists_per_user_credential(tmp_path: Path) -> None:
    app = create_app(byok_settings(tmp_path / "replace-race.db"))
    repository = app.state.repository

    user_id = repository.upsert_github_user(GitHubUserProfile(7000, "race"))
    session = repository.issue_session(user_id)
    principal = repository.authenticate_session(session.token)
    assert principal is not None

    status = app.state.credential_manager.replace(
        principal,
        "openrouter",
        ModelCredentialUpsert(api_key="sk-race"),
    )
    assert status.configured is True
    # Cross-device: revoking the session that wrote the key must not clear the
    # account's credential (it is not session-bound anymore).
    assert repository.revoke_session(session.token) is True
    with sqlite3.connect(app.state.settings.database_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM model_credentials WHERE user_id = ? AND provider_id = ?",
            (str(user_id), "openrouter"),
        ).fetchone()[0] == 1
