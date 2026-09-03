# SCUT 老学长 AB 分支优化计划

版本：0.1（基于最新 AB 实跑后的收敛方案）
状态：**P0/P1 最小实现及本轮两项修复已完成本地回归；真实模型合并门槛尚未验证**。

本文只针对 `ab-test/agent-action-shadow`。它不是 PLAN-2 的替代文档，也不是
把系统扩展成通用 Agent 平台的方案。目标是解释当前 AB 分支到底做了什么，保留
已经证明有价值的证据增强，同时消除额外模型调用带来的延迟、重试和输出冗余。

## 1. 结论与边界

### 1.1 当前结论

当前 AB 分支是“受限模型决策适配器 + 原有同步运行时”的 post-retrieval 实验：

```text
请求校验 → 确定性计划/首轮检索 → post_retrieval 模型决策
       → 直接生成，或一次查询改写检索 → 引用 Guard → 收尾与持久化
```

它借鉴了 EventStream 的事件账本、Reducer 和 Observe → Decide → Act 形式，
但还不是一个由 Action 驱动执行的完整 EventStream Loop：

- `decision_produced` 会记录模型选择的动作；
- 服务端仍按既定代码路径执行检索和生成；
- 固定首轮检索和最终回答阶段由服务端预期动作执行，不额外询问模型；
- 首轮检索后，模型只在 `generate_answer` 与
  `retrieve_with_query_rewrite` 之间选择；后者通过 Action Guard 后才执行第二次检索；
- `finish`、`ask_clarification` 暂未暴露给模型，避免出现无执行语义的动作；
- 不合规模型动作会记录 `action_rejected` 并显式回退到服务端动作。

因此，旧实跑仍不能把引用数量提升归因给 Agent 决策；当时成功样本的
`decision_call_count=0`。本轮改造后的归因必须同时看到决策调用、被接受的模型动作
以及对应执行事件，不能再由最终引用数倒推。

### 1.2 版本目标

本计划只做四件事：

1. 让决策记录与实际执行一致，或者明确关闭模型决策；
2. 降低不必要的决策调用、回答重试和附录冗余；
3. 保留 AB 已观察到的证据覆盖和知识点组织能力；
4. 建立可归因、可复现、不过度依赖供应商统计口径的下一轮实验。

### 1.3 明确不做

- 不引入 LangChain、ReAct 框架、独立 Planner、消息队列或新的常驻服务；
- 不把工具开放给模型直接调用；
- 不改变五类 Workflow、课程权限、引用 Guard 和本地单机部署边界；
- 不在本计划中重新设计前端 Trace 或学生侧复杂 Agent 调试面板。

## 2. 当前实现地图

### 2.1 Harness 与 Workflow 边界

入口为 `main.py#create_app`，由 `HARNESS_REGISTRY.resolve_preset()` 将请求的
`workflow_type` 绑定到一个不可变 `AgentPreset`。Preset 提供：

- Workflow 与 focus strategy 的一一映射；
- 允许工具的元数据；
- 输入模态与模型兼容性检查；
- 课程与权限边界的运行前置条件。

工具目录中的 `model_callable=False` 仍然有效：课程检索、证据定位、Bilibili
搜索和临时材料读取均由服务端编排，模型不能直接发起工具调用。

### 2.2 Agent 内核

`agent_loop.py` 包含：

- `WORKFLOW_ACTIONS`：按 Workflow 的动作白名单（当前仅暴露有执行语义的三类动作）；
- `ModelAgentDecision`：用同一个 `ModelGateway` 询问下一个 Action；
- `RuleBasedAgentDecision`：模型决策关闭或解析失败时的确定性 fallback；
- `AgentState` 与 `reduce_agent_event()`：不可变状态折叠；
- `AgentBudget`：步骤、检索轮次、查询改写、同动作重试、Guard 重试和运行时限；
- `parse_model_action()`：只接受单个动作 token，解析失败时 fail-closed。

