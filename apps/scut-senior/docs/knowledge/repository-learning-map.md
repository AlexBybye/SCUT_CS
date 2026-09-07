# SCUT 老学长：仓库学习地图

## 1. 范围与静态边界

- **目标应用**：当前仓库的主体是课程资料集合，真正具备 Web、API、持久化和 AI 流水线的应用位于 `apps/scut-senior/`。`source: code`；`evidence: README.md:L109-L119`、`apps/scut-senior/web/src/main.ts#createApp`、`apps/scut-senior/api/src/scut_senior_api/main.py#create_app`。
- **分析方法**：只读静态分析应用源码、契约、迁移、CI/容器配置及已保存的评测报告；没有启动应用、调用模型、运行测试、迁移或联网。
- **不能由静态代码证明**：当前线上部署状态、真实流量、P95 延迟、并发容量、实际 token 成本、安全有效性和生产就绪均为 `source: unavailable`。部署工作流还明确把发布、灰度和回滚留在阻断步骤。`evidence: .github/workflows/app-deploy.yml:L73-L111`。
- **历史报告不等于复现实验**：仓库中的评测 JSON 是已保存证据，可陈述其样本、模型与结果，但本次没有复跑；任何未来提升数字必须标为模拟或待验证。

## 2. 五域路由摘要

| 域 | 状态 | 理由 | source / evidence |
|---|---|---|---|
| Web | relevant | Vue 入口真实挂载 `App`，页面组件通过单例 store 调用 Workflow 流接口 | `source: code`；`apps/scut-senior/web/src/main.ts:L1-L10`、`apps/scut-senior/web/src/composables/useAppStore.ts#submitWorkflow` |
| Mobile | skipped | 定向盘点没有独立移动应用入口、清单、导航或 UI 实现；课程表中的移动开发资料不属于应用实现 | `source: unavailable`；已检查 `apps/scut-senior/` 入口与清单，缺少移动端注册关系 |
| Backend | relevant | FastAPI 注册 HTTP、OAuth、Workflow、贡献与维护者路由，并装配 service | `source: code`；`apps/scut-senior/api/src/scut_senior_api/main.py#create_app` |
| Data / Infra | relevant | 存在 SQLite 迁移、DAO、TTL 清理、Docker 与 CI/部署配置 | `source: config/code`；`apps/scut-senior/api/migrations/0001_iteration_zero.sql:L1-L59`、`apps/scut-senior/api/src/scut_senior_api/adapters/sqlite.py#SQLiteWorkflowRepository`、`apps/scut-senior/Dockerfile:L3-L68` |
| AI | relevant | 存在语料构建、Embedding、混合检索、Prompt、真实模型适配、Guard、Agent reducer 与评测执行路径 | `source: code`；`apps/scut-senior/worker/src/scut_senior_worker/corpus_builder.py#build_candidate`、`apps/scut-senior/api/src/scut_senior_api/service.py#IterationZeroService._run` |

## 3. 架构总览

```text
Vue Composer / Workflow Drawer
  → typed WorkflowRunRequest
  → FastAPI 鉴权、限流式 body 校验、课程/模型准入
  → Workflow Focus（权威 query + typed context）
  → 受限 Agent reducer（固定 phase、预算、事件重放）
  → Local Corpus Retrieval
       → query variants
       → BM25F variant RRF
       → optional dense variant RRF
       → lexical-first + dense backfill
  → Prompt assembly
  → exact provider/model call（OpenRouter / Zhipu / BYOK / Mock）
  → compatible answer parser
  → citation / URL / answer-block Guard
  → SQLite 终态持久化
  → NDJSON：trace / agent / answer_delta / result / error
  → 前端严格状态机验证与渲染
```

**关键定性**：这是“typed workflow + 确定性 one-shot RAG + 可重放 reducer”的受控 AI 应用，不是模型自主选择任意工具的开放 Agent。`source: inferred`；推断来自固定动作选择 `apps/scut-senior/api/src/scut_senior_api/agent_loop.py#choose_next_action` 与服务端固定 phase 调度 `apps/scut-senior/api/src/scut_senior_api/service.py#IterationZeroService._run`。

