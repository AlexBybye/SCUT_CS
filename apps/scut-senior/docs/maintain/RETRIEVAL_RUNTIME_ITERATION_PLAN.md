# 检索排序、向量执行与运行时拆分迭代方案

日期：2026-09-13。代码基线：`7d5c030b`。状态：待实施；本文不代表功能或性能验收已完成。

## 1. 范围与实施原则

本轮只处理三项：P1 检索排序、P1 向量执行效率、P2 运行时拆分。人工重建 P0 评测集暂缓；继续利用现有可解析的评测数据、合成边界用例和可复现性能基准，不把旧标签指标解释为教学质量证明。

保持 FastAPI / Vue 单体部署、SQLite 文件、现有公共 API、Workflow 请求及结果合同、NDJSON 事件合同、五类 Workflow、课程授权、私人材料 TTL、模型调用额度和 Guard 语义。此次不增加外部向量服务、模型 reranker、自动课程扩展或新的 Agent 决策功能。

排序行为变化、等价性能优化、结构重构分别提交和验收。推荐执行顺序：自动基线 → 向量优化 → 排序实验 → 运行时拆分。先优化向量可减少排序对照的运行成本；排序达到切换门槛后再设为默认。

## 2. 当前实现与需要纠正的假设

- `adapters/local_corpus.py`：单课程生成 query variants；BM25F 和 dense 各取候选，各腿内部做 RRF；最终调用 `rule_rerank`。默认最终 limit=5，允许 1–20。
- `rule_rerank.py`：exact lexical 优先，其余 lexical 随后，dense 只补空位。因此词法足够多时 dense 无法进入上下文。
- `bm25f.py::exact_match_ids`：匹配原始整句在字段中的包含关系。它不等于题号或标题的结构化精确定位。词法评分里的 EXACT_MATCH_BONUS 与最终硬保护是两个机制，本轮先保留前者，只替换新策略的硬保护判定。
- `vector_store.py`：SQLite BLOB 保存 float32；每次 search 解码向量，Python 循环计算余弦，再全量排序。
- `local_corpus.py::_dense_chunk_ids`：每个 variant 单独 embed；跨课程通过递归 search，再轮询合并，可能重复编码同样的文本。
- `service.py::_run`：约千行的执行主流程，文件共约 2,400 行；混合模型准入、运行状态、检索、Guard、持久化和流输出。
- 当前检出与上一张图的 `c234256b` 不同：当前主流程是规则动作与空结果的历史上下文补查。不可直接按上一版图中的 model/shadow 决策结构实施本轮重构。

## 3. 阶段 0：自动基线与兼容约束

### 交付

新增离线对照入口，复用 `retrieval_eval.py`，输出机器可读 JSON。报告绑定 git SHA、corpus_version、embedding 模型身份、策略名、配置、数据集摘要、硬件、线程数和重复次数。

记录候选池 Recall、Recall@5/@20、MRR、已有标签下的未标注比例代理值；另记录 dense-only 进入 Top-K 的比例、精确锚点保留率、空结果率、每课程结果分布、词法/编码/向量加载/相似度/排序耗时、冷暖 p50/p95 和峰值内存。

将以下用例作为自动回归，不要求新增人工审核流程：题号加试卷名；同题号不同年份；数字出现在公式中；完整标题；短泛化标题；同义表达；无相关证据；空查询；重复 chunk；禁用课程；跨课程；私人材料用户隔离；版本切换。

性能对照先固定相同排序策略与候选深度。使用实际存在的课程和语料数量，禁止把不存在的数据集目录当成已完成基线。历史黄金引用失效时报告并停止该组质量比较；不能静默丢弃失败条目美化指标。

### 门槛

公共合同检查通过。记录现有失败项及其复现方式；不得把既有失败归因于本轮，也不得掩盖新增失败。性能指标是后续验收的比较对象，此阶段不承诺绝对延迟。

## 4. P1-A：向量执行效率

### 4.1 请求级查询编码复用

将多课程递归调用改为一次 search 内的明确编排：

1. 验证课程集合，读取一次 active pointer，绑定一个有效 corpus snapshot。
2. 为每门课程生成原有 variants，保留课程自己的扩展，不共享课程扩展规则。
3. 对最终送入 embedding 的文本精确去重，按配置 batch size 分批 embed。
4. 建立本次 search 独有的文本到向量映射，再分发给各课程 dense 检索。
5. 保留每课程召回、腿内 RRF 和现有跨课程轮询合并语义。

编码缓存第一版仅存在于一次 search 请求内，不建立跨用户的全局查询缓存。这样可复用跨课程相同文本，又不长期缓存用户查询。带前缀或预处理后的文本才是缓存键；不能把不等价输入合并。

