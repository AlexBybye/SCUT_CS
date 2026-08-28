"""Build version-bound SQLite vector files for an immutable corpus candidate."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from .adapters.onnx import OnnxEmbeddingProvider
from .embedding import EmbeddingProvider
from .vector_store import VectorStore


def build_candidate_vectors(
    candidate_path: Path,
    embedding: EmbeddingProvider,
    *,
    batch_size: int = 32,
) -> int:
    """Write one vector SQLite file per course and return vector count."""
    if isinstance(batch_size, bool) or batch_size < 1:
        raise ValueError("vector batch_size must be positive")
    candidate = candidate_path.resolve()
    metadata = json.loads((candidate / "metadata.json").read_text(encoding="utf-8"))
    if metadata.get("embedding_model_id") != embedding.model_id:
        raise ValueError("candidate embedding_model_id does not match provider")
    total = 0
    by_course: dict[str, list[dict[str, object]]] = defaultdict(list)
    for course_file in sorted((candidate / "courses").glob("*.json")):
        course = json.loads(course_file.read_text(encoding="utf-8"))
        course_id = course.get("course_id")
        chunks = course.get("chunks")
        if not isinstance(course_id, str) or not isinstance(chunks, list):
            raise ValueError(f"invalid course payload: {course_file.name}")
        by_course[course_id].extend(chunk for chunk in chunks if isinstance(chunk, dict))
    for course_id, chunks in by_course.items():
        vector_path = candidate / "vectors" / f"{course_id}.db"
        vector_path.parent.mkdir(parents=True, exist_ok=True)
        store = VectorStore(
            vector_path, dimensions=embedding.dimensions, model_id=embedding.model_id
        )
        try:
            for offset in range(0, len(chunks), batch_size):
                batch = chunks[offset : offset + batch_size]
                texts = [_chunk_text(chunk) for chunk in batch]
                vectors = embedding.embed(texts)
                if len(vectors) != len(batch):
                    raise ValueError("embedding provider returned an unexpected batch size")
                store.bulk_upsert(
                    (
                        str(chunk["chunk_id"]),
                        course_id,
                        vector,
                    )
                    for chunk, vector in zip(batch, vectors)
                )
                total += len(batch)
        finally:
            store.close()
    return total


def _chunk_text(chunk: dict[str, object]) -> str:
    parts: list[str] = []
    for key in ("source_title", "heading_path", "question_id", "text"):
        value = chunk.get(key)
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
        elif isinstance(value, str):
            parts.append(value)
    return "\n".join(part for part in parts if part)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--model-dir", required=True, type=Path)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args(list(argv) if argv is not None else None)
    provider = OnnxEmbeddingProvider(args.model_dir)
    count = build_candidate_vectors(args.candidate, provider, batch_size=args.batch_size)
    print(json.dumps({"ok": True, "vector_count": count}, ensure_ascii=False))
    return 0
