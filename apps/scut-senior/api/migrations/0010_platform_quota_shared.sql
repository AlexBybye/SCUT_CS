-- 迭代 7.5（SOP §12A 分组 B）：平台 RPM／每日额度锁存迁移到多 worker 共享存储。
--
-- platform_rate_events：平台通道请求预留流水；RPM 窗口判定与写入在同一条
--   BEGIN IMMEDIATE 事务内完成，多 worker 并发不会重复发放窗口额度，
--   重启后窗口状态仍在（不再依赖进程内存 deque）。
-- platform_quota_latch：每日免费额度耗尽后的全局闩锁，单行表；
--   到期时间以 UTC wall-clock 存储，任何 worker 写入后其余 worker 立即可见。
CREATE TABLE IF NOT EXISTS platform_rate_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    requested_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_platform_rate_events_requested_at
    ON platform_rate_events (requested_at);

CREATE TABLE IF NOT EXISTS platform_quota_latch (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    exhausted_until TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
