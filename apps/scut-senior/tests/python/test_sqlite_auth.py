from __future__ import annotations

import hashlib
import os
import shutil
import sqlite3
import stat
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

import pytest

from scut_senior_api.adapters.sqlite import (
    SQLiteMockWorkflowRepository,
    SQLiteWorkflowRepository,
)
from scut_senior_api.auth import (
    OAUTH_STATE_TTL,
    SESSION_TTL,
    GitHubUserProfile,
)
from scut_senior_api.paths import MIGRATION_ROOT


class MutableClock:
    def __init__(self, current: datetime):
        self.current = current

    def __call__(self) -> datetime:
        return self.current

    def advance(self, delta: timedelta) -> None:
        self.current += delta


def token_factory(tokens: Iterator[str]):
    return lambda: next(tokens)


def connect(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def test_auth_migrations_are_ledgered_and_sqlite_runtime_pragmas_are_enabled(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "auth.db"

    repository = SQLiteWorkflowRepository(database_path)
    SQLiteWorkflowRepository(database_path)

    with repository.connect() as connection:
        migrations = connection.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).fetchall()
        assert [row["version"] for row in migrations] == [
            "0001_iteration_zero.sql",
            "0002_identity_sessions.sql",
            "0003_conversation_history.sql",
            "0004_model_credentials.sql",
            "0005_finalize_model_credentials.sql",
            "0006_feedback.sql",
        ]
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert connection.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        assert connection.execute("PRAGMA busy_timeout").fetchone()[0] == 5000
        assert connection.execute("PRAGMA synchronous").fetchone()[0] == 1

    assert SQLiteMockWorkflowRepository is SQLiteWorkflowRepository


def test_legacy_0004_schema_is_rebuilt_without_removed_providers_or_extra_columns(
    tmp_path: Path,
) -> None:
    legacy_migrations = tmp_path / "legacy-migrations"
    legacy_migrations.mkdir()
    for filename in (
        "0001_iteration_zero.sql",
        "0002_identity_sessions.sql",
        "0003_conversation_history.sql",
    ):
        shutil.copy2(MIGRATION_ROOT / filename, legacy_migrations / filename)
    (legacy_migrations / "0004_model_credentials.sql").write_text(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_auth_sessions_binding
            ON auth_sessions (auth_session_id, user_id);
        CREATE TABLE model_credentials (
            auth_session_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            provider_id TEXT NOT NULL CHECK (
                provider_id IN ('openrouter', 'deepseek', 'retired_provider')
            ),
            ciphertext BLOB NOT NULL CHECK (length(ciphertext) > 16),
            nonce BLOB NOT NULL CHECK (length(nonce) = 12),
            algorithm TEXT NOT NULL CHECK (algorithm = 'AES-256-GCM'),
            key_version INTEGER NOT NULL CHECK (key_version > 0),
            legacy_unused TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            PRIMARY KEY (auth_session_id, provider_id),
            FOREIGN KEY (auth_session_id, user_id)
                REFERENCES auth_sessions(auth_session_id, user_id)
                ON DELETE CASCADE
        );
        CREATE INDEX idx_model_credentials_expiry
            ON model_credentials (expires_at);
        CREATE TRIGGER delete_credentials_when_session_revoked
        AFTER UPDATE OF revoked_at ON auth_sessions
        WHEN NEW.revoked_at IS NOT NULL
        BEGIN
            DELETE FROM model_credentials
            WHERE auth_session_id = NEW.auth_session_id;
        END;
        """,
        encoding="utf-8",
    )

    database_path = tmp_path / "legacy.db"
    legacy = SQLiteWorkflowRepository(database_path, migration_root=legacy_migrations)
    user_id = legacy.upsert_github_user(
        GitHubUserProfile(98_765, "legacy-user", "Legacy User")
    )
    session = legacy.issue_session(user_id)
    principal = legacy.authenticate_session(session.token)
    assert principal is not None
    now = datetime(2026, 8, 16, tzinfo=UTC).isoformat()
    with legacy.connect() as connection:
        connection.executemany(
            """
            INSERT INTO model_credentials (
                auth_session_id, user_id, provider_id, ciphertext, nonce,
                algorithm, key_version, legacy_unused,
                created_at, updated_at, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    str(principal.auth_session_id),
                    str(user_id),
                    provider_id,
                    sqlite3.Binary(bytes([ordinal]) * 17),
                    sqlite3.Binary(bytes([ordinal]) * 12),
                    "AES-256-GCM",
                    1,
                    profile,
                    now,
                    now,
                    session.expires_at.isoformat(),
                )
                for ordinal, (provider_id, profile) in enumerate(
                    (
                        ("openrouter", None),
                        ("deepseek", None),
                        ("retired_provider", "retired-value"),
                    ),
                    start=1,
                )
            ],
        )

    upgraded = SQLiteWorkflowRepository(database_path)
    with upgraded.connect() as connection:
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(model_credentials)")
        }
        table_sql = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
            ("model_credentials",),
        ).fetchone()["sql"]
        providers = [
            row["provider_id"]
            for row in connection.execute(
                "SELECT provider_id FROM model_credentials ORDER BY provider_id"
            )
        ]
        migrations = {
            row["version"]
            for row in connection.execute("SELECT version FROM schema_migrations")
        }

        assert "legacy_unused" not in columns
        assert "retired_provider" not in table_sql
        assert providers == ["deepseek", "openrouter"]
        assert "0005_finalize_model_credentials.sql" in migrations

        connection.execute(
            "UPDATE auth_sessions SET revoked_at = ? WHERE auth_session_id = ?",
            (now, str(principal.auth_session_id)),
        )
        assert connection.execute(
            "SELECT COUNT(*) FROM model_credentials"
        ).fetchone()[0] == 0


