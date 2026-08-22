"""Course registry integration.

Reads packages/contracts/v1/courses.json (the app's CourseRegistry) so that
adding a new course (e.g. sophomore/junior subjects) requires zero code
changes here: register the course there, then run the converter.

Legacy quirks of the first 10 courses are encoded below:
- manifest source_id prefixes that differ from course_id
- knowledge directory names that differ from course_id
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

# course_id -> source_id prefix overrides (first-batch legacy names)
LEGACY_SOURCE_PREFIX = {
    "engineering_math_analysis_1": "engineering-mathematical-analysis-1",
    "engineering_math_analysis_2": "engineering-mathematical-analysis-2",
    "probability_theory": "probability-theory",
}

# course_id -> knowledge directory overrides
LEGACY_KNOWLEDGE_DIR = {
    "probability_theory": "probability",
}


def repo_root() -> Path:
    """Return the repository root (location-agnostic).

    Walks upward until it finds a directory containing both ``apps`` and
    ``学科资料`` (the SCUT_CS repo layout). Works regardless of where this
    package is installed/moved.
    """
    p = Path(__file__).resolve()
    for anc in p.parents:
        if (anc / "apps").exists() and (anc / "学科资料").exists():
            return anc
    # fallback: nearest ancestor with a .git
    for anc in p.parents:
        if (anc / ".git").exists():
            return anc
    return p.parents[-1]


def courses_json() -> Path:
    return (repo_root() / "apps/scut-senior/packages/contracts/v1/courses.json")


@lru_cache(maxsize=1)
def load_courses() -> dict[str, dict]:
    payload = json.loads(courses_json().read_text(encoding="utf-8"))
    return {c["course_id"]: c for c in payload["courses"]}


def subject_dirs() -> dict[str, str]:
    """course_id -> 学科资料/ folder name, taken from repository_paths."""
    out = {}
    for cid, c in load_courses().items():
        for p in c.get("repository_paths", []):
            if p.startswith("学科资料/"):
                out[cid] = p.split("/", 1)[1]
                break
    return out


def source_prefix(course_id: str) -> str:
    if course_id in LEGACY_SOURCE_PREFIX:
        return LEGACY_SOURCE_PREFIX[course_id]
    return course_id.replace("_", "-")


def knowledge_dir(course_id: str) -> Path:
    """Directory under knowledge/ used by this course (existing wins)."""
    root = repo_root() / "apps/scut-senior/knowledge"
    if course_id in LEGACY_KNOWLEDGE_DIR:
        return root / LEGACY_KNOWLEDGE_DIR[course_id]
    return root / course_id


def folder_to_course_id(folder: str) -> str | None:
    for cid, d in subject_dirs().items():
        if d == folder:
            return cid
    return None


def normalize_course_arg(arg: str | None):
    """Accept a course_id OR a 学科资料/ folder name; return course_id or None."""
    if not arg:
        return None
    if arg in load_courses():
        return arg
    return folder_to_course_id(arg)


TEXT_EXTS = {".docx", ".doc", ".pdf", ".pptx", ".ppt", ".md", ".txt", ".cpp", ".c++"}
IMAGE_ONLY_EXTS = {".png", ".jpg", ".jpeg"}
