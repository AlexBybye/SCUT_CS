-- PLAN-3 C-1 contribution metadata and private attachment payloads.
ALTER TABLE contributions ADD COLUMN github_email TEXT;
ALTER TABLE contributions ADD COLUMN workflow_type TEXT;
ALTER TABLE contributions ADD COLUMN run_id TEXT;
ALTER TABLE contributions ADD COLUMN supplementary_text TEXT;
ALTER TABLE contributions ADD COLUMN citation_metadata_json TEXT NOT NULL DEFAULT '[]';
ALTER TABLE contributions ADD COLUMN corpus_metadata_json TEXT NOT NULL DEFAULT '{}';

CREATE INDEX IF NOT EXISTS idx_contributions_run ON contributions (run_id);

CREATE TABLE IF NOT EXISTS contribution_attachments (
    attachment_id TEXT PRIMARY KEY,
    contribution_id TEXT NOT NULL REFERENCES contributions(contribution_id) ON DELETE CASCADE,
    original_filename TEXT NOT NULL,
    content_type TEXT NOT NULL,
    byte_size INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    payload BLOB NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_contribution_attachments_owner
    ON contribution_attachments (contribution_id, created_at);
CREATE INDEX IF NOT EXISTS idx_contribution_attachments_expiry
    ON contribution_attachments (expires_at);