验证 batch 推理与单条推理在 padding/mask 下等价。空 variants 不调用模型。批大小先以 32 为实验起点，结合真实长文本和内存测量调整。

### 4.2 只读向量快照与缓存

新增 `vector_search.py`，将构建写入和在线查询分开：现有 `VectorStore` 写入及文件 schema 保留；在线加载使用只读 SQLite 连接，不执行 CREATE TABLE。

`VectorSnapshot` 包含稳定顺序的 chunk_ids、course_ids、归一化 float32 矩阵和维度/模型身份。加载后关闭连接，矩阵不可变，线程之间共享数据而不是共享 SQLite connection。

缓存键至少包含：解析后的 store_root、corpus_version、course_id、embedding model_id、dimensions。现有模型 ID 必须代表同一套资产；模型文件更新必须换身份或增加资产指纹，不能用相同字符串跨模型复用。

使用按字节计量的 LRU，计入矩阵和 ID 元数据开销。初始缓存预算建议 256 MiB，可配置；单项超预算时不入缓存，使用分块扫描。每 worker 都有自己的缓存，部署预算必须乘 worker 数，避免误把进程预算当整机预算。

同一缓存键采用单次加载协调，避免并发重复加载。只在检查和发布缓存时持锁，不持全局锁执行 SQLite I/O、ONNX 或矩阵搜索。失败不发布半成品。

每次新请求仍检查 active pointer 和课程开关；缓存命中不能绕过授权。一个请求只使用捕获的同一 snapshot。返回前若 pointer/开关改变，拒绝该次结果并允许调用方重新发起，不能拼接两个版本，也不自动增加隐藏检索重试。旧快照已有读引用可安全释放，缓存淘汰不破坏在途对象。

### 4.3 矩阵精确搜索

加载时一次完成 BLOB 解码和行归一化，查询向量归一化后计算 `scores = matrix @ queries.T`。分块处理过大的矩阵或 query batch，避免完整 N×Q 临时矩阵超预算；块间设置取消/截止时间检查点。

保留现有正相似度过滤和 `(-score, chunk_id)` 排序契约。Top-K 可用局部分区选择，但必须纳入边界同分项后稳定排序，不能任由 argpartition 随机截断同分项。先实现稳定全排序参考路径，再决定局部分区是否确有收益。

零向量不产生命中；NaN、Inf、错误 BLOB 长度、模型/维度不一致属于损坏资产，明确报错，不静默返回空集。缺少合法 dense 资产沿用现有 BM25F 降级。

float32 矩阵运算与原 Python 累加可能有微小数值差异。合成样本使用可解释的 margin；真实语料记录 Top-K 差异和边界分差，以绝对误差 1e-5 作为初始数值验证容差，不宣称无条件逐位相等。明显排序变化必须调查，不能统归浮点误差。

NumPy 为直接依赖时，在 dense 对应 optional extra 显式声明，运行时延迟导入，词法模式不要求安装 ML 栈。保留旧标量引擎为对照和显式回滚选项；不要在资产损坏时偷偷切换引擎。

### 4.4 验收与回滚

- 相同查询文本在一次多课程 search 中只编码一次；测试实际传入 batch，不只测函数调用计数。
- 暖缓存不再反复读取/解码相同课程向量；禁用课程、版本切换、回滚、多线程首次加载与超预算分块均有测试。
- 同排序策略下，非近似并列样本 Top-K 一致，其他差异有分数证据；课程边界零泄漏。
- 单课程、3 课程和可用的更大课程集合分别测冷启动、暖缓存、并发；记录总检索耗时，不能只展示矩阵核耗时。
- 建议优化目标：暖态 dense search p95 至少下降 50%，总检索 p95 不回退超过 10%；这是待实测目标，未达成时分析后再决定默认开关。
- 通过 `vector_search_engine=scalar|matrix` 独立回滚，不回滚文件 schema，不重建全部语料。

## 5. P1-B：精确锚点保护与融合排序

### 5.1 结构化锚点

新增 `retrieval_anchors.py`，输出 `ExactAnchorMatch(chunk_id, kind, confidence, matched_fields, ambiguity)`。从原始 authoritative query 提取锚点；variants 参与召回，不能凭扩展词制造硬保护。

强保护条件：

- 题号与来源/试卷标题或年份限定联合匹配结构化 question_id 和来源字段，且没有明确冲突。
- 标题或 heading 完整归一化匹配，标题来自明确引用或可靠识别的目录项；规范化限 NFKC、大小写、空白和明确的标点规则，不做激进语义合并。
- 裸题号只有在当前选择课程的相关题目定位唯一时才可强保护。同题号跨试卷/跨课程重复时标记歧义，参与普通排序。

