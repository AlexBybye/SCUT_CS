"""Provider-neutral answer invocation used by the workflow runtime."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ..contracts import WorkflowRunRequest
from ..ports import ConversationTurn, GeneratedAnswer, ModelGateway, RetrievedSource, UserKeyModelGateway


@dataclass(slots=True)
class AnswerGenerator:
    """Keep provider selection and repair prompt construction out of the facade.

    Credential loading, call budgets, retries and citation guards remain owned
    by the caller's lifecycle. The key is supplied only for this invocation
    and is never retained on the object or returned in an outcome.
    """

    platform_model: ModelGateway
    byok_model: UserKeyModelGateway
    zhipu_model: ModelGateway | None = None

    def generate(
        self,
        *,
        request: WorkflowRunRequest,
        sources: list[RetrievedSource],
        history: tuple[ConversationTurn, ...],
        use_user_key: bool,
        api_key: str | None,
        connection: object | None,
        provider_id: str,
        repair_context: str | None,
        cancel_check: Callable[[], bool] | None,
    ) -> GeneratedAnswer:
        generation_request = request
        if repair_context:
            generation_request = request.model_copy(
                update={
                    "user_input": (
                        f"{request.user_input}\n\n"
                        "[内部引用校验修复提示] 上一次回答未通过引用校验，"
                        f"请只修复以下问题：{repair_context}"
                    )
                }
            )
        if use_user_key:
            if api_key is None or connection is None:
                raise RuntimeError("BYOK generation requires an active credential")
            return self.byok_model.generate(
                api_key=api_key,
                connection=connection,
                request=generation_request,
                sources=sources,
                history=history,
                cancel_check=cancel_check,
            )
        active_model = (
            self.zhipu_model
            if provider_id == "zhipu" and self.zhipu_model is not None
            else self.platform_model
        )
        return active_model.generate(
            generation_request,
            sources,
            history=history,
            cancel_check=cancel_check,
        )
