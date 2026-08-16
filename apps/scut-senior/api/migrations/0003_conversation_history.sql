ALTER TABLE conversations ADD COLUMN title TEXT NOT NULL DEFAULT '新会话';
ALTER TABLE conversations ADD COLUMN updated_at TEXT NOT NULL DEFAULT '';
ALTER TABLE conversations ADD COLUMN expires_at TEXT NOT NULL DEFAULT '';

UPDATE conversations
SET updated_at = created_at,
    expires_at = strftime(
        '%Y-%m-%dT%H:%M:%f+00:00',
        created_at,
        '+30 days'
    )
WHERE updated_at = '' OR expires_at = '';

CREATE INDEX IF NOT EXISTS idx_conversations_history
    ON conversations (user_id, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversations_expiry
    ON conversations (expires_at);

ALTER TABLE workflow_runs ADD COLUMN attempt_group_id TEXT;
ALTER TABLE workflow_runs ADD COLUMN regenerated_from_run_id TEXT;
ALTER TABLE workflow_runs ADD COLUMN expires_at TEXT NOT NULL DEFAULT '';

UPDATE workflow_runs
SET attempt_group_id = workflow_run_id,
    expires_at = strftime(
        '%Y-%m-%dT%H:%M:%f+00:00',
        created_at,
        '+30 days'
    )
WHERE attempt_group_id IS NULL OR expires_at = '';

CREATE INDEX IF NOT EXISTS idx_workflow_runs_attempt_group
    ON workflow_runs (attempt_group_id, created_at);

CREATE INDEX IF NOT EXISTS idx_workflow_runs_expiry
    ON workflow_runs (expires_at);