当前 `agent_decision_mode` 由环境变量
`SCUT_SENIOR_AGENT_DECISION_MODE` 控制，默认值仍为 `rule`。AB 实跑必须显式打开
`model`，否则运行的是 master 侧的确定性策略。

### 2.3 事件流与账本

`workflow_stream.py` 负责请求级 NDJSON 顺序、取消和终态竞争；`agent` 事件只是
可选的额外流事件，默认不发送。SQLite 中的 `agent_events` 和
`agent_state_snapshots` 负责单个 run 的追加事件与状态快照，并在写入时进行重放
一致性校验。

这部分是运行审计基础，不等于存在一个异步事件总线。当前运行主逻辑仍在
`service.py#IterationZeroService._run` 中同步推进。

### 2.4 实际运行路径

`service.py#_run` 的关键顺序如下：

1. 校验用户、课程、模型、Workflow 和历史上下文；
2. 初始化 `RunStateMachine`、`AgentState`，保存 running run；
3. `exam_review` 时先生成确定性复习计划；
4. 服务端确定性执行一次检索，不调用完整模型询问 `retrieve`；
5. 执行课程检索、私有知识合并、课程授权校验和来源去重；
6. `model` 模式在首轮检索后询问一次轻量决策；选择改写时执行一次有界二次检索，
   选择生成时直接继续；`rule` 模式保留原有空结果追问补锚；
7. 进入回答模型；固定阶段不重复调用完整模型询问 `generate_answer`；
8. 调用 OpenRouter、智谱、BYOK 或 Mock 模型生成回答；
9. 解析 Markdown/JSON、全角引用和 `scut-meta`；
10. 执行引用、课程范围、URL 和 AnswerBlock Guard；
11. Guard 或供应商输出错误时最多重试一次；
12. 可选执行 Humanizer 和主回答语气控制；
13. `exam_review` 追加确定性统计附录；
14. 根据受控关键词执行一次 Bilibili 匿名搜索；
15. 保存回答、引用、Trace、外部资源和 Agent 状态。

### 2.5 输出组成

最终学生可见内容由三部分组成：

```text
模型正文
  + 可选 Humanizer 后的正文
  + exam_review 系统附录
```

其中附录由 `exam_review.py#render_exam_review_appendix()` 确定性生成，包含范围
说明、证据边界、历年题统计、知识点分层、代表性真题、复习建议和未覆盖内容。
这解释了 AB 与 master 都出现的“未覆盖内容重复用户大纲”和统计篇幅偏大的问题。

## 3. 实跑证据的正确解读

### 3.1 可以保留的观察

- AB 在这两次样本中的引用数量和接受数高于 master；
- AB 的章节组织和“复习顺序 + 易错点”表达更规整；
- master 的运行路径更短，没有模型输出重试；
- 两边课程越权均为 0，证据状态均为 `sufficient`；
- 两边都存在附录冗余，说明这是共同输出链路问题，不是单纯 AB 问题。

### 3.2 不能直接归因的观察

AB 的引用提升不能直接证明是模型 Action 决策带来的，因为当前 Action 并未真正
改变检索和生成分支。下一轮必须增加“决定动作”和“实际执行动作”的对应证据，
再讨论 Agent 是否有收益。

### 3.3 数据口径提醒

表格中的耗时显示：

```text
AB       84.77 秒
AB-2     90.83 秒
master   80.17 秒
master-2 82.59 秒
```

按表格计算，AB 比 master 慢约 5.7%～11.8%，不能同时表述为“接近 master 的
三倍”。后续以原始运行记录和统一计算方法为准。

`input token`、`未命中缓存` 和 `output token` 在四次运行中的统计形态不一致，
例如出现 input token 为 0 的记录。因此它们只能作为供应商观测字段，不能在没有
统一账单口径时直接做精确成本归因。

## 4. P0：必须先沉淀的最小修复

P0 的目标不是增加 Agent 能力，而是让实验结果可信、运行成本可控。

### P0-1 决策与执行一致性

