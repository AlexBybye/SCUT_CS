from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from uuid import UUID


OAUTH_STATE_TTL = timedelta(minutes=10)
SESSION_TTL = timedelta(days=7)
MIN_TOKEN_LENGTH = 32
SESSION_COOKIE_NAME = "__Host-scut_senior_session"
SESSION_COOKIE_MAX_AGE = int(SESSION_TTL.total_seconds())
SESSION_COOKIE_PATH = "/"
SESSION_COOKIE_HTTP_ONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAME_SITE = "lax"

Clock = Callable[[], datetime]
TokenFactory = Callable[[], str]


def utc_now() -> datetime:
    return datetime.now(UTC)


def secure_token() -> str:
    return token_urlsafe(32)


class AuthRequired(Exception):
    code = "auth_required"
    detail = "请先使用 GitHub 登录。"

    def __init__(self) -> None:
        super().__init__(self.detail)


class OAuthStateInvalid(Exception):
    code = "oauth_state_invalid"
    detail = "GitHub 登录状态无效、已过期或已使用，请重新登录。"

    def __init__(self) -> None:
        super().__init__(self.detail)


@dataclass(frozen=True, slots=True)
class GitHubUserProfile:
    github_user_id: int
    login: str
    display_name: str | None = None

    def __post_init__(self) -> None:
        if (
            isinstance(self.github_user_id, bool)
            or self.github_user_id <= 0
            or self.github_user_id > 2**63 - 1
        ):
            raise ValueError("github_user_id must be a positive 64-bit integer")
        login = self.login.strip()
        if not login:
            raise ValueError("GitHub login must not be blank")
        display_name = self.display_name.strip() if self.display_name else None
        object.__setattr__(self, "login", login)
        object.__setattr__(self, "display_name", display_name)

    @property
    def resolved_display_name(self) -> str:
        return self.display_name or self.login


@dataclass(frozen=True, slots=True)
class IssuedOAuthState:
    state: str
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class IssuedSession:
    token: str
    auth_session_id: UUID
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    user_id: UUID
    display_name: str
    is_mock: bool
    auth_session_id: UUID
    github_user_id: int
    github_login: str
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class AuthCleanupCounts:
    oauth_states: int
    auth_sessions: int