年份单独出现、正文提及题号、公式数字、泛化短标题（如“绪论”“例题”）只作为弱信号。中文题号与层级小题只处理明确支持的形式，不把“第3题”误匹配为“第13题”。缺少元数据时保守取消硬保护。

构造按标题、heading、question locator 的小型索引，随 corpus snapshot 缓存。强命中可以从本课程已验证索引补入候选池，即使原 BM25F top50 没包含它；禁止向所选课程之外查找。原有整句 exact 检测仅保留在 legacy 策略。

### 5.2 候选与新策略

新增内部 `RankedCandidate`，携带 chunk ID、course ID、lexical rank、dense rank、锚点原因、最终分数。它不替代公开的 RetrievedSource，也不把数值评分传给模型充当可信度。

继续保持腿内 variants RRF。候选初始深度保持每腿 50，不同时扩大池子和调权，降低归因难度。

增加可选择的 `protected_rrf_v1`：

1. 将已验证的强锚点候选按确定性规则置前。
2. 对剩余两腿候选计算 weighted RRF：`score(d) = wL/(k+rL(d)) + wD/(k+rD(d))`；不在某腿时该项为零。
3. 去重后截断到 limit；分数相同按 chunk_id 排序。
4. dense-only 候选可以凭融合分数进入结果，不设置“词法优先占满”的隐含规则。

强保护不设置任意的每来源截断，以免拆断一个明确问题的多块证据。若强命中多于 limit，则按锚点具体程度、原词法 rank、chunk ID 截断并记录 protected_overflow；超出上下文容量时不承诺全部保留。若标题泛化导致大量保护，修正锚点判定，不用增大 limit 掩盖问题。

### 5.3 小范围参数对照

固定 wL=1、k=60，比较 wD=0.2/0.4/0.6；选择表现最稳定者后，才决定是否单独试 k=20。保留原 `lexical_first_v1` 对照，不预设新策略必然更好。

必须单测“词法候选已满、dense-only 高位候选仍能进入 Top-K”，证明新策略具备目标能力；同时测试弱 dense 候选不会被无条件保送。

跨课程继续现有轮询合并与总 limit，不将本轮扩展成跨课程全局重排。锚点歧义判定使用完整的所选课程集合。课程数大于 limit 时不能保证每课程都有返回项，报告中须明确；不强行引入无证据课程。

私人材料保持用户/课程/TTL 过滤和现有追加路径，不进入共享公共候选缓存或本轮公共语料 RRF。其独立排序和总上下文预算属于后续范围。

### 5.4 评测和默认切换

扩展现有评测报告：候选并集覆盖率、最终 Recall@5/@20、MRR、逐题赢/输、题号/标题/语义/无证据分组、dense-only 最终贡献率和保护溢出数。未标注候选不直接称为错误证据。

自动边界用例要求全部通过，真实现有标签的强定位用例不能出现已确认退化。建议质量切换门槛：总体 Recall@5、MRR 不低于旧策略，Recall@20 下降不超过 1 个百分点，语义组至少一项改善；任何失效标签或样本不足均在报告中说明。门槛通过也只说明现有回归数据表现，不证明真实教学质量提升。

原策略与新策略通过 `retrieval_ranking_strategy` 独立切换。新策略未达门槛时保留可调用实现及对照报告，默认仍使用旧策略，不强行上线。离线运行两套排序，不默认在每个在线请求复制模型或检索工作。

## 6. P2：进程内运行时拆分

### 6.1 目标结构

保留 `service.py` 对外类、构造方式、run/run_stream/regenerate 等入口。新增内部 `runtime/` 包：

| 模块 | 拥有职责 | 不拥有职责 |
| --- | --- | --- |
| `context.py` | RunContext：已验证请求、用户标识、课程集合、模型描述、run/attempt IDs、版本上下文 | API Key、万能服务对象、动态可变依赖容器 |
| `lifecycle.py` | RunStateMachine、AgentState/Budget、截止时间、取消准入、动作事件和终态协调 | SQL、检索算法、模型 prompt |
| `retrieval.py` | focus/复习检索入口、一次主检索和既有上下文补查、版本校验、私人来源过滤、source authorization、去重 | 引用最终输出、模型调用、改变课程范围 |
| `answer.py` | 平台/BYOK生成协调、调用预算、兼容解析、citation guard、既有修复重试、topics/style/Humanizer、复习附录、相关学习结果 | 绕过生命周期调用模型、直接写 SQLite |
| `persistence.py` | running/completed/failed/interrupted 记录、attempt 关联、存储完成后确认 trace | 决定业务终态、控制模型重试 |
| `runner.py` | 依次调用以上模块，管理异常路径和最终结果组装 | 再次堆积所有底层逻辑 |

复用已有 `ports.py`、`runtime_guards.py`、`state_machine.py`、`agent_loop.py`、`workflow_stream.py`；不复制第二套 Guard 或状态机。贡献与账号管理方法本轮仍可留在 service 门面，避免顺带扩张任务。