## 4. 相关域单元

<!-- code-analyzer:unit=web::apps/scut-senior/web/src/main.ts#workflow-ui:start -->
### 4.1 Web：从 Composer 到严格流式 UI

**作用**：提供课程/模型/Workflow 选择、流式运行、历史恢复、引用展示与结果后操作。

**入口**：`createApp(App).mount("#app")`；`App` 普通路径装配顶栏、历史轨、记录区和 Composer，`/maintainer` 切换维护面板。`source: code`；`evidence: apps/scut-senior/web/src/main.ts:L1-L10`、`apps/scut-senior/web/src/App.vue:L10-L75`。

**流转**：
1. `useAppStore` 以模块级单例管理认证、课程、模型、会话、表单和流状态；不是 Pinia。`source: code`；`evidence: apps/scut-senior/web/src/composables/useAppStore.ts:L103-L193`、`apps/scut-senior/web/src/composables/useAppStore.ts:L1637-L1642`。
2. 本地规则按“错题→备考→材料→题目→问答”选择 Workflow，用户可人工纠偏。`source: code`；`evidence: apps/scut-senior/web/src/workflowRouter.ts:L25-L60`、`apps/scut-senior/web/src/components/WorkflowDrawer.vue:L15-L31`。
3. 请求携带 typed payload、课程范围、模型来源、回答模式、语气和知识范围；cross 只有知识问答与题目辅导允许。`source: code`；`evidence: apps/scut-senior/web/src/workflowRequest.ts:L105-L149`。
4. `POST /api/v1/workflow-runs/stream` 接收 NDJSON；客户端拒绝未知 kind/字段、非连续 sequence、run id 漂移、回答块跳号/换类型，以及终态与增量不一致。`source: code`；`evidence: apps/scut-senior/web/src/api.ts:L214-L233`、`apps/scut-senior/web/src/workflowStream.ts:L39-L119`、`apps/scut-senior/web/src/workflowStream.ts:L196-L274`。
5. 显式取消会尽力调用服务端 cancel 后 abort；网络断线不等同取消，而是保留服务端任务并轮询历史恢复。`source: code`；`evidence: apps/scut-senior/web/src/composables/useAppStore.ts:L583-L612`、`apps/scut-senior/web/src/composables/useAppStore.ts:L1258-L1288`。
6. Markdown/LaTeX 渲染后经 DOMPurify 再 `v-html`；结果按 repository、user material、general、personalized analysis 分块。`source: code`；`evidence: apps/scut-senior/web/src/markdown.ts:L38-L90`、`apps/scut-senior/web/src/components/WorkflowResult.vue:L284-L375`。

**结果与边界**：严格客户端协议提高串流隔离与落盘一致性，但协议演进必须同步多处白名单。当前 answer delta 不是 provider token 实时流，而是后端完整 Guard/持久化后的分块。`source: inferred`；`evidence: apps/scut-senior/api/src/scut_senior_api/service.py:L744-L754`、`apps/scut-senior/api/src/scut_senior_api/workflow_stream.py:L87-L105`。

**源码可见不足**：跨课程能力直到提交阶段才限制；按钮可提交条件未覆盖文本和部分专属字段；创建会话/计划预览期间缺少取消；前端类型与运行时白名单重复维护。`source: code/inferred`；`evidence: apps/scut-senior/web/src/components/Composer.vue:L92-L114`、`apps/scut-senior/web/src/composables/useAppStore.ts:L460-L468`、`apps/scut-senior/web/src/workflowResultValidation.ts:L11-L171`。
<!-- code-analyzer:unit=web::apps/scut-senior/web/src/main.ts#workflow-ui:end -->

<!-- code-analyzer:unit=backend::apps/scut-senior/api/src/scut_senior_api/main.py#http-api:start -->
### 4.2 Backend：HTTP、鉴权、契约与服务边界

**作用**：把认证用户的 typed Workflow 请求接入受控运行时，并承载账户、BYOK、贡献和维护能力。

