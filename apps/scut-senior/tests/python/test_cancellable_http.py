"""迭代 7.5（SOP §12A 分组 B）测试：可取消的上游模型 transport。

覆盖：未取消时结果原样透传；取消标记置位后立即放弃等待并抛出
UpstreamRequestCancelled；网关层把 cancel_check 传递给支持取消的
transport；服务层在取消后把运行收敛为 interrupted（由
test_iteration_3_guard_stream_acceptance 的路由级用例覆盖端到端）。
"""

from __future__ import annotations

import inspect
from threading import Event
from time import monotonic

import pytest

from scut_senior_api.adapters.openrouter import (
    HttpResponse,
    OpenRouterModelGateway,
)
from scut_senior_api.cancellable_http import (
    CancellableJsonHttpClient,
    UpstreamRequestCancelled,
)


def test_passthrough_when_no_cancel_check() -> None:
    class Inner:
        def __init__(self):
            self.calls = 0

        def post_json(self, url, *, headers, payload, timeout_seconds):
            self.calls += 1
            return HttpResponse(status_code=200, body=b"{}")

    inner = Inner()
    client = CancellableJsonHttpClient(inner)
    response = client.post_json(
        "https://example.test",
        headers={},
        payload={},
        timeout_seconds=5,
    )
    assert response.status_code == 200
    assert inner.calls == 1


def test_cancelled_before_start_never_reaches_upstream() -> None:
    class Inner:
        def __init__(self):
            self.calls = 0

        def post_json(self, url, *, headers, payload, timeout_seconds):
            self.calls += 1
            return HttpResponse(status_code=200, body=b"{}")

    inner = Inner()
    client = CancellableJsonHttpClient(inner)
    with pytest.raises(UpstreamRequestCancelled):
        client.post_json(
            "https://example.test",
            headers={},
            payload={},
            timeout_seconds=5,
            cancel_check=lambda: True,
        )
    assert inner.calls == 0


def test_cancel_during_blocked_call_abandons_wait_promptly() -> None:
    inner_entered = Event()
    release_inner = Event()

    class BlockedInner:
        def post_json(self, url, *, headers, payload, timeout_seconds):
            inner_entered.set()
            if not release_inner.wait(timeout=2):
                raise TimeoutError("inner was not released")
            return HttpResponse(status_code=200, body=b"{}")

    client = CancellableJsonHttpClient(BlockedInner(), poll_interval_seconds=0.05)
    cancelled = Event()

    def cancel_check() -> bool:
        return cancelled.is_set()

    import threading

    result: list[object] = []

    def call():
        try:
            result.append(
                client.post_json(
                    "https://example.test",
                    headers={},
                    payload={},
                    timeout_seconds=10,
                    cancel_check=cancel_check,
                )
            )
        except Exception as exc:  # noqa: BLE001
            result.append(exc)

    thread = threading.Thread(target=call)
    thread.start()
    assert inner_entered.wait(timeout=1)
    started = monotonic()
    cancelled.set()
    thread.join(timeout=2)

    assert not thread.is_alive()
    elapsed = monotonic() - started
    assert elapsed < 1.0, "cancellation must not wait for the upstream call"
    assert isinstance(result[0], UpstreamRequestCancelled)

    # 收尾：放行被放弃的 worker，让 daemon 线程尽快退出。
    release_inner.set()


def test_openrouter_gateway_passes_cancel_check_to_capable_transport() -> None:
    seen: dict[str, object] = {}

    class CapableClient:
        def post_json(
            self, url, *, headers, payload, timeout_seconds, cancel_check=None
        ):
            seen["cancel_check"] = cancel_check
            return HttpResponse(status_code=200, body=b"{}")

    gateway = OpenRouterModelGateway(
        api_key="secret-key",
        allowed_model_ids={"google/gemma-4-26b-a4b-it:free"},
        http_client=CapableClient(),
    )
    assert gateway._transport_accepts_cancel_check is True
    marker = lambda: True  # noqa: E731
    from scut_senior_api.adapters.openrouter import _build_structured_request
    from scut_senior_api.contracts import WorkflowRunRequest

    # 直接调用内部 _post_upstream 验证参数传递；不构造完整契约请求。
    gateway._post_upstream({"model": "x"}, marker)
    assert seen["cancel_check"] is marker

    gateway._post_upstream({"model": "x"}, None)
    assert seen["cancel_check"] is None


def test_legacy_transport_without_cancel_check_stays_supported() -> None:
    class LegacyClient:
        def __init__(self):
            self.kwargs_seen: dict = {}

        def post_json(self, url, *, headers, payload, timeout_seconds):
            self.kwargs_seen = {"has_cancel": "cancel_check" in inspect.signature(
                self.post_json
            ).parameters}
            return HttpResponse(status_code=200, body=b"{}")

    legacy = LegacyClient()
    gateway = OpenRouterModelGateway(
        api_key="secret-key",
        allowed_model_ids={"google/gemma-4-26b-a4b-it:free"},
        http_client=legacy,
    )
    assert gateway._transport_accepts_cancel_check is False
    gateway._post_upstream({"model": "x"}, lambda: True)  # 必须不抛 TypeError


def test_cancellable_wrapper_rejects_non_positive_poll_interval() -> None:
    with pytest.raises(ValueError):
        CancellableJsonHttpClient(object(), poll_interval_seconds=0)
