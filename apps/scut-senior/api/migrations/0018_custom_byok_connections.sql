-- Replace the fixed four-provider key ring with user-defined OpenAI-compatible
-- connections. Existing keys receive the profile formerly supplied by the
-- fixed catalog, so this migration does not discard encrypted credentials.

ALTER TABLE model_credentials RENAME TO model_credentials_fixed;

CREATE TABLE model_credentials (
    user_id TEXT NOT NULL,
    provider_id TEXT NOT NULL CHECK (
        length(provider_id) BETWEEN 1 AND 64
        AND provider_id NOT GLOB '*[^a-z0-9-]*'
        AND substr(provider_id, 1, 1) BETWEEN 'a' AND 'z'
        AND provider_id NOT GLOB '*--*'
        AND substr(provider_id, -1, 1) <> '-'
    ),
    display_name TEXT NOT NULL CHECK (length(display_name) BETWEEN 1 AND 100),
    base_url TEXT NOT NULL CHECK (length(base_url) BETWEEN 1 AND 2048),
    model_id TEXT NOT NULL CHECK (length(model_id) BETWEEN 1 AND 100),
    protocol TEXT NOT NULL CHECK (protocol = 'openai_chat_completions'),
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

INSERT INTO model_credentials (
    user_id, provider_id, display_name, base_url, model_id, protocol,
    ciphertext, nonce, algorithm, key_version, created_at, updated_at, expires_at
)
SELECT
    user_id,
    provider_id,
    CASE provider_id
        WHEN 'openrouter' THEN 'OpenRouter'
        WHEN 'deepseek' THEN 'DeepSeek'
        WHEN 'siliconflow' THEN '硅基流动'
        WHEN 'zhipu' THEN '智谱 AI'
    END,
    CASE provider_id
        WHEN 'openrouter' THEN 'https://openrouter.ai/api/v1'
        WHEN 'deepseek' THEN 'https://api.deepseek.com'
        WHEN 'siliconflow' THEN 'https://api.siliconflow.cn/v1'
        WHEN 'zhipu' THEN 'https://open.bigmodel.cn/api/paas/v4'
    END,
    CASE provider_id
        WHEN 'openrouter' THEN 'deepseek/deepseek-v4-flash-0731'
        WHEN 'deepseek' THEN 'deepseek-v4-flash'
        WHEN 'siliconflow' THEN 'Pro/zai-org/GLM-4.7'
        WHEN 'zhipu' THEN 'glm-5.2'
    END,
    'openai_chat_completions',
    ciphertext, nonce, algorithm, key_version, created_at, updated_at, expires_at
FROM model_credentials_fixed;

DROP TABLE model_credentials_fixed;

CREATE INDEX IF NOT EXISTS idx_model_credentials_expiry
    ON model_credentials (expires_at);
