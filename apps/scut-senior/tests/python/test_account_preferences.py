from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from scut_senior_api.auth import GitHubUserProfile, SESSION_COOKIE_NAME
from scut_senior_api.config import Settings
from scut_senior_api.main import create_app


def _oauth_settings(database_path: Path) -> Settings:
    return Settings(
        app_env="test",
        identity_mode="github_oauth",
        storage_mode="sqlite",
        database_path=database_path,
        github_client_id="prefs-client",
        github_client_secret="prefs-secret",
        github_callback_url="https://testserver/api/v1/auth/github/callback",
        post_login_redirect_url="https://testserver/",
    )


def _login(app, github_id: int, login: str) -> tuple[TestClient, str]:
    repository = app.state.repository
    user_id = repository.upsert_github_user(GitHubUserProfile(github_id, login))
    session = repository.issue_session(user_id)
    client = TestClient(app, base_url="https://testserver")
    client.cookies.set(SESSION_COOKIE_NAME, session.token, path="/")
    return client, session.token


def test_account_preferences_require_github_login(tmp_path: Path) -> None:
    app = create_app(_oauth_settings(tmp_path / "prefs.db"))
    client = TestClient(app, base_url="https://testserver")
    assert client.get("/api/v1/account/preferences").status_code == 401
    assert client.put(
        "/api/v1/account/preferences", json={"preferences": {"tone": "study_partner"}}
    ).status_code == 401


def test_preferences_survive_relogin_and_are_user_scoped(tmp_path: Path) -> None:
    database_path = tmp_path / "prefs.db"
    app = create_app(_oauth_settings(database_path))
    first, _ = _login(app, 1001, "prefs-user")

    saved = first.put(
        "/api/v1/account/preferences",
        json={
            "preferences": {
                "theme_mode": "1",
                "accent_theme": "indigo",
                "answer_mode": "concise",
                "tone": "study_partner",
            }
        },
    )
    assert saved.status_code == 200, saved.text
    first_prefs = saved.json()["preferences"]
    assert first_prefs["theme_mode"] == "1"
    assert first_prefs["tone"] == "study_partner"

    # A second session for the same GitHub account sees the same preferences
    # (cross-device). Logout then re-login to force a new auth_session_id.
    assert first.post("/api/v1/auth/logout").status_code == 200
    second, _ = _login(app, 1001, "prefs-user")
    seen = second.get("/api/v1/account/preferences")
    assert seen.status_code == 200
    assert seen.json()["preferences"]["accent_theme"] == "indigo"
    assert seen.json()["preferences"]["answer_mode"] == "concise"

    # Another GitHub account is isolated.
    other, _ = _login(app, 1002, "other")
    other_prefs = other.get("/api/v1/account/preferences")
    assert other_prefs.status_code == 200
    assert other_prefs.json()["preferences"] == {}
