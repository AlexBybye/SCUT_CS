from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


APP_ROOT = Path(__file__).resolve().parents[2]
WORKER_SRC = APP_ROOT / "worker" / "src"
if str(WORKER_SRC) not in sys.path:
    sys.path.insert(0, str(WORKER_SRC))

from scut_senior_worker.corpus_validator import (  # noqa: E402
    MANIFEST_HEADERS,
    load_course_registry,
    parse_markdown,
    validate_corpus,
)


CORPUS_ROOT = APP_ROOT / "tests" / "fixtures" / "corpus"
MANIFEST = CORPUS_ROOT / "manifest.csv"


def _write_manifest(
    tmp_path: Path, row: dict[str, str], headers: tuple[str, ...] = MANIFEST_HEADERS
) -> Path:
    manifest = tmp_path / "manifest.csv"
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerow(row)
    return manifest


def _row_for_invalid_fixture(name: str) -> dict[str, str]:
    rows = {
        "locator-non-increasing.md": {
            "source_id": "invalid-locator-order",
            "title": "合成页码倒序负例",
            "original_path": "sources/invalid-locator-order.txt",
            "document_role": "note",
            "year": "",
            "locator_type": "page",
        },
        "slide-non-increasing.md": {
            "source_id": "invalid-slide-order",
            "title": "合成幻灯片重复负例",
            "original_path": "sources/invalid-slide-order.txt",
            "document_role": "slides",
            "year": "",
            "locator_type": "slide",
        },
        "heading-skips-level.md": {
            "source_id": "invalid-heading-jump",
            "title": "合成标题跳级负例",
            "original_path": "sources/invalid-heading-jump.txt",
            "document_role": "note",
            "year": "",
            "locator_type": "heading",
        },
        "question-duplicate.md": {
            "source_id": "invalid-question-duplicate",
            "title": "合成题号重复负例",
            "original_path": "sources/invalid-question-duplicate.txt",
            "document_role": "past_exam",
            "year": "2023",
            "locator_type": "page",
        },
        "frontmatter-missing-title.md": {
            "source_id": "invalid-frontmatter-title",
            "title": "合成缺失标题负例",
            "original_path": "sources/invalid-frontmatter-title.txt",
            "document_role": "note",
            "year": "",
            "locator_type": "heading",
        },
    }
    fixture = rows[name]
    return {
        "source_id": fixture["source_id"],
        "course": "linear_algebra",
        "title": fixture["title"],
        "original_path": fixture["original_path"],
        "format": "txt",
        "document_role": fixture["document_role"],
        "year": fixture["year"],
        "output_md": f"invalid/{name}",
        "locator_type": fixture["locator_type"],
        "method": "synthetic",
        "ocr_used": "false",
        "ocr_confidence": "",
        "ocr_warning": "",
        "status": "passed",
        "reviewer": "fixture-reviewer",
        "notes": "fixture_only",
    }


def test_valid_fixture_only_exposes_passed_source() -> None:
    report = validate_corpus(MANIFEST)

    assert report.errors == []
    assert report.ok
    assert [document["status"] for document in report.documents] == [
        "passed",
        "pending",
    ]
    assert len(report.searchable_sources) == 1
    source = report.searchable_sources[0]
    assert source["source_id"] == "synthetic-linear-algebra-exam"
    assert source["source_title"] == "合成线性代数页码题目"
    assert source["course_id"] == "linear_algebra"
    assert source["locator_type"] == "page"
    assert source["first_page"] == 1
    assert source["first_question"] == "synthetic-2023-A-Q1"
    assert source["first_heading"] == "合成矩阵练习"


def test_parse_markdown_exposes_mock_retrieval_locators() -> None:
    parsed = parse_markdown(
        CORPUS_ROOT / "linear_algebra" / "synthetic-linear-algebra-exam.md"
    )

    assert parsed.pages == (1, 2)
    assert parsed.slides == ()
    assert parsed.questions == (
        "synthetic-2023-A-Q1",
        "synthetic-2023-A-Q2",
    )
    assert [heading.level for heading in parsed.headings] == [1, 2, 3, 2, 3]
    assert parsed.first_locator() == {
        "page": 1,
        "question": "synthetic-2023-A-Q1",
        "heading": "合成矩阵练习",
    }


