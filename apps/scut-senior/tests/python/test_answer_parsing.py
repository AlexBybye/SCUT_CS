from __future__ import annotations

import json

import pytest

from scut_senior_api.adapters.answer_parsing import (
    ModelAnswerParseError,
    parse_chat_completion_answer,
)


def _chat_completion_body(content: object) -> bytes:
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


def test_parser_accepts_multimodal_content_parts_list() -> None:
    body = json.dumps(
        {
            "choices": [
                {
                    "message": {
                        "content": [
                            {"type": "text", "text": "先求主元，"},
                            {"type": "image_url", "image_url": {"url": "ignored"}},
                            {"type": "text", "text": "再判断秩。[S1]"},
                        ]
                    }
                }
            ]
        }
    ).encode()

    answer = parse_chat_completion_answer(body)

    assert answer.repository_answer == "先求主元，再判断秩。[S1]"
    assert answer.citation_ids == ("S1",)


def test_parser_accepts_single_part_content_mapping() -> None:
    body = _chat_completion_body({"type": "text", "text": "答案是 2。[S2]"})

    answer = parse_chat_completion_answer(body)

    assert answer.repository_answer == "答案是 2。[S2]"
    assert answer.citation_ids == ("S2",)


def test_parser_appends_honest_notice_when_output_hits_length_cap() -> None:
    body = json.dumps(
        {
            "choices": [
                {
                    "message": {"content": "## 结论\n\n代入公式 $$P(3;2)=\\frac{"},
                    "finish_reason": "length",
                }
            ]
        }
    ).encode()

    answer = parse_chat_completion_answer(body)

    assert answer.repository_answer.startswith("## 结论\n\n代入公式")
    assert "达到单次输出长度上限" in answer.repository_answer
    assert "被截断" in answer.repository_answer


def test_truncation_notice_stays_before_a_wellformed_scut_meta_sidecar() -> None:
    content = (
        "## 结论\n\n初等行变换不改变矩阵的秩。[S1]\n\n"
        + "<!-- scut-meta: "
        + json.dumps(
            {"related_topics": ["初等行变换"], "bilibili_search_keywords": ["初等行变换"]},
            ensure_ascii=False,
        )
        + " -->"
    )
    body = json.dumps(
        {
            "choices": [
                {"message": {"content": content}, "finish_reason": "length"}
            ]
        }
    ).encode()

    answer = parse_chat_completion_answer(body)

    # 提示插入正文与注释之间；注释仍被正常剥离为结构化元数据。
    assert "达到单次输出长度上限" in answer.repository_answer
    assert "scut-meta" not in answer.repository_answer
    assert answer.related_topics == ("初等行变换",)


def test_parser_ignores_non_length_finish_reasons() -> None:
    body = json.dumps(
        {
            "choices": [
                {"message": {"content": "完整结论。[S1]"}, "finish_reason": "stop"}
            ]
        }
    ).encode()

    answer = parse_chat_completion_answer(body)

    assert answer.repository_answer == "完整结论。[S1]"
    assert "截断" not in answer.repository_answer


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("markdown", "## 结论\n\n行列式按行展开。[S3]"),
        ("output", "直接输出：秩等于主元个数。"),
        ("text", "用 text 键包裹的正文。"),
    ],
)
def test_parser_accepts_common_envelope_keys(key: str, expected: str) -> None:
    answer = parse_chat_completion_answer(_chat_completion_body({key: expected}))

    assert answer.repository_answer == expected


@pytest.mark.parametrize(
    "content",
    [
        None,
        "",
        [],
        [{"type": "image_url", "image_url": {"url": "x"}}],
        {"type": "image_url"},
        {"unknown": "no answer text"},
    ],
)
def test_parser_still_fails_closed_on_unusable_assistant_content(content: object) -> None:
    with pytest.raises(ModelAnswerParseError):
        parse_chat_completion_answer(_chat_completion_body(content))
