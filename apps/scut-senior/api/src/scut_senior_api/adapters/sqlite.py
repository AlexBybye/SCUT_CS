from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from ..contracts import (
    ConversationDetail,
    ConversationSummary,
    WorkflowResult,
    WorkflowRunRequest,
)
from ..paths import MIGRATION_ROOT


class SQLiteMockWorkflowRepository:
    """Local iteration-0 adapter, not a production storage selection."""

    def __init__(self, database_path: Path, migration_root: Path | None = None):
        self.database_path = database_path
        self.migration_root = migration_root or MIGRATION_ROOT
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._migrate()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _migrate(self) -> None:
        with self._connect() as connection:
            for migration in sorted(self.migration_root.glob("*.sql")):
                connection.executescript(migration.read_text(encoding="utf-8"))

    def create_conversation(
        self, user_id: str, course_id: str
    ) -> ConversationSummary:
        conversation = ConversationSummary(
            conversation_id=uuid4(),
            user_id=user_id,
            course_id=course_id,
            created_at=datetime.now(UTC),
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO conversations (conversation_id, user_id, course_id, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    str(conversation.conversation_id),
                    conversation.user_id,
                    conversation.course_id,
                    conversation.created_at.isoformat(),
                ),
            )
        return conversation

    def get_conversation(
        self, user_id: str, conversation_id: UUID
    ) -> ConversationDetail | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT conversation_id, user_id, course_id, created_at
                FROM conversations
                WHERE conversation_id = ? AND user_id = ?
                """,
                (str(conversation_id), user_id),
            ).fetchone()
            if row is None:
                return None
            run_rows = connection.execute(
                """
                SELECT result_json
                FROM workflow_runs
                WHERE conversation_id = ? AND user_id = ?
                ORDER BY created_at ASC
                """,
                (str(conversation_id), user_id),
            ).fetchall()
        return ConversationDetail(
            conversation_id=UUID(row["conversation_id"]),
            user_id=row["user_id"],
            course_id=row["course_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            runs=[
                WorkflowResult.model_validate_json(run_row["result_json"])
                for run_row in run_rows
            ],
        )

    def save_run(
        self, user_id: str, request: WorkflowRunRequest, result: WorkflowResult
    ) -> None:
        now = datetime.now(UTC).isoformat()
        request_json = request.model_dump_json()
        result_json = result.model_dump_json()
        with self._connect() as connection:
            owner = connection.execute(
                """
                SELECT 1 FROM conversations
                WHERE conversation_id = ? AND user_id = ?
                """,
                (str(result.conversation_id), user_id),
            ).fetchone()
            if owner is None:
                raise PermissionError("conversation is missing or belongs to another user")
            connection.execute(
                """
                INSERT INTO workflow_runs (
                    workflow_run_id, conversation_id, user_id, run_status,
                    answer_status, workflow_type, request_json, result_json,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(workflow_run_id) DO UPDATE SET
                    run_status = excluded.run_status,
                    answer_status = excluded.answer_status,
                    result_json = excluded.result_json,
                    updated_at = excluded.updated_at
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
                ),
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
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT result_json FROM workflow_runs
                WHERE workflow_run_id = ? AND user_id = ?
                """,
                (str(run_id), user_id),
            ).fetchone()
        if row is None:
            return None
        return WorkflowResult.model_validate_json(row["result_json"])

