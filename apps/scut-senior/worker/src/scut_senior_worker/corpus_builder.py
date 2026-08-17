"""Build and operate immutable, review-gated course corpus artifacts.

The builder deliberately reads only ``passed`` Markdown named by the manifest.
It never opens ``original_path``.  A candidate is written to a temporary
directory, validated, and renamed into place; activation is a separate atomic
pointer update so a failed build cannot replace the active corpus.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import uuid
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence
from urllib.parse import unquote, urlsplit

from .corpus_validator import (
    CONTRACT_VERSION,
    MANIFEST_HEADERS,
    _FENCE_RE,
    _HEADING_RE,
    _LOCATOR_RE,
    _normalize_optional_year,
    _safe_output_path,
    _validate_frontmatter,
    _validate_locators,
    _validate_manifest_values,
    load_course_registry,
    parse_markdown,
)


BUILDER_VERSION = "0.2.0"
LOCATOR_CONTRACT_VERSION = "locator-v1"
CANDIDATE_SCHEMA_VERSION = "corpus-candidate-v1"
COURSE_INDEX_SCHEMA_VERSION = "course-index-v1"
COURSE_PACK_SCHEMA_VERSION = "course-pack-v1"
ACTIVE_SCHEMA_VERSION = "corpus-active-v1"

_COMMIT_RE = re.compile(r"[0-9a-f]{40}")
_VERSION_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_IMAGE_RE = re.compile(
    r"!\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\)"
)


class CorpusBuildError(ValueError):
    """Raised when a candidate or store operation cannot fail closed."""


@dataclass(frozen=True)
class BuildResult:
    corpus_version: str
    candidate_path: Path
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": True,
            "corpus_version": self.corpus_version,
            "candidate_path": str(self.candidate_path),
            "metadata": self.metadata,
        }


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CorpusBuildError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CorpusBuildError(f"JSON root must be an object: {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{uuid.uuid4().hex}")
    try:
        _write_json(temporary, payload)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _require_commit(value: str) -> str:
    if not isinstance(value, str):
        raise CorpusBuildError("source_commit must be a string")
    normalized = value.strip().casefold()
    if not _COMMIT_RE.fullmatch(normalized):
        raise CorpusBuildError("source_commit must be a full 40-character Git commit")
    return normalized


def _require_version(value: str, field: str = "version") -> str:
    if not isinstance(value, str):
        raise CorpusBuildError(f"{field} must be a string")
    normalized = value.strip()
    if not _VERSION_RE.fullmatch(normalized):
        raise CorpusBuildError(
            f"{field} must contain only letters, digits, dot, underscore, and hyphen"
        )
    return normalized


def derive_corpus_version(
    source_commit: str,
    *,
    max_chunk_chars: int,
    workflow_version: str,
    outline_version: str,
) -> str:
    """Return a readable version bound to all deterministic build inputs."""

    commit = _require_commit(source_commit)
    workflow = _require_version(workflow_version, "workflow_version")
    outline = _require_version(outline_version, "outline_version")
    if max_chunk_chars < 200:
        raise CorpusBuildError("max_chunk_chars must be at least 200")
    builder = BUILDER_VERSION.replace(".", "_")
    return (
        f"corpus-{commit[:12]}-b{builder}-m{max_chunk_chars}"
        f"-w{workflow}-o{outline}"
    )


def _verify_fixed_checkout(
    repository_root: Path,
    source_commit: str,
    knowledge_root: Path,
    manifest_path: Path,
) -> None:
    root = repository_root.resolve()
    expected_knowledge_root = root / "knowledge"
    if knowledge_root.resolve() != expected_knowledge_root:
        raise CorpusBuildError("knowledge_root must be <repository-root>/knowledge")
    if manifest_path.resolve() != expected_knowledge_root / "manifest.csv":
        raise CorpusBuildError(
            "manifest must be <repository-root>/knowledge/manifest.csv"
        )
    try:
        head = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "status",
                "--porcelain",
                "--untracked-files=all",
                "--",
                "knowledge",
                "apps/scut-senior/worker",
                "apps/scut-senior/packages/contracts/v1",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CorpusBuildError(f"cannot verify fixed Git checkout: {exc}") from exc
    if head.casefold() != source_commit:
        raise CorpusBuildError(
            f"checkout HEAD {head} does not match source_commit {source_commit}"
        )
    if status:
        raise CorpusBuildError(
            "candidate inputs have tracked or untracked changes; build from a clean fixed commit"
        )


def _verify_commit_on_trusted_master(
    repository_root: Path, source_commit: str, trusted_master_ref: str
) -> tuple[str, str]:
    """Prove that ``source_commit`` is already reachable from a named master ref."""

    root = repository_root.resolve()
    commit = _require_commit(source_commit)
    requested_ref = trusted_master_ref.strip()
    if not requested_ref or requested_ref != trusted_master_ref:
        raise CorpusBuildError("trusted_master_ref must be a non-empty Git ref")
    try:
        canonical_ref = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "rev-parse",
                "--symbolic-full-name",
                "--verify",
                requested_ref,
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if not (
            canonical_ref == "refs/heads/master"
            or (
                canonical_ref.startswith("refs/remotes/")
                and canonical_ref.endswith("/master")
            )
        ):
            raise CorpusBuildError(
                "trusted_master_ref must resolve to a local or remote master branch"
            )
        master_commit = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "rev-parse",
                "--verify",
                f"{canonical_ref}^{{commit}}",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip().casefold()
        ancestry = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "merge-base",
                "--is-ancestor",
                commit,
                master_commit,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except CorpusBuildError:
        raise
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CorpusBuildError(f"cannot verify trusted master history: {exc}") from exc
    if ancestry.returncode == 1:
        raise CorpusBuildError(
            f"source_commit {commit} is not merged into trusted master ref {canonical_ref}"
        )
    if ancestry.returncode != 0:
        detail = ancestry.stderr.strip() or "git merge-base failed"
        raise CorpusBuildError(f"cannot verify trusted master ancestry: {detail}")
    return canonical_ref, _require_commit(master_commit)


def _safe_relative_path(root: Path, path: Path, label: str) -> str:
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise CorpusBuildError(f"{label} escapes knowledge root: {path}") from exc
    return relative.as_posix()


def _extract_assets(text: str, markdown_path: Path, knowledge_root: Path) -> list[str]:
    assets: set[str] = set()
    for match in _IMAGE_RE.finditer(text):
        raw_target = unquote((match.group(1) or match.group(2)).strip())
        parsed_target = urlsplit(raw_target)
        if parsed_target.scheme or parsed_target.netloc or raw_target.startswith("#"):
            raise CorpusBuildError(
                "passed Markdown image assets must be repository-local files"
            )
        asset_path = (markdown_path.parent / parsed_target.path).resolve()
        relative = _safe_relative_path(knowledge_root, asset_path, "asset")
        if not asset_path.is_file():
            raise CorpusBuildError(
                f"{relative}: referenced Markdown asset does not exist or is not a file"
            )
        assets.add(relative)
    return sorted(assets)


def _slug(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip().casefold()
    value = re.sub(r"[^\w.-]+", "-", value, flags=re.UNICODE).strip("-._")
    return value or "untitled"


def _split_plain_block(block: str, max_chars: int) -> list[str]:
    pieces: list[str] = []
    remaining = block.strip()
    while len(remaining) > max_chars:
        cut = max_chars
        for delimiter in ("\n", "。", "！", "？", "；", "，", " "):
            candidate = remaining.rfind(delimiter, 0, max_chars + 1)
            if candidate >= max_chars // 2:
                cut = candidate + len(delimiter)
                break
        piece = remaining[:cut].strip()
        if not piece:
            piece = remaining[:max_chars]
            cut = max_chars
        pieces.append(piece)
        remaining = remaining[cut:].strip()
    if remaining:
        pieces.append(remaining)
    return pieces


def _is_intact_fenced_block(text: str) -> bool:
    lines = text.strip().splitlines()
    if len(lines) < 2:
        return False
    opening = _FENCE_RE.match(lines[0])
    closing = _FENCE_RE.match(lines[-1])
    if opening is None or closing is None:
        return False
    opening_marker = opening.group(1)
    closing_marker = closing.group(1)
    return (
        opening_marker[0] == closing_marker[0]
        and len(closing_marker) >= len(opening_marker)
    )


def _split_long_text(text: str, max_chars: int) -> list[str]:
    """Hard-limit prose chunks; keep one complete fenced block as an exception."""

    lines = text.strip().splitlines()
    if not lines:
        return []
    blocks: list[tuple[str, bool]] = []
    current: list[str] = []
    fence_character: str | None = None
    fence_length = 0

    def flush(*, fenced: bool = False) -> None:
        nonlocal current
        block = "\n".join(current).strip()
        current = []
        if block:
            blocks.append((block, fenced))

    for line in lines:
        fence = _FENCE_RE.match(line)
        if fence_character is None and fence:
            flush()
            marker = fence.group(1)
            fence_character = marker[0]
            fence_length = len(marker)
            current.append(line)
            continue
        if fence_character is not None:
            current.append(line)
            if fence:
                marker = fence.group(1)
                if marker[0] == fence_character and len(marker) >= fence_length:
                    flush(fenced=True)
                    fence_character = None
                    fence_length = 0
            continue
        if not line.strip():
            flush()
            continue
        current.append(line)
    if fence_character is not None:
        raise CorpusBuildError("Markdown contains an unclosed fenced code block")
    flush()

    chunks: list[str] = []
    packed = ""
    for block, fenced in blocks:
        if fenced:
            if packed:
                chunks.append(packed)
                packed = ""
            chunks.append(block)
            continue
        for piece in _split_plain_block(block, max_chars):
            proposed = piece if not packed else f"{packed}\n\n{piece}"
            if packed and len(proposed) > max_chars:
                chunks.append(packed)
                packed = piece
            else:
                packed = proposed
    if packed:
        chunks.append(packed)
    return chunks


def _locator_payload(
    page: int | None,
    slide: int | None,
    heading_path: Sequence[str],
) -> tuple[str, int | None, int | None]:
    if page is not None:
        return "page", page, page
    if slide is not None:
        return "slide", slide, slide
    if heading_path:
        return "heading", None, None
    return "none", None, None


def _locator_key(
    page: int | None,
    slide: int | None,
    question: str | None,
    heading_path: Sequence[str],
) -> str:
    components: list[str] = []
    if page is not None:
        components.append(f"p{page}")
    if slide is not None:
        components.append(f"s{slide}")
    if question is not None:
        components.append(f"q-{_slug(question)}")
    if not components and heading_path:
        components.append("h-" + "~".join(_slug(item) for item in heading_path))
    return ":".join(components) or "root"


def _chunk_document(
    *,
    parsed: Any,
    source: dict[str, Any],
    markdown_path: Path,
    knowledge_root: Path,
    max_chunk_chars: int,
) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    ordinals: defaultdict[str, int] = defaultdict(int)
    heading_stack: list[str] = []
    current_page: int | None = None
    current_slide: int | None = None
    current_question: str | None = None
    buffer: list[str] = []
    fence_character: str | None = None
    fence_length = 0

    def emit() -> None:
        nonlocal buffer
        text = "\n".join(buffer).strip()
        buffer = []
        if not text:
            return
        locator_type, locator_start, locator_end = _locator_payload(
            current_page, current_slide, heading_stack
        )
        locator_key = _locator_key(
            current_page, current_slide, current_question, heading_stack
        )
        for piece in _split_long_text(text, max_chunk_chars):
            ordinals[locator_key] += 1
            chunk_id = (
                f"{source['source_id']}:{locator_key}:c{ordinals[locator_key]:02d}"
            )
            chunks.append(
                {
                    "assets": _extract_assets(piece, markdown_path, knowledge_root),
                    "chunk_id": chunk_id,
                    "course_id": source["course_id"],
                    "heading_path": list(heading_stack),
                    "locator_end": locator_end,
                    "locator_start": locator_start,
                    "locator_type": locator_type,
                    "question_id": current_question,
                    "source_id": source["source_id"],
                    "source_title": source["source_title"],
                    "text": piece,
                }
            )

    for line in parsed.body.splitlines():
        fence = _FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            if fence_character is None:
                fence_character = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_character and len(marker) >= fence_length:
                fence_character = None
                fence_length = 0
            buffer.append(line)
            continue
        if fence_character is not None:
            buffer.append(line)
            continue

        markers = list(_LOCATOR_RE.finditer(line))
        if markers:
            emit()
            for marker in markers:
                marker_type = marker.group(1).casefold()
                raw_value = marker.group(2).strip()
                if marker_type == "page":
                    current_page = int(raw_value)
                elif marker_type == "slide":
                    current_slide = int(raw_value)
                else:
                    current_question = raw_value
            remainder = _LOCATOR_RE.sub("", line).strip()
            if remainder:
                buffer.append(remainder)
            continue

        heading = _HEADING_RE.match(line)
        if heading:
            emit()
            level = len(heading.group(1))
            title = heading.group(2).strip()
            heading_stack[:] = heading_stack[: level - 1]
            heading_stack.append(title)
            continue
        buffer.append(line)
    emit()
    return chunks


def _manifest_rows(
    manifest_path: Path, knowledge_root: Path, courses_path: Path
) -> list[tuple[dict[str, str], Any, dict[str, Any], Path, list[str]]]:
    """Validate manifest metadata and open only passed Markdown/assets."""

    registry = load_course_registry(courses_path)
    try:
        handle = manifest_path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise CorpusBuildError(f"cannot read manifest {manifest_path}: {exc}") from exc
    with handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != MANIFEST_HEADERS:
            raise CorpusBuildError(
                "manifest headers must exactly match: " + ",".join(MANIFEST_HEADERS)
            )
        raw_rows = list(reader)

    errors: list[str] = []
    seen_ids: set[str] = set()
    seen_outputs: set[str] = set()
    passed: list[tuple[dict[str, str], Any, dict[str, Any], Path, list[str]]] = []
    for row_number, raw_row in enumerate(raw_rows, start=2):
        row = {key: (value or "") for key, value in raw_row.items() if key is not None}
        source_id = row["source_id"].strip() or f"<row-{row_number}>"
        row_errors = _validate_manifest_values(row, registry)
        if raw_row.get(None) is not None:
            row_errors.append(f"{source_id}: manifest row has unexpected extra columns")
        if source_id in seen_ids:
            row_errors.append(f"{source_id}: duplicate source_id")
        seen_ids.add(source_id)
        output_md = row["output_md"].strip()
        if output_md in seen_outputs:
            row_errors.append(f"{source_id}: duplicate output_md {output_md!r}")
        seen_outputs.add(output_md)
        if row["status"].strip() != "passed":
            errors.extend(row_errors)
            continue

        try:
            markdown_path = _safe_output_path(knowledge_root, output_md)
            if markdown_path.suffix.casefold() != ".md":
                row_errors.append(f"{source_id}: output_md must end in .md")
            parsed = parse_markdown(markdown_path)
            course_id, frontmatter_errors = _validate_frontmatter(
                row, parsed, registry
            )
            row_errors.extend(frontmatter_errors)
            row_errors.extend(_validate_locators(row, parsed))
            assets = _extract_assets(parsed.body, markdown_path, knowledge_root)
        except (ValueError, OSError) as exc:
            row_errors.append(f"{source_id}: {exc}")
            course_id = None
            parsed = None
            markdown_path = knowledge_root
            assets = []
        errors.extend(row_errors)
        if not row_errors:
            assert course_id is not None and parsed is not None
            source = {
                "course_id": course_id,
                "document_role": row["document_role"].strip(),
                "locator_type": row["locator_type"].strip() or "none",
                "output_md": output_md,
                "source_id": source_id,
                "source_title": row["title"].strip(),
                "year": _normalize_optional_year(row["year"]) or None,
            }
            passed.append((row, parsed, source, markdown_path, assets))
    if errors:
        raise CorpusBuildError("candidate input validation failed:\n- " + "\n- ".join(errors))
    if not passed:
        raise CorpusBuildError("manifest contains no valid passed Markdown sources")
    return passed


def _question_index(chunks: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for chunk in chunks:
        if chunk["question_id"] is not None:
            grouped[(chunk["source_id"], chunk["question_id"])].append(chunk)
    records: list[dict[str, Any]] = []
    for (source_id, question_id), members in sorted(grouped.items()):
        numeric = [
            member["locator_start"]
            for member in members
            if isinstance(member["locator_start"], int)
        ]
        first = members[0]
        records.append(
            {
                "chunk_ids": [member["chunk_id"] for member in members],
                "heading_path": first["heading_path"],
                "locator_end": max(numeric) if numeric else None,
                "locator_start": min(numeric) if numeric else None,
                "locator_type": first["locator_type"],
                "question_id": question_id,
                "source_id": source_id,
                "source_title": first["source_title"],
            }
        )
    return records


def _heading_index(chunks: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for chunk in chunks:
        if chunk["heading_path"]:
            grouped[tuple(chunk["heading_path"])].append(chunk)
    return [
        {
            "chunk_ids": [member["chunk_id"] for member in members],
            "heading_path": list(path),
            "source_ids": sorted({member["source_id"] for member in members}),
        }
        for path, members in sorted(grouped.items())
    ]


def _candidate_directory(store_root: Path, corpus_version: str) -> Path:
    version = _require_version(corpus_version, "corpus_version")
    candidates = (store_root / "candidates").resolve()
    candidate = (candidates / version).resolve()
    try:
        candidate.relative_to(candidates)
    except ValueError as exc:
        raise CorpusBuildError("candidate path escapes store") from exc
    return candidate


def _artifact_asset_is_valid(candidate: Path, value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        return False
    if relative.parts[0] != "assets":
        return False
    asset = candidate / relative
    try:
        asset.resolve().relative_to(candidate.resolve())
    except ValueError:
        return False
    return asset.is_file() and not asset.is_symlink()


def build_candidate(
    *,
    manifest_path: Path,
    knowledge_root: Path,
    store_root: Path,
    source_commit: str,
    repository_root: Path,
    max_chunk_chars: int = 1200,
    workflow_version: str = "workflow-contract-v1",
    outline_version: str = "outline-none-v1",
) -> BuildResult:
    """Build one validated immutable candidate without activating it."""

    commit = _require_commit(source_commit)
    workflow = _require_version(workflow_version, "workflow_version")
    outline = _require_version(outline_version, "outline_version")
    root = knowledge_root.resolve()
    manifest = manifest_path.resolve()
    _safe_relative_path(root, manifest, "manifest")
    _verify_fixed_checkout(repository_root, commit, root, manifest)
    passed = _manifest_rows(
        manifest,
        root,
        repository_root.resolve()
        / "apps"
        / "scut-senior"
        / "packages"
        / "contracts"
        / "v1"
        / "courses.json",
    )
    corpus_version = derive_corpus_version(
        commit,
        max_chunk_chars=max_chunk_chars,
        workflow_version=workflow,
        outline_version=outline,
    )
    final_path = _candidate_directory(store_root.resolve(), corpus_version)
    if final_path.exists():
        raise CorpusBuildError(f"immutable candidate already exists: {final_path}")
    final_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = final_path.parent / f".{corpus_version}.tmp-{uuid.uuid4().hex}"

    all_chunks: list[dict[str, Any]] = []
    sources_by_course: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    chunks_by_course: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    read_paths = {_safe_relative_path(root, manifest, "manifest")}
    try:
        temporary.mkdir(parents=False, exist_ok=False)
        for _row, parsed, source, markdown_path, assets in passed:
            source_chunks = _chunk_document(
                parsed=parsed,
                source=source,
                markdown_path=markdown_path,
                knowledge_root=root,
                max_chunk_chars=max_chunk_chars,
            )
            if not source_chunks:
                raise CorpusBuildError(
                    f"{source['source_id']}: passed source produced no searchable chunks"
                )
            artifact_assets = [f"assets/{asset}" for asset in assets]
            for asset, artifact_asset in zip(assets, artifact_assets):
                destination = temporary / artifact_asset
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / asset, destination)
            for chunk in source_chunks:
                chunk["assets"] = [
                    f"assets/{asset}" for asset in chunk["assets"]
                ]
            source_record = {
                **source,
                "assets": artifact_assets,
                "chunk_ids": [chunk["chunk_id"] for chunk in source_chunks],
            }
            sources_by_course[source["course_id"]].append(source_record)
            chunks_by_course[source["course_id"]].extend(source_chunks)
            all_chunks.extend(source_chunks)
            read_paths.add(_safe_relative_path(root, markdown_path, "Markdown"))
            read_paths.update(assets)

        pack_versions: dict[str, str] = {}
        for course_id in sorted(chunks_by_course):
            chunks = chunks_by_course[course_id]
            sources = sorted(
                sources_by_course[course_id], key=lambda item: item["source_id"]
            )
            questions = _question_index(chunks)
            index_payload = {
                "chunks": chunks,
                "corpus_version": corpus_version,
                "course_id": course_id,
                "questions": questions,
                "schema_version": COURSE_INDEX_SCHEMA_VERSION,
                "source_commit": commit,
            }
            _write_json(temporary / "courses" / f"{course_id}.json", index_payload)

            pack_version = (
                f"course-pack-{course_id}-{commit[:12]}-b"
                f"{BUILDER_VERSION.replace('.', '_')}-w{workflow}-o{outline}"
            )
            pack_versions[course_id] = pack_version
            pack_payload = {
                "corpus_version": corpus_version,
                "course_id": course_id,
                "course_pack_version": pack_version,
                "heading_index": _heading_index(chunks),
                "outline_version": outline,
                "questions": questions,
                "schema_version": COURSE_PACK_SCHEMA_VERSION,
                "source_commit": commit,
                "sources": sources,
                "statistics": {
                    "chunk_count": len(chunks),
                    "question_count": len(questions),
                    "source_count": len(sources),
                },
                "workflow_version": workflow,
            }
            _write_json(
                temporary / "course-packs" / f"{course_id}.json", pack_payload
            )

        metadata = {
            "available_courses": sorted(chunks_by_course),
            "builder_version": BUILDER_VERSION,
            "build_parameters": {"max_chunk_chars": max_chunk_chars},
            "checkout_verified": True,
            "chunk_count": len(all_chunks),
            "corpus_version": corpus_version,
            "course_pack_versions": pack_versions,
            "locator_contract_version": LOCATOR_CONTRACT_VERSION,
            "manifest_contract_version": CONTRACT_VERSION,
            "manifest_path": _safe_relative_path(root, manifest, "manifest"),
            "outline_version": outline,
            "oversize_fenced_chunk_count": sum(
                1 for chunk in all_chunks if len(chunk["text"]) > max_chunk_chars
            ),
            "read_paths": sorted(read_paths),
            "schema_version": CANDIDATE_SCHEMA_VERSION,
            "source_commit": commit,
            "source_count": len(passed),
            "status": "validated",
            "workflow_version": workflow,
        }
        _write_json(temporary / "metadata.json", metadata)
        validation = validate_candidate(temporary)
        _write_json(temporary / "validation.json", validation)
        temporary.rename(final_path)
        return BuildResult(corpus_version, final_path, metadata)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def _validate_candidate_payload(candidate_path: Path) -> dict[str, Any]:
    """Validate generated references and version bindings before activation."""

    candidate = candidate_path.resolve()
    metadata = _read_json(candidate / "metadata.json")
    errors: list[str] = []
    required_metadata = {
        "available_courses",
        "builder_version",
        "build_parameters",
        "checkout_verified",
        "chunk_count",
        "corpus_version",
        "course_pack_versions",
        "locator_contract_version",
        "manifest_contract_version",
        "manifest_path",
        "outline_version",
        "oversize_fenced_chunk_count",
        "read_paths",
        "schema_version",
        "source_commit",
        "source_count",
        "status",
        "workflow_version",
    }
    if set(metadata) != required_metadata:
        errors.append("metadata fields do not match candidate-v1 contract")
    if metadata.get("schema_version") != CANDIDATE_SCHEMA_VERSION:
        errors.append("candidate schema_version is invalid")
    if metadata.get("status") != "validated":
        errors.append("candidate status must be validated")
    if metadata.get("checkout_verified") is not True:
        errors.append("candidate fixed checkout was not verified")
    corpus_version = metadata.get("corpus_version")
    try:
        _require_commit(metadata.get("source_commit", ""))
        normalized_version = _require_version(corpus_version, "corpus_version")
    except CorpusBuildError as exc:
        errors.append(str(exc))
        normalized_version = None
    if normalized_version is not None:
        temporary_name = re.fullmatch(
            rf"\.{re.escape(normalized_version)}\.tmp-[0-9a-f]{{32}}",
            candidate.name,
        )
        if candidate.name != normalized_version and temporary_name is None:
            errors.append("candidate directory name does not match corpus_version")

    courses = metadata.get("available_courses")
    if (
        not isinstance(courses, list)
        or not courses
        or not all(isinstance(course, str) for course in courses)
        or courses != sorted(set(courses))
    ):
        errors.append("available_courses must be a sorted non-empty unique list")
        courses = []
    else:
        for course in courses:
            try:
                if _require_version(course, "course_id") != course:
                    errors.append(f"invalid course_id: {course!r}")
            except CorpusBuildError as exc:
                errors.append(str(exc))

    course_pack_versions = metadata.get("course_pack_versions")
    if not isinstance(course_pack_versions, dict):
        errors.append("course_pack_versions must be an object")
        course_pack_versions = {}
    elif set(course_pack_versions) != set(courses) or not all(
        isinstance(value, str) and bool(_VERSION_RE.fullmatch(value))
        for value in course_pack_versions.values()
    ):
        errors.append("course_pack_versions must bind every available course")
    read_paths = metadata.get("read_paths")
    if not isinstance(read_paths, list) or not read_paths:
        errors.append("read_paths must be non-empty")
    else:
        for item in read_paths:
            if (
                not isinstance(item, str)
                or not item
                or Path(item).is_absolute()
                or ".." in Path(item).parts
                or item.startswith("学科资料/")
            ):
                errors.append(f"unsafe build read_path: {item!r}")

    build_parameters = metadata.get("build_parameters")
    max_chunk_chars = (
        build_parameters.get("max_chunk_chars")
        if isinstance(build_parameters, dict)
        else None
    )
    if (
        not isinstance(build_parameters, dict)
        or set(build_parameters) != {"max_chunk_chars"}
        or isinstance(max_chunk_chars, bool)
        or not isinstance(max_chunk_chars, int)
        or max_chunk_chars < 200
    ):
        errors.append("build_parameters.max_chunk_chars must be an integer >= 200")
        max_chunk_chars = 200

    seen_chunks: set[str] = set()
    counted_sources: set[str] = set()
    referenced_assets: set[str] = set()
    oversize_fenced_chunk_count = 0
    for course_id in courses:
        try:
            _require_version(course_id, "course_id")
            index = _read_json(candidate / "courses" / f"{course_id}.json")
            pack = _read_json(candidate / "course-packs" / f"{course_id}.json")
        except CorpusBuildError as exc:
            errors.append(str(exc))
            continue
        if index.get("schema_version") != COURSE_INDEX_SCHEMA_VERSION:
            errors.append(f"{course_id}: invalid course index schema")
        for field in ("corpus_version", "source_commit", "course_id"):
            if index.get(field) != metadata.get(field, course_id if field == "course_id" else None):
                expected = course_id if field == "course_id" else metadata.get(field)
                if index.get(field) != expected:
                    errors.append(f"{course_id}: index {field} version binding mismatch")
        if pack.get("schema_version") != COURSE_PACK_SCHEMA_VERSION:
            errors.append(f"{course_id}: invalid course pack schema")
        expected_pack = course_pack_versions.get(course_id)
        bindings = {
            "corpus_version": metadata.get("corpus_version"),
            "course_id": course_id,
            "course_pack_version": expected_pack,
            "outline_version": metadata.get("outline_version"),
            "source_commit": metadata.get("source_commit"),
            "workflow_version": metadata.get("workflow_version"),
        }
        for field, expected in bindings.items():
            if pack.get(field) != expected:
                errors.append(f"{course_id}: course pack {field} binding mismatch")

        sources = pack.get("sources")
        source_map: dict[str, dict[str, Any]] = {}
        if not isinstance(sources, list) or not sources:
            errors.append(f"{course_id}: course pack sources must be non-empty")
            sources = []
        for source in sources:
            if not isinstance(source, dict):
                errors.append(f"{course_id}: invalid source record")
                continue
            required_source_fields = {
                "assets",
                "chunk_ids",
                "course_id",
                "document_role",
                "locator_type",
                "output_md",
                "source_id",
                "source_title",
                "year",
            }
            if set(source) != required_source_fields:
                errors.append(f"{course_id}: source fields do not match course-pack-v1")
            source_id = source.get("source_id")
            if not isinstance(source_id, str) or not source_id or source_id in source_map:
                errors.append(f"{course_id}: duplicate or invalid source_id")
                continue
            if source.get("course_id") != course_id:
                errors.append(f"{source_id}: source course mismatch")
            source_assets = source.get("assets")
            if not isinstance(source_assets, list) or not all(
                _artifact_asset_is_valid(candidate, asset) for asset in source_assets
            ):
                errors.append(f"{source_id}: invalid or missing copied asset")
                source_assets = []
            referenced_assets.update(source_assets)
            source_map[source_id] = source
            counted_sources.add(source_id)

        chunks = index.get("chunks")
        if not isinstance(chunks, list) or not chunks:
            errors.append(f"{course_id}: chunks must be non-empty")
            chunks = []
        course_chunk_ids: set[str] = set()
        required_chunk_fields = {
            "assets",
            "chunk_id",
            "course_id",
            "heading_path",
            "locator_end",
            "locator_start",
            "locator_type",
            "question_id",
            "source_id",
            "source_title",
            "text",
        }
        for chunk in chunks:
            if not isinstance(chunk, dict) or set(chunk) != required_chunk_fields:
                errors.append(f"{course_id}: chunk fields do not match course-index-v1")
                continue
            chunk_id = chunk["chunk_id"]
            if not isinstance(chunk_id, str) or not chunk_id or chunk_id in seen_chunks:
                errors.append(f"{course_id}: duplicate or invalid chunk_id {chunk_id!r}")
                continue
            seen_chunks.add(chunk_id)
            course_chunk_ids.add(chunk_id)
            source = source_map.get(chunk["source_id"])
            if source is None:
                errors.append(f"{chunk_id}: source_id is absent from course pack")
            elif source.get("source_title") != chunk["source_title"]:
                errors.append(f"{chunk_id}: source_title mismatch")
            if chunk["course_id"] != course_id:
                errors.append(f"{chunk_id}: cross-course chunk")
            if not isinstance(chunk["text"], str) or not chunk["text"].strip():
                errors.append(f"{chunk_id}: text must be non-empty")
            elif len(chunk["text"]) > max_chunk_chars:
                if _is_intact_fenced_block(chunk["text"]):
                    oversize_fenced_chunk_count += 1
                else:
                    errors.append(
                        f"{chunk_id}: prose exceeds max_chunk_chars={max_chunk_chars}"
                    )
            if not isinstance(chunk["heading_path"], list) or not all(
                isinstance(item, str) and item for item in chunk["heading_path"]
            ):
                errors.append(f"{chunk_id}: invalid heading_path")
            locator_type = chunk["locator_type"]
            if locator_type in {"page", "slide"}:
                if not (
                    isinstance(chunk["locator_start"], int)
                    and chunk["locator_start"] > 0
                    and isinstance(chunk["locator_end"], int)
                    and chunk["locator_end"] >= chunk["locator_start"]
                ):
                    errors.append(f"{chunk_id}: invalid numeric locator")
            elif locator_type == "heading":
                if chunk["locator_start"] is not None or chunk["locator_end"] is not None or not chunk["heading_path"]:
                    errors.append(f"{chunk_id}: invalid heading locator")
            elif locator_type == "none":
                if chunk["locator_start"] is not None or chunk["locator_end"] is not None:
                    errors.append(f"{chunk_id}: none locator must not invent a position")
            else:
                errors.append(f"{chunk_id}: unsupported locator_type")
            if not isinstance(chunk["assets"], list) or not all(
                _artifact_asset_is_valid(candidate, asset) for asset in chunk["assets"]
            ):
                errors.append(f"{chunk_id}: invalid or missing copied asset")
            elif source is not None and not set(chunk["assets"]) <= set(
                source.get("assets", [])
            ):
                errors.append(f"{chunk_id}: asset is absent from source payload")
            else:
                referenced_assets.update(chunk["assets"])
        for source_id, source in source_map.items():
            expected = source.get("chunk_ids")
            actual = [
                chunk["chunk_id"]
                for chunk in chunks
                if isinstance(chunk, dict) and chunk.get("source_id") == source_id
            ]
            if expected != actual:
                errors.append(f"{source_id}: source chunk_ids mismatch")

        questions = index.get("questions")
        if questions != pack.get("questions") or not isinstance(questions, list):
            errors.append(f"{course_id}: question index and course pack differ")
        else:
            for question in questions:
                if not isinstance(question, dict) or not set(question.get("chunk_ids", [])) <= course_chunk_ids:
                    errors.append(f"{course_id}: question references unknown chunks")

    if metadata.get("chunk_count") != len(seen_chunks):
        errors.append("metadata chunk_count mismatch")
    if metadata.get("source_count") != len(counted_sources):
        errors.append("metadata source_count mismatch")
    if metadata.get("oversize_fenced_chunk_count") != oversize_fenced_chunk_count:
        errors.append("metadata oversize_fenced_chunk_count mismatch")
    copied_assets = {
        path.relative_to(candidate).as_posix()
        for path in (candidate / "assets").rglob("*")
        if path.is_file() and not path.is_symlink()
    } if (candidate / "assets").is_dir() else set()
    if copied_assets != referenced_assets:
        errors.append("candidate copied assets do not match referenced assets")
    if errors:
        raise CorpusBuildError("candidate validation failed:\n- " + "\n- ".join(errors))
    return {
        "chunk_count": len(seen_chunks),
        "course_count": len(courses),
        "ok": True,
        "schema_version": CANDIDATE_SCHEMA_VERSION,
        "source_count": len(counted_sources),
    }


def validate_candidate(candidate_path: Path) -> dict[str, Any]:
    """Fail closed for both contract errors and malformed nested JSON values."""

    try:
        return _validate_candidate_payload(candidate_path)
    except CorpusBuildError:
        raise
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as exc:
        raise CorpusBuildError(
            f"candidate validation failed closed for malformed artifact: {exc}"
        ) from exc


def _active_path(store_root: Path) -> Path:
    return store_root.resolve() / "active.json"


def _load_active(store_root: Path) -> dict[str, Any]:
    pointer = _read_json(_active_path(store_root))
    required = {
        "active_corpus_version",
        "course_switches",
        "previous_corpus_version",
        "schema_version",
        "source_commit",
        "trusted_master_commit",
        "trusted_master_ref",
    }
    if set(pointer) != required or pointer.get("schema_version") != ACTIVE_SCHEMA_VERSION:
        raise CorpusBuildError("active.json does not match corpus-active-v1")
    if not isinstance(pointer.get("course_switches"), dict) or not all(
        isinstance(key, str)
        and bool(_VERSION_RE.fullmatch(key))
        and isinstance(value, bool)
        for key, value in pointer["course_switches"].items()
    ):
        raise CorpusBuildError("active.json course_switches must be booleans")
    _require_version(str(pointer.get("active_corpus_version", "")), "corpus_version")
    previous = pointer.get("previous_corpus_version")
    if previous is not None:
        _require_version(str(previous), "previous_corpus_version")
    _require_commit(str(pointer.get("source_commit", "")))
    _require_commit(str(pointer.get("trusted_master_commit", "")))
    trusted_ref = pointer.get("trusted_master_ref")
    if not isinstance(trusted_ref, str) or not (
        trusted_ref == "refs/heads/master"
        or (
            trusted_ref.startswith("refs/remotes/")
            and trusted_ref.endswith("/master")
        )
    ):
        raise CorpusBuildError("active.json trusted master proof is invalid")
    return pointer


def _require_active_candidate_binding(
    pointer: dict[str, Any], metadata: dict[str, Any]
) -> None:
    if pointer.get("active_corpus_version") != metadata.get("corpus_version"):
        raise CorpusBuildError("active pointer corpus_version binding mismatch")
    if pointer.get("source_commit") != metadata.get("source_commit"):
        raise CorpusBuildError("active pointer source_commit binding mismatch")
    available = metadata.get("available_courses")
    switches = pointer.get("course_switches")
    if not isinstance(available, list) or not isinstance(switches, dict):
        raise CorpusBuildError("active pointer course binding is invalid")
    if set(switches) != set(available):
        raise CorpusBuildError("active pointer course switches binding mismatch")


def activate_candidate(
    store_root: Path,
    corpus_version: str,
    *,
    repository_root: Path,
    trusted_master_ref: str,
) -> dict[str, Any]:
    """Validate then atomically point active.json at an immutable candidate."""

    candidate = _candidate_directory(store_root.resolve(), corpus_version)
    validate_candidate(candidate)
    metadata = _read_json(candidate / "metadata.json")
    canonical_ref, master_commit = _verify_commit_on_trusted_master(
        repository_root,
        metadata["source_commit"],
        trusted_master_ref,
    )
    active_file = _active_path(store_root)
    if active_file.exists():
        current = _load_active(store_root)
        if current["active_corpus_version"] == corpus_version:
            _require_active_candidate_binding(current, metadata)
            return current
        previous = current["active_corpus_version"]
        existing_switches = current["course_switches"]
    else:
        previous = None
        existing_switches = {}
    switches = {
        course_id: existing_switches.get(course_id, False)
        for course_id in metadata["available_courses"]
    }
    pointer = {
        "active_corpus_version": corpus_version,
        "course_switches": switches,
        "previous_corpus_version": previous,
        "schema_version": ACTIVE_SCHEMA_VERSION,
        "source_commit": metadata["source_commit"],
        "trusted_master_commit": master_commit,
        "trusted_master_ref": canonical_ref,
    }
    _atomic_write_json(active_file, pointer)
    return pointer


def rollback_active(
    store_root: Path,
    *,
    repository_root: Path,
    trusted_master_ref: str,
) -> dict[str, Any]:
    """Atomically swap active and previous after validating the rollback target."""

    current = _load_active(store_root)
    previous = current["previous_corpus_version"]
    if not isinstance(previous, str) or not previous:
        raise CorpusBuildError("active corpus has no previous version to roll back to")
    target = _candidate_directory(store_root.resolve(), previous)
    validate_candidate(target)
    metadata = _read_json(target / "metadata.json")
    canonical_ref, master_commit = _verify_commit_on_trusted_master(
        repository_root,
        metadata["source_commit"],
        trusted_master_ref,
    )
    switches = {
        course_id: current["course_switches"].get(course_id, False)
        for course_id in metadata["available_courses"]
    }
    pointer = {
        "active_corpus_version": previous,
        "course_switches": switches,
        "previous_corpus_version": current["active_corpus_version"],
        "schema_version": ACTIVE_SCHEMA_VERSION,
        "source_commit": metadata["source_commit"],
        "trusted_master_commit": master_commit,
        "trusted_master_ref": canonical_ref,
    }
    _atomic_write_json(_active_path(store_root), pointer)
    return pointer


def set_course_enabled(
    store_root: Path, course_id: str, *, enabled: bool
) -> dict[str, Any]:
    """Update one explicit course switch without changing the active version."""

    if not isinstance(enabled, bool):
        raise CorpusBuildError("enabled must be a boolean")
    course = _require_version(course_id, "course_id")
    pointer = _load_active(store_root)
    candidate = _candidate_directory(
        store_root.resolve(), pointer["active_corpus_version"]
    )
    validate_candidate(candidate)
    metadata = _read_json(candidate / "metadata.json")
    _require_active_candidate_binding(pointer, metadata)
    if course not in metadata["available_courses"]:
        raise CorpusBuildError(f"course is absent from active corpus: {course}")
    pointer["course_switches"][course] = enabled
    _atomic_write_json(_active_path(store_root), pointer)
    return pointer


def load_active_course(store_root: Path, course_id: str) -> dict[str, Any]:
    """Load one enabled course index through the validated active pointer."""

    course = _require_version(course_id, "course_id")
    pointer = _load_active(store_root)
    if pointer["course_switches"].get(course) is not True:
        raise CorpusBuildError(f"course is disabled or unavailable: {course}")
    candidate = _candidate_directory(
        store_root.resolve(), pointer["active_corpus_version"]
    )
    validate_candidate(candidate)
    metadata = _read_json(candidate / "metadata.json")
    _require_active_candidate_binding(pointer, metadata)
    return _read_json(candidate / "courses" / f"{course}.json")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build", help="build, but do not activate, candidate")
    build.add_argument("--manifest", required=True, type=Path)
    build.add_argument("--knowledge-root", required=True, type=Path)
    build.add_argument("--store-root", required=True, type=Path)
    build.add_argument("--source-commit", required=True)
    build.add_argument("--repository-root", required=True, type=Path)
    build.add_argument("--max-chunk-chars", type=int, default=1200)
    build.add_argument("--workflow-version", default="workflow-contract-v1")
    build.add_argument("--outline-version", default="outline-none-v1")
    activate = subparsers.add_parser("activate")
    activate.add_argument("--store-root", required=True, type=Path)
    activate.add_argument("--corpus-version", required=True)
    activate.add_argument("--repository-root", required=True, type=Path)
    activate.add_argument("--trusted-master-ref", required=True)
    rollback = subparsers.add_parser("rollback")
    rollback.add_argument("--store-root", required=True, type=Path)
    rollback.add_argument("--repository-root", required=True, type=Path)
    rollback.add_argument("--trusted-master-ref", required=True)
    course = subparsers.add_parser("course")
    course.add_argument("--store-root", required=True, type=Path)
    course.add_argument("--course-id", required=True)
    course.add_argument("--enabled", choices=("true", "false"), required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("--candidate", required=True, type=Path)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "build":
            payload = build_candidate(
                manifest_path=args.manifest,
                knowledge_root=args.knowledge_root,
                store_root=args.store_root,
                source_commit=args.source_commit,
                repository_root=args.repository_root,
                max_chunk_chars=args.max_chunk_chars,
                workflow_version=args.workflow_version,
                outline_version=args.outline_version,
            ).to_dict()
        elif args.command == "activate":
            payload = {
                "ok": True,
                "active": activate_candidate(
                    args.store_root,
                    args.corpus_version,
                    repository_root=args.repository_root,
                    trusted_master_ref=args.trusted_master_ref,
                ),
            }
        elif args.command == "rollback":
            payload = {
                "ok": True,
                "active": rollback_active(
                    args.store_root,
                    repository_root=args.repository_root,
                    trusted_master_ref=args.trusted_master_ref,
                ),
            }
        elif args.command == "course":
            payload = {
                "ok": True,
                "active": set_course_enabled(
                    args.store_root,
                    args.course_id,
                    enabled=args.enabled == "true",
                ),
            }
        else:
            payload = {"ok": True, "validation": validate_candidate(args.candidate)}
    except CorpusBuildError as exc:
        json.dump({"ok": False, "error": str(exc)}, sys.stderr, ensure_ascii=False)
        sys.stderr.write("\n")
        return 1
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
