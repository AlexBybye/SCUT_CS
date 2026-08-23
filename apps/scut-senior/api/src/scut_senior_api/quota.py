"""迭代 7.5（SOP §12A 分组 B）：平台 RPM／每日额度锁存的多 worker 共享存储。

此前 OpenRouter 网关把 RPM 滑动窗口与每日额度闩锁保存在进程内
（``deque``＋一个 float 字段）：单进程重启即丢失，多 worker／多进程各自
记账、额度被重复发放。本模块把两种锁存抽象为一个最小协议并提供两个实现：

- :class:`InProcessPlatformQuotaLatch`：原进程内语义（默认，保持既有单元
  测试与无 SQLite 场景的行为不变）；
- :class:`SqlitePlatformQuotaStore`：以应用既有 SQLite 数据库为共享存储，
  预留、计数、写入在一条 ``BEGIN IMMEDIATE`` 事务内完成——重启不丢失，
  多 worker 不重复发放。

这是单机／共享文件系统部署下的务实方案；不冒充分布式协调能力。
"""

from __future__ import annotations

import threading
from collections import deque
from datetime import timedelta
from time import monotonic
from typing import Callable, Protocol, runtime_checkable

from .adapters.sqlite import SQLiteWorkflowRepository
from .auth import Clock, utc_now

MonotonicClock = Callable[[], float]

PLATFORM_REQUESTS_PER_MINUTE = 20
PLATFORM_RATE_WINDOW = timedelta(minutes=1)


@runtime_checkable
class PlatformQuotaStore(Protocol):
    """平台通道额度锁存的最小接口。"""

    def reserve_request(self) -> bool:
        """尝试预留一个请求名额；返回 False 表示窗口已满需拒绝。"""
        ...

    def daily_exhausted_until(self):
        """返回仍生效的每日耗尽闩锁到期时间；无生效闩锁返回 None。"""
        ...

    def latch_daily_exhaustion(self, *, exhausted_until) -> None:
        """登记每日额度耗尽，直到 exhausted_until（timezone-aware）。"""
        ...


class InProcessPlatformQuotaLatch:
    """原 OpenRouter 网关内存语义的提取，行为逐条保留。"""

    def __init__(
        self,
        *,
        limit: int = PLATFORM_REQUESTS_PER_MINUTE,
        window_seconds: float = PLATFORM_RATE_WINDOW.total_seconds(),
        clock: Clock = utc_now,
        monotonic_clock: MonotonicClock = monotonic,
        lock: threading.Lock | None = None,
    ):
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer")
        if not window_seconds > 0:
            raise ValueError("window_seconds must be positive")
        self._limit = limit
        self._window_seconds = float(window_seconds)
        self._clock = clock
        self._monotonic_clock = monotonic_clock
        self._request_times: deque[float] = deque()
        self._daily_exhausted_until_monotonic: float | None = None
        self._quota_lock = lock or threading.Lock()

    def reserve_request(self) -> bool:
        with self._quota_lock:
            now = self._monotonic_clock()
            cutoff = now - self._window_seconds
            while self._request_times and self._request_times[0] <= cutoff:
                self._request_times.popleft()
            if len(self._request_times) >= self._limit:
                return False
            self._request_times.append(now)
            return True

    def daily_exhausted_until(self):
        now_wall = self._clock()
        with self._quota_lock:
            deadline = self._daily_exhausted_until_monotonic
            if deadline is None:
                return None
            now_mono = self._monotonic_clock()
            if now_mono >= deadline:
                self._daily_exhausted_until_monotonic = None
                return None
            remaining = max(deadline - now_mono, 0.0)
            return now_wall + timedelta(seconds=remaining)

    def latch_daily_exhaustion(self, *, exhausted_until) -> None:
        if exhausted_until.tzinfo is None or exhausted_until.utcoffset() is None:
            raise ValueError("exhausted_until must be timezone-aware")
        until_wall = exhausted_until.astimezone(exhausted_until.tzinfo)
        now_wall = self._clock()
        with self._quota_lock:
            self._daily_exhausted_until_monotonic = self._monotonic_clock() + max(
                (until_wall - now_wall).total_seconds(), 1.0
            )


class SqlitePlatformQuotaStore:
    """以 SQLite 为共享存储的额度锁存；重启不丢失、多进程不重复发放。"""

    def __init__(
        self,
        repository: SQLiteWorkflowRepository,
        *,
        limit: int = PLATFORM_REQUESTS_PER_MINUTE,
        window_seconds: float = PLATFORM_RATE_WINDOW.total_seconds(),
    ):
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer")
        if not window_seconds > 0:
            raise ValueError("window_seconds must be positive")
        self._repository = repository
        self._limit = limit
        self._window_seconds = float(window_seconds)

    def reserve_request(self) -> bool:
        return self._repository.reserve_platform_request(
            limit=self._limit, window_seconds=self._window_seconds
        )

    def daily_exhausted_until(self):
        return self._repository.platform_daily_exhaustion()

    def latch_daily_exhaustion(self, *, exhausted_until) -> None:
        self._repository.latch_platform_daily_exhaustion(
            exhausted_until=exhausted_until
        )
