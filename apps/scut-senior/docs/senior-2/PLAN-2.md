# SCUT 老学长二期迭代 PLAN-2：三阶段 SOP（Agent 化与混合检索）

版本：1.0（三阶段 SOP 定型，建议稿）

状态：**PLAN-1 定义的一期已开发完成**——五类固定 Workflow、HARNESS_REGISTRY 受控工具注册表、确定性词法 RAG、引用/来源 Guard、配额与 BYOK 目录、NDJSON 流式前端均已落地并有测试覆盖。本文是**老学长二期迭代计划**，按三阶段 SOP 落地：地基（统一输入 + 混合检索）、内核（EventStream Agent Loop）、出口（工具服务化与上线标定）。它不替代 PLAN-1 的任何冻结决策；与 PLAN-1 冲突时以 PLAN-1 为准。

> **替代说明**：本文整体替换原 v0.1《检索升级与最小部署配置 PLAN-2（建议稿）》：检索分级改造并入 §3（阶段一），最小部署规格并入 §6，待确认事项并入 §7。
>
> **v0.2 → v0.3 范式收敛**：运行机制收敛为一套——EventStream + Reducer 作为承载方式，受限单步决策作为行为方式；不再叠加独立的 LLM Planner、ReAct 框架或 Replan 循环。`exam_review` 的计划是确定性业务规则。"ReAct"一词仅作为 Observe → Decide → Act 行为模式的解释保留，不再是架构组件名。
>
> **v0.3 → v0.4 预算重构**：Agent 预算只防死循环，不管自然输入输出——删除全部 per-call / 累计 Token 限额；输入由请求合同管（question ≤2 万字符、problem ≤4 万字符、材料 ≤10 万字符），输出由生成参数管。平台免费档三模型的配额限制独立成层，在 ModelGateway 配额层执行（对齐 PLAN-1 §1.6）；BYOK 只保留死循环防线。
>
> **v0.5 → v1.0 三阶段 SOP 重组**：原 Phase 1~5 重排为三个阶段——阶段一（统一输入 + 混合检索）、阶段二（EventStream Agent Loop + exam_review 确定性计划）、阶段三（工具服务化 + 上线标定）；每阶段按「目标 / 前置依赖 / 实施步骤 / 验收 DoD / 止损回滚点」SOP 模板展开。新增一条贯穿不变量：**二期全程仍不部署服务器**。
>
> **写作动机**：一期已交付的价值重心在"可验证"一侧——locator 定位合同、引用 Guard、min_score 地板、契约评测全部闭环；已知短板同样明确：召回只有单课程词法加权打分（无 IDF、无语义通道），执行是一次性链路（证据缺口无法驱动下一步动作）。二期据此立两条主线：混合检索补"召回聪明"，EventStream Agent Loop 补"证据驱动的动态决策"，全程保持一期 harness 边界不动摇。

## 1. 目标定位

在已交付的一期之上，二期把系统迭代为**面向课程学习的 EventStream-driven Agent Runtime**：

```text
统一输入 → 自动任务路由 → EventStream Agent Loop
  → 受限单步决策（Action 或 Final）
  → 混合检索 RAG → 服务端工具执行 → Observation/证据回流
  → 引用与安全 Guard → 可终止的最终回答
```

六条不变量贯穿三个阶段：

1. 课程边界不可越权引用；
2. 工具由服务端执行，模型不获得直接调用能力（`model_callable=False` 是设计不是待办）；
3. 关键校验失败一律 fail-closed；
4. 每条引用可回到 `chunk_id` + locator + `corpus_version`；
5. 一切改动以评测数据验收，负收益即回退；
6. **二期全程仍不部署服务器**：部署面维持"一台小机器 + 一组文件"，不引入 PostgreSQL、Qdrant 独立服务、对象存储、任务队列或本地推理节点。

## 2. 三阶段总览

```text
阶段一【地基】统一输入与混合检索
  → 阶段二【内核】EventStream Agent Loop + exam_review 确定性计划
  → 阶段三【出口】工具服务化（条件触发）+ 上线压测标定
```

- 三阶段串行落地，每阶段独立提交、独立验收、独立回滚；
- 阶段二依赖阶段一的检索质量基线（P0 评测集在阶段一前置建立）；
- 阶段三为条件触发 + 交付收尾，不阻塞阶段一、二的独立上线；
- 借鉴项按 §5 的 P0/P1 清单挂接到对应阶段，其余明确不借；
- 每阶段验收均含"不部署服务器"核对项，见 §6 部署边界。

