from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import stat
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

from ..auth import (
    MIN_TOKEN_LENGTH,
    OAUTH_STATE_TTL,
    SESSION_TTL,
    AuthCleanupCounts,
    AuthRequired,
    AuthenticatedPrincipal,
    Clock,
    GitHubUserProfile,
    IssuedOAuthState,
    IssuedSession,
    TokenFactory,
    secure_token,
    utc_now,
)
from ..agent_loop import replay_agent_events
from ..contracts import (
    ContributionRecord,
    ContributionState,
    ConversationDetail,
    ConversationSummary,
    FeedbackRecord,
    TemporaryMaterialDetail,
    TemporaryMaterialRecord,
    WorkflowAttempt,
    WorkflowResult,
    WorkflowRunRequest,
)
from ..contributions import (
    CONTRIBUTION_REVIEW_COPY_TTL_DAYS,
    TEMPORARY_MATERIAL_TTL_DAYS,
)
from ..credentials import CREDENTIAL_ALGORITHM
from ..paths import MIGRATION_ROOT
from ..ports import StoredModelCredential


HISTORY_TTL = timedelta(days=30)
PRIVATE_DIRECTORY_MODE = 0o700
PRIVATE_FILE_MODE = 0o600


@dataclass(frozen=True, slots=True)
class MaterialCleanupCounts:
    """迭代 7 清理结果：物理删除的材料数与载荷清空的贡献数。"""

    materials: int
    contributions_cleared: int


def _ensure_private_parent_directory(parent: Path) -> None:
    """Create and protect only the requested parent; never chmod an existing one."""

    try:
        parent.mkdir(mode=PRIVATE_DIRECTORY_MODE, parents=True, exist_ok=False)
    except FileExistsError:
        if not parent.is_dir():
            raise NotADirectoryError(parent)
        return
    if os.name == "posix":
        parent.chmod(PRIVATE_DIRECTORY_MODE)


def _create_private_file(path: Path) -> None:
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, PRIVATE_FILE_MODE)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise ValueError(f"private SQLite path must be a regular file: {path}")
        if os.name == "posix":
            os.fchmod(descriptor, PRIVATE_FILE_MODE)
    finally:
        os.close(descriptor)


def _protect_private_file(path: Path, *, required: bool) -> tuple[int, int] | None:
    """Tighten an existing regular file without following a symlink."""

    if os.name != "posix":
        if required and not path.is_file():
            raise FileNotFoundError(path)
        return None
    try:
        before = path.lstat()
    except FileNotFoundError:
        if required:
            raise
        return None
    if not stat.S_ISREG(before.st_mode):
        raise ValueError(f"private SQLite path must be a regular file: {path}")

    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except FileNotFoundError:
        if required:
            raise
        return None
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError(f"private SQLite path must be a regular file: {path}")
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise RuntimeError(f"private SQLite path changed while opening: {path}")
        os.fchmod(descriptor, PRIVATE_FILE_MODE)
        return opened.st_dev, opened.st_ino
    finally:
        os.close(descriptor)


def _protect_database_bundle(path: Path) -> tuple[int, int] | None:
    database_identity = _protect_private_file(path, required=True)
    _protect_private_file(Path(f"{path}-wal"), required=False)
    _protect_private_file(Path(f"{path}-shm"), required=False)
    return database_identity


def _prepare_database_path(path: Path) -> None:
    _ensure_private_parent_directory(path.parent)
    try:
        _create_private_file(path)
    except FileExistsError:
        pass
    _protect_database_bundle(path)


@dataclass(frozen=True, slots=True)
class HistoryCleanupCounts:
    workflow_runs: int
    conversations: int
    feedback: int


def _feedback_record(row: sqlite3.Row) -> FeedbackRecord:
    return FeedbackRecord(
        feedback_id=UUID(row["feedback_id"]),
        user_id=row["user_id"],
        run_id=UUID(row["run_id"]),
        conversation_id=UUID(row["conversation_id"]),
        course_id=row["course_id"],
        workflow_type=row["workflow_type"],
        feedback_type=row["feedback_type"],
        note=row["note"],
        answer_status=row["answer_status"],
        created_at=datetime.fromisoformat(row["created_at"]),
        expires_at=datetime.fromisoformat(row["expires_at"]),
    )


