from __future__ import annotations

import json
from collections.abc import Collection

from ..contracts import WorkflowRunRequest
from ..ports import ConversationTurn, GeneratedAnswer, RetrievedSource
from .answer_parsing import ModelAnswerParseError, parse_chat_completion_answer
from .http_security import is_timeout_transport_error
from .openrouter import (
    HttpResponse,
    JsonHttpClient,
    UrllibJsonHttpClient,
    _build_structured_request,
)

# Zhipu bigmodel (智谱) OpenAI-compatible chat completions endpoint.
# https://docs.bigmodel.cn/cn/guide/develop/http/api
ZHIPU_CHAT_COMPLETIONS_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
PLATFORM_RATE_LIMITED_MESSAGE = "平台免费通道请求过于频繁，请稍后重试。"

# Zhipu error codes observed on the live endpoint. These are surfaced verbatim
# (sanitized) so a model-level throttle (1305 "该模型当前访问量过大") is not
# misreported as a per-account concurrency limit. Codes are documented at
# https://docs.bigmodel.cn/cn/api-reference/错误码 and remain stable.
ZHIPU_ERROR_CODE_THROTTLED = "1305"
ZHIPU_ERROR_MESSAGE_THROTTLED = "该模型当前访问量过大，请稍后再试。"


class ZhipuPlatformGatewayError(RuntimeError):
    def __init__(self, *, status_code: int, code: str, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.code = code
        self.detail = detail


class ZhipuPlatformModelGateway:
    """Server-side free gateway for Zhipu bigmodel's ``glm-4.7-flash``.

    Zhipu's free tier is a fixed, first-party model with no ``:free`` suffix or
    public zero-price catalog equivalent to OpenRouter's, so there is no daily
    quota header to latch. Upstream 429 responses still fail closed as
    ``platform_rate_limited``, and every transport/parse failure maps to the
    shared ``platform_model_*`` error codes so the service retry policy and the
    API error handlers treat Zhipu exactly like the OpenRouter platform channel.
    """

    provider_id = "zhipu"

    def __init__(
        self,
        *,
        api_key: str,
        allowed_model_ids: Collection[str],
        http_client: JsonHttpClient | None = None,
        timeout_seconds: float = 60.0,
    ):
        if not api_key.strip():
            raise ValueError("Zhipu API key is required")
        self._api_key = api_key
        self._allowed_model_ids = frozenset(allowed_model_ids)
        self._http_client = http_client or UrllibJsonHttpClient()
        self._timeout_seconds = timeout_seconds

    def generate(
        self,
        request: WorkflowRunRequest,
        sources: list[RetrievedSource],
        history: tuple[ConversationTurn, ...] = (),
    ) -> GeneratedAnswer:
        if (
            request.provider_id != self.provider_id
            or request.model_id not in self._allowed_model_ids
        ):
            raise ZhipuPlatformGatewayError(
                status_code=422,
                code="model_not_registered",
                detail="所选模型未在当前可用的平台目录中登记。",
            )

        payload = _build_structured_request(request, sources, history)
        try:
            response = self._http_client.post_json(
                ZHIPU_CHAT_COMPLETIONS_URL,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                payload=payload,
                timeout_seconds=self._timeout_seconds,
            )
        except OSError as exc:
            if is_timeout_transport_error(exc):
                raise ZhipuPlatformGatewayError(
                    status_code=503,
                    code="platform_model_timeout",
                    detail="平台模型响应超时，请稍后重试。",
                ) from None
            raise ZhipuPlatformGatewayError(
                status_code=503,
                code="platform_model_unavailable",
                detail="平台模型服务暂时不可用，请稍后重试。",
            ) from None

        if response.status_code == 429:
            raise _rate_limit_error(response)
        if response.status_code < 200 or response.status_code >= 300:
            raise _safe_upstream_error(response.status_code)

        try:
            return parse_chat_completion_answer(response.body)
        except ModelAnswerParseError:
            raise ZhipuPlatformGatewayError(
                status_code=502,
                code="platform_model_invalid_response",
                detail="平台模型返回了无法处理的结果，请稍后重试。",
            ) from None


def _rate_limit_error(response: HttpResponse) -> ZhipuPlatformGatewayError:
    """Distinguish a model-level throttle from an account concurrency limit.

    Zhipu's 1305 ("该模型当前访问量过大") is a platform-wide, model-level
    throttle unrelated to the caller's concurrency. Surfacing it honestly lets
    a student retry against a different model instead of thinking their own
    request rate is at fault. Any other 429 falls back to the generic channel
    message without leaking the upstream body.
    """

    code = _safe_error_code(response.body)
    if code == ZHIPU_ERROR_CODE_THROTTLED:
        return ZhipuPlatformGatewayError(
            status_code=429,
            code="platform_rate_limited",
            detail=ZHIPU_ERROR_MESSAGE_THROTTLED,
        )
    return ZhipuPlatformGatewayError(
        status_code=429,
        code="platform_rate_limited",
        detail=PLATFORM_RATE_LIMITED_MESSAGE,
    )


def _safe_error_code(body: bytes) -> str | None:
    """Extract Zhipu's ``error.code`` without ever echoing the error body."""

    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    error = payload.get("error")
    if not isinstance(error, dict):
        return None
    code = error.get("code")
    return str(code) if code is not None else None


def _safe_upstream_error(status_code: int) -> ZhipuPlatformGatewayError:
    if status_code in {401, 403}:
        code = "platform_model_authentication_failed"
        detail = "平台模型服务认证失败，请联系维护者。"
    elif status_code == 402:
        code = "platform_model_credit_unavailable"
        detail = "平台模型免费通道当前不可用，请联系维护者。"
    elif status_code in {408, 504}:
        code = "platform_model_timeout"
        detail = "平台模型响应超时，请稍后重试。"
    else:
        code = "platform_model_unavailable"
        detail = "平台模型服务暂时不可用，请稍后重试。"
    return ZhipuPlatformGatewayError(status_code=503, code=code, detail=detail)