### 6.2 内部结果类型与依赖

`RetrievalOutcome` 返回授权 sources、corpus/course pack version、focus 和可选 exam plan。`AnswerOutcome` 返回已校验 blocks、有效引用、evidence_status 和 related learning 信息。生命周期对象持有可变状态；RunContext 尽量不可变，版本结果通过显式结果传递。

Repository、RetrievalGateway、ModelGateway、CredentialManager、Clock/EventSink 使用窄依赖注入；不要把整个 service 传给子模块。API Key 只在已有凭据加载及调用范围内短暂存在，不进入 context、trace 或结果对象。

### 6.3 分步抽取顺序

1. 固化旧行为：五类 Workflow、单/跨课程、平台/BYOK、mock/fixture、取消和错误路径的外部可观察序列。
2. 抽取 persistence，保留原私有方法委托包装，先不改调用顺序和事务。
3. 抽取 lifecycle，将 _run 闭包中的计时、预算和取消协调移入对象；不改变事件计数。
4. 抽取 retrieval；先搬迁已验收的 P1 入口，保持补查触发条件、授权顺序和版本处理。
5. 抽取 answer；原 Guard 重试、降级和附录顺序逐项保持。
6. 引入 runner，使 service.run/run_stream/regenerate 委托它；确认无外部依赖后清理过渡包装。

### 6.4 必须锁定的语义

- 未授权候选不进入模型；未经 Guard 的 answer_delta 不进入客户端。
- 模型调用次数、Guard 修复次数和原有异常分类不因拆分改变。
- 用户取消与完成竞争时，复用 WorkflowStreamSession 的 claim 规则；一个运行只有一次终态。
- result/error 的顺序、sequence、run_id、regenerate 的 attempt 关联保持。
- DB 写入成功才发持久化确认；不能因异常处理分散重复保存或把失败标记为已完成。
- 来源、citation 映射、证据状态、Humanizer 回退、复习附录在重构前后等价。
- 现有检索补查的动作记录时序如需修正，应另开明确的行为修复提交；不能藏在机械抽取中。

### 6.5 验收

采用固定 UUID/时钟/mock provider 的行为比较，剔除耗时等非确定字段，比较结果、来源顺序、事件类型顺序、终态和持久化状态。覆盖取消发生在检索前、模型中、完成保存前，以及 provider 超时、Guard 拒绝、DB 失败、流断开。

优先在公共入口测试，避免大量测试绑定新私有方法。既有 fake gateway 和构造注入继续工作。每次抽取都通过相关测试，最后执行完整 API、Web 测试、类型检查、合同导出检查和 Web build。回滚以单次抽取提交为单位，不引入常驻两套 runner。

## 7. 提交序列与交付物

| 批次 | 内容 | 完成依据 |
| --- | --- | --- |
| 0 | 自动基线、报告 schema、现有行为快照 | 可复现基线 + 合同不变 |
| 1 | 多课程同 snapshot 编排、query batch / 去重 | scope/version 边界与编码等价通过 |
| 2 | 只读矩阵快照、LRU、矩阵精确搜索 | 数值/并发/内存/冷暖性能报告 |
| 3 | 强锚点解析与内部候选元数据 | 题号/标题/歧义/伪命中测试 |
| 4 | protected RRF、参数对照、独立策略开关 | 质量报告 + 默认切换决定 |
| 5 | persistence + lifecycle 抽取 | 终态/事务/取消行为等价 |
| 6 | retrieval + answer + runner 抽取 | 五类 Workflow 与全套合同回归 |
| 7 | 清理过渡层、更新架构文档和运行配置说明 | 实际默认策略、缓存预算、回滚说明齐全 |

不为方便一次提交全部改动。三条核心回滚路径互不绑定：排序切回 legacy；向量搜索切回 scalar；结构重构回退对应提交。整个迭代无需修改公共数据库 schema 或重建已有向量文件。

## 8. 验证命令与结果记录

从 `apps/scut-senior` 执行现有命令：

```text
uv run --project api pytest tests/python
npm --prefix web run test
npm --prefix web run typecheck
uv run --project api python -m scut_senior_api.export_contracts --check
npm --prefix web run build
```

dense 基准在实际安装 ONNX/NumPy 依赖且有本地模型与合法向量资产的环境执行；缺失时标记该项未验证，不把 mock 编码性能当真实结果。新增离线入口的具体命令随实现确定并写入运行说明。

所有报告明确：实施内容、配置、语料/数据版本、通过与未通过项、性能绝对值和相对变化、默认是否切换、剩余风险。人工评测延期不会阻止等价性能优化和模块拆分；排序收益证据不足时保留旧默认即可。
