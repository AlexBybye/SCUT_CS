from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from urllib.parse import unquote

import idna


_DOMAIN_DOT_TRANSLATION = str.maketrans(
    {
        "\u3002": ".",  # ideographic full stop
        "\uff0e": ".",  # fullwidth full stop
        "\uff61": ".",  # halfwidth ideographic full stop
    }
)
_MAX_PERCENT_DECODE_PASSES = 2
_URL_LIKE_RE = re.compile(
    r"(?:"
    r"(?<![A-Za-z0-9+.-])[A-Za-z][A-Za-z0-9+.-]{1,31}://|"
    r"(?<![A-Za-z0-9_])//(?=(?:www\.)?[A-Za-z0-9\[])|"
    r"(?<![A-Za-z0-9_@-])(?:www\.)?[A-Za-z0-9-]+"
    r"(?:\.[A-Za-z0-9-]+)*\."
    r"(?:[A-Za-z]{2,63}|xn--[A-Za-z0-9-]{2,59})"
    r"(?::\d{1,5})?(?![A-Za-z0-9_-])|"
    r"(?<![A-Za-z0-9_.-])(?:\d{1,3}\.){3}\d{1,3}"
    r"(?::\d{1,5}|[/?#])|"
    r"(?<![A-Za-z0-9_.-])localhost(?::\d{1,5}|[/?#])|"
    r"(?<![A-Za-z0-9_.-])\[[0-9A-Fa-f:.]+\](?::\d{1,5}|[/?#])"
    r")",
    re.IGNORECASE,
)


def contains_url_like_text(text: str) -> bool:
    """Reject model-controlled URL text before it reaches any result field.

    The Runtime contract allows only the backend-built Bilibili search entry in
    ``external_resources``. Answer blocks, suggestions, and model keywords must
    therefore reject schemes, scheme-relative URLs, bare domains, and local/IP
    URL forms after the same bounded Unicode/percent canonicalization.
    """

    return _URL_LIKE_RE.search(canonicalize_url_detection_text(text)) is not None


def canonicalize_url_detection_text(text: str) -> str:
    """Canonicalize URL obfuscations for detection without rewriting output.

    Browsers and URL parsers may treat Unicode hostname separators as ASCII
    dots. Percent-decoding before every normalization pass also covers encoded
    separators (including their UTF-8 forms) and one layer of double encoding.
    The bounded loop prevents attacker-controlled input from causing unbounded
    canonicalization work.
    """

    canonical = text
    for _ in range(_MAX_PERCENT_DECODE_PASSES):
        canonical = _normalize_detection_pass(canonical)
        decoded = unquote(canonical)
        if decoded == canonical:
            break
        canonical = decoded
    return _normalize_detection_pass(canonical)


def _normalize_detection_pass(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).translate(
        _DOMAIN_DOT_TRANSLATION
    )
    without_controls = "".join(
        character
        for character in normalized
        if not unicodedata.category(character).startswith("C")
    )
    try:
        return idna.uts46_remap(
            without_controls,
            std3_rules=False,
            transitional=False,
        )
    except (idna.IDNAError, UnicodeError):
        # Arbitrary answer text can contain emoji or other code points that are
        # invalid in a hostname. Remap character-by-character so one unrelated
        # symbol cannot make ignored UTS-46 hostname characters fail open.
        return "".join(_uts46_remap_character(char) for char in without_controls)


@lru_cache(maxsize=4_096)
def _uts46_remap_character(character: str) -> str:
    try:
        return idna.uts46_remap(
            character,
            std3_rules=False,
            transitional=False,
        )
    except (idna.IDNAError, UnicodeError):
        return character
