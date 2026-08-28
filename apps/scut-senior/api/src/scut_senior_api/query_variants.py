"""Deterministic, auditable retrieval query variants.

The table is intentionally data-only.  It expands terms already present in a
typed workflow anchor; it never rewrites the question with an LLM or changes
the requested course scope.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Mapping

from .paths import APP_ROOT


QUERY_EXPANSIONS_PATH = APP_ROOT / "resources" / "retrieval" / "query-expansions.json"
MAX_QUERY_VARIANTS = 3


@lru_cache(maxsize=1)
def load_query_expansions() -> Mapping[str, Mapping[str, tuple[str, ...]]]:
    """Load and validate the checked-in course expansion table once."""

    payload = json.loads(QUERY_EXPANSIONS_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != "query-expansions-v1":
        raise ValueError("query expansion table schema is invalid")
    courses = payload.get("courses")
    if not isinstance(courses, dict):
        raise ValueError("query expansion table courses must be an object")
    result: dict[str, dict[str, tuple[str, ...]]] = {}
    for course_id, terms in courses.items():
        if not isinstance(course_id, str) or not course_id.strip() or not isinstance(terms, dict):
            raise ValueError("query expansion table course entry is invalid")
        normalized: dict[str, tuple[str, ...]] = {}
        for source, expansions in terms.items():
            if (
                not isinstance(source, str)
                or not source.strip()
                or not isinstance(expansions, list)
                or not expansions
                or not all(isinstance(item, str) and item.strip() for item in expansions)
            ):
                raise ValueError("query expansion table term entry is invalid")
            normalized[source.casefold()] = tuple(dict.fromkeys(item.strip() for item in expansions))
        result[course_id] = normalized
    return result


def build_query_variants(course_id: str, query: str) -> tuple[str, ...]:
    """Return the original query plus at most two deterministic expansions."""

    original = query.strip()
    if not original:
        return ("",)
    terms = load_query_expansions().get(course_id, {})
    variants = [original]
    folded = original.casefold()
    for source, expansions in terms.items():
        if source not in folded:
            continue
        for expansion in expansions:
            if expansion.casefold() in folded:
                continue
            variants.append(f"{original} {expansion}")
            if len(variants) >= MAX_QUERY_VARIANTS:
                return tuple(variants)
    return tuple(variants)