**入口与中间件**：`create_app` 装配 registry、repository、检索/模型 adapter 和 `IterationZeroService`；请求体在 Pydantic 之前受 2 MiB 全局限制，验证错误不回显输入值，私有 API 尽量设置 `private, no-store`。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/main.py#create_app`、`apps/scut-senior/api/src/scut_senior_api/main.py#_RequestBodyLimitMiddleware`、`apps/scut-senior/api/src/scut_senior_api/main.py#request_validation_error_handler`。

**鉴权**：GitHub OAuth state 与 session 只保存 SHA-256 digest；state 原子单次消费；Cookie 使用 `__Host-`、Secure、HttpOnly、SameSite=Lax。维护者在真实 GitHub principal 上再叠加 allowlist。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/auth.py:L10-L18`、`apps/scut-senior/api/src/scut_senior_api/adapters/sqlite.py#consume_oauth_state`、`apps/scut-senior/api/src/scut_senior_api/main.py#require_maintainer`。

**契约**：Pydantic 基类 `extra="forbid"`；Workflow 类型与 payload、single/cross 课程范围、长度、附件和 `course_only` 规则均在服务端再次约束。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/contracts.py#ContractModel`、`apps/scut-senior/api/src/scut_senior_api/contracts.py#WorkflowRunRequest.enforce_v1_invariants`。

**流转**：HTTP handler 完成认证和反序列化后调用 service；流接口在线程中执行同步运行时，用进程内 registry 关联 `run_id → user/session` 并输出 NDJSON。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/main.py#stream_workflow`、`apps/scut-senior/api/src/scut_senior_api/main.py#cancel_workflow`。

**边界与不足**：
- 限定源码未见独立 CSRF token/origin middleware，不能证明 SameSite=Lax 覆盖所有部署情形。`source: unavailable`；`evidence: 已检查 main.py#create_app 与 auth.py:L10-L18，缺少显式校验连接点`。
- 部分 `HTTPException` 保持 FastAPI 默认 `detail`，与统一 `error` envelope 不一致。`source: inferred`；`evidence: apps/scut-senior/api/src/scut_senior_api/main.py#require_maintainer`、`apps/scut-senior/api/src/scut_senior_api/main.py#_error_response`。
- 全局 2 MiB body limit 会先于附件自身 10 MiB 校验，使 2–10 MiB 附件不可达。`source: inferred`；`evidence: apps/scut-senior/api/src/scut_senior_api/main.py:L161-L166`、`apps/scut-senior/api/src/scut_senior_api/main.py:L1355-L1367`。
- 考试计划 decision 直接写 repository，静态路径未证明 conversation owner 校验。`source: inferred`；`evidence: apps/scut-senior/api/src/scut_senior_api/main.py:L1039-L1055`、`apps/scut-senior/api/src/scut_senior_api/adapters/sqlite.py#record_exam_plan_decision`。
<!-- code-analyzer:unit=backend::apps/scut-senior/api/src/scut_senior_api/main.py#http-api:end -->

<!-- code-analyzer:unit=data_infra::apps/scut-senior/api/migrations/0001_iteration_zero.sql#sqlite-lifecycle:start -->
### 4.3 Data / Infra：SQLite 生命周期、清理与部署边界

**作用**：保存身份、会话、运行、答案、引用、Trace、反馈、贡献、私人知识、额度和 Agent 事件，并支持单机容器运行。

**持久化**：repository 启动时创建 `schema_migrations`，按文件名顺序对每个迁移执行 `BEGIN IMMEDIATE`，只支持前向迁移。DB 使用 FK、WAL、5 秒 busy timeout、`synchronous=NORMAL`，并保护目录/文件权限。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/adapters/sqlite.py#SQLiteWorkflowRepository._migrate`、`apps/scut-senior/api/src/scut_senior_api/adapters/sqlite.py#SQLiteWorkflowRepository.connect`。

**事务**：`save_run` 在单个 `BEGIN IMMEDIATE` 中验证归属、保存 run 并重写答案/引用/外部资源/Trace；终态不可覆盖。额度预留和账户删除也使用写事务。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/adapters/sqlite.py#save_run`、`#reserve_platform_request`、`#delete_account`。

