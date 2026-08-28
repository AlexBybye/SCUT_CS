"""PLAN-2 阶段一 步骤 1：P0 检索评测基线（golden set + 指标）。

This module is the retrieval-only half of the evaluation baseline that every
later phase-1 change (BM25F, dense + RRF, query variants, rerank) is measured
against. It loads a checked-in golden/query candidate set, proves every referenced chunk
actually exists in the active corpus, drives the local-corpus retrieval
gateway, and reports per-course recall@5 / recall@20 / MRR and a noise-rate
proxy used to re-calibrate ``min_score``.

Golden set contract
-------------------
One JSON file per course under ``resources/evaluation/retrieval-golden/``::

    {
      "schema_version": "retrieval-golden-v1",
      "course_id": "linear_algebra",
      "corpus_version": "corpus-...",           // optional annotation target
      "entries": [
        {
          "query": "已知向量组的秩是多少",
          "expected_chunk_ids": ["linear-algebra-012:p1:q-linear-algebra-012-q3:c01"],
          "note": "历年题题干 -> 题目 chunk"
        }
      ]
    }

Metrics (all computed against the gateway's ranked, score-floor-filtered
top-N candidates for the single query):

- ``recall@5``  : |expected ∩ top-5|  / |expected|
- ``recall@20`` : |expected ∩ top-20| / |expected|
- ``mrr``       : 1 / rank of the first expected hit, 0 when none hits
- ``noise_rate``: |top-N \\ expected| / |top-N|  (retrieval-only proxy for the
  full-pipeline "returned but never cited" share; a high value is the signal
  to raise ``min_score``)

Reference validation fails closed: an expected chunk_id that is absent from
the active course index aborts the evaluation, because a golden set whose
references do not resolve cannot produce a meaningful recall number.

Preview-only courses with no text chunks may use an explicitly noted empty
``expected_chunk_ids`` list; those entries are query candidates only and have
no recall target until text is added to the course corpus.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from scut_senior_worker.corpus_builder import (
    CorpusBuildError,
    _candidate_directory,
    _load_active,
    _read_json,
)

from .adapters.local_corpus import LocalCorpusRetrievalGateway
from .embedding import EmbeddingProvider
from .paths import APP_ROOT

GOLDEN_SCHEMA_VERSION = "retrieval-golden-v1"
EVAL_SCHEMA_VERSION = "retrieval-eval-v1"
RUNNER_ID = "scut-senior-retrieval-eval-v1"

DEFAULT_GOLDEN_ROOT = APP_ROOT / "resources" / "evaluation" / "retrieval-golden"
DEFAULT_CORPUS_STORE = APP_ROOT / ".local" / "corpus-store"

_EVAL_TOP_N = 20


@dataclass(frozen=True, slots=True)
class GoldenEntry:
    course_id: str
    query: str
    expected_chunk_ids: tuple[str, ...]
    note: str = ""


@dataclass(frozen=True, slots=True)
class EntryResult:
    course_id: str
    query: str
    note: str
    expected_chunk_ids: tuple[str, ...]
    top_chunk_ids: tuple[str, ...]
    recall_at_5: float
    recall_at_20: float
    mrr: float
    noise_rate: float

    def to_dict(self) -> dict[str, object]:
        return {
            "course_id": self.course_id,
            "query": self.query,
            "note": self.note,
            "expected_chunk_ids": list(self.expected_chunk_ids),
            "top_chunk_ids": list(self.top_chunk_ids),
            "recall_at_5": self.recall_at_5,
            "recall_at_20": self.recall_at_20,
            "mrr": self.mrr,
            "noise_rate": self.noise_rate,
        }


def load_golden_set(golden_root: Path) -> list[GoldenEntry]:
    """Load and strictly validate every ``<course_id>.json`` under ``golden_root``."""
    root = golden_root.resolve()
    files = sorted(root.glob("*.json"))
    if not files:
        raise ValueError(f"golden set root contains no course files: {root}")
    entries: list[GoldenEntry] = []
    seen_course_files: set[str] = set()
    for path in files:
        entries.extend(_load_golden_file(path, seen_course_files))
    if not entries:
        raise ValueError("golden set is empty")
    entries.sort(key=lambda entry: (entry.course_id, entry.query))
    return entries


def _load_golden_file(path: Path, seen_course_files: set[str]) -> list[GoldenEntry]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read golden set file {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"golden set file root must be an object: {path}")
    allowed = {"schema_version", "course_id", "corpus_version", "entries"}
    unknown = set(payload) - allowed
    if unknown:
        raise ValueError(f"{path.name}: unknown golden set fields: {sorted(unknown)}")
    if payload.get("schema_version") != GOLDEN_SCHEMA_VERSION:
        raise ValueError(
            f"{path.name}: schema_version must be {GOLDEN_SCHEMA_VERSION!r}"
        )
    course_id = payload.get("course_id")
    if not isinstance(course_id, str) or not course_id:
        raise ValueError(f"{path.name}: course_id must be a non-empty string")
    if course_id in seen_course_files:
        raise ValueError(f"duplicate golden set file for course {course_id!r}")
    seen_course_files.add(course_id)
    corpus_version = payload.get("corpus_version")
    if corpus_version is not None and (
        not isinstance(corpus_version, str) or not corpus_version
    ):
        raise ValueError(f"{path.name}: corpus_version must be a non-empty string")
    raw_entries = payload.get("entries")
    if not isinstance(raw_entries, list) or not raw_entries:
        raise ValueError(f"{path.name}: entries must be a non-empty list")
    entries: list[GoldenEntry] = []
    seen_queries: set[str] = set()
    for index, raw in enumerate(raw_entries):
        entry = _parse_golden_entry(path, index, course_id, raw)
        if entry.query in seen_queries:
            raise ValueError(
                f"{path.name}: duplicate query {entry.query!r}"
            )
        seen_queries.add(entry.query)
        entries.append(entry)
    return entries


def _parse_golden_entry(
    path: Path, index: int, course_id: str, raw: object
) -> GoldenEntry:
    if not isinstance(raw, dict):
        raise ValueError(f"{path.name}: entries[{index}] must be an object")
    allowed = {"query", "expected_chunk_ids", "note"}
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError(
            f"{path.name}: entries[{index}] unknown fields: {sorted(unknown)}"
        )
    query = raw.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError(
            f"{path.name}: entries[{index}].query must be a non-empty string"
        )
    expected = raw.get("expected_chunk_ids")
    note = raw.get("note")
    if note is not None and not isinstance(note, str):
        raise ValueError(f"{path.name}: entries[{index}].note must be a string")
    # A preview-only course can have no searchable chunk at all. Keep its
    # generated query candidates loadable, but require an explicit note so an
    # accidentally empty target list never passes silently.
    if (
        not isinstance(expected, list)
        or (not expected and not (note or "").startswith("无可检索文本 chunk"))
        or not all(isinstance(chunk, str) and chunk for chunk in expected)
    ):
        raise ValueError(
            f"{path.name}: entries[{index}].expected_chunk_ids must be a "
            "list of non-empty strings (or an explicitly noted empty list)"
        )
    if len(set(expected)) != len(expected):
        raise ValueError(
            f"{path.name}: entries[{index}].expected_chunk_ids must be unique"
        )
    return GoldenEntry(
        course_id=course_id,
        query=query.strip(),
        expected_chunk_ids=tuple(expected),
        note=(note or ""),
    )


def _course_chunk_ids(store_root: Path, course_id: str) -> set[str]:
    """Read the active candidate's chunk inventory for one course."""
    pointer = _load_active(store_root)
    candidate = _candidate_directory(
        store_root.resolve(), pointer["active_corpus_version"]
    )
    index = _read_json(candidate / "courses" / f"{course_id}.json")
    chunks = index.get("chunks")
    if not isinstance(chunks, list):
        raise ValueError(f"{course_id}: active course index has no chunk list")
    return {chunk["chunk_id"] for chunk in chunks if isinstance(chunk, dict)}