---

## 3. 阶段一【地基】统一输入与混合检索

**目标**：用户不再手选 Workflow；在确定性词法检索之上增加向量召回，且精确匹配能力不回退。这一阶段不引入任何动态决策，Agent 闭环留待阶段二。

**前置依赖**：一期语料管线、`RetrievalGateway` 接口、契约评测框架已就绪（均已交付）；无新增服务依赖。

### 3.1 实施步骤（SOP）

**步骤 1 —— P0 检索评测基线（一切改造的前置）**

- Golden set：`(course_id, query) → 必须命中的 chunk_id 列表`，来源用历年题题干 → 题目 chunk、知识点名词 → 定义标题 chunk，每门首批课程 ≥30 条，人工核对；存放 `resources/evaluation/retrieval-golden/`，随 Corpus CI 校验引用真实存在；
- 指标：recall@5、recall@20、MRR、噪声率（返回但未被回答引用的占比，用于重定标 min_score）；
- 落点：eval_runner 增加 `--retrieval-only` 模式与逐课程报告。

**步骤 2 —— 词法腿升级为 BM25F**

- 纯算法替换：字段权重 title > heading/question > text，映射现有 ×4/×3/×3/×1 的意图，加饱和抑制；
- 43 门课约 24k chunks 规模纯 Python 倒排毫秒级；
- 接口保持 `RetrievalGateway.search(course_ids, query)` 对 service 层透明；
- `min_score` 阈值由步骤 1 的 P0 数据重定标，不沿用旧值 6。

**步骤 3 —— 密集腿（embedding）+ RRF 融合**

- 中文 embedding 二选一：本地 bge-m3 或 API（硅基流动/智谱均有接口，目录加第五类条目）；**推荐 API，不本地推理**（见 §6）；
- 存储：**sqlite-vec 或 lance 单文件，不用 Qdrant**；向量文件放进 candidate 目录随 activate/rollback 天然获得版本门与回退；validate 校验行数与维度；
- 融合：两腿各取 top50，**RRF(k=60)** 后取 top-N——只用排名不用分值，无需归一化，保持确定性排序（同输入同输出）；两路召回并行执行，T_retrieval ≈ max(词法, 向量) + 合并；
- 版本绑定：`corpus_version` 追加 embedding 模型 id 段，换模型 = 重建 candidate = 重走激活门；RetrievalBatch 校验向量版本与 course_pack_version 同源，不一致按 `ContractConflict` 处理；
- 元数据过滤：course_id、审核状态、corpus_version 为确定性过滤，绝不交给相似度。

**步骤 4 —— Query 变体与词表增强**

- exam_review 已有确定性检索词合成；其余 workflow 从 `workflow_payload` 锚点生成 1～3 个规则查询变体，同一轮 RRF；
- 新增每课程**确定性同义词/缩写展开表**（人工维护、可审计），不用 LLM 改写：省一趟调用、不碰"检索词不改课程范围语义"红线；LLM 改写仅作可选开关默认关。

**步骤 5 —— 重排（可选增强）**

- 召回 top20～50 → reranker → top5 进 prompt；本地 bge-reranker-v2-m3 或 API 二选一，**推荐 API**；
- API 失败时降级回 RRF 顺序继续 run（rerank 是增强不是依赖）；
- Trace 记录两腿命中数、融合顺序、rerank 前后顺序；数值只用于候选排序，不解释为概率。

**步骤 6 —— 统一输入与自动路由**

- 增加统一 Composer，Router 输出 `workflow_type + typed_payload + confidence`；
- 置信度低时向用户澄清，路由失败时允许手动纠正；
- 五类 Workflow 保留为受控 Skill（能力入口），复用现有 `WorkflowType` 合同与 payload schema。

### 3.2 验收（DoD）

- recall@K 与 MRR 提升；题号/公式/函数名精确命中率不回退；语义改写命中率提升；
- 课程越权候选数 = 0；索引版本切换与回滚可用；
- 路由分类准确率、payload schema 通过率、低置信度误执行率、用户纠正率达标；
- **不部署服务器核对**：无新增常驻进程、无新增独立存储服务，向量文件为单文件随 candidate 版本门管理。

