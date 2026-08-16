from __future__ import annotations

import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError as JsonSchemaValidationError
from scut_senior_worker.corpus_validator import parse_markdown, validate_corpus

from ..contracts import ExternalResource, WorkflowRunRequest
from ..paths import CONTRACT_ROOT, FIXTURE_ROOT
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
                )
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
        )


class FixtureBilibiliCatalog:
    def __init__(self, path: Path | None = None):
        self.path = path or FIXTURE_ROOT / "bilibili" / "catalog.json"
        schema_path = (
            CONTRACT_ROOT / "schemas" / "bilibili-fixture-catalog.schema.json"
        )
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            Draft202012Validator(schema).validate(payload)
        except (
            OSError,
            json.JSONDecodeError,
            SchemaError,
            JsonSchemaValidationError,
        ) as exc:
            raise FixtureContractViolation(
                f"synthetic Bilibili fixture failed validation: {exc}"
            ) from exc
        self._payload = payload

    @property
    def catalog_version(self) -> str:
        return self._payload.get("catalog_version", "fixture-unknown")

    def match(
        self, course_id: str, query: str, limit: int = 3
    ) -> list[ExternalResource]:
        normalized_query = query.casefold()
        matches: list[ExternalResource] = []
        for item in self._payload.get("resources", []):
            if item.get("course_id") != course_id:
                continue
            if item.get("review_status") != "reviewed":
                continue
            terms = [
                item.get("knowledge_point", ""),
                *item.get("aliases", []),
                *item.get("keywords", []),
            ]
            if terms and not any(
                str(term).casefold() in normalized_query for term in terms if term
            ):
                continue
            matches.append(
                ExternalResource(
                    resource_id=item.get("resource_id"),
                    course_id=course_id,
                    platform="bilibili",
                    resource_type="video",
                    title=item["title"],
                    url=item.get("canonical_url") or item["url"],
                    matched_topic=item.get("knowledge_point", ""),
                    review_status=item["review_status"],
                    catalog_version=self.catalog_version,
                    evidence_role="supplementary_only",
                )
            )
            if len(matches) >= min(max(limit, 0), 3):
                break
        return matches


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
