from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from typing import Mapping, Protocol
from urllib.error import HTTPError
from urllib.parse import urlencode, urlparse
from urllib.request import Request

from .http_security import build_no_redirect_opener


GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_API_VERSION = "2022-11-28"
GITHUB_USER_AGENT = "SCUT-Senior/0.1"

_MAX_RESPONSE_BYTES = 1_000_000


@dataclass(frozen=True, slots=True)
class GitHubAuthorizationRequest:
    url: str
    state: str


@dataclass(frozen=True, slots=True)
class GitHubIdentity:
    github_id: int
    login: str
    display_name: str
    avatar_url: str | None


@dataclass(frozen=True, slots=True)
class HttpResponse:
    status_code: int
    body: bytes = b""


class HttpTransport(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        body: bytes | None,
        timeout_seconds: float,
    ) -> HttpResponse: ...


class UrllibHttpTransport:
    def __init__(self) -> None:
        self._opener = build_no_redirect_opener()

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        body: bytes | None,
        timeout_seconds: float,
    ) -> HttpResponse:
        request = Request(
            url,
            data=body,
            headers=dict(headers),
            method=method,
        )
        try:
            with self._opener.open(request, timeout=timeout_seconds) as response:
                return HttpResponse(
                    status_code=response.status,
                    body=response.read(_MAX_RESPONSE_BYTES),
                )
        except HTTPError as exc:
            return HttpResponse(
                status_code=exc.code,
                body=exc.read(_MAX_RESPONSE_BYTES),
            )


class FailClosedHttpTransport:
    """Prevents test profiles from accidentally reaching GitHub."""

    def request(self, *_: object, **__: object) -> HttpResponse:
        raise OSError("GitHub test transport was not injected")


class GitHubOAuthError(RuntimeError):
    """A deliberately body-free and credential-free OAuth failure."""

    def __init__(self, *, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


class GitHubOAuthAdapter:
    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        http_transport: HttpTransport | None = None,
        timeout_seconds: float = 10.0,
    ):
        if not client_id.strip():
            raise ValueError("GitHub OAuth client_id is required")
        if not client_secret.strip():
            raise ValueError("GitHub OAuth client_secret is required")
        if not redirect_uri.strip():
            raise ValueError("GitHub OAuth redirect_uri is required")
        if timeout_seconds <= 0:
            raise ValueError("GitHub OAuth timeout must be positive")

        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._http_transport = http_transport or UrllibHttpTransport()
        self._timeout_seconds = timeout_seconds

    def create_authorization_request(self) -> GitHubAuthorizationRequest:
        # 32 random bytes provide a high-entropy, single-use correlation value.
        state = secrets.token_urlsafe(32)
        return GitHubAuthorizationRequest(
            url=self.build_authorization_url(state),
            state=state,
        )

    def build_authorization_url(self, state: str) -> str:
        if not state.strip():
            raise ValueError("GitHub OAuth state is required")
        query = urlencode(
            {
                "client_id": self._client_id,
                "redirect_uri": self._redirect_uri,
                "state": state,
            }
        )
        # Deliberately omit scope: public GitHub identity is sufficient.
        return f"{GITHUB_AUTHORIZE_URL}?{query}"

    def authenticate(self, code: str) -> GitHubIdentity:
        if not code.strip():
            raise GitHubOAuthError(
                code="github_callback_invalid",
                detail="GitHub 登录回调无效，请重新发起登录。",
            )

        token_response = self._request_token(code)
        token_payload = _parse_json_object(
            token_response,
            failure_code="github_oauth_unavailable",
        )
        access_token = token_payload.get("access_token")
        if not isinstance(access_token, str) or not access_token.strip():
            raise _safe_oauth_error("github_oauth_unavailable")

        user_response = self._request_user(access_token)
        user_payload = _parse_json_object(
            user_response,
            failure_code="github_identity_invalid",
        )
        return _parse_identity(user_payload)

    def _request_token(self, code: str) -> HttpResponse:
        body = urlencode(
            {
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "code": code,
                "redirect_uri": self._redirect_uri,
            }
        ).encode("ascii")
        return self._request(
            "POST",
            GITHUB_TOKEN_URL,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": GITHUB_USER_AGENT,
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
            },
            body=body,
        )

    def _request_user(self, access_token: str) -> HttpResponse:
        return self._request(
            "GET",
            GITHUB_USER_URL,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {access_token}",
                "User-Agent": GITHUB_USER_AGENT,
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
            },
            body=None,
        )

    def _request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        body: bytes | None,
    ) -> HttpResponse:
        try:
            response = self._http_transport.request(
                method,
                url,
                headers=headers,
                body=body,
                timeout_seconds=self._timeout_seconds,
            )
        except (OSError, TimeoutError):
            raise _safe_oauth_error("github_oauth_unavailable") from None

        if response.status_code < 200 or response.status_code >= 300:
            raise _safe_oauth_error("github_oauth_unavailable")
        return response


def _parse_json_object(
    response: HttpResponse,
    *,
    failure_code: str,
) -> dict[str, object]:
    try:
        payload = json.loads(response.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise _safe_oauth_error(failure_code) from None
    if not isinstance(payload, dict):
        raise _safe_oauth_error(failure_code)
    return payload


def _parse_identity(payload: Mapping[str, object]) -> GitHubIdentity:
    github_id = payload.get("id")
    login = payload.get("login")
    name = payload.get("name")
    avatar_url = payload.get("avatar_url")

    if type(github_id) is not int or github_id <= 0:
        raise _safe_oauth_error("github_identity_invalid")
    if not isinstance(login, str) or not login.strip():
        raise _safe_oauth_error("github_identity_invalid")
    if name is not None and not isinstance(name, str):
        raise _safe_oauth_error("github_identity_invalid")
    if avatar_url is not None:
        if not isinstance(avatar_url, str) or not _is_https_url(avatar_url):
            raise _safe_oauth_error("github_identity_invalid")

    normalized_login = login.strip()
    display_name = name.strip() if isinstance(name, str) else ""
    return GitHubIdentity(
        github_id=github_id,
        login=normalized_login,
        display_name=display_name or normalized_login,
        avatar_url=avatar_url,
    )


def _is_https_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def _safe_oauth_error(code: str) -> GitHubOAuthError:
    if code == "github_identity_invalid":
        return GitHubOAuthError(
            code=code,
            detail="GitHub 返回的身份资料无效，请重新登录。",
        )
    return GitHubOAuthError(
        code="github_oauth_unavailable",
        detail="GitHub 登录服务暂时不可用，请稍后重试。",
    )