def validate_golden_references(
    store_root: Path, entries: Iterable[GoldenEntry]
) -> list[str]:
    """Return ``"course_id: chunk_id"`` for every expected chunk absent from the
    active corpus. An empty list means every golden reference resolves."""
    missing: list[str] = []
    chunk_ids_by_course: dict[str, set[str]] = {}
    for entry in entries:
        inventory = chunk_ids_by_course.get(entry.course_id)
        if inventory is None:
            try:
                inventory = _course_chunk_ids(store_root, entry.course_id)
            except (CorpusBuildError, OSError, ValueError, KeyError) as exc:
                raise ValueError(
                    f"cannot load active chunk inventory for "
                    f"{entry.course_id!r}: {exc}"
                ) from exc
            chunk_ids_by_course[entry.course_id] = inventory
        for chunk_id in entry.expected_chunk_ids:
            if chunk_id not in inventory:
                missing.append(f"{entry.course_id}: {chunk_id}")
    return missing


def _recall_at(expected: tuple[str, ...], top: tuple[str, ...], k: int) -> float:
    if not expected:
        return 1.0
    expected_set = set(expected)
    hits = sum(1 for chunk in top[:k] if chunk in expected_set)
    return hits / len(expected)


def _mrr(expected: tuple[str, ...], top: tuple[str, ...]) -> float:
    expected_set = set(expected)
    for index, chunk_id in enumerate(top, start=1):
        if chunk_id in expected_set:
            return 1.0 / index
    return 0.0


