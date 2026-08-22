-- 迭代 7（SOP §12）：临时材料精读与贡献待处理队列。
--
-- temporary_materials：用户会话内私有材料，普通材料 7 天 TTL 到期物理删除；
--   默认不进入公共索引、课程包或跨用户缓存。
-- contributions：用户主动提交的贡献记录；content_snapshot 是“必要待审副本”，
--   最长保留 30 天，到期清理时载荷清空、未决状态置为 expired。
--   PR 只能由人工在仓库侧创建与合并；本表不产生任何自动合并路径。
CREATE TABLE IF NOT EXISTS temporary_materials (
    material_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    conversation_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    content_sha256 TEXT NOT NULL,
    char_count INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_temporary_materials_owner
    ON temporary_materials (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_temporary_materials_expiry
    ON temporary_materials (expires_at);

CREATE TABLE IF NOT EXISTS contributions (
    contribution_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    material_id TEXT,
    course_id TEXT NOT NULL,
    proposed_source_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content_snapshot TEXT NOT NULL,
    state TEXT NOT NULL CHECK (
        state IN ('draft', 'submitted', 'pr_open', 'merged', 'rejected', 'expired')
    ),
    pr_url TEXT,
    maintainer_note TEXT,
    char_count INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_contributions_owner
    ON contributions (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_contributions_queue
    ON contributions (state, created_at ASC);

CREATE INDEX IF NOT EXISTS idx_contributions_expiry
    ON contributions (expires_at);
