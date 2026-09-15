"""Provider-neutral answer invocation used by the workflow runtime."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import inspect

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
        timeout_seconds: float | None,
        cancel_check: Callable[[], bool] | None,
    ) -> GeneratedAnswer:
        if use_user_key:
            if api_key is None or connection is None:
                raise RuntimeError("BYOK generation requires an active credential")
            return _generate_with_optional_repair(
                self.byok_model.generate,
                api_key=api_key,
                connection=connection,
                request=request,
                sources=sources,
                history=history,
                repair_context=repair_context,
                timeout_seconds=timeout_seconds,
                cancel_check=cancel_check,
            )
        active_model = (
            self.zhipu_model
            if provider_id == "zhipu" and self.zhipu_model is not None
            else self.platform_model
        )
        return _generate_with_optional_repair(
            active_model.generate,
            request,
            sources,
            history=history,
            repair_context=repair_context,
            timeout_seconds=timeout_seconds,
            cancel_check=cancel_check,
        )


def _generate_with_optional_repair(
    generate: Callable[..., GeneratedAnswer],
    *args: object,
    repair_context: str | None,
    timeout_seconds: float | None,
    **kwargs: object,
) -> GeneratedAnswer:
    """Pass server-owned repair instructions without changing user input.

    Gateways that predate this optional argument (notably deterministic test
    doubles and third-party implementations) retain their existing call
    contract. Provider adapters that accept it place the instruction in a
    separately labelled, server-owned prompt section.
    """

    parameters = inspect.signature(generate).parameters
    supports_keyword = "repair_context" in parameters or any(
        parameter.kind is inspect.Parameter.VAR_KEYWORD
        for parameter in parameters.values()
    )
    if repair_context and supports_keyword:
        kwargs["repair_context"] = repair_context
    if timeout_seconds is not None and _supports_keyword(parameters, "timeout_seconds"):
        kwargs["timeout_seconds"] = timeout_seconds
    return generate(*args, **kwargs)


def _supports_keyword(
    parameters: dict[str, inspect.Parameter], keyword: str
) -> bool:
    return keyword in parameters or any(
        parameter.kind is inspect.Parameter.VAR_KEYWORD
        for parameter in parameters.values()
    )
