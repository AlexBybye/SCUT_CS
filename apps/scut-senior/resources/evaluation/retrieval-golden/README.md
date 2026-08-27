# P0 检索评测 Golden Set（PLAN-2 阶段一 步骤 1）

本目录存放检索评测的**人工核对金标准**，是阶段一所有检索改造（BM25F、dense + RRF、
query 变体、rerank）的评测基线。格式契约见 `retrieval_eval.py` 模块 docstring。

## 文件组织

- 每门课程一个文件：`<course_id>.json`（与 `active.json` 的 `course_switches` 键一致）。
- `eval_runner --retrieval-only` 会加载本目录全部 `*.json`，逐条校验引用真实存在后
  跑检索，输出逐课程 `recall@5 / recall@20 / MRR / noise_rate` 报告。

## 单条格式

```json
{
  "query": "已知向量组的秩是多少",
  "expected_chunk_ids": ["linear-algebra-012:p1:q-linear-algebra-012-q3:c01"],
  "note": "历年题题干 -> 题目 chunk"
}
```

- `query`：学生自然会问的检索词，**不是** chunk 原文照抄。
- `expected_chunk_ids`：该 query 必须命中的 chunk_id（可多个，表示"都该进 top-K"）。
- `note`：标注来源类别（历年题题干→题目 chunk / 知识点名词→定义标题 chunk 等）。

## 标注规则（每门首批 ≥30 条，人工核对）

1. 来源用**历年题题干 → 题目 chunk**、**知识点名词 → 定义标题 chunk** 两类，人工核对。
2. chunk_id 必须真实存在于当前激活语料；跑 `--retrieval-only` 时引用缺失会 **fail-closed**。
3. `corpus_version` 记录标注时的激活版本；换模型/重建 candidate 后需重走校验（见 PLAN-2 §3 步骤 3）。

## 运行

```bash
# 项目 venv 下，从 apps/scut-senior 目录：
api/.venv/bin/python -m scut_senior_api.eval_runner \
  --retrieval-only \
  --golden resources/evaluation/retrieval-golden \
  --corpus-store .local/corpus-store \
  --report resources/evaluation/retrieval-baseline.json
```

`--min-score` 默认 6（沿用一期 `retrieval_min_score`），噪声率偏高时再据此重定标。

## 状态

- `linear_algebra.json`：**种子样例**（8 条，已验证 top-1 命中），用于打通机制；
  完整 ≥30 条人工标注待补（PLAN-2 §7 待确认事项 1：标注人力归属）。
- 其余 45 门课程：待标注。