**数据安全**：session/state 存 digest，BYOK 用 AES-256-GCM；SQLite 整库并未加密，因此会话正文、结果 JSON 和材料仍是明文列。`source: inferred`；`evidence: apps/scut-senior/api/migrations/0002_identity_sessions.sql:L10-L27`、`apps/scut-senior/api/migrations/0014_byok_cross_device.sql:L12-L29`、`apps/scut-senior/api/migrations/0008_temporary_materials_contributions.sql:L8-L43`。

**TTL 与维护**：OAuth state 10 分钟、session 7 天、历史 30 天、临时/私人知识 7 天、BYOK 365 天；进程内 daemon thread 默认每小时清理，各步骤失败隔离。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/auth.py:L10-L18`、`apps/scut-senior/api/src/scut_senior_api/maintenance.py#MaintenanceScheduler`。

**构建/部署**：Docker 以 Node 22 构建 Vue，以 Python 3.13 非 root 用户运行单个 Uvicorn 进程；App CI 跑 Web test/typecheck/build、Python tests 和 Docker build。`source: config`；`evidence: apps/scut-senior/Dockerfile:L3-L68`、`.github/workflows/app-ci.yml:L119-L169`。

**部署边界**：deploy workflow 的 validation-only 只构建镜像，正式步骤明确阻断 SWR 发布/ECS 灰度与回滚；`Settings.assert_safe()` 也拒绝 production 启动。`source: config/code`；`evidence: .github/workflows/app-deploy.yml:L35-L111`、`apps/scut-senior/api/src/scut_senior_api/config.py#Settings.assert_safe`。

**关键不足**：
- 账户删除路径未见删除 `private_knowledge_items`，该表又无 users FK。`source: inferred`；`evidence: apps/scut-senior/api/src/scut_senior_api/adapters/sqlite.py#delete_account`、`apps/scut-senior/api/migrations/0016_private_knowledge.sql:L3-L14`。
- 附件声明 expiry 并建索引，但维护清理未见删除附件 BLOB。`source: inferred`；`evidence: apps/scut-senior/api/src/scut_senior_api/adapters/sqlite.py#create_contribution_attachment`、`#cleanup_material_records`、`apps/scut-senior/api/migrations/0017_contribution_metadata_attachments.sql:L11-L25`。
- BYOK 过期主要在读取时过滤，未见周期物理清理。`source: inferred`；`evidence: apps/scut-senior/api/src/scut_senior_api/adapters/sqlite.py#list_model_credentials`、`apps/scut-senior/api/src/scut_senior_api/maintenance.py#sweep`。
- 未见 metrics exporter、分布式 trace、request correlation ID、告警、自动备份保留与恢复演练。`source: unavailable`；`evidence: 已检查 main/config/maintenance、Dockerfile 与 CI/deploy，缺少连接点`。
<!-- code-analyzer:unit=data_infra::apps/scut-senior/api/migrations/0001_iteration_zero.sql#sqlite-lifecycle:end -->

<!-- code-analyzer:unit=ai::apps/scut-senior/worker/src/scut_senior_worker/corpus_builder.py#ingestion-indexing:start -->
### 4.4 AI ingestion：审核语料、稳定切块与候选激活

**作用**：把人工审核通过的课程 Markdown 构造成可版本化、可验证、可回滚的 corpus candidate。

**入口**：CLI 提供 `build/validate/activate/rollback/course`；build 只生成候选，activate 是独立门。`source: config/code`；`evidence: apps/scut-senior/worker/pyproject.toml#project.scripts`、`apps/scut-senior/worker/src/scut_senior_worker/corpus_builder.py#main`。

