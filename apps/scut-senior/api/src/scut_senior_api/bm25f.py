"""BM25F lexical ranking for the local-corpus retrieval leg.

PLAN-2 阶段一 步骤 2 replaces the iteration-1 weighted-overlap scorer with a
proper BM25F: an inverted index over the four chunk fields (title / heading /
question / text) with field boosts ``title > heading/question > text`` and k1
saturation. The index is pure Python, built once per course index load, and
queries are deterministic (same input -> same ranking).

Tokenization is the deterministic lexical tokenizer shared with the rest of the
lexical leg: ASCII word tokens plus Chinese bigrams/trigrams.
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Iterable

WORD_RE = re.compile(r"[a-z0-9_]+(?:[+#][a-z0-9_+#]*)?|[\u3400-\u4dbf\u4e00-\u9fff]+")
MAX_QUERY_TERMS = 256
MAX_DOCUMENT_TERMS = 4096

# Field boosts mirror the iteration-1 ×4/×3/×3/×1 intent.
DEFAULT_FIELD_WEIGHTS = {"title": 4.0, "heading": 3.0, "question": 3.0, "text": 1.0}
DEFAULT_K1 = 1.5
DEFAULT_B = 0.75

# Whole-query verbatim hits (formulas, question ids, sentence fragments) keep a
# fixed, small bonus so exact-match recall never regresses behind term-overlap
# noise. It is deliberately a nudge, not the dominant signal: BM25F field
# weighting and IDF carry the ranking, the bonus only breaks near-ties.
EXACT_MATCH_BONUS = 1.0


def term_counts(value: str, *, max_terms: int = MAX_DOCUMENT_TERMS) -> dict[str, int]:
    """Tokenize into ``term -> occurrence count``.

    Identical tokenization to the original deterministic lexical leg, but keeps
    term frequency (BM25F needs it) instead of collapsing to a frozenset.
    """
    normalized = unicodedata.normalize("NFKC", value).casefold()
    counts: dict[str, int] = {}
    for match in WORD_RE.finditer(normalized):
        token = match.group(0)
        if token[0].isascii():
            candidates = (token,)
        elif len(token) == 1:
            candidates = (token,)
        else:
            candidates = tuple(
                token[index : index + width]
                for width in (2, 3)
                if len(token) >= width
                for index in range(len(token) - width + 1)
            )
        for candidate in candidates:
            counts[candidate] = counts.get(candidate, 0) + 1
            if len(counts) > max_terms:
                return counts
    return counts


def _normalized_substring(value: str) -> str:
    return "".join(unicodedata.normalize("NFKC", value).casefold().split())


@dataclass
class _Document:
    chunk_id: str
    fields: dict[str, str]


class BM25FIndex:
    """Deterministic BM25F inverted index over fielded course-chunk documents."""

    def __init__(
        self,
        documents: Iterable[dict[str, str]],
        *,
        k1: float = DEFAULT_K1,
        b: float = DEFAULT_B,
        field_weights: dict[str, float] | None = None,
    ):
        self.k1 = k1
        self.b = b
        self.field_weights = dict(field_weights or DEFAULT_FIELD_WEIGHTS)
        self._docs: list[_Document] = []
        # term -> {doc_index: {field: tf}}
        self._postings: dict[str, dict[int, dict[str, int]]] = defaultdict(dict)
        # doc_index -> {field: term count}
        self._field_term_counts: list[dict[str, dict[str, int]]] = []
        self._field_lengths: list[dict[str, int]] = []
        self._field_total_lengths: dict[str, int] = defaultdict(int)
        self._document_frequency: dict[str, int] = defaultdict(int)

        for raw in documents:
            self._add_document(raw)

        self._doc_count = len(self._docs)
        self._avg_field_lengths = {
            field: (
                self._field_total_lengths[field] / self._doc_count
                if self._doc_count
                else 0.0
            )
            for field in self.field_weights
        }
        self._idf = {
            term: math.log(
                1.0 + (self._doc_count - df + 0.5) / (df + 0.5)
            )
            for term, df in self._document_frequency.items()
        }

    def _add_document(self, raw: dict[str, str]) -> None:
        chunk_id = raw["chunk_id"]
        fields = {
            field: raw.get(field, "") or ""
            for field in self.field_weights
        }
        doc_index = len(self._docs)
        self._docs.append(_Document(chunk_id=chunk_id, fields=fields))
        field_counts: dict[str, dict[str, int]] = {}
        field_lengths: dict[str, int] = {}
        seen_terms: set[str] = set()
        for field, text in fields.items():
            counts = term_counts(text)
            field_counts[field] = counts
            length = sum(counts.values())
            field_lengths[field] = length
            self._field_total_lengths[field] += length
            for term in counts:
                seen_terms.add(term)
        self._field_term_counts.append(field_counts)
        self._field_lengths.append(field_lengths)
        for field, counts in field_counts.items():
            for term, tf in counts.items():
                self._postings[term].setdefault(doc_index, {})[field] = tf
        for term in seen_terms:
            self._document_frequency[term] += 1

    def score(self, query: str) -> list[tuple[float, str]]:
        """Return ``(score, chunk_id)`` for every chunk with score > 0,
        ordered by descending score then ascending chunk_id."""
        query_terms = set(term_counts(query, max_terms=MAX_QUERY_TERMS))
        if not query_terms:
            return []
        normalized_query = _normalized_substring(query)
        scores: dict[int, float] = defaultdict(float)
        for term in query_terms:
            idf = self._idf.get(term)
            if idf is None:
                continue
            for doc_index, field_tfs in self._postings.get(term, {}).items():
                tf_weighted = 0.0
                lengths = self._field_lengths[doc_index]
                for field, weight in self.field_weights.items():
                    tf = field_tfs.get(field, 0)
                    if not tf:
                        continue
                    average = self._avg_field_lengths[field]
                    tf_normalized = tf / (1.0 - self.b + self.b * lengths[field] / average)
                    tf_weighted += weight * tf_normalized
                saturation = tf_weighted / (self.k1 + tf_weighted)
                scores[doc_index] += idf * saturation
        ranked: list[tuple[float, str]] = []
        for doc_index, score in scores.items():
            doc = self._docs[doc_index]
            if normalized_query and any(
                normalized_query in _normalized_substring(doc.fields[field])
                for field in self.field_weights
            ):
                score += EXACT_MATCH_BONUS
            ranked.append((score, doc.chunk_id))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        return ranked