def test_oauth_state_is_digest_only_ten_minute_and_one_time(tmp_path: Path) -> None:
    clock = MutableClock(datetime(2026, 8, 15, 8, 0, tzinfo=UTC))
    states = iter(("state-" + "a" * 48, "state-" + "b" * 48))
    repository = SQLiteWorkflowRepository(
        tmp_path / "state.db",
        clock=clock,
        state_token_factory=token_factory(states),
    )

    issued = repository.issue_oauth_state()

    assert issued.expires_at == clock.current + OAUTH_STATE_TTL
    with connect(repository.database_path) as connection:
        row = connection.execute(
            "SELECT state_digest, expires_at, consumed_at FROM oauth_states"
        ).fetchone()
        assert row is not None
        assert row["state_digest"] == hashlib.sha256(issued.state.encode()).hexdigest()
        assert issued.state not in "|".join(str(value) for value in row)
        assert row["consumed_at"] is None

    assert repository.consume_oauth_state(issued.state) is True
    assert repository.consume_oauth_state(issued.state) is False

    expired = repository.issue_oauth_state()
    clock.advance(OAUTH_STATE_TTL)
    assert repository.consume_oauth_state(expired.state) is False
    assert repository.consume_oauth_state("unknown-" + "z" * 48) is False


def test_github_numeric_id_maps_to_stable_local_uuid_and_profile_can_update(
    tmp_path: Path,
) -> None:
    repository = SQLiteWorkflowRepository(tmp_path / "users.db")

    first_user_id = repository.upsert_github_user(
        GitHubUserProfile(
            github_user_id=123456,
            login="old-login",
            display_name="旧名称",
        )
    )
    updated_user_id = repository.upsert_github_user(
        GitHubUserProfile(
            github_user_id=123456,
            login="renamed-login",
            display_name="新名称",
        )
    )
    different_numeric_id = repository.upsert_github_user(
        GitHubUserProfile(
            github_user_id=654321,
            login="renamed-login",
            display_name="同名不同账号",
        )
    )

    assert isinstance(first_user_id, UUID)
    assert updated_user_id == first_user_id
    assert different_numeric_id != first_user_id
    with connect(repository.database_path) as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE github_user_id = 123456"
        ).fetchone()
        assert row is not None
        assert row["user_id"] == str(first_user_id)
        assert row["github_login"] == "renamed-login"
        assert row["display_name"] == "新名称"
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 2
        all_columns = {
            column[1]
            for table in ("users", "oauth_states", "auth_sessions")
            for column in connection.execute(f"PRAGMA table_info({table})")
        }
        assert "access_token" not in all_columns
        assert "github_access_token" not in all_columns


