from __future__ import annotations

from urllib.request import HTTPRedirectHandler, OpenerDirector, build_opener


class RejectRedirectHandler(HTTPRedirectHandler):
    """Turn every redirect response into an HTTPError at the original origin."""

    def redirect_request(self, *args: object, **kwargs: object) -> None:
        return None


def build_no_redirect_opener() -> OpenerDirector:
    return build_opener(RejectRedirectHandler())