def _noise_rate(expected: tuple[str, ...], top: tuple[str, ...]) -> float:
    if not top:
        return 0.0
    expected_set = set(expected)
    noise = sum(1 for chunk_id in top if chunk_id not in expected_set)
    return noise / len(top)


def run_retrieval_evaluation(
    golden_root: Path,
    report_path: Path,
    *,
    store_root: Path,
    min_score: float = 1.0,
    top_n: int = _EVAL_TOP_N,
    embedding: EmbeddingProvider | None = None,
) -> dict[str, object]:
    """Run the golden set against the active local corpus and write the report.

    Raises ``ValueError`` (fail closed) when the golden set is malformed or
    any expected chunk_id does not resolve in the active corpus.
    """
    entries = load_golden_set(golden_root)
    missing = validate_golden_references(store_root, entries)
    if missing:
        raise ValueError(
            "golden set references do not exist in the active corpus:\n- "
            + "\n- ".join(sorted(missing))
        )
    gateway = LocalCorpusRetrievalGateway(
        store_root, limit=top_n, min_score=min_score, embedding=embedding
    )
    results: list[EntryResult] = []
    for entry in entries:
        batch = gateway.search([entry.course_id], entry.query)
        top = tuple(source.chunk_id for source in batch.sources)
        results.append(
            EntryResult(
                course_id=entry.course_id,
                query=entry.query,
                note=entry.note,
                expected_chunk_ids=entry.expected_chunk_ids,
                top_chunk_ids=top,
                recall_at_5=_recall_at(entry.expected_chunk_ids, top, 5),
                recall_at_20=_recall_at(entry.expected_chunk_ids, top, 20),
                mrr=_mrr(entry.expected_chunk_ids, top),
                noise_rate=_noise_rate(entry.expected_chunk_ids, top),
            )
        )
    report = _build_report(results, gateway, top_n)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def _build_report(
    results: list[EntryResult], gateway: LocalCorpusRetrievalGateway, top_n: int
) -> dict[str, object]:
    corpus_version = _active_corpus_version(gateway.store_root)
    entry_dicts = [result.to_dict() for result in results]

    def _avg(field: str) -> float:
        values = [getattr(result, field) for result in results]
        return round(sum(values) / len(values), 6) if values else 0.0

    by_course: dict[str, dict[str, object]] = {}
    for result in results:
        course = by_course.setdefault(
            result.course_id,
            {"entry_count": 0, "recall_at_5": 0.0, "recall_at_20": 0.0,
             "mrr": 0.0, "noise_rate": 0.0},
        )
        course["entry_count"] = int(course["entry_count"]) + 1
        course["recall_at_5"] = round(
            float(course["recall_at_5"]) + result.recall_at_5, 6
        )
        course["recall_at_20"] = round(
            float(course["recall_at_20"]) + result.recall_at_20, 6
        )
        course["mrr"] = round(float(course["mrr"]) + result.mrr, 6)
        course["noise_rate"] = round(
            float(course["noise_rate"]) + result.noise_rate, 6
        )
    for course in by_course.values():
        count = int(course["entry_count"])
        for field in ("recall_at_5", "recall_at_20", "mrr", "noise_rate"):
            course[field] = round(float(course[field]) / count, 6)

    return {
        "runner_id": RUNNER_ID,
        "schema_version": EVAL_SCHEMA_VERSION,
        "corpus_version": corpus_version,
        "top_n": top_n,
        "min_score": gateway.min_score,
        "executed_at": datetime.now(UTC).isoformat(),
        "summary": {
            "entry_count": len(results),
            "recall_at_5": _avg("recall_at_5"),
            "recall_at_20": _avg("recall_at_20"),
            "mrr": _avg("mrr"),
            "noise_rate": _avg("noise_rate"),
        },
        "by_course": {
            course: dict(course_report)
            for course, course_report in sorted(by_course.items())
        },
        "entries": entry_dicts,
    }


def _active_corpus_version(store_root: Path) -> str:
    pointer = _load_active(store_root)
    version = pointer.get("active_corpus_version")
    if not isinstance(version, str) or not version:
        raise ValueError("active.json has no valid active_corpus_version")
    return version
