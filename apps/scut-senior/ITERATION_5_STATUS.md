# 迭代 5 状态：备考复习（exam_review）双路径、客观统计与私有输入隔离

日期：2026-08-21

开发分支：`iteration-5`（基于 `codex/repo-path-migration` @ `d2819b2`）

状态：`committed_local_green_external_evidence_pending`。本地全量 Python／Web 测试与契约导出通过；真实模型行为下的逐课程评测、真实 corpus 远端激活与生产部署证据仍缺失，不由本地测试替代。

## 本轮完成（按 SOP §4.2 顺序）

### 1. 契约先行

- `tests/python/test_exam_review_plan.py`（24 例）先于实现固化 SOP §10.3 必验场景：双路径优先级、诚实空统计、统计可回查来源、不输出命题概率／"必考"、课程包文件在运行前后哈希不变、运行时缓存保持关闭、worker 构建器无模型／BYOK 依赖。
- `TraceSafeResult` 新增安全字段 `review_path`（路径代码）与 `sample_years`（客观年份列表）；四个导出 schema 再生成并通过 `--check`。私有大纲／薄弱点原文永不进入 Trace。

### 2. 确定性规划器（新增 `api/src/scut_senior_api/exam_review.py`）

- 路径选择：`with_syllabus`＝用户大纲 > 课程资料 > 历年题 >（允许时）标记的通用知识；`without_syllabus`＝历年题 > 课程资料 >（允许时）通用知识。优先级链写入 `workflow_output.exam_review.priority_order`。
- 客观统计：只从已审核语料的事实（历年题 role 的 source 年份 + question 定位）计算样本年份、年份覆盖、题型分布与出现次数；题型仅从已审核标题关键词识别，无信息计入"未标注题型"。附录固定声明"不输出命题概率，也没有'必考'预测"。
- 知识点分层：按已审核标题栈取层（≤3 层）、按知识点组织题组与代表性真题（含资料位置 locator），排序依据（匹配薄弱点 / 真题客观出现次数 / 课程资料对应标题）写入 `order_reasons`。
- 有大纲路径计算大纲条目覆盖：未命中已审核标题的条目如实列入"未覆盖内容"；无大纲路径不计算覆盖缺口。
- AI 样题边界：固定声明"模型补充的练习样题均为 AI 生成、非历年真题"，并同步写入 `workflow_focus` 指令（样题必须放入以「AI 生成样题」开头的标题小节）。
- 输出有界：知识点 ≤12、每组真题 ≤8、统计题目清单 ≤64、大纲条目 ≤32。

### 3. 语料事实适配器（新增 `api/src/scut_senior_api/adapters/exam_facts.py`）

- `LocalCorpusExamFactsProvider`：经 active 指针绑定读取已验证 course pack（questions + sources 年份／role + heading index），路径遍历双重校验。
- `FixtureExamFactsProvider`：只读合成 fixture；复用 worker chunker 保证逐题标题栈与正式语料一致；无任何已审核来源的课程 fail-closed。
- 两个适配器均无模型调用、无 BYOK 依赖、只读不改写课程包（SOP §10.2"课程包构建不使用普通用户 BYOK"由架构保持 + 测试断言共同约束）。

### 4. Runtime 集成（`service.py`）

- 新节点 `exam_review_plan` 位于 retrieval 之前：失败或 flag 关闭时跳过（trace 记 `degradation_code=exam_review_facts_unavailable` 或完全不产生节点），绝不阻塞已通畅的五 Workflow 链路。
- 无大纲且无薄弱点时检索词不再为空：按路径合成确定性检索词（薄弱点 + 历年题客观题组主题），Bilibili 兜底词共用同一有效查询；有大纲路径检索语义与迭代 4 一致。
- 系统生成的"备考复习统计（系统生成）"附录在人译器与语气约束之后追加到 repository 回答块（确定性内容不被改写）；无 repository 块的诚实 insufficient 结果不注入。
- 结构化计划写入 `workflow_output.exam_review`（web 端严格校验只要求 record，向后兼容旧历史记录）。

### 5. 前端

- `web/src/examReviewPlan.ts` 防御式解析（形状不符整体隐藏面板）；`WorkflowResult.vue` 新增可折叠"备考复习计划（系统生成）"面板：路径徽标、证据顺序链、年份/题型客观计数、知识点分层（资料位置＋代表性真题）、复习建议、未覆盖内容警示与 AI 样题边界。
- `WorkflowDrawer.vue` 备考复习字段区新增双路径提示；`contracts.ts`／`workflowResultValidation.ts` 同步 Trace 白名单与新字段类型校验。
- Bundle 影响：JS gzip 154.84 → 161.64 kB（KaTeX 占大头，按需加载仍列为后续优化项）。

### 6. Feature flag 与配置

- `Settings.exam_review_plan_enabled`（env `SCUT_SENIOR_EXAM_REVIEW_PLAN_ENABLED`，默认 true）。关闭后 exam_review 与迭代 4 行为一致：无 plan 节点、无附录、检索词回退旧规则（契约测试锁定）。

## 验证证据

