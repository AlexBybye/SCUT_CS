from __future__ import annotations

from scut_senior_api.query_variants import build_query_variants


def test_query_variants_keep_original_and_expand_in_table_order() -> None:
    assert build_query_variants(
        "information_security_intro", "如何理解对称加密和密钥管理"
    ) == (
        "如何理解对称加密和密钥管理",
        "如何理解对称加密和密钥管理 symmetric encryption",
        "如何理解对称加密和密钥管理 key management",
    )


def test_query_variants_are_bounded_and_course_scoped() -> None:
    variants = build_query_variants(
        "information_security_intro", "访问控制、对称加密、密钥管理"
    )
    assert len(variants) == 3
    assert variants[0] == "访问控制、对称加密、密钥管理"
    assert build_query_variants("unknown_course", "对称加密") == ("对称加密",)


def test_query_variants_do_not_duplicate_existing_expansion() -> None:
    assert build_query_variants(
        "information_security_intro", "对称加密 symmetric encryption"
    ) == ("对称加密 symmetric encryption",)
