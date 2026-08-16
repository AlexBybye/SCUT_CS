from __future__ import annotations

import re
from pathlib import Path

from scut_senior_worker.corpus_validator import parse_markdown, validate_corpus

from ..contracts import WorkflowRunRequest
from ..paths import FIXTURE_ROOT
from ..ports import GeneratedAnswer, RetrievedSource, UserIdentity
from ..registry import CourseRegistry


class MockIdentityProvider:
    def current_user(self) -> UserIdentity:
        return UserIdentity(
            user_id="mock-user-iteration-0",
            display_name="Iteration 0 Mock User",
            is_mock=True,
        )


class FixtureContractViolation(RuntimeError):
    pass


class FixtureRetrievalGateway:
    """Reads only synthetic passed fixtures; it never scans real course materials."""

    def __init__(
        self,
        registry: CourseRegistry,
        knowledge_root: Path | None = None,
    ):
        self.registry = registry
        self.knowledge_root = knowledge_root or FIXTURE_ROOT / "corpus"
        self.manifest_path = self.knowledge_root / "manifest.csv"

    def search(self, course_ids: list[str], query: str) -> list[RetrievedSource]:
        del query  # Iteration 0 proves filtering/contracts, not retrieval quality.
        if not self.manifest_path.exists():
            return []
        report = validate_corpus(self.manifest_path, self.knowledge_root)
        if report.errors:
            raise FixtureContractViolation(
                "synthetic corpus fixture failed validation: " + "; ".join(report.errors)
            )
        results: list[RetrievedSource] = []
        for record in report.searchable_sources:
            course_id = record["course_id"]
            if course_id not in course_ids:
                continue
            markdown_path = self.knowledge_root / record["output_md"]
            parsed = parse_markdown(markdown_path)
            results.append(_source_from_validated_fixture(parsed.body, record, parsed))
        return results[:5]


class MockModelGateway:
    provider_id = "mock"
    model_id = "deterministic-fixture-v1"

    def generate(
        self, request: WorkflowRunRequest, sources: list[RetrievedSource]
    ) -> GeneratedAnswer:
        if not sources:
            return GeneratedAnswer(
                repository_answer=(
                    "迭代 0 Mock 未找到可用的 passed Fixture。"
                    "这只表示契约测试资料不足，不代表真实课程资料结论。"
                ),
                bilibili_search_keywords=("矩阵的秩", "初等行变换"),
            )
        source = sources[0]
        preview = re.sub(r"\s+", " ", source.text).strip()[:180]
        answer = (
            "这是迭代 0 的确定性 Mock 回答，仅用于验证契约、来源与持久化链路。\n\n"
            f"已从合成 Fixture《{source.source_title}》读取：{preview}\n\n"
            f"本次结构化输入类型为 `{request.workflow_type.value}`；"
            "尚未调用真实模型，也未运行生产检索。"
        )
        return GeneratedAnswer(
            repository_answer=answer,
            related_topics=("矩阵", "线性方程组"),
            related_questions=("如何判断矩阵的秩？",),
            bilibili_search_keywords=("矩阵的秩", "初等行变换"),
        )


def _source_from_validated_fixture(body: str, record: dict[str, object], parsed) -> RetrievedSource:
    headings = [heading.text for heading in parsed.headings]
    locator_type = str(record["locator_type"] or "heading")
    locator_start: int | str | None
    if locator_type == "page":
        locator_start = record.get("first_page")
    elif locator_type == "slide":
        locator_start = record.get("first_slide")
    elif locator_type == "heading" and headings:
        locator_start = headings[0]
    else:
        locator_start = None
    text = re.sub(r"<!--.*?-->", " ", body, flags=re.DOTALL)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE).strip()
    source_id = str(record["source_id"])
    ordinal = "c01"
    locator_token = (
        f"p{locator_start}"
        if locator_type == "page"
        else f"s{locator_start}"
        if locator_type == "slide"
        else "heading"
    )
    return RetrievedSource(
        chunk_id=f"{source_id}:{locator_token}:{ordinal}",
        course_id=str(record["course_id"]),
        source_id=source_id,
        source_title=str(record["source_title"]),
        text=text,
        locator_type=locator_type,
        locator_start=locator_start,
        locator_end=locator_start,
        question_id=(
            str(record["first_question"])
            if locator_type != "none" and record.get("first_question") is not None
            else None
        ),
        heading_path=tuple(headings[:3]) if locator_type != "none" else (),
    )
