"""Build a source-snapshot coverage harness for every active course.

The output tests retrieval evidence, not semantic answer correctness.  It is
deliberately separate from reviewed-v2/retrieval.json: each generated task
contains the source text a reviewer must use when judging an answer.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
OUT = APP / "resources" / "evaluation" / "reviewed-v2"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def body(text: str) -> str:
    return re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text).strip()


def clean_label(value: str, fallback: str) -> str:
    value = re.sub(r"[#*_`]+", "", value).strip()
    return value[:90] if value else fallback


def source_card(chunk: dict, path: Path) -> dict:
    return {
        "chunk_id": chunk["chunk_id"],
        "course_id": chunk["course_id"],
        "source_id": chunk["source_id"],
        "source_title": chunk["source_title"],
        "heading_path": chunk["heading_path"],
        "locator_type": chunk["locator_type"],
        "locator_start": chunk["locator_start"],
        "locator_end": chunk["locator_end"],
        "question_id": chunk["question_id"],
        "text": chunk["text"],
        "text_sha256": hashlib.sha256(chunk["text"].encode()).hexdigest(),
        "knowledge_path": path.relative_to(APP).as_posix(),
        "knowledge_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def choose_cards(chunks: list[dict], paths: dict[str, Path]) -> list[tuple[dict, Path]]:
    """Choose three legible passages from distinct source files when possible."""
    candidates: list[tuple[tuple, dict, Path]] = []
    for chunk in chunks:
        text = body(chunk["text"])
        if len(re.sub(r"\W", "", text)) < 180 or "\ufffd" in text:
            continue
        image_weight = len(re.findall(r"!\[[^\]]*\]\([^)]*\)", chunk["text"]))
        heading = " ".join(chunk["heading_path"])
        # Pure agendas, answer sheets and URL pages are poor semantic anchors.
        penalty = sum(term in (chunk["source_title"] + heading).lower() for term in (
            "overview", "course information", "参考答案", "answer sheet", "目录", "url",
        ))
        score = (penalty, image_weight, -min(len(text), 2200), chunk["chunk_id"])
        path = paths.get(chunk["source_id"])
        if path is not None:
            candidates.append((score, chunk, path))
    candidates.sort(key=lambda item: item[0])
    selected: list[tuple[dict, Path]] = []
    used_sources: set[str] = set()
    used_headings: set[tuple[str, ...]] = set()
    for _, chunk, path in candidates:
        heading = tuple(chunk["heading_path"])
        if chunk["source_id"] in used_sources or heading in used_headings:
            continue
        selected.append((chunk, path))
        used_sources.add(chunk["source_id"])
        used_headings.add(heading)
        if len(selected) == 3:
            return selected
    for _, chunk, path in candidates:
        if all(chunk["chunk_id"] != existing[0]["chunk_id"] for existing in selected):
            selected.append((chunk, path))
        if len(selected) == 3:
            break
    return selected


def entry(course: str, suffix: str, difficulty: str, scenario: str, query: str, cards: list[dict], answer_contract: str) -> dict:
    return {
        "case_id": f"coverage-{course}-{suffix}",
        "topic_id": f"coverage-{course}-{suffix}",
        "course_id": course,
        "scenario": scenario,
        "difficulty": difficulty,
        "task_type": "retrieval_evidence",
        "split": "coverage",
        "source_family": "+".join(sorted({card["source_id"] for card in cards})),
        "query": query,
        "evidence_groups": [
            {"need": clean_label(card["heading_path"][-1] if card["heading_path"] else card["source_title"], card["source_title"]), "chunk_ids": [card["chunk_id"]]}
            for card in cards
        ],
        "reference_answer": answer_contract,
        "verification": "Evidence target is a frozen readable corpus passage. Semantic correctness must be judged against the quoted passage; this generated coverage task is not an independently authored answer key.",
        "pitfalls": [
            "用未引用的课程材料替代指定主题",
            "把检索命中或引用编号存在当作回答正确",
            "无证据时补写材料未支持的细节",
        ],
    }


def main() -> None:
    store = APP / ".local" / "corpus-store"
    version = read(store / "active.json")["active_corpus_version"]
    candidate = store / "candidates" / version
    paths = {path.stem: path for path in (APP / "knowledge").glob("*/*.md")}
    evidence: dict[str, dict] = {}
    entries: list[dict] = []
    matrix: list[dict] = []
    for index_path in sorted((candidate / "courses").glob("*.json")):
        index = read(index_path)
        course = index["course_id"]
        cards = choose_cards(index["chunks"], paths)
        if len(cards) < 2:
            matrix.append({
                "course_id": course, "coverage_status": "vision_or_extraction_required",
                "readable_anchor_count": len(cards), "topics": [],
                "reason": "The active corpus lacks two legible text passages; semantic topics must wait for OCR/visual review.",
            })
            # Two hard boundary cases ensure such courses are not silently omitted.
            entries.extend([
                entry(course, "visual-availability", "medium", "evidence_boundary",
                      f"请定位 {course} 课程资料中与当前问题最相关的原始页面；如果只有图片或无法读出的公式，请明确说明文本证据不足，不要猜测内容。", [],
                      "指出资料是否存在可读文本证据，并在不足时请求原图、OCR结果或用户材料。"),
                entry(course, "visual-no-fabrication", "hard", "evidence_boundary",
                      f"仅根据 {course} 当前可检索文本，判断能否可靠讲解一个具体题目。请区分“文件存在”“图片存在”和“题干/公式已被文本化”。", [],
                      "区分资源可见性与可验证内容；无可读题干或公式时不得生成具体解答。"),
            ])
            continue
        cards_data = [source_card(chunk, path) for chunk, path in cards]
        for card in cards_data:
            evidence[card["chunk_id"]] = card
        labels = [clean_label(card["heading_path"][-1] if card["heading_path"] else card["source_title"], card["source_title"]) for card in cards_data]
        matrix.append({
            "course_id": course, "coverage_status": "source_snapshot_ready",
            "readable_anchor_count": len(cards_data), "topics": labels,
            "difficulty_profile": {"easy": 1, "medium": 1, "hard": 1},
        })
        entries.extend([
            entry(course, "anchor", "easy", "definition_or_location",
                  f"请根据《{cards_data[0]['source_title']}》中“{labels[0]}”这一部分，指出资料给出的核心对象、定义或步骤。只说资料实际支持的内容。",
                  [cards_data[0]],
                  "准确定位该段，给出至少两项由原文直接支持的信息，并标注不确定或图像缺失部分。"),
            entry(course, "condition", "medium", "condition_or_error_analysis",
                  f"我把“{labels[1]}”中的条件、过程或适用范围混淆了。请按资料解释：哪些前提不能省略、遗漏后会导致什么判断错误？",
                  [cards_data[1]],
                  "提取原文的条件、顺序、限制或反例；若原文只列主题而未给条件，应明确证据不足。"),
            entry(course, "synthesis", "hard", "multi_evidence_synthesis",
                  f"比较《{cards_data[0]['source_title']}》的“{labels[0]}”与《{cards_data[-1]['source_title']}》的“{labels[-1]}”：它们解决的对象、前提或步骤有什么联系和区别？请分别给出证据，不要把两个主题强行等同。",
                  [cards_data[0], cards_data[-1]],
                  "每个主题至少给出一项被其对应材料支持的事实，再说明可证明的联系或明确说明材料不足以建立联系。"),
        ])
    suite = {
        "schema_version": "coverage-harness-v2", "corpus_version": version,
        "provenance": {
            "review_date": "2026-09-12", "method": "Deterministic selection of legible active-corpus passages; queries are authored templates bound to frozen source snapshots.",
            "status": "coverage harness, not semantic answer-key certification",
        },
        "annotation_scope": "Each positive group names one required evidence need. Unlisted chunks are unjudged. Difficulty describes retrieval/reasoning demand, not a claim that the source passage itself is error-free.",
        "evidence": evidence, "entries": entries,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "coverage-harness.json").write_text(json.dumps(suite, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "coverage-matrix.json").write_text(json.dumps({
        "schema_version": "coverage-matrix-v2", "corpus_version": version, "courses": matrix,
        "summary": {
            "courses": len(matrix),
            "source_snapshot_ready": sum(row["coverage_status"] == "source_snapshot_ready" for row in matrix),
            "vision_or_extraction_required": sum(row["coverage_status"] != "source_snapshot_ready" for row in matrix),
            "harness_cases": len(entries),
        },
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"courses": len(matrix), "source_backed": sum(bool(row["topics"]) for row in matrix), "cases": len(entries), "evidence": len(evidence)}))


if __name__ == "__main__":
    main()
