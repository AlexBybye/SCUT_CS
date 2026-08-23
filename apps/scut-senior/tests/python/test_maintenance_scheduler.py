"""迭代 7.5（SOP §12A 分组 B）测试：周期清理调度器。

覆盖必验场景「清理调度器停机重启后，到期数据仍在期限内被物理清理」，
以及进程内线程形态的启动补扫、协作停机与配置校验。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from scut_senior_api.adapters.sqlite import SQLiteWorkflowRepository
from scut_senior_api.auth import GitHubUserProfile
from scut_senior_api.config import Settings, UnsafeRuntimeConfiguration
from scut_senior_api.main import create_app
from scut_senior_api.maintenance import MaintenanceScheduler


class MutableClock:
    def __init__(self, current: datetime):
        self.current = current

    def __call__(self) -> datetime:
        return self.current

    def advance(self, delta: timedelta) -> None:
        self.current += delta


class CountingRepository:
    """只统计 sweep 调用次数的假仓储；用于启停时序验证。"""

    def __init__(self):
        self.sweeps = 0

    def cleanup_auth_records(self):
        self.sweeps += 1

        class _Counts:
            states = 0
            sessions = 0

        return _Counts()

    def cleanup_history_records(self):
        class _Counts:
            workflow_runs = 0
            conversations = 0
            feedback = 0

        return _Counts()

    def cleanup_material_records(self):
        class _Counts:
            materials = 0
            contributions_cleared = 0

        return _Counts()


def make_repository(tmp_path: Path, clock: MutableClock) -> SQLiteWorkflowRepository:
    return SQLiteWorkflowRepository(
        tmp_path / "maintenance.db",
        clock=clock,
    )


def seed_expired_data(repository: SQLiteWorkflowRepository, user_id):
    return repository.save_temporary_material(
        user_id=str(user_id),
        conversation_id=repository.create_conversation(
            user_id=str(user_id), course_id="linear_algebra", title="维护测试"
        ).conversation_id,
        course_id="linear_algebra",
        title="过期材料",
        content="到期后必须被物理删除",
    )


@pytest.fixture()
def fixed_now() -> datetime:
    return datetime(2026, 8, 23, 12, 0, 0, tzinfo=UTC)


def test_scheduler_removes_expired_records_on_sweep(tmp_path, fixed_now):
    clock = MutableClock(fixed_now)
    repository = make_repository(tmp_path, clock)
    user_id = repository.upsert_github_user(GitHubUserProfile(7001, "sweep-user"))
    detail = seed_expired_data(repository, user_id)

    # 材料未到期：清理不得误删。
    scheduler = MaintenanceScheduler(repository, interval_seconds=3600, clock=clock)
    first = scheduler.sweep()
    assert first.materials == 0
    assert repository.get_temporary_material(
        user_id=str(user_id), material_id=detail.material_id
    ) is not None

    # 推进时钟越过 7 天 TTL（模拟调度器停机窗口内到期）。
    clock.advance(timedelta(days=8))
    second = scheduler.sweep()
    assert second.materials == 1
    assert (
        repository.get_temporary_material(
            user_id=str(user_id), material_id=detail.material_id
        )
        is None
    )


def test_startup_catch_up_covers_downtime_window(tmp_path, fixed_now):
    """停机重启后：到期数据在下一轮（这里是启动补扫）即被物理清理。"""

    clock = MutableClock(fixed_now)
    repository = make_repository(tmp_path, clock)
    user_id = repository.upsert_github_user(GitHubUserProfile(7002, "restart-user"))
    session = repository.issue_session(user_id)
    detail = seed_expired_data(repository, user_id)

    # “停机”期间时钟推进：会话 7 天 TTL 与材料 7 天 TTL 均已越过。
    clock.advance(timedelta(days=8))

    scheduler = MaintenanceScheduler(repository, interval_seconds=60, clock=clock)
    result = scheduler.sweep()  # 启动补扫
    assert result.materials == 1
    assert result.auth_sessions >= 1
    assert not repository.authenticate_session(session.token)
    assert (
        repository.get_temporary_material(
            user_id=str(user_id), material_id=detail.material_id
        )
        is None
    )


def test_start_runs_immediate_sweep_then_stops_cleanly():
    repository = CountingRepository()
    scheduler = MaintenanceScheduler(repository, interval_seconds=0.05)
    try:
        scheduler.start()
        assert scheduler.running
        # 启动立即补扫一次；随后按间隔继续，直到 stop 置位。
        deadline_loop = 0
        while repository.sweeps < 2 and deadline_loop < 200:
            import time

            time.sleep(0.01)
            deadline_loop += 1
        assert repository.sweeps >= 2
    finally:
        stopped = scheduler.stop(timeout=2.0)
    assert stopped
    assert not scheduler.running
    sweeps_after_stop = repository.sweeps
    import time

    time.sleep(0.15)
    assert repository.sweeps == sweeps_after_stop


def test_start_is_idempotent():
    repository = CountingRepository()
    scheduler = MaintenanceScheduler(repository, interval_seconds=3600)
    try:
        scheduler.start()
        thread_first = scheduler._thread
        scheduler.start()
        assert scheduler._thread is thread_first
    finally:
        scheduler.stop(timeout=2.0)


@pytest.mark.parametrize("bad_interval", [0, -1, "60", True])
def test_invalid_interval_rejected(bad_interval):
    with pytest.raises(ValueError):
        MaintenanceScheduler(CountingRepository(), interval_seconds=bad_interval)


def test_settings_reject_non_positive_interval():
    with pytest.raises(UnsafeRuntimeConfiguration):
        Settings(
            app_env="test",
            maintenance_interval_seconds=0,
        ).assert_safe()


def test_app_lifespan_starts_and_stops_scheduler(tmp_path):
    settings = Settings(
        app_env="test",
        database_path=tmp_path / "lifespan.db",
        maintenance_scheduler_enabled=True,
        maintenance_interval_seconds=3600,
    )
    app = create_app(settings)
    scheduler = app.state.maintenance_scheduler
    assert scheduler is not None
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        capabilities = response.json()["capabilities"]
        assert capabilities["periodic_cleanup_scheduler"] is True
        assert scheduler.running
    assert not scheduler.running
    scheduler.stop(timeout=2.0)


def test_app_lifespan_disabled_leaves_scheduler_unstarted(tmp_path):
    settings = Settings(
        app_env="test",
        database_path=tmp_path / "lifespan-off.db",
        maintenance_scheduler_enabled=False,
    )
    app = create_app(settings)
    scheduler = app.state.maintenance_scheduler
    assert scheduler is not None
    with TestClient(app):
        pass
    assert not scheduler.running
