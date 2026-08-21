# 迭代 3 状态：Workflow Runtime、安全事件流与引用守卫

日期：2026-08-17

开发分支：`codex/scut-senior-iteration-3`

固定开发基座：`cc09a4aa897542656807ccd152cbf8feecc6a26d`

状态：`committed_local_green_external_evidence_pending`；迭代 3 的本地 Fixture Runtime、注入式供应商 transport、前端事件流和持久化退出条件已通过并提交到开发分支。真实 corpus、真实供应商账号、生产 OAuth 与云端运行证据仍分别保持未验证，不能由本地测试替代。

固定开发基座只绑定本分支的起点；本轮已把工作区差异作为一条提交落在 `codex/scut-senior-iteration-3`，尚未推送、合并 `master` 或经过远端 App CI，也没有改变资料审核状态、激活 corpus 或执行华为云部署。

## 已实现能力

- 五个 `workflow_type` 显式进入同一个 Runtime；请求不会静默切换 Workflow。
- `workflow_run` 在执行模型前保存 `running`，Trace、回答增量、终态和历史恢复绑定同一个 run；SQLite 使用终态 compare-and-set，已完成结果不能被迟到的中断覆盖。
- `POST /api/v1/workflow-runs/stream` 返回严格 NDJSON：事件序列从 0 连续递增，只允许 `trace`、`answer_delta`、`result`、`error` 四类事件和一个终态；前端拒绝缺号、重复、倒序、跨 run、未知安全字段和终态后的事件。
- 回答固定拆分为 `repository`、`user_material`、`general`、`personalized_analysis` 四类块；`citations[]`、`external_resources[]` 和 `evidence_status` 独立保存与展示。
- 引用 Guard 只接受本次候选中的唯一 `[S1] [S2] ...`，拒绝重复、越界、跨课程、未声明引用以及非 repository 块引用。`course_only` 无有效引用时丢弃无依据的 repository 正文并返回 `insufficient_evidence`。
- Bilibili 仍为 search-only：选择 B站延伸学习时，模型在 Markdown 末尾的不可见 sidecar 提供可选搜索词与本题核心知识点；后端按“显式搜索词 → 核心知识点 → 当前问题关键词组合 → 请求／课程兜底”执行 NFKC、控制字符、空白、去重、数量、长度和 URL-like 文本过滤，并固定生成一条 `https://search.bilibili.com/all?keyword=...`。不抓搜索结果、不维护视频单、不返回视频直链。
- OpenRouter 与 BYOK 的 transport 超时（包括 urllib 包装的 timeout）分别映射为 `platform_model_timeout` 和 `byok_provider_timeout`；超时或无效结构化响应只允许同一模型、同一 endpoint、同一 Key 重试一次。认证、额度、429 和普通 5xx 不重试。
- 正常 Runtime 不再把未配置的 post-generation humanizer 伪装成一个已执行的节点：自然、清晰的表达与四种回答方式都作为单次模型生成提示的一部分，Trace 记录 `response_style_control / single_pass_model_prompt`。测试仍可注入 humanizer 验证 Guard；其输出使用深拷贝基线，数字、公式、引用、术语、链接或任何无法证明等价的文本变化都会回退。当前没有启用第二次模型调用的真实后处理润色能力。

## 五类 Workflow 聚焦

Runtime 从分型后的 `workflow_payload` 建立五种明确策略，忽略与其冲突的外层 `user_input`：

| Workflow | 聚焦策略 | 权威输入 |
|---|---|---|
| `knowledge_qa` | `question_concept` | 所问概念 |
| `exam_review` | `syllabus_weak_topics` | 大纲与薄弱点；两者为空时不造检索词 |
| `problem_tutor` | `problem_main_topic` | 题目主知识点 |
| `mistake_review` | `mistake_root_cause` | 题面、原答案和可选参考答案的错误根因 |
| `temporary_material_reading` | `material_title_main_topics` | 显式材料标题或首个 Markdown 标题与材料主旨 |

- OpenRouter 与四家固定 BYOK 路由共用同一聚焦指令和有界 JSON anchor context，不新增第二次模型调用。
- 临时材料没有明确标题时不得臆造标题；不得按全文词频、重复次数或噪声词选择检索词。
- Trace 只记录策略枚举与归一化后的主题，不保存题面、错答、材料正文、内部提示词或 anchor context。
- Mock 为五种策略返回不同的确定性 Fixture 输出，用于证明路由与契约，不代表真实模型的语义质量。

## 流式与取消边界

- 当前回答增量是完整模型结果通过引用 Guard、answer block 校验和持久化后，再按块切分的安全事件流；不是供应商 token 的原样透传，也不应描述为 token-level streaming。
- 浏览器取消或页面断开会标记 request-local cancellation，停止后续确定性节点；模型调用返回后，取消优先于成功、普通失败或重试，最终保存 `interrupted`，不发送回答增量。
- 当前 OpenRouter／BYOK transport 仍使用同步 urllib。正在阻塞的 HTTP 请求没有可强制关闭的公开句柄，因此页面断开不能证明供应商已停止推理或停止计费；本地工作线程可能继续到上游返回或超时。强制终止本地 HTTP exchange 需要另行把 transport 与 Runtime 改为可取消异步调用，不能用私有 socket 补丁冒充完成。

## 验证证据

- Python 全量：`402 passed, 1 warning`；唯一 warning 是 FastAPI TestClient 对当前 httpx 兼容层的第三方弃用提示。
- Vue/Vitest：`9 files, 58 tests passed`。
- Vue typecheck：通过。
- Vue production build：通过，Vite 转换 22 modules；主 JS `138.31 kB`（gzip `48.18 kB`），主 CSS `24.41 kB`（gzip `5.13 kB`）。
- 生成式契约漂移检查：通过；`workflow-stream-event.schema.json` 已生成，临时材料可选 `material_title` 已同步到请求和历史契约。
- 专项覆盖包括：四类回答块、引用攻击、humanizer 原地修改、五 Workflow 聚焦、Bilibili 绕过、真实 adapter 超时分类、同模型一次重试、非重试错误、连续 NDJSON、模型阻塞期间取消、running 可观察性、终态 CAS 与历史恢复。
- 提交前最后一次全量为 11 个红测试，全部是守卫拒绝文案的期望不一致：实现统一使用通用 URL 拒绝文案（`回答不得返回 URL。`，守卫拦截任意 URL 形式而非仅 Bilibili），测试期望已对齐到通用文案，未改动守卫实现，也未新增任何规格。

## 尚未完成或未宣称的证据

- 真实 corpus 未激活。本轮保留用户对 Markdown 公式的替换，不把公式修订自动等同于人工审核，不改 reviewer 或 `passed/pending` 裁决；迭代 2 的 corpus 发布门仍独立有效。
- 平台 OpenRouter 与四家 BYOK 均未使用真实账号或真实 Key 发起实网推理。注入 transport 可以证明固定路由、请求结构、错误分类、重试、Guard、历史和前端链路，不能证明用户账户余额、权限、模型当日可用性或真实响应质量。
- GitHub OAuth 没有生产 HTTPS 回调证据。
- 华为云预算继续延期；`DEPLOYMENT_ENABLED` 保持 fail-closed，不创建资源、不登录 SWR、不推送镜像、不修改 ECS。
- Trace 排序分数的学生端展示程度仍保留为待确认配置，本轮没有擅自增加检索分数 UI。
- 提交已落在本开发分支，尚未推送、经过远端 App CI 或合并 `master`；这些本地结果不能替代固定提交上的远端检查。
