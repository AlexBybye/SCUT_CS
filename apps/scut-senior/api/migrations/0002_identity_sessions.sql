CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    github_user_id INTEGER NOT NULL UNIQUE CHECK (github_user_id > 0),
    github_login TEXT NOT NULL CHECK (length(github_login) > 0),
    display_name TEXT NOT NULL CHECK (length(display_name) > 0),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS oauth_states (
    oauth_state_id TEXT PRIMARY KEY,
    state_digest TEXT NOT NULL UNIQUE CHECK (length(state_digest) = 64),
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    consumed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_oauth_states_expiry
    ON oauth_states (expires_at);

CREATE TABLE IF NOT EXISTS auth_sessions (
    auth_session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    session_token_digest TEXT NOT NULL UNIQUE CHECK (length(session_token_digest) = 64),
    issued_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    revoked_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_auth_sessions_user
    ON auth_sessions (user_id, issued_at);

CREATE INDEX IF NOT EXISTS idx_auth_sessions_expiry
    ON auth_sessions (expires_at);
