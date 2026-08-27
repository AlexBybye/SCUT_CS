from __future__ import annotations

from scut_senior_api.bm25f import BM25FIndex, EXACT_MATCH_BONUS, term_counts


def test_term_counts_emits_chinese_bigrams_and_trigrams_with_frequency() -> None:
    # A 2-char Chinese token yields only its single bigram (no trigram).
    assert term_counts("加密") == {"加密": 1}

    # A 4-char token expands into every bigram and trigram.
    four = term_counts("对称加密")
    assert four["对称"] == 1
    assert four["称加"] == 1
    assert four["加密"] == 1
    assert four["对称加"] == 1
    assert four["称加密"] == 1

    # Term frequency is preserved for repeated occurrences.
    repeated = term_counts("加密加密")
    assert repeated["加密"] == 2


def test_term_counts_keeps_ascii_tokens_whole() -> None:
    counts = term_counts("least privilege")
    assert counts["least"] == 1
    assert counts["privilege"] == 1
    assert "lea" not in counts


def test_bm25f_ranks_rare_terms_above_common_terms() -> None:
    docs = [
        {"chunk_id": "a", "title": "", "heading": "", "question": "", "text": "矩阵的秩 矩阵 矩阵"},
        {"chunk_id": "b", "title": "", "heading": "", "question": "", "text": "矩阵 奇异值分解"},
    ]
    index = BM25FIndex(docs)
    # "奇异值" is rare (one document) while "矩阵" is common (two documents).
    assert index.score("奇异值分解")[0][1] == "b"
    assert index.score("矩阵的秩")[0][1] == "a"


def test_bm25f_field_weights_favor_title_over_text() -> None:
    docs = [
        {
            "chunk_id": "text-only",
            "title": "",
            "heading": "",
            "question": "",
            "text": "the quick brown fox",
        },
        {
            "chunk_id": "title-hit",
            "title": "quick",
            "heading": "",
            "question": "",
            "text": "lorem ipsum",
        },
    ]
    index = BM25FIndex(docs)
    assert index.score("quick")[0][1] == "title-hit"


def test_bm25f_exact_substring_gets_a_bonus() -> None:
    index = BM25FIndex(
        [{"chunk_id": "d", "title": "", "heading": "", "question": "", "text": "xyz abc"}]
    )
    # Base BM25F contribution is non-negative, so the exact-match chunk must
    # clear the fixed bonus on its own.
    score = index.score("xyz")[0][0]
    assert score >= EXACT_MATCH_BONUS


def test_bm25f_is_deterministic() -> None:
    docs = [
        {"chunk_id": "a", "title": "", "heading": "", "question": "", "text": "矩阵 线性方程组"},
        {"chunk_id": "b", "title": "", "heading": "", "question": "", "text": "线性方程组 初等行变换"},
    ]
    index = BM25FIndex(docs)
    assert index.score("线性方程组") == index.score("线性方程组")
