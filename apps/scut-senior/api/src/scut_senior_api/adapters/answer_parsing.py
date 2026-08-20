from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping

from ..ports import GeneratedAnswer


class ModelAnswerParseError(ValueError):
    """The provider returned no usable assistant text.

    This deliberately distinguishes an absent/empty completion from a
    completion that merely does not follow the optional response envelope.
    Providers are allowed to return ordinary text, a JSON object, or a fenced
    JSON object; deterministic guards validate any source claims afterwards.
    """


_JSON_FENCE_RE = re.compile(
    r"^\s*```(?:json)?\s*\n(?P<body>[\s\S]*?)\n?```\s*$",
    re.IGNORECASE,
)
_CITATION_RE = re.compile(r"(?<![A-Za-z0-9_])\[S([1-9][0-9]*)\]")
_SCUT_META_COMMENT_RE = re.compile(
    r"\s*<!--\s*scut-meta\s*:\s*(?P<body>\{[\s\S]*?\})\s*-->\s*$",
    re.IGNORECASE,
)


def parse_chat_completion_answer(body: bytes) -> GeneratedAnswer:
    """Extract a best-effort answer from a Chat Completions response body."""

    try:
        payload = json.loads(body.decode("utf-8"))
        content = payload["choices"][0]["message"]["content"]
    except (
        AttributeError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        KeyError,
        IndexError,
        TypeError,
    ):
        raise ModelAnswerParseError("chat completion has no assistant content") from None
    if not isinstance(content, str) or not content.strip():
        raise ModelAnswerParseError("chat completion assistant content is empty")
    return parse_answer_content(content)


def parse_answer_content(content: str) -> GeneratedAnswer:
    """Normalize JSON, fenced JSON, and plain assistant text into one shape.

    Auxiliary recommendation fields are optional.  Source identifiers are only
    collected from explicit ``citation_ids`` or inline ``[S#]`` markers, and
    remain subject to the request-local citation guard in ``runtime_guards``.
    """

    text = content.strip()
    if not text:
        raise ModelAnswerParseError("assistant content is empty")

    decoded = _decode_json(text)
    if isinstance(decoded, Mapping):
        return _from_mapping(decoded)
    if isinstance(decoded, str) and decoded.strip():
        return _plain_text_answer_with_metadata(decoded.strip())
    return _plain_text_answer_with_metadata(text)


def _decode_json(text: str) -> object | None:
    fenced = _JSON_FENCE_RE.match(text)
    candidate = fenced.group("body").strip() if fenced else text
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def _from_mapping(value: Mapping[object, object]) -> GeneratedAnswer:
    repository_answer = _first_text(
        value,
        "repository_answer",
        "answer",
        "content",
        "response",
    )
    repository_answer, comment_metadata = _extract_scut_metadata(repository_answer)
    general_supplement = _text(value.get("general_supplement"))
    user_material_answer = _text(value.get("user_material_answer"))
    personalized_analysis = _text(value.get("personalized_analysis"))
    if not any(
        (
            repository_answer,
            general_supplement,
            user_material_answer,
            personalized_analysis,
        )
    ):
        raise ModelAnswerParseError("structured completion has no answer text")

    # Keep declared identifiers in their original order so the request-local
    # guard can still reject an explicit duplicate.  Inline markers merely
    # fill in an omitted declaration; they must not silently turn a duplicate
    # provider declaration into a valid citation set.
    declared_citations = _string_items(value.get("citation_ids"))
    inline_citations = _inline_citation_ids(repository_answer)
    citation_ids = declared_citations + tuple(
        citation for citation in inline_citations if citation not in declared_citations
    )
    return GeneratedAnswer(
        repository_answer=repository_answer,
        citation_ids=citation_ids,
        general_supplement=general_supplement,
        user_material_answer=user_material_answer,
        personalized_analysis=personalized_analysis,
        related_topics=(
            _string_items(value.get("related_topics"))
            or _string_items(comment_metadata.get("related_topics"))
        ),
        related_questions=_string_items(value.get("related_questions")),
        bilibili_search_keywords=(
            _string_items(value.get("bilibili_search_keywords"))
            or _string_items(comment_metadata.get("bilibili_search_keywords"))
        ),
    )


def _plain_text_answer_with_metadata(text: str) -> GeneratedAnswer:
    repository_answer, comment_metadata = _extract_scut_metadata(text)
    return GeneratedAnswer(
        repository_answer=repository_answer,
        citation_ids=_inline_citation_ids(repository_answer),
        related_topics=_string_items(comment_metadata.get("related_topics")),
        bilibili_search_keywords=_string_items(
            comment_metadata.get("bilibili_search_keywords")
        ),
    )


def _extract_scut_metadata(text: str) -> tuple[str, Mapping[object, object]]:
    """Remove the optional model sidecar before it reaches student-visible Markdown."""

    match = _SCUT_META_COMMENT_RE.search(text)
    if match is None:
        return text.strip(), {}
    body = match.group("body")
    try:
        decoded = json.loads(body)
    except json.JSONDecodeError:
        decoded = None
    metadata = decoded if isinstance(decoded, Mapping) else {}
    return text[: match.start()].strip(), metadata


def _first_text(value: Mapping[object, object], *keys: str) -> str:
    for key in keys:
        candidate = _text(value.get(key))
        if candidate:
            return candidate
    return ""


def _text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _string_items(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item.strip() for item in value if isinstance(item, str) and item.strip())


def _inline_citation_ids(text: str) -> tuple[str, ...]:
    return _ordered_unique(f"S{number}" for number in _CITATION_RE.findall(text))


def _ordered_unique(values: Iterable[str]) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = value.strip()
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return tuple(result)
