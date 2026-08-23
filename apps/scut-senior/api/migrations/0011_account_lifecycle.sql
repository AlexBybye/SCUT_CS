-- 迭代 7.5（SOP §12A 分组 B / §16 待确认项 3 落地）：账号生命周期。
--
-- deleted_accounts：已注销账号的 GitHub 身份封锁名单（只保留 github_user_id
--   与注销时间，不保留任何档案数据）。登录回调在建立/复用用户前先查本表，
--   命中即拒绝——注销后无法再登录。这是唯一的注销后残留，用于 fail-closed。
CREATE TABLE IF NOT EXISTS deleted_accounts (
    github_user_id INTEGER PRIMARY KEY CHECK (github_user_id > 0),
    deleted_at TEXT NOT NULL
);
