# 来源核验的学习评测集 v2

2026-09-12，由Codex读取指定材料、推导答案并编写场景。此处的“核验”指具体记录中的有限结论，不代表原材料全文正确、所有相关证据均已穷尽或独立专家双审。问题是贴近实际学习需求的自拟场景，不是真实用户日志。

## 内容

| 文件 | 用途 |
| --- | --- |
| annotations.json | 25个主题的两种问法、证据组、参考答案、核验理由、典型错误；主要维护入口 |
| retrieval.json | 50条检索问题，14门课、27个原始证据片段；含来源路径、原文及指纹 |
| scenarios.json | 22条端到端场景：五类Workflow、真实错答、临时材料、时间预算、多轮、精确查题、跨课、资料缺失、输入不足 |
| legacy-audit.json | 旧1,380条问题逐条引用存在性、文本形态与指纹检查；不是自动语义认证 |
| legacy-scenarios-audit.json | 旧12条真实语料场景和20条备考扫描的逐条处置理由 |
| AUDIT.md | 发现、事实核验方法、范围与未覆盖项 |
| baseline-bm25f.json / baseline-hybrid.json | 新集上的首轮纯检索基线，无在线回答模型调用 |

## 判断什么才算正确

1. **资料定位：** chunk存在、对应正确课程/来源，原文没有在核验后变化。
2. **内容支持：** 问题限定到材料中可读的知识；公式残缺、只剩图片、题号错配都不能凭编号认定正确。
3. **答案正确：** 引用只是依据；按reference_answer与verification独立判断数学、代码、逻辑。source_correction中的来源是待反驳对象。
4. **任务完成：** 回答当前追问、解释实际错因、满足复习时长、区分两门课，而非仅输出answered/sufficient。

reference_answer是语义要点，允许等价表达、正确的其他推导。pitfalls不应当通过简单关键词命中判错——例如引用错误说法再反驳应通过。暂不自动用另一个模型评分，避免用未经验证的裁判替代核验。

证据组内是替代关系；组间是不同信息需要。未列出的chunk是unjudged，不是负例。因此已知证据覆盖与MRR只是非穷尽标注下的诊断值，不计算“未标注=噪声”的比例。看到合理的新候选，读原文、记下理由后增加标注；统一升版并重算所有对照，不能只为某条链路变绿而改答案。

## 使用

在apps/scut-senior目录下用项目Python运行。Windows为`api/.venv/Scripts/python.exe`，其他系统使用对应虚拟环境Python。

```text
python -m scut_senior_api.learning_eval --validate-only
python -m scut_senior_api.learning_eval --split dev --report .local/evaluation/reviewed-dev.json
python -m scut_senior_api.learning_eval --split validation --report .local/evaluation/reviewed-validation.json
python -m scut_senior_api.learning_eval --embedding-model-dir .local/models/bge-small-zh-v1.5 --report .local/evaluation/reviewed-hybrid.json
```

默认只运行本地检索，不调用在线回答模型。当前dev为26题，validation为24题；同一来源及其关联证据、同主题改写不跨集合。这个validation由同一作者看过，且此次跑了全量基线，属于来源隔离的验证集，不是从未接触的盲测集。上线决策还应收集新的真实问题作为外部验证。

端到端仍使用现有eval_runner，指定`--cases resources/evaluation/reviewed-v2/scenarios.json`。`--local-corpus`加默认Mock只验证运行机制，不能形成真实回答质量结论；真实模型沿用其provider/model参数。没有提供参考答案给被测模型，rubric只进入结果报告。多轮场景先实际运行前一问，再发送追问；不注入虚构assistant答案。

报告中的`outcome`仅表示管线检查结果，`quality_outcome=not_reviewed`表示尚未按rubric核验。报告附最终正文、引用及Workflow结果，便于逐题审阅。跨课程在功能开启时真实执行；关闭时明确skipped。临时材料或资料缺失任务未指定引用要求时，评测器不额外要求“必须引用”或“禁止引用”。

修改annotations后，运行`python scripts/build_reviewed_evaluation.py`重新生成数据；更新旧集检查用`python scripts/audit_evaluation_sets.py`。改动证据或答案须说明原因，不用生成脚本自动创造审核结论。语料版本或来源变更时，先核对受影响题目再重新生成指纹。

## 本轮结果

| 策略 | 已知证据组覆盖@5 | @20 | known-positive MRR |
| --- | ---: | ---: | ---: |
| BM25F | 0.660000 | 0.860000 | 0.511547 |
| 旧Hybrid | 0.660000 | 0.860000 | 0.511547 |

min_score=1.0，top20，50题。单轮耗时包含首次载入，不作为稳定P95或线上时延结论。新旧集不可直接比较绝对分数。没有执行新的在线回答实验。

14门课的向量资产均存在且有数据。两组有5题的top20列表不同，只是已知正例指标相同，不能称两种检索完全等价。

评测相关回归32 passed。22条新场景已在真实语料+Mock模型下做运行检查：20条管线通过、2条失败、0条跳过；跨课程已实际执行。失败为`reviewed-os-states`与`reviewed-network-ack-followup`触发现有URL Guard，保留失败记录，没有为使其变绿改题。全部22条语义质量仍标记not_reviewed；Mock输出不代表真实模型能力。本地报告为`.local/evaluation/reviewed-v2-mock-smoke.json`（相对应用根目录）。
