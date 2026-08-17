from __future__ import annotations

from urllib.request import HTTPRedirectHandler, OpenerDirector, build_opener


class RejectRedirectHandler(HTTPRedirectHandler):
    """Turn every redirect response into an HTTPError at the original origin."""

    def redirect_request(self, *args: object, **kwargs: object) -> None:
        return None


def build_no_redirect_opener() -> OpenerDirector:
    return build_opener(RejectRedirectHandler())


def is_timeout_transport_error(error: BaseException) -> bool:
    """Recognize direct and urllib-wrapped timeouts without parsing responses."""

    pending: list[BaseException] = [error]
    seen: set[int] = set()
    while pending:
        current = pending.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        if isinstance(current, TimeoutError):
            return True
        for nested in (getattr(current, "reason", None), current.__cause__):
            if isinstance(nested, BaseException):
                pending.append(nested)
            elif isinstance(nested, str) and nested.strip().casefold() in {
                "timeout",
                "timed out",
            }:
                return True
    return False
