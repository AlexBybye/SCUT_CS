from __future__ import annotations

import json
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlparse

import pytest

from scut_senior_api.adapters.github import (
    GITHUB_API_VERSION,
    GITHUB_AUTHORIZE_URL,
    GITHUB_TOKEN_URL,
    GITHUB_USER_AGENT,
    GITHUB_USER_URL,
    GitHubIdentity,
    GitHubOAuthAdapter,
    GitHubOAuthError,
    HttpResponse,
)


CLIENT_ID = "github-client-id"
CLIENT_SECRET = "github-client-secret"
REDIRECT_URI = "http://127.0.0.1:8000/api/v1/auth/github/callback"
CALLBACK_CODE = "single-use-callback-code"
ACCESS_TOKEN = "github-access-token"


@dataclass
class RecordedRequest:
    method: str
    url: str
    headers: dict[str, str]
    body: bytes | None
    timeout_seconds: float


@dataclass
class StubTransport:
    responses: list[HttpResponse]
    requests: list[RecordedRequest] = field(default_factory=list)

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str],
        body: bytes | None,
        timeout_seconds: float,
    ) -> HttpResponse:
        self.requests.append(
            RecordedRequest(
                method=method,
                url=url,
                headers=dict(headers),
                body=body,
                timeout_seconds=timeout_seconds,
            )
        )
        return self.responses.pop(0)


def _adapter(transport: StubTransport) -> GitHubOAuthAdapter:
    return GitHubOAuthAdapter(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        http_transport=transport,
        timeout_seconds=7.5,
    )


def _successful_transport(
    *,
    user_payload: dict[str, object] | None = None,
) -> StubTransport:
    return StubTransport(
        responses=[
            HttpResponse(
                200,
                json.dumps(
                    {
                        "access_token": ACCESS_TOKEN,
                        "token_type": "bearer",
                        "scope": "",
                    }
                ).encode(),
            ),
            HttpResponse(
                200,
                json.dumps(
                    user_payload
                    or {
                        "id": 58_391_231,
                        "login": "student-user",
                        "name": "Student User",
                        "avatar_url": "https://avatars.githubusercontent.com/u/58391231?v=4",
                        "email": "must-not-leave-adapter@example.com",
                    }
                ).encode(),
            ),
        ]
    )


def test_authorization_request_uses_official_endpoint_and_random_state() -> None:
    transport = StubTransport([])
    adapter = _adapter(transport)

    first = adapter.create_authorization_request()
    second = adapter.create_authorization_request()

    assert first.state != second.state
    assert len(first.state) >= 40
    parsed = urlparse(first.url)
    assert f"{parsed.scheme}://{parsed.netloc}{parsed.path}" == GITHUB_AUTHORIZE_URL
    assert parse_qs(parsed.query) == {
        "client_id": [CLIENT_ID],
        "redirect_uri": [REDIRECT_URI],
        "state": [first.state],
    }
    assert "scope" not in parse_qs(parsed.query)
    assert transport.requests == []


def test_authenticate_exchanges_code_then_reads_public_identity() -> None:
    transport = _successful_transport()

    identity = _adapter(transport).authenticate(CALLBACK_CODE)

    assert identity == GitHubIdentity(
        github_id=58_391_231,
        login="student-user",
        display_name="Student User",
        avatar_url="https://avatars.githubusercontent.com/u/58391231?v=4",
    )
    assert not hasattr(identity, "access_token")
    assert not hasattr(identity, "email")
    assert len(transport.requests) == 2

    token_request, user_request = transport.requests
    assert (token_request.method, token_request.url) == ("POST", GITHUB_TOKEN_URL)
    assert token_request.headers == {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": GITHUB_USER_AGENT,
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }
    assert parse_qs(token_request.body.decode()) == {
        "client_id": [CLIENT_ID],
        "client_secret": [CLIENT_SECRET],
        "code": [CALLBACK_CODE],
        "redirect_uri": [REDIRECT_URI],
    }
    assert token_request.timeout_seconds == 7.5

    assert (user_request.method, user_request.url) == ("GET", GITHUB_USER_URL)
    assert user_request.headers == {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "User-Agent": GITHUB_USER_AGENT,
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }
    assert user_request.body is None
    assert user_request.timeout_seconds == 7.5


def test_null_display_name_falls_back_to_login() -> None:
    transport = _successful_transport(
        user_payload={
            "id": 42,
            "login": "octocat",
            "name": None,
            "avatar_url": None,
        }
    )

    identity = _adapter(transport).authenticate(CALLBACK_CODE)

    assert identity.display_name == "octocat"
    assert identity.avatar_url is None


@pytest.mark.parametrize("github_id", [None, True, 0, -1, "58391231", 1.5])
def test_identity_requires_positive_immutable_numeric_github_id(
    github_id: object,
) -> None:
    transport = _successful_transport(
        user_payload={
            "id": github_id,
            "login": "student-user",
            "name": "Student User",
            "avatar_url": None,
        }
    )

    with pytest.raises(GitHubOAuthError) as raised:
        _adapter(transport).authenticate(CALLBACK_CODE)

    assert raised.value.code == "github_identity_invalid"


@pytest.mark.parametrize(
    "responses",
    [
        [HttpResponse(401, b'{"error":"bad_verification_code"}')],
        [HttpResponse(200, b"not-json")],
        [HttpResponse(200, b'{"error":"incorrect_client_credentials"}')],
        [
            HttpResponse(200, json.dumps({"access_token": ACCESS_TOKEN}).encode()),
            HttpResponse(403, b'{"message":"API rate limit exceeded"}'),
        ],
        [
            HttpResponse(200, json.dumps({"access_token": ACCESS_TOKEN}).encode()),
            HttpResponse(200, b'{"id":1,"login":"octocat","avatar_url":"javascript:alert(1)"}'),
        ],
    ],
)
def test_upstream_failures_are_safe_and_do_not_leak_payloads_or_credentials(
    responses: list[HttpResponse],
) -> None:
    secret_markers = {
        CLIENT_ID,
        CLIENT_SECRET,
        CALLBACK_CODE,
        ACCESS_TOKEN,
        "bad_verification_code",
        "incorrect_client_credentials",
        "API rate limit exceeded",
        "javascript:alert(1)",
    }

    with pytest.raises(GitHubOAuthError) as raised:
        _adapter(StubTransport(responses)).authenticate(CALLBACK_CODE)

    rendered = f"{raised.value!s} {raised.value!r} {raised.value.__dict__}"
    assert raised.value.code in {
        "github_oauth_unavailable",
        "github_identity_invalid",
    }
    assert all(marker not in rendered for marker in secret_markers)


@pytest.mark.parametrize("failure", [TimeoutError("token"), OSError("secret")])
def test_transport_failures_are_mapped_without_original_exception(
    failure: Exception,
) -> None:
    class FailingTransport:
        def request(self, *args: object, **kwargs: object) -> HttpResponse:
            raise failure

    adapter = GitHubOAuthAdapter(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        http_transport=FailingTransport(),
    )

    with pytest.raises(GitHubOAuthError) as raised:
        adapter.authenticate(CALLBACK_CODE)

    assert raised.value.code == "github_oauth_unavailable"
    assert raised.value.__cause__ is None
    assert "secret" not in str(raised.value)


def test_blank_callback_code_never_reaches_transport() -> None:
    transport = StubTransport([])

    with pytest.raises(GitHubOAuthError) as raised:
        _adapter(transport).authenticate("  ")

    assert raised.value.code == "github_callback_invalid"
    assert transport.requests == []
