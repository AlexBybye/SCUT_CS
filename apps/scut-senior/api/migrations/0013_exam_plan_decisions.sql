CREATE TABLE IF NOT EXISTS exam_plan_decisions (
    decision_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('confirmed', 'edited', 'rejected')),
    plan_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_exam_plan_decisions_owner
    ON exam_plan_decisions (user_id, conversation_id, created_at);
