"""PLAN-3 §8.2 定向单测：``_ACTIVE_STREAMS`` 并发安全 registry 操作。

registry 在事件循环协程、``asyncio.to_thread`` 后台线程与取消端点之间共享。
锁内只做字典操作与用户校验；``session.cancel()`` 由调用方在锁外执行。
"""

from __future__ import annotations

from scut_senior_api.main import (
    _ACTIVE_STREAMS,
    _find_stream_session,
    _register_stream,
    _unregister_stream,
)


class FakeStreamSession:
    def __init__(self) -> None:
        self.cancelled = False

    def cancel(self) -> None:
        self.cancelled = True


def test_register_find_and_unregister_roundtrip():
    _ACTIVE_STREAMS.clear()
    session = FakeStreamSession()
    _register_stream("run-1", "user-1", session)

    # 同用户可定位会话。
    assert _find_stream_session("run-1", "user-1") is session
    # 用户校验：其他用户不能定位。
    assert _find_stream_session("run-1", "user-2") is None
    # 未知 run：返回 None。
    assert _find_stream_session("run-2", "user-1") is None

    _unregister_stream("run-1")
    assert _find_stream_session("run-1", "user-1") is None
    # 重复 unregister 是安全 no-op。
    _unregister_stream("run-1")


def test_find_returns_session_but_cancel_is_caller_responsibility():
    _ACTIVE_STREAMS.clear()
    session = FakeStreamSession()
    _register_stream("run-1", "user-1", session)

    found = _find_stream_session("run-1", "user-1")
    assert found is session
    # helper 只负责定位与用户校验；取消由 cancel_workflow 在锁外执行。
    assert not session.cancelled
    found.cancel()
    assert session.cancelled
    _unregister_stream("run-1")


def test_register_overwrites_previous_entry_for_same_run():
    _ACTIVE_STREAMS.clear()
    first = FakeStreamSession()
    second = FakeStreamSession()
    _register_stream("run-1", "user-1", first)
    _register_stream("run-1", "user-2", second)

    # 同一 run 最新注册生效，且按最新用户校验。
    assert _find_stream_session("run-1", "user-2") is second
    assert _find_stream_session("run-1", "user-1") is None
    _unregister_stream("run-1")