### 3.3 止损/回滚点

- BM25F 若精确命中率回退 → 回退纯词法加权打分，保留评测基线继续调权；
- 向量腿若引入越权候选或 ContractConflict 频发 → 关闭 dense 腿，降级回单腿；
- 路由误执行率超阈值 → 恢复手动选 Workflow 入口，统一 Composer 转可选。

---

## 4. 阶段二【内核】EventStream Agent Loop

**目标**：从单链路变成证据闭环。只保留一套主运行机制：EventStream + Reducer 承载，受限单步决策驱动——不引入独立 LLM Planner、ReAct 框架或 Replan 循环。

**前置依赖**：阶段一的混合检索与 P0 评测基线已就绪；一期 `try_claim_step_start / try_claim_terminal` 单飞语义、NDJSON 流式通道已交付。

### 4.1 运行结构（SOP）

```text
事件进入 → reducer 更新 AgentState
  → 未终止则模型输出一个 Action 或 Final
  → Action Guard → 服务端执行
  → observation_recorded → 回到 reducer
```

1. 扩充 NDJSON 事件词表：`decision_produced / action_rejected / observation_recorded / budget_crossed / clarification_requested / run_finished`；
2. 服务端纯 reducer：`state = reduce_agent_event(state, event)`，与前端 `reduceWorkflowStreamEvent` 同构；测试方法为喂事件序列断言终态；
3. 事件追加式写入 SQLite 事件日志，**终态快照必须等于事件重放结果**；
4. 取消实现为注入的取消事件，由 reducer 在节点边界收敛为 `interrupted`；
5. 同会话请求串行排队，复用 `try_claim_step_start / try_claim_terminal` 单飞语义；
6. 新增事件 kind 走协议版本协商或特性开关，保证旧客户端兼容；
7. 动作白名单首批：`retrieve / retrieve_with_query_rewrite / ask_clarification / generate_answer / finish`；
8. 不过度事件溯源：事件只在单个 run 生命周期内是真相源，对外查询以终态快照为准。

### 4.2 预算：防死循环是本职，配额另层管

**原则**：Agent 预算只防循环失控。自然输入输出不由 Agent 限额——输入由请求合同管（question ≤2 万字符、problem ≤4 万字符、材料 ≤10 万字符），输出由供应商调用参数（max_tokens）管。

**死循环防线**（所有模型一致，Agent Runtime 执行）：

```text
max_steps                = 4      # 每次模型交互都算一步，含 Final 与 Guard 重试
max_retrieval_rounds     = 2
max_query_rewrite        = 1
max_same_action_retries  = 1
max_guard_retries        = 1      # 计入步数
max_runtime_seconds      = 120    # 进程级防悬挂兜底，不是成本控制
```

单一计数器：决策、Final、Guard 重试共享步数预算，结构上总模型调用 ≤ max_steps，不设独立 model_calls 上限。

**平台免费档配额防线**（仅 platform_daily_free_quota 三模型，ModelGateway 配额层执行）：

```text
每用户每日请求数 / Token 数   # 对齐 OpenRouter 免费额度口径
单次输出                      # 由该通道生成参数设定，偏紧
每用户并发                    = 1
额度耗尽                      = 明确报错，不自动切换（PLAN-1 §1.6 冻结）
```

**BYOK / 其他模型**：只有死循环防线；输入输出不设 Agent 限额。

终止条件：证据覆盖达标；已生成通过 Guard 的回答；模型输出 Final；触达步数或运行时限；同动作重复失败；Guard 重试达上限；用户取消；检测到越权动作。预算到达返回有边界的降级结果（如 `insufficient_evidence`）。

### 4.3 Context Compaction 与长材料预处理（确定性优先）

- 证据账本按 chunk_id 去重；未被引用候选在后续轮次降级为标题+locator 一行；Observation 只存结构化字段；老对话轮次滚入数百字封顶的结构化摘要；
- 临时材料（合同上限 10 万字符）走零模型调用的确定性预处理：解析标题树并按节切块 → 生成材料地图（标题树 + 各节字数/首句）→ 按任务焦点词法选段 → 注入地图与带 locator 的选段。仅用户显式要求通读全文时启用分批 map-reduce 精读，消耗扩展预算档。

