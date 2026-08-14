PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS conversations (
    conversation_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_conversations_owner
    ON conversations (user_id, created_at);

CREATE TABLE IF NOT EXISTS workflow_runs (
    workflow_run_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    run_status TEXT NOT NULL,
    answer_status TEXT NOT NULL,
    workflow_type TEXT NOT NULL,
    request_json TEXT NOT NULL,
    result_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_workflow_runs_conversation
    ON workflow_runs (conversation_id, created_at);

CREATE TABLE IF NOT EXISTS answers (
    answer_id TEXT PRIMARY KEY,
    workflow_run_id TEXT NOT NULL UNIQUE REFERENCES workflow_runs(workflow_run_id) ON DELETE CASCADE,
    repository_answer TEXT,
    general_supplement TEXT,
    answer_status TEXT NOT NULL,
    evidence_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS citations (
    workflow_run_id TEXT NOT NULL REFERENCES workflow_runs(workflow_run_id) ON DELETE CASCADE,
    citation_id TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    PRIMARY KEY (workflow_run_id, citation_id)
);

CREATE TABLE IF NOT EXISTS external_resources (
    workflow_run_id TEXT NOT NULL REFERENCES workflow_runs(workflow_run_id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL,
    payload_json TEXT NOT NULL,
    PRIMARY KEY (workflow_run_id, ordinal)
);

CREATE TABLE IF NOT EXISTS trace_events (
    workflow_run_id TEXT NOT NULL REFERENCES workflow_runs(workflow_run_id) ON DELETE CASCADE,
    sequence INTEGER NOT NULL,
    event_id TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    PRIMARY KEY (workflow_run_id, sequence),
    UNIQUE (workflow_run_id, event_id)
);

