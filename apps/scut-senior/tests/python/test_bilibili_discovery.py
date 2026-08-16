from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import parse_qs, urlsplit

import pytest

from scut_senior_api.adapters.bilibili import (
    MAX_KEYWORD_LENGTH,
    BilibiliLinkDiscoveryAdapter,
    normalize_keywords,
)


def test_keywords_use_nfkc_remove_controls_collapse_space_dedupe_and_cap() -> None:
    long_keyword = "长" * (MAX_KEYWORD_LENGTH + 10)

    normalized = normalize_keywords(
        [
            "  矩阵\x00\n  的秩  ",
            "ＭＡＴＲＩＸ",
            "matrix",
            long_keyword,
            "不会进入第四项",
        ]
    )

    assert normalized == (
        "矩阵 的秩",
        "MATRIX",
        "长" * MAX_KEYWORD_LENGTH,
    )


def test_non_string_and_control_only_keywords_are_ignored() -> None:
    normalized = normalize_keywords(["\x00\u200b", 42, None, "秩"])  # type: ignore[list-item]

    assert normalized == ("秩",)


def test_valid_keywords_always_produce_one_anonymous_live_search_link() -> None:
    generated_at = datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc)
    resources = BilibiliLinkDiscoveryAdapter(clock=lambda: generated_at).discover(
        course_id="linear_algebra",
        course_title="  线性\x00 代数 ",
        keywords=["矩阵的秩", "线性无关"],
    )

    assert len(resources) == 1
    resource = resources[0]
    assert resource.resource_id is None
    assert resource.course_id == "linear_algebra"
    assert resource.platform == "bilibili"
    assert resource.resource_type == "search"
    assert resource.review_status == "unreviewed_live_search"
    assert resource.catalog_version is None
    assert resource.evidence_role == "supplementary_only"
    assert resource.matched_topic == "矩阵的秩、线性无关"
    assert resource.query_keywords == ["矩阵的秩", "线性无关"]
    assert resource.generated_at == generated_at

    parsed = urlsplit(str(resource.url))
    assert parsed.scheme == "https"
    assert parsed.hostname == "search.bilibili.com"
    assert parsed.path == "/all"
    assert parsed.fragment == ""
    assert parse_qs(parsed.query) == {"keyword": ["矩阵的秩 线性无关"]}


def test_url_encoding_prevents_keyword_or_course_title_injection() -> None:
    resources = BilibiliLinkDiscoveryAdapter().discover(
        course_id="linear_algebra",
        course_title="线性代数&order=click",
        keywords=[
            "秩&duration=4#fragment",
            "https://evil.example/x?keyword=pwned",
        ],
    )

    parsed = urlsplit(str(resources[-1].url))
    query = parse_qs(parsed.query)
    assert parsed.scheme == "https"
    assert parsed.netloc == "search.bilibili.com"
    assert parsed.path == "/all"
    assert parsed.fragment == ""
    assert set(query) == {"keyword"}
    assert query["keyword"] == [
        "秩&duration=4#fragment https://evil.example/x?keyword=p"
    ]


def test_empty_normalized_keywords_return_nothing() -> None:
    resources = BilibiliLinkDiscoveryAdapter().discover(
        course_id="linear_algebra",
        course_title="线性代数",
        keywords=["", "\x00", "  \n  "],
    )

    assert resources == []


@pytest.mark.parametrize(
    ("course_id", "course_title"),
    [("\x00", "线性代数"), ("linear_algebra", "\u200b")],
)
def test_required_course_fields_cannot_normalize_to_empty(
    course_id: str, course_title: str
) -> None:
    with pytest.raises(ValueError, match="must remain non-empty"):
        BilibiliLinkDiscoveryAdapter().discover(
            course_id=course_id,
            course_title=course_title,
            keywords=["矩阵的秩"],
        )