**治理链路**：
1. 构建绑定 40 位 source commit，并要求 knowledge、worker、contracts checkout 干净。`source: code`；`evidence: apps/scut-senior/worker/src/scut_senior_worker/corpus_builder.py#_verify_fixed_checkout`。
2. Manifest 固定 17 列，只有 `status=passed` 且有 reviewer 的文档进入正文处理；frontmatter 必须与 manifest 身份一致。`source: code`；`evidence: apps/scut-senior/worker/src/scut_senior_worker/corpus_validator.py#MANIFEST_HEADERS`、`#_validate_frontmatter`。
3. chunk 在 locator/heading 处 flush，普通块默认 1200 字，优先自然边界；稳定 ID 由 source、page/slide/question/heading 与 ordinal 组成。`source: code`；`evidence: apps/scut-senior/worker/src/scut_senior_worker/corpus_builder.py#_chunk_document`、`#_locator_key`、`#_split_long_text`。
4. 临时候选完整生成并验证后 rename；已有同版本拒绝覆盖；激活时再次验证并原子更新 `active.json`，课程还需显式 enable。`source: code`；`evidence: apps/scut-senior/worker/src/scut_senior_worker/corpus_builder.py#build_candidate`、`#activate_candidate`、`#set_course_enabled`。
5. Embedding 不是候选 build 的一体化步骤；独立 CLI 用本地 ONNX `bge-small-zh-v1.5`，默认 512 维、max length 512、batch 32，向每课程 SQLite 写 fp32 向量。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/vector_index.py#build_candidate_vectors`、`apps/scut-senior/api/src/scut_senior_api/adapters/onnx.py#OnnxEmbeddingProvider`。

**不足**：向量在候选 rename 后原地写入，批量 upsert 又可能逐条提交；中断可能留下部分 DB，且未见禁止修改 active candidate。`source: inferred`；`evidence: apps/scut-senior/api/src/scut_senior_api/vector_index.py#build_candidate_vectors`、`apps/scut-senior/api/src/scut_senior_api/vector_store.py#VectorStore.bulk_upsert`。

**缺失资产**：实现要求 `apps/scut-senior/packages/contracts/v1/courses.json`，当前 checkout 定向查找未发现；实际课程注册表构建能力因此为 `source: unavailable`。`evidence: apps/scut-senior/worker/src/scut_senior_worker/corpus_validator.py#DEFAULT_COURSES_PATH`、`apps/scut-senior/api/src/scut_senior_api/registry.py:L45`。
<!-- code-analyzer:unit=ai::apps/scut-senior/worker/src/scut_senior_worker/corpus_builder.py#ingestion-indexing:end -->

<!-- code-analyzer:unit=ai::apps/scut-senior/api/src/scut_senior_api/adapters/local_corpus.py#hybrid-retrieval:start -->
### 4.5 AI retrieval：BM25F、dense 与真实融合语义

**作用**：在被激活且启用的课程范围内返回可定位的候选 chunk。

**查询链路**：
1. 单课程检查 active pointer、candidate 绑定和 course switch；多课程逐门检索后 round-robin 合并，避免首课程独占。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/adapters/local_corpus.py#LocalCorpusRetrievalGateway.search`。
2. 规则 query expansion 最多产生 3 个 variants，不调用 LLM、不扩课程范围。`source: code/config`；`evidence: apps/scut-senior/api/src/scut_senior_api/query_variants.py#build_query_variants`、`apps/scut-senior/resources/retrieval/query-expansions.json#schema_version`。
3. BM25F 字段权重 title/heading/question/text = 4/3/3/1，`k1=1.5`、`b=0.75`、exact bonus=1.0；中文使用二/三元 n-gram。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/bm25f.py#DEFAULT_FIELD_WEIGHTS`、`#BM25FIndex.score`。
4. 每个 lexical variant 先过默认 1.0 分数线并取 50，variant 之间用 RRF(k=60)；dense 各 variant 也各取 50 后做自己的 RRF。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/adapters/local_corpus.py#LocalCorpusRetrievalGateway.search`、`apps/scut-senior/api/src/scut_senior_api/fusion.py#reciprocal_rank_fusion`。
5. **最终不是 lexical/dense 跨路 RRF**：`rule_rerank` 先 exact-protected lexical，再其余 lexical，dense 只补未满的槽位。若 lexical 已达到默认 `limit=5`，dense 不影响最终结果。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/rule_rerank.py#rule_rerank`。
6. 输出保留 chunk/course/source/title/text 和 page/slide/heading/question locator，供下游引用。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/adapters/local_corpus.py#_source_from_chunk`。

**降级**：无 embedding provider、corpus 无 embedding identity 或课程向量文件缺失时 lexical-only；模型/维度 identity 不匹配则 fail closed。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/adapters/local_corpus.py#_dense_chunk_ids`、`apps/scut-senior/api/src/scut_senior_api/vector_store.py#VectorStore._load_or_write_meta`。

