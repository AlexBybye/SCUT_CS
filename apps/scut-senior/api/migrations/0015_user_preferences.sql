-- 个人中心偏好：随 GitHub 账号（user_id）维护，跨设备同步。
-- 存 theme_mode / accent_theme / answer_mode / tone 等键值对，值以文本存储。

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id TEXT NOT NULL,
    preference_key TEXT NOT NULL,
    preference_value TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (user_id, preference_key),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
