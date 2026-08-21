from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone
from typing import Callable, Sequence
from urllib.parse import quote, urlencode

from ..contracts import ExternalResource
from ..url_safety import contains_url_like_text

BILIBILI_SEARCH_URL = "https://search.bilibili.com/all"
MAX_KEYWORDS = 3
MAX_KEYWORD_LENGTH = 32
MAX_COURSE_TITLE_LENGTH = 40

_QUESTION_SPLIT_RE = re.compile(r"[,，。；、！？?!]+")
_QUESTION_PREFIX_RE = re.compile(
    r"^(?:请(?:帮我)?|麻烦(?:你)?|能否|可以|为什么|如何|怎么(?:样)?|什么是|"
    r"解释(?:一下)?|讲解(?:一下)?|说明(?:一下)?|我想知道)\s*"
)
_EXAMPLE_PREFIX_RE = re.compile(
    r"^(?:并且|并|再|以及)?(?:给出|举(?:一个|个)?例(?:说明)?|提供)"
    r"(?:一个|一[个种])?\s*"
)


class BilibiliLinkDiscoveryAdapter:
    """Build one anonymous Bilibili search link from focused keywords.

    This adapter never fetches Bilibili pages or APIs. The fixed search URL is
    opened by the user, so Bilibili supplies the current results. Keywords are
    treated only as URL-encoded query text and can never select a host or path.

    The project does not maintain or read a video catalog, so concrete video
    links cannot enter answers.
    """

    def __init__(
        self,
        *,
        clock: Callable[[], datetime] | None = None,
    ):
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def discover(
        self,
        *,
        course_id: str,
        course_title: str,
        keywords: Sequence[str],
    ) -> list[ExternalResource]:
        normalized_course_id = _normalize_text(course_id, max_length=100)
        normalized_course_title = _normalize_text(
            course_title, max_length=MAX_COURSE_TITLE_LENGTH
        )
        if not normalized_course_id:
            raise ValueError("course_id must remain non-empty after normalization")
        if not normalized_course_title:
            raise ValueError("course_title must remain non-empty after normalization")

        normalized_keywords = normalize_keywords(keywords)
        if not normalized_keywords:
            return []

        search_query = " ".join(normalized_keywords)
        search_resource = ExternalResource(
            resource_id=None,
            course_id=normalized_course_id,
            platform="bilibili",
            resource_type="search",
            title=f"在哔哩哔哩搜索：{search_query}",
            url=_search_url(search_query),
            matched_topic="、".join(normalized_keywords),
            review_status="unreviewed_live_search",
            catalog_version=None,
            query_keywords=list(normalized_keywords),
            generated_at=self._clock(),
            evidence_role="supplementary_only",
        )
        return [search_resource]


def normalize_keywords(keywords: Sequence[str]) -> tuple[str, ...]:
    """Normalize, deduplicate, and cap model-provided Bilibili search terms."""

    if isinstance(keywords, str):
        values: Sequence[object] = (keywords,)
    else:
        values = keywords

    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str):
            continue
        keyword = _normalize_text(value, max_length=MAX_KEYWORD_LENGTH)
        if not keyword or contains_url_like_text(value):
            continue
        dedupe_key = keyword.casefold()
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        normalized.append(keyword)
        if len(normalized) >= MAX_KEYWORDS:
            break
    return tuple(normalized)


def derive_question_keywords(question: str) -> tuple[str, ...]:
    """Build one bounded Bilibili query from the current workflow question.

    This intentionally does not reuse model-generated topics: the live-search
    entry must reflect what the student just asked, even when a provider emits
    ordinary Markdown rather than the optional JSON envelope.
    """

    normalized = _normalize_text(question, max_length=MAX_KEYWORD_LENGTH * 8)
    if not normalized or contains_url_like_text(normalized):
        return ()

    parts: list[str] = []
    for raw_part in _QUESTION_SPLIT_RE.split(normalized):
        part = raw_part
        while True:
            stripped = _QUESTION_PREFIX_RE.sub("", part)
            if stripped == part:
                break
            part = stripped
        part = _EXAMPLE_PREFIX_RE.sub("", part)
        part = part.strip()
        if not part or contains_url_like_text(part):
            continue
        separator = " " if parts else ""
        if len(" ".join(parts)) + len(separator) + len(part) > MAX_KEYWORD_LENGTH:
            if not parts:
                parts.append(part[:MAX_KEYWORD_LENGTH].strip())
            break
        parts.append(part)

    return normalize_keywords((" ".join(parts),)) if parts else ()


def _normalize_text(value: str, *, max_length: int) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    without_controls = "".join(
        " " if unicodedata.category(character).startswith("C") else character
        for character in normalized
    )
    collapsed = " ".join(without_controls.split())
    return collapsed[:max_length].strip()


def _search_url(query: str) -> str:
    encoded_query = urlencode({"keyword": query}, quote_via=quote, safe="")
    return f"{BILIBILI_SEARCH_URL}?{encoded_query}"