def test_course_legacy_field_is_compatible_but_pending_is_not_searchable() -> None:
    parsed = parse_markdown(
        CORPUS_ROOT / "linear_algebra" / "synthetic-linear-algebra-pending.md"
    )
    assert parsed.frontmatter["course"] == "线性代数"

    report = validate_corpus(MANIFEST)
    assert all(
        source["source_id"] != "synthetic-linear-algebra-pending"
        for source in report.searchable_sources
    )


def test_course_resolution_is_normalized_exact_not_substring() -> None:
    registry = load_course_registry()

    assert registry.resolve(" 工科数学分析 Ｉ ") == "engineering_math_analysis_1"
    assert registry.resolve("C++程序设计基础") == "cpp"
    assert registry.resolve("大物上实验合辑") is None
    assert registry.resolve("信息安全") == "information_security_intro"
    # 信息安全数学基础已注册为独立课程（2026-08-23 全量注册），不再视为被排除名。
    assert registry.resolve("信息安全数学基础") == "information_security_mathematics"
    assert registry.resolve("线性代数课程") is None
    assert registry.resolve("请讲线性代数") is None


@pytest.mark.parametrize(
    ("fixture_name", "expected_error"),
    [
        ("locator-non-increasing.md", "page locators must be strictly increasing"),
        ("slide-non-increasing.md", "slide locators must be strictly increasing"),
        ("heading-skips-level.md", "heading level jumps from H1 to H3"),
        ("question-duplicate.md", "question locators must be unique"),
        ("frontmatter-missing-title.md", "missing frontmatter fields"),
    ],
)
def test_invalid_markdown_fixtures_fail(
    tmp_path: Path, fixture_name: str, expected_error: str
) -> None:
    manifest = _write_manifest(tmp_path, _row_for_invalid_fixture(fixture_name))

    report = validate_corpus(manifest, knowledge_root=CORPUS_ROOT)

    assert not report.ok
    assert report.searchable_sources == []
    assert any(expected_error in error for error in report.errors)


def test_manifest_headers_and_status_are_exact(tmp_path: Path) -> None:
    valid_row = _row_for_invalid_fixture("locator-non-increasing.md")
    valid_row["status"] = "needs_review"
    manifest = _write_manifest(tmp_path, valid_row)

    report = validate_corpus(manifest, knowledge_root=CORPUS_ROOT)
    assert any("manifest status must be one of" in error for error in report.errors)

    wrong_headers = tuple(reversed(MANIFEST_HEADERS))
    wrong_manifest = _write_manifest(tmp_path, valid_row, wrong_headers)
    wrong_report = validate_corpus(wrong_manifest, knowledge_root=CORPUS_ROOT)
    assert wrong_report.errors == [
        "manifest headers must exactly match: " + ",".join(MANIFEST_HEADERS)
    ]


def test_manifest_rejects_extra_row_columns(tmp_path: Path) -> None:
    row = _row_for_invalid_fixture("locator-non-increasing.md")
    manifest = tmp_path / "manifest.csv"
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(MANIFEST_HEADERS)
        writer.writerow([row[field] for field in MANIFEST_HEADERS] + ["unexpected"])

    report = validate_corpus(manifest, knowledge_root=CORPUS_ROOT)

    assert any("unexpected extra columns" in error for error in report.errors)


def test_manifest_rejects_unknown_locator_type(tmp_path: Path) -> None:
    row = _row_for_invalid_fixture("locator-non-increasing.md")
    row["locator_type"] = "section"
    manifest = _write_manifest(tmp_path, row)

    report = validate_corpus(manifest, knowledge_root=CORPUS_ROOT)

    assert any("locator_type must be page, slide, heading, none, or blank" in error for error in report.errors)


