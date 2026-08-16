from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlencode, urlsplit

from fastapi.testclient import TestClient

from scut_senior_api.adapters.github import GitHubIdentity
from scut_senior_api.auth import (
    SESSION_COOKIE_MAX_AGE,
    SESSION_COOKIE_NAME,
    GitHubUserProfile,
)
from scut_senior_api.config import Settings
from scut_senior_api.main import OAUTH_STATE_COOKIE_NAME, create_app


@dataclass
class MutableClock:
    current: datetime

    def __call__(self) -> datetime:
        return self.current


class FakeGitHubOAuthAdapter:
    def __init__(self) -> None:
        self.authenticate_calls: list[str] = []
        self.identity = GitHubIdentity(
            github_id=123456,
            login="scut-student",
            display_name="SCUT Student",
            avatar_url="https://avatars.githubusercontent.com/u/123456",
        )

    def build_authorization_url(self, state: str) -> str:
        return "https://github.com/login/oauth/authorize?" + urlencode(
            {
                "client_id": "test-client-id",
                "redirect_uri": "https://testserver/api/v1/auth/github/callback",
                "state": state,
            }
        )

    def authenticate(self, code: str) -> GitHubIdentity:
        self.authenticate_calls.append(code)
        return self.identity


def oauth_settings(tmp_path) -> Settings:
    return Settings(
        app_env="test",
        identity_mode="github_oauth",
        storage_mode="sqlite",
        model_mode="mock",
        database_path=tmp_path / "oauth.db",
        github_client_id="test-client-id",
        github_client_secret="test-client-secret",
        github_callback_url="https://testserver/api/v1/auth/github/callback",
        post_login_redirect_url="https://frontend.test/",
    )


def secure_client(app) -> TestClient:
    return TestClient(app, base_url="https://testserver")


def start_and_finish_login(
    client: TestClient, adapter: FakeGitHubOAuthAdapter
) -> tuple[str, str]:
    start = client.get("/api/v1/auth/github/start", follow_redirects=False)
    assert start.status_code == 302
    query = parse_qs(urlsplit(start.headers["location"]).query)
    state = query["state"][0]
    assert "scope" not in query
    assert client.cookies.get(OAUTH_STATE_COOKIE_NAME) == state

    callback = client.get(
        "/api/v1/auth/github/callback",
        params={"code": "one-time-code", "state": state},
        follow_redirects=False,
    )
    assert callback.status_code == 303
    assert callback.headers["location"] == "https://frontend.test/"
    assert adapter.authenticate_calls == ["one-time-code"]
    session_token = client.cookies.get(SESSION_COOKIE_NAME)
    assert session_token
    return state, session_token


def test_oauth_state_cookie_session_cookie_and_restart_recovery(tmp_path) -> None:
    clock = MutableClock(datetime(2026, 8, 16, 1, 0, tzinfo=UTC))
    adapter = FakeGitHubOAuthAdapter()
    settings = oauth_settings(tmp_path)
    app = create_app(
        settings,
        github_oauth_adapter=adapter,  # type: ignore[arg-type]
        clock=clock,
    )
    client = secure_client(app)

    start = client.get("/api/v1/auth/github/start", follow_redirects=False)
    state_cookie = next(
        value
        for value in start.headers.get_list("set-cookie")
        if value.startswith(f"{OAUTH_STATE_COOKIE_NAME}=")
    )
    lowered_state_cookie = state_cookie.lower()
    assert "httponly" in lowered_state_cookie
    assert "secure" in lowered_state_cookie
    assert "samesite=lax" in lowered_state_cookie
    assert "path=/" in lowered_state_cookie
    assert "domain=" not in lowered_state_cookie
    state = parse_qs(urlsplit(start.headers["location"]).query)["state"][0]

    callback = client.get(
        "/api/v1/auth/github/callback",
        params={"code": "one-time-code", "state": state},
        follow_redirects=False,
    )
    session_cookie = next(
        value
        for value in callback.headers.get_list("set-cookie")
        if value.startswith(f"{SESSION_COOKIE_NAME}=") and "Max-Age=0" not in value
    )
    lowered_session_cookie = session_cookie.lower()
    assert "httponly" in lowered_session_cookie
    assert "secure" in lowered_session_cookie
    assert "samesite=lax" in lowered_session_cookie
    assert "path=/" in lowered_session_cookie
    assert f"max-age={SESSION_COOKIE_MAX_AGE}" in lowered_session_cookie
    assert "domain=" not in lowered_session_cookie

    me = client.get("/api/v1/me")
    assert me.status_code == 200
    assert me.json() == {
        "user_id": me.json()["user_id"],
        "display_name": "SCUT Student",
        "auth_mode": "github_oauth",
        "is_mock": False,
        "github_login": "scut-student",
        "session_expires_at": "2026-08-23T01:00:00+00:00",
    }

    raw_token = client.cookies.get(SESSION_COOKIE_NAME)
    assert raw_token
    with sqlite3.connect(settings.database_path) as connection:
        stored_digest = connection.execute(
            "SELECT session_token_digest FROM auth_sessions"
        ).fetchone()[0]
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(auth_sessions)")
        }
        assert raw_token != stored_digest
        assert "access_token" not in columns
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1

    restarted = secure_client(
        create_app(
            settings,
            github_oauth_adapter=FakeGitHubOAuthAdapter(),  # type: ignore[arg-type]
            clock=clock,
        )
    )
    restarted.cookies.set(SESSION_COOKIE_NAME, raw_token, path="/")
    assert restarted.get("/api/v1/me").status_code == 200