**现有结果证据**：保存的 1380 条 P0 集比较中，Hybrid 相比 BM25F 的 Recall@5 从 0.605072 到 0.638406（+0.033334），Recall@20 从 0.791304 到 0.860870（+0.069566），MRR 从 0.439231 到 0.462348（+0.023117），但 noise rate 从 0.863231 升至 0.928617（+0.065386）。`source: config`；`evidence: apps/scut-senior/resources/evaluation/retrieval-comparison.json:L1-L29`。这是已保存报告，不是本次复跑。

**不足**：命名容易让人误以为跨路融合；dense 只有固定 cosine > 0，没有评测校准阈值；空 query 未在该层拒绝；向量扫描为 SQLite 全量 brute-force；document role/year/assets 未进入检索 DTO。`source: code/inferred`；`evidence: apps/scut-senior/api/src/scut_senior_api/vector_store.py#VectorStore.search`、`apps/scut-senior/api/src/scut_senior_api/adapters/local_corpus.py#_source_from_chunk`。
<!-- code-analyzer:unit=ai::apps/scut-senior/api/src/scut_senior_api/adapters/local_corpus.py#hybrid-retrieval:end -->

<!-- code-analyzer:unit=ai::apps/scut-senior/api/src/scut_senior_api/service.py#workflow-agent-rag:start -->
### 4.6 AI runtime：Workflow、Agent reducer、模型与 Guard

**作用**：把 typed 请求变成有界检索、模型生成和可验证结果。

**准入与聚焦**：5 类 Workflow 使用封闭 payload；服务先验证 cross feature、用户偏好、课程可用性和模型模态，再由 `build_workflow_focus` 生成权威 query、anchor JSON 与 Workflow 指令。`source: code/config`；`evidence: apps/scut-senior/packages/contracts/v1/schemas/workflow-request.schema.json:L21-L289`、`apps/scut-senior/api/src/scut_senior_api/workflow_focus.py#build_workflow_focus`。

**Agent 语义**：动作白名单含 retrieve、rewrite、clarify、generate、finish，默认预算为 4 decisions、2 retrievals、1 rewrite、1 guard retry、120 秒；Reducer 可拒绝乱序事件并重放状态。但当前 action 由服务端固定 phase 选择，不是模型 planner。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/agent_loop.py#AgentBudget`、`#choose_next_action`、`#reduce_agent_event`。

**检索与上下文**：首次 local corpus 为空且有历史时，最多补最近 2 个用户轮次重写一次；检索结果与当前用户私人知识合并，按 chunk ID 去重并再次限制课程范围。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/service.py#_compose_context_carry_query`、`apps/scut-senior/api/src/scut_senior_api/service.py:L1194-L1242`。

**Prompt 与调用**：消息为 system + 最多 6 轮服务端历史 + user；user 中包含 typed payload、权威 query、anchor JSON 和 `[S#]` 编号来源。平台默认 `max_tokens=16384, temperature=0.2`，模型精确指定，不自动切换；BYOK 只允许固定 provider/model/endpoint。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/adapters/openrouter.py#_build_structured_request`、`apps/scut-senior/api/src/scut_senior_api/adapters/byok.py#_build_byok_request`。

**解析与 Guard**：parser 接受纯文本、JSON 和 fenced JSON，输出四类回答块和 citation IDs；Guard 拒绝未知/越界引用、非 repository 引用和 URL-like 文本，并根据 `course_only/course_first` 隐藏或降级无引用内容。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/adapters/answer_parsing.py#parse_answer_content`、`apps/scut-senior/api/src/scut_senior_api/runtime_guards.py#validate_model_citations`、`#build_guarded_answer`。

**关键边界**：引用 Guard 证明的是“引用 ID 属于本次候选”，不是 claim 与 source 的语义蕴含；已声明引用甚至可以不在正文出现，因此不能声称 grounded correctness。`source: inferred`；`evidence: apps/scut-senior/api/src/scut_senior_api/runtime_guards.py:L91-L110`、`apps/scut-senior/api/src/scut_senior_api/runtime_guards.py:L141-L159`。

