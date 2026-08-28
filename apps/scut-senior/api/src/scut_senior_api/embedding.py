"""Embedding provider abstraction for the dense retrieval leg.

PLAN-2 阶段一 步骤 3 adds a dense leg on top of the BM25F lexical leg. The
embedding provider is the only part that talks to a model, and it is an
explicit seam so the rest of the pipeline is testable offline and the vendor
choice (§7.2 待确认) stays a configuration concern, not an architecture one.

- ``EmbeddingProvider``: the contract (``model_id`` + ``dimensions`` + ``embed``).
- ``DeterministicHashEmbeddingProvider``: deterministic unit vectors for tests
  and for the disabled-dense-leg fallback. It is explicitly NOT semantic — it
  only exists so the fusion/version-binding machinery can be exercised without
  an API key. Production semantic vectors come from the local ONNX BGE
  provider; this module keeps the provider contract independent from its
  runtime adapter.
"""

from __future__ import annotations

import hashlib
import math
import random
from typing import Protocol, Sequence


class EmbeddingProvider(Protocol):
    model_id: str
    dimensions: int

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class DeterministicHashEmbeddingProvider:
    """Offline deterministic unit vectors, never a semantic model.

    Same text always maps to the same normalized vector; different texts map to
    effectively unrelated vectors. Used to prove the dense-leg plumbing (vector
    store, RRF fusion, version binding) without network or API credentials.
    """

    def __init__(self, dimensions: int = 64):
        if isinstance(dimensions, bool) or not isinstance(dimensions, int) or dimensions < 1:
            raise ValueError("embedding dimensions must be a positive integer")
        self.dimensions = dimensions
        self.model_id = f"deterministic-hash-v1-d{dimensions}"

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        digest = hashlib.blake2b(text.encode("utf-8"), digest_size=8).digest()
        rng = random.Random(int.from_bytes(digest, "big"))
        vector = [rng.uniform(-1.0, 1.0) for _ in range(self.dimensions)]
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0.0:
            return vector
        return [value / norm for value in vector]