在 `service.py#_run` 中增加显式的动作执行边界：

```text
decision_produced
  → Action Guard
  → action_executed
  → observation_recorded
```

最小方案有两种，优先采用第一种：

1. 只保留当前已实现的 `retrieve`、`retrieve_with_query_rewrite`、
   `generate_answer`，让它们真正决定对应执行函数；
2. 如果暂时不实现 `finish`、`ask_clarification`，就从当前实验白名单中移除，
   不让模型返回一个服务端不会执行的动作。

如果模型动作不适合当前阶段，必须：

- 写入 `action_rejected`；
- 进入确定性的阶段 fallback；
- 记录 `requested_action` 和 `executed_action`；
- 不把不一致状态当成正常成功运行。

验收要求：正常路径中 `decision_produced.action` 与
`action_executed.action` 一致；发生 fallback 时有明确 Trace 原因。

### P0-2 移除完整模型的重复决策调用

旧实现复用回答模型和完整请求构造，曾让一次 Action 判断接近一次完整回答的成本。
本轮已把 OpenRouter 决策调用拆为独立紧凑请求：只传问题摘要、证据数量和来源标题，
使用 `max_tokens=16`、`temperature=0`，不发送来源正文和完整历史。它仍复用平台
模型身份和额度，不是新的常驻决策服务。

已采用的做法：

- 第一次检索固定由服务端执行，不调用模型决定 `retrieve`；
- 首轮证据返回后，只调用一次轻量决策器判断直接生成还是补检索；
- 选择生成后直接进入回答，选择改写时最多补一次检索。

模型决策实验保持以下边界：

- 决策请求路径、token 预算和调用计数与回答请求分离；
- 当前仍复用所选平台模型身份，是否另选小模型留给实测后决定；
- 决策请求只传结构化观察量，不传完整 source 正文；
- `max_tokens` 使用很小的控制预算；
- temperature 设为 0；
- 决策调用失败或输出不合规时使用显式确定性 fallback。

P0 不要求引入新的模型供应商，也不要求建立新的服务。

### P0-3 分离重试类型和模型调用计数

当前 `retry_count` 不能清楚区分回答重试、Guard 重试、供应商重试和再次决策。
应增加运行级内部指标或 Trace 字段：

```text
decision_call_count
model_action_accepted_count
answer_call_count
provider_retry_count
guard_retry_count
decision_fallback_count
action_rejection_count
```

其中 `decision_call_count` 只表示尝试过模型决策；只有
`model_action_accepted_count` 才表示一个合法、阶段适配的模型 Action 被执行。这些
字段只用于 Trace、评测和服务端诊断，不需要变成学生侧复杂 UI。

同时修正预算口径：如果文档继续声明“Guard 重试计入 max_steps”，就让
`guard_retry_recorded` 同步增加 `step_count`；否则修改文档，明确它是独立计数。

### P0-4 Guard 重试必须携带修复原因

Guard 失败后的第二次回答不能继续使用完全相同的上下文。增加请求级、服务端内部
的修复提示，例如：

```text
上一次回答未通过引用校验：未知引用 [S7]；请只修复引用问题，保持主题和结构不变。
```

修复提示：

- 只进入模型调用上下文；
- 不进入学生可见正文；
- 不改变 Workflow 和课程范围；
- 仍受一次 Guard 重试上限约束。

### P0-5 压缩 exam_review 学生可见附录

系统计划与模型正文应明确分工：

```text
系统：复习顺序、统计、未覆盖项、证据边界
模型：解释顺序原因、易错点、记忆方法和练习方式
```

学生可见附录只保留：

- 短的复习顺序；
- 少量代表性统计；
- 2～4 条代表性引用；
- 未覆盖项的数量和短名称。

详细题组、年份分布和完整统计继续放入 `workflow_output.exam_review` 与 Trace。

“未覆盖内容”不得重新复制整段用户大纲。优先输出：

```text
未覆盖 3 项：矩阵分块、Jordan 标准形、正定判定
```

