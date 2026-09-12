"""Deterministic final ranking strategies for hybrid retrieval.

``rule_rerank`` is the historical lexical-first strategy.  The opt-in
``protected_rrf_rerank`` keeps only verified structural anchors hard-protected,
then lets lexical and dense candidates compete by weighted reciprocal rank.
"""

from __future__ import annotations

from collections.abc import Collection, Sequence

from .fusion import DEFAULT_RRF_K


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


def protected_rrf_rerank(
    lexical_ranked: Sequence[str],
    dense_ranked: Sequence[str],
    *,
    protected_ids: Collection[str] = (),
    limit: int,
    lexical_weight: float = 1.0,
    dense_weight: float = 0.6,
    k: int = DEFAULT_RRF_K,
) -> list[str]:
    """Keep verified anchors, then rank both retrieval legs with weighted RRF."""

    if limit < 1:
        raise ValueError("protected RRF limit must be positive")
    if k < 1 or lexical_weight < 0 or dense_weight < 0:
        raise ValueError("protected RRF parameters must be non-negative")
    lexical_positions = {
        chunk_id: rank for rank, chunk_id in enumerate(lexical_ranked, 1)
    }
    dense_positions = {
        chunk_id: rank for rank, chunk_id in enumerate(dense_ranked, 1)
    }
    candidates = set(lexical_positions) | set(dense_positions) | set(protected_ids)
    protected = sorted(
        set(protected_ids) & candidates,
        key=lambda chunk_id: (
            min(
                lexical_positions.get(chunk_id, float("inf")),
                dense_positions.get(chunk_id, float("inf")),
            ),
            chunk_id,
        ),
    )
    result = protected[:limit]
    remainder = candidates - set(result)
    scored = []
    for chunk_id in remainder:
        score = 0.0
        if (rank := lexical_positions.get(chunk_id)) is not None:
            score += lexical_weight / (k + rank)
        if (rank := dense_positions.get(chunk_id)) is not None:
            score += dense_weight / (k + rank)
        scored.append((score, chunk_id))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return result + [chunk_id for _, chunk_id in scored[: limit - len(result)]]