**流式与持久化**：run 先保存 running，终态再次保存；只有 save 成功后才发确认持久化 Trace。完整结果 Guard/落盘后才按 2000 字符发 answer delta，确保客户端看不到未审查 token。`source: code/inferred`；`evidence: apps/scut-senior/api/src/scut_senior_api/service.py:L1707-L1762`、`apps/scut-senior/api/src/scut_senior_api/workflow_stream.py:L87-L105`。

**失败与隐私边界**：provider 默认 HTTP timeout 60 秒，service 对 timeout/解析/Guard 共享最多一次 retry；BYOK 接收 cancel check 却未传给 HTTP client。typed payload、历史、检索正文和私人知识会发送到所选供应商，限定源码未见发送前 PII/secret 扫描。`source: code/inferred`；`evidence: apps/scut-senior/api/src/scut_senior_api/adapters/byok.py:L84-L128`、`apps/scut-senior/api/src/scut_senior_api/adapters/openrouter.py:L253-L294`。
<!-- code-analyzer:unit=ai::apps/scut-senior/api/src/scut_senior_api/service.py#workflow-agent-rag:end -->

<!-- code-analyzer:unit=ai::apps/scut-senior/api/src/scut_senior_api/eval_runner.py#evaluation:start -->
### 4.7 AI evaluation：契约评测与检索 Golden Set

**作用**：检查 Workflow 结果契约和检索排序，而非完整测量语义正确率。

**Pipeline case sweep**：case 可要求 answer/evidence 状态、回答块、引用有无、locator 与 exam plan/path；runner 聚合 passed/failed/skipped 和 by-course，有 failed 时退出 1。`source: code/config`；`evidence: apps/scut-senior/packages/contracts/v1/schemas/evaluation-case.schema.json:L83-L124`、`apps/scut-senior/api/src/scut_senior_api/eval_runner.py#_check_expected`。

**局限**：没有 claim correctness、citation entailment、风格、延迟或成本指标；cross case 在 runner 中会 skip；`case_ids` 和 `group_by` 的实现语义与合同并未完全闭合；真实网关异常的 retry 路径存在静态逻辑缺口。`source: code/inferred`；`evidence: apps/scut-senior/api/src/scut_senior_api/eval_runner.py:L216-L313`。

**Retrieval evaluation**：每课程 Golden Set 记录 query 与 expected chunk IDs，计算 Recall@5、Recall@20、MRR 和 noise rate；但 runner 没有这些指标的 acceptance threshold，正常生成报告即成功。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/retrieval_eval.py#load_golden_set`、`#_build_report`、`apps/scut-senior/api/src/scut_senior_api/eval_runner.py:L404-L435`。

**真实报告证据**：
- 最终保存的真实 corpus/model 报告使用 Zhipu `glm-4-flash-250414` 与 local corpus，12 例中 9 通过、2 失败、1 因 cross feature 跳过；失败为 sparse general supplement 与无大纲 exam review。`source: config`；`evidence: apps/scut-senior/resources/evaluation/iteration-7.5-real-corpus-eval-final.json:L1-L24`、`:L44-L54`、`:L115-L126`。
- 两次 11 例运行均为 9 通过、1 失败、1 跳过，但失败 case 不同，表明单次 pass rate 无法刻画模型波动。`source: inferred`；`evidence: apps/scut-senior/resources/evaluation/iteration-7.5-real-corpus-eval-run1.json:L9-L24`、`apps/scut-senior/resources/evaluation/iteration-7.5-real-corpus-eval-run2.json:L9-L24`。
- 10 门课程 exam-review sweep 为 20 例 14 通过、6 失败。`source: config`；`evidence: apps/scut-senior/resources/evaluation/iteration-7.5-exam-review-sweep.json:L1-L59`。

以上报告不是本次复跑，且其时间戳晚于当前分析所能验证的运行环境；只能作为仓库保存的历史实验产物使用。
<!-- code-analyzer:unit=ai::apps/scut-senior/api/src/scut_senior_api/eval_runner.py#evaluation:end -->