并在模型 prompt 中明确禁止重新粘贴完整大纲和系统统计。

### P0-6 让实验具备因果可比性

下一轮至少保留四个对照组：

| 组别 | 决策器              | 目的                |
| ---- | ------------------- | ------------------- |
| A    | 无，固定链路        | master 基线         |
| B    | 有，但不驱动执行    | 测量纯额外调用成本  |
| C    | 有，真正驱动 Action | 测量 Agent 行为收益 |
| D    | 确定性/轻量决策     | 测量收益成本比      |

每组使用相同的请求、课程包、模型、温度和检索配置。至少记录：

```text
P50/P95 总耗时
决策调用次数
回答调用次数
Guard/供应商重试次数
候选数、接受引用数、引用接受率
回答字符数
供应商 token 字段与本地调用计数
成本字段
决定动作、执行动作及 fallback 原因
```

四次已有运行作为历史观察保留，不作为长期稳定性结论。

## 5. P1：在 P0 稳定后再考虑的改造

P0 已通过后端全量回归（662 passed，1 warning）及 AB 专项回归。当前 P1 只沿着
已有同步执行表收敛，不扩展为通用 Agent 平台。

### P1-1 最小 Action Executor（已以兼容执行边界落地）

服务端已形成等价的最小执行边界：

```text
retrieve                     → execute_retrieval
retrieve_with_query_rewrite → execute_query_rewrite
generate_answer              → execute_generation
finish                       → finish_run
```

查询改写动作在调用检索前完成决策校验，固定检索/生成不再进行冗余决策调用。
不增加通用插件发现、不增加动态工具注册、不增加跨运行任务队列。

### P1-2 证据驱动的有限循环（当前实现已满足上限，保留后续观测）

对于 `exam_review`，运行时只支持以下有限路径：

```text
retrieve
  → 证据足够 → generate_answer
  → 证据不足且未超限 → retrieve_with_query_rewrite
  → 仍不足 → bounded insufficient_evidence
```

不引入自由 ReAct，也不允许模型无限决定下一步。

### P1-3 统一输出责任

对 `exam_review` 的模型 prompt、附录渲染和结果契约做一次责任收敛：

- 模型不复制用户大纲；
- 模型不重复完整统计；
- 系统计划只生成一次；
- 详细统计从正文移到结果元数据或折叠区域；
- 引用仍由现有 Guard 最终裁决。

### P1-4 继续保留的证据增强

以下能力不因关闭模型决策而回滚：

- exam_review 确定性计划；
- 历年题标题和知识点检索锚点；
- 混合检索与规则重排；
- `【S1】` / `[S1]` 兼容解析；
- Bilibili 关键词中的课程名 + 聚焦知识点；
- 课程越权、引用重复和未知编号的 fail-closed Guard。

这些能力应与“是否启用模型 Action 决策”分开配置和评测。

## 6. P2：仅在证据支持时做的增强

以下事项不作为当前 AB 优化的前置条件：

- 更复杂的上下文压缩或自动摘要；
- 独立的决策模型服务；
- 多 Agent 协作；
- 在线学习或自动调参；
- 复杂的学生侧 Agent 可视化；
- 以供应商 token 统计为唯一成本真相；
- 自动根据模型回答生成新的课程事实。

如果 P0/P1 已证明轻量决策能在不增加明显 P95 的情况下提高引用接受率，再单独
提出小范围 P2 变更。

## 7. 验收与止损

### 7.1 P0 验收

- 决策动作与执行动作一致，或明确记录 fallback/rejection；
- 正常 exam_review 路径不再为固定阶段重复调用完整回答模型；
- 决策、回答、供应商和 Guard 重试可以分别统计；
- Guard 重试携带有限的修复原因；
- “未覆盖内容”不再整段复制用户大纲；
- 学生可见统计明显缩短，但详细结果仍可从 `workflow_output` 追溯；
- 既有课程范围、引用 Guard、Bilibili 分离和旧 NDJSON 兼容测试保持通过。

