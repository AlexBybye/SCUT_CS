# 评测入口

2026-09-12起，新实验使用[来源核验评测集reviewed-v2](reviewed-v2/README.md)，优化规划见[下一轮实验方案](../../docs/senior-ab/next-experiments.md)。

- `eval_runner --retrieval-only --report ...`默认使用新版已知证据组指标。
- 复现旧指标需显式指定`--golden resources/evaluation/retrieval-golden`；旧集不是已经确认正确的语义金标准。
- 端到端使用`--cases resources/evaluation/reviewed-v2/scenarios.json`。`outcome`只检查管线合同，`quality_outcome`另行核验。
- 原`scut-real-corpus-cases.json`保留为历史数据，12条均有审查理由；`exam-review-sweep.cases.json`的20条仅作流程冒烟。不能把历史状态/引用通过率当成答案准确率。
- 历史报告保持原样，新旧数据集分数不可直接相减宣称改进。

完整发现、已验证答案和覆盖限制见[核验报告](reviewed-v2/AUDIT.md)。
