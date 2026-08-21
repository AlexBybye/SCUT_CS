# 迭代 4 状态：DSH 启发的受控插件化、BYOK 对齐、五 Workflow 打通与前端打磨

日期：2026-08-17

开发分支：`codex/scut-senior-iteration-4`

状态：`committed_local_green_external_evidence_pending`。本轮改造与验证全部提交到开发分支并通过本地全量测试；真实 corpus 激活、真实供应商账号实网联调、生产 OAuth 与云端运行证据仍保持未验证，不能由本地测试替代。

## 本轮完成（按 SOP 4.5 顺序门）

### 1. SOP 4.5：DSH 借鉴、受控插件化和资料治理前置门

- `docs/CODE_ITERATION_SOP.md` 新增 4.5：DSH 只作为外部架构参考检出，绝不合并源码；五类已登记能力（Agent Preset/Workflow、声明式课程包、受控工具、模型供应商/能力匹配、维护者技能）；课程包与贡献插件声明式、不可执行任意代码；不提供学生 shell/文件系统/任意 Web 工具；资料转换轨道的逐文件人工审核门；顺序门（先改造，再迭代 4，再模型字段，再前端）。
- 4.1 进入检查第 7 条同步改为：默认不含人工资料转写与 `passed` 裁决，显式启动 4.5 资料治理轨时由指定 reviewer 执行、自动化不得代签。
- 4.5 增加 BYOK 不变量：保留会话级 AEAD 加密、固定 endpoint/模型、随登录会话到期，只借鉴 DSH credential seam 的 describe/resolve 语义与按请求生效的轮换，明确拒绝迁移到 DSH 式本地凭据文件。

### 2. 受控插件注册（改造）

- 新增 `api/src/scut_senior_api/harness_registry.py`：不可变注册表，恰好五个 Agent Preset 与五个 `WorkflowType` 一一对应（构造时校验无缺漏/重复）；受控工具目录（`course_retrieval`、`evidence_location`、`bilibili_anonymous_search`、`temporary_material_read`，全部 `model_callable=False`，模型不可直接调用）；维护者 `material_conversion` skill 仅 `contract_only` 元数据，`human_review_required=True`、`can_mark_passed_or_active=False`；诚实课程状态 `active / fixture_only / registered` 由 CourseRegistry + 当前 RetrievalGateway 派生，C++ 等未激活课程绝不声明 enabled workflows。
- 新增只读 `GET /api/v1/plugin-registry`，供未来内部插件管理页消费。
- 每次运行解析 Agent Preset；`request_validation` Trace 结果新增安全字段 `agent_preset_id` / `agent_preset_version`（web 严格 Trace 校验同步放行）。
- 真实平台模型 fail-closed：`preset.check_model_compatibility` 校验输入模态与结构化输出要求，不满足返回 503 `capability_unavailable`。

### 3. BYOK credential seam（借鉴 DSH，保留学生 BYOK）

- `ModelCredentialStatus` 新增 `writable`、`source="user_key"`、`updated_at`（repository 暴露表中已有列）；web 在 `writable=false` 时渲染只读态并禁用替换/删除。
- 抽共享 `validate_user_api_key()`（严格、不 trim），保存与生成两条路径统一拒绝带空格/控制字符的 Key。
- `ByokModelEntry` 声明服务端 `default_max_tokens` / `default_temperature` / `input_modalities` / `supports_structured_outputs`（不进入公共 payload，避免破坏 web 精确键契约）；BYOK 请求构建从目录读取调用默认值。
- 服务层对用户 Key 模型同样执行 preset 能力门。
- 明确不采用：DSH 的 `.credentials.yaml`、env 层优先遮蔽、端点探测、动态 provider 注册。

### 4. 五 Workflow 打通（迭代 4 阶段）

- fixture+mock 下五个 Workflow 全部 `run_status=completed`、`answered/sufficient`、repository 块 + page 定位引用。
- 评测用例扩展为 10 例，覆盖全部五种 `workflow_type`：新增 `exam-review-fixture-001`、`mistake-review-fixture-001`、`temporary-material-fixture-001`（fixture 契约诚实通过）；`course-knowledge-001` 等 6 例仍诚实失败（需真实 corpus 的 heading/question 定位与真实模型行为），`cross-course-scope-001` 因 feature flag 跳过。不伪造通过。
- `scut-senior-eval` 报告：`10 cases, 3 passed, 6 failed, 1 skipped`。

### 5. 前端 UI 与性能（design-taste 选择性应用）

