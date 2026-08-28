from scut_senior_api.rule_rerank import rule_rerank


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