def test_document_role_may_be_present_but_blank(tmp_path: Path) -> None:
    markdown = tmp_path / "blank-document-role.md"
    markdown.write_text(
        """---
source_id: blank-document-role
course_id: linear_algebra
title: 合成未分类资料
original_file: sources/blank-document-role.txt
document_role:
year:
locator_type: heading
---

# 合成未分类资料

这段内容验证资料类型不确定时可以留空。
""",
        encoding="utf-8",
    )
    row = {
        "source_id": "blank-document-role",
        "course": "linear_algebra",
        "title": "合成未分类资料",
        "original_path": "sources/blank-document-role.txt",
        "format": "txt",
        "document_role": "",
        "year": "",
        "output_md": markdown.name,
        "locator_type": "heading",
        "method": "synthetic",
        "ocr_used": "false",
        "ocr_confidence": "",
        "ocr_warning": "",
        "status": "passed",
        "reviewer": "fixture-reviewer",
        "notes": "fixture_only",
    }
    manifest = _write_manifest(tmp_path, row)

    report = validate_corpus(manifest, knowledge_root=tmp_path)

    assert report.errors == []
    assert [source["document_role"] for source in report.searchable_sources] == [""]


def test_passed_source_without_reliable_locator_uses_none(tmp_path: Path) -> None:
    markdown = tmp_path / "no-locator.md"
    markdown.write_text(
        """---
source_id: no-locator
course_id: linear_algebra
title: 合成无定位资料
original_file: sources/no-locator.txt
document_role: note
year:
locator_type: none
---

这段合成内容没有可靠页码、幻灯片、题号或标题定位。
""",
        encoding="utf-8",
    )
    row = {
        "source_id": "no-locator",
        "course": "linear_algebra",
        "title": "合成无定位资料",
        "original_path": "sources/no-locator.txt",
        "format": "txt",
        "document_role": "note",
        "year": "",
        "output_md": markdown.name,
        "locator_type": "none",
        "method": "synthetic",
        "ocr_used": "false",
        "ocr_confidence": "",
        "ocr_warning": "",
        "status": "passed",
        "reviewer": "fixture-reviewer",
        "notes": "fixture_only",
    }
    manifest = _write_manifest(tmp_path, row)

    report = validate_corpus(manifest, knowledge_root=tmp_path)

    assert report.errors == []
    assert report.searchable_sources[0]["locator_type"] == "none"
    assert report.searchable_sources[0]["first_locator"] == {}


@pytest.mark.parametrize("status", ["pending", "passed"])
def test_pending_and_passed_allow_blank_notes(tmp_path: Path, status: str) -> None:
    row = {
        "source_id": "synthetic-linear-algebra-exam",
        "course": "linear_algebra",
        "title": "合成线性代数页码题目",
        "original_path": "sources/linear-algebra-exam.txt",
        "format": "txt",
        "document_role": "past_exam",
        "year": "2023",
        "output_md": "linear_algebra/synthetic-linear-algebra-exam.md",
        "locator_type": "page",
        "method": "synthetic",
        "ocr_used": "false",
        "ocr_confidence": "",
        "ocr_warning": "",
        "status": status,
        "reviewer": "fixture-reviewer" if status == "passed" else "",
        "notes": "",
    }
    manifest = _write_manifest(tmp_path, row)

    report = validate_corpus(manifest, knowledge_root=CORPUS_ROOT)

    assert report.errors == []
    assert len(report.searchable_sources) == (1 if status == "passed" else 0)


def test_image_only_status_is_valid_but_never_searchable(tmp_path: Path) -> None:
    """image_only 是技术性排除态：合法，但绝不进入可检索集合。"""
    row = {
        "source_id": "synthetic-linear-algebra-exam",
        "course": "linear_algebra",
        "title": "合成线性代数页码题目",
        "original_path": "sources/linear-algebra-exam.txt",
        "format": "txt",
        "document_role": "past_exam",
        "year": "2023",
        "output_md": "linear_algebra/synthetic-linear-algebra-exam.md",
        "locator_type": "page",
        "method": "synthetic",
        "ocr_used": "false",
        "ocr_confidence": "",
        "ocr_warning": "",
        "status": "image_only",
        "reviewer": "",
        "notes": "纯图片扫描件无可提取文本层（零chunk）",
    }
    manifest = _write_manifest(tmp_path, row)

    report = validate_corpus(manifest, knowledge_root=CORPUS_ROOT)

    assert report.errors == []
    assert report.searchable_sources == []
    assert [document["status"] for document in report.documents] == ["image_only"]
    assert all(document["valid"] for document in report.documents)