- 修复暗色模式主按钮对比度（新增 `--accent-contrast` token，暗色下用深色文字，满足 WCAG AA）。
- 有动机的动效，全部 `prefers-reduced-motion` 门控：骨架屏 shimmer、流式回答末尾的生成光标。
- 主/次/取消按钮按压反馈。
- 收敛 section kicker 至全页两处（eyebrow 约束）。
- 性能审计结论：bundle 49KB gzip、无 scroll listener、无整页大图、`100dvh`、骨架/空/错误态齐全，无需拆包或懒加载。

## 验证

- Python：`431 passed, 1 warning`（StarletteDeprecationWarning 为既有告警）。
- Web：typecheck 通过；`59 passed`；`npm run build` 通过（JS 140.97 kB / gzip 49.00 kB，CSS 26.77 kB / gzip 5.59 kB）。
- 契约：`export_contracts --check` 通过，四个 schema 再生成（Trace 预设字段 + 凭据状态字段）。

## 仍待外部证据（未变）

- 真实 corpus 激活（受信 `master` 上的 `active.json`）与逐课程评测；
- 真实模型实网调用与 BYOK 四家实网联调；
- 生产 OAuth 回调（当前联调走 Tailscale 隧道 HTTPS）；
- 正式在线 Chat 地址与云端部署（华为云设计保留，本地+隧道为当前启用路径）。

## 追加：真实模型联调尝试（2026-08-17，诚实记录）

在线实例（`openrouter_platform_with_github_oauth_sqlite`）已恢复运行，Tailscale 隧道 200。服务端直接驱动真实 OpenRouter 网关做了两次真实调用：

1. `google/gemma-4-26b-a4b-it:free`：真实网关连通，免费通道返回 **429 限流**，按设计映射为 `platform_model_rate_limited` fail-closed（不重试、不自动切换）。
2. `nvidia/nemotron-3-super-120b-a12b:free`：真实推理返回 200，但响应未通过严格结构化 JSON 解析，按设计映射为 `平台模型返回了无法处理的结果` fail-closed。

结论：真实 Key 认证、真实网关可达、守卫/解析/错误映射管线按设计拦截均已获得外部证据；**“真实模型 run 完成”仍缺一次返回合规 JSON 的真实响应**（需额度恢复或换模型重试），不伪造通过。

## 追加：合并就绪检查（2026-08-17）

- `git merge-tree`：iteration-3 → master 与 iteration-4 → master 均为 **0 冲突**；master 是 iteration-4 的祖先（领先 19 提交）。
- ⚠️ 注意：分支历史中 `e08dfb3`（SCUT_SKILL/README.md、Summary_Skill.md）与 `987d1da`（CONTRIBUTING.md）修改了 master 上的 SCUT_SKILL 内容；合并会**静默采用分支版本**。合并 master 前需决策：接受、回退这两个文件的改动，或以路径级策略排除。

## 追加：harness-refactor 重构迭代（2026-08-19 ～ 08-20，代码超前于上文 status-4 快照）

上文各节描述的是 iteration-4 合并（`c0f4de6`）当时的快照。此后在 `codex/scut-senior-harness-refactor` 分支新增 7 个提交（`e834830`、`dfdb431`、`cc06e2a`、`595cbe0`、`9672746`、`c4fe232`、`7a33b31`），本轮验证在分支 HEAD（`7a33b31`）上全量重跑。以下为 status-4 未记录的超前实现、新证据与诚实差异。

### 1. 超前实现（status-4 未记录）

