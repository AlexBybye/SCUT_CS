-- PLAN-3 C-2: cross-conversation, user-bound private knowledge.
-- These entries are never public corpus candidates and expire physically after 7 days.
CREATE TABLE IF NOT EXISTS private_knowledge_items (
    knowledge_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    content_sha256 TEXT NOT NULL,
    char_count INTEGER NOT NULL,
    visibility TEXT NOT NULL CHECK (visibility = 'private'),
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_private_knowledge_retrieval
    ON private_knowledge_items (user_id, course_id, expires_at);
CREATE INDEX IF NOT EXISTS idx_private_knowledge_expiry
    ON private_knowledge_items (expires_at);