## 5. AI 阶段状态表

| 阶段 | 状态 | 核心实现与边界 |
|---|---|---|
| ingestion | present | 审核 manifest、frontmatter、locator、candidate/activation；`corpus_builder.py#build_candidate` |
| chunk | present | locator/heading-aware，默认 1200 字，稳定 chunk ID；`corpus_builder.py#_chunk_document` |
| embedding | present | 独立 ONNX CPU 构建，512 维；缺资产可 lexical-only；`adapters/onnx.py#OnnxEmbeddingProvider` |
| retrieval | present | BM25F + dense backfill；不是跨腿 RRF；`local_corpus.py#search`、`rule_rerank.py#rule_rerank` |
| prompt/model | present | typed focus + exact provider/model；`workflow_focus.py#build_workflow_focus`、`adapters/openrouter.py#_build_structured_request` |
| output/citation | present but bounded | 结构/ID/范围 Guard 存在，claim entailment 不存在；`runtime_guards.py#validate_model_citations` |
| tools/agent | present but constrained | reducer、预算、重放存在；无模型自主 planner；`agent_loop.py#reduce_agent_event` |
| evaluation | present but incomplete | 契约与检索指标存在；无语义 judge、阈值和稳定性门；`eval_runner.py#_check_expected` |
| safety/privacy | partial | URL/课程/引用/输入长度控制；无 provider 前 PII/secret scanner；后者 `unavailable` |
| cost/latency | partial | timeout、max tokens、额度标签；无 token/cost ledger、P95 运行证据 |
| fallback | present | lexical-only、一次 query carry、一次 model/guard retry、insufficient evidence；不自动换模型 |

## 6. 跨域闭环路径

1. 用户在 Composer 选择课程、模型和 Workflow。`source: code`；`evidence: apps/scut-senior/web/src/components/Composer.vue:L92-L223`。
2. Store 构造 typed request 并 POST NDJSON endpoint。`source: code`；`evidence: apps/scut-senior/web/src/workflowRequest.ts:L105-L149`、`apps/scut-senior/web/src/api.ts:L214-L233`。
3. FastAPI 限制 body、鉴权、Pydantic 校验并调用 service。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/main.py#_RequestBodyLimitMiddleware`、`#stream_workflow`。
4. Service 验证课程/模型，构造 Workflow Focus 并驱动 reducer。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/service.py:L784-L940`、`apps/scut-senior/api/src/scut_senior_api/agent_loop.py#choose_next_action`。
5. Retrieval 只在选定课程的 active corpus 中返回带 locator 的 chunk。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/adapters/local_corpus.py#LocalCorpusRetrievalGateway.search`。
6. Prompt 将来源编号为 `[S#]` 发给精确 provider/model；Parser 与 Guard 收敛为结构化结果。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/adapters/openrouter.py#_build_structured_request`、`apps/scut-senior/api/src/scut_senior_api/runtime_guards.py#build_guarded_answer`。
7. SQLite 原子保存终态、引用与 Trace。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/adapters/sqlite.py#save_run`。
8. 服务端分块发 NDJSON，前端验证 sequence/run/result 一致性后渲染。`source: code`；`evidence: apps/scut-senior/api/src/scut_senior_api/workflow_stream.py#WorkflowStreamSession`、`apps/scut-senior/web/src/workflowStream.ts:L196-L274`。

## 7. 缺失、跳过与不能夸大的结论

- **Mobile skipped**：仓库内没有移动应用实现。
- **Cache/messaging skipped**：没有独立 cache 与消息队列实现；进程内 registry/daemon 不应称作分布式基础设施。
- **Production unavailable**：生产配置拒绝启动，部署 workflow 主动阻断发布。
- **Grounded correctness unavailable**：引用 ID Guard 不等同语义蕴含验证。
- **真实 token streaming unavailable**：当前是完成后安全分块。
- **开放 Agent skipped**：模型没有自主工具选择；现状是受限状态机。
- **课程注册资产 unavailable**：当前 checkout 缺少实现所需 `courses.json`。
- **质量与性能边界**：只能引用已保存报告，不能把它们外推为全课程、全模型或线上 SLA。
