"""迭代 7.5（SOP §12A 分组 B / §16 待确认项 3）测试：账号注销与数据导出。

必验场景：注销后的用户无法再登录；导出包经扫描不含 Key 明文、密文或
他人资源。历史提前删除沿用既有会话/会话内运行删除路径，并在注销时整体
物理清除。
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit
from uuid import uuid4

from fastapi.testclient import TestClient

from scut_senior_api.adapters.github import GitHubIdentity
from scut_senior_api.auth import SESSION_COOKIE_NAME, secure_token
from scut_senior_api.config import Settings
from scut_senior_api.main import OAUTH_STATE_COOKIE_NAME, create_app

CREDENTIAL_SECRET = "byok-plaintext-key-do-not-leak"


@dataclass
class MutableClock:
    current: datetime

    def __call__(self) -> datetime:
        return self.current


class FakeGitHubOAuthAdapter:
    def __init__(self) -> None:
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
        return self.identity


def oauth_settings(tmp_path: Path) -> Settings:
    return Settings(
        app_env="test",
        identity_mode="github_oauth",
        storage_mode="sqlite",
        model_mode="mock",
        database_path=tmp_path / "account.db",
        github_client_id="test-client-id",
        github_client_secret="test-client-secret",
        github_callback_url="https://testserver/api/v1/auth/github/callback",
        post_login_redirect_url="https://testserver/",
    )


def make_oauth_app(tmp_path: Path):
    adapter = FakeGitHubOAuthAdapter()
    app = create_app(
        oauth_settings(tmp_path),
        github_oauth_adapter=adapter,  # type: ignore[arg-type]
    )
    client = TestClient(app, base_url="https://testserver")
    return app, client, adapter


def login(client: TestClient) -> None:
    start = client.get("/api/v1/auth/github/start", follow_redirects=False)
    assert start.status_code == 302
    state = parse_qs(urlsplit(start.headers["location"]).query)["state"][0]
    callback = client.get(
        "/api/v1/auth/github/callback",
        params={"code": "one-time-code", "state": state},
        follow_redirects=False,
    )
    assert callback.status_code == 303


def seed_account_data(app, client: TestClient, *, with_credential: bool) -> None:
    """为已登录用户种入会话、运行、临时材料、贡献副本与（可选）凭据密文。"""

    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    run_response = client.post(
        "/api/v1/workflow-runs",
        json={
            "workflow_type": "knowledge_qa",
            "course_scope": "single",
            "course_id": "linear_algebra",
            "allowed_course_ids": [],
            "conversation_id": conversation["conversation_id"],
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
        },
    )
    assert run_response.status_code == 201, run_response.text
    material_response = client.post(
        "/api/v1/temporary-materials",
        json={
            "conversation_id": conversation["conversation_id"],
            "course_id": "linear_algebra",
            "title": "导出测试材料",
            "content": "仅本人可见的材料内容",
        },
    )
    assert material_response.status_code == 201, material_response.text

    repository = app.state.repository
    # 直接查库拿 user_id（登录流程已建立映射）。
    with sqlite3.connect(app.state.settings.database_path) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            "SELECT user_id FROM users WHERE github_user_id = 123456"
        ).fetchone()
    alice_user_id = row["user_id"]

    # 贡献待审副本：直接按迁移 schema 插入一行 submitted 记录。
    now = datetime.now(UTC)
    expires = (now + timedelta(days=30)).isoformat()
    with sqlite3.connect(app.state.settings.database_path) as connection:
        connection.execute(
            """
            INSERT INTO contributions (
                contribution_id, user_id, material_id, course_id,
                proposed_source_id, title, content_snapshot, state,
                pr_url, char_count, created_at, updated_at, expires_at
            ) VALUES (?, ?, NULL, 'linear_algebra', 'linear_algebra-contribution-test0001',
                      '测试贡献', '本人贡献正文', 'submitted', NULL, 6, ?, ?, ?)
            """,
            (str(uuid4()), alice_user_id, now.isoformat(), now.isoformat(), expires),
        )

    if with_credential:
        from uuid import UUID

        session = repository.issue_session(UUID(alice_user_id))
        repository.upsert_model_credential(
            user_id=UUID(alice_user_id),
            provider_id="openrouter",
            ciphertext=b"0123456789abcdef0123456789abcdef",  # 模拟密文
            nonce=b"0123456789ab",
            algorithm="AES-256-GCM",
            key_version=1,
        )


def test_export_contains_own_data_and_never_credentials(tmp_path: Path) -> None:
    app, client, _ = make_oauth_app(tmp_path)
    login(client)
    seed_account_data(app, client, with_credential=True)

    response = client.get("/api/v1/account/export")
    assert response.status_code == 200
    assert "attachment" in response.headers["content-disposition"]
    payload = response.json()
    assert payload["schema_version"] == "scut-senior-account-export-v1"
    assert payload["github_login"] == "scut-student"
    assert len(payload["conversations"]) == 1
    assert len(payload["runs"]) == 1
    assert payload["runs"][0]["result"]["run_status"] == "completed"
    assert len(payload["temporary_materials"]) == 1
    # 临时材料只导出元数据，不携带内容。
    assert "content" not in payload["temporary_materials"][0]
    assert len(payload["contributions"]) == 1
    assert payload["contributions"][0]["content_snapshot"] == "本人贡献正文"

    text = response.text
    assert CREDENTIAL_SECRET not in text
    assert "ciphertext" not in text
    assert "AES-256-GCM" not in text


def test_delete_account_wipes_data_blocks_relogin(tmp_path: Path) -> None:
    app, client, adapter = make_oauth_app(tmp_path)
    login(client)
    seed_account_data(app, client, with_credential=True)

    database_path = app.state.settings.database_path
    with sqlite3.connect(database_path) as connection:
        before = {
            table: connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            for table in (
                "users",
                "conversations",
                "workflow_runs",
                "feedback",
                "temporary_materials",
                "contributions",
                "model_credentials",
                "auth_sessions",
            )
        }
    assert before["conversations"] >= 1
    assert before["workflow_runs"] >= 1
    assert before["contributions"] >= 1
    assert before["temporary_materials"] >= 1
    assert before["model_credentials"] >= 1

    old_cookie = client.cookies.get(SESSION_COOKIE_NAME)
    response = client.delete("/api/v1/account")
    assert response.status_code == 200
    summary = response.json()
    assert summary["conversations"] >= 1
    assert summary["workflow_runs"] >= 1
    assert summary["auth_sessions"] >= 1
    assert summary["login_blocked"] is True

    with sqlite3.connect(database_path) as connection:
        after = {
            table: connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            for table in (
                "users",
                "conversations",
                "workflow_runs",
                "feedback",
                "temporary_materials",
                "contributions",
                "model_credentials",
                "auth_sessions",
                "deleted_accounts",
            )
        }
    assert after["users"] == 0
    assert after["conversations"] == 0
    assert after["workflow_runs"] == 0
    assert after["feedback"] == 0
    assert after["temporary_materials"] == 0
    assert after["contributions"] == 0
    assert after["model_credentials"] == 0
    assert after["auth_sessions"] == 0
    assert after["deleted_accounts"] == 1

    # 注销后旧会话立即失效。
    client.cookies.set(SESSION_COOKIE_NAME, old_cookie, path="/")
    me = client.get("/api/v1/me")
    assert me.status_code == 401

    # 注销后无法再次登录：完整走一遍 OAuth start→callback 被拒。
    fresh_client = TestClient(app, base_url="https://testserver")
    start = fresh_client.get("/api/v1/auth/github/start", follow_redirects=False)
    state = parse_qs(urlsplit(start.headers["location"]).query)["state"][0]
    retry = fresh_client.get(
        "/api/v1/auth/github/callback",
        params={"code": "another-code", "state": state},
        follow_redirects=False,
    )
    assert retry.status_code == 400
    assert retry.json()["error"]["code"] == "account_deleted"

    # 注销后导出：旧会话已在认证层被拒（会话随账号一起物理删除）。
    gone = client.get("/api/v1/account/export")
    assert gone.status_code == 401


def test_mock_identity_is_rejected_for_lifecycle_endpoints(tmp_path: Path) -> None:
    settings = Settings(app_env="test", database_path=tmp_path / "mock.db")
    app = create_app(settings)
    client = TestClient(app, base_url="https://testserver")
    denied = client.delete("/api/v1/account")
    assert denied.status_code == 401
    export_denied = client.get("/api/v1/account/export")
    assert export_denied.status_code == 401