def test_test_profile_without_injected_github_adapter_fails_closed(tmp_path) -> None:
    client = secure_client(create_app(oauth_settings(tmp_path)))
    start = client.get("/api/v1/auth/github/start", follow_redirects=False)
    state = parse_qs(urlsplit(start.headers["location"]).query)["state"][0]

    callback = client.get(
        "/api/v1/auth/github/callback",
        params={"code": "must-not-go-to-network", "state": state},
        follow_redirects=False,
    )

    assert callback.status_code == 502
    assert callback.json()["error"]["code"] == "github_oauth_unavailable"


def test_protected_routes_return_auth_required_before_payload_validation(tmp_path) -> None:
    app = create_app(
        oauth_settings(tmp_path),
        github_oauth_adapter=FakeGitHubOAuthAdapter(),  # type: ignore[arg-type]
    )
    client = secure_client(app)

    checks = [
        client.get("/api/v1/me"),
        client.post("/api/v1/auth/logout"),
        client.post("/api/v1/conversations", content=b"not-json"),
        client.get("/api/v1/conversations"),
        client.get("/api/v1/conversations/00000000-0000-0000-0000-000000000000"),
        client.patch(
            "/api/v1/conversations/00000000-0000-0000-0000-000000000000",
            content=b"not-json",
        ),
        client.delete(
            "/api/v1/conversations/00000000-0000-0000-0000-000000000000"
        ),
        client.post("/api/v1/workflow-runs", content=b"not-json"),
        client.post(
            "/api/v1/workflow-runs/00000000-0000-0000-0000-000000000000/regenerate"
        ),
        client.get("/api/v1/workflow-runs/00000000-0000-0000-0000-000000000000"),
        client.get(
            "/api/v1/workflow-runs/00000000-0000-0000-0000-000000000000/trace"
        ),
    ]

    assert all(response.status_code == 401 for response in checks)
    assert all(
        response.headers["cache-control"] == "private, no-store"
        for response in checks
    )
    assert all(
        response.json() == {
            "error": {
                "code": "auth_required",
                "detail": "请先使用 GitHub 登录。",
            }
        }
        for response in checks
    )


def test_private_cache_control_is_scoped_and_covers_two_users(tmp_path) -> None:
    app = create_app(
        oauth_settings(tmp_path),
        github_oauth_adapter=FakeGitHubOAuthAdapter(),  # type: ignore[arg-type]
    )
    repository = app.state.repository
    user_a = repository.upsert_github_user(GitHubUserProfile(2001, "cache-user-a"))
    user_b = repository.upsert_github_user(GitHubUserProfile(2002, "cache-user-b"))
    session_a = repository.issue_session(user_a)
    session_b = repository.issue_session(user_b)
    client_a = secure_client(app)
    client_b = secure_client(app)
    client_a.cookies.set(SESSION_COOKIE_NAME, session_a.token, path="/")
    client_b.cookies.set(SESSION_COOKIE_NAME, session_b.token, path="/")

    me_a = client_a.get("/api/v1/me")
    me_b = client_b.get("/api/v1/me")
    assert me_a.status_code == me_b.status_code == 200
    assert me_a.json()["user_id"] != me_b.json()["user_id"]
    assert me_a.headers["cache-control"] == "private, no-store"
    assert me_b.headers["cache-control"] == "private, no-store"

    created = client_a.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    )
    assert created.status_code == 201
    assert created.headers["cache-control"] == "private, no-store"
    conversation_id = created.json()["conversation_id"]

    owner_read = client_a.get(f"/api/v1/conversations/{conversation_id}")
    other_user_read = client_b.get(f"/api/v1/conversations/{conversation_id}")
    assert owner_read.status_code == 200
    assert other_user_read.status_code == 404
    assert owner_read.headers["cache-control"] == "private, no-store"
    assert other_user_read.headers["cache-control"] == "private, no-store"

    public_health = client_a.get("/api/v1/health")
    assert public_health.status_code == 200
    assert public_health.headers.get("cache-control") != "private, no-store"


