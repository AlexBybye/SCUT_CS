"""Inventory legacy annotations against the active corpus; never certify semantics.

Run from anywhere with the project Python. Output is deterministic and contains
one record per legacy query, including evidence fingerprints and reasons.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
EVAL = APP / "resources/evaluation"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def text_body(text):
    return re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text).strip()


def main():
    store = APP / ".local/corpus-store"
    version = read(store / "active.json")["active_corpus_version"]
    root = store / "candidates" / version / "courses"
    records, courses = [], []
    for path in sorted((EVAL / "retrieval-golden").glob("*.json")):
        data = read(path)
        chunks = {c["chunk_id"]: c for c in read(root / path.name)["chunks"]}
        courses.append({
            "course_id": data["course_id"], "legacy_queries": len(data["entries"]),
            "chunks": len(chunks),
            "image_only_chunks": sum(not text_body(c["text"]) for c in chunks.values()),
        })
        for index, entry in enumerate(data["entries"], 1):
            reasons = ["no_per_query_answer_or_relevance_rationale"]
            if any(t in entry["query"] for t in (
                "主要讲什么", "应该从哪里开始", "哪些内容最重要", "里的方法或结论怎么理解",
                "哪些概念容易混淆", "考试会怎么考", "应该先从哪一步入手",
            )):
                reasons.append("broad_or_template_query_with_specific_chunk_target")
            evidence = []
            for cid in entry["expected_chunk_ids"]:
                chunk = chunks.get(cid)
                if chunk is None:
                    reasons.append("missing_chunk")
                    evidence.append({"chunk_id": cid, "exists": False})
                    continue
                body = text_body(chunk["text"])
                flags = []
                if not body:
                    flags.append("image_only_not_text_answer_evidence")
                elif len(re.sub(r"\W", "", body)) < 40:
                    flags.append("short_text_requires_semantic_review")
                if "\ufffd" in body:
                    flags.append("replacement_character_in_source")
                reasons.extend(flags)
                evidence.append({
                    "chunk_id": cid, "exists": True, "source_id": chunk["source_id"],
                    "source_title": chunk["source_title"], "locator_type": chunk["locator_type"],
                    "locator_start": chunk["locator_start"],
                    "text_sha256": hashlib.sha256(chunk["text"].encode()).hexdigest(),
                    "text_excerpt": chunk["text"][:240], "flags": flags,
                })
            records.append({
                "legacy_id": f"{data['course_id']}:{index:03d}", "course_id": data["course_id"],
                "query": entry["query"], "original_note": entry.get("note"),
                "corpus_version_matches": data.get("corpus_version") == version,
                "disposition": "historical_only_not_certified",
                "reasons": list(dict.fromkeys(reasons)), "evidence": evidence,
            })
    findings = Counter(reason for record in records for reason in record["reasons"])
    report = {
        "schema_version": "evaluation-annotation-audit-v1", "review_date": "2026-09-12",
        "method": "Exhaustive reference/text-shape inventory; semantic examples reviewed by Codex in AUDIT.md. No blanket human/semantic certification.",
        "corpus_version": version, "summary": {"queries": len(records), "courses": len(courses), "findings": dict(findings)},
        "courses": courses, "entries": records,
    }
    out = EVAL / "reviewed-v2/legacy-audit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=True))


if __name__ == "__main__":
    main()