def test_image_only_requires_notes(tmp_path: Path) -> None:
    row = {
        "source_id": "synthetic-linear-algebra-exam",
        "course": "linear_algebra",
        "title": "合成线性代数页码题目",
        "original_path": "sources/linear-algebra-exam.txt",
        "format": "txt",
        "document_role": "past_exam",
        "year": "2023",
        "output_md": "linear_algebra/synthetic-linear-algebra-exam.md",
        "locator_type": "page",
        "method": "synthetic",
        "ocr_used": "false",
        "ocr_confidence": "",
        "ocr_warning": "",
        "status": "image_only",
        "reviewer": "",
        "notes": "",
    }
    manifest = _write_manifest(tmp_path, row)

    report = validate_corpus(manifest, knowledge_root=CORPUS_ROOT)

    assert any("image_only source requires notes" in error for error in report.errors)


@pytest.mark.parametrize("status", ["needs_fix", "rejected"])
def test_needs_fix_and_rejected_require_notes(tmp_path: Path, status: str) -> None:
    row = _row_for_invalid_fixture("locator-non-increasing.md")
    row["status"] = status
    row["notes"] = ""
    manifest = _write_manifest(tmp_path, row)

    report = validate_corpus(manifest, knowledge_root=CORPUS_ROOT)

    assert any(f"{status} source requires notes" in error for error in report.errors)


def test_output_path_cannot_escape_explicit_knowledge_root(tmp_path: Path) -> None:
    row = _row_for_invalid_fixture("locator-non-increasing.md")
    row["output_md"] = "../../学科资料/线性代数/真实资料.md"
    manifest = _write_manifest(tmp_path, row)

    report = validate_corpus(manifest, knowledge_root=CORPUS_ROOT)

    assert report.searchable_sources == []
    assert any("output_md escapes knowledge root" in error for error in report.errors)


def test_cli_outputs_json_and_success() -> None:
    command = [
        sys.executable,
        "-m",
        "scut_senior_worker.corpus_validator",
        "--manifest",
        str(MANIFEST),
        "--pretty",
    ]
    result = subprocess.run(
        command,
        cwd=APP_ROOT,
        env={
            **os.environ,
            "PYTHONPATH": str(WORKER_SRC),
            "SCUT_SENIOR_APP_ROOT": str(APP_ROOT),
        },
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert len(payload["searchable_sources"]) == 1


@pytest.mark.parametrize("blank_year", ["", "null", "none", "NULL", "None"])
def test_manifest_accepts_blank_and_null_literal_years(
    tmp_path: Path, blank_year: str
) -> None:
    row = _row_for_invalid_fixture("locator-non-increasing.md")
    row["year"] = blank_year
    manifest = _write_manifest(tmp_path, row)

    report = validate_corpus(manifest, knowledge_root=CORPUS_ROOT)

    assert not any("year" in error for error in report.errors)


def test_manifest_rejects_non_numeric_year(tmp_path: Path) -> None:
    row = _row_for_invalid_fixture("locator-non-increasing.md")
    row["year"] = "2022级"
    manifest = _write_manifest(tmp_path, row)

    report = validate_corpus(manifest, knowledge_root=CORPUS_ROOT)

    assert any(
        "year must be null, blank, or four digits" in error for error in report.errors
    )


def test_frontmatter_null_year_matches_manifest_null_year(tmp_path: Path) -> None:
    markdown = tmp_path / "null-year.md"
    markdown.write_text(
        """---
source_id: null-year
course_id: linear_algebra
title: 合成年份为空资料
original_file: sources/null-year.txt
document_role: note
year: null
locator_type: heading
---

# 合成年份为空资料

这段内容验证 frontmatter 的 year 为 null 时与 manifest 的 null 一致。
""",
        encoding="utf-8",
    )
    row = {
        "source_id": "null-year",
        "course": "linear_algebra",
        "title": "合成年份为空资料",
        "original_path": "sources/null-year.txt",
        "format": "txt",
        "document_role": "note",
        "year": "null",
        "output_md": markdown.name,
        "locator_type": "heading",
        "method": "synthetic",
        "ocr_used": "false",
        "ocr_confidence": "",
        "ocr_warning": "",
        "status": "passed",
        "reviewer": "fixture-reviewer",
        "notes": "fixture_only",
    }
    manifest = _write_manifest(tmp_path, row)

    report = validate_corpus(manifest, knowledge_root=tmp_path)

    assert report.errors == []
    assert [source["year"] for source in report.searchable_sources] == [None]