def test_session_is_digest_only_fixed_seven_days_and_revocable(tmp_path: Path) -> None:
    clock = MutableClock(datetime(2026, 8, 15, 9, 30, tzinfo=UTC))
    sessions = iter(("session-" + "x" * 48, "session-" + "y" * 48))
    repository = SQLiteWorkflowRepository(
        tmp_path / "sessions.db",
        clock=clock,
        session_token_factory=token_factory(sessions),
    )
    user_id = repository.upsert_github_user(
        GitHubUserProfile(987654, "octocat", "The Octocat")
    )

    issued = repository.issue_session(user_id)
    principal = repository.authenticate_session(issued.token)

    assert issued.expires_at == clock.current + SESSION_TTL
    assert principal is not None
    assert principal.user_id == user_id
    assert principal.display_name == "The Octocat"
    assert principal.is_mock is False
    assert principal.auth_session_id == issued.auth_session_id
    assert principal.github_user_id == 987654
    assert principal.github_login == "octocat"
    assert principal.expires_at == issued.expires_at

    with connect(repository.database_path) as connection:
        row = connection.execute(
            "SELECT * FROM auth_sessions WHERE auth_session_id = ?",
            (str(issued.auth_session_id),),
        ).fetchone()
        assert row is not None
        assert row["session_token_digest"] == hashlib.sha256(
            issued.token.encode()
        ).hexdigest()
        assert issued.token not in "|".join(str(value) for value in row)
        original_expiry = row["expires_at"]

    clock.advance(timedelta(days=6))
    assert repository.authenticate_session(issued.token) is not None
    with connect(repository.database_path) as connection:
        assert (
            connection.execute(
                "SELECT expires_at FROM auth_sessions WHERE auth_session_id = ?",
                (str(issued.auth_session_id),),
            ).fetchone()[0]
            == original_expiry
        )

    clock.advance(timedelta(days=1))
    assert repository.authenticate_session(issued.token) is None

    replacement = repository.issue_session(user_id)
    assert repository.revoke_session(replacement.token) is True
    assert repository.revoke_session(replacement.token) is False
    assert repository.authenticate_session(replacement.token) is None
    assert repository.authenticate_session("unknown-" + "q" * 48) is None


def test_cleanup_removes_dead_auth_records_but_preserves_users(tmp_path: Path) -> None:
    clock = MutableClock(datetime(2026, 8, 15, 10, 0, tzinfo=UTC))
    repository = SQLiteWorkflowRepository(
        tmp_path / "cleanup.db",
        clock=clock,
        state_token_factory=token_factory(iter(("state-" + "c" * 48,))),
        session_token_factory=token_factory(
            iter(("session-" + "m" * 48, "session-" + "n" * 48))
        ),
    )
    user_id = repository.upsert_github_user(
        GitHubUserProfile(111111, "cleanup-user", None)
    )
    repository.issue_oauth_state()
    expired_session = repository.issue_session(user_id)
    revoked_session = repository.issue_session(user_id)
    assert repository.revoke_session(revoked_session.token) is True
    clock.advance(SESSION_TTL)

    deleted = repository.cleanup_auth_records()

    assert deleted.oauth_states == 1
    assert deleted.auth_sessions == 2
    with connect(repository.database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM oauth_states").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM auth_sessions").fetchone()[0] == 0
        user = connection.execute(
            "SELECT user_id, display_name FROM users WHERE user_id = ?",
            (str(user_id),),
        ).fetchone()
        assert user is not None
        assert user["display_name"] == "cleanup-user"
    assert repository.authenticate_session(expired_session.token) is None