### 7.2 P1 验收

- `action_executed` 确实由决策结果驱动；
- 证据不足最多补一次检索；
- 证据仍不足时返回有边界的 insufficient evidence，而不是继续空转；
- `finish` 和 `ask_clarification` 若重新加入白名单，均有真实执行和持久化语义；
- 事件重放状态与终态快照一致。

### 7.3 止损点

出现以下任一情况时，关闭 `agent_decision_mode=model`，保留确定性链路和证据增强：

- P95 延迟持续高于 master 且无引用收益；
- 决策动作与执行动作不一致；
- Guard 或供应商重试率上升；
- 事件快照与重放不一致；
- 输出长度没有下降或附录仍重复大纲；
- 引用提升无法在成对实验中复现。

## 8. 推荐实施顺序

```text
P0-1 先统一 Action 与实际执行
  → P0-2 去掉固定阶段的完整模型决策
  → P0-3/P0-4 补齐重试与 Guard 观测
  → P0-5 压缩 exam_review 输出
  → P0-6 做四组可归因实验
  → 只有有收益时进入 P1 最小 Action Executor
```

最终是否合并回 master，不以“AB 引用数曾经更高”为单一条件，而以以下组合为准：

```text
引用接受率不下降
并且 P95 延迟、回答长度、重试次数和成本接近 master
```

在达到该条件前，master 继续作为线上效率基线；AB 只保留经过单独验证的证据增强
与输出收敛改动。

## 9. 本轮实施记录

截至当前工作树，本计划的 P0 已落地并完成回归：

- 固定检索/生成阶段不再调用完整模型询问 Action；
- 查询改写在第二次检索前决策，错误 Action 会记录拒绝并回退；
- `decision_call_count`、`model_action_accepted_count`、`answer_call_count`、
  供应商/Guard 重试及 fallback/rejection 已进入安全 Trace；
- Guard 重试携带服务端内部修复原因，并计入统一步骤预算；
- `exam_review` 的未覆盖内容已压缩为数量与短名称，完整结构化明细仍可追溯；
- 评测 runner 支持 `--agent-decision-mode rule|model`，每条用例输出受限运行指标，
  可复用同一请求集做成对比较；
- AB 专项测试与后端全量测试均通过（当前为 673 passed，1 warning；警告来自现有
  Starlette/httpx 依赖兼容提示）。

新增注入式回归已经覆盖正常 `generate_answer`、正常查询改写、阶段不兼容 Action、
解析失败 fallback 和 3/4 软水位跳过。正常可达样本可稳定得到
`decision_call_count=1` 与 `model_action_accepted_count=1`；选择直接生成时只有一次
检索，选择改写时恰好两次检索。这里证明的是代码路径和归因口径，不是供应商真实
延迟或引用收益。

P1 的最小范围已完成：有限执行边界、一次查询改写上限和输出责任收敛均复用现有
同步运行时；不继续扩展为通用 Action 平台。当前实现已足够支撑下一轮对照实验。
只有当成对实验显示轻量决策在 P95、重试和回答长度接近 master 的前提下提高引用
接受率，才再提出更细的 P1 行为改动。

## 10. 真实 NVIDIA 修复后对照（2026-09-03）

使用同一个本地 corpus、同一份线性代数考试大纲和
`nvidia/nemotron-3-super-120b-a12b:free`，按 master/AB 交替顺序各运行三次。
结果只作为当前小样本，不扩展为长期成功率：

| 分支 | 完成运行 | 有引用回答 | 成功样本耗时 | 成功样本引用 |
| ---- | -------- | ---------- | ------------ | ------------ |
| master | 3/3 | 1/3 | 64.434s、65.664s、47.926s | 4、0、0 |
| AB | 2/3 | 2/2 | 120.906s、27.716s | 5、2 |

AB 未完成的一次发生在模型目录健康检查阶段，现已从误导性的 `ModelNotRegistered`
改为 `ModelTemporarilyUnavailable` / HTTP 503。两次 AB 成功样本均为：

