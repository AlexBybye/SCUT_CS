"""Source-reviewed learning retrieval evaluation (no model/LLM calls).

Evidence groups represent distinct needs; any listed chunk can satisfy one
group. Unlisted chunks remain unjudged. Scores are known-evidence lower bounds,
not exhaustive recall, answer accuracy, or a noise estimate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

from .paths import APP_ROOT
from .retrieval_eval import DEFAULT_CORPUS_STORE

DEFAULT_SUITE = APP_ROOT / "resources/evaluation/reviewed-v2/retrieval.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_suite(suite: dict[str, Any], store_root: Path) -> dict[str, int]:
    if suite.get("schema_version") != "reviewed-retrieval-v2":
        raise ValueError("unsupported learning evaluation schema")
    pointer = read_json(store_root / "active.json")
    if suite["corpus_version"] != pointer["active_corpus_version"]:
        raise ValueError("annotation corpus version differs from active corpus")
    entries, evidence = suite["entries"], suite["evidence"]
    if not entries or not evidence:
        raise ValueError("empty reviewed suite")
    root = store_root / "candidates" / suite["corpus_version"] / "courses"
    indexes = {}
    for course in {e["course_id"] for e in evidence.values()}:
        indexes[course] = {c["chunk_id"]: c for c in read_json(root / f"{course}.json")["chunks"]}
    for cid, saved in evidence.items():
        current = indexes[saved["course_id"]].get(cid)
        if current is None or current["text"] != saved["text"]:
            raise ValueError(f"evidence missing or changed: {cid}")
        if hashlib.sha256(current["text"].encode()).hexdigest() != saved["text_sha256"]:
            raise ValueError(f"evidence fingerprint mismatch: {cid}")
        for key in ("source_id", "source_title", "locator_type", "locator_start", "locator_end", "question_id", "heading_path"):
            if current[key] != saved[key]:
                raise ValueError(f"evidence metadata changed: {cid}: {key}")
        path = APP_ROOT / saved["knowledge_path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != saved["knowledge_sha256"]:
            raise ValueError(f"knowledge source changed: {cid}; review affected labels")
    seen, source_splits, topic_splits = set(), {}, {}
    for entry in entries:
        if entry["case_id"] in seen or not entry["query"].strip():
            raise ValueError("duplicate case id or blank query")
        seen.add(entry["case_id"])
        if entry["split"] not in {"dev", "validation"}:
            raise ValueError("unknown split")
        if not entry["reference_answer"] or not entry["verification"] or not entry["evidence_groups"]:
            raise ValueError(f"missing review rationale: {entry['case_id']}")
        previous_topic = topic_splits.setdefault(entry["topic_id"], entry["split"])
        if previous_topic != entry["split"]:
            raise ValueError("paraphrase family crosses splits")
        for group in entry["evidence_groups"]:
            ids = group["chunk_ids"]
            if not group["need"] or not ids or len(ids) != len(set(ids)):
                raise ValueError("invalid evidence group")
            for cid in ids:
                if cid not in evidence or evidence[cid]["course_id"] != entry["course_id"]:
                    raise ValueError(f"invalid course evidence: {cid}")
                source = evidence[cid]["source_id"]
                previous = source_splits.setdefault(source, entry["split"])
                if previous != entry["split"]:
                    raise ValueError(f"source family crosses splits: {source}")
    return {"queries": len(entries), "topics": len(topic_splits), "courses": len(indexes), "evidence_chunks": len(evidence)}


def score_ranking(groups: list[dict[str, Any]], ranked: list[str]) -> dict[str, Any]:
    if not groups or any(not group["chunk_ids"] for group in groups):
        raise ValueError("scoring requires non-empty positive evidence groups")
    ranked = list(dict.fromkeys(ranked))
    known = {cid for group in groups for cid in group["chunk_ids"]}
    result = {}
    for k in (5, 20):
        top = set(ranked[:k])
        hit = sum(bool(top.intersection(group["chunk_ids"])) for group in groups)
        result[f"known_evidence_coverage_at_{k}"] = hit / len(groups)
        result[f"all_evidence_groups_at_{k}"] = int(hit == len(groups))
    result["known_positive_mrr"] = next((1 / i for i, cid in enumerate(ranked, 1) if cid in known), 0.0)
    result["unjudged_chunk_ids"] = [cid for cid in ranked if cid not in known]
    return result


def run_suite(suite_path: Path, store_root: Path, *, embedding=None, min_score=1.0, split="all"):
    from .adapters.local_corpus import LocalCorpusRetrievalGateway

    suite = read_json(suite_path)
    validation = validate_suite(suite, store_root)
    if embedding is not None:
        candidate = store_root / "candidates" / suite["corpus_version"]
        if read_json(candidate / "metadata.json").get("embedding_model_id") != embedding.model_id:
            raise ValueError("hybrid evaluation requires a matching corpus embedding model")
        for course in {entry["course_id"] for entry in suite["entries"]}:
            if not (candidate / "vectors" / f"{course}.db").is_file():
                raise ValueError(f"hybrid evaluation missing vectors: {course}")
    gateway = LocalCorpusRetrievalGateway(store_root, limit=20, min_score=min_score, embedding=embedding)
    rows = []
    for entry in suite["entries"]:
        if split != "all" and entry["split"] != split:
            continue
        start = time.perf_counter()
        batch = gateway.search([entry["course_id"]], entry["query"])
        ids = [s.chunk_id for s in batch.sources]
        rows.append({
            **{k: entry[k] for k in ("case_id", "topic_id", "course_id", "scenario", "split")},
            "query": entry["query"], "top_chunk_ids": ids,
            "duration_ms": round((time.perf_counter() - start) * 1000, 3),
            **score_ranking(entry["evidence_groups"], ids),
        })
    metric_keys = ("known_evidence_coverage_at_5", "known_evidence_coverage_at_20", "all_evidence_groups_at_5", "all_evidence_groups_at_20", "known_positive_mrr")

    def summary(values):
        return {"queries": len(values), **{k: round(sum(v[k] for v in values) / len(values), 6) for k in metric_keys}}

    if not rows:
        raise ValueError("selected split has no queries")
    report = {
        "schema_version": "reviewed-retrieval-report-v2", "corpus_version": suite["corpus_version"],
        "suite_sha256": hashlib.sha256(suite_path.read_bytes()).hexdigest(),
        "mode": "hybrid" if embedding else "bm25f", "min_score": min_score,
        "split": split, "validation": validation, "summary": summary(rows),
        "interpretation": "Known-positive lower bounds; unjudged candidates require review, never automatic negative labels. No generation or answer-quality score. Timing includes first-load overhead.",
        "entries": rows,
    }
    for key in ("course_id", "scenario", "split"):
        groups = defaultdict(list)
        for row in rows:
            groups[row[key]].append(row)
        report[f"by_{key}"] = {name: summary(values) for name, values in groups.items()}
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=DEFAULT_SUITE)
    parser.add_argument("--corpus-store", type=Path, default=DEFAULT_CORPUS_STORE)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--embedding-model-dir", type=Path)
    parser.add_argument("--min-score", type=float, default=1.0)
    parser.add_argument("--split", choices=("all", "dev", "validation"), default="all")
    args = parser.parse_args(argv)
    if args.validate_only:
        print(json.dumps(validate_suite(read_json(args.suite), args.corpus_store)))
        return 0
    if args.report is None:
        parser.error("--report required for retrieval evaluation")
    embedding = None
    if args.embedding_model_dir:
        from .adapters.onnx import OnnxEmbeddingProvider
        embedding = OnnxEmbeddingProvider(args.embedding_model_dir)
    report = run_suite(args.suite, args.corpus_store, embedding=embedding, min_score=args.min_score, split=args.split)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
