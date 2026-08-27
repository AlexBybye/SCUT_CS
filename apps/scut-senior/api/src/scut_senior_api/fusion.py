"""Reciprocal Rank Fusion for the hybrid (lexical + dense) retrieval leg.

PLAN-2 阶段一 步骤 3 fuses the two legs with RRF(k=60): only ranks are used,
never the raw scores, so BM25F scores and cosine similarities need no
normalization and the ordering stays deterministic (same input -> same output).
"""

from __future__ import annotations

from collections import defaultdict
from typing import Sequence

DEFAULT_RRF_K = 60


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
