"""Validate the V1 manifest and converted Markdown contract.

The validator only opens Markdown files named by ``output_md`` beneath the
explicit knowledge root. It records ``original_path`` as metadata and never
opens the raw source file, so validation cannot accidentally traverse the real
``学科资料`` tree.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

import yaml


CONTRACT_VERSION = "v1"
MANIFEST_HEADERS = (
    "source_id",
    "course",
    "title",
    "original_path",
    "format",
    "document_role",
    "year",
    "output_md",
    "locator_type",
    "method",
    "ocr_used",
    "ocr_confidence",
    "ocr_warning",
    "status",
    "reviewer",
    "notes",
)
MANIFEST_STATUSES = frozenset({"pending", "passed", "needs_fix", "rejected"})
LOCATOR_TYPES = frozenset({"page", "slide", "heading", "none", ""})
FRONTMATTER_FIELDS = frozenset(
    {
        "source_id",
        "course_id",
        "course",
        "title",
        "original_file",
        "document_role",
        "year",
        "locator_type",
    }
)
FRONTMATTER_REQUIRED = frozenset(
    {"source_id", "title", "original_file", "document_role", "locator_type"}
)

_APP_ROOT = Path(
    os.getenv("SCUT_SENIOR_APP_ROOT", str(Path(__file__).resolve().parents[3]))
).resolve()
DEFAULT_COURSES_PATH = _APP_ROOT / "packages" / "contracts" / "v1" / "courses.json"

_LOCATOR_RE = re.compile(
    r"<!--\s*(page|slide|question)\s*:\s*(.*?)\s*-->", re.IGNORECASE
)
_POSITIVE_INTEGER_RE = re.compile(r"[1-9][0-9]*")
_QUESTION_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]*")
_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)(?:[ \t]+#+)?[ \t]*$")
_FENCE_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})")


class ContractError(ValueError):
    """Raised when a shared contract asset cannot be parsed."""


@dataclass(frozen=True)
class Heading:
    """One Markdown ATX heading outside fenced code."""

    level: int
    text: str
    line_number: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "text": self.text,
            "line_number": self.line_number,
        }


@dataclass(frozen=True)
class ParsedMarkdown:
    """Frontmatter and deterministic locator data parsed from one Markdown file."""

    path: Path
    frontmatter: dict[str, Any]
    body: str
    pages: tuple[int, ...]
    slides: tuple[int, ...]
    questions: tuple[str, ...]
    headings: tuple[Heading, ...]
    syntax_errors: tuple[str, ...] = ()

    @property
    def first_page(self) -> int | None:
        return self.pages[0] if self.pages else None

    @property
    def first_slide(self) -> int | None:
        return self.slides[0] if self.slides else None

    @property
    def first_question(self) -> str | None:
        return self.questions[0] if self.questions else None

    @property
    def first_heading(self) -> str | None:
        return self.headings[0].text if self.headings else None

    def first_locator(self) -> dict[str, Any]:
        """Return the first available locator components for Mock retrieval."""

        locator: dict[str, Any] = {}
        if self.first_page is not None:
            locator["page"] = self.first_page
        if self.first_slide is not None:
            locator["slide"] = self.first_slide
        if self.first_question is not None:
            locator["question"] = self.first_question
        if self.first_heading is not None:
            locator["heading"] = self.first_heading
        return locator


@dataclass
class ValidationReport:
    """Machine-readable result returned by :func:`validate_corpus`."""

    errors: list[str] = field(default_factory=list)
    searchable_sources: list[dict[str, Any]] = field(default_factory=list)
    documents: list[dict[str, Any]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def is_valid(self) -> bool:
        return self.ok

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": CONTRACT_VERSION,
            "ok": self.ok,
            "errors": self.errors,
            "searchable_sources": self.searchable_sources,
            "documents": self.documents,
        }


def normalize_course_name(value: str) -> str:
    """Normalize a course label without broadening it to substring matching."""

    if not isinstance(value, str):
        raise TypeError("course name must be a string")
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return "".join(normalized.split())


class CourseRegistry:
    """Resolve IDs, display names and aliases by normalized exact match."""

    _COURSE_FIELDS = frozenset(
        {
            "course_id",
            "display_name",
            "aliases",
            "repository_paths",
            "is_open",
            "fixture_available",
        }
    )

    def __init__(self, payload: dict[str, Any]):
        if set(payload) != {"contract_version", "courses"}:
            raise ContractError(
                "courses.json must contain exactly contract_version and courses"
            )
        if payload.get("contract_version") != CONTRACT_VERSION:
            raise ContractError("courses.json contract_version must be v1")
        courses = payload.get("courses")
        if not isinstance(courses, list) or not courses:
            raise ContractError("courses.json courses must be a non-empty array")

        self.courses: tuple[dict[str, Any], ...] = tuple(courses)
        self._by_id: dict[str, dict[str, Any]] = {}
        self._normalized_to_id: dict[str, str] = {}

        for index, course in enumerate(courses):
            if not isinstance(course, dict) or set(course) != self._COURSE_FIELDS:
                raise ContractError(f"courses[{index}] has unexpected fields")
            course_id = course.get("course_id")
            display_name = course.get("display_name")
            aliases = course.get("aliases")
            repository_paths = course.get("repository_paths")
            if not isinstance(course_id, str) or not course_id:
                raise ContractError(f"courses[{index}].course_id must be non-empty")
            if course_id in self._by_id:
                raise ContractError(f"duplicate course_id: {course_id}")
            if not isinstance(display_name, str) or not display_name:
                raise ContractError(f"{course_id}.display_name must be non-empty")
            if not isinstance(aliases, list) or not all(
                isinstance(alias, str) and alias for alias in aliases
            ):
                raise ContractError(f"{course_id}.aliases must be strings")
            if not isinstance(repository_paths, list) or not all(
                isinstance(path, str) and path for path in repository_paths
            ):
                raise ContractError(f"{course_id}.repository_paths must be strings")
            if not isinstance(course.get("is_open"), bool) or not isinstance(
                course.get("fixture_available"), bool
            ):
                raise ContractError(f"{course_id} switches must be booleans")

            self._by_id[course_id] = course
            labels = [course_id, display_name, *aliases]
            for label in labels:
                normalized = normalize_course_name(label)
                previous = self._normalized_to_id.get(normalized)
                if previous is not None and previous != course_id:
                    raise ContractError(
                        f"course alias collision: {label!r} maps to {previous} and {course_id}"
                    )
                self._normalized_to_id[normalized] = course_id

    @property
    def course_ids(self) -> tuple[str, ...]:
        return tuple(self._by_id)

    def get(self, course_id: str) -> dict[str, Any] | None:
        return self._by_id.get(course_id)

    def resolve(self, value: str) -> str | None:
        if not isinstance(value, str) or not value.strip():
            return None
        return self._normalized_to_id.get(normalize_course_name(value))


def load_course_registry(path: Path | None = None) -> CourseRegistry:
    registry_path = path or DEFAULT_COURSES_PATH
    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot load course registry {registry_path}: {exc}") from exc
    return CourseRegistry(payload)


def _split_frontmatter(text: str, path: Path) -> tuple[dict[str, Any], str, int]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ContractError(f"{path}: Markdown must start with YAML frontmatter")

    closing_index: int | None = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing_index = index
            break
    if closing_index is None:
        raise ContractError(f"{path}: YAML frontmatter is not closed")

    raw_frontmatter = "\n".join(lines[1:closing_index])
    try:
        payload = yaml.safe_load(raw_frontmatter) or {}
    except yaml.YAMLError as exc:
        raise ContractError(f"{path}: invalid YAML frontmatter: {exc}") from exc
    if not isinstance(payload, dict):
        raise ContractError(f"{path}: YAML frontmatter must be an object")

    body = "\n".join(lines[closing_index + 1 :])
    return payload, body, closing_index + 2


def _scan_markdown_body(
    body: str, body_start_line: int
) -> tuple[
    tuple[int, ...],
    tuple[int, ...],
    tuple[str, ...],
    tuple[Heading, ...],
    tuple[str, ...],
]:
    pages: list[int] = []
    slides: list[int] = []
    questions: list[str] = []
    headings: list[Heading] = []
    errors: list[str] = []
    fence_character: str | None = None
    fence_length = 0

    for offset, line in enumerate(body.splitlines()):
        line_number = body_start_line + offset
        fence = _FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            if fence_character is None:
                fence_character = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_character and len(marker) >= fence_length:
                fence_character = None
                fence_length = 0
            continue
        if fence_character is not None:
            continue

        heading = _HEADING_RE.match(line)
        if heading:
            headings.append(
                Heading(
                    level=len(heading.group(1)),
                    text=heading.group(2).strip(),
                    line_number=line_number,
                )
            )

        for marker in _LOCATOR_RE.finditer(line):
            marker_type = marker.group(1).casefold()
            raw_value = marker.group(2).strip()
            if marker_type in {"page", "slide"}:
                if not _POSITIVE_INTEGER_RE.fullmatch(raw_value):
                    errors.append(
                        f"line {line_number}: {marker_type} must be a positive integer"
                    )
                    continue
                value = int(raw_value)
                (pages if marker_type == "page" else slides).append(value)
            else:
                if not _QUESTION_ID_RE.fullmatch(raw_value):
                    errors.append(
                        f"line {line_number}: question must be a stable non-empty ID"
                    )
                    continue
                questions.append(raw_value)

    return (
        tuple(pages),
        tuple(slides),
        tuple(questions),
        tuple(headings),
        tuple(errors),
    )


def parse_markdown(path: Path) -> ParsedMarkdown:
    """Parse frontmatter and locators without reading any referenced source file."""

    markdown_path = Path(path)
    try:
        text = markdown_path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ContractError(f"cannot read Markdown {markdown_path}: {exc}") from exc
    frontmatter, body, body_start_line = _split_frontmatter(text, markdown_path)
    pages, slides, questions, headings, syntax_errors = _scan_markdown_body(
        body, body_start_line
    )
    return ParsedMarkdown(
        path=markdown_path,
        frontmatter=frontmatter,
        body=body,
        pages=pages,
        slides=slides,
        questions=questions,
        headings=headings,
        syntax_errors=syntax_errors,
    )


def _as_contract_string(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _normalize_optional_year(value: Any) -> str:
    """Normalize an optional year field to a blank string when absent.

    Blank cells and the literal ``null`` / ``none`` markers (some CSV exports
    write them explicitly) all mean "year unknown" and must not fail
    validation or mismatch a frontmatter ``year:`` null.
    """

    text = _as_contract_string(value)
    if text.casefold() in {"", "null", "none"}:
        return ""
    return text


def _strictly_increasing(values: Sequence[int]) -> bool:
    return all(current > previous for previous, current in zip(values, values[1:]))


def _safe_output_path(knowledge_root: Path, relative_path: str) -> Path:
    candidate = (knowledge_root / relative_path).resolve()
    root = knowledge_root.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ContractError(f"output_md escapes knowledge root: {relative_path}") from exc
    return candidate


def _validate_manifest_values(row: dict[str, str], registry: CourseRegistry) -> list[str]:
    source_id = row["source_id"].strip() or "<blank-source-id>"
    errors: list[str] = []
    for field_name in (
        "source_id",
        "course",
        "title",
        "original_path",
        "format",
        "output_md",
        "locator_type",
        "method",
        "ocr_used",
        "status",
    ):
        if not row[field_name].strip():
            errors.append(f"{source_id}: manifest {field_name} must be non-empty")

    if row["status"].strip() not in MANIFEST_STATUSES:
        errors.append(
            f"{source_id}: manifest status must be one of {sorted(MANIFEST_STATUSES)}"
        )
    if row["locator_type"].strip() not in LOCATOR_TYPES:
        errors.append(
            f"{source_id}: locator_type must be page, slide, heading, none, or blank"
        )
    if registry.resolve(row["course"]) is None:
        errors.append(f"{source_id}: unknown course {row['course']!r}")
    if row["ocr_used"].strip().casefold() not in {"true", "false"}:
        errors.append(f"{source_id}: ocr_used must be true or false")
    if row["ocr_warning"].strip().casefold() not in {"", "true", "false"}:
        errors.append(f"{source_id}: ocr_warning must be blank, true, or false")
    if row["ocr_confidence"].strip():
        try:
            confidence = float(row["ocr_confidence"])
        except ValueError:
            errors.append(f"{source_id}: ocr_confidence must be numeric")
        else:
            if not 0 <= confidence <= 1:
                errors.append(f"{source_id}: ocr_confidence must be between 0 and 1")
    year_text = _normalize_optional_year(row["year"])
    if year_text and not re.fullmatch(r"[0-9]{4}", year_text):
        errors.append(f"{source_id}: year must be null, blank, or four digits")
    if row["status"].strip() == "passed" and not row["reviewer"].strip():
        errors.append(f"{source_id}: passed source requires reviewer")
    if row["status"].strip() in {"needs_fix", "rejected"} and not row["notes"].strip():
        errors.append(
            f"{source_id}: {row['status'].strip()} source requires notes"
        )
    return errors


def _resolve_frontmatter_course(
    source_id: str, frontmatter: dict[str, Any], registry: CourseRegistry
) -> tuple[str | None, list[str]]:
    errors: list[str] = []
    preferred = _as_contract_string(frontmatter.get("course_id"))
    legacy = _as_contract_string(frontmatter.get("course"))

    if preferred:
        resolved = preferred if registry.get(preferred) is not None else None
        if resolved is None:
            errors.append(f"{source_id}: unknown frontmatter course_id {preferred!r}")
        if legacy:
            legacy_resolved = registry.resolve(legacy)
            if legacy_resolved is None:
                errors.append(f"{source_id}: unknown frontmatter course {legacy!r}")
            elif resolved is not None and legacy_resolved != resolved:
                errors.append(
                    f"{source_id}: frontmatter course_id and course resolve differently"
                )
        return resolved, errors

    if legacy:
        resolved = registry.resolve(legacy)
        if resolved is None:
            errors.append(f"{source_id}: unknown frontmatter course {legacy!r}")
        return resolved, errors

    errors.append(f"{source_id}: frontmatter requires course_id or compatible course")
    return None, errors


def _validate_frontmatter(
    row: dict[str, str], parsed: ParsedMarkdown, registry: CourseRegistry
) -> tuple[str | None, list[str]]:
    source_id = row["source_id"].strip() or "<blank-source-id>"
    frontmatter = parsed.frontmatter
    errors: list[str] = []

    unknown_fields = sorted(set(frontmatter) - FRONTMATTER_FIELDS)
    if unknown_fields:
        errors.append(f"{source_id}: unknown frontmatter fields: {unknown_fields}")
    missing_fields = sorted(
        field_name
        for field_name in FRONTMATTER_REQUIRED
        if field_name not in frontmatter
        or (
            field_name != "document_role"
            and not _as_contract_string(frontmatter.get(field_name))
        )
    )
    if missing_fields:
        errors.append(f"{source_id}: missing frontmatter fields: {missing_fields}")

    resolved_course, course_errors = _resolve_frontmatter_course(
        source_id, frontmatter, registry
    )
    errors.extend(course_errors)
    manifest_course = registry.resolve(row["course"])
    if (
        manifest_course is not None
        and resolved_course is not None
        and manifest_course != resolved_course
    ):
        errors.append(f"{source_id}: frontmatter course does not match manifest course")

    exact_pairs = (
        ("source_id", "source_id"),
        ("title", "title"),
        ("original_file", "original_path"),
        ("document_role", "document_role"),
        ("year", "year"),
        ("locator_type", "locator_type"),
    )
    for frontmatter_field, manifest_field in exact_pairs:
        front_value = _as_contract_string(frontmatter.get(frontmatter_field))
        manifest_value = row[manifest_field].strip()
        if frontmatter_field == "year":
            front_value = _normalize_optional_year(front_value)
            manifest_value = _normalize_optional_year(manifest_value)
        if front_value != manifest_value:
            errors.append(
                f"{source_id}: frontmatter {frontmatter_field} does not match manifest {manifest_field}"
            )
    return resolved_course, errors


def _validate_locators(row: dict[str, str], parsed: ParsedMarkdown) -> list[str]:
    source_id = row["source_id"].strip() or "<blank-source-id>"
    errors = [f"{source_id}: {error}" for error in parsed.syntax_errors]

    if not _strictly_increasing(parsed.pages):
        errors.append(f"{source_id}: page locators must be strictly increasing")
    if not _strictly_increasing(parsed.slides):
        errors.append(f"{source_id}: slide locators must be strictly increasing")

    seen_questions: set[str] = set()
    duplicate_questions: set[str] = set()
    for question in parsed.questions:
        if question in seen_questions:
            duplicate_questions.add(question)
        seen_questions.add(question)
    if duplicate_questions:
        errors.append(
            f"{source_id}: question locators must be unique: {sorted(duplicate_questions)}"
        )

    for previous, current in zip(parsed.headings, parsed.headings[1:]):
        if current.level > previous.level + 1:
            errors.append(
                f"{source_id}: heading level jumps from H{previous.level} to H{current.level} at line {current.line_number}"
            )

    locator_type = row["locator_type"].strip()
    if locator_type == "page":
        if not parsed.pages:
            errors.append(f"{source_id}: locator_type page requires page markers")
        if parsed.slides:
            errors.append(f"{source_id}: page document cannot contain slide markers")
    elif locator_type == "slide":
        if not parsed.slides:
            errors.append(f"{source_id}: locator_type slide requires slide markers")
        if parsed.pages:
            errors.append(f"{source_id}: slide document cannot contain page markers")
    elif locator_type == "heading":
        if not parsed.headings:
            errors.append(f"{source_id}: locator_type heading requires a heading")
        if parsed.pages or parsed.slides:
            errors.append(
                f"{source_id}: heading document cannot contain page or slide markers"
            )
    elif locator_type in {"", "none"} and (parsed.pages or parsed.slides):
        errors.append(
            f"{source_id}: document with locator_type none cannot contain page or slide markers"
        )
    return errors


def _source_record(
    row: dict[str, str], course_id: str, parsed: ParsedMarkdown
) -> dict[str, Any]:
    return {
        "source_id": row["source_id"].strip(),
        "source_title": row["title"].strip(),
        "course_id": course_id,
        "output_md": row["output_md"].strip(),
        "locator_type": row["locator_type"].strip() or "none",
        "document_role": row["document_role"].strip(),
        "year": _normalize_optional_year(row["year"]) or None,
        "first_page": parsed.first_page,
        "first_slide": parsed.first_slide,
        "first_question": parsed.first_question,
        "first_heading": parsed.first_heading,
        "first_locator": parsed.first_locator(),
    }


def validate_corpus(
    manifest_path: Path, knowledge_root: Path | None = None
) -> ValidationReport:
    """Validate a manifest and return only valid ``passed`` searchable sources.

    ``knowledge_root`` defaults to the manifest's parent directory. The function
    never reads ``original_path``; only ``output_md`` beneath this root is opened.
    """

    manifest = Path(manifest_path)
    root = Path(knowledge_root) if knowledge_root is not None else manifest.parent
    report = ValidationReport()

    try:
        registry = load_course_registry()
    except ContractError as exc:
        report.errors.append(str(exc))
        return report

    try:
        manifest_file = manifest.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        report.errors.append(f"cannot read manifest {manifest}: {exc}")
        return report

    with manifest_file:
        reader = csv.DictReader(manifest_file)
        if tuple(reader.fieldnames or ()) != MANIFEST_HEADERS:
            report.errors.append(
                "manifest headers must exactly match: " + ",".join(MANIFEST_HEADERS)
            )
            return report
        rows = list(reader)

    seen_source_ids: set[str] = set()
    seen_output_paths: set[str] = set()

    for row_number, raw_row in enumerate(rows, start=2):
        row = {key: (value or "") for key, value in raw_row.items() if key is not None}
        source_id = row["source_id"].strip() or f"<row-{row_number}>"
        row_errors = _validate_manifest_values(row, registry)
        if raw_row.get(None) is not None:
            row_errors.append(
                f"{source_id}: manifest row {row_number} has unexpected extra columns"
            )

        if source_id in seen_source_ids:
            row_errors.append(f"{source_id}: duplicate source_id")
        seen_source_ids.add(source_id)
        output_md = row["output_md"].strip()
        if output_md in seen_output_paths:
            row_errors.append(f"{source_id}: duplicate output_md {output_md!r}")
        seen_output_paths.add(output_md)

        try:
            markdown_path = _safe_output_path(root, output_md)
        except ContractError as exc:
            row_errors.append(f"{source_id}: {exc}")
            report.errors.extend(row_errors)
            continue
        if markdown_path.suffix.casefold() != ".md":
            row_errors.append(f"{source_id}: output_md must end in .md")

        try:
            parsed = parse_markdown(markdown_path)
        except ContractError as exc:
            row_errors.append(f"{source_id}: {exc}")
            report.errors.extend(row_errors)
            continue

        resolved_course, frontmatter_errors = _validate_frontmatter(
            row, parsed, registry
        )
        row_errors.extend(frontmatter_errors)
        row_errors.extend(_validate_locators(row, parsed))

        document = {
            "source_id": source_id,
            "status": row["status"].strip(),
            "output_md": output_md,
            "valid": not row_errors,
        }
        report.documents.append(document)
        report.errors.extend(row_errors)

        if not row_errors and row["status"].strip() == "passed":
            assert resolved_course is not None
            report.searchable_sources.append(
                _source_record(row, resolved_course, parsed)
            )

    return report


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument(
        "--knowledge-root",
        type=Path,
        default=None,
        help="Root used to resolve output_md (defaults to the manifest directory)",
    )
    parser.add_argument("--pretty", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _build_argument_parser().parse_args(list(argv) if argv is not None else None)
    report = validate_corpus(args.manifest, args.knowledge_root)
    json.dump(
        report.to_dict(),
        sys.stdout,
        ensure_ascii=False,
        indent=2 if args.pretty else None,
        sort_keys=True,
    )
    sys.stdout.write("\n")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
