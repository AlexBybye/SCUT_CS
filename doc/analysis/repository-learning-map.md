# SCUT_CS 仓库学习地图

分析对象：`/Users/bilibili/Documents/SCUT_CS`（下文所有相对路径均以它为根）。
本地图只依据当前源码与配置的静态证据写成，不包含任何运行、部署或模型质量的结论。

## 1. 范围与静态边界

- 仓库本体是华南理工计院学习资料库；可执行代码集中在 `apps/scut-senior/`（智能复习助手「SCUT 老学长」）与 `apps/tools/material_converter/`（资料转换工具）。`学科资料/`、`培养计划/` 等目录是课程资料内容，不属于应用源码，本次未逐文件读取。
- 分析覆盖四个域：`web`、`backend`、`ai`（RAG 与 harness）、`data_infra`。`mobile` 经定向检查后无应用证据，跳过。
- 静态源码无法证明：线上是否部署、真实并发与性能、检索与回答的实际质量、成本开销、安全在真实攻击下的表现。这些一律记为 `unavailable`，正文不再重复。
- `apps/scut-senior/.local/`（SQLite 运行数据）、`.venv/`、`web/node_modules/`、`web/dist/`、`.cache/` 为本地运行产物或第三方依赖，不作为业务证据。

## 2. 路由摘要

