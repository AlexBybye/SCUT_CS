"""Reciprocal Rank Fusion for the hybrid (lexical + dense) retrieval leg.

PLAN-2 阶段一 步骤 3 fuses the two legs with RRF(k=60): only ranks are used,
never the raw scores, so BM25F scores and cosine similarities need no
normalization and the ordering stays deterministic (same input -> same output).
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Collection
from typing import Sequence

DEFAULT_RRF_K = 60
DEFAULT_LEXICAL_WEIGHT = 1.0
DEFAULT_DENSE_WEIGHT = 0.85


def reciprocal_rank_fusion(
    ranked_lists: Sequence[Sequence[str]],
    *,
    k: int = DEFAULT_RRF_K,
    top_n: int,
) -> list[str]:
    """Fuse ranked chunk-id lists into one deterministic top-N list.

    Each list contributes ``1 / (k + rank)`` per chunk (rank is 1-based). Ties
    break on ascending chunk_id for stability.
    """
    if k < 1:
        raise ValueError("rrf k must be >= 1")
    if top_n < 0:
        raise ValueError("rrf top_n must be >= 0")
    scores: dict[str, float] = defaultdict(float)
    for ranking in ranked_lists:
        for rank, chunk_id in enumerate(ranking, start=1):
            scores[chunk_id] += 1.0 / (k + rank)
    ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return [chunk_id for chunk_id, _ in ordered[:top_n]]


def weighted_reciprocal_rank_fusion(
    ranked_lists: Sequence[Sequence[str]],
    *,
    weights: Sequence[float],
    k: int = DEFAULT_RRF_K,
    top_n: int,
) -> list[str]:
    """Fuse ranked lists while retaining a fixed, auditable leg preference.

    Sparse and dense scores are not directly comparable.  Weighting their RRF
    contributions, rather than raw scores, lets the lexical leg remain the
    slightly stronger default for course titles, years and question numbers
    while allowing dense-only candidates to compete for the head of the list.
    """
    if len(ranked_lists) != len(weights):
        raise ValueError("ranked_lists and weights must have the same length")
    if k < 1:
        raise ValueError("rrf k must be >= 1")
    if top_n < 0:
        raise ValueError("top_n must be >= 0")
    if any(weight <= 0 for weight in weights):
        raise ValueError("RRF weights must be positive")

    scores: dict[str, float] = defaultdict(float)
    for weight, ranking in zip(weights, ranked_lists, strict=True):
        for rank, chunk_id in enumerate(ranking, start=1):
            scores[chunk_id] += weight / (k + rank)
    ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return [chunk_id for chunk_id, _ in ordered[:top_n]]


def rank_hybrid_candidates(
    lexical_ranked: Sequence[str],
    dense_ranked: Sequence[str],
    *,
    protected_ids: Collection[str] = (),
    limit: int,
    lexical_weight: float = DEFAULT_LEXICAL_WEIGHT,
    dense_weight: float = DEFAULT_DENSE_WEIGHT,
) -> list[str]:
    """Return a cross-leg ranking with exact lexical matches kept at the head.

    Only explicit exact-match IDs are protected.  Every other sparse and dense
    candidate participates in weighted RRF, replacing the old behaviour where
    dense results could only fill slots left empty by lexical retrieval.
    """
    if limit < 1:
        raise ValueError("limit must be positive")
    protected = set(protected_ids)
    result: list[str] = []
    seen: set[str] = set()
    for chunk_id in lexical_ranked:
        if chunk_id in protected and chunk_id not in seen:
            result.append(chunk_id)
            seen.add(chunk_id)
            if len(result) == limit:
                return result
    fused = weighted_reciprocal_rank_fusion(
        [lexical_ranked, dense_ranked],
        weights=[lexical_weight, dense_weight],
        top_n=limit + len(protected),
    )
    for chunk_id in fused:
        if chunk_id not in seen:
            result.append(chunk_id)
            seen.add(chunk_id)
            if len(result) == limit:
                break
    return result