class SQLiteWorkflowRepository:
    """SQLite persistence for workflows, local identities, and server sessions."""

    def __init__(
        self,
        database_path: Path,
        migration_root: Path | None = None,
        *,
        clock: Clock = utc_now,
        state_token_factory: TokenFactory = secure_token,
        session_token_factory: TokenFactory = secure_token,
    ):
        self.database_path = database_path
        self.migration_root = migration_root or MIGRATION_ROOT
        self._clock = clock
        self._state_token_factory = state_token_factory
        self._session_token_factory = session_token_factory
        _prepare_database_path(self.database_path)
        self._migrate()
        self.cleanup_auth_records()
        self.cleanup_history_records()
        self.cleanup_material_records()
        _protect_database_bundle(self.database_path)

    def connect(self) -> sqlite3.Connection:
        expected_identity = _protect_database_bundle(self.database_path)
        connection = sqlite3.connect(self.database_path, timeout=5.0)
        try:
            opened_identity = _protect_database_bundle(self.database_path)
            if (
                expected_identity is not None
                and opened_identity is not None
                and opened_identity != expected_identity
            ):
                raise RuntimeError("SQLite database path changed while connecting")
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("PRAGMA busy_timeout = 5000")
            connection.execute("PRAGMA synchronous = NORMAL")
            _protect_database_bundle(self.database_path)
        except Exception:
            connection.close()
            raise
        return connection

    _connect = connect

    def _now(self) -> datetime:
        current = self._clock()
        if current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("clock must return a timezone-aware datetime")
        return current.astimezone(UTC)

    def _history_expires_at(self, now: datetime | None = None) -> datetime:
        return (now or self._now()) + HISTORY_TTL

    def _migrate(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TEXT NOT NULL
                )
                """
            )
            applied = {
                row["version"]
                for row in connection.execute("SELECT version FROM schema_migrations")
            }
            for migration in sorted(self.migration_root.glob("*.sql")):
                if migration.name in applied:
                    continue
                version = migration.name.replace("'", "''")
                applied_at = self._now().isoformat().replace("'", "''")
                script = migration.read_text(encoding="utf-8")
                try:
                    connection.executescript(
                        "BEGIN IMMEDIATE;\n"
                        f"{script}\n"
                        "INSERT OR IGNORE INTO schema_migrations (version, applied_at) "
                        f"VALUES ('{version}', '{applied_at}');\n"
                        "COMMIT;"
                    )
                except Exception:
                    connection.rollback()
                    raise

    @staticmethod
    def _digest(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    @staticmethod
    def _validate_new_token(token_factory: Callable[[], str]) -> str:
        token = token_factory()
        if not isinstance(token, str) or len(token) < MIN_TOKEN_LENGTH:
            raise ValueError("token factory must return at least 32 characters")
        return token

    @staticmethod
    def _is_token_candidate(token: str) -> bool:
        return isinstance(token, str) and len(token) >= MIN_TOKEN_LENGTH

    def issue_oauth_state(self) -> IssuedOAuthState:
        self.cleanup_auth_records()
        state = self._validate_new_token(self._state_token_factory)
        now = self._now()
        expires_at = now + OAUTH_STATE_TTL
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO oauth_states (
                    oauth_state_id, state_digest, created_at, expires_at, consumed_at
                ) VALUES (?, ?, ?, ?, NULL)
                """,
                (str(uuid4()), self._digest(state), now.isoformat(), expires_at.isoformat()),
            )
        return IssuedOAuthState(state=state, expires_at=expires_at)

    def consume_oauth_state(self, state: str) -> bool:
        if not self._is_token_candidate(state):
            return False
        now = self._now().isoformat()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE oauth_states SET consumed_at = ?
                WHERE state_digest = ? AND consumed_at IS NULL AND expires_at > ?
                """,
                (now, self._digest(state), now),
            )
        return cursor.rowcount == 1

    def upsert_github_user(self, profile: GitHubUserProfile) -> UUID:
        now = self._now().isoformat()
        candidate_id = uuid4()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO users (
                    user_id, github_user_id, github_login, display_name,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(github_user_id) DO UPDATE SET
                    github_login = excluded.github_login,
                    display_name = excluded.display_name,
                    updated_at = excluded.updated_at
                """,
                (
                    str(candidate_id),
                    profile.github_user_id,
                    profile.login,
                    profile.resolved_display_name,
                    now,
                    now,
                ),
            )
            row = connection.execute(
                "SELECT user_id FROM users WHERE github_user_id = ?",
                (profile.github_user_id,),
            ).fetchone()
        if row is None:
            raise RuntimeError("GitHub identity mapping was not persisted")
        return UUID(row["user_id"])

    def issue_session(self, user_id: UUID | str) -> IssuedSession:
        self.cleanup_auth_records()
        normalized_user_id = UUID(str(user_id))
        token = self._validate_new_token(self._session_token_factory)
        now = self._now()
        expires_at = now + SESSION_TTL
        auth_session_id = uuid4()
        with self._connect() as connection:
            owner = connection.execute(
                "SELECT 1 FROM users WHERE user_id = ?", (str(normalized_user_id),)
            ).fetchone()
            if owner is None:
                raise LookupError("local user does not exist")
            connection.execute(
                """
                INSERT INTO auth_sessions (
                    auth_session_id, user_id, session_token_digest,
                    issued_at, expires_at, revoked_at
                ) VALUES (?, ?, ?, ?, ?, NULL)
                """,
                (
                    str(auth_session_id),
                    str(normalized_user_id),
                    self._digest(token),
                    now.isoformat(),
                    expires_at.isoformat(),
                ),
            )
        return IssuedSession(token, auth_session_id, expires_at)

    def authenticate_session(self, token: str) -> AuthenticatedPrincipal | None:
        if not self._is_token_candidate(token):
            return None
        self.cleanup_auth_records()
        now = self._now().isoformat()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT s.auth_session_id, s.expires_at, u.user_id,
                       u.github_user_id, u.github_login, u.display_name
                FROM auth_sessions AS s
                JOIN users AS u ON u.user_id = s.user_id
                WHERE s.session_token_digest = ?
                  AND s.revoked_at IS NULL
                  AND s.expires_at > ?
                """,
                (self._digest(token), now),
            ).fetchone()
        if row is None:
            return None
        return AuthenticatedPrincipal(
            user_id=UUID(row["user_id"]),
            display_name=row["display_name"],
            is_mock=False,
            auth_session_id=UUID(row["auth_session_id"]),
            github_user_id=row["github_user_id"],
            github_login=row["github_login"],
            expires_at=datetime.fromisoformat(row["expires_at"]),
        )

    def revoke_session(self, token: str) -> bool:
        if not self._is_token_candidate(token):
            return False
        now = self._now().isoformat()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE auth_sessions SET revoked_at = ?
                WHERE session_token_digest = ? AND revoked_at IS NULL AND expires_at > ?
                """,
                (now, self._digest(token), now),
            )
        return cursor.rowcount == 1

    def cleanup_auth_records(self) -> AuthCleanupCounts:
        now = self._now().isoformat()
        with self._connect() as connection:
            states = connection.execute(
                "DELETE FROM oauth_states WHERE consumed_at IS NOT NULL OR expires_at <= ?",
                (now,),
            ).rowcount
            sessions = connection.execute(
                "DELETE FROM auth_sessions WHERE revoked_at IS NOT NULL OR expires_at <= ?",
                (now,),
            ).rowcount
        return AuthCleanupCounts(states, sessions)

    def cleanup_history_records(self) -> HistoryCleanupCounts:
        """Physically remove expired private history while preserving users."""

        now = self._now().isoformat()
        with self._connect() as connection:
            runs = connection.execute(
                "DELETE FROM workflow_runs WHERE expires_at <= ?",
                (now,),
            ).rowcount
            conversations = connection.execute(
                "DELETE FROM conversations WHERE expires_at <= ?",
                (now,),
            ).rowcount
            # The feedback table arrives with migration 0006; older databases
            # must keep working until that migration is applied.
            tables = {
                row["name"]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            feedback = 0
            if "feedback" in tables:
                feedback = connection.execute(
                    "DELETE FROM feedback WHERE expires_at <= ?",
                    (now,),
                ).rowcount
        return HistoryCleanupCounts(runs, conversations, feedback)

    # ------------------------------------------------------------------
    # 迭代 7（SOP §12）：临时材料与贡献待处理队列。
    # ------------------------------------------------------------------

    def cleanup_material_records(self) -> MaterialCleanupCounts:
        """迭代 7 清理：到期临时材料物理删除；到期贡献载荷实际清空。

        - 临时材料 7 天 TTL：到期整行删除，不留内容。
        - 贡献 30 天 TTL：到期后 content_snapshot 实际清空（不能只在 UI 隐藏）；
          未决状态置为 expired，终态保留状态标记但同样清除载荷。
        """

        now = self._now().isoformat()
        with self._connect() as connection:
            tables = {
                row["name"]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            if "temporary_materials" not in tables:
                return MaterialCleanupCounts(0, 0)
            materials = connection.execute(
                "DELETE FROM temporary_materials WHERE expires_at <= ?",
                (now,),
            ).rowcount
            cleared = connection.execute(
                """
                UPDATE contributions
                SET state = CASE
                        WHEN state IN ('draft', 'submitted', 'pr_open') THEN 'expired'
                        ELSE state
                    END,
                    content_snapshot = '',
                    char_count = 0,
                    updated_at = ?
                WHERE expires_at <= ? AND content_snapshot != ''
                """,
                (now, now),
            ).rowcount
        return MaterialCleanupCounts(materials, cleared)

    # ------------------------------------------------------------------
    # 迭代 7.5（SOP §12A 分组 B）：平台额度锁存的共享存储。
    # ------------------------------------------------------------------

    def reserve_platform_request(
        self, *, limit: int, window_seconds: float
    ) -> bool:
        """跨 worker 原子预留一个平台请求窗口名额。

        窗口外事件清理、计数与写入在同一条 ``BEGIN IMMEDIATE`` 事务内完成；
        多进程并发时由 SQLite 写串行化保证不重复发放。重启后窗口状态仍在。
        """

        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer")
        if not window_seconds > 0:
            raise ValueError("window_seconds must be positive")
        now = self._now()
        cutoff = (now - timedelta(seconds=window_seconds)).isoformat()
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "DELETE FROM platform_rate_events WHERE requested_at <= ?",
                (cutoff,),
            )
            row = connection.execute(
                "SELECT COUNT(*) AS active FROM platform_rate_events"
            ).fetchone()
            if int(row["active"]) >= limit:
                connection.rollback()
                return False
            connection.execute(
                "INSERT INTO platform_rate_events (requested_at) VALUES (?)",
                (now.isoformat(),),
            )
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def latch_platform_daily_exhaustion(self, *, exhausted_until: datetime) -> None:
        """登记每日额度耗尽闩锁；任何 worker 写入后其余 worker 立即可见。"""

        until = self._require_aware(exhausted_until)
        now = self._now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO platform_quota_latch (singleton, exhausted_until, updated_at)
                VALUES (1, ?, ?)
                ON CONFLICT(singleton) DO UPDATE SET
                    exhausted_until = excluded.exhausted_until,
                    updated_at = excluded.updated_at
                """,
                (until.isoformat(), now.isoformat()),
            )

    def platform_daily_exhaustion(self) -> datetime | None:
        """返回仍生效的每日额度闩锁到期时间；已过期则清除并返回 None。"""

        now = self._now()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT exhausted_until FROM platform_quota_latch WHERE singleton = 1"
            ).fetchone()
        if row is None:
            return None
        until = datetime.fromisoformat(row["exhausted_until"])
        if until <= now:
            with self._connect() as connection:
                connection.execute(
                    "DELETE FROM platform_quota_latch WHERE singleton = 1"
                )
            return None
        return until

    def cleanup_platform_quota_records(self) -> int:
        """清理过期窗口流水与过期闩锁；返回删除的事件行数。"""

        now = self._now().isoformat()
        with self._connect() as connection:
            events = connection.execute(
                "DELETE FROM platform_rate_events WHERE requested_at <= ?",
                (now,),
            ).rowcount
            connection.execute(
                "DELETE FROM platform_quota_latch WHERE exhausted_until <= ?",
                (now,),
            )
        return events

    @staticmethod
    def _require_aware(value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("quota timestamps must be timezone-aware")
        return value.astimezone(UTC)

    # ------------------------------------------------------------------
    # 迭代 7.5（SOP §12A 分组 B / §16 待确认项 3）：账号注销、历史提前删除
    # 与数据导出。
    # ------------------------------------------------------------------

    def account_is_deleted(self, github_user_id: int) -> bool:
        """注销封锁名单查询：命中即拒绝再次登录。"""

        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM deleted_accounts WHERE github_user_id = ?",
                (int(github_user_id),),
            ).fetchone()
        return row is not None

    def delete_account(self, user_id: str) -> dict[str, int]:
        """物理删除该账号的全部私有数据并封锁其 GitHub 身份。

        注销语义（§16 待确认项 3 决议）：会话立即失效、历史／反馈／临时材料/
        贡献副本/模型凭据密文全部物理删除、users 行删除；deleted_accounts 仅
        保留 github_user_id 用于登录封锁。导出请先于注销调用。
        """

        normalized_user_id = str(UUID(str(user_id)))
        now = self._now().isoformat()
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT github_user_id FROM users WHERE user_id = ?",
                (normalized_user_id,),
            ).fetchone()
            if row is None:
                connection.rollback()
                raise LookupError("account not found")
            github_user_id = int(row["github_user_id"])
            counts = {
                "temporary_materials": connection.execute(
                    "DELETE FROM temporary_materials WHERE user_id = ?",
                    (normalized_user_id,),
                ).rowcount,
                "contributions": connection.execute(
                    "DELETE FROM contributions WHERE user_id = ?",
                    (normalized_user_id,),
                ).rowcount,
                "model_credentials": connection.execute(
                    "DELETE FROM model_credentials WHERE user_id = ?",
                    (normalized_user_id,),
                ).rowcount,
                "feedback": connection.execute(
                    "DELETE FROM feedback WHERE user_id = ?",
                    (normalized_user_id,),
                ).rowcount,
                "workflow_runs": connection.execute(
                    "DELETE FROM workflow_runs WHERE user_id = ?",
                    (normalized_user_id,),
                ).rowcount,
                "conversations": connection.execute(
                    "DELETE FROM conversations WHERE user_id = ?",
                    (normalized_user_id,),
                ).rowcount,
                "auth_sessions": connection.execute(
                    "DELETE FROM auth_sessions WHERE user_id = ?",
                    (normalized_user_id,),
                ).rowcount,
            }
            connection.execute(
                "DELETE FROM users WHERE user_id = ?", (normalized_user_id,)
            )
            connection.execute(
                """
                INSERT INTO deleted_accounts (github_user_id, deleted_at)
                VALUES (?, ?)
                ON CONFLICT(github_user_id) DO UPDATE SET deleted_at = excluded.deleted_at
                """,
                (github_user_id, now),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return counts

    def export_account_data(self, user_id: str) -> dict[str, object]:
        """导出本人数据：历史、贡献与临时材料元数据。

        不含他人资源（所有查询按 user_id 硬绑定），不含任何模型凭据——
        既无密文也无明文，凭据表根本不进入导出路径。
        """

        normalized_user_id = str(UUID(str(user_id)))
        with self._connect() as connection:
            profile = connection.execute(
                """
                SELECT github_login, display_name, created_at
                FROM users WHERE user_id = ?
                """,
                (normalized_user_id,),
            ).fetchone()
            if profile is None:
                raise LookupError("account not found")
            conversations = [
                {
                    "conversation_id": row["conversation_id"],
                    "course_id": row["course_id"],
                    "title": row["title"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "expires_at": row["expires_at"],
                }
                for row in connection.execute(
                    """
                    SELECT conversation_id, course_id, title,
                           created_at, updated_at, expires_at
                    FROM conversations WHERE user_id = ?
                    ORDER BY created_at ASC
                    """,
                    (normalized_user_id,),
                )
            ]
            runs: list[dict[str, object]] = []
            for row in connection.execute(
                """
                SELECT workflow_run_id, conversation_id, workflow_type,
                       run_status, answer_status, request_json, result_json,
                       created_at, expires_at
                FROM workflow_runs WHERE user_id = ?
                ORDER BY created_at ASC
                """,
                (normalized_user_id,),
            ):
                try:
                    result_payload = json.loads(row["result_json"])
                except json.JSONDecodeError:
                    result_payload = {"unparseable": True}
                runs.append(
                    {
                        "workflow_run_id": row["workflow_run_id"],
                        "conversation_id": row["conversation_id"],
                        "workflow_type": row["workflow_type"],
                        "run_status": row["run_status"],
                        "answer_status": row["answer_status"],
                        "request": json.loads(row["request_json"]),
                        "result": result_payload,
                        "created_at": row["created_at"],
                        "expires_at": row["expires_at"],
                    }
                )
            tables = {
                table["name"]
                for table in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            contributions: list[dict[str, object]] = []
            temporary_materials: list[dict[str, object]] = []
            if "contributions" in tables:
                contributions = [
                    {
                        "contribution_id": row["contribution_id"],
                        "course_id": row["course_id"],
                        "proposed_source_id": row["proposed_source_id"],
                        "title": row["title"],
                        "state": row["state"],
                        "pr_url": row["pr_url"],
                        "char_count": row["char_count"],
                        "content_snapshot": row["content_snapshot"],
                        "created_at": row["created_at"],
                        "expires_at": row["expires_at"],
                    }
                    for row in connection.execute(
                        """
                        SELECT contribution_id, course_id, proposed_source_id,
                               title, state, pr_url, char_count,
                               content_snapshot, created_at, expires_at
                        FROM contributions WHERE user_id = ?
                        ORDER BY created_at ASC
                        """,
                        (normalized_user_id,),
                    )
                ]
            if "temporary_materials" in tables:
                # 临时材料只导出元数据：7 天 TTL 的短命数据不鼓励长期留存，
                # 内容本身可随时在应用内重新粘贴生成。
                temporary_materials = [
                    {
                        "material_id": row["material_id"],
                        "conversation_id": row["conversation_id"],
                        "course_id": row["course_id"],
                        "title": row["title"],
                        "char_count": row["char_count"],
                        "created_at": row["created_at"],
                        "expires_at": row["expires_at"],
                    }
                    for row in connection.execute(
                        """
                        SELECT material_id, conversation_id, course_id, title,
                               char_count, created_at, expires_at
                        FROM temporary_materials WHERE user_id = ?
                        ORDER BY created_at ASC
                        """,
                        (normalized_user_id,),
                    )
                ]
        return {
            "github_login": profile["github_login"],
            "display_name": profile["display_name"],
            "account_created_at": profile["created_at"],
            "conversations": conversations,
            "contributions": contributions,
            "temporary_materials": temporary_materials,
            "runs": runs,
        }


    @staticmethod
    def _temporary_material_record(
        row: sqlite3.Row, *, include_content: bool
    ) -> TemporaryMaterialDetail | TemporaryMaterialRecord:
        base: dict[str, object] = {
            "material_id": UUID(row["material_id"]),
            "conversation_id": UUID(row["conversation_id"]),
            "course_id": row["course_id"],
            "title": row["title"],
            "char_count": int(row["char_count"]),
            "content_sha256": row["content_sha256"],
            "created_at": datetime.fromisoformat(row["created_at"]),
            "expires_at": datetime.fromisoformat(row["expires_at"]),
        }
        if include_content:
            return TemporaryMaterialDetail(
                **base, content=row["content"]  # type: ignore[arg-type]
            )
        return TemporaryMaterialRecord(**base)  # type: ignore[arg-type]

    def save_temporary_material(
        self,
        *,
        user_id: str,
        conversation_id: UUID,
        course_id: str,
        title: str | None,
        content: str,
    ) -> TemporaryMaterialDetail:
        """保存会话内临时材料；TTL 固定 7 天，到期由清理任务物理删除。"""

        now = self._now()
        material_id = uuid4()
        created_at = now.isoformat()
        expires_at = (now + timedelta(days=TEMPORARY_MATERIAL_TTL_DAYS)).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO temporary_materials (
                    material_id, user_id, conversation_id, course_id, title,
                    content, content_sha256, char_count, created_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(material_id),
                    user_id,
                    str(conversation_id),
                    course_id,
                    title,
                    content,
                    hashlib.sha256(content.encode("utf-8")).hexdigest(),
                    len(content),
                    created_at,
                    expires_at,
                ),
            )
        record = self.get_temporary_material(
            user_id, material_id, include_content=True
        )
        assert record is not None  # 刚插入的行必然存在。
        return record

    def get_temporary_material(
        self,
        user_id: str,
        material_id: UUID,
        *,
        include_content: bool = False,
    ) -> TemporaryMaterialDetail | TemporaryMaterialRecord | None:
        """所有权硬绑定：user_id 不匹配时等同于不存在。"""

        now = self._now().isoformat()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM temporary_materials
                WHERE material_id = ? AND user_id = ? AND expires_at > ?
                """,
                (str(material_id), user_id, now),
            ).fetchone()
        if row is None:
            return None
        return self._temporary_material_record(
            row, include_content=include_content
        )

    def list_temporary_materials(
        self, user_id: str
    ) -> list[TemporaryMaterialRecord]:
        now = self._now().isoformat()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM temporary_materials
                WHERE user_id = ? AND expires_at > ?
                ORDER BY created_at DESC
                """,
                (user_id, now),
            ).fetchall()
        return [
            self._temporary_material_record(row, include_content=False)
            for row in rows
        ]

    def delete_temporary_material(self, user_id: str, material_id: UUID) -> bool:
        with self._connect() as connection:
            deleted = connection.execute(
                """
                DELETE FROM temporary_materials
                WHERE material_id = ? AND user_id = ?
                """,
                (str(material_id), user_id),
            ).rowcount
        return deleted > 0

    @staticmethod
    def _contribution_record(row: sqlite3.Row) -> ContributionRecord:
        pr_url = row["pr_url"]
        keys = row.keys()
        proposed_repo_path = (
            row["proposed_repo_path"] if "proposed_repo_path" in keys else ""
        )
        return ContributionRecord(
            contribution_id=UUID(row["contribution_id"]),
            user_id=row["user_id"],
            material_id=(
                UUID(row["material_id"]) if row["material_id"] is not None else None
            ),
            course_id=row["course_id"],
            proposed_source_id=row["proposed_source_id"],
            proposed_repo_path=proposed_repo_path,
            title=row["title"],
            state=ContributionState(row["state"]),
            pr_url=pr_url,
            maintainer_note=row["maintainer_note"],
            char_count=int(row["char_count"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]),
        )

    def create_contribution(
        self,
        *,
        user_id: str,
        material_id: UUID | None,
        course_id: str,
        proposed_source_id: str,
        title: str,
        content_snapshot: str,
        state: ContributionState,
        proposed_repo_path: str = "",
    ) -> ContributionRecord:
        """创建贡献记录。

        draft 继承临时材料 7 天期限（随材料一起过期）；
        submitted/pr_open 及终态使用“必要待审副本”30 天上限。
        """

        now = self._now()
        contribution_id = uuid4()
        ttl_days = (
            TEMPORARY_MATERIAL_TTL_DAYS
            if state == ContributionState.DRAFT
            else CONTRIBUTION_REVIEW_COPY_TTL_DAYS
        )
        created_at = now.isoformat()
        updated_at = created_at
        expires_at = (now + timedelta(days=ttl_days)).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO contributions (
                    contribution_id, user_id, material_id, course_id,
                    proposed_source_id, proposed_repo_path, title,
                    content_snapshot, state,
                    pr_url, maintainer_note, char_count,
                    created_at, updated_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?, ?)
                """,
                (
                    str(contribution_id),
                    user_id,
                    str(material_id) if material_id is not None else None,
                    course_id,
                    proposed_source_id,
                    proposed_repo_path,
                    title,
                    content_snapshot,
                    state.value,
                    len(content_snapshot),
                    created_at,
                    updated_at,
                    expires_at,
                ),
            )
        record = self.get_contribution(user_id, contribution_id)
        assert record is not None  # 刚插入的行必然存在。
        return record

    def get_contribution(
        self, user_id: str, contribution_id: UUID
    ) -> ContributionRecord | None:
        """用户只能读取自己的贡献状态；他人记录等同不存在。"""

        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM contributions WHERE contribution_id = ? AND user_id = ?",
                (str(contribution_id), user_id),
            ).fetchone()
        return None if row is None else self._contribution_record(row)

    def list_contributions(self, user_id: str) -> list[ContributionRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM contributions WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [self._contribution_record(row) for row in rows]

    def get_contribution_with_payload(
        self, contribution_id: UUID
    ) -> tuple[ContributionRecord, str] | None:
        """维护者导出专用：按 ID 取记录与待审副本全文（不做用户过滤）。"""

        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM contributions WHERE contribution_id = ?",
                (str(contribution_id),),
            ).fetchone()
        if row is None:
            return None
        return self._contribution_record(row), row["content_snapshot"]

    def list_maintainer_queue(
        self, state: ContributionState | None = None
    ) -> list[ContributionRecord]:
        """维护者待处理队列：只返回元数据视图需要的记录行。"""

        with self._connect() as connection:
            if state is None:
                rows = connection.execute(
                    """
                    SELECT * FROM contributions
                    WHERE state IN ('submitted', 'pr_open')
                    ORDER BY created_at ASC
                    """
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM contributions WHERE state = ? ORDER BY created_at ASC",
                    (state.value,),
                ).fetchall()
        return [self._contribution_record(row) for row in rows]

    def transition_contribution(
        self,
        contribution_id: UUID,
        *,
        from_states: frozenset[ContributionState],
        target_state: ContributionState,
        pr_url: str | None,
        note: str | None,
    ) -> ContributionRecord | None:
        """原子状态迁移：仅当当前状态仍在允许集合内时生效。"""

        now = self._now().isoformat()
        from_states = sorted(from_states)
        placeholders = ", ".join("?" for _ in from_states)
        with self._connect() as connection:
            updated = connection.execute(
                f"""
                UPDATE contributions
                SET state = ?, pr_url = ?, maintainer_note = ?, updated_at = ?
                WHERE contribution_id = ? AND state IN ({placeholders})
                """,
                (
                    target_state.value,
                    pr_url,
                    note,
                    now,
                    str(contribution_id),
                    *[state.value for state in from_states],
                ),
            ).rowcount
            if updated == 0:
                return None
            row = connection.execute(
                "SELECT * FROM contributions WHERE contribution_id = ?",
                (str(contribution_id),),
            ).fetchone()
        assert row is not None
        return self._contribution_record(row)

    def is_course_plugin_loaded(self, course_id: str) -> bool:
        """A course plugin is loaded unless an explicit unload row exists.

        Absence of a row means loaded (the registry default), so pre-0007
        databases and never-touched courses behave identically.
        """
        with self._connect() as connection:
            row = connection.execute(
                "SELECT loaded FROM course_plugin_states WHERE course_id = ?",
                (course_id,),
            ).fetchone()
        return row is None or bool(row["loaded"])

    def set_course_plugin_loaded(
        self,
        course_id: str,
        loaded: bool,
        updated_by_user_id: str | None = None,
    ) -> None:
        now = self._now().isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO course_plugin_states (course_id, loaded, updated_at, updated_by_user_id)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(course_id) DO UPDATE SET
                    loaded = excluded.loaded,
                    updated_at = excluded.updated_at,
                    updated_by_user_id = excluded.updated_by_user_id
                """,
                (course_id, 1 if loaded else 0, now, updated_by_user_id),
            )

    def session_is_active(self, user_id: UUID, auth_session_id: UUID) -> bool:
        now = self._now().isoformat()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT 1 FROM auth_sessions
                WHERE auth_session_id = ? AND user_id = ?
                  AND revoked_at IS NULL AND expires_at > ?
                """,
                (str(auth_session_id), str(user_id), now),
            ).fetchone()
        return row is not None

    @staticmethod
    def _stored_model_credential(row: sqlite3.Row) -> StoredModelCredential:
        return StoredModelCredential(
            user_id=UUID(row["user_id"]),
            auth_session_id=UUID(row["auth_session_id"]),
            provider_id=row["provider_id"],
            ciphertext=bytes(row["ciphertext"]),
            nonce=bytes(row["nonce"]),
            algorithm=row["algorithm"],
            key_version=row["key_version"],
            expires_at=datetime.fromisoformat(row["expires_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def list_model_credentials(
        self, user_id: UUID, auth_session_id: UUID
    ) -> list[StoredModelCredential]:
        self.cleanup_auth_records()
        now = self._now().isoformat()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT c.user_id, c.auth_session_id, c.provider_id,
                       c.ciphertext, c.nonce, c.algorithm, c.key_version,
                       c.expires_at, c.updated_at
                FROM model_credentials AS c
                JOIN auth_sessions AS s
                  ON s.auth_session_id = c.auth_session_id
                 AND s.user_id = c.user_id
                WHERE c.user_id = ? AND c.auth_session_id = ?
                  AND c.expires_at > ?
                  AND s.revoked_at IS NULL AND s.expires_at > ?
                ORDER BY c.provider_id
                """,
                (str(user_id), str(auth_session_id), now, now),
            ).fetchall()
        return [self._stored_model_credential(row) for row in rows]

    def get_model_credential(
        self, user_id: UUID, auth_session_id: UUID, provider_id: str
    ) -> StoredModelCredential | None:
        self.cleanup_auth_records()
        now = self._now().isoformat()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT c.user_id, c.auth_session_id, c.provider_id,
                       c.ciphertext, c.nonce, c.algorithm, c.key_version,
                       c.expires_at, c.updated_at
                FROM model_credentials AS c
                JOIN auth_sessions AS s
                  ON s.auth_session_id = c.auth_session_id
                 AND s.user_id = c.user_id
                WHERE c.user_id = ? AND c.auth_session_id = ?
                  AND c.provider_id = ? AND c.expires_at > ?
                  AND s.revoked_at IS NULL AND s.expires_at > ?
                """,
                (
                    str(user_id),
                    str(auth_session_id),
                    provider_id,
                    now,
                    now,
                ),
            ).fetchone()
        return self._stored_model_credential(row) if row is not None else None

    def upsert_model_credential(
        self,
        *,
        user_id: UUID,
        auth_session_id: UUID,
        provider_id: str,
        ciphertext: bytes,
        nonce: bytes,
        algorithm: str,
        key_version: int,
    ) -> StoredModelCredential:
        if algorithm != CREDENTIAL_ALGORITHM:
            raise ValueError("unsupported credential algorithm")
        if len(nonce) != 12 or len(ciphertext) <= 16:
            raise ValueError("invalid credential envelope")
        if isinstance(key_version, bool) or key_version < 1:
            raise ValueError("invalid credential key version")
        now_value = self._now()
        now = now_value.isoformat()
        with self._connect() as connection:
            # Serialize the active-session check with credential replacement.
            # If replacement wins, a later revoke trigger deletes the row; if
            # revoke wins, this check fails and no late ciphertext is written.
            connection.execute("BEGIN IMMEDIATE")
            session = connection.execute(
                """
                SELECT expires_at FROM auth_sessions
                WHERE auth_session_id = ? AND user_id = ?
                  AND revoked_at IS NULL AND expires_at > ?
                """,
                (str(auth_session_id), str(user_id), now),
            ).fetchone()
            if session is None:
                raise AuthRequired()
            expires_at = datetime.fromisoformat(session["expires_at"])
            if expires_at <= now_value:
                raise AuthRequired()
            connection.execute(
                """
                INSERT INTO model_credentials (
                    auth_session_id, user_id, provider_id, ciphertext, nonce,
                    algorithm, key_version,
                    created_at, updated_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(auth_session_id, provider_id) DO UPDATE SET
                    ciphertext = excluded.ciphertext,
                    nonce = excluded.nonce,
                    algorithm = excluded.algorithm,
                    key_version = excluded.key_version,
                    updated_at = excluded.updated_at,
                    expires_at = excluded.expires_at
                """,
                (
                    str(auth_session_id),
                    str(user_id),
                    provider_id,
                    sqlite3.Binary(ciphertext),
                    sqlite3.Binary(nonce),
                    algorithm,
                    key_version,
                    now,
                    now,
                    expires_at.isoformat(),
                ),
            )
            row = connection.execute(
                """
                SELECT user_id, auth_session_id, provider_id, ciphertext,
                       nonce, algorithm, key_version, expires_at, updated_at
                FROM model_credentials
                WHERE auth_session_id = ? AND provider_id = ?
                """,
                (str(auth_session_id), provider_id),
            ).fetchone()
        if row is None:
            raise RuntimeError("model credential was not persisted")
        return self._stored_model_credential(row)

    def delete_model_credential(
        self, user_id: UUID, auth_session_id: UUID, provider_id: str
    ) -> bool:
        now = self._now().isoformat()
        with self._connect() as connection:
            active = connection.execute(
                """
                SELECT 1 FROM auth_sessions
                WHERE auth_session_id = ? AND user_id = ?
                  AND revoked_at IS NULL AND expires_at > ?
                """,
                (str(auth_session_id), str(user_id), now),
            ).fetchone()
            if active is None:
                raise AuthRequired()
            cursor = connection.execute(
                """
                DELETE FROM model_credentials
                WHERE auth_session_id = ? AND user_id = ? AND provider_id = ?
                """,
                (str(auth_session_id), str(user_id), provider_id),
            )
        return cursor.rowcount == 1

    def backup_to(self, destination_path: Path) -> None:
        if destination_path.resolve() == self.database_path.resolve():
            raise ValueError("backup destination must differ from the live database")
        if destination_path.exists():
            raise FileExistsError(destination_path)
        _ensure_private_parent_directory(destination_path.parent)
        _create_private_file(destination_path)
        try:
            source = self._connect()
            destination = sqlite3.connect(destination_path)
            try:
                source.backup(destination)
            finally:
                destination.close()
                source.close()
            _protect_private_file(destination_path, required=True)
        except Exception:
            destination_path.unlink(missing_ok=True)
            raise

    @classmethod
    def restore_from_backup(
        cls,
        backup_path: Path,
        database_path: Path,
        migration_root: Path | None = None,
        *,
        clock: Clock = utc_now,
        state_token_factory: TokenFactory = secure_token,
        session_token_factory: TokenFactory = secure_token,
    ) -> SQLiteWorkflowRepository:
        if not backup_path.is_file():
            raise FileNotFoundError(backup_path)
        _protect_private_file(backup_path, required=True)
        if database_path.exists():
            raise FileExistsError(database_path)
        _ensure_private_parent_directory(database_path.parent)
        _create_private_file(database_path)
        source = sqlite3.connect(backup_path)
        try:
            if source.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise sqlite3.DatabaseError("backup integrity check failed")
            destination = sqlite3.connect(database_path)
            try:
                source.backup(destination)
            finally:
                destination.close()
            _protect_private_file(database_path, required=True)
        except Exception:
            database_path.unlink(missing_ok=True)
            raise
        finally:
            source.close()
        restored = cls(
            database_path,
            migration_root,
            clock=clock,
            state_token_factory=state_token_factory,
            session_token_factory=session_token_factory,
        )
        restored._invalidate_authentication_after_restore()
        return restored

    def _invalidate_authentication_after_restore(self) -> None:
        """Never revive pre-backup browser sessions or OAuth correlations."""

        with self._connect() as connection:
            connection.execute("DELETE FROM auth_sessions")
            connection.execute("DELETE FROM oauth_states")

    def create_conversation(
        self, user_id: str, course_id: str, title: str
    ) -> ConversationSummary:
        normalized_title = title.strip()
        if not normalized_title or len(normalized_title) > 100:
            raise ValueError("conversation title must contain 1 to 100 characters")
        now = self._now()
        conversation = ConversationSummary(
            conversation_id=uuid4(),
            user_id=user_id,
            course_id=course_id,
            title=normalized_title,
            created_at=now,
            updated_at=now,
            expires_at=self._history_expires_at(now),
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO conversations (
                    conversation_id, user_id, course_id, title,
                    created_at, updated_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(conversation.conversation_id),
                    conversation.user_id,
                    conversation.course_id,
                    conversation.title,
                    conversation.created_at.isoformat(),
                    conversation.updated_at.isoformat(),
                    conversation.expires_at.isoformat(),
                ),
            )
        return conversation

    @staticmethod
    def _conversation_summary(row: sqlite3.Row) -> ConversationSummary:
        return ConversationSummary(
            conversation_id=UUID(row["conversation_id"]),
            user_id=row["user_id"],
            course_id=row["course_id"],
            title=row["title"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]),
        )

    @staticmethod
    def _workflow_attempt(row: sqlite3.Row) -> WorkflowAttempt:
        result = WorkflowResult.model_validate_json(row["result_json"])
        return WorkflowAttempt(
            workflow_run_id=UUID(row["workflow_run_id"]),
            attempt_group_id=UUID(row["attempt_group_id"]),
            regenerated_from_run_id=(
                UUID(row["regenerated_from_run_id"])
                if row["regenerated_from_run_id"]
                else None
            ),
            request=WorkflowRunRequest.model_validate_json(row["request_json"]),
            result=result,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]),
        )

    def list_conversations(self, user_id: str) -> list[ConversationSummary]:
        self.cleanup_history_records()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT conversation_id, user_id, course_id, title,
                       created_at, updated_at, expires_at
                FROM conversations
                WHERE user_id = ?
                ORDER BY updated_at DESC, conversation_id DESC
                """,
                (user_id,),
            ).fetchall()
        return [self._conversation_summary(row) for row in rows]

    def save_feedback(self, user_id: str, record: FeedbackRecord) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO feedback (
                    feedback_id, user_id, run_id, conversation_id, course_id,
                    workflow_type, feedback_type, note, answer_status,
                    created_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(record.feedback_id),
                    user_id,
                    str(record.run_id),
                    str(record.conversation_id),
                    record.course_id,
                    record.workflow_type.value,
                    record.feedback_type.value,
                    record.note,
                    record.answer_status.value,
                    record.created_at.isoformat(),
                    record.expires_at.isoformat(),
                ),
            )

    def list_feedback(self, user_id: str) -> list[FeedbackRecord]:
        self.cleanup_history_records()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT feedback_id, user_id, run_id, conversation_id, course_id,
                       workflow_type, feedback_type, note, answer_status,
                       created_at, expires_at
                FROM feedback
                WHERE user_id = ?
                ORDER BY created_at DESC, feedback_id DESC
                """,
                (user_id,),
            ).fetchall()
        return [_feedback_record(row) for row in rows]

    def get_conversation(
        self, user_id: str, conversation_id: UUID
    ) -> ConversationDetail | None:
        self.cleanup_history_records()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT conversation_id, user_id, course_id, title,
                       created_at, updated_at, expires_at
                FROM conversations
                WHERE conversation_id = ? AND user_id = ?
                """,
                (str(conversation_id), user_id),
            ).fetchone()
            if row is None:
                return None
            run_rows = connection.execute(
                """
                SELECT workflow_run_id, attempt_group_id,
                       regenerated_from_run_id, request_json, result_json,
                       created_at, updated_at, expires_at
                FROM workflow_runs
                WHERE conversation_id = ? AND user_id = ?
                  AND run_status NOT IN ('created', 'running')
                ORDER BY created_at DESC, workflow_run_id DESC
                """,
                (str(conversation_id), user_id),
            ).fetchall()
        summary = self._conversation_summary(row)
        return ConversationDetail(
            **summary.model_dump(),
            runs=[self._workflow_attempt(run_row) for run_row in run_rows],
        )

    def rename_conversation(
        self, user_id: str, conversation_id: UUID, title: str
    ) -> ConversationSummary | None:
        self.cleanup_history_records()
        normalized_title = title.strip()
        if not normalized_title or len(normalized_title) > 100:
            raise ValueError("conversation title must contain 1 to 100 characters")
        now = self._now()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE conversations
                SET title = ?, updated_at = ?, expires_at = ?
                WHERE conversation_id = ? AND user_id = ?
                """,
                (
                    normalized_title,
                    now.isoformat(),
                    self._history_expires_at(now).isoformat(),
                    str(conversation_id),
                    user_id,
                ),
            )
            if cursor.rowcount != 1:
                return None
            row = connection.execute(
                """
                SELECT conversation_id, user_id, course_id, title,
                       created_at, updated_at, expires_at
                FROM conversations
                WHERE conversation_id = ? AND user_id = ?
                """,
                (str(conversation_id), user_id),
            ).fetchone()
        if row is None:
            return None
        return self._conversation_summary(row)

    def delete_conversation(self, user_id: str, conversation_id: UUID) -> bool:
        self.cleanup_history_records()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM conversations
                WHERE conversation_id = ? AND user_id = ?
                """,
                (str(conversation_id), user_id),
            )
        return cursor.rowcount == 1

    def save_run(
        self,
        user_id: str,
        request: WorkflowRunRequest,
        result: WorkflowResult,
        *,
        attempt_group_id: UUID | None = None,
        regenerated_from_run_id: UUID | None = None,
        auth_session_id: UUID | None = None,
    ) -> None:
        now_value = self._now()
        now = now_value.isoformat()
        expires_at = self._history_expires_at(now_value).isoformat()
        resolved_attempt_group_id = attempt_group_id or result.workflow_run_id
        if regenerated_from_run_id is None:
            if resolved_attempt_group_id != result.workflow_run_id:
                raise ValueError("an initial run must start its own attempt group")
        elif regenerated_from_run_id == result.workflow_run_id:
            raise ValueError("an attempt cannot regenerate itself")
        request_json = request.model_dump_json()
        result_json = result.model_dump_json()
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            if auth_session_id is not None:
                active_session = connection.execute(
                    """
                    SELECT 1 FROM auth_sessions
                    WHERE auth_session_id = ? AND user_id = ?
                      AND revoked_at IS NULL AND expires_at > ?
                    """,
                    (str(auth_session_id), user_id, now),
                ).fetchone()
                if active_session is None:
                    raise AuthRequired()
            owner = connection.execute(
                """
                SELECT 1 FROM conversations
                WHERE conversation_id = ? AND user_id = ?
                """,
                (str(result.conversation_id), user_id),
            ).fetchone()
            if owner is None:
                raise PermissionError("conversation is missing or belongs to another user")
            if regenerated_from_run_id is not None:
                parent = connection.execute(
                    """
                    SELECT attempt_group_id, conversation_id
                    FROM workflow_runs
                    WHERE workflow_run_id = ? AND user_id = ?
                    """,
                    (str(regenerated_from_run_id), user_id),
                ).fetchone()
                if (
                    parent is None
                    or parent["conversation_id"] != str(result.conversation_id)
                    or parent["attempt_group_id"] != str(resolved_attempt_group_id)
                ):
                    raise PermissionError(
                        "regenerated attempt parent is missing or belongs to another history"
                    )
            run_cursor = connection.execute(
                """
                INSERT INTO workflow_runs (
                    workflow_run_id, conversation_id, user_id, run_status,
                    answer_status, workflow_type, request_json, result_json,
                    created_at, updated_at, attempt_group_id,
                    regenerated_from_run_id, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(workflow_run_id) DO UPDATE SET
                    run_status = excluded.run_status,
                    answer_status = excluded.answer_status,
                    result_json = excluded.result_json,
                    updated_at = excluded.updated_at,
                    expires_at = excluded.expires_at
                WHERE workflow_runs.run_status IN ('created', 'running')
                """,
                (
                    str(result.workflow_run_id),
                    str(result.conversation_id),
                    user_id,
                    result.run_status.value,
                    result.answer_status.value,
                    result.workflow_type.value,
                    request_json,
                    result_json,
                    now,
                    now,
                    str(resolved_attempt_group_id),
                    (
                        str(regenerated_from_run_id)
                        if regenerated_from_run_id is not None
                        else None
                    ),
                    expires_at,
                ),
            )
            if run_cursor.rowcount != 1:
                raise ValueError("workflow run is already terminal")
            connection.execute(
                """
                UPDATE conversations
                SET updated_at = ?, expires_at = ?
                WHERE conversation_id = ? AND user_id = ?
                """,
                (now, expires_at, str(result.conversation_id), user_id),
            )
            connection.execute(
                """
                INSERT INTO answers (
                    answer_id, workflow_run_id, repository_answer,
                    general_supplement, answer_status, evidence_status
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(answer_id) DO UPDATE SET
                    repository_answer = excluded.repository_answer,
                    general_supplement = excluded.general_supplement,
                    answer_status = excluded.answer_status,
                    evidence_status = excluded.evidence_status
                """,
                (
                    str(result.answer_id),
                    str(result.workflow_run_id),
                    result.repository_answer,
                    result.general_supplement,
                    result.answer_status.value,
                    result.evidence_status.value,
                ),
            )
            connection.execute(
                "DELETE FROM citations WHERE workflow_run_id = ?",
                (str(result.workflow_run_id),),
            )
            connection.executemany(
                """
                INSERT INTO citations (workflow_run_id, citation_id, payload_json)
                VALUES (?, ?, ?)
                """,
                [
                    (
                        str(result.workflow_run_id),
                        citation.citation_id,
                        citation.model_dump_json(),
                    )
                    for citation in result.citations
                ],
            )
            connection.execute(
                "DELETE FROM external_resources WHERE workflow_run_id = ?",
                (str(result.workflow_run_id),),
            )
            connection.executemany(
                """
                INSERT INTO external_resources (workflow_run_id, ordinal, payload_json)
                VALUES (?, ?, ?)
                """,
                [
                    (
                        str(result.workflow_run_id),
                        index,
                        resource.model_dump_json(),
                    )
                    for index, resource in enumerate(result.external_resources)
                ],
            )
            connection.execute(
                "DELETE FROM trace_events WHERE workflow_run_id = ?",
                (str(result.workflow_run_id),),
            )
            connection.executemany(
                """
                INSERT INTO trace_events (
                    workflow_run_id, sequence, event_id, payload_json
                ) VALUES (?, ?, ?, ?)
                """,
                [
                    (
                        str(result.workflow_run_id),
                        event.sequence,
                        event.event_id,
                        event.model_dump_json(),
                    )
                    for event in result.trace
                ],
            )

    def get_run(self, user_id: str, run_id: UUID) -> WorkflowResult | None:
        attempt = self.get_attempt(user_id, run_id)
        return attempt.result if attempt is not None else None

    def discard_nonterminal_run(self, user_id: str, run_id: UUID) -> bool:
        """Remove an abandoned pre-terminal run without touching completed history."""

        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM workflow_runs
                WHERE workflow_run_id = ? AND user_id = ?
                  AND run_status IN ('created', 'running')
                """,
                (str(run_id), user_id),
            )
        return cursor.rowcount == 1

    def append_agent_event(
        self,
        run_id: UUID,
        event: dict[str, object],
        state: dict[str, object],
    ) -> int:
        """Append one reducer event and its derived snapshot atomically."""
        if not isinstance(event, dict) or not isinstance(state, dict):
            raise TypeError("agent event and state must be objects")
        payload = json.dumps(event, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        state_payload = json.dumps(state, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        now = self._now().isoformat()
        normalized_run_id = str(run_id)
        with self._connect() as connection:
            owner = connection.execute(
                "SELECT 1 FROM workflow_runs WHERE workflow_run_id = ?",
                (normalized_run_id,),
            ).fetchone()
            if owner is None:
                raise LookupError("workflow run does not exist")
            row = connection.execute(
                "SELECT COALESCE(MAX(sequence), -1) + 1 AS next_sequence "
                "FROM agent_events WHERE workflow_run_id = ?",
                (normalized_run_id,),
            ).fetchone()
            sequence = int(row["next_sequence"])
            existing = connection.execute(
                "SELECT payload_json FROM agent_events "
                "WHERE workflow_run_id = ? ORDER BY sequence ASC",
                (normalized_run_id,),
            ).fetchall()
            replayed = replay_agent_events(
                [json.loads(item["payload_json"]) for item in existing] + [event]
            )
            if replayed.to_dict() != state:
                raise ValueError("agent snapshot does not match event replay")
            connection.execute(
                "INSERT INTO agent_events "
                "(workflow_run_id, sequence, event_id, payload_json, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (normalized_run_id, sequence, str(uuid4()), payload, now),
            )
            connection.execute(
                "INSERT INTO agent_state_snapshots "
                "(workflow_run_id, state_json, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(workflow_run_id) DO UPDATE SET "
                "state_json = excluded.state_json, updated_at = excluded.updated_at",
                (normalized_run_id, state_payload, now),
            )
        return sequence

    def list_agent_events(self, run_id: UUID) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload_json FROM agent_events "
                "WHERE workflow_run_id = ? ORDER BY sequence ASC",
                (str(run_id),),
            ).fetchall()
        return [json.loads(row["payload_json"]) for row in rows]

    def record_exam_plan_decision(
        self, user_id: str, conversation_id: UUID, decision: str, plan: dict[str, object]
    ) -> None:
        if decision not in {"confirmed", "edited", "rejected"}:
            raise ValueError("invalid exam plan decision")
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO exam_plan_decisions "
                "(decision_id, conversation_id, user_id, decision, plan_json, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (str(uuid4()), str(conversation_id), user_id, decision,
                 json.dumps(plan, ensure_ascii=False, separators=(",", ":")), self._now().isoformat()),
            )

    def get_agent_snapshot(self, run_id: UUID) -> dict[str, object] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT state_json FROM agent_state_snapshots WHERE workflow_run_id = ?",
                (str(run_id),),
            ).fetchone()
        return json.loads(row["state_json"]) if row is not None else None

    def get_attempt(self, user_id: str, run_id: UUID) -> WorkflowAttempt | None:
        self.cleanup_history_records()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT workflow_run_id, attempt_group_id,
                       regenerated_from_run_id, request_json, result_json,
                       created_at, updated_at, expires_at
                FROM workflow_runs
                WHERE workflow_run_id = ? AND user_id = ?
                """,
                (str(run_id), user_id),
            ).fetchone()
        if row is None:
            return None
        return self._workflow_attempt(row)


# Compatibility for iteration-0 callers while the runtime adopts the formal name.
SQLiteMockWorkflowRepository = SQLiteWorkflowRepository
