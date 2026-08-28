CREATE TABLE IF NOT EXISTS agent_events (
    workflow_run_id TEXT NOT NULL REFERENCES workflow_runs(workflow_run_id) ON DELETE CASCADE,
    sequence INTEGER NOT NULL CHECK (sequence >= 0),
    event_id TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (workflow_run_id, sequence),
    UNIQUE (workflow_run_id, event_id)
);

CREATE TABLE IF NOT EXISTS agent_state_snapshots (
    workflow_run_id TEXT PRIMARY KEY REFERENCES workflow_runs(workflow_run_id) ON DELETE CASCADE,
    state_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
