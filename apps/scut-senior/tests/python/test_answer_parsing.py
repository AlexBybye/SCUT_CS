from __future__ import annotations

import json

import pytest

from scut_senior_api.adapters.answer_parsing import parse_chat_completion_answer


def _chat_completion_body(content: str) -> bytes:
    return json.dumps({"choices": [{"message": {"content": content}}]}).encode()


@pytest.mark.parametrize(
    ("content", "expected_answer", "expected_citations"),
    [
        (
            "先写出方程的约束，再逐步消元并检查每一步是否保留等价关系。",
            "先写出方程的约束，再逐步消元并检查每一步是否保留等价关系。",
            (),
        ),
        (
            "```json\n"
            + json.dumps(
                {
                    "answer": "矩阵秩可由主元个数判断。[S2]",
                    "future_extension": {"trace": "must be ignored"},
                },
                ensure_ascii=False,
            )
            + "\n```",
            "矩阵秩可由主元个数判断。[S2]",
            ("S2",),
        ),
    ],
    ids=["plain_text", "fenced_json_with_missing_auxiliary_fields"],
)
def test_parser_accepts_normal_answer_shapes_without_auxiliary_schema_fields(
    content: str,
    expected_answer: str,
    expected_citations: tuple[str, ...],
) -> None:
    answer = parse_chat_completion_answer(_chat_completion_body(content))

    assert answer.repository_answer == expected_answer
    assert answer.citation_ids == expected_citations
    assert answer.related_topics == ()
    assert answer.related_questions == ()
    assert answer.bilibili_search_keywords == ()


def test_parser_ignores_unknown_fields_and_malformed_auxiliary_fields() -> None:
    content = json.dumps(
        {
            "repository_answer": "先求出主元，再判断秩。[S1]",
            "related_topics": "不是列表",
            "related_questions": ["如何验证主元？", 7],
            "bilibili_search_keywords": {"not": "a list"},
            "unknown_provider_diagnostics": {"internal": True},
        },
        ensure_ascii=False,
    )

    answer = parse_chat_completion_answer(_chat_completion_body(content))

    assert answer.repository_answer == "先求出主元，再判断秩。[S1]"
    assert answer.citation_ids == ("S1",)
    assert answer.related_topics == ()
    assert answer.related_questions == ("如何验证主元？",)
    assert answer.bilibili_search_keywords == ()


def test_parser_extracts_and_hides_markdown_bilibili_metadata_sidecar() -> None:
    content = (
        "## 结论\n\n"
        "初等行变换不改变矩阵的秩。[S1]\n\n"
        "<!-- scut-meta: "
        + json.dumps(
            {
                "related_topics": ["初等行变换", "矩阵的秩"],
                "bilibili_search_keywords": ["初等行变换 矩阵的秩"],
            },
            ensure_ascii=False,
        )
        + " -->"
    )

    answer = parse_chat_completion_answer(_chat_completion_body(content))

    assert answer.repository_answer == "## 结论\n\n初等行变换不改变矩阵的秩。[S1]"
    assert answer.citation_ids == ("S1",)
    assert answer.related_topics == ("初等行变换", "矩阵的秩")
    assert answer.bilibili_search_keywords == ("初等行变换 矩阵的秩",)


def test_parser_defers_duplicate_and_unknown_citation_claims_to_the_runtime_guard() -> None:
    content = json.dumps(
        {
            "repository_answer": "模型声明了多个来源。",
            "citation_ids": ["S1", "S1", "S999"],
        },
        ensure_ascii=False,
    )

    answer = parse_chat_completion_answer(_chat_completion_body(content))

    # Parsing only preserves the provider's explicit claims. The request-local
    # citation guard later rejects duplicate IDs and IDs absent from candidates.
    assert answer.citation_ids == ("S1", "S1", "S999")
