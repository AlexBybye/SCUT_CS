from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from scut_senior_api.adapters.sqlite import HISTORY_TTL
from scut_senior_api.auth import GitHubUserProfile, SESSION_COOKIE_NAME
from scut_senior_api.config import Settings
from scut_senior_api.main import create_app
from scut_senior_api.paths import MIGRATION_ROOT


class MutableClock:
    def __init__(self, current: datetime):
        self.current = current

    def __call__(self) -> datetime:
        return self.current

    def advance(self, delta: timedelta) -> None:
        self.current += delta


def workflow_request(conversation_id: str) -> dict[str, object]:
    return {
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


def oauth_settings(database_path: Path) -> Settings:
    return Settings(
        app_env="test",
        identity_mode="github_oauth",
        storage_mode="sqlite",
        database_path=database_path,
        github_client_id="test-client-id",
        github_client_secret="test-client-secret",
        github_callback_url="https://testserver/api/v1/auth/github/callback",
        post_login_redirect_url="https://testserver/",
    )


def authenticated_client(app, github_id: int, login: str) -> TestClient:
    repository = app.state.repository
    user_id = repository.upsert_github_user(GitHubUserProfile(github_id, login))
    session = repository.issue_session(user_id)
    client = TestClient(app, base_url="https://testserver")
    client.cookies.set(SESSION_COOKIE_NAME, session.token, path="/")
    return client


def table_count(database_path: Path, table: str) -> int:
    with sqlite3.connect(database_path) as connection:
        return connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_history_migration_backfills_existing_conversations_and_runs(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "upgrade.db"
    created_at = "2026-08-15T07:00:00+00:00"
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
            """
        )
        for filename in (
            "0001_iteration_zero.sql",
            "0002_identity_sessions.sql",
        ):
            connection.executescript(
                (MIGRATION_ROOT / filename).read_text(encoding="utf-8")
            )
            connection.execute(
                "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                (filename, created_at),
            )
        connection.execute(
            """
            INSERT INTO conversations (
                conversation_id, user_id, course_id, created_at
            ) VALUES ('00000000-0000-0000-0000-000000000001', 'legacy-user',
                      'linear_algebra', ?)
            """,
            (created_at,),
        )
        connection.execute(
            """
            INSERT INTO workflow_runs (
                workflow_run_id, conversation_id, user_id, run_status,
                answer_status, workflow_type, request_json, result_json,
                created_at, updated_at
            ) VALUES (
                '00000000-0000-0000-0000-000000000002',
                '00000000-0000-0000-0000-000000000001',
                'legacy-user', 'completed', 'answered', 'knowledge_qa',
                '{}', '{}', ?, ?
            )
            """,
            (created_at, created_at),
        )

    create_app(
        Settings(app_env="test", database_path=database_path),
        clock=MutableClock(datetime(2026, 8, 16, 7, 0, tzinfo=UTC)),
    )

    with sqlite3.connect(database_path) as connection:
        conversation = connection.execute(
            "SELECT title, updated_at, expires_at FROM conversations"
        ).fetchone()
        run = connection.execute(
            """
            SELECT attempt_group_id, regenerated_from_run_id, expires_at
            FROM workflow_runs
            """
        ).fetchone()
    assert conversation is not None
    assert conversation[0] == "新会话"
    assert datetime.fromisoformat(conversation[1]) == datetime.fromisoformat(created_at)
    assert (
        datetime.fromisoformat(conversation[2]) - datetime.fromisoformat(created_at)
        == HISTORY_TTL
    )
    assert run is not None
    assert run[0] == "00000000-0000-0000-0000-000000000002"
    assert run[1] is None
    assert datetime.fromisoformat(run[2]) - datetime.fromisoformat(created_at) == HISTORY_TTL


def test_history_list_rename_and_restart_restore_request_and_result(
    tmp_path: Path,
) -> None:
    clock = MutableClock(datetime(2026, 8, 16, 8, 0, tzinfo=UTC))
    settings = Settings(
        app_env="test",
        database_path=tmp_path / "history-restart.db",
    )
    client = TestClient(create_app(settings, clock=clock))

    created = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    )
    assert created.status_code == 201
    conversation = created.json()
    assert conversation["title"] == "线性代数"
    assert conversation["created_at"] == "2026-08-16T08:00:00Z"
    assert conversation["updated_at"] == conversation["created_at"]
    assert conversation["expires_at"] == "2026-09-15T08:00:00Z"

    run = client.post(
        "/api/v1/workflow-runs",
        json=workflow_request(conversation["conversation_id"]),
    )
    assert run.status_code == 201, run.text
    result = run.json()

    renamed = client.patch(
        f"/api/v1/conversations/{conversation['conversation_id']}",
        json={"title": "  矩阵秩复习  "},
    )
    assert renamed.status_code == 200
    assert renamed.json()["title"] == "矩阵秩复习"

    restarted = TestClient(create_app(settings, clock=clock))
    history = restarted.get("/api/v1/conversations")
    assert history.status_code == 200
    assert [item["conversation_id"] for item in history.json()] == [
        conversation["conversation_id"]
    ]
    assert history.json()[0]["title"] == "矩阵秩复习"

    detail = restarted.get(
        f"/api/v1/conversations/{conversation['conversation_id']}"
    )
    assert detail.status_code == 200
    attempts = detail.json()["runs"]
    assert len(attempts) == 1
    assert attempts[0]["workflow_run_id"] == result["workflow_run_id"]
    assert attempts[0]["attempt_group_id"] == result["workflow_run_id"]
    assert attempts[0]["regenerated_from_run_id"] is None
    assert attempts[0]["request"] == workflow_request(
        conversation["conversation_id"]
    )
    assert attempts[0]["result"] == result


def test_same_github_identity_recovers_history_after_logout_and_new_session(
    tmp_path: Path,
) -> None:
    settings = oauth_settings(tmp_path / "relogin-history.db")
    app = create_app(settings)
    repository = app.state.repository
    profile = GitHubUserProfile(998877, "student-first")
    first_user_id = repository.upsert_github_user(profile)
    first_session = repository.issue_session(first_user_id)
    first = TestClient(app, base_url="https://testserver")
    first.cookies.set(SESSION_COOKIE_NAME, first_session.token, path="/")
    conversation = first.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    run = first.post(
        "/api/v1/workflow-runs",
        json=workflow_request(conversation["conversation_id"]),
    )
    assert run.status_code == 201
    assert first.post("/api/v1/auth/logout").status_code == 200

    second_user_id = repository.upsert_github_user(
        GitHubUserProfile(998877, "student-renamed")
    )
    assert second_user_id == first_user_id
    second_session = repository.issue_session(second_user_id)
    second = TestClient(app, base_url="https://testserver")
    second.cookies.set(SESSION_COOKIE_NAME, second_session.token, path="/")

    restored = second.get(
        f"/api/v1/conversations/{conversation['conversation_id']}"
    )
    assert restored.status_code == 200
    assert [attempt["workflow_run_id"] for attempt in restored.json()["runs"]] == [
        run.json()["workflow_run_id"]
    ]


def test_regenerate_creates_linked_attempt_and_preserves_old_request_and_result(
    tmp_path: Path,
) -> None:
    clock = MutableClock(datetime(2026, 8, 16, 9, 0, tzinfo=UTC))
    settings = Settings(app_env="test", database_path=tmp_path / "attempts.db")
    client = TestClient(create_app(settings, clock=clock))
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    request = workflow_request(conversation["conversation_id"])
    first_response = client.post("/api/v1/workflow-runs", json=request)
    assert first_response.status_code == 201
    first = first_response.json()

    clock.advance(timedelta(seconds=1))
    regenerated_response = client.post(
        f"/api/v1/workflow-runs/{first['workflow_run_id']}/regenerate"
    )
    assert regenerated_response.status_code == 201, regenerated_response.text
    regenerated = regenerated_response.json()
    second = regenerated["result"]

    assert regenerated["workflow_run_id"] == second["workflow_run_id"]
    assert second["workflow_run_id"] != first["workflow_run_id"]
    assert regenerated["attempt_group_id"] == first["workflow_run_id"]
    assert regenerated["regenerated_from_run_id"] == first["workflow_run_id"]
    assert regenerated["request"] == request
    assert client.get(
        f"/api/v1/workflow-runs/{first['workflow_run_id']}"
    ).json() == first

    detail = client.get(
        f"/api/v1/conversations/{conversation['conversation_id']}"
    ).json()
    attempts_by_id = {item["workflow_run_id"]: item for item in detail["runs"]}
    assert set(attempts_by_id) == {
        first["workflow_run_id"],
        second["workflow_run_id"],
    }
    assert attempts_by_id[first["workflow_run_id"]]["result"] == first
    assert attempts_by_id[first["workflow_run_id"]][
        "regenerated_from_run_id"
    ] is None
    assert attempts_by_id[second["workflow_run_id"]]["request"] == request

    with sqlite3.connect(settings.database_path) as connection:
        request_rows = connection.execute(
            "SELECT request_json FROM workflow_runs ORDER BY created_at"
        ).fetchall()
    assert len(request_rows) == 2
    assert request_rows[0][0] == request_rows[1][0]

    restarted = TestClient(create_app(settings, clock=clock))
    restored = restarted.get(
        f"/api/v1/conversations/{conversation['conversation_id']}"
    )
    assert restored.status_code == 200
    assert len(restored.json()["runs"]) == 2


def test_history_mutations_and_regeneration_are_owner_scoped(tmp_path: Path) -> None:
    clock = MutableClock(datetime(2026, 8, 16, 10, 0, tzinfo=UTC))
    settings = oauth_settings(tmp_path / "ownership.db")
    app = create_app(settings, clock=clock)
    owner = authenticated_client(app, 10001, "history-owner")
    other = authenticated_client(app, 10002, "history-other")

    conversation = owner.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    result = owner.post(
        "/api/v1/workflow-runs",
        json=workflow_request(conversation["conversation_id"]),
    ).json()

    assert other.get("/api/v1/conversations").json() == []
    assert other.patch(
        f"/api/v1/conversations/{conversation['conversation_id']}",
        json={"title": "越权改名"},
    ).status_code == 404
    assert other.delete(
        f"/api/v1/conversations/{conversation['conversation_id']}"
    ).status_code == 404
    assert other.post(
        f"/api/v1/workflow-runs/{result['workflow_run_id']}/regenerate"
    ).status_code == 404

    owner_history = owner.get("/api/v1/conversations")
    assert owner_history.status_code == 200
    assert owner_history.json()[0]["conversation_id"] == conversation[
        "conversation_id"
    ]
    assert owner.get(
        f"/api/v1/workflow-runs/{result['workflow_run_id']}"
    ).status_code == 200


def test_delete_conversation_physically_cascades_all_run_payloads(
    tmp_path: Path,
) -> None:
    settings = Settings(app_env="test", database_path=tmp_path / "delete.db")
    client = TestClient(create_app(settings))
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    request = workflow_request(conversation["conversation_id"])
    request["include_bilibili_resources"] = True
    run = client.post(
        "/api/v1/workflow-runs",
        json=request,
    )
    assert run.status_code == 201
    for table in (
        "workflow_runs",
        "answers",
        "citations",
        "external_resources",
        "trace_events",
    ):
        assert table_count(settings.database_path, table) > 0

    deleted = client.delete(
        f"/api/v1/conversations/{conversation['conversation_id']}"
    )
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(
        f"/api/v1/conversations/{conversation['conversation_id']}"
    ).status_code == 404
    assert client.get("/api/v1/conversations").json() == []
    for table in (
        "conversations",
        "workflow_runs",
        "answers",
        "citations",
        "external_resources",
        "trace_events",
    ):
        assert table_count(settings.database_path, table) == 0


def test_history_access_cleans_at_thirty_day_boundary_and_preserves_users(
    tmp_path: Path,
) -> None:
    clock = MutableClock(datetime(2026, 8, 16, 11, 0, tzinfo=UTC))
    settings = Settings(app_env="test", database_path=tmp_path / "ttl-access.db")
    app = create_app(settings, clock=clock)
    repository = app.state.repository
    repository.upsert_github_user(GitHubUserProfile(20001, "retained-user"))
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    client.post(
        "/api/v1/workflow-runs",
        json=workflow_request(conversation["conversation_id"]),
    )

    clock.advance(HISTORY_TTL - timedelta(microseconds=1))
    assert len(client.get("/api/v1/conversations").json()) == 1

    clock.advance(timedelta(microseconds=1))
    assert client.get("/api/v1/conversations").json() == []
    assert table_count(settings.database_path, "conversations") == 0
    assert table_count(settings.database_path, "workflow_runs") == 0
    assert table_count(settings.database_path, "answers") == 0
    assert table_count(settings.database_path, "users") == 1


def test_expired_run_payloads_are_removed_while_recent_conversation_survives(
    tmp_path: Path,
) -> None:
    clock = MutableClock(datetime(2026, 8, 16, 11, 30, tzinfo=UTC))
    settings = Settings(app_env="test", database_path=tmp_path / "run-ttl.db")
    client = TestClient(create_app(settings, clock=clock))
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    request = workflow_request(conversation["conversation_id"])
    request["include_bilibili_resources"] = True
    assert client.post("/api/v1/workflow-runs", json=request).status_code == 201

    clock.advance(HISTORY_TTL - timedelta(days=1))
    renamed = client.patch(
        f"/api/v1/conversations/{conversation['conversation_id']}",
        json={"title": "保留会话，清理旧尝试"},
    )
    assert renamed.status_code == 200

    clock.advance(timedelta(days=1))
    history = client.get("/api/v1/conversations")
    assert history.status_code == 200
    assert len(history.json()) == 1
    detail = client.get(
        f"/api/v1/conversations/{conversation['conversation_id']}"
    )
    assert detail.status_code == 200
    assert detail.json()["runs"] == []
    assert table_count(settings.database_path, "conversations") == 1
    for table in (
        "workflow_runs",
        "answers",
        "citations",
        "external_resources",
        "trace_events",
    ):
        assert table_count(settings.database_path, table) == 0


def test_startup_cleanup_removes_expired_history_but_not_github_user(
    tmp_path: Path,
) -> None:
    clock = MutableClock(datetime(2026, 8, 16, 12, 0, tzinfo=UTC))
    settings = Settings(app_env="test", database_path=tmp_path / "ttl-startup.db")
    first_app = create_app(settings, clock=clock)
    first_app.state.repository.upsert_github_user(
        GitHubUserProfile(20002, "startup-retained-user")
    )
    first_client = TestClient(first_app)
    conversation = first_client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    first_client.post(
        "/api/v1/workflow-runs",
        json=workflow_request(conversation["conversation_id"]),
    )
    assert table_count(settings.database_path, "workflow_runs") == 1

    clock.advance(HISTORY_TTL)
    create_app(settings, clock=clock)

    assert table_count(settings.database_path, "conversations") == 0
    assert table_count(settings.database_path, "workflow_runs") == 0
    assert table_count(settings.database_path, "trace_events") == 0
    assert table_count(settings.database_path, "users") == 1
