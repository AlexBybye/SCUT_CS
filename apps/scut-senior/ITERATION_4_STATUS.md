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
