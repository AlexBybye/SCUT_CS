from __future__ import annotations

import json
import logging
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


logger = logging.getLogger("scut_senior_api.adapters.answer_parsing")

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
    """Extract a best-effort answer from a Chat Completions response body.

    Real OpenAI-compatible providers differ in the assistant payload shape:
    ``message.content`` may be a plain string, a list of typed content parts
    (multimodal ``{"type": "text", "text": ...}`` items), or a single part
    mapping. All of these are normalized here; anything else still fails
    closed with a server-side shape diagnostic so a broken upstream is not
    silently turned into a student-visible answer.
    """

    try:
        payload = json.loads(body.decode("utf-8"))
        message = payload["choices"][0]["message"]
        content = message.get("content")
    except (
        AttributeError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        KeyError,
        IndexError,
        TypeError,
    ):
        raise ModelAnswerParseError("chat completion has no assistant content") from None

    text = _assistant_text(content)
    if not text.strip():
        _log_unparsable_shape(body, content)
        raise ModelAnswerParseError("chat completion assistant content is empty")
    return parse_answer_content(text)


def _assistant_text(content: object) -> str:
    """Normalize plain-string, part-list, and single-part assistant content."""

    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part.get("text", "")
            for part in content
            if isinstance(part, Mapping) and isinstance(part.get("text"), str)
        )
    if isinstance(content, Mapping):
        candidate = content.get("text")
        if isinstance(candidate, str):
            return candidate
        # A structured envelope object (e.g. {"markdown": ...}) is re-serialized
        # so the downstream parser can decode it as a structured completion.
        return json.dumps(content, ensure_ascii=False)
    return ""


def _log_unparsable_shape(body: bytes, content: object) -> None:
    """Record why an upstream completion was rejected, without leaking it to
    the student-visible Trace or answer. Detail stays server-side."""

    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        payload = None
    top_keys = list(payload) if isinstance(payload, Mapping) else []
    message: object = None
    finish_reason: object = None
    if isinstance(payload, Mapping) and isinstance(payload.get("choices"), list):
        for choice in payload["choices"]:
            if not isinstance(choice, Mapping):
                continue
            if isinstance(choice.get("message"), Mapping):
                message = choice["message"]
            finish_reason = choice.get("finish_reason")
            break
    msg_keys = list(message) if isinstance(message, Mapping) else []
    content_len = len(content) if isinstance(content, (str, list, Mapping)) else -1
    reasoning_len = -1
    if (
        isinstance(message, Mapping)
        and isinstance(message.get("reasoning_content"), str)
    ):
        reasoning_len = len(message["reasoning_content"])
    logger.warning(
        "chat completion assistant content is unusable: content_type=%s "
        "content_len=%s top_keys=%s msg_keys=%s reasoning_content_len=%s "
        "finish_reason=%s body_preview=%r",
        type(content).__name__,
        content_len,
        top_keys,
        msg_keys,
        reasoning_len,
        finish_reason,
        body[:120].decode("utf-8", errors="replace"),
    )


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
        "markdown",
        "output",
        "text",
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