def test_state_mismatch_and_replay_fail_before_exchange(tmp_path) -> None:
    adapter = FakeGitHubOAuthAdapter()
    client = secure_client(
        create_app(
            oauth_settings(tmp_path),
            github_oauth_adapter=adapter,  # type: ignore[arg-type]
        )
    )
    start = client.get("/api/v1/auth/github/start", follow_redirects=False)
    state = parse_qs(urlsplit(start.headers["location"]).query)["state"][0]

    mismatch = client.get(
        "/api/v1/auth/github/callback",
        params={"code": "should-not-run", "state": "x" * 43},
        follow_redirects=False,
    )
    assert mismatch.status_code == 400
    assert mismatch.json()["error"]["code"] == "oauth_state_invalid"
    assert adapter.authenticate_calls == []

    client.cookies.set(OAUTH_STATE_COOKIE_NAME, state, path="/")
    success = client.get(
        "/api/v1/auth/github/callback",
        params={"code": "valid-code", "state": state},
        follow_redirects=False,
    )
    assert success.status_code == 303

    client.cookies.set(OAUTH_STATE_COOKIE_NAME, state, path="/")
    replay = client.get(
        "/api/v1/auth/github/callback",
        params={"code": "replay-code", "state": state},
        follow_redirects=False,
    )
    assert replay.status_code == 400
    assert adapter.authenticate_calls == ["valid-code"]


def test_logout_revokes_session_and_keeps_user_mapping(tmp_path) -> None:
    adapter = FakeGitHubOAuthAdapter()
    settings = oauth_settings(tmp_path)
    client = secure_client(
        create_app(settings, github_oauth_adapter=adapter)  # type: ignore[arg-type]
    )
    _, old_token = start_and_finish_login(client, adapter)

    logout = client.post("/api/v1/auth/logout")
    assert logout.status_code == 200
    assert logout.json() == {"logged_out": True}
    assert client.get("/api/v1/me").status_code == 401

    with sqlite3.connect(settings.database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM auth_sessions WHERE revoked_at IS NOT NULL"
        ).fetchone()[0] == 1
    assert old_token not in settings.database_path.read_bytes().decode(
        "utf-8", errors="ignore"
    )


def test_resource_ownership_is_enforced_before_model_call(tmp_path) -> None:
    app = create_app(
        oauth_settings(tmp_path),
        github_oauth_adapter=FakeGitHubOAuthAdapter(),  # type: ignore[arg-type]
    )
    repository = app.state.repository
    user_a = repository.upsert_github_user(GitHubUserProfile(1001, "student-a"))
    user_b = repository.upsert_github_user(GitHubUserProfile(1002, "student-b"))
    session_a = repository.issue_session(user_a)
    session_b = repository.issue_session(user_b)
    client_a = secure_client(app)
    client_b = secure_client(app)
    client_a.cookies.set(SESSION_COOKIE_NAME, session_a.token, path="/")
    client_b.cookies.set(SESSION_COOKIE_NAME, session_b.token, path="/")

    conversation = client_a.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    )
    assert conversation.status_code == 201
    conversation_id = conversation.json()["conversation_id"]

    request = {
        "workflow_type": "knowledge_qa",
        "course_scope": "single",
        "course_id": "linear_algebra",
        "allowed_course_ids": [],
        "conversation_id": conversation_id,
        "model_source": "platform_default",
        "provider_id": "mock",
        "model_id": "deterministic-fixture-v1",
        "user_input": "请解释矩阵的秩",
        "answer_mode": "detailed",
        "tone": "teaching_assistant",
        "knowledge_scope": "course_first",
        "include_bilibili_resources": False,
        "context_refs": [],
        "attachments": [],
        "workflow_payload": {"question": "请解释矩阵的秩"},
    }
    owner_run = client_a.post("/api/v1/workflow-runs", json=request)
    assert owner_run.status_code == 201
    owner_result = owner_run.json()
    run_id = owner_result["workflow_run_id"]
    trace_by_node = {
        event["node"]: event["result"] for event in owner_result["trace"]
    }
    assert trace_by_node["identity"] == {"auth_mode": "github_oauth"}
    assert trace_by_node["fixture_retrieval"]["mode"] == "synthetic_fixture_only"
    assert trace_by_node["persistence"] == {
        "stored": True,
        "adapter": "sqlite",
    }
    assert client_b.get(f"/api/v1/workflow-runs/{run_id}").status_code == 404
    assert client_b.get(f"/api/v1/workflow-runs/{run_id}/trace").status_code == 404

    class ModelSpy:
        called = False

        def generate(self, *_args, **_kwargs):
            self.called = True
            raise AssertionError("model must not run for another user's conversation")

    spy = ModelSpy()
    app.state.service.model = spy
    forbidden_run = client_b.post("/api/v1/workflow-runs", json=request)
    assert forbidden_run.status_code == 404
    assert spy.called is False
    assert client_b.get(f"/api/v1/conversations/{conversation_id}").status_code == 404
