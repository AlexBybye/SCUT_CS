from scut_senior_api.rule_rerank import protected_rrf_rerank, rule_rerank


def test_rule_rerank_preserves_lexical_priority_and_exact_protection() -> None:
    assert rule_rerank(
        ["lexical-2", "exact", "lexical-3"],
        ["dense-only", "exact"],
        protected_ids={"exact"},
        limit=3,
    ) == ["exact", "lexical-2", "lexical-3"]


def test_rule_rerank_uses_dense_only_for_empty_lexical_slots() -> None:
    assert rule_rerank(["lexical"], ["dense", "lexical"], limit=3) == [
        "lexical",
        "dense",
    ]


def test_protected_rrf_allows_a_high_rank_dense_only_candidate_into_a_full_pool() -> None:
    lexical = [f"lexical-{index:02d}" for index in range(1, 51)]

    ranked = protected_rrf_rerank(lexical, ["dense-only"], limit=50)

    assert "dense-only" in ranked
    assert "lexical-50" not in ranked


def test_protected_rrf_keeps_verified_anchors_ahead_of_fused_candidates() -> None:
    assert protected_rrf_rerank(
        ["lexical", "anchor"],
        ["dense", "anchor"],
        protected_ids={"anchor"},
        limit=2,
    ) == ["anchor", "lexical"]
