from scut_senior_api.ports import RetrievedSource
from scut_senior_api.retrieval_anchors import find_exact_anchor_matches


def _source(
    chunk_id: str, *, question_id: str | None = None, title: str = "Notes", heading: str = "Topic"
) -> RetrievedSource:
    return RetrievedSource(
        chunk_id=chunk_id,
        course_id="course-a",
        source_id="source-a",
        source_title=title,
        text="content",
        locator_type="heading",
        locator_start=1,
        locator_end=1,
        question_id=question_id,
        heading_path=(heading,),
    )


def test_unique_question_number_is_a_protected_anchor() -> None:
    matches = find_exact_anchor_matches(
        "请讲解第 3 题", [_source("q3", question_id="2024-A-Q3")]
    )
    assert [(match.chunk_id, match.kind) for match in matches] == [("q3", "question")]


def test_ambiguous_question_number_is_not_hard_protected() -> None:
    matches = find_exact_anchor_matches(
        "第3题怎么做",
        [
            _source("paper-a-q3", question_id="2023-A-Q3"),
            _source("paper-b-q3", question_id="2024-B-Q3"),
        ],
    )
    assert matches == ()


def test_full_specific_heading_is_protected_but_generic_heading_is_not() -> None:
    title = find_exact_anchor_matches(
        "Access Control", [_source("access", heading="Access Control")]
    )
    generic = find_exact_anchor_matches("绪论", [_source("intro", heading="绪论")])

    assert [(match.chunk_id, match.kind) for match in title] == [("access", "title")]
    assert generic == ()