### 4.4 exam_review 确定性计划确认

- `exam_review` 由代码根据大纲、薄弱点和历年题事实生成短计划，零额外模型调用；
- 计划先展示给用户确认，再进入同一个 EventStream Agent Loop；
- 计划只影响检索顺序和覆盖目标，不新增工具，不改变 Agent Runtime；
- Observation 只更新覆盖率与缺失主题，后续动作仍受本阶段单步决策和死循环防线限制；
- Hook 延伸：`observation_recorded` 后自动更新覆盖率，`action_rejected` 自动埋 rejection 指标。

### 4.5 成本与延迟预估（估算口径，上线前压测标定）

| 场景 | 模型调用 | 检索轮次 | 总时间估算 |
| --- | --- | --- | --- |
| 高置信直接回答 | 1 | 1 | T_retrieval + 1×T_llm |
| 先检索后回答（常见） | 2 | 1 | T_retrieval + 2×T_llm |
| 补一次检索（上限路径） | 3 | 2 | 2×T_retrieval + 3×T_llm |

- EventStream 自身开销 = 本地事件序列化 + SQLite 追加写 + reducer 折叠，量级远小于一次远程模型请求；具体毫秒数需压测，不在方案中承诺；
- 主要延迟来自模型调用次数，这正是预算按调用次数封顶的原因；
- 相比一期（1 次生成）：常见路径 +1 次决策调用；上限路径 +2 次。Token 增量为决策调用的输入/输出，Observation 只传结构化摘要以压低该增量。

### 4.6 验收（DoD）

- 证据不足能补一次检索、充分不空转；普通问题模型调用通常 1～2 次、最坏 ≤3 次；
- 非法工具/跨课程参数全部拒绝并留 `action_rejected` 事件；
- 取消/超时/预算进入终态且事件日志完整；终态快照与事件重放一致；旧客户端在新事件流下不崩溃；
- exam_review 计划生成零额外模型调用；用户确认/修改/拒绝路径可审计；计划主题有课程证据或明确标记未覆盖；
- **不部署服务器核对**：EventStream 为进程内事件 + SQLite 追加写，不新增常驻服务或消息队列。

### 4.7 止损/回滚点

- 事件重放与终态快照不一致 → 冻结 Agent Loop 上线，回退单链路执行；
- 模型调用次数/延迟超压测上限 → 收紧死循环防线数值或回退单链路；
- 旧客户端因新事件 kind 崩溃 → 特性开关关闭新事件，保持兼容。

---

## 5. 阶段三【出口】工具服务化（条件触发）+ 上线标定

**目标**：在阶段一、二可独立上线的前提下，完成工具服务化可选扩展与上线前压测标定；确认二期交付后部署面不变。

**前置依赖**：阶段二 EventStream Agent Loop 已验收；无强制新增服务。

### 5.1 工具服务化与 MCP（条件触发）

仅在课程知识库、资料转换、代码实验等能力需要独立部署并被多客户端复用时启动：

1. 先稳定内部 Action Port，再为特定工具实现 MCP Adapter；
2. Guard 前置不变：Tool Calling → Action Guard → MCP Client → MCP Server → 结果过滤与引用 Guard；
3. 远程调用增加超时、重试、幂等键和审计日志；
4. **不因 MCP 引入独立服务**：MCP Server 优先同机进程/子进程形态，不新增需要单独运维的常驻服务或容器编排。

### 5.2 上线压测标定（SOP）

1. 压测三场景（高置信 / 常见 / 上限路径）的 P50/P95 延迟与 Token 消耗，回填 §4.5 成本表的实测值；
2. 核对平台免费档三模型的每日额度口径，标定 §4.2 配额防线数值；
3. 标定 `max_runtime_seconds` 与死循环防线各数值为压测上限，而非拍脑袋值；
4. 回归验证：取消、断线重连、终态一致性、跨课程越权拒绝四类安全路径。

### 5.3 验收（DoD）

- MCP（若启动）前后 Guard 与权限策略不变，远程调用有超时/重试/幂等/审计；
- §4.5 成本表、§4.2 配额与运行时限均有压测实测值支撑；
- **不部署服务器核对**：升级后部署面仍是"一台小机器 + 一组文件"，无 PostgreSQL、无 Qdrant 独立服务、无对象存储、无任务队列、无本地推理节点。

