from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from scut_senior_api.auth import GitHubUserProfile, SESSION_COOKIE_NAME
from scut_senior_api.config import Settings
from scut_senior_api.main import create_app


CONFIRMATIONS = {key: True for key in (
    "course_confirmed", "source_confirmed", "public_share_rights_confirmed",
    "no_sensitive_info_confirmed", "public_pr_visibility_acknowledged",
)}


@pytest.fixture
def accounts(tmp_path):
    now = [datetime(2026, 9, 14, tzinfo=UTC)]
    app = create_app(Settings(
        app_env="test", identity_mode="github_oauth", storage_mode="sqlite", database_path=tmp_path / "content.db",
        github_client_id="test", github_client_secret="test",
        github_callback_url="https://testserver/api/v1/auth/github/callback",
        post_login_redirect_url="https://testserver/", maintainer_github_logins=("owner",),
    ), clock=lambda: now[0])
    clients = []
    for number, name in enumerate(("student", "other", "owner"), 1):
        user = app.state.repository.upsert_github_user(GitHubUserProfile(number, name))
        session = app.state.repository.issue_session(user)
        client = TestClient(app, base_url="https://testserver")
        client.cookies.set(SESSION_COOKIE_NAME, session.token, path="/")
        clients.append(client)
    return app, clients, now


def test_cross_course_environment_defaults_enabled_and_can_be_disabled(monkeypatch):
    monkeypatch.delenv("SCUT_SENIOR_CROSS_COURSE_ENABLED", raising=False)
    assert Settings.from_env().cross_course_enabled
    monkeypatch.setenv("SCUT_SENIOR_CROSS_COURSE_ENABLED", "false")
    assert not Settings.from_env().cross_course_enabled


def test_private_management_scopes_and_expiry(accounts):
    app, (alice, bob, _), now = accounts
    record = app.state.repository.save_private_knowledge(
        user_id=alice.get("/api/v1/me").json()["user_id"], course_id="linear_algebra",
        title="复习笔记", content="可对角化需要线性无关的特征向量。",
    )
    path = f"/api/v1/private-knowledge/{record.knowledge_id}"
    private_list = alice.get("/api/v1/private-knowledge")
    assert private_list.headers["cache-control"] == "private, no-store"
    assert "content" not in private_list.json()[0]
    assert bob.get("/api/v1/private-knowledge").json() == []
    for suffix in ("", "/export"):
        assert alice.get(path + suffix).status_code == 200
        assert bob.get(path + suffix).status_code == 404
    assert bob.delete(path).status_code == 404
    assert bob.post(path + "/renew").status_code == 404
    assert alice.get(path + "/export").headers["cache-control"] == "private, no-store"
    now[0] += timedelta(days=2)
    renewed = alice.post(path + "/renew")
    assert renewed.status_code == 200
    assert datetime.fromisoformat(renewed.json()["expires_at"]) == now[0] + timedelta(days=7)
    # Read/export does not renew again, nor does it change the original content.
    assert alice.get(path).json()["expires_at"] == renewed.json()["expires_at"]
    assert alice.delete(path).status_code == 204
    assert alice.get(path).status_code == 404
    assert app.state.repository.list_private_knowledge_sources(
        user_id=alice.get("/api/v1/me").json()["user_id"], course_ids=["linear_algebra"],
    ) == []


def test_expired_private_cannot_be_restored_by_renew(accounts):
    app, (alice, _, _), now = accounts
    user_id = alice.get("/api/v1/me").json()["user_id"]
    record = app.state.repository.save_private_knowledge(user_id=user_id, course_id="linear_algebra", title=None, content="旧笔记")
    now[0] += timedelta(days=7)
    assert app.state.repository.renew_private_knowledge(user_id, record.knowledge_id) is None
    assert app.state.repository.get_private_knowledge(user_id, record.knowledge_id) is None


def test_direct_contribution_email_and_owned_exports(accounts):
    app, (alice, bob, owner), _ = accounts
    payload = dict(course_id="linear_algebra", title="矩阵笔记", content="# 矩阵\n条件与反例。",
                   github_email="123+student@users.noreply.github.com", confirmations=CONFIRMATIONS)
    created = alice.post("/api/v1/contributions", json=payload)
    assert created.status_code == 201, created.text
    item = created.json()
    assert item["state"] == "submitted" and item["material_id"] is None
    path = f"/api/v1/contributions/{item['contribution_id']}"
    assert alice.get(path + "/detail").json()["content_snapshot"] == payload["content"]
    assert bob.get(path + "/detail").status_code == 404
    assert bob.get(path + "/export").status_code == 404
    assert alice.get(path + "/export").json()["github_email"] == payload["github_email"]
    exported = owner.get(f"/api/v1/maintainer/contributions/{item['contribution_id']}/export")
    assert exported.status_code == 200, exported.text
    assert exported.json()["coauthor_trailer"] == f"Co-authored-by: student <{payload['github_email']}>"
    assert alice.get("/api/v1/maintainer/contributions").status_code == 403
    for changed in ({"github_email": "bad"}, {"github_email": "x@y.com\nInjected"},
                    {"as_draft": True}, {"material_id": str(uuid4())}, {"content": "  "},
                    {"confirmations": {**CONFIRMATIONS, "source_confirmed": False}}):
        assert alice.post("/api/v1/contributions", json={**payload, **changed}).status_code == 422
    missing_email = {key: value for key, value in payload.items() if key != "github_email"}
    assert alice.post("/api/v1/contributions", json=missing_email).status_code == 422
    assert alice.post(path + "/submit", json={"confirmations": CONFIRMATIONS}).status_code in (404, 405)
    assert alice.post("/api/v1/contributions", json={**payload, "run_id": str(uuid4())}).status_code == 404


def test_personal_content_anonymous_requests_are_denied(accounts):
    app, _, _ = accounts
    client = TestClient(app, base_url="https://testserver")
    for path in ("/api/v1/private-knowledge", "/api/v1/contributions"):
        assert client.get(path).status_code == 401


def test_private_list_pagination_and_validation(accounts):
    app, (alice, _, _), _ = accounts
    user_id = alice.get("/api/v1/me").json()["user_id"]
    for index in range(4):
        app.state.repository.save_private_knowledge(user_id=user_id, course_id="linear_algebra", title=str(index), content="笔记")
    first = alice.get("/api/v1/private-knowledge?limit=2").json()
    second = alice.get("/api/v1/private-knowledge?limit=2&offset=2").json()
    assert len({item["knowledge_id"] for item in first + second}) == 4
    assert alice.get("/api/v1/private-knowledge?limit=101").status_code == 422
    assert alice.get("/api/v1/private-knowledge?course_id=probability_theory").json() == []
