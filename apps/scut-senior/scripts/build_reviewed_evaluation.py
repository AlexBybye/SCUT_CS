"""Materialize explicitly authored annotations, evidence snapshots and scenarios.

Does not invent annotations or infer semantic validity from retrieval results.
Edit reviewed-v2/annotations.json after reading sources, then rerun this script.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
OUT = APP / "resources/evaluation/reviewed-v2"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    annotations = read(OUT / "annotations.json")
    expansion_path = OUT / "annotations-expanded.json"
    expansions = read(expansion_path) if expansion_path.exists() else {"topics": []}
    topics = [*annotations["topics"], *expansions["topics"]]
    store = APP / ".local/corpus-store"
    version = read(store / "active.json")["active_corpus_version"]
    root = store / "candidates" / version / "courses"
    courses = {t["course_id"] for t in topics}
    chunks = {c["chunk_id"]: c for course in courses for c in read(root / f"{course}.json")["chunks"]}
    evidence = {}
    source_paths = {p.stem: p for p in (APP / "knowledge").glob("*/*.md")}
    # Connected source families, not individual paraphrases, define the split.
    families = []
    for topic in topics:
        ids = {cid for group in topic["groups"] for cid in group["chunk_ids"]}
        family = {chunks[cid]["source_id"] for cid in ids}
        for cid in sorted(ids):
            c = chunks[cid]
            assert c["course_id"] == topic["course_id"]
            path = source_paths[c["source_id"]]
            assert path.exists(), path
            evidence[cid] = {
                **{k: c[k] for k in ("course_id", "source_id", "source_title", "locator_type", "locator_start", "locator_end", "question_id", "heading_path", "text")},
                "knowledge_path": path.relative_to(APP).as_posix(),
                "text_sha256": hashlib.sha256(c["text"].encode()).hexdigest(),
                "knowledge_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        families.append(family)
    changed = True
    while changed:
        changed = False
        for i in range(len(families)):
            for j in range(i):
                if families[i] & families[j] and families[i] != families[j]:
                    families[i] = families[j] = families[i] | families[j]
                    changed = True
    entries = []
    for topic, family in zip(topics, families):
        key = "+".join(sorted(family))
        split = "validation" if int(hashlib.sha256(key.encode()).hexdigest(), 16) % 4 == 0 else "dev"
        for i, query_spec in enumerate(topic["queries"], 1):
            query = query_spec["text"] if isinstance(query_spec, dict) else query_spec
            entries.append({
                "case_id": f"{topic['id']}-{i}", "topic_id": topic["id"], "course_id": topic["course_id"],
                "scenario": topic["scenario"], "query": query, "split": split, "source_family": key,
                "difficulty": query_spec.get("difficulty", topic.get("difficulty", "medium")) if isinstance(query_spec, dict) else topic.get("difficulty", "medium"),
                "evidence_groups": topic["groups"], "reference_answer": topic["answer"],
                "verification": topic["verification"], "pitfalls": topic["pitfalls"],
                "external_reference": topic.get("external_reference"),
                "verified_values": topic.get("verified_values"),
            })
    write("retrieval.json", {
        "schema_version": "reviewed-retrieval-v2", "corpus_version": version,
        "provenance": {k: annotations[k] for k in ("reviewer", "review_date", "review_method")},
        "annotation_scope": "Positive evidence groups are non-exhaustive. Missing labels are unjudged, not irrelevant. Validation is source-disjoint within this suite, not an independent blind test.",
        "evidence": evidence, "entries": entries,
    })
    by_id = {t["id"]: t for t in topics}
    cases = []

    def add(topic_id, workflow="knowledge_qa", *, query=None, payload=None, suffix="", turns=None):
        t = by_id[topic_id]
        first_query = t["queries"][0]
        question = query or (first_query["text"] if isinstance(first_query, dict) else first_query)
        case = {
            "case_id": f"reviewed-{topic_id}{suffix}", "category": t["scenario"],
            "course_id": t["course_id"], "course_scope": "single", "allowed_course_ids": [],
            "workflow_type": workflow, "knowledge_scope": "course_first",
            "turns": turns or [{"role": "user", "content": question}],
            "expected": {"answer_status": "answered", "requires_citation": True, "allows_general": True},
            "quality_rubric": {
                "topic_id": topic_id, "reference_answer": t["answer"],
                "evidence_groups": t["groups"], "verification": t["verification"],
                "must_not_claim": t["pitfalls"], "external_reference": t.get("external_reference"),
                "grading": "Review correctness, requested help level, evidence support and task completion separately. Contract pass is not a quality pass; equivalent reasoning is acceptable.",
            },
        }
        if payload is not None:
            case["workflow_payload"] = payload
        cases.append(case)
        return case

    for tid in ("la-diagonalization", "db-having", "os-states", "network-ack", "ai-prepruning", "ds-source-error"):
        add(tid)
    for tid in ("prob-t-symmetry", "prob-unbiased", "algo-knapsack", "testing-insurance", "discrete-partition", "network-napt"):
        add(tid, "problem_tutor")
    add("db-null", "mistake_review", payload={
        "problem": "从Student表中筛出年龄AGE缺失的学生。",
        "original_answer": "SELECT * FROM Student WHERE AGE = NULL;",
        "reference_answer": None, "review_focus": "指出错误原因并给出正确SQL",
    })
    add("os-producer", "mistake_review", payload={
        "problem": "容量N的有界缓冲区，empty初值N，full初值0，mutex初值1；检查生产者的PV顺序。",
        "original_answer": "生产者P(mutex); P(empty); 放入数据; V(full); V(mutex)。消费者先P(full)再P(mutex)。",
        "reference_answer": None, "review_focus": "缓冲区满时是否死锁；给出修正顺序",
    })
    add("electrical-plan", "exam_review", payload={
        "syllabus": "一阶电路暂态：初始值、稳态值、时间常数", "exam_date": None,
        "available_hours": 2, "goals": ["能独立求出一阶电路暂态三要素"], "weak_topics": ["换路初始值", "时间常数"],
    })
    cases[-1]["expected"].update({"requires_exam_review_plan": True, "review_path": "with_syllabus"})
    cases[-1]["quality_rubric"]["task_requirements"] = ["总时间不超过2小时", "覆盖三要素", "给出练习顺序并照顾两个薄弱点", "不捏造必考概率"]
    add("network-ack", suffix="-followup", turns=[
        {"role": "user", "content": "TCP确认号为n表示什么？"},
        {"role": "user", "content": "那如果它是501，500这个字节算收到了吗？"},
    ])
    cases[-1]["quality_rubric"]["task_requirements"] = ["使用前轮TCP语境解析它", "明确500已确认，而501是期待的下一个字节"]
    add("testing-boundary", suffix="-followup", turns=[
        {"role": "user", "content": "三个独立输入变量的健壮最坏情况边界值测试需要多少组？"},
        {"role": "user", "content": "那为什么不是19？我把它和另一种方法混了。"},
    ])
    add("db-having", "temporary_material_reading", suffix="-temporary", query="精读我贴的SQL规则，用成绩分组举例。", payload={
        "material_title": "我整理的SQL规则",
        "material_text": "WHERE在分组前筛选行；GROUP BY把行分组；HAVING在分组后筛选分组。例：GROUP BY 学号 HAVING AVG(成绩)>=85。",
        "reading_goal": "用一个均分达到85但其中一门低于85的学生解释HAVING，区分它与每门成绩都达标。",
    })
    cases[-1]["expected"] = {"answer_status": "answered", "allows_general": True}
    cases[-1]["quality_rubric"]["evidence_groups"] = []
    cases[-1]["quality_rubric"]["verification"] = "输入材料自身完整；例如成绩80和90均分85，满足HAVING但不满足每门>=85。无需强制公共仓库引用。"
    add("la-diagonalization", "problem_tutor", suffix="-exact", query="讲解2019-2020年度线性代数期末卷A的选择题第4题：相似于对角矩阵的条件。")
    cases[-1]["quality_rubric"]["task_requirements"] = ["定位试卷选择题第4题，不能把内部q10当成试卷第10题", "选B并解释线性无关特征向量条件"]
    cross = add("org-cache", suffix="-cross", query="结合计组和操作系统资料，比较Cache与虚拟存储器利用局部性的共同点，以及它们解决的问题有何不同。")
    cross.update({"course_id": None, "course_scope": "cross", "allowed_course_ids": ["computer_organization", "operating_systems"]})
    cross["quality_rubric"].update({
        "reference_answer": "两者都利用时间与空间局部性；Cache缓解CPU与主存速度差，虚拟存储器提供地址空间抽象并按需调页。Cache命中/失效与缺页异常不是同一层次的事件。",
        "evidence_groups": [by_id["org-cache"]["groups"][0], {"need": "操作系统材料对时间空间局部性的定义", "chunk_ids": ["operating-systems-005:p1:c01"]}],
        "verification": "读取两门课指定段落；OS答案页关于逻辑容量等于内外存之和的说法不作为标准答案，只使用其局部性定义。",
        "must_not_claim": ["Cache等同于虚拟内存", "逻辑地址空间容量无条件等于内存加外存容量"],
        "task_requirements": ["同时使用两门指定课程的相关证据", "解释共同点与区别"],
    })
    absent = add("la-diagonalization", suffix="-missing-paper", query="请找出仓库中2023-2024年度线性代数期末卷A的原题和标准答案。")
    all_la = read(root / "linear_algebra.json")["chunks"]
    assert not any("2023-2024" in c["source_title"] or "2023-2024" in c["text"] for c in all_la)
    absent["knowledge_scope"] = "course_only"
    absent["expected"] = {"allows_general": False}
    absent["quality_rubric"] = {
        "reference_answer": "当前绑定语料未收录该指定试卷，说明未找到，可以提出查找已收录年份或请用户提供试卷；不能虚构该卷原题和标准答案。",
        "evidence_groups": [], "verification": f"对{version}全部linear_algebra标题和正文查找2023-2024无匹配；仅确认指定资料未收录，不把候选是否为空当成正确性。",
        "must_not_claim": ["编造2023-2024原题", "用旧年份试卷冒充指定试卷"],
    }
    missing = add("la-diagonalization", suffix="-missing-work", query="我算这个矩阵的秩好像错了，能帮我找出哪一步错了吗？")
    missing["expected"] = {"allows_general": True}
    missing["quality_rubric"] = {
        "reference_answer": "请用户提供矩阵和自己的计算步骤，可简短说明会检查行变换或主元；在输入到来前不能指出一个虚构的具体错误。",
        "evidence_groups": [], "verification": "当前输入没有矩阵也没有计算过程，无法推断具体哪一步出错。允许简短通用建议，不要求拒答模板。",
        "must_not_claim": ["虚构用户矩阵", "虚构具体错误步骤"],
    }
    write("scenarios.json", {
        "contract_version": "v1", "dataset_status": "source_reviewed_authored_scenarios",
        "corpus_version": version, "quality_requires_review": True,
        "notes": f"{len(cases)} authored cases, not student logs. Multiturn executes actual first responses. Expected fields check mechanics only; no model output was used to tune labels.",
        "cases": cases,
    })
    print(json.dumps({"topics": len(topics), "retrieval_queries": len(entries), "courses": len(courses), "evidence_chunks": len(evidence), "scenarios": len(cases)}))


if __name__ == "__main__":
    main()
