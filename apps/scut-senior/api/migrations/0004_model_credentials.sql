CREATE UNIQUE INDEX IF NOT EXISTS idx_auth_sessions_binding
    ON auth_sessions (auth_session_id, user_id);

CREATE TABLE IF NOT EXISTS model_credentials (
    auth_session_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    provider_id TEXT NOT NULL CHECK (
        provider_id IN ('openrouter', 'deepseek', 'siliconflow', 'zhipu')
    ),
    ciphertext BLOB NOT NULL CHECK (length(ciphertext) > 16),
    nonce BLOB NOT NULL CHECK (length(nonce) = 12),
    algorithm TEXT NOT NULL CHECK (algorithm = 'AES-256-GCM'),
    key_version INTEGER NOT NULL CHECK (key_version > 0),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    PRIMARY KEY (auth_session_id, provider_id),
    FOREIGN KEY (auth_session_id, user_id)
        REFERENCES auth_sessions(auth_session_id, user_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_model_credentials_expiry
    ON model_credentials (expires_at);

CREATE TRIGGER IF NOT EXISTS delete_credentials_when_session_revoked
AFTER UPDATE OF revoked_at ON auth_sessions
WHEN NEW.revoked_at IS NOT NULL
BEGIN
    DELETE FROM model_credentials
    WHERE auth_session_id = NEW.auth_session_id;
END;
