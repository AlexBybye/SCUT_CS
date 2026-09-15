"""Expand reviewed semantic anchors into realistic student workflow cases.

The script does not assert new facts or create new answer keys: every case
inherits one reviewed-v2 anchor's answer, verification, pitfalls and evidence.
It is for multi-turn/workflow robustness. Results must aggregate by
anchor_topic_id, because variants of an anchor are correlated observations.
"""
from __future__ import annotations

import json
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
ROOT = APP / "resources" / "evaluation" / "reviewed-v2"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def scenario_variants(anchor: dict) -> list[dict]:
    query = anchor["query"]
    pitfall = anchor["pitfalls"][0]
    course = anchor["course_id"]
    topic = anchor["topic_id"]
    common = {
        "course_id": course,
        "course_scope": "single",
        "allowed_course_ids": [],
        "knowledge_scope": "course_first",
        "expected": {"answer_status": "answered", "requires_citation": True, "allows_general": True},
        "quality_rubric": {
            "anchor_topic_id": topic,
            "reference_answer": anchor["reference_answer"],
            "evidence_groups": anchor["evidence_groups"],
            "verification": anchor["verification"],
            "must_not_claim": anchor["pitfalls"],
            "grading": "Judge against the reviewed anchor. Equivalent reasoning is acceptable. Do not count sibling variants as independent semantic evidence.",
        },
    }
    variants = [
        ("recall", "knowledge_qa", "考前概念确认", [{"role": "user", "content": f"我在复习{course}，不想只背结论。{query} 请按定义、条件和结论解释。"}]),
        ("mistake", "mistake_review", "错题复盘", [{"role": "user", "content": f"我做题时写了“{pitfall}”。题目是：{query}。请指出这一步为什么错，并给出最短的改正路径。"}]),
        ("timebox", "problem_tutor", "限时练习", [{"role": "user", "content": f"离考试还有十分钟。{query} 请先给我一条能防止误判的检查顺序，再给结论。"}]),
        ("followup", "knowledge_qa", "追问澄清", [{"role": "user", "content": query}, {"role": "user", "content": "我容易在前提上偷换概念。请指出这个题最不能省略的条件，并说明删掉它会怎样。"}]),
        ("teachback", "problem_tutor", "讲给同学听", [{"role": "user", "content": f"同学问我：{query}。请帮我组织一段可以讲给他听的回答，必须包含一个反例、边界或检验步骤，不能只报答案。"}]),
        ("evidence", "temporary_material_reading", "资料对照", [{"role": "user", "content": f"我找到了这条课程资料，但担心自己把它理解偏了：{query}。请区分资料直接支持的结论与需要推导才能得到的结论。"}]),
    ]
    result = []
    for suffix, workflow, label, turns in variants:
        result.append({
            **common,
            "case_id": f"student-{topic}-{suffix}",
            "category": anchor["scenario"],
            "workflow_type": workflow,
            "scenario_label": label,
            "anchor_topic_id": topic,
            "difficulty": anchor["difficulty"],
            "student_profile": {"stage": "final_review", "need": label, "source": "simulated_from_reviewed_anchor"},
            "turns": turns,
        })
    return result


def main() -> None:
    suite = read(ROOT / "retrieval.json")
    anchors = {}
    for entry in suite["entries"]:
        anchors.setdefault(entry["topic_id"], entry)
    cases = [case for anchor in anchors.values() for case in scenario_variants(anchor)]
    visual_suite = read(ROOT / "visual-reviewed.json")
    for entry in visual_suite["entries"]:
        cases.append({
            "case_id": f"student-{entry['case_id']}",
            "category": "visual_problem_tutor",
            "course_id": entry["course_id"],
            "course_scope": "single",
            "allowed_course_ids": [],
            "workflow_type": "problem_tutor",
            "knowledge_scope": "course_first",
            "scenario_label": "图片资料读题与推导",
            "anchor_topic_id": entry["case_id"],
            "difficulty": entry["difficulty"],
            "student_profile": {"stage": "final_review", "need": "图片题复盘", "source": "manually_reviewed_image_anchor"},
            "turns": [{"role": "user", "content": entry["query"]}],
            "expected": {"answer_status": "answered", "allows_general": True},
            "quality_rubric": {
                "anchor_topic_id": entry["case_id"],
                "reference_answer": entry["reference_answer"],
                "image_evidence": entry["image_evidence"],
                "verification": entry["verification"],
                "must_not_claim": entry["pitfalls"],
                "grading": "Requires an image-capable or OCR-backed answer path. Do not score this case as a text-retrieval failure.",
            },
        })
    output = {
        "contract_version": "v1",
        "dataset_status": "simulated_student_scenarios_from_reviewed_semantic_anchors",
        "corpus_version": suite["corpus_version"],
        "quality_requires_review": True,
        "notes": (
            "Six realistic workflow variants per reviewed text topic plus six manually reviewed image cases. They inherit, rather than expand, the semantic answer key. "
            "Aggregate quality and retrieval results by anchor_topic_id/source family; raw case count is a robustness load, not an independent sample size."
        ),
        "cases": cases,
    }
    (ROOT / "student-scenarios.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"anchors": len(anchors), "cases": len(cases), "courses": len({case['course_id'] for case in cases})}))


if __name__ == "__main__":
    main()
