"""Deterministic final ranking guard for hybrid retrieval.

Dense retrieval is a supplement only. Lexical candidates always retain
priority, and exact BM25F matches from the original query are protected at the
front of the result. Dense candidates fill unused slots instead of replacing
the lexical answer.
"""

from __future__ import annotations

from collections.abc import Collection, Sequence


def rule_rerank(
    lexical_ranked: Sequence[str],
    dense_ranked: Sequence[str],
    *,
    protected_ids: Collection[str] = (),
    limit: int,
) -> list[str]:
    if limit < 1:
        raise ValueError("rule rerank limit must be positive")
    protected = set(protected_ids)
    result: list[str] = []
    seen: set[str] = set()
    for chunk_id in lexical_ranked:
        if chunk_id in protected and chunk_id not in seen:
            result.append(chunk_id)
            seen.add(chunk_id)
    for chunk_id in lexical_ranked:
        if chunk_id not in seen:
            result.append(chunk_id)
            seen.add(chunk_id)
    for chunk_id in dense_ranked:
        if len(result) >= limit:
            break
        if chunk_id not in seen:
            result.append(chunk_id)
            seen.add(chunk_id)
    return result[:limit]