def test_auth_cleanup_runs_on_startup_and_before_new_state_or_session(
    tmp_path: Path,
) -> None:
    clock = MutableClock(datetime(2026, 8, 15, 10, 30, tzinfo=UTC))
    database_path = tmp_path / "automatic-cleanup.db"
    repository = SQLiteWorkflowRepository(
        database_path,
        clock=clock,
        state_token_factory=token_factory(
            iter(("state-" + "d" * 48, "state-" + "e" * 48))
        ),
        session_token_factory=token_factory(
            iter(("session-" + "o" * 48, "session-" + "p" * 48))
        ),
    )
    user_id = repository.upsert_github_user(
        GitHubUserProfile(121212, "automatic-cleanup-user")
    )

    consumed_state = repository.issue_oauth_state()
    assert repository.consume_oauth_state(consumed_state.state) is True
    repository.issue_oauth_state()
    with connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM oauth_states").fetchone()[0] == 1

    revoked_session = repository.issue_session(user_id)
    assert repository.revoke_session(revoked_session.token) is True
    active_session = repository.issue_session(user_id)
    with connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM auth_sessions").fetchone()[0] == 1

    clock.advance(SESSION_TTL)
    restarted = SQLiteWorkflowRepository(database_path, clock=clock)

    with connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM oauth_states").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM auth_sessions").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
    assert restarted.authenticate_session(active_session.token) is None


def test_online_backup_restores_users_and_history_but_requires_new_login(
    tmp_path: Path,
) -> None:
    clock = MutableClock(datetime(2026, 8, 15, 11, 0, tzinfo=UTC))
    token = "session-" + "r" * 48
    repository = SQLiteWorkflowRepository(
        tmp_path / "source.db",
        clock=clock,
        session_token_factory=lambda: token,
    )
    user_id = repository.upsert_github_user(
        GitHubUserProfile(222222, "backup-user", "备份用户")
    )
    issued = repository.issue_session(user_id)
    issued_state = repository.issue_oauth_state()
    conversation = repository.create_conversation(
        str(user_id), "linear_algebra", "备份中的历史"
    )
    backup_path = tmp_path / "backups" / "auth.sqlite3"
    restored_path = tmp_path / "restored" / "restored.db"

    repository.backup_to(backup_path)
    restored = SQLiteWorkflowRepository.restore_from_backup(
        backup_path,
        restored_path,
        clock=clock,
    )

    assert backup_path.is_file()
    with connect(backup_path) as connection:
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert repository.authenticate_session(issued.token) is not None
    assert restored.authenticate_session(issued.token) is None
    assert restored.consume_oauth_state(issued_state.state) is False
    with connect(restored_path) as connection:
        user = connection.execute(
            "SELECT github_user_id, github_login FROM users WHERE user_id = ?",
            (str(user_id),),
        ).fetchone()
        assert user is not None
        assert tuple(user) == (222222, "backup-user")
        assert connection.execute("SELECT COUNT(*) FROM auth_sessions").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM oauth_states").fetchone()[0] == 0
    restored_history = restored.get_conversation(str(user_id), conversation.conversation_id)
    assert restored_history is not None
    assert restored_history.title == "备份中的历史"

    replacement = restored.issue_session(user_id)
    replacement_principal = restored.authenticate_session(replacement.token)
    assert replacement_principal is not None
    assert replacement_principal.user_id == user_id


