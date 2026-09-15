"""Conservative structural anchors for protected hybrid retrieval ranking."""

from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata
from collections.abc import Sequence

from .ports import RetrievedSource


_QUESTION_RE = re.compile(
    r"(?:第\s*)?(\d{1,3})\s*(?:题|question\b|q\b)", re.IGNORECASE
)
_GENERIC_TITLES = frozenset({"绪论", "概述", "例题", "总结", "附录", "introduction", "overview"})


@dataclass(frozen=True, slots=True)
class ExactAnchorMatch:
    chunk_id: str
    kind: str


def find_exact_anchor_matches(
    query: str, sources: Sequence[RetrievedSource]
) -> tuple[ExactAnchorMatch, ...]:
    """Return only unambiguous question or full-title matches.

    A whole-query substring hit is deliberately not a hard anchor: it may be a
    formula, a generic heading, or incidental prose.  The resulting chunk ids
    are source-local and therefore cannot extend the selected course scope.
    """

    matches: dict[str, ExactAnchorMatch] = {}
    normalized_query = _normalize(query)
    if not normalized_query:
        return ()

    for number in _question_numbers(query):
        candidates = [
            source
            for source in sources
            if source.question_id is not None
            and _question_id_has_number(source.question_id, number)
        ]
        if len(candidates) == 1:
            source = candidates[0]
            matches[source.chunk_id] = ExactAnchorMatch(source.chunk_id, "question")

    if normalized_query not in _GENERIC_TITLES and len(normalized_query) >= 4:
        for source in sources:
            title_fields = (source.source_title, *source.heading_path)
            if any(_normalize(value) == normalized_query for value in title_fields):
                matches.setdefault(
                    source.chunk_id, ExactAnchorMatch(source.chunk_id, "title")
                )
    return tuple(sorted(matches.values(), key=lambda match: (match.kind, match.chunk_id)))


def _question_numbers(query: str) -> frozenset[str]:
    return frozenset(str(int(match.group(1))) for match in _QUESTION_RE.finditer(query))


def _question_id_has_number(question_id: str, number: str) -> bool:
    return re.search(rf"(?<!\d)0*{re.escape(number)}(?!\d)", question_id) is not None


def _normalize(value: str) -> str:
    return "".join(
        char
        for char in unicodedata.normalize("NFKC", value).casefold()
        if not char.isspace() and not unicodedata.category(char).startswith("P")
    )
