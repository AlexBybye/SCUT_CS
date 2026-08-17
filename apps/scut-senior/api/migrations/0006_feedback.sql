CREATE TABLE IF NOT EXISTS feedback (
    feedback_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    run_id TEXT NOT NULL REFERENCES workflow_runs(workflow_run_id) ON DELETE CASCADE,
    conversation_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    workflow_type TEXT NOT NULL,
    feedback_type TEXT NOT NULL CHECK (
        feedback_type IN ('helpful', 'not_helpful', 'knowledge_error', 'did_not_answer')
    ),
    note TEXT,
    answer_status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_feedback_owner
    ON feedback (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_feedback_workflow_type
    ON feedback (workflow_type, feedback_type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_feedback_expiry
    ON feedback (expires_at);
