from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Mapping

from ..contracts import WorkflowRunRequest
from ..ports import GeneratedAnswer, RetrievedSource
from .openrouter import HttpResponse, JsonHttpClient, UrllibJsonHttpClient


OPENROUTER_BYOK_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEEPSEEK_BYOK_ENDPOINT = "https://api.deepseek.com/chat/completions"
SILICONFLOW_BYOK_ENDPOINT = "https://api.siliconflow.cn/v1/chat/completions"
ZHIPU_BYOK_ENDPOINT = "https://open.bigmodel.cn/api/paas/v4/chat/completions"


@dataclass(frozen=True, slots=True)
class FixedByokRoute:
    endpoint: str
    model_id: str


FIXED_BYOK_ROUTES: Mapping[str, FixedByokRoute] = {
    "openrouter": FixedByokRoute(
        OPENROUTER_BYOK_ENDPOINT,
        "deepseek/deepseek-v4-flash-0731",
    ),
    "deepseek": FixedByokRoute(
        DEEPSEEK_BYOK_ENDPOINT,
        "deepseek-v4-flash",
    ),
    "siliconflow": FixedByokRoute(
        SILICONFLOW_BYOK_ENDPOINT,
        "Pro/zai-org/GLM-4.7",
    ),
    "zhipu": FixedByokRoute(
        ZHIPU_BYOK_ENDPOINT,
        "glm-5.2",
    ),
}


class FailClosedJsonHttpClient:
    """Test-only default that makes accidental live network use impossible."""

    def post_json(self, *_: object, **__: object) -> HttpResponse:
        raise OSError("model test transport was not injected")


class ByokGatewayError(RuntimeError):
    def __init__(self, *, status_code: int, code: str, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.code = code
        self.detail = detail


class FixedByokModelGateway:
    """One fixed model and endpoint per enabled provider, with no fallback."""

    def __init__(
        self,
        *,
        http_client: JsonHttpClient | None = None,
        timeout_seconds: float = 60.0,
    ):
        self._http_client = http_client or UrllibJsonHttpClient()
        self._timeout_seconds = timeout_seconds

    def generate(
        self,
        *,
        api_key: str,
        request: WorkflowRunRequest,
        sources: list[RetrievedSource],
    ) -> GeneratedAnswer:
        route = FIXED_BYOK_ROUTES.get(request.provider_id)
        if route is None or request.model_id != route.model_id:
            raise ByokGatewayError(
                status_code=422,
                code="byok_route_not_registered",
                detail="所选 BYOK 供应商或模型未登记。",
            )
        if not api_key or api_key != api_key.strip():
            raise ByokGatewayError(
                status_code=422,
                code="invalid_model_credential",
                detail="已保存的 API Key 无效，请重新保存。",
            )
        payload = _build_byok_request(request, sources)
        try:
            response = self._http_client.post_json(
                route.endpoint,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                payload=payload,
                timeout_seconds=self._timeout_seconds,
            )
        except Exception:
            raise ByokGatewayError(
                status_code=503,
                code="byok_provider_unavailable",
                detail="模型供应商暂时不可用，请稍后重试。",
            ) from None
        if response.status_code < 200 or response.status_code >= 300:
            raise _safe_byok_upstream_error(response.status_code)
        return _parse_byok_answer(response)


def _build_byok_request(
    request: WorkflowRunRequest, sources: list[RetrievedSource]
) -> dict[str, object]:
    source_context = "\n\n".join(
        f"[S{index}] {source.source_title}\n{source.text}"
        for index, source in enumerate(sources, start=1)
    ) or "（本次没有可用课程资料候选。）"
    payload: dict[str, object] = {
        "model": request.model_id,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是 SCUT 课程助教。只能把下方 [S1]、[S2] 等候选编号视为"
                    "课程资料来源，不得编造来源。只输出一个 JSON 对象，字段必须为 "
                    "repository_answer、related_topics、related_questions、"
                    "bilibili_search_keywords。最后一个字段只能包含 0～3 个短检索词，"
                    "不能包含 URL、推荐理由或思考过程。"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Workflow: {request.workflow_type.value}\n"
                    f"知识范围: {request.knowledge_scope.value}\n"
                    "Bilibili 搜索词: "
                    f"{'可返回 0～3 个' if request.include_bilibili_resources else '必须为空数组'}\n"
                    f"问题: {request.user_input}\n\n"
                    f"课程资料候选:\n{source_context}"
                ),
            },
        ],
        "max_tokens": 2048,
        "temperature": 0.2,
    }
    if request.provider_id == "openrouter":
        payload["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "scut_senior_workflow_answer",
                "strict": True,
                "schema": _answer_schema(),
            },
        }
        payload["provider"] = {"require_parameters": True}
    else:
        payload["response_format"] = {"type": "json_object"}
    return payload


def _answer_schema() -> dict[str, object]:
    return {
        "type": "object",
        "properties": {
            "repository_answer": {"type": "string"},
            "related_topics": {
                "type": "array",
                "items": {"type": "string"},
            },
            "related_questions": {
                "type": "array",
                "items": {"type": "string"},
            },
            "bilibili_search_keywords": {
                "type": "array",
                "items": {"type": "string", "maxLength": 32},
                "maxItems": 3,
            },
        },
        "required": [
            "repository_answer",
            "related_topics",
            "related_questions",
            "bilibili_search_keywords",
        ],
        "additionalProperties": False,
    }


def _safe_byok_upstream_error(status_code: int) -> ByokGatewayError:
    if status_code in {401, 403}:
        return ByokGatewayError(
            status_code=422,
            code="byok_provider_authentication_failed",
            detail="你提供的 API Key 无效，或无权调用所选模型。",
        )
    if status_code == 402:
        return ByokGatewayError(
            status_code=402,
            code="byok_provider_credit_unavailable",
            detail="你的模型供应商账户余额或额度不足。",
        )
    if status_code == 429:
        return ByokGatewayError(
            status_code=429,
            code="byok_provider_rate_limited",
            detail="你的模型供应商账户请求过于频繁，请稍后重试。",
        )
    if status_code in {408, 504}:
        return ByokGatewayError(
            status_code=504,
            code="byok_provider_timeout",
            detail="模型供应商响应超时，请稍后重试。",
        )
    return ByokGatewayError(
        status_code=502,
        code="byok_provider_unavailable",
        detail="模型供应商暂时不可用，请稍后重试。",
    )


def _parse_byok_answer(response: HttpResponse) -> GeneratedAnswer:
    try:
        payload = json.loads(response.body.decode("utf-8"))
        content = payload["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            raise TypeError
        structured = json.loads(content)
        answer = structured["repository_answer"]
        topics = structured["related_topics"]
        questions = structured["related_questions"]
        keywords = structured.get("bilibili_search_keywords", [])
        if not isinstance(answer, str) or not answer.strip():
            raise TypeError
        if not _is_string_list(topics) or not _is_string_list(questions):
            raise TypeError
        if not _is_string_list(keywords):
            keywords = []
    except (
        AttributeError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        KeyError,
        IndexError,
        TypeError,
    ):
        raise ByokGatewayError(
            status_code=502,
            code="byok_provider_invalid_response",
            detail="模型供应商返回了无法处理的结果，请稍后重试。",
        ) from None
    return GeneratedAnswer(
        repository_answer=answer.strip(),
        related_topics=tuple(item.strip() for item in topics if item.strip()),
        related_questions=tuple(
            item.strip() for item in questions if item.strip()
        ),
        bilibili_search_keywords=tuple(
            item.strip() for item in keywords[:3] if item.strip()
        ),
    )


def _is_string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)