@pytest.mark.skipif(os.name != "posix", reason="POSIX mode bits are required")
def test_existing_database_and_wal_bundle_is_tightened_on_init_and_open(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "legacy-mode.db"
    legacy_connection = sqlite3.connect(database_path)
    legacy_connection.execute("PRAGMA journal_mode = WAL")
    legacy_connection.execute("CREATE TABLE legacy_marker (value TEXT)")
    legacy_connection.execute("INSERT INTO legacy_marker VALUES ('kept')")
    legacy_connection.commit()

    bundle = (
        database_path,
        Path(f"{database_path}-wal"),
        Path(f"{database_path}-shm"),
    )
    assert all(path.is_file() for path in bundle)
    for path in bundle:
        path.chmod(0o644)

    repository = SQLiteWorkflowRepository(database_path)

    assert all(stat.S_IMODE(path.stat().st_mode) == 0o600 for path in bundle)
    for path in bundle:
        path.chmod(0o644)
    with repository.connect() as connection:
        assert connection.execute("SELECT value FROM legacy_marker").fetchone()[0] == "kept"
        assert all(stat.S_IMODE(path.stat().st_mode) == 0o600 for path in bundle)
    legacy_connection.close()


@pytest.mark.skipif(os.name != "posix", reason="POSIX mode bits are required")
def test_database_and_backup_paths_reject_symlinks_without_chmod_target(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target.db"
    sqlite3.connect(target).close()
    target.chmod(0o644)
    database_link = tmp_path / "database-link.db"
    database_link.symlink_to(target)

    with pytest.raises(ValueError, match="regular file"):
        SQLiteWorkflowRepository(database_link)
    assert stat.S_IMODE(target.stat().st_mode) == 0o644

    source = SQLiteWorkflowRepository(tmp_path / "source.db")
    backup_target = tmp_path / "backup-target.db"
    source.backup_to(backup_target)
    backup_target.chmod(0o644)
    backup_link = tmp_path / "backup-link.db"
    backup_link.symlink_to(backup_target)

    with pytest.raises(ValueError, match="regular file"):
        SQLiteWorkflowRepository.restore_from_backup(
            backup_link,
            tmp_path / "must-not-exist.db",
        )
    assert stat.S_IMODE(backup_target.stat().st_mode) == 0o644


@pytest.mark.skipif(os.name != "posix", reason="POSIX mode bits are required")
def test_new_database_and_backup_files_are_private_without_chmod_existing_parents(
    tmp_path: Path,
) -> None:
    tmp_mode_before = stat.S_IMODE(tmp_path.stat().st_mode)
    private_database_parent = tmp_path / "private-database"
    private_database_path = private_database_parent / "app.db"

    repository = SQLiteWorkflowRepository(private_database_path)

    assert stat.S_IMODE(private_database_parent.stat().st_mode) == 0o700
    assert stat.S_IMODE(private_database_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(tmp_path.stat().st_mode) == tmp_mode_before

    shared_parent = tmp_path / "shared"
    shared_parent.mkdir()
    shared_parent.chmod(0o777)
    shared_mode_before = stat.S_IMODE(shared_parent.stat().st_mode)
    shared_database_path = shared_parent / "shared.db"

    SQLiteWorkflowRepository(shared_database_path)

    assert stat.S_IMODE(shared_parent.stat().st_mode) == shared_mode_before == 0o777
    assert stat.S_IMODE(shared_database_path.stat().st_mode) == 0o600

    backup_parent = tmp_path / "private-backup"
    backup_path = backup_parent / "app.sqlite3"
    repository.backup_to(backup_path)

    assert stat.S_IMODE(backup_parent.stat().st_mode) == 0o700
    assert stat.S_IMODE(backup_path.stat().st_mode) == 0o600

    backup_path.chmod(0o644)
    restored_path = shared_parent / "restored.db"
    SQLiteWorkflowRepository.restore_from_backup(backup_path, restored_path)

    assert stat.S_IMODE(shared_parent.stat().st_mode) == shared_mode_before
    assert stat.S_IMODE(backup_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(restored_path.stat().st_mode) == 0o600
