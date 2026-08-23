"""迭代 7.5（SOP §12A 分组 B）测试：平台额度锁存迁移到共享存储。

必验场景：双 worker 并发请求下平台日额度不被重复发放，重启后锁存仍在。
generate() 路径上的 429 映射由 test_openrouter_models.py 既有用例覆盖；
这里直接驱动网关的额度预留／闩锁方法验证共享存储语义。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from scut_senior_api.adapters.openrouter import HttpResponse, OpenRouterModelGateway
from scut_senior_api.adapters.sqlite import SQLiteWorkflowRepository
from scut_senior_api.quota import (
    PLATFORM_RATE_WINDOW,
    PLATFORM_REQUESTS_PER_MINUTE,
    InProcessPlatformQuotaLatch,
    SqlitePlatformQuotaStore,
)


class MutableClock:
    def __init__(self, current: datetime):
        self.current = current

    def __call__(self) -> datetime:
        return self.current

    def advance(self, delta: timedelta) -> None:
        self.current += delta


@pytest.fixture()
def fixed_now() -> datetime:
    return datetime(2026, 8, 23, 12, 0, 0, tzinfo=UTC)


DAILY_HEADERS = {
    "X-RateLimit-Limit": "50",
    "X-RateLimit-Remaining": "0",
    "X-RateLimit-Reset": "86400",
}


def test_sqlite_store_respects_window_limit_across_workers(tmp_path, fixed_now):
    """两个"worker"（两个仓储实例、同一数据库）合计不超发窗口额度。"""

    clock = MutableClock(fixed_now)
    worker_a = SQLiteWorkflowRepository(tmp_path / "quota.db", clock=clock)
    worker_b = SQLiteWorkflowRepository(tmp_path / "quota.db", clock=clock)
    store_a = SqlitePlatformQuotaStore(worker_a, limit=3, window_seconds=60.0)
    store_b = SqlitePlatformQuotaStore(worker_b, limit=3, window_seconds=60.0)

    granted = [store.reserve_request() for store in [store_a, store_b] * 3]

    # 前三个名额发放，第四个起拒绝——跨实例合计记账。
    assert granted == [True, True, True, False, False, False]

    # 窗口滑过后恢复发放。
    clock.advance(timedelta(seconds=61))
    assert store_a.reserve_request() is True


def test_daily_latch_survives_restart_and_is_shared(tmp_path, fixed_now):
    """闩锁写入后：新进程（新仓储实例）仍看到生效的每日耗尽锁。"""

    clock = MutableClock(fixed_now)
    first = SQLiteWorkflowRepository(tmp_path / "latch.db", clock=clock)
    store_first = SqlitePlatformQuotaStore(first)
    until = fixed_now + timedelta(hours=10)
    store_first.latch_daily_exhaustion(exhausted_until=until)

    second = SQLiteWorkflowRepository(tmp_path / "latch.db", clock=clock)
    store_second = SqlitePlatformQuotaStore(second)
    assert store_second.daily_exhausted_until() == until

    # 过期后自动清除并返回 None。
    clock.advance(timedelta(hours=11))
    assert store_second.daily_exhausted_until() is None
    assert store_first.daily_exhausted_until() is None


def test_repository_rejects_naive_timestamp(tmp_path):
    repository = SQLiteWorkflowRepository(tmp_path / "naive.db")
    with pytest.raises(ValueError):
        repository.latch_platform_daily_exhaustion(
            exhausted_until=datetime(2026, 8, 24, 12, 0, 0)
        )




class _NoNetworkClient:
    """占位 transport：额度路径不应触达网络。"""

    def post_json(self, url, *, headers, payload, timeout_seconds):
        raise AssertionError("quota path must not reach the network")


def make_gateway(tmp_path: Path, clock: MutableClock) -> OpenRouterModelGateway:
    """构造挂接 SQLite 共享额度存储的真实网关（假 HTTP 不影响额度路径）。"""

    class FakeHttpClient:
        def post_json(self, url, *, headers, payload, timeout_seconds):
            return HttpResponse(status_code=429, headers=DAILY_HEADERS, body=b"{}")

    return OpenRouterModelGateway(
        api_key="secret-key",
        allowed_model_ids={"google/gemma-4-26b-a4b-it:free"},
        http_client=FakeHttpClient(),
        clock=clock,
        quota_store=SqlitePlatformQuotaStore(
            SQLiteWorkflowRepository(tmp_path / "gw.db", clock=clock)
        ),
    )


def test_gateway_shared_latch_refuses_after_restart(tmp_path, fixed_now):
    """429 触发闩锁后，"重启"（新网关＋新存储实例）仍然拒绝上游调用。"""

    clock = MutableClock(fixed_now)
    gateway = make_gateway(tmp_path, clock)

    gateway._latch_daily_exhaustion(
        HttpResponse(status_code=429, headers=DAILY_HEADERS, body=b"{}")
    )
    with pytest.raises(Exception) as latched:
        gateway._reserve_platform_request()
    assert getattr(latched.value, "code", "") == "platform_daily_quota_exhausted"

    restarted = make_gateway(tmp_path, clock)
    with pytest.raises(Exception) as after_restart:
        restarted._reserve_platform_request()
    assert (
        getattr(after_restart.value, "code", "")
        == "platform_daily_quota_exhausted"
    )

    # 越过闩锁到期时间后恢复 RPM 预留（此处成功即代表不再报每日耗尽）。
    clock.advance(timedelta(hours=25))
    restarted._reserve_platform_request()


def test_gateway_rpm_window_shared_across_instances(tmp_path, fixed_now):
    """两个网关实例共用同一 SQLite 存储：RPM 窗口合计记账、重启仍在。"""

    clock = MutableClock(fixed_now)

    def make():
        return OpenRouterModelGateway(
            api_key="secret-key",
            allowed_model_ids={"google/gemma-4-26b-a4b-it:free"},
            http_client=_NoNetworkClient(),  # 不触达网络
            clock=clock,
            quota_store=SqlitePlatformQuotaStore(
                SQLiteWorkflowRepository(tmp_path / "rpm.db", clock=clock),
                limit=2,
                window_seconds=PLATFORM_RATE_WINDOW.total_seconds(),
            ),
        )

    first = make()
    second = make()
    first._reserve_platform_request()
    second._reserve_platform_request()
    with pytest.raises(Exception) as limited:
        first._reserve_platform_request()
    assert getattr(limited.value, "code", "") == "platform_rate_limited"

    # “重启”第三个实例：窗口状态仍在共享存储中。
    third = make()
    with pytest.raises(Exception) as after_restart:
        third._reserve_platform_request()
    assert getattr(after_restart.value, "code", "") == "platform_rate_limited"

    clock.advance(timedelta(minutes=2))
    third._reserve_platform_request()


def test_in_process_latch_defaults_match_documented_constants():
    latch = InProcessPlatformQuotaLatch()
    results = [latch.reserve_request() for _ in range(PLATFORM_REQUESTS_PER_MINUTE)]
    assert all(results)
    assert latch.reserve_request() is False


def test_maintenance_cleanup_prunes_expired_quota_records(tmp_path, fixed_now):
    clock = MutableClock(fixed_now)
    repository = SQLiteWorkflowRepository(tmp_path / "cleanup.db", clock=clock)
    store = SqlitePlatformQuotaStore(repository, limit=2, window_seconds=60.0)
    assert store.reserve_request() is True
    assert store.reserve_request() is True
    assert store.reserve_request() is False  # 窗口满

    clock.advance(timedelta(minutes=5))
    pruned = repository.cleanup_platform_quota_records()
    assert pruned == 2
    assert store.reserve_request() is True