- Python：**511 passed**（迭代 4 重构基线 476 → +35：exam_review 契约 24 + workflow_focus 指令 1 + eval 用例扩展等；既有测试除 trace 节点序列契约外零改动）。
- Web：**91 passed**（76 → +15）；typecheck 通过；build 通过（JS 508.34 kB / gzip 161.64 kB，CSS 57.77 kB / gzip 14.59 kB）。
- 契约：`export_contracts --check` 通过（schema 因 TraceSafeResult 新增字段再生成）；evaluation-case schema 扩展两个 category 与可选 `syllabus`/`weak_topics`/`requires_exam_review_plan`/`review_path` 字段。
- 评测：`12 cases, 5 passed, 6 failed, 1 skipped`——3 个 exam_review case（fixture、有大纲、无大纲）全部诚实通过；6 个失败与迭代 4 基线完全相同（需真实 corpus 定位与真实模型行为），1 个跨课程按 flag 跳过。不伪造通过。
- 真实 corpus 本地冒烟（`.local/corpus-store`，不入库）：`probability_theory` 无大纲路径返回 55 道题、7 个年份（2013–2021）、填空/选择/未标注客观分布与可读题组；`engineering_math_analysis_1`、`discrete_mathematics` 的历年卷无题号标记，诚实返回空统计并声明"没有可统计的历年题"。

## 私有输入隔离（SOP §10.2/§10.3）

- 私有大纲／薄弱点只影响请求本人的计划排序与覆盖缺口；Trace 只含路径代码与客观计数；公共课程包在多次运行前后 SHA-256 不变（测试锁定）；`cache_policy` 保持 `runtime_cache_not_configured`，不存在跨用户缓存。
- 未覆盖条目是唯一的大纲派生回显，仅存入该用户自己的运行历史。

## 已知限制与诚实边界

1. **逐课程真实模型评测未完成**：评测执行器的 exam_review 断言基于 fixture+mock；真实模型下"AI 样题标记"依赖指令遵从，确定性层只能保证系统附录的边界声明，不能强制改写模型正文。（2026-08-22 部分解除：两条真实模型 exam_review 线上运行验证了指令遵从与解析兼容，见文末追加；逐课程 ×10 双路径 eval 仍未执行。）
2. **统计粒度受已审核语料限制**：题型只识别标题中明确写出的类型（未标注如实计数）；无 `<!-- question: -->` 标记的历年卷不产生题目级统计；知识点分组来自已审核标题结构，不是语义抽取。
3. ~~**health 端点仍返回 `"iteration": 3`**（既有滞后，本轮不改，避免破坏现有断言链）。~~ 已于 2026-08-22 解决：health 现返回 `"iteration": 5`，`iteration_status` 取值升级为带迭代号的 `iteration5_*` 自声明口径（见文末追加）。
4. KaTeX 体积问题沿用迭代 4 重构记录，未在本轮处理。
5. 分支基于 `codex/repo-path-migration`；另一并行 CI 修复工作流在检出同一分支期间把 `bdd8ab8`（npm 拉包超时加固）提交并推送到本分支，该提交不属于本迭代范围，本迭代未改动其内容。

## 下一步进入条件

- 受信 `master` 上重新构建并激活含题号标记的 corpus 后，用 `scut-senior-eval` 对 10 门课逐课程跑 exam_review 双路径；
- 真实平台模型额度恢复后补一次真实模型 exam_review 运行，验证指令遵从与解析兼容；（2026-08-22 已完成，见文末追加）
- ~~决定是否把 health 端点的 iteration 字段推进到 5（需同步更新既有断言）。~~ 已决定并执行（2026-08-22，见文末追加）。

## 追加（2026-08-22）：health iteration 推进到 5 与真实模型线上实测

### health 端点口径变更

- `"iteration"`：`3` → `5`。此前迭代 4/5 两轮均记录"字段停在 3 的滞后"，本轮随真实模型实测证据一并推进。
- `"iteration_status"` 取值升级为**带迭代号的自声明口径**：`iteration5_runtime_with_active_corpus` / `iteration5_fixture_runtime_active_corpus_required`，取代迭代 3 时代的历史取值 `local_runtime_with_active_corpus` / `local_fixture_runtime_active_corpus_required`。口径含义不变（仍由 active corpus 可用性二分），但状态字符串自声明所属迭代，后续迭代推进时不会再出现静默滞后。
- `"status": "ok"` 保持存活语义不变：语料与模型状态继续由 `iteration_status` 与 `capabilities` 承担。
- 断言同步更新：`test_iteration_3_runtime.py` 中原 `test_health_reports_iteration_three_without_claiming_active_corpus` 更名为 `test_health_reports_iteration_five_without_claiming_active_corpus`，断言 `iteration == 5` 与新状态值；全仓无其他代码引用旧取值（历史 STATUS 文档中的旧值作为当时快照保留，不改写）。

### 真实模型线上实测证据

- `.local/online.db` 两条 exam_review 真实运行均 `run_status=completed`：
  - `49ab1d7b`：`user_key / deepseek / deepseek-v4-flash`（BYOK）；
  - `c3263d68`：`platform_default / openrouter / nvidia/nemotron-3-super-120b-a12b:free`。
- 「AI 生成样题」小节按 workflow_focus 指令正确标注且首行声明"非历年真题"；回答正文围绕所问知识点（泊松分布）；未触发长度截断（BYOK `default_max_tokens=8192` 与截断提示路径就绪）。
- 诚实边界符合设计：检索仅命中历年卷（hit_count=1）→ citations 为空、`evidence=insufficient`、`answer_status=partial`，回答以通用补充展示并明确声明无可回查课程资料候选。
- 验证基线：Python **522 passed**；Web 94 passed + typecheck + build 通过。

### 本轮附带修复（同日）

- 流式断线语义分离：客户端连接中断不再取消运行（后台继续执行并持久化终态）；显式取消走新增 `POST /api/v1/workflow-runs/{run_id}/cancel`。
- 会话详情排除非终态尝试（后端过滤 + 前端防御跳过），修复运行中刷新触发 "invalid Workflow result run_status"。
- 全部 fetch 路径网络错误中文化，流式中断后自动轮询取回结果。
