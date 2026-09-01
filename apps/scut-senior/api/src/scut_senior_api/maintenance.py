"""迭代 7.5（SOP §12A 分组 B）：周期清理调度器。

决策门结论（2026-08-23，使用者确认）：单机部署采用**进程内后台线程**形态。
失效语义如实如下：

- 调度器随应用进程启停；进程停止期间不发生任何清理。
- 线程启动后立即补扫一次（覆盖停机窗口内到期的数据），随后按固定间隔扫描，
  因此"到期数据物理清理"的最坏延迟为「停机时长 + 一个扫描间隔」。
- 每个清理步骤独立捕获异常：单一步骤失败只记录步骤名与堆栈、该步骤计数按 0
  处理，后续步骤继续执行，不让一个坏表拖垮整轮清理；
  清理语句本身是幂等的 ``DELETE ... WHERE expires_at <= now``，多 worker
  并发重复执行不会双重删除或误删未到期数据（SQLite 写串行化保证）。
- 时钟与间隔可注入，便于测试用受控时钟验证"停机重启后到期数据仍被清理"。

这不是分布式任务队列：它只承诺单机部署下的到点物理清理，不冒充
生产级多副本协调能力。
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

from .auth import Clock, utc_now

LOGGER = logging.getLogger("scut_senior.maintenance")

DEFAULT_SWEEP_INTERVAL_SECONDS = 3600.0


@dataclass(frozen=True, slots=True)
class MaintenanceSweepResult:
    """一次周期清理的结果计数（透传各 cleanup_* 的返回值）。"""

    auth_states: int
    auth_sessions: int
    history_runs: int
    history_conversations: int
    history_feedback: int
    materials: int
    contributions_cleared: int
    platform_rate_events: int = 0


class MaintenanceScheduler:
    """进程内 daemon 线程：启动补扫一次，然后按固定间隔周期清理。"""

    def __init__(
        self,
        repository: Any,
        *,
        interval_seconds: float = DEFAULT_SWEEP_INTERVAL_SECONDS,
        clock: Clock = utc_now,
    ):
        if isinstance(interval_seconds, bool) or not isinstance(
            interval_seconds, (int, float)
        ):
            raise ValueError("interval_seconds must be a positive number")
        if not interval_seconds > 0:
            raise ValueError("interval_seconds must be a positive number")
        self._repository = repository
        self._interval_seconds = float(interval_seconds)
        self._clock = clock
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

    @property
    def interval_seconds(self) -> float:
        return self._interval_seconds

    @property
    def running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def sweep(self) -> MaintenanceSweepResult:
        """执行一次完整清理；由后台线程与启动补扫共用。

        每个清理步骤独立捕获异常：失败步骤只记录日志、计数按 0 处理，
        后续步骤继续执行；结果结构、SQL 与调度间隔保持不变。
        """

        auth = self._run_cleanup_step(
            "cleanup_auth_records",
            lambda: self._repository.cleanup_auth_records(),
            SimpleNamespace(oauth_states=0, auth_sessions=0),
        )
        history = self._run_cleanup_step(
            "cleanup_history_records",
            lambda: self._repository.cleanup_history_records(),
            SimpleNamespace(workflow_runs=0, conversations=0, feedback=0),
        )
        materials = self._run_cleanup_step(
            "cleanup_material_records",
            lambda: self._repository.cleanup_material_records(),
            SimpleNamespace(materials=0, contributions_cleared=0),
        )
        # 迭代 7.5：共享额度锁存的窗口流水／过期闩锁一并周期清理。
        quota_events = self._run_cleanup_step(
            "cleanup_platform_quota_records",
            lambda: (
                self._repository.cleanup_platform_quota_records()
                if callable(
                    getattr(self._repository, "cleanup_platform_quota_records", None)
                )
                else 0
            ),
            0,
        )
        result = MaintenanceSweepResult(
            auth_states=auth.oauth_states,
            auth_sessions=auth.auth_sessions,
            history_runs=history.workflow_runs,
            history_conversations=history.conversations,
            history_feedback=history.feedback,
            materials=materials.materials,
            contributions_cleared=materials.contributions_cleared,
            platform_rate_events=quota_events,
        )
        total = (
            result.auth_states
            + result.auth_sessions
            + result.history_runs
            + result.history_conversations
            + result.history_feedback
            + result.materials
            + result.contributions_cleared
            + result.platform_rate_events
        )
        if total:
            LOGGER.info(
                "maintenance sweep removed expired records at %s: %s",
                self._clock().isoformat(),
                result,
            )
        return result

    def _run_cleanup_step(self, step_name: str, fn: Any, zero: Any) -> Any:
        """执行单个清理步骤；异常只记录步骤名与堆栈，不阻断后续步骤。

        ``zero`` 是该步骤失败时的零计数回退（属性对象或整数），
        保证 ``MaintenanceSweepResult`` 结构与成功路径完全一致。
        """

        try:
            return fn()
        except Exception:  # noqa: BLE001 - 单步骤失败不得拖垮整轮清理
            LOGGER.exception(
                "maintenance step %s failed; continuing schedule", step_name
            )
            return zero

    def start(self) -> None:
        """启动后台线程；幂等——已在运行时是 no-op。"""

        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._run,
                name="scut-senior-maintenance",
                daemon=True,
            )
            self._thread.start()

    def stop(self, *, timeout: float | None = None) -> bool:
        """协作式停机：置位 stop event 并等待当前轮结束。"""

        with self._lock:
            thread = self._thread
        self._stop_event.set()
        if thread is None or not thread.is_alive():
            return True
        thread.join(timeout=timeout)
        return not thread.is_alive()

    def _run(self) -> None:
        # 启动即补扫一次：覆盖上一进程实例停止窗口内到期的数据。
        while True:
            try:
                self.sweep()
            except Exception:  # noqa: BLE001 - 后台线程必须存活到 stop
                LOGGER.exception("maintenance sweep failed; continuing schedule")
            if self._stop_event.wait(timeout=self._interval_seconds):
                return
