-- BYOK 跨设备：凭据作用域从“登录会话”改为“用户（GitHub 账号）”。
-- 同一账号在任何设备登录（新 auth_session_id）都能解密同一把 BYOK。
--
-- 安全说明：AES-256-GCM 的 AAD 由绑定 user_id+auth_session_id+provider_id
-- 改为绑定 user_id+provider_id（见 credentials._credential_aad），因此旧密文
-- 无法再解密。故这里不迁移旧密文，用户需在任一设备重新保存一次 API Key。

DROP TRIGGER IF EXISTS delete_credentials_when_session_revoked;
DROP INDEX IF EXISTS idx_model_credentials_expiry;
DROP TABLE IF EXISTS model_credentials;

CREATE TABLE model_credentials (
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
    PRIMARY KEY (user_id, provider_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_model_credentials_expiry
    ON model_credentials (expires_at);