| 域 | 判定 | 理由 | source | evidence |
| --- | --- | --- | --- | --- |
| web | relevant | Vue 3 SPA 有明确浏览器入口挂载和组件树 | code | apps/scut-senior/web/src/main.ts#createApp().mount, apps/scut-senior/web/src/App.vue#template |
| mobile | skipped | 全仓无移动端工程清单或入口（无 AndroidManifest/build.gradle/Podfile 等，仅命中 .cache 内 LibreOffice 自带文件）；课程名「Android 开发」只是资料目录 | inferred | glob `**/{AndroidManifest.xml,Podfile,build.gradle,Info.plist}` 仅命中 .cache/LibreOffice.app/**；README.md#课程资源概览 |
| backend | relevant | FastAPI 工厂注册了完整 HTTP 路由表与中间件，另有 corpus CLI worker 入口 | code | apps/scut-senior/api/src/scut_senior_api/main.py#create_app, apps/scut-senior/worker/src/scut_senior_worker/corpus_builder.py#_parser |
| data_infra | relevant | SQLite 迁移序列 + 共享配额存储 + Docker 多阶段构建 + 三条 GitHub Actions 工作流 | config | apps/scut-senior/api/migrations/, apps/scut-senior/Dockerfile#runtime-stage, .github/workflows/app-ci.yml#jobs |
| ai | relevant | 存在被入口实际调用的检索网关、prompt 组装、模型调用适配器、引用 Guard、评测执行器与 harness 注册表 | code | apps/scut-senior/api/src/scut_senior_api/adapters/local_corpus.py#LocalCorpusRetrievalGateway.search, apps/scut-senior/api/src/scut_senior_api/harness_registry.py#HARNESS_REGISTRY |

## 3. Web 域单元

<!-- code-analyzer:unit=web::web/src/main.ts#createApp-mount:start -->
### web::web/src/main.ts#createApp-mount —— 单页应用壳与会话工作台

**作用**：把 Vue 应用挂载到浏览器，并组装出「顶栏 + 会话左轨 + 记录面板 + 输入区」的单页工作台。全站没有客户端路由，是一个纯单页聊天式界面。

**入口与装配**
- 入口 `createApp(App).mount("#app")`；基础样式先于组件加载以保证级联顺序。source: code，evidence: apps/scut-senior/web/src/main.ts:L1-L10。
- `App.vue` 模板固定渲染四块：`AppTopBar`、`ConversationRail`、`TranscriptPanel`、`Composer`，外加窄屏浮层遮罩与跳转链接。source: code，evidence: apps/scut-senior/web/src/App.vue:L41-L73。
- 依赖里没有 vue-router 之类的路由库，只有 vue/marked/dompurify/katex。source: config，evidence: apps/scut-senior/web/package.json#dependencies。
- KaTeX 不进首屏入口包：注释声明它只由异步加载的回答渲染视图（WorkflowResult → markdown.ts）按需引入。source: code，evidence: apps/scut-senior/web/src/main.ts:L6-L8。

**启动行为与状态**
- 挂载后并行触发 `store.loadAuth()` / `loadCourses()` / `loadModels()`，卸载时调用 `abortActiveWorkflow` 取消进行中的运行；Escape 关浮层、窗口小于 640px 收起左轨是仅有的两个全局监听。source: code，evidence: apps/scut-senior/web/src/App.vue:L26-L38。
- 所有共享状态集中在单一 store 组合式函数 `useAppStore`（约 1400 行），含会话列表、课程目录、模型目录、BYOK 凭据状态与流式运行状态等读写函数。source: code，evidence: apps/scut-senior/web/src/composables/useAppStore.ts:L234-L1387。

**结果与边界**
- 页面消费的全部数据都来自 `src/api.ts` 的请求函数（见下一单元的请求边界）；前端不直接接触数据库或语料文件。
- 组件目录还有 ByokCredentialsPanel、PluginRegistryPanel、MaterialContributionPanel、WorkflowDrawer 等，它们经由 store 的检查器页签与顶栏入口挂载，属于同一工作台的子面板，不另立单元。
<!-- code-analyzer:unit=web::web/src/main.ts#createApp-mount:end -->

<!-- code-analyzer:unit=web::web/src/composables/useAppStore.ts#submitWorkflow:start -->
### web::web/src/composables/useAppStore.ts#submitWorkflow —— 提问到流式渲染的交互流

**作用**：用户在 Composer 提交问题后，前端以 NDJSON 流方式消费一次 workflow run，并把 trace、增量回答块与终态结果还原成界面状态。

**流转**
1. `submitWorkflow()` 用 `makeRequest()` 组装 `WorkflowRunRequest`，再调 `startWorkflowRunStream(request, callback)`。source: code，evidence: apps/scut-senior/web/src/composables/useAppStore.ts:L1089-L1122, L603。
2. `startWorkflowRunStream` 向 `POST ${API_BASE}/api/v1/workflow-runs/stream` 发 JSON body，请求头带 `Accept: application/x-ndjson`、`credentials: "include"`。source: code，evidence: apps/scut-senior/web/src/api.ts:L174-L194。
3. 流解析器用 fetch body reader 逐行读事件，事件种类白名单为 `trace | answer_delta | result | error`；`reduceWorkflowStreamEvent` 校验 trace 序号连续、event_id 不重复，并在终态时核对「result 的回答块/Trace 与已流出的 delta 完全一致」，终态后再来事件直接抛协议错误。source: code，evidence: apps/scut-senior/web/src/workflowStream.ts:L17, L106, L191-L235。
4. 普通 REST 走 `apiRequest` 封装：统一 Accept/Content-Type、携带 cookie；网络失败转成中文 `ApiError(code="network_error")`，非 2xx 解析服务端 `{error:{code,detail}}` 映射为 ApiError。source: code，evidence: apps/scut-senior/web/src/api.ts:L45-L86。
5. 会话详情、run 结果、重试 attempt 在入 store 前还要过客户端 schema 校验器。source: code，evidence: apps/scut-senior/web/src/api.ts:L26-L30, L162-L172, L196-L201。
6. 取消有两条路：显式 `cancelWorkflowRun()` 打 `POST /api/v1/workflow-runs/{id}/cancel`；切换会话或离开页面走 `abortActiveWorkflow`。断网后由 `scheduleNetworkRecovery` 尝试恢复读取。source: code，evidence: apps/scut-senior/web/src/api.ts:L240-L245; useAppStore.ts:L452-L468, L1061-L1089。

**开发期请求路径**
- Vite dev server 把 `/api` 代理到 `VITE_API_PROXY_TARGET || http://127.0.0.1:8000`，并允许一个 tailscale 主机名。source: config，evidence: apps/scut-senior/web/vite.config.ts#server.proxy。

**结果与边界**
- 渲染终点是 TranscriptPanel/WorkflowResult 对回答块与引用的展示；前端能证明的请求边界止于上述 URL 与请求函数，服务端一跳见 backend 单元。
<!-- code-analyzer:unit=web::web/src/composables/useAppStore.ts#submitWorkflow:end -->

## 4. Backend 域单元

<!-- code-analyzer:unit=backend::api/src/scut_senior_api/main.py#create_app:start -->
### backend::api/src/scut_senior_api/main.py#create_app —— FastAPI 装配与路由表

**作用**：一个工厂函数把设置、注册表、检索/模型适配器、存储仓库和服务层装配成一个 FastAPI 应用；模块尾部 `app = create_app()` 是 uvicorn 的启动目标。

**装配链（全部 source: code，evidence: apps/scut-senior/api/src/scut_senior_api/main.py）**
- `Settings.from_env()` 后立即 `assert_safe()`；`app_env=production` 会直接拒绝启动，直到生产检索、HTTPS 部署与恢复验证完成（config.py:L203-L206）。source: code，evidence: main.py:L233-L234; config.py#assert_safe。
- 检索网关二选一：`SCUT_SENIOR_RETRIEVAL_MODE=local_corpus` 时构造 `LocalCorpusRetrievalGateway(corpus_store_path, min_score=…)`，否则 `FixtureRetrievalGateway(registry)`。evidence: main.py:L237-L244。
- 模型通道：`model_mode=openrouter_platform` 且配置 Key 时构造 `OpenRouterModelGateway`（配额锁存用 `SqlitePlatformQuotaStore` 共享存储），否则回落 `MockModelGateway`；智谱通道独立可选；BYOK 走 `FixedByokModelGateway`，其启用前提是 AES 主密钥 + github_oauth 身份 + sqlite 存储。evidence: main.py:L295-L339。
- 持久化统一是 `SQLiteWorkflowRepository(database_path)`；GitHub OAuth 适配器仅在 `identity_mode=github_oauth` 时构造。evidence: main.py:L289-L294, L340-L351。
- `MaintenanceScheduler` 在 lifespan 里启动：先补扫一次，再按固定间隔周期清理到期数据。evidence: main.py:L371-L389。

**中间件与错误映射**
- `_RequestBodyLimitMiddleware` 在 FastAPI 解析前限制请求体 2 MiB；受保护 API 响应强制 `Cache-Control: private, no-store`。evidence: main.py:L124, L397-L407。
- 十余个异常处理器把领域错误映射为稳定错误码：如 `RuntimeGuardError → 502 workflow_output_rejected`、跨课程未开 → 503 capability_unavailable、校验失败返回刻意泛化的 422 文案以免回显凭据。evidence: main.py:L426-L518, L463-L472。

**鉴权依赖**
- 业务路由统一挂 `Depends(require_user)`，mock 身份或已认证主体二选一。evidence: main.py:L615, L625。

**路由表（同一 evidence 文件，行号随注）**
- 健康：GET `/api/v1/health`（内嵌迭代口径与 active corpus 门控字段，L535-L560）。
- 身份：GET `/auth/github/start|callback`、POST `/auth/logout`、GET `/me`、账号导出/注销（L631-L764）。
- 目录：GET `/models`、GET/PUT/DELETE `/model-credentials/{provider_id}`、GET `/courses`（L766-L811）。
- harness 面板：GET `/plugin-registry`、POST `/plugin-registry/courses/{id}/load|unload`（L813-L870）。
- 会话：POST/GET/PATCH/DELETE `/conversations`（L872-L922）。
- 运行：POST `/workflow-runs`、POST `/workflow-runs/stream`、POST `/{run_id}/cancel`、POST `/{run_id}/regenerate`、GET `/{run_id}`、GET `/{run_id}/trace`（L924-L1064）。
- 反馈与材料：POST/GET `/feedback`；临时材料 POST/GET/DELETE `/temporary-materials`；贡献预览/提交/六态流转与维护者队列导出（L1065-L1212）。
- 兜底：`app.mount("/", StaticFiles(html=True))` 把构建出的前端 dist 由同进程托管（L1214）。

**结果与边界**
- 该文件证明的是"进程内已注册的路由与装配关系"；是否有公网流量到达这些路由，静态不可证。
<!-- code-analyzer:unit=backend::api/src/scut_senior_api/main.py#create_app:end -->

<!-- code-analyzer:unit=backend::api/src/scut_senior_api/main.py#stream_workflow:start -->
### backend::api/src/scut_senior_api/main.py#stream_workflow —— NDJSON 流式运行端点

**作用**：以严格 NDJSON 协议推送一次 workflow run 的全过程，并管理活跃流会话与取消语义。

**流转（source: code，evidence: apps/scut-senior/api/src/scut_senior_api/main.py:L933-L1034）**
1. handler 建 `asyncio.Queue` 与 `WorkflowStreamSession`；真正的执行体 `service.run_stream(user, payload, session)` 通过 `asyncio.to_thread` 在工作线程跑，事件经 `call_soon_threadsafe` 回事件循环。
2. 每个 Pydantic 事件 dump 成 JSON 时，`trace_event/answer_delta/result/error` 四个兄弟键中的 null 字段会被剔除——省略即协议的一部分，客户端拒绝显式 null。
3. 响应头 `Cache-Control: private, no-store`、`X-Accel-Buffering: no`，media type `application/x-ndjson`（L1013-L1020）。
4. 执行线程异常时若尚未发过终态事件，经 `_safe_stream_error` 折叠成有界公共错误码再发 error 事件（L954-L963, L1268）。
5. 断连语义（迭代 7.5）：GeneratorExit/CancelledError 触发 `session.cancel()`，尽力取消上游 transport；运行在下一个节点边界收敛为 `interrupted` 并留 trace/日志，供应商侧是否停止计费明确声明不可在本进程证实（注释原文口径，L994-L1007）。
6. 显式取消：`_ACTIVE_STREAMS[run_id]=(user_id, session)` 登记活跃会话，`POST /{run_id}/cancel` 校验属主后置位取消（L120-L121, L1022-L1034）。

**同步对照口**
- 非 流式 `POST /api/v1/workflow-runs` 直接委托 `service.run`，一次性返回终态 WorkflowResult（L924-L931）。
<!-- code-analyzer:unit=backend::api/src/scut_senior_api/main.py#stream_workflow:end -->

<!-- code-analyzer:unit=backend::worker/src/scut_senior_worker/corpus_builder.py#main:start -->
### backend::worker/src/scut_senior_worker/corpus_builder.py#main —— 语料 CLI worker

**作用**：独立 Python 包 `scut-senior-worker`（被 api 以 editable path 依赖）提供语料的构建、校验、激活与回退命令行，是 RAG 语料生命周期的唯一操作入口。

**CLI 子命令（source: code，evidence: apps/scut-senior/worker/src/scut_senior_worker/corpus_builder.py:L1324-L1364）**
- `build`：从 manifest + knowledge 根构建 candidate；`--max-chunk-chars` 默认 1200。
- `validate`：对 candidate 做结构校验。
- `activate`：校验通过后原子地把 `active.json` 指向该 candidate。
- `rollback` / `set-course-enabled`：回退指针、按课程启停。

**激活门（同一文件）**
- `source_commit` 必须是完整 40 位 commit（L104-L111）；构建前校验当前 checkout HEAD 与之一致（`_verify_fixed_checkout`，L145-L196）；还要求该 commit 已可达自受信 master ref（`_verify_commit_on_trusted_master`，L198 起）。
- `active.json` 必须匹配 `corpus-active-v1` 形状并绑定同一 source_commit（`_load_active`/`_require_active_candidate_binding`，L1147-L1202）；写入用临时文件原子替换（`_atomic_write_json`，L94）。
- `load_active_course(store_root, course_id)` 是给 API 检索网关复用的只读入口（L1308）。

**CI 同构约束**
- Corpus CI 明确禁止任何 `active.json` 进入版本库，并在 CI 里对真实 knowledge 语料做 build+validate 但不激活。source: config，evidence: .github/workflows/corpus-ci.yml:L104-L141。
<!-- code-analyzer:unit=backend::worker/src/scut_senior_worker/corpus_builder.py#main:end -->

## 5. AI 域单元（RAG 与 harness）

<!-- code-analyzer:unit=ai::worker/src/scut_senior_worker/corpus_builder.py#_chunk_document:start -->
### ai::worker/src/scut_senior_worker/corpus_builder.py#_chunk_document —— ingestion 与切分

**作用**：把人工审核通过的 Markdown 资料切成带定位器的 chunk，并生成课程索引与题目/标题索引，构成检索侧的全部输入。

**阶段事实**
- ingestion 数据源：`apps/scut-senior/knowledge/<course>/*.md`，由 `knowledge/manifest.csv` 登记；manifest 列含 `source_id/course/original_path/format/document_role/year/output_md/locator_type/method/ocr_used/status/reviewer/notes`，`status=passed` 表示人工审核通过（表头实测，1705 数据行）。source: config，evidence: apps/scut-senior/knowledge/manifest.csv#header-row。
- 上游转换工具 `apps/tools/material_converter` 负责 docx/pptx/pdf→Markdown 的确定性抽取（OMML→LaTeX、page/slide 锚点），AI 只做 OCR 校正、公式图转写与题界候选；GLM-4V 视觉转写走「三票多数决→确定性校验→mathtext 渲染闸」三道闸，不过闸保留 PNG；最终 passed 由人工决定。source: config，evidence: apps/tools/material_converter/SKILL.md:L20-L49; material_converter/vision_worker.py。
- chunk 规则：按标题栈切分，超长散文硬限 `max_chunk_chars`（默认 1200，下限 200），完整 fenced 代码块可整块保留例外并计入 `oversize_fenced_chunk_count`。source: code，evidence: worker/src/scut_senior_worker/corpus_builder.py:L344-L406, L441-L535。
- chunk 身份：`chunk_id = {source_id}:{locator_key}:c{序号}`，locator 合同 `locator-v1` 支持 page/slide（数字区间）、heading（标题路径）、none 三类，禁止编造位置。source: code，evidence: corpus_builder.py:L44-L56, L409-L441, L1065-L1081。
- 附带索引：题目索引按 `(source_id, question_id)` 聚合 chunk，标题索引按 heading_path 聚合（L614-L655）。
- 版本身份：`corpus_version = corpus-{commit 前 12 位}-b{builder}-m{max_chunk_chars}`（L124-L141）。
- embedding 阶段：无任何实现，切分产物就是词法倒查用的文本块（见检索单元）。stage: skipped。
<!-- code-analyzer:unit=ai::worker/src/scut_senior_worker/corpus_builder.py#_chunk_document:end -->

<!-- code-analyzer:unit=ai::api/src/scut_senior_api/adapters/local_corpus.py#LocalCorpusRetrievalGateway.search:start -->
### ai::api/src/scut_senior_api/adapters/local_corpus.py#LocalCorpusRetrievalGateway.search —— 课程内确定性词法检索

**作用**：在单个课程的已激活语料上做可复现的词法检索，输出带版本绑定的候选集；这是 RAG 里 retrieval/rerank 一段的全部实现。

**检索参数与打分（source: code，evidence: apps/scut-senior/api/src/scut_senior_api/adapters/local_corpus.py）**
- 强制恰好一个课程 ID；top-k `limit` 默认 5、合法区间 1–20；相关性地板 `min_score` 默认 6、区间 1–100（可由 `SCUT_SENIOR_RETRIEVAL_MIN_SCORE` 注入，见 create_app）。evidence: L24-L52; main.py:L237-L241。
- 词元化：NFKC + casefold 后，ASCII 取词，中文串生成 bigram/trigram 词元集合（L14, L151-L174）。
- 加权重叠打分：正文命中 ×1、标题 ×4、标题路径 ×3、题目号 ×3，连续子串整体命中再加 25 分（L177-L198）。低于 min_score 的候选直接丢弃；无候选过线就返回空集，由上层诚实降级为"证据不足"。排序键 `(-score, chunk_id)` 保证确定性（L81-L92）。
- 版本绑定：结果必须携带 `corpus_version` 与 `course_pack_version`（后者取自 `candidates/<corpus_version>/course-packs/<course_id>.json`，路径穿越受 `relative_to` 约束，L132-L148）。
- fail-closed：store 缺失、JSON 损坏、形状不对一律抛 `CapabilityUnavailable`，绝不回退到其他课程或未审核资料（L64-L79, L201-L205）。

**fixture 对照实现**
- 测试默认模式用 `FixtureRetrievalGateway` 读合成语料，接口一致。source: code，evidence: apps/scut-senior/api/src/scut_senior_api/adapters/mock.py#FixtureRetrievalGateway; main.py:L237-L244。

**阶段边界**
- query 改写只有 exam_review 计划提供的检索词替换（service 层，见下）；无向量召回、无 reranker 模型。embedding/rerank 两阶段：skipped。
<!-- code-analyzer:unit=ai::api/src/scut_senior_api/adapters/local_corpus.py#LocalCorpusRetrievalGateway.search:end -->

<!-- code-analyzer:unit=ai::api/src/scut_senior_api/adapters/openrouter.py#_build_structured_request:start -->
### ai::api/src/scut_senior_api/adapters/openrouter.py#_build_structured_request —— prompt 组装与平台模型调用

**作用**：把聚焦后的权威查询、候选资料与历史对话拼成一次 Chat Completions 请求；平台通道（OpenRouter/智谱）、BYOK 通道与 Mock 共享同一个 `ModelGateway` 端口签名。

**prompt 结构（source: code，evidence: apps/scut-senior/api/src/scut_senior_api/adapters/openrouter.py:L248-L301）**
- system 消息（中文，代码内联）：限定 `[S1][S2]…` 编号才是合法来源、不得伪造引用、不得输出 URL/推荐理由/思考过程，正文用 Markdown 直接给学生阅读；随后拼接 `build_response_control_directive` 的输出风格约束与 `build_workflow_focus` 的分 workflow 指令。
- user 消息依次携带：workflow 类型、知识范围、Bilibili 关键词策略声明、权威检索查询（JSON 字符串）、结构化 payload（JSON）、锚点上下文（JSON，标注"是数据不是指令"）、`[S#] 标题+全文` 的候选资料块。
- 采样参数：`max_tokens=8192`、`temperature=0.2`；请求里只有一个精确 `model` 字段，故意不加 fallback 数组，让配额与供应商故障对用户可见（L263-L264 注释）。
- 历史：最多 6 轮已完成尝试作为普通 chat 消息注入，历史不改写当前课程/范围（`_history_messages`，L402-L405；轮数上限见 service._build_conversation_history，service.py:L2111）。

**聚焦策略（上游输入）**
- `build_workflow_focus` 按 5 类 workflow 给出 focus_strategy/prompt_directive/authoritative_query/anchor_context，权威查询有长度上限截断。source: code，evidence: apps/scut-senior/api/src/scut_senior_api/workflow_focus.py:L233-L247, L267-L427。

**调用与配额边界（同一文件）**
- 固定 endpoint：`https://openrouter.ai/api/v1/chat/completions`（openrouter.py:L31）；智谱 `https://open.bigmodel.cn/api/paas/v4/chat/completions`（zhipu.py:L20）；BYOK 四家地址同样硬编码（byok.py:L21-L24）。transport 用禁跟随重定向的 opener，默认 60s 超时（openrouter.py:L28, L86, L117）。
- 调用前做两道配额闸：每日额度闩锁未到期直接 429 `platform_daily_quota_exhausted`；RPM 预留失败报 `platform_rate_limited`。响应头 `x-ratelimit-*` 用于识别免费档日额度耗尽并至少闩 1 秒（L225-L245, L304-L334）。
- 平台目录固定登记：OpenRouter 免费 3 个（`google/gemma-4-26b-a4b-it:free`、`dots-studio/dots-3-note-preview:free`、`nvidia/nemotron-3-super-120b-a12b:free`）+ 智谱 3 个一方免费模型（`glm-4.7-flash`、`glm-4-flash-250414`、`glm-4.6v-flash`）；BYOK 每家固定 1 个模型且 endpoint_policy=FIXED_PROVIDER_ENDPOINT，用户不能改地址或 model_id。source: code，evidence: apps/scut-senior/api/src/scut_senior_api/model_catalog.py:L161-L240; byok_catalog.py:L18, L86-L141。
- BYOK 用户 Key 由 `ModelCredentialManager.load_api_key` 在调用前解密载入，密文绑定 user/session/provider。source: code，evidence: service.py:L1102-L1104; credentials.py#CredentialCipher。
<!-- code-analyzer:unit=ai::api/src/scut_senior_api/adapters/openrouter.py#_build_structured_request:end -->

<!-- code-analyzer:unit=ai::api/src/scut_senior_api/runtime_guards.py#build_guarded_answer:start -->
### ai::api/src/scut_senior_api/runtime_guards.py#build_guarded_answer —— 输出解析、引用 Guard 与降级

**作用**：把供应商原始回复规整成安全回答块，并用引用 Guard 保证每个引用都能落回本次检索候选；这是 output/citation 阶段的安全合同。

**解析（source: code，evidence: apps/scut-senior/api/src/scut_senior_api/adapters/answer_parsing.py）**
- 兼容三种供应商形态：自然语言、JSON 对象、JSON 代码围栏，统一归一为 `GeneratedAnswer`（L16-L41, L148-L175）。
- 模型可能在不可见 sidecar 里夹带 Bilibili 关键词等元数据，`_extract_scut_metadata` 在进入学生可见 Markdown 前把它剥出（L229-L254）。

**Guard 规则（source: code，evidence: apps/scut-senior/api/src/scut_senior_api/runtime_guards.py:L81-L230）**
- 引用编号必须唯一、格式合法（`S[1-9][0-9]*`）、且逐一命中本次候选来源；正文提到未声明或未知编号即拒绝。
- 任何回答块不允许出现 URL 形态文本；非 repository 块不得携带课程引用；user_material 块只允许临时材料 workflow 使用；general/personalized_analysis 块按知识范围与 workflow 白名单放行。
- 引用映射：`citation_source_map = {S# → RetrievedSource}`，Guard 通过后把命中的 chunk 元数据（course/source/locator/question/heading_path）填进 Citation 契约对象（service.py:L1242-L1262）。

**重试与降级（source: code，evidence: apps/scut-senior/api/src/scut_senior_api/service.py）**
- 模型输出可重试错误或 Guard 拒绝最多重试 1 次（`retry_count >= 1` 即止，L1146-L1210；可重试判定 `_is_retryable_model_output_error`，L2097）。
- 候选为零时 Guard 拒绝不可修复，直接产出诚实的 insufficient_evidence 结果而不是让 run 失败（L1182-L1189; `_empty_candidate_insufficient_evidence`，L2078）。
- 可选 humanizer 二次润色带保护词表，失败或越界改写则回退原块并记 trace 降级码（L1299-L1349; runtime_guards.py#protect_humanizer_output）。
- Bilibili 延伸：关键词优先级为显式搜索词 > 模型核心知识点 > 当前问题，服务端据此拼唯一匿名搜索链接（`https://search.bilibili.com/all`），不抓取结果页。source: code，evidence: service.py#_select_bilibili_keywords(L1922), adapters/bilibili.py:L12, main.py:L288。
<!-- code-analyzer:unit=ai::api/src/scut_senior_api/runtime_guards.py#build_guarded_answer:end -->

<!-- code-analyzer:unit=ai::api/src/scut_senior_api/harness_registry.py#HARNESS_REGISTRY:start -->
### ai::api/src/scut_senior_api/harness_registry.py#HARNESS_REGISTRY —— 受控插件/harness 注册表

**作用**：这是项目里"harness"一词的实体：一张导入期冻结、构造期校验的注册表，管理 Agent Preset、受控工具目录与维护者 skill 元数据，并派生每门课的诚实运行状态。

**结构与不变量（source: code，evidence: apps/scut-senior/api/src/scut_senior_api/harness_registry.py）**
- 版本常量 `harness-registry-v1`；构造时 fail-closed：preset 必须**恰好覆盖**全部 `WorkflowType`（不多、不少、不重复）、allowed_tools 必须存在于工具目录、模态必须在已知词表 {text,image,video} 内（L158-L234）。
- 五个 preset 与五类 workflow 一一对应：知识点问答/备考复习/题目辅导/错题复盘/临时材料阅读，各自绑定 FocusStrategy 与允许工具；preset 刻意不含任何 prompt 文本，只描述能力与路由（L95-L111 docstring，L287-L359）。
- 受控工具 4 个：课程检索、证据定位、Bilibili 匿名搜索、临时材料读取；全部 `model_callable=False`——工具由服务端编排，模型永远拿不到直接工具调用能力（L52-L68 注释与 L245-L278）。
- 维护者 skill 槽位保留但为空：material-conversion 流水线归外部贡献轨道，注册表不再携带其 contract-only 元数据（L280-L285）。
- preset ↔ 模型兼容检查：`check_model_compatibility` 校验必需输入模态与结构化输出要求，不满足即由上层抛 capability 错误（L113-L143；调用点 service.py:L752-L757, L799-L804）。

**课程插件状态（同一文件）**
- `derive_course_plugin_states` 从 CourseRegistry + 检索网关实况派生三态：`active`（当前网关当场证明可服务）/`fixture_only`/`registered`；fixture 可用绝不会被抬升为 active；网关异常按不可用处理（L377-L432）。
- 对外暴露：GET `/api/v1/plugin-registry` 返回注册表（含 registry_version），load/unload 端点切换课程插件状态并存 `course_plugin_states` 表。source: code，evidence: main.py:L813-L870; api/migrations/0007_course_plugin_states.sql。

**边界**
- 该注册表描述的是编排权限与元数据；没有工具执行循环、没有 agent 自主多步规划——每类 workflow 都是固定节点顺序的单遍流水线（见跨域路径 A）。
<!-- code-analyzer:unit=ai::api/src/scut_senior_api/harness_registry.py#HARNESS_REGISTRY:end -->

<!-- code-analyzer:unit=ai::api/src/scut_senior_api/eval_runner.py#run_evaluation:start -->
### ai::api/src/scut_senior_api/eval_runner.py#run_evaluation —— 评测执行器

**作用**：控制台脚本 `scut-senior-eval`（pyproject 注册）批量执行评测 case，对每次运行的契约结果做期望比对，输出逐课程聚合报告。

**事实（source: code 除注明外）**
- 入口注册：`scut-senior-eval = scut_senior_api.eval_runner:main`。source: config，evidence: apps/scut-senior/api/pyproject.toml#[project.scripts]。
- 输入是 cases.json（含 runner 配置），逐 case 构造 WorkflowRunRequest 调用服务管线，outcome/reasons 逐条如实记录，汇总 total/passed/failed/skipped 并写 report.json；docstring 明确 fixture case 只证明管线契约，真实语料+真实模型的期望不得伪造通过（eval_runner.py:L1-L13, L198-L313）。
- case 资产：`resources/evaluation/` 下有 exam-review-sweep.cases.json、多轮 iteration-7.5 real-corpus eval 报告与 activation drill 语料。source: config，evidence: apps/scut-senior/resources/evaluation/（目录清单）。
- CLI 另支持 real-model sweep 的 case 间 sleep 参数（L352-L356）。

**边界**：报告数字反映的是当次执行的契约符合性；静态分析不据此声称检索质量或模型效果。unavailable。
<!-- code-analyzer:unit=ai::api/src/scut_senior_api/eval_runner.py#run_evaluation:end -->

## 6. Data / Infra 域单元

<!-- code-analyzer:unit=data_infra::api/migrations/0001_iteration_zero.sql#schema-migrations:start -->
### data_infra::api/migrations/0001_iteration_zero.sql#schema-migrations —— SQLite 持久化

**persistence（present）**
- 迁移序列 0001–0011 顺序落地：核心 run 存储（conversations / workflow_runs / answers / citations / external_resources / trace_events，外键 ON DELETE CASCADE）→ identity_sessions → conversation_history → model_credentials（两步）→ feedback → course_plugin_states → temporary_materials_contributions → contributions_repo_path → platform_quota_shared → account_lifecycle。source: config，evidence: apps/scut-senior/api/migrations/0001…0011*.sql（文件名与 0001 表定义）。
- `SQLiteWorkflowRepository` 启动时按 `schema_migrations` 表应用迁移（sqlite.py:L231），承担会话、run、trace、凭据密文、反馈、贡献队列、配额共享与账号生命周期的全部读写；测试替身可实现同一端口。source: code，evidence: apps/scut-senior/api/src/scut_senior_api/adapters/sqlite.py#SQLiteWorkflowRepository。
- 平台 RPM/日额度锁存迁入 SQLite 共享存储，重启不丢、多 worker 不重复发放。source: code，evidence: quota.py#SqlitePlatformQuotaStore; main.py:L308。
- 清理：进程内周期调度器物理删除到期数据（临时材料 7 天 TTL、反馈随 30 天历史、待审副本 30 天），启动补扫覆盖停机窗口。source: code，evidence: maintenance.py#MaintenanceScheduler; main.py:L371-L389。

**cache / messaging / observability**
- cache：runtime 无缓存，trace 里有专门节点记录 `cache_hit=false, reason_code=runtime_cache_not_configured`。source: code，evidence: service.py:L1071-L1079。子能力 skipped。
- messaging：任务队列/向量索引/对象存储/GitHub App 四个端口被显式注册为 `DisabledCapability`，访问即 503。source: code，evidence: main.py:L419-L424, ports.py#DisabledCapability。子能力 skipped。
- observability：仅标准 logging（模块 logger + 断连 warning），无 metric/trace 后端配置。source: code，evidence: main.py:L65, L1002-L1006。覆盖范围 unavailable。

**build/deploy 见下一单元。**
<!-- code-analyzer:unit=data_infra::api/migrations/0001_iteration_zero.sql#schema-migrations:end -->

<!-- code-analyzer:unit=data_infra::Dockerfile#runtime-stage:start -->
### data_infra::Dockerfile#runtime-stage —— 构建、CI 与部署骨架

**镜像（source: config，evidence: apps/scut-senior/Dockerfile）**
- 两阶段：node:22-alpine 构建 web（npm 固定 v11、fetch 超时受限、三次重试后兜底无锁安装）→ python:3.13-slim 运行时安装 worker+api，`PYTHONPATH` 同时含 api/worker src；dist 拷到 /app/static 并 symlink 到 /app/web/dist，由 API 进程托管。
- 非 root 用户 scut-senior 运行；CMD 为 uvicorn `scut_senior_api.main:app`。context 内 `knowledge/` 由 `.dockerignore` 排除，真实语料不进镜像（CI 用 `grep -qx knowledge .dockerignore` 复核此约束，app-ci.yml:L51）。

**CI（source: config，evidence: .github/workflows/app-ci.yml、corpus-ci.yml）**
- 两条流水线都用 partial clone（blob:none）+ sparse checkout + `GIT_LFS_SKIP_SMUDGE=1`，显式避免拉取 `学科资料/`；permissions 仅 contents: read。
- App CI：web test/typecheck/build → 安装 worker+api[dev] → pytest 全量 Python 测试 → 通过后 docker build 镜像（不推送）。
- Corpus CI：对 `knowledge/manifest.csv` 跑 corpus_validator；build+validate 一个真实 candidate 但禁止激活；禁止任何 active.json 入库；另验 fixture manifest。

**部署（source: config，evidence: .github/workflows/app-deploy.yml; apps/scut-senior/infra/README.md）**
- deploy 工作流两个 job：默认 validation_only 只验证受限检出与镜像构建；`deployment-skeleton` job 被 `vars.DEPLOYMENT_ENABLED == 'true'` 门控，即便误开也只会走到一条显式的"Deployment intentionally unavailable"失败步骤，不触 SWR/ECS。
- infra/README 冻结的安全边界：仅 master push 或人工 dispatch、校验仓库为 AlexBybye/SCUT_CS、绑定受保护 Environment、Docker context 固定 apps/scut-senior/。华为云 SWR→ECS 为设计保留项（README 口径：规划改期迭代 10）。
- 当前启用的对外路径是本机 `make serve-online`（uvicorn 0.0.0.0:8000，前后端同进程）+ HTTPS 隧道满足 OAuth Secure Cookie 回调。source: config，evidence: apps/scut-senior/Makefile#serve-online。
<!-- code-analyzer:unit=data_infra::Dockerfile#runtime-stage:end -->

## 7. 跨域端到端路径

### 路径 A：学生提问 → 流式回答（web → backend → ai → data_infra）

1. Composer 提交 → `useAppStore.submitWorkflow` 组装请求。source: code，evidence: web/src/composables/useAppStore.ts:L1089-L1122。
2. `POST /api/v1/workflow-runs/stream`（NDJSON）。source: code，evidence: web/src/api.ts:L174-L194; main.py:L933。
3. `require_user` 鉴权 + 2MiB 请求体上限 + 私有响应头中间件。source: code，evidence: main.py:L128, L397-L407, L615。
4. `service.run_stream → _run`：`HARNESS_REGISTRY.resolve_preset(workflow_type)` 解析唯一 preset，按 model_mode/user_key 解析模型条目并做兼容检查。source: code，evidence: service.py:L702-L762, L828-L857; harness_registry.py:L236-L242。
5. 状态机 RUNNING、running attempt 先落库（SQLite workflow_runs/answers/trace_events）。source: code，evidence: service.py:L830-L892; migrations/0001_iteration_zero.sql#tables。
6. exam_review 计划（可选）给出检索词 → `retrieval.search([course_id], query)`（fixture 或 local_corpus 词法打分，min_score 地板）。source: code，evidence: service.py:L966-L998; local_corpus.py:L57-L92。
7. 来源授权 Guard 校验候选全部属于当前课程，cache_policy 节点如实记 skipped。source: code，evidence: service.py:L1022-L1079。
8. 模型调用：BYOK 解密用户 Key 或平台通道走 OpenRouter/智谱/Mock，prompt 含 [S#] 候选块与聚焦指令，temperature 0.2/max_tokens 8192，配额双闸前置。source: code，evidence: service.py:L1096-L1145; openrouter.py:L248-L301, L225-L245。
9. 输出解析兼容三种形态并剥离 sidecar → `build_guarded_answer` 引用 Guard → Citation 映射回 chunk 定位 → 可选 humanizer → `_select_bilibili_keywords` 生成唯一匿名搜索链接作为 external_resource。source: code，evidence: answer_parsing.py:L148-L175; runtime_guards.py:L81-L130; service.py:L1242-L1349, L1922; bilibili.py:L12。
10. trace_event / answer_delta / result(error) 事件经线程→队列→NDJSON 推回；终态与中断持久化。source: code，evidence: main.py:L938-L1020; service.py:L1542-L1919。
11. 前端 reduce 校验序号与终态一致性后渲染回答块与引用。source: code，evidence: web/src/workflowStream.ts:L191-L235。

### 路径 B：一份试卷入库 → 可被检索（tools → ai ingestion → backend worker → data_infra CI）

1. `学科资料/` 原件经 material_converter 确定性抽取 + GLM-4V 三道闸视觉转写产出 Markdown 骨架（AI 不改原文、不判 passed）。source: config，evidence: apps/tools/material_converter/SKILL.md:L20-L49。
2. 人工审核后 manifest 行置 `passed`（reviewer 字段实名）。source: config，evidence: apps/scut-senior/knowledge/manifest.csv#status-column。
3. corpus_builder `build` 在受信 master 的固定 commit 上切 chunk（heading/page/slide locator，max 1200 字符）并产出 candidate + course-packs。source: code，evidence: worker/src/scut_senior_worker/corpus_builder.py:L441-L535, L684-L836。
4. `validate` 结构校验通过后 `activate` 原子切换 active.json（要求 trusted master 可达证明）；rollback 可回退。source: code，evidence: corpus_builder.py:L198-L270, L1147-L1283。
5. 运行时 `LocalCorpusRetrievalGateway.load_active_course` 只读该 store，版本绑定进每次检索结果。source: code，evidence: local_corpus.py:L57-L92, L132-L148。
6. Corpus CI 对同一条流水线做无激活演练并禁止 active.json 入库。source: config，evidence: .github/workflows/corpus-ci.yml:L104-L141。

## 8. 缺失与跳过

**仓库未实现（skipped）**
- mobile：无任何移动端工程目标。
- embedding/向量检索：无代码；`vector_index` 端口被显式禁用。检索完全是词法加权重叠。
- rerank 模型、运行时缓存、消息队列/异步任务：均无实现；缓存缺失在 trace 中有专节点位，队列/对象存储/GitHub App 端口注册为 DisabledCapability。
- 跨课程检索：契约冻结、feature flag 关闭，请求即 503（service.py:L711-L720）。

**边界外或仅有设计（unavailable）**
- 生产部署：`app_env=production` 直接拒绝启动；SWR→ECS 只有 validation-only 骨架，预算与认证方案未定；当前对外形态是本机进程 + HTTPS 隧道。是否存在任何公网实例，静态不可证。
- 真实网络证据：README 自述真实 GitHub 凭据回调、四家供应商真实 Key 实网联调、逐课程真实模型评测仍未完成。这是仓库文档的自我声明，本地图不将其当作已验证事实，也不据此推断线上行为。
- 检索与回答质量、成本、延迟、线上安全表现：无运行证据，unavailable。

**单元状态**：13 个单元全部 completed，无 failed；单元边界标记见各节首尾注释，恢复状态存于 `doc/analysis/pipeline_state.json`。