- **内部插件管理页从“预留 API”落地为交互面板**：status-4 只记录了 `GET /api/v1/plugin-registry` 供未来内部页面消费；现 web 已实现 `PluginRegistryPanel.vue`，展示五类 Agent Preset、受控工具（全部 `model_callable=false`）、维护者技能槽和逐课程诚实状态。
- **课程插件 load/unload**：新增迁移 `0007_course_plugin_states.sql`（显式 unload 行是唯一关闭方式，缺省即 loaded，未迁移数据库行为不变）；服务层课程可用 = 插件 loaded 且检索可服务；`POST /api/v1/plugin-registry/courses/{id}/load|unload` 要求真实 GitHub 登录；unloaded 课程 `enabled_workflows` 归零。SOP 4.5 受控插件的“装载/卸载”管理语义至此落库可操作。
- **维护者技能元数据已清空（与 status-4 的差异）**：`MAINTAINER_SKILLS` 由 status-4 记录的 `material_conversion` contract_only 元数据改为空元组；material-conversion 轨道按 SOP 4.5 归外部治理，保留 skill 类型与注册表槽位供未来注册。
- **课程选择与运行时可用性**：新增 `api/src/scut_senior_api/course_availability.py` 与 web `courseAvailability.ts`，逐课程投影 `retrieval_availability`（`fixture`/`local_corpus`/`unavailable`）、`retrieval_available`、`plugin_loaded`、`selectable`；前端课程选项标签、选择错误文案和课程目录结构相应更新。
- **前端 shell 重构**：DSH 启发的三栏布局（sidebar | main | details，1120/840px 折叠断点）；status-4 的暗色对比度与动效门控继续保留。
- **Markdown 渲染升级（KaTeX/LaTeX）**：新增 `web/src/markdown.ts` 与 katex 依赖，支持 `$$...$$` 公式渲染。⚠️ **status-4 的性能结论已过期**：JS gzip 从 49.00 kB 增至 154.84 kB（CSS 5.59 → 14.50 kB），此前“无需拆包或懒加载”的审计结论不再成立，应重新评估 KaTeX 按需加载。
- **回答解析重构**：`adapters/answer_parsing.py` 兼容自然语言、JSON 对象、fenced JSON 三类供应商输出，统一抽取正文并校验 `scut-meta` 侧车。status-4 追加记录中“nemotron 200 但未过严格结构化解析”的失败路径在重构解析器中有对应容错分支，但仍需一次返回合规内容的真实响应验证，不冒充已修复。
- `workflow_focus.py` 指令化重构、助教/学长/复习搭子可见提示行、Bilibili 关键词兜底；Vite `allowedHosts`（隧道域名联调用）。

### 2. 本地 corpus 激活证据（status-4 列为“仍待外部证据”，现本地已有部分证据）

- `.local/corpus-store/active.json`（2026-08-20 16:00）：`active_corpus_version=corpus-14b63e204eb3-…`，`source_commit=14b63e2`（已用 `git merge-base --is-ancestor` 证明为受信 `master` 祖先），`trusted_master_commit=c0f4de6`（当前 master tip），`trusted_master_ref=refs/heads/master`，10 门课程开关全部为 true。
- `SCUT_SENIOR_RETRIEVAL_MODE=local_corpus` 下实测：health 返回 `iteration_status=local_runtime_with_active_corpus`、`formal_exit_blocked=False`、`local_corpus_available=True`、10/10 课程 `selectable`；plugin-registry 10 门课程 `state=active` 且 loaded，`enabled_workflows` 非空；`LocalCorpusRetrievalGateway` 对 `cpp`/`information_security_intro`/`linear_algebra`/`computer_science_intro` 均 `is_course_available=True`（cpp 51 chunks），检索“模拟机试/图像相似度”返回真实命中；跨课程检索被 `CapabilityUnavailable` 拒绝。
- **诚实边界**：这是本地证据（`.local` 不入库、非远端 CI/提交证据）；激活门“source_commit 进入受信 master”本地已满足，但**逐课程评测（真实 corpus + 真实模型行为）仍未完成**。

### 3. 验证证据（分支 HEAD 全量重跑）

- Python：`476 passed, 1 warning`（status-4 记录 431 → **+45**）。
- Web：`76 passed`（status-4 记录 59 → **+17**）；typecheck 通过；build 通过（JS 488.52 kB / gzip 154.84 kB，CSS 60.48 kB / gzip 14.50 kB）。
- 契约：`export_contracts --check` 通过，无漂移。
- 评测：与 status-4 一致，`10 cases, 3 passed, 6 failed, 1 skipped`；fixture+mock 下不伪造通过，真实模型合规响应仍缺。

### 4. 已知不一致（如实记录）

- health 端点仍返回 `"iteration": 3`（`test_iteration_3_runtime.py:309` 断言锁定），相对 iteration-4 完成与重构迭代已滞后；本轮不改代码，仅记录。
- README「明确关闭或待确认」仍写“迭代 4 切片（进行中）”，与 status-4 完成描述不一致（历史遗留，未在本轮改写）。
- KaTeX 使 gzip 体积翻约三倍，status-4 性能审计结论需更新（见上）。
- **未进入迭代 5（备考复习）**：`exam_review` 仍是共用 Runtime 的 payload（`syllabus`/`weak_topics`/…），SOP §10 的大纲/无大纲双路径、年份覆盖/题型统计与 AI 样题标记均未实现。
