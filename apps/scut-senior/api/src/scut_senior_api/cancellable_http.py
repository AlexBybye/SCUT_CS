"""迭代 7.5（SOP §12A 分组 B）：可取消的上游模型 transport。

取代迭代 5"客户端断开后后台跑完落库"的过渡语义：页面断开时尽力中止
等待上游响应。包装器把阻塞的 ``post_json`` 放进受监督的 daemon 线程，
主线程按固定间隔轮询取消标记；一旦置位即抛出
:class:`UpstreamRequestCancelled`，不再等待、不再把结果落库为完成。

如实说明失效语义（不冒充已完成取消）：
- 被放弃的 daemon 线程里的底层套接字按其自身超时上限最终关闭；
  供应商侧是否因此停止计费无法在本进程内证实，只能如实留痕。
- 取消证据有两份：持久化 trace 的 ``workflow_interrupted``／
  ``client_interrupted`` 节点，以及断开时的应用日志（LOGGER.warning）。
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from time import monotonic
from typing import Mapping

from .adapters.openrouter import HttpResponse

CancelCheck = Callable[[], bool]

DEFAULT_CANCEL_POLL_INTERVAL_SECONDS = 0.1


class UpstreamRequestCancelled(RuntimeError):
    """上游调用在等待期间被请求方取消；结果被丢弃，不得落库为完成。"""

    def __init__(self) -> None:
        super().__init__("upstream request cancelled by caller")


class CancellableJsonHttpClient:
    """为任意阻塞 :class:`JsonHttpClient` 提供协作式取消的包装器。"""

    def __init__(
        self,
        inner: object,
        *,
        poll_interval_seconds: float = DEFAULT_CANCEL_POLL_INTERVAL_SECONDS,
    ):
        self._inner = inner
        if not poll_interval_seconds > 0:
            raise ValueError("poll_interval_seconds must be positive")
        self._poll_interval_seconds = poll_interval_seconds

    def post_json(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        payload: Mapping[str, object],
        timeout_seconds: float,
        cancel_check: CancelCheck | None = None,
    ) -> HttpResponse:
        if cancel_check is None or cancel_check():
            # 无取消语义时直连；已取消的调用直接拒绝，不再发起。
            if cancel_check is not None:
                raise UpstreamRequestCancelled
            return self._post_inner(url, headers, payload, timeout_seconds)

        result: list[HttpResponse] = []
        error: list[BaseException] = []
        done = threading.Event()

        def run() -> None:
            try:
                result.append(
                    self._post_inner(url, headers, payload, timeout_seconds)
                )
            except BaseException as exc:  # noqa: BLE001 - 必须唤醒主线程
                error.append(exc)
            finally:
                done.set()

        worker = threading.Thread(
            target=run,
            name="scut-senior-cancellable-upstream",
            daemon=True,
        )
        worker.start()
        deadline = monotonic() + max(timeout_seconds, 0.0)
        while not done.wait(self._poll_interval_seconds):
            if cancel_check():
                # 尽力取消：放弃等待。worker 是 daemon，套接字按自身超时回收，
                # 其结果永远不会被本调用采用或落库。
                raise UpstreamRequestCancelled
            if monotonic() >= deadline:
                raise TimeoutError("upstream request timed out (supervised)")
        if error:
            raise error[0]
        return result[0]

    def _post_inner(
        self,
        url: str,
        headers: Mapping[str, str],
        payload: Mapping[str, object],
        timeout_seconds: float,
    ) -> HttpResponse:
        post_json = getattr(self._inner, "post_json")
        return post_json(
            url,
            headers=headers,
            payload=payload,
            timeout_seconds=timeout_seconds,
        )