### 5.4 止损/回滚点

- 压测发现延迟/成本超预期 → 回退到阶段一、二的单链路或更紧预算档；
- MCP 引入运维负担 → 撤回 MCP，保留内部 Action Port（工具服务化永远可推迟）。

---

## 6. 部署边界：仍不部署服务器

二期全程坚持"小机器只编排、不推理"边界，部署面不变：

- **一期形态维持 1C2G / 40GB / 1–2Mbps 基线**（Makefile `serve-online` 单机单进程路径）；
- 完成阶段一推荐组合 **API embedding + API rerank + sqlite-vec**：增量约 2 vCPU / 内存维持 2GB（24k × 1024 维 fp32 mmap 约 100MB 级）/ 磁盘量级不变 / 外部依赖两个 API 配额；
- 本地跑 bge-m3 + reranker 需 4C8G 起步，**不推荐**——ECS 不承担 embedding/索引构建/重排推理；
- 面向真实学生开放时带宽先于 CPU 成为瓶颈：建议 5Mbps 起或将 SPA 静态资源 CDN 前置；
- 阶段二的 EventStream 为进程内事件与 SQLite 追加写，不改变部署形态；
- **明确不因二期引入**：PostgreSQL、Qdrant 独立服务、对象存储、任务队列、MCP 常驻服务、本地推理节点——升级后部署面仍是"一台小机器 + 一组文件"。

## 7. 待确认事项

1. Golden set 人工标注的人力归属（资料 A/B 还是开发组）；
2. embedding/rerank 走 API 时挂靠哪家供应商、并入 BYOK 目录还是平台目录新增分类；
3. 阶段一起 corpus-active-v1 是否升版为 v2，旧 store 只允许重建还是提供迁移工具；
4. rerank 降级是否学生端可见（建议仅 Trace 可见）；
5. 阶段二流事件协议版本号方案与旧客户端兼容窗口；
6. 澄清（clarification）交互形态与滚动摘要的字段边界；
7. §4.2 运行时限与平台配额数值、§4.5 成本表在上线前经压测标定，当前值为设计上限。

## 8. 借鉴取舍总览

判断标准是"最适配"而非"最优"；每个 borrowed 概念必须指认到它替换或补强的现有机制，说不出来就不引入。

| 概念 | 一期现状 | 借 | 不借 |
| --- | --- | --- | --- |
| Session | conversation / run / attempt_group 三层已有 | run 升格为一等 Session 对象（阶段二已含） | 进程级可恢复运行时 |
| Subagent | 无 | 无；并行取证用 asyncio 进程内并发 | 多 Agent 协作 |
| Memory | 版本化语料库 + 六轮截断 | 结构化滚动摘要外部化状态 | 向量库存对话、跨会话画像 |
| Permissions | fail-closed 全套 | 动作白名单与预算（阶段二） | —— |
| Approval | manifest passed / 六态流转 = 离线审批 | exam_review 计划确认（阶段二） | 运行时逐动作弹窗 |
| Hooks | Guard 节点即确定性反射 | 动作环延伸埋 rejection 指标 | 用户可配置钩子 |
| Agent Loop | 见 §4 EventStream Agent Loop | Observe/Decide/Act ↔ observation_recorded / decision_produced / 受控执行 | 独立 ReAct 框架、全局 Planner |
| Compaction | 字段级长度上限 | 证据账本去重、候选降级、轮次滚入摘要 | 语义压缩模型 |

**P0（挂阶段一/二）**：RRF 融合；embedding 身份入索引版本；证据账本去重 + 候选降级摘要；结构化滚动摘要。
**P1（挂阶段二）**：exam_review 计划确认；同义词展开表；Hook 延伸埋 rejection 指标。
**明确不借**：独立 LLM Planner、ReAct 框架、Replan 循环、Subagent、运行时审批弹窗、MCP（现阶段）、向量库存对话、语义压缩模型、自动模型路由；继承冻结：agent 自主多跳检索、语义缓存、跨课程检索开放。

来源标注：DSH（goal/budget 边界、spill 文件、结构化 todo）、Claude Code（auto-compact、plan mode）、Codex（AGENTS.md 约定、沙箱 fail-closed）均取公开资料口径的机制思想，不冒称了解各家内部实现细节。