```text
decision_call_count = 0
provider_retry_count = 0
guard_retry_count = 0
```

因此本轮可以证明：

- 固定生成阶段不再产生额外决策调用；
- `generate_answer` 现在有对应的 `action_executed` 与 `observation_recorded`；
- AB 两次成功输出均通过引用 Guard，但不能把这一结果归因给模型 Action 决策；
- NVIDIA 免费通道仍有明显可用性和延迟波动，当前不满足稳定合并条件。

另外增加了一条有边界的证据修复：`exam_review` 已检索到候选但首次回答零引用时，
只补一次带允许编号的内部修复请求；第二次仍无引用则保留诚实的
`partial/insufficient`，不继续循环，也不由服务端伪造引用。该路径已由确定性集成测试
覆盖，本次真实 AB 成功样本首次生成已有引用，所以没有额外消耗第二次模型调用。

真实运行也暴露出系统附录仍占据过多篇幅：原渲染会展示最多 10 份试卷、每份最多
8 个题号，并把较多建议和未覆盖项放进学生正文。最终收敛为：

- 学生可见题组最多 4 组，每组最多 3 个代表题号；
- 复习建议最多 4 条；
- 未覆盖内容最多展示 3 个短摘要；
- 完整题组、155 道题结构和未覆盖明细仍保留在 `workflow_output.exam_review`，不丢失
  审计与导出能力。

将两次真实 AB 成功结果重放到新渲染器后，附录收敛带来的预计正文变化为：

```text
AB-1：4722 → 2810 字符，减少 1912
AB-3：4482 → 2570 字符，减少 1912
```

这是对已保存结果的确定性重渲染，不是重新调用模型，因此只证明输出冗余已被压缩，
不作为线上耗时、模型稳定性或回答质量的新样本。

## 11. DeepSeek V4 Flash 限额对照（2026-09-03）

成本约束为 master、AB 各两个 Workflow 运行，不做失败补跑。两边都使用 DeepSeek
供应商的 `deepseek-v4-flash`、同一份线性代数请求和本地 corpus；凭据与在线数据库
只通过临时数据库副本读取，未写入线上历史。

| 分支 | 轮次 | 结果 | 耗时 | 说明 |
| ---- | ---- | ---- | ---- | ---- |
| master | 1/2 | 中止 | 37.067s | 凭据口径确认时人工中止，可能已到达供应商，不补跑 |
| master | 2/2 | 504 | 121.497s | `byok_provider_timeout`，没有可用回答 |
| AB | 1/2 | 409 | 145.721s | 推理内容耗尽输出预算，最终正文为空；随后越过 120s Agent 预算 |
| AB | 2/2 | 成功 | 17.095s | `answered/sufficient`，5 条引用，3692 字符 |

AB 成功样本只有一次回答调用，`decision_call_count`、供应商重试和 Guard 重试均为
0；事件顺序完整结束。因此它再次证明固定 `exam_review` 路径没有额外 Action 模型
成本，但仍不能证明模型决策提高了引用覆盖。

成功回答本身仍有两个质量问题：附录占 1172/3692 字符，“未覆盖内容”虽然限为
3 个摘要，却仍是截断后的大纲原文片段，P0-5 的“短名称”只完成限长、尚未完成语义
提取；正文还错误地声称 `λI-A` 与 `A-λI` 会让特征向量符号相反，实际上两者互为
相反矩阵且零空间相同。现有引用 Guard 只能确认引用编号属于候选，不能把
`sufficient` 解释为数学事实或相邻说法已经通过语义核验。

本组无法比较两边回答质量或稳定延迟：master 没有成功回答，样本也只有两轮。它新
暴露了三个运行边界：120 秒 Agent 预算目前不能中止正在进行的供应商请求；推理模型
可能用尽 16384 token 预算而不给最终正文；“两个 Workflow 运行”也不一定等于两个
上游 HTTP 尝试，因为服务端可能在单次运行内执行受限供应商重试。后续若继续做成本
受限实验，应同时限制 Workflow 次数和上游调用次数，并先验证 DeepSeek 的推理/最终
正文预算配置，同时把正在进行的供应商请求纳入真正的墙钟超时；在此之前不以本组
结果改变合并结论。

## 12. 预算收敛与 Action 实验口径

DeepSeek 对照后不修改既有错误分类，预算按以下最小规则收敛：

- Agent 最大运行时长保持 120 秒，90 秒为 3/4 软水位；
- 控制权回到运行时且已超过软水位后，不再启动可选查询改写、供应商重试、引用修复
  或 Humanizer，直接使用已有结果继续收尾；
- 单个 Workflow 最多两次回答调用，避免供应商重试后再叠加 Guard 修复成为第三次调用；
- BYOK 单次 `max_tokens` 从 16384 收敛到 12288；通用 OpenAI-compatible 请求不再
  发送并非所有供应商都支持的 `reasoning_effort`。当前非流式接口不能在调用中实时
  观察“已使用 3/4 token”，因此使用调用前硬上限替代伪实时判断；
- BYOK 请求的总墙钟上限保持 120 秒，不收紧为 60 秒。

旧成功样本的 `decision_call_count=0` 不是统计错误，而是旧节点只允许在“首检为空、
有历史、无 exam_plan”时触发，正常 `exam_review` 结构上不可达。本轮把真正存在选择
意义的节点放在首轮检索之后：模型只决定“直接生成”还是“补一次改写检索”。这使
正常复习样本可达，但不会让模型接管首轮检索、课程范围、工具参数或最终终态。

后续对照仍需拆开看：

1. `decision_call_count=1`：确实发起过模型决策；
2. `model_action_accepted_count=1`：返回值合法且适合当前阶段；
3. `decision_source=model` 与后续 `action_executed` 一致：模型 Action 确实驱动执行；
4. 只有第 3 项成立后，引用候选或引用接受率变化才有资格进入因果比较。

解析失败、上游失败或非法 Action 都回退 `generate_answer`，并分别记录 fallback 或
rejection；这种成功回答不能记作模型 Action 成功。进入 90 秒软水位后不再发起该
可选决策，120 秒硬上限保持不变。

## 13. 自定义 BYOK 连接

BYOK 已从四组固定供应商/模型改为用户私有的 OpenAI-compatible 连接。用户保存：

```text
连接 ID + 显示名称 + HTTPS Base URL + 模型 ID + API Key
```

服务端继续加密保存 Key；前端和查询接口只拿到脱敏状态。Workflow 仍以
`provider_id + model_id` 选择连接，其中 `provider_id` 为兼容现有协议保留的字段名，
语义已经变为用户自定义连接 ID。旧四家凭据通过 `0018` 迁移补齐原 endpoint 和模型
信息，密文、nonce、版本和到期时间保持不变。

P0 只支持 `openai_chat_completions`，调用路径为
`<base_url>/chat/completions`。服务端要求 HTTPS，拒绝 URL 账号密码、query、fragment、
localhost、明显的私网/链路本地字面地址，并继续禁止重定向。`/api/v1/models` 不发布
用户私有连接；登录后通过 `/api/v1/model-credentials` 获取自己的脱敏连接列表。

当前边界需要如实保留：尚未实现 `/models` 自动发现，也没有在传输层完成可抵御 DNS
rebinding 的 IP 固定，因此不能宣称任意 Base URL 已具备完整 SSRF 防护；面向不可信
公网用户开放前仍需补齐。Agent Action 决策当前使用平台决策模型，用户 BYOK 只负责
回答生成，二者的调用次数和成本不能混为一谈。

本轮没有追加真实供应商调用：先前获准的 DeepSeek 实网轮次已经用完。自定义连接、
迁移保密性、动态模型选择和 Agent Action 可达性均由注入 HTTP 与本地回归验证，不能
冒充新的线上稳定性或回答质量证据。
