# SCUT 老学长 V3 非资料转换代码迭代 SOP

版本：1.7

基座：`docs/PLAN-1.md` v1.11（2026-08-16）

负责人：项目代码负责人
性质：按能力依赖逐期实施的操作规范，不制定日历排期

> 1.1 修订：SCUT_CS 确认为课程资料与应用源码的唯一公开主仓；全部应用代码落在 `apps/scut-senior/`，不另建主要应用代码仓；App CI 与 corpus CI 按路径隔离，应用镜像推送华为云 SWR 后由 ECS 部署；GitHub Project 只作为可选任务看板。
>
> 1.2 修订：平台无需用户 Key 的默认通道冻结为 OpenRouter 每日免费额度通道，目录分类为 `platform_daily_free_quota`；首批只登记 Google · Gemma 4 26B A4B、Dots Studio · Dots3 Note Preview、NVIDIA · Nemotron 3 Super 120B A12B，由用户显式选择，不自动切换到用户 Key、其他模型或付费端点。
>
> 1.3 修订：华为云未来首发基线冻结为华南-广州优先的 1C2G、40GB、1～2Mbps，但预算获批前部署保持 fail-closed；Bilibili 不匿名抓取具体视频，本次所选模型聚焦 0～3 个检索词后，后端必须生成固定 Bilibili 匿名搜索入口。
>
> 1.4 修订：Bilibili 运行时只保留匿名关键词搜索入口；不匹配或下发具体视频直链。聚焦关键词非空时，后端必须且只生成一条固定 Bilibili 搜索页 URL。
>
> 1.5 修订：取消具体 Bilibili 视频资产的建设、审核、Fixture、CI 和维护安排；任何迭代都只实现 search-only 链路，不增加视频目录或具体视频直链。BYOK 每家只选一个主流、当前可调用且有官方示例依据的目录模型；目录冻结不等于真实用户 Key 的线上调用证据。
>
> 1.6 修订：BYOK 首批立即改为 OpenRouter `deepseek/deepseek-v4-flash-0731`、DeepSeek `deepseek-v4-flash`、硅基流动 `Pro/zai-org/GLM-4.7`、智谱 `glm-5.2` 四组固定目录和固定 endpoint；移除旧供应商全部枚举与兼容项。四家卡片始终展示，只有 `enabled=true` 且当前登录会话已保存 Key 的模型进入可选列表。
>
> 1.7 修订：课程注册表首批范围同步收敛为 10 门；大学物理实验与 SRP 资料不进入知识 manifest 或检索语料，只执行源资料隐私清理。

## 1. 文档效力与使用方式

本 SOP 只把 `PLAN-1` 已确认的非人工资料转换工作改写为执行顺序、验证动作和退出条件。

- 与 `PLAN-1` 冲突时，以 `PLAN-1` 为准；
- 不在本 SOP 中替尚待确认事项做选型；
- 每一期通过退出验收后再进入下一期；
- 迭代编号表达依赖关系，不表达周次或工期；
- 如果 `PLAN-1` 后续修改，先同步更新本 SOP，再继续实现；
- 每期都要留下可复现的代码、迁移、配置样例、测试结果和已知限制，不能只以页面演示宣布完成。

## 2. 代码负责人和资料负责人的边界

资料负责人提供：

- 人工审核为 `passed` 的 Markdown；
- `manifest.csv`；
- page、slide、question、heading 定位；
- assets 和必要的固定渲染审核产物；
- 资料问题修复与人工复核结论。

代码负责人负责：

- 课程注册表和资料契约；
- manifest/Markdown 校验器；
- 统一 chunker、chunk ID 和来源 payload；
- candidate 构建、验证、激活和回退；
- 课程资料和历年题题目级索引；
- 课程预生成包与公共缓存；
- GitHub OAuth、BYOK、模型路由、历史和期限清理；
- Workflow Runtime、Trace、引用校验和 humanizer 保护；
- Vue 学生端、维护者轻量页面、反馈和评测；
- 临时材料、图片和资料贡献的应用流程；
- 当前仓库内 `apps/scut-senior/` 的工程目录、路径级 CI/CD 和发布说明；
- 维护华为云 SWR→ECS 的目标发布边界；预算获批前只验证 fail-closed 骨架，不发布镜像、不创建或修改云资源。

代码不得：

- 自动改写原资料；
- 把未人工审核的资料改成 `passed`；
- 让回答模型猜页码、幻灯片或题号；
- 让用户反馈直接修改知识库；
- 绕过 GitHub PR、人工审核或 candidate 验证发布公共语料。

## 3. 全部迭代共同遵守的不变量

### 3.1 产品不变量

- 产品是一个统一 Chat，不为五个 Workflow 建五套站点；
- 五个 Workflow 固定为：

```text
knowledge_qa
exam_review
problem_tutor
mistake_review
temporary_material_reading
```

- 每次请求显式携带 `workflow_type`，系统不能静默切换 Workflow；
- 回答方式固定为简短、详细、举例、分步骤；
- 表达风格固定为助教式（默认）、复习搭子、学长聊天；
- 知识范围固定为 `仅课程资料` 和 `资料优先，可补充通用知识`（默认）；
- 五个 Workflow 共同继承 `answer_mode`、`tone`、`knowledge_scope`、课程范围、模型选择和 `include_bilibili_resources`；默认知识范围下该开关初始为 true、用户可关闭，`仅课程资料` 必须强制设为 false；
- 默认单课程检索；跨课程默认关闭，必须显式选择课程集合并受 feature flag 控制；
- 未达标课程可以单独关闭，不让薄弱课程阻塞已经达标的课程。

### 3.2 知识和来源不变量

- SCUT_CS GitHub 主分支中人工审核通过的公共 Markdown、manifest、历年题结构和生成规则是公共知识事实源；同一仓库的 `apps/scut-senior/` 是 RAG/Chat 应用源码的唯一规范位置；项目不建设或维护具体 Bilibili 视频资产，动态 Bilibili 搜索入口是一次运行的未审核补充资源，不是仓库知识事实源；
- 用户私有材料、通用模型补充、历史、Trace、BYOK 和运行数据库不写入公共仓库；
- `answer_blocks[]` 的 `repository`、`user_material`、`general`、`personalized_analysis` 必须保持语义分离；`evidence_status` 是独立字段，`external_resources[]` 又是独立外部资源数组；
- 模型只能引用本次请求允许的来源候选编号；
- `citations[]` 由后端的已验证元数据生成，不采用模型自由文本作为来源事实；
- Bilibili 运行时只把匿名搜索入口放入 `external_resources[]`，不进入 `citations[]`，不改变 `evidence_status`；模型只提供聚焦检索词，URL 必须由后端固定规则生成；
- 没有 locator 时只能显示资料名或标题，不能补造页码或题号；
- 所有语料变更先生成 candidate，通过校验后才能替换 active，并保留上一有效版本回退。

### 3.3 模型和凭据不变量

- 所有正式模型调用经过后端；前端不直连模型；
- 平台默认凭证和用户 BYOK 分离；
- 平台无需用户 Key 的通道使用 OpenRouter 项目 Key，目录分类固定为 `platform_daily_free_quota`，不能称为无限额度；
- 首批平台模型只允许 Google · Gemma 4 26B A4B（`google/gemma-4-26b-a4b-it:free`）、Dots Studio · Dots3 Note Preview（`dots-studio/dots-3-note-preview:free`）、NVIDIA · Nemotron 3 Super 120B A12B（`nvidia/nemotron-3-super-120b-a12b:free`）；用户必须显式选择具体模型；
- 2026-08-15 核验的 OpenRouter 官方上限是每分钟 20 次；项目账号累计购入 credits 少于 10 美元时每天 50 次，至少 10 美元时每天 1000 次。条款、模型免费状态和上游可用性可能变化，目录必须记录核验时间并检查 Key 状态与公开模型目录；该检查不发起推理，不能证明回答链路实时可用；
- 平台日额度耗尽时明确提示“今日平台免费额度已用完，第二天再来重试吧！着急请使用你自己的 API Key。”；不得自动切换到用户 Key、其他模型或付费端点；
- OpenRouter 项目 Key 只进入服务端 Secret，不进入浏览器、仓库、数据库、日志或 Trace；任何已经暴露的旧 Key 必须撤销或轮换，且不得写入文件；
- BYOK 只用于用户明确发起的 Workflow run；
- BYOK 首批只允许四组固定目录项：`openrouter` + `deepseek/deepseek-v4-flash-0731`、`deepseek` + `deepseek-v4-flash`、`siliconflow` + `Pro/zai-org/GLM-4.7`、`zhipu` + `glm-5.2`；不接受任意 `model_id`、`base_url` 或供应商；四家使用服务端固定 endpoint，只有 `enabled=true` 且当前登录会话已保存对应 Key 的模型可以进入可选列表；
- 普通用户 BYOK 不用于课程包、离线批处理、其他用户或断线后的后台任务；
- Key 明文或密文不能进入 Git、Cookie、响应、历史、Trace、反馈、附件、缓存或日志；
- humanizer 只能在事实、证据和引用锁定后运行；受保护内容变化时返回未润色版本。

### 3.4 登录、所有权和期限不变量

| 数据 | 期限或规则 |
|---|---|
| GitHub 登录会话 | 7 天，过期重新登录 |
| 会话级 BYOK 密文 | 不晚于当前登录会话到期，最长 7 天 |
| 对话、消息、回答、来源、外部资源快照、Trace、反馈、错题 | 30 天 |
| 普通临时材料、OCR 中间结果、图片和附件 | 7 天 |
| 用户主动提交贡献后的必要待审附件／图片副本 | 最多 30 天 |
| 已进入公开 PR 的审校 Markdown/manifest | 按仓库规则 |

- 所有模型调用、会话、模型凭据、上传、贡献、反馈和错题接口都要求有效 GitHub 登录；
- 所有私有资源都检查当前用户归属；
- 期限到达后必须实际清理，不能只在 UI 隐藏；
- 7 天登录会话到期不等于删除 GitHub 用户身份映射；
- 30 天历史可以保留“附件已过期”标记，但不能承诺恢复已删除附件。

### 3.5 Trace 和状态不变量

运行状态与回答状态分开：

```text
run_status:
created
running
completed
interrupted
failed

answer_status:
answered
partial
insufficient_evidence
needs_clarification
refused
error
```

- Trace 来自实际执行节点，不由模型事后编造；
- 学生端和内部日志复用同一组事件，学生端只读取安全字段白名单；
- 不展示或保存模型 CoT、完整内部提示词、Key、token、受限正文、后端堆栈或内部地址；
- 重新生成创建新的回答尝试，不覆盖旧回答。

### 3.6 单一主仓和云端部署不变量

- 当前 `AlexBybye/SCUT_CS` 是唯一公开主仓，同时承载课程资料、审核后知识内容和应用源码；不得另建需要人工同步或承接主要开发入口的应用源码仓；
- 应用目录固定为 `apps/scut-senior/`，内部至少按 `web/`、`api/`、`worker/`、`packages/`、`infra/` 和 `tests/` 分责；目录分层不要求首版拆成微服务；
- 根 README 提供在线 Chat、助手源码、本地运行和资料贡献入口；应用目录 README 提供只检出应用代码的轻量开发方式；
- App CI 主要监听应用运行代码，corpus CI 主要监听 `knowledge/**`、manifest 和语料规则；修改 worker、chunker、索引 schema、manifest/locator 契约或语料构建器时，两条检查都要运行；
- App CI 使用 path filter、partial/sparse checkout 和 `GIT_LFS_SKIP_SMUDGE=1`；Docker build context 限定在应用所需目录，不能把全部原始课程资料发送给 Docker daemon；
- 应用镜像未来进入华为云 SWR 后由 ECS 部署；预算未获批前 `DEPLOYMENT_ENABLED` 保持未设置或 `false`，工作流只允许 validation-only／fail-closed，不登录 SWR、不推送镜像、不修改 ECS；candidate/active 索引、chunk、课程包缓存和运行数据库属于派生产物，不构成第二个源码或知识事实源；
- 未来首发规格为华南-广州优先的 1 vCPU／2GB、40GB 系统盘、1～2Mbps；华为云不部署大模型，首发 ECS 不承担 OCR、embedding、全量索引或课程包构建，生产 SQLite 和轻量本地索引优先，扩容只以监控或功能证据为依据；
- 部署 Secret 只存在于受保护的 GitHub Environment 或华为云 Secret；fork PR 和普通内容校验任务不能读取部署、OAuth、平台模型或 BYOK 加密主密钥；
- GitHub Project 可以汇总当前仓库的资料、前端、后端、Workflow、评测和部署 Issue/PR，但不保存源码、不承担部署，也不继承或替代 Repository 的 Star。

## 4. 每一期的标准执行循环

每个迭代都按以下顺序执行。

### 4.1 进入检查

1. 确认上一期退出条件已经通过；
2. 记录当前 Git 分支、提交、工作区状态和运行配置；
3. 根据本期变更路径和契约影响，明确运行 App CI、corpus CI 或两者，并记录本次绑定的主仓固定 commit；
4. 确认本期依赖的契约版本、语料版本和 Fixture；
5. 列出本期触及的 `PLAN-1` 尚待确认项；
6. 未确认事项只建立接口、配置位、关闭态或 Mock，不自行选型；
7. 确认本期不包含人工资料转写和 `passed` 裁决。

### 4.2 实施顺序

1. 先更新或补充契约测试；
2. 用最小 Fixture 复现目标链路；
3. 实现后端确定性规则和数据归属；
4. 接入模型或 Agent 判断节点；
5. 接入前端交互；
6. 增加失败、中断、降级和清理路径；
7. 增加逐课程评测与 feature flag；
8. 更新运行说明和已知限制。

### 4.3 验证顺序

按本期实际范围执行：

- 单元测试：纯规则、状态机、TTL、字段映射；
- 契约测试：请求、结果、Trace、来源和错误状态；
- 集成测试：数据库、模型适配、索引、GitHub 拉取和对象存储边界；
- 端到端测试：学生端到后端再到持久化和恢复；
- 隔离测试：用户、课程、知识范围和来源类型；
- 泄漏检查：Key、token、提示词、CoT、堆栈和受限内容；
- 回退测试：失败 candidate、旧课程包和运行中断；
- 逐课程评测：不能只看总体平均。
- 仓库与部署隔离：path filter、LFS 跳过、Docker context、fork Secret、纯资料变更不部署应用，以及普通 UI/API 变更不全量重建语料。

### 4.4 退出记录

每期结束至少记录：

- 已实现能力；
- 未实现或关闭能力；
- 测试命令与结果；
- Fixture、语料和配置版本；
- 数据迁移状态；
- 已知降级；
- 尚待确认项；
- 下一期可依赖的稳定契约。

没有通过本期退出条件时，不把后续依赖功能当作已经可用。

## 5. 迭代 0：契约和工程基座

### 5.1 目标

不等待全量资料，用 Mock 身份、Mock 模型和最小 Fixture 打通第一条可持久化的垂直链路。

### 5.2 进入条件

- `PLAN-1` v1.11 为当前唯一功能基座；
- 当前仓库、分支、Git LFS、忽略规则和已有可复用代码可只读审计；
- 10 个首批课程及别名可用于课程注册表，大学物理实验与 SRP 不得登记为知识语料；
- 可以制作少量 Markdown/manifest Fixture；
- SWR→ECS 是未来目标发布路径，但预算获批前保持 validation-only／fail-closed；迭代 0 和后续本地实现不以创建华为云资源、生产 HTTPS/OAuth 域名或云端数据库为进入条件。

### 5.3 执行动作

- [ ] 只读审计仓库结构、分支、Git LFS、忽略规则、现有工程和可复用代码；
- [ ] 冻结单仓目录，应用代码只进入 `apps/scut-senior/`，不在仓库根目录铺开应用依赖，也不新建主要应用代码仓；
- [ ] 建立课程注册表，包含课程 ID、显示名称、别名和课程开放开关；
- [ ] 冻结五个 Workflow 枚举和 `workflow_payload` 分型；
- [ ] 冻结回答方式、风格、知识范围、课程范围和模型来源枚举；
- [ ] 冻结 `run_status`、`answer_status`、`evidence_status`；
- [ ] 冻结 Workflow 请求、结果、`citations[]`、`external_resources[]` 和 Trace 事件契约；
- [ ] 冻结 Bilibili 模型聚焦关键词和唯一固定匿名搜索入口接口；搜索入口使用空 `resource_id` 和未审核状态；不建立具体视频资产、目录或运行时匹配；
- [ ] 冻结 SCUT 评测 case 和 runner 契约；
- [ ] 建立最小 Markdown、manifest、历年题和 Bilibili 匿名搜索入口契约样例；
- [ ] 实现 manifest/frontmatter/locator 校验器；
- [ ] 在 `apps/scut-senior/` 中初始化 `web/`、`api/`、`worker/`、`packages/`、`infra/`、`tests/`，以及数据库迁移和应用 README；
- [ ] 建立按路径隔离的 App CI 与 corpus CI；App CI 使用 partial/sparse checkout、`GIT_LFS_SKIP_SMUDGE=1`，Docker build context 只覆盖应用所需目录；
- [ ] 对 worker、chunker、索引 schema、manifest/locator 契约和语料构建器变更建立“双检查”规则：应用代码测试与 candidate 兼容性构建均必须运行；
- [ ] 建立默认 validation-only／fail-closed 的 SWR→ECS 目标部署骨架；预算获批前不读取部署 Secret、不登录 SWR、不推送镜像、不更新 ECS；
- [ ] 在根 README 增加开发中的助手源码入口；正式在线 Chat 地址在迭代 4 验收后开放；
- [ ] 用 Mock 身份和 Mock 模型打通“选课程与 Workflow → 运行 → 保存回答、来源和 Trace → 重新读取”；
- [ ] 为模型供应商、关系存储、向量索引、对象存储、任务系统和 GitHub App 建立可替换边界，不在本期擅自选型。

### 5.4 必验场景

- 非法 Workflow、状态或知识范围被拒绝；
- 非 `passed` Fixture 不进入可检索集合；
- page、slide、question、heading 无效或顺序错误时校验失败；
- `source_title` 确定性来自 manifest title；
- Bilibili 匿名搜索入口契约样例与 citations 契约完全分离；
- Mock 垂直链路能持久化并恢复回答、来源和 Trace；
- 前后端契约测试与 CI 通过；
- 纯知识内容变更不会触发 Web/API 部署，普通 UI/API 变更不会触发全量 corpus 构建；
- 普通 App CI 和 Docker 构建不下载、复制或发送全部原始资料及无关 LFS 对象；
- fork PR 无法读取华为云、OAuth、平台模型或 BYOK 加密主密钥等 Secret。

### 5.5 退出条件

- V1 请求、结果、来源、Trace 和枚举契约已经可执行；
- 课程注册表和最小 Fixture 可供后续迭代复用；
- Mock 垂直链路闭合；
- 单一主仓目录、App CI/corpus CI 触发边界和 SWR→ECS fail-closed 骨架可执行；真实发布不属于预算延期期间的退出条件；
- 未确认项仍明确处于未配置、关闭或 Mock 状态；
- 没有把 Mock 能力描述成真实 OAuth、真实模型或生产检索。

## 6. 迭代 1：身份、平台默认模型、BYOK 和历史

### 6.1 目标

建立所有后续在线能力共同依赖的身份、模型调用、凭据保护和历史持久化基座。

### 6.2 决策门

平台默认模型通道已经确认：

- 供应商为 OpenRouter，分类为 `platform_daily_free_quota`；
- 首批模型固定为 Google · Gemma 4 26B A4B、Dots Studio · Dots3 Note Preview、NVIDIA · Nemotron 3 Super 120B A12B；
- 用户显式选择模型；额度耗尽、模型不可用或健康检查失败时不自动切换到用户 Key、其他模型或付费端点。

BYOK 每家唯一目录模型已冻结为：OpenRouter `deepseek/deepseek-v4-flash-0731`（2026-08-15 OpenRouter 周榜第 1）、DeepSeek `deepseek-v4-flash`（官方稳定别名）、硅基流动 `Pro/zai-org/GLM-4.7`（2026-08-16 官方 Chat Completions 默认示例）、智谱 `glm-5.2`（2026-08-16 当前可调用旗舰与 OpenAI 兼容示例）。智谱 GLM-5.3 当日仍明确标注 API 尚未上线，不登记为可调用目录。2026-08-16 01:05 CST 的新增冻结证据链接见 PLAN-1 v1.11 第 3.1 节；硅基流动无公开调用量排名，不将默认示例冒充调用量最高。四家 endpoint 均已冻结；真实用户 Key 实网调用仍需用户在当前登录会话自行保存 Key，自动化测试使用注入 HTTP 替身并不得冒充实网证据。华为云首发规格已确认但启用延期；生产 HTTPS/OAuth 域名、部署身份、灰度和回滚只在预算恢复后冻结。

未确认项只能完成适配接口和禁用态，不能任意开放 `base_url` 或 `model_id`。平台通道也必须在项目 Secret、健康检查和限额处理可用后才能启用，不能把已冻结目录写成已经完成的真实调用。

### 6.3 执行动作

- [ ] 保持 SWR→ECS 骨架 fail-closed；先在本地／测试环境完成可注入的 HTTPS、OAuth 回调和 Secret 边界，不创建华为云资源；
- [ ] 实现 GitHub OAuth `state` 校验；
- [ ] 使用 GitHub 不可变数字 ID 建立本地用户；
- [ ] 用户 OAuth 只申请身份所需权限；不再需要调用 GitHub API 时，不长期保存用户 access token；
- [ ] 建立服务端会话和 `HttpOnly + Secure + SameSite` Cookie；
- [ ] 登录会话 TTL 固定为 7 天；
- [ ] 所有用户资源执行所有权检查；
- [ ] 所有受保护接口统一返回 `auth_required`；
- [ ] 实现后端模型目录、`platform_default`／`user_key` 分路和可用性／限流状态；
- [ ] 建立四组固定 BYOK 目录项及服务端固定 endpoint（无用户可选地区或地址）：OpenRouter `https://openrouter.ai/api/v1/chat/completions` + `deepseek/deepseek-v4-flash-0731`、DeepSeek `https://api.deepseek.com/chat/completions` + `deepseek-v4-flash`、硅基流动 `https://api.siliconflow.cn/v1/chat/completions` + `Pro/zai-org/GLM-4.7`、智谱 `https://open.bigmodel.cn/api/paas/v4/chat/completions` + `glm-5.2`；拒绝任意供应商、任意 `base_url` 和任意模型 ID；
- [ ] 平台目录只放行三项已确认的 OpenRouter `platform_daily_free_quota` 模型，并要求用户显式选择；
- [ ] 通过 Key 状态与公开模型目录，对模型是否仍存在、零价格状态、结构化输出支持和目录接口可达性执行带 `last_checked_at` 的检查；不再满足条件时将对应模型标记为不可选；检查不发起推理，运行时 429／5xx 单独报错；
- [ ] 执行平台每分钟／每日额度边界；日额度耗尽时返回固定提示，不自动切换到用户 Key、其他模型或付费端点；
- [ ] OpenRouter 项目 Key 只从服务端 Secret 读取；撤销或轮换任何已暴露旧 Key，禁止写入仓库、配置样例、数据库、日志或 Trace；
- [ ] 实现 BYOK 的 AEAD 会话级加密；
- [ ] 密文绑定 `user_id + auth_session_id + provider_id`；
- [ ] 实现 Key 保存／替换、脱敏查询、删除、到期清理和请求内解密；
- [ ] 加密主密钥在本地／CI 验证中只通过测试 Secret 或进程环境注入，正式部署后才进入华为云运行 Secret；始终保留轻量 `key_version` 且不得入库或日志；
- [ ] 持久化用户、对话、消息、回答尝试、来源、外部资源快照和 Trace；
- [ ] 随回答保存 `corpus_version`、`course_pack_version`、`workflow_version`、`model_source`、供应商／模型和安全的 availability／计费状态；
- [ ] 实现历史查看、重命名、删除和重新生成新 attempt；
- [ ] 实现 GitHub 登录、模型选择、Key 保存／替换／删除／脱敏状态／到期时间和历史记录的前端交互；
- [ ] 实现历史类内容 30 天清理，并确保会话过期不会删除 GitHub 用户身份映射；
- [ ] 本期只冻结 `interrupted` 状态、持久化边界和迭代 3 可复用接口；真实流式取消、页面断开与 `interrupted` 落库随迭代 3 的流式 Runtime 一并验收，不作为同步迭代 1 的退出条件，也不得用合成状态冒充完成。

### 6.4 必验场景

- 未登录不能创建会话、运行 Workflow、管理凭据或访问他人资源；
- OAuth `state`、Cookie 属性和 GitHub 数字 ID 映射正确；
- 同一有效登录会话中，BYOK 跨硬刷新和新标签页仍可使用；
- 新独立登录会话默认要求重新输入 Key；
- BYOK 不晚于登录会话到期，最长 7 天；
- 登出、撤销、到期或主动删除后，旧密文不能继续调用；
- 页面和接口不能取回 Key 明文或密文；
- 数据库和备份不存在 Key 明文；密文只存在于会话凭据专用存储，不进入响应、历史、Trace、反馈、附件、缓存或日志；
- 平台目录只包含三项已确认模型，用户选择哪一项就只调用哪一项；
- 平台日额度耗尽时显示“今日平台免费额度已用完，第二天再来重试吧！着急请使用你自己的 API Key。”，且不静默切到 BYOK、其他模型或付费端点；
- 目录检查发现模型移除、零价格或结构化输出条件变化时，对应模型明确不可选；该检查不作为真实推理可用性证据，运行时 429／5xx 仍如实失败；
- OpenRouter 项目 Key 只存在于服务端 Secret，已暴露旧 Key 已撤销或轮换，仓库、数据库、响应、历史、Trace 和日志均不存在该 Key；
- BYOK 只允许 `openrouter` + `deepseek/deepseek-v4-flash-0731`、`deepseek` + `deepseek-v4-flash`、`siliconflow` + `Pro/zai-org/GLM-4.7`、`zhipu` + `glm-5.2`；其他供应商、用户自定义 `base_url` 和任意模型被拒绝；四家卡片始终可见，只有 `enabled=true` 且当前登录会话已保存对应 Key 的模型进入可选列表；
- 历史能跨刷新和重新登录恢复；
- 重新生成保留旧 attempt。
- 30 天历史清理实际执行，7 天登录会话到期不会删除用户身份映射。
- 预算延期期间部署工作流保持 validation-only／fail-closed；恢复部署后才验证应用消费 SWR 镜像、ECS 不完整检出原始资料仓以及失败回退上一镜像。

### 6.5 退出条件

- 身份、资源归属、7 天会话和历史恢复闭环通过；
- 历史运行版本／模型元数据完整，30 天清理和用户映射保留规则通过；
- 模型目录和两条凭据通道完成隔离；
- 三项 OpenRouter 平台模型的显式选择、健康检查、限额提示和无自动降级边界通过；
- BYOK 保存、调用、删除和到期清理通过泄漏检查；
- 真实供应商只包含已经确认并登记的条目。

## 7. 迭代 2：Markdown 入库、检索和课程包

### 7.1 目标

把 GitHub 主分支中的人工 `passed` Markdown 变成可版本化、可回查、可回退的检索语料。

### 7.2 进入条件

- 迭代 0 的课程、manifest、来源和状态契约已冻结；
- 至少有一小批人工 `passed` Markdown；
- 测试资料中包含可验证的 page、slide、question 或 heading 定位；无可靠 locator 的资料允许按契约退化为资料名或标题；
- GitHub 公共事实源和本地／GitHub corpus CI 构建边界可用；华为云部署继续延期也不阻塞。

### 7.3 执行动作

- [ ] 由同仓 corpus builder 读取 SCUT_CS 主分支固定 commit 中的 `knowledge/manifest.csv`、`passed` Markdown 和必要 assets；云端按需检出这些路径，不完整拉取全部原始资料和 LFS 对象；
- [ ] 只导入 manifest 状态为 `passed` 的 Markdown；
- [ ] 解析 frontmatter、page/slide/question 标记和 H1-H6 标题栈；
- [ ] page、slide、question 作为硬边界统一切块；
- [ ] chunk 同时继承 page/slide、question 和 `heading_path`；
- [ ] 使用 `source_id + locator + ordinal` 等可读组合生成 chunk ID；
- [ ] 生成包含 `source_id`、`source_title`、`course_id` 和可用 locator 的 payload；
- [ ] 为检索候选生成请求内来源编号 `[S1] [S2] ...`，并建立编号到已验证 payload 的后端映射和回查；
- [ ] 建立 candidate 引用完整性校验；
- [ ] 建立默认单课程硬过滤；
- [ ] 建立受控 `course_scope=cross` 和显式课程集合校验，默认保持关闭；
- [ ] 建立课程资料索引；
- [ ] 按已审核 question 标记建立历年题题目级索引；
- [ ] 生成课程预生成包、版本和公共缓存；
- [ ] 课程包绑定 `course_id`、`corpus_version`、`workflow_version`、`outline_version`；
- [ ] 实现 candidate 验证、active 激活、上一版回退和课程开关；
- [ ] `knowledge/**`、manifest 和语料规则更新只触发 candidate 构建，不能直接覆盖 active，也不部署 Web/API；Bilibili 匿名搜索入口由运行时确定性生成，不属于 corpus 构建输入；
- [ ] worker、chunker、索引 schema、manifest/locator 契约或语料构建器变化同时运行应用检查和受控 candidate 重建。

### 7.4 必验场景

- 每个 chunk 都携带正确 source、course、title 和可用 locator；原资料无可靠 locator 时保留资料名／标题且不补造；
- page/slide 与 question 可以同时继承，不因拆题丢失页码；
- `source_title` 与 manifest title 一致；
- 已提供的 locator 能在已审核 Markdown 中真实回查；
- `[S1]` 能确定性映射为资料名、页码／幻灯片／题号或标题；不存在、跨课程或已过滤编号不能通过回查；
- 非 `passed`、source 不存在、课程／标题不一致或 locator 乱序会阻断 candidate；
- candidate 失败时 active 不变；
- 单课程模式不存在跨课程来源；
- cross 只检索用户显式选择的课程，每条来源保留课程；
- 课程包的结论能回到资料或题目来源；
- 用户大纲、错题和学习状态不会进入公共包；
- 新课程包失败时继续使用上一有效包；
- 激活和回退都能复现。
- 构建日志能够证明只读取固定 commit 的审核后知识路径和必要构建规则，没有完整下载全部原始资料及无关 LFS；
- 每个 candidate/active 都记录主仓 commit、manifest/locator 契约版本和 builder 版本，纯知识更新不触发 Web/API 部署。

### 7.5 退出条件

至少一批真实 `passed` 语料完成以下闭环：

```text
GitHub 固定版本
→ chunk
→ candidate
→ 引用完整性与课程隔离校验
→ active
→ 检索
→ [S1] 编号与后端来源映射
→ 来源回查
→ 回退
```

同时，历年题题目级索引、课程包版本和逐课程开关可用；每个 active corpus 能回查当前主仓固定 commit、manifest/契约版本和构建版本。

## 8. 迭代 3：Workflow Runtime 和真实 Trace

### 8.1 目标

建立五个 Workflow 共用的固定运行骨架、真实事件流、证据与引用守卫。

### 8.2 执行动作

- [ ] 实现固定 Workflow 状态机；
- [ ] Agent 只用于理解问题、识别知识点、组织讲解和在同一次回答结构中给出 0～3 个 Bilibili 聚焦检索词；不增加独立的推荐理由或 URL 生成权限；
- [ ] 课程过滤、权限、检索、缓存、知识范围、来源和历史使用确定性节点；
- [ ] 建立统一 `workflow_run` 记录；
- [ ] 实现流式回答和结构化 Trace；
- [ ] 实现 `answer_blocks[]` 的 repository／user_material／general／personalized_analysis 类型，以及独立的 `evidence_status`；
- [ ] 消费迭代 2 已建立的 `[S1] [S2] ...` 候选编号与后端来源映射；
- [ ] 校验模型引用只属于本次候选、课程和权限范围；
- [ ] 实现 humanizer 前后保护字段校验；
- [ ] 实现取消、短暂重试、中断和降级状态；
- [ ] 建立学生 Trace 安全白名单和内部调试字段分层；
- [ ] Trace 与回答一起保存并恢复；
- [ ] 建立五个 Workflow 共用的知识点标准化节点；
- [ ] 建立 Bilibili 资源节点：清洗、去重、限长模型检索词，后端固定生成匿名搜索入口；不读取或匹配任何具体视频资产；
- [ ] 关键词非空时必须且只返回 1 条 `https://search.bilibili.com/all?keyword=...` 搜索入口，不补充任何具体视频直链；
- [ ] 五个 Workflow 分别使用：所问概念、大纲／薄弱点、题目主知识点、错误根因、临时材料标题与主要知识点；临时材料不按全文词频乱推；
- [ ] `external_resources[]` 保留可空 `resource_id`、`course_id`、平台、类型、标题、URL、命中知识点、查询关键词、审核状态、可选生成时间和 `supplementary_only` 角色；Bilibili 只输出空 `resource_id` 的 `unreviewed_live_search` 搜索入口；
- [ ] 模型和前端都不能提供 URL；后端只允许固定 Bilibili 搜索 host/path，回答结果不能包含具体视频直链。

### 8.3 必验场景

- Trace 由每个真实节点直接产生，不是模型生成的思考摘要；
- Trace 不泄露 CoT、完整提示词、Key、token、堆栈、内部地址或受限正文；
- 无效、跨课程、已过滤或不属于本次候选的引用不能进入最终答案；
- `仅课程资料` 不调用通用知识，并强制关闭 Bilibili；
- 默认知识范围的 general 内容有轻量标记，不伪造仓库引用；
- `external_resources[]` 与 `citations[]` 分开，且不改变证据状态；
- Bilibili 节点失败不阻塞主回答；
- 模型聚焦词经过后端 NFKC、控制字符、空白、去重、数量和长度校验，不能通过 `&`、`#` 或 URL 文本改变固定搜索 host/path；
- 关键词非空时唯一搜索入口一定存在，且没有具体视频直链；
- 不匿名抓取搜索结果、不依赖 WBI 私有接口、不读取字幕、不根据播放或点赞打质量分；
- humanizer 改动事实、公式、术语、引用、证据状态或回答状态时回退；
- 页面断开时尽力取消上游请求，并保存 `interrupted`；
- BYOK 不进入离线队列继续运行；
- 五种 Workflow 不会静默互相切换。

### 8.4 退出条件

- 五种 `workflow_type` 都能显式进入同一 Runtime 骨架；
- 流式事件、最终结果、历史 Trace 来自同一 run；
- 引用 Guard、证据标记、humanizer 和安全过滤闭环通过；
- Trace 排序分数默认展示程度继续保留为待确认配置。

## 9. 迭代 4：知识答疑

### 9.1 目标

完成第一个面向学生的完整 Workflow，并在 SCUT_CS 仓库入口可发现。

### 9.2 执行动作

- [ ] 实现单课程文本多轮；
- [ ] 支持中文和英文问题；
- [ ] 实现回答方式、表达风格和知识范围三组控制；
- [ ] 支持概念、原理、概念对比和常见误区；
- [ ] 返回相关知识点和题目级历年题；
- [ ] 资料不足时返回覆盖缺口；
- [ ] `仅课程资料` 证据不足时明确停止猜测；
- [ ] 默认知识范围允许轻量标记的通用补充；
- [ ] 实现统一折叠输入框和五个 Workflow 说明；
- [ ] 实现课程选择和默认关闭的跨课程开关；开启前提示可能增加 Token 消耗、BYOK 费用和术语混淆；
- [ ] 实现折叠来源、完成后折叠 Trace 和独立折叠 Bilibili；
- [ ] 实现回答有帮助／没帮助、知识错误、没有回答问题和简短说明；
- [ ] 实现 Bilibili 搜索入口无法打开／关键词不相关反馈；未审核搜索入口使用 `url_snapshot + course_id + matched_topic`；
- [ ] 反馈关联用户、问题、回答、课程、Workflow、来源、Trace、语料／课程包／Workflow 版本和当时模型安全元数据，不自动修改知识库；
- [ ] 建立维护者轻量失败问题列表和同题重跑入口；
- [ ] 建立维护者轻量视图，显示资料处理状态、反馈筛选、高频失败、同题重跑、当前语料／课程包版本和逐课程评测结果；Bilibili 只接入聚焦检索词、匿名搜索入口与入口反馈，贡献 PR 状态、审核结果与链接在迭代 7 接入；
- [ ] 建立并运行 SCUT 专属评测集，覆盖课程知识、题目级真题、资料稀疏时的通用补充、证据不足、多轮追问、跨课程开关和来源标记；
- [ ] 在 SCUT_CS 根 README/站点增加在线 Chat、`apps/scut-senior/` 源码、本地运行和资料贡献入口。
- [ ] 对外文案使用“在已有高 Star 的 SCUT_CS 仓库中新增并落地课程 RAG 助手”，不把仓库既有 Star 表述为 RAG 子功能独立获得。

### 9.3 必验场景

- 单课程不存在串课；
- 多轮上下文不会静默改变课程、Workflow 或知识范围；
- 中文、英文及四种回答方式可运行；
- humanizer 不改变受保护内容；
- 仅资料模式严格停止猜测；
- 默认模式的通用补充不产生仓库 citation；
- 相关真题来自题目级索引；
- Bilibili 匿名搜索入口只进入外部资源区域；
- 硬刷新和重新登录后，回答、来源、Trace 和反馈可恢复；
- 修复后重跑创建新 attempt，旧结果仍保留；
- SCUT 评测集的七类最小覆盖均有 case，且每门课程独立评测；未达标课程保持关闭。

### 9.4 退出条件

`knowledge_qa` 完成“登录 → 选择课程和控制 → 多轮问答 → 来源／Trace／匿名搜索入口 → 反馈 → 历史恢复”的真实闭环，至少一个达标课程可以独立开放；从根 README 可以到达已经验收的在线 Chat、助手源码、本地运行和资料贡献入口。

## 10. 迭代 5：备考复习

### 10.1 目标

利用课程包和历年题结构，提供有大纲和无大纲两条证据化备考路径。

### 10.2 执行动作

- [ ] 有大纲路径采用“用户大纲 > 课程资料 > 历年题 > 允许时的通用知识”；
- [ ] 无大纲路径采用“历年题 > 课程资料 > 允许时的通用知识”；
- [ ] 输出范围和证据说明；
- [ ] 输出知识点分层、建议顺序和资料位置；
- [ ] 输出历年题年份覆盖、题型分布和客观出现次数；
- [ ] 按知识点组织题组和代表性真题；
- [ ] AI 样题明确标记为 AI 生成；
- [ ] 输出复习建议、未覆盖内容和证据边界；
- [ ] 复用 Bilibili 节点；
- [ ] 隔离公共课程包与用户私有大纲、薄弱点和学习状态；
- [ ] 课程包构建不使用普通用户 BYOK。

### 10.3 必验场景

- 有大纲时用户大纲优先；
- 无大纲时明确声明不是官方范围，也不构成考试重点预测；
- 所有统计显示样本年份和题目数量，并能回到题目来源；
- 不输出命题概率、“必考”或变相预测；
- 私有输入不进入公共课程包和跨用户缓存；
- 新课程包失败时继续使用旧有效版本；
- 公共包的版本、失效、重建和回退可复现；
- `exam_review` 的来源、Trace 和 Bilibili 仍遵守共用契约。

### 10.4 退出条件

有大纲和无大纲两条路径均通过逐课程验收，课程包、题目统计和个性化输入边界清楚。

## 11. 迭代 6：文本题目辅导和错题复盘

### 11.1 目标

完成文本题目的知识点识别、相似真题、分级帮助和用户主动错题闭环。

### 11.2 执行动作

- [ ] 识别文本题目的主要知识点；
- [ ] 检索课程资料、相似真题和已有题解；
- [ ] 按用户选择提供知识点、思路、分步提示、完整讲解或答案分析；
- [ ] 历史试题允许完整讲解；
- [ ] AI 新生成练习题明确标记；
- [ ] 实现用户作答分析；
- [ ] 实现错误位置和概念、条件、公式、方法、计算、审题、表达等错误类型；
- [ ] 输出正确推理、下次检查动作和可选迁移练习；
- [ ] 错题只由用户主动保存；
- [ ] 错题关联原题、用户答案、讲解、来源和当时语料版本；
- [ ] 实现错题查询、保存和删除。

### 11.3 必验场景

- 相似真题真实来自题目级索引；
- AI 练习与历史真题不会混淆；
- 提示层级与用户选择一致；
- 回答失败不会自动保存错题；
- 错题所有权、历史恢复和 30 天期限正确；
- 文本版不冒充已经支持图片；
- 不建设独立学术诚信分类器、考试识别器或阻塞闸门；
- 仍遵守版权、隐私和模型供应商策略。

### 11.4 退出条件

`problem_tutor` 和 `mistake_review` 均完成真实端到端闭环，用户能主动保存、查看和删除错题。

## 12. 迭代 7：临时材料精读和贡献 PR

### 12.1 目标

支持用户在当前会话精读粘贴文本或 Markdown，并在主动授权后进入受审核的资料贡献流程。

### 12.2 决策门

实现自动 PR 前确认：

- 对象存储与离线任务的最终实现；
- GitHub App 的实现方式和权限；
- 账号注销、提前删除和导出规则中与临时材料有关的部分。

如果 GitHub App 尚未确认，按 PLAN 允许进入维护者待处理队列，不得用用户 OAuth token 冒充自动 PR 能力。

### 12.3 执行动作

- [ ] 支持粘贴文本和 Markdown；
- [ ] 会话内临时切分与课程资料联合检索；
- [ ] 区分 repository 和 user_material 来源；
- [ ] “材料写了什么”以材料原文优先；
- [ ] “材料说得对不对”以仓库资料核验；
- [ ] 冲突内容分别陈述；
- [ ] 临时材料默认不进入公共索引、课程包或跨用户缓存；
- [ ] 普通临时材料执行 7 天 TTL；
- [ ] 建立贡献 `draft/submitted/pr_open/merged/rejected/expired` 状态；
- [ ] 提交前确认课程、来源、公开分享权利和不含敏感信息；
- [ ] 提交前提示公开仓库 PR 可能长期公开；
- [ ] 用户预览转换结果；
- [ ] 使用 GitHub App/机器人隔离分支创建 PR，或进入维护者待处理队列；
- [ ] GitHub App／机器人只授予目标仓库最小 Contents 与 Pull Requests 权限，不使用用户 OAuth token；
- [ ] GitHub App／机器人服务端凭证不进入数据库或日志；
- [ ] PR 不自动合并；
- [ ] 公开展示贡献者 GitHub login 前另行取得同意；默认使用机器人和不透明贡献 ID；
- [ ] 必要待审附件／图片副本最多保留 30 天；
- [ ] 只有人工合并、资料 `passed` 和 candidate 验证后才能进入 active；
- [ ] 实现临时材料和贡献状态接口；
- [ ] 用户只能读取自己的贡献状态和 PR 链接。

### 12.4 必验场景

- 未登录和越权访问失败；
- 临时材料只对所属用户可见；
- 未提交、待审、私有、拒绝或过期材料不能跨用户检索；
- 用户没有主动确认时不能提交公共贡献；
- PR 描述和状态不含 Key、token、完整私密载荷或多余个人信息；
- PR 不自动合并；
- 合并不会直接绕过 candidate；
- 普通原件 7 天、必要待审副本最多 30 天的清理任务实际生效；
- 贡献材料复用统一资料转换和人工审核 SOP。

### 12.5 退出条件

文本／Markdown 精读、来源隔离、TTL 和贡献状态闭环通过；无论采用自动 PR 还是待处理队列，都不能绕过人工审核和 candidate/active 发布链。

## 13. 迭代 8：图片 OCR 与复杂图片理解

### 13.1 目标

在迭代 7 的附件、所有权和 TTL 基座上增加图片问答，不直接跳到视觉相似检索。

### 13.2 执行动作

- [ ] 实现图片上传和临时存储；
- [ ] 限制格式、大小、像素和频率；
- [ ] 实现 OCR；
- [ ] OCR 低于 `0.85` 时进入用户确认、裁剪或重传路径；
- [ ] 高于 `0.85` 也不自动宣称识别正确；
- [ ] 支持公式识别与 LaTeX；
- [ ] 支持表格、图表、流程图和结构图解释；
- [ ] 支持图片题目知识点识别和分级提示；
- [ ] 支持用户图片作答讲评；
- [ ] 区分用户上传、仓库资料和通用知识来源；
- [ ] 原始图片、OCR 中间结果和附件执行 7 天 TTL；
- [ ] 30 天历史只保留回答、来源元数据和附件过期标记。

### 13.3 必验场景

- OCR 低置信不静默猜测；
- 公式、数字、单位、代码和表格在固定测试中无明显语义错误；
- 上传限制和用户所有权有效；
- 临时图片默认不进入公共知识库；
- 7 天后原图和 OCR 中间结果确实删除；
- 历史不会承诺恢复过期附件；
- 图片题目仍遵守 Workflow、来源、Trace 和回答控制契约。

### 13.4 退出条件

OCR、低置信交互、复杂图片解释和图片题目辅导通过固定测试；视觉相似检索继续保持关闭。

## 14. 迭代 9：视觉检索与全仓扩展

### 14.1 目标

在已有文字检索基线上验证视觉检索是否真的增益，并把构建能力扩展到约 10GB 全仓资料。

### 14.2 执行动作

- [ ] 建立页面和幻灯片视觉索引；
- [ ] 建立图片与仓库页面相似检索；
- [ ] 建立纯 OCR 文本检索对照；
- [ ] 用固定测试比较两条路径；
- [ ] 只有视觉方案明显更好时才开放学生端；
- [ ] 全仓只消费 GitHub 主分支中 `passed` 内容；
- [ ] 全仓扩展继续按固定 commit 和必要路径增量获取内容，不让 App CI 或 Docker 构建携带全部资料；
- [ ] 支持约 10GB 资料的增量 candidate 构建；
- [ ] 建立缓存、性能和逐课程质量收敛；
- [ ] 保留课程开关、active 回退和构建失败保护；
- [ ] 跨课程继续由 feature flag 控制并默认关闭。

### 14.3 必验场景

- 视觉结果仍携带 course、source 和 locator；
- 视觉引用仍通过候选编号 Guard；
- 视觉检索没有明显优于纯 OCR 文本检索时，学生端保持关闭；
- 增、删、改资料能增量重建；
- candidate 失败不替换 active；
- 全仓构建可以回退；
- 每门课程独立评测；
- cross 只检索显式课程集合，每条来源标明课程并展示 Token／BYOK 费用提示。

### 14.4 退出条件

- 视觉检索是否开放由固定对照评测决定；
- 全仓 candidate → 验证 → active／回退闭环稳定；
- 只开放逐课程达标能力；
- 跨课程正式门槛、最大课程数和文案未确认前，不扩大开放。

## 15. 跨迭代验收矩阵

每次准备开放新能力时，至少复核以下项目。

### 15.1 课程和检索

- [ ] 单课程模式不存在跨课程来源；
- [ ] cross 默认关闭并只查显式课程集合；
- [ ] 每条跨课程来源标明课程；
- [ ] 每条 citation 属于本次允许的资料、历年题或用户材料；
- [ ] 无效、跨课或被过滤的候选编号不会进入答案；
- [ ] 每门课程单独评测和开关。

### 15.2 知识范围和回答

- [ ] 仅资料模式不调用通用知识；
- [ ] 证据不足时明确停止猜测；
- [ ] 默认模式的通用补充有轻量标记；
- [ ] 通用内容不伪造仓库 citation；
- [ ] humanizer 不改变事实、公式、术语、引用、证据或状态；
- [ ] Workflow 不静默切换。

### 15.3 Bilibili

- [ ] 只在默认知识范围启用；
- [ ] `仅课程资料` 强制关闭；
- [ ] 模型只输出 0～3 个聚焦词，后端执行清洗、去重、限长并固定生成 Bilibili 搜索 URL；模型不能提供 URL；
- [ ] 关键词非空时必须且只返回 1 条匿名搜索入口，不返回任何具体视频直链；
- [ ] 不建设、审核或维护具体视频资产；不匿名抓搜索结果、不依赖 WBI 私有接口、不读取字幕、不总结视频；
- [ ] `external_resources[]` 与 `citations[]` 分离；
- [ ] 节点失败不影响主回答；
- [ ] 搜索入口无法打开／关键词不相关反馈能关联本次运行；
- [ ] 未审核搜索入口没有 `resource_id`，反馈保存 `url_snapshot + course_id + matched_topic + query_keywords + generated_at`。

### 15.4 身份、凭据和期限

- [ ] 未登录统一返回 `auth_required`；
- [ ] 用户不能访问他人历史、附件、错题或贡献；
- [ ] BYOK 不晚于登录会话到期；
- [ ] Key 明文和密文不进入禁止位置；
- [ ] 默认模型不会静默切换到付费路径；
- [ ] 30 天、7 天和贡献副本 30 天期限正确执行；
- [ ] 过期数据实际删除。

### 15.5 Trace、反馈和恢复

- [ ] Trace 来自真实节点；
- [ ] 不暴露 CoT、完整提示词或敏感载荷；
- [ ] 历史能跨刷新和重新登录恢复；
- [ ] 反馈关联问题、回答、来源、Trace 和版本；
- [ ] 反馈不会自动修改知识库；
- [ ] 同题重跑创建新 attempt 并保留旧结果；
- [ ] 失败课程可独立关闭。

### 15.6 单一主仓和云端部署

- [ ] 应用源码只以当前 SCUT_CS 仓库的 `apps/scut-senior/` 为规范版本，不存在需要人工同步的第二个主要应用源码仓；
- [ ] 根 README 可以直接到达在线 Chat、助手源码、本地运行说明和资料贡献入口；
- [ ] App CI 使用路径过滤并跳过无关 LFS，Docker build context 不包含全部原始课程资料；
- [ ] 纯资料变更只构建和验证 candidate，不部署 Web/API；普通 UI/API 变更不重建全量语料；
- [ ] worker、chunker、索引 schema、manifest/locator 契约或语料构建器变化同时通过应用测试和 corpus 兼容性验证；
- [ ] 预算延期期间 `DEPLOYMENT_ENABLED` 保持未设置或 `false`，工作流不登录 SWR、不推送镜像、不修改 ECS；恢复部署后再验收镜像发布和上一有效镜像回退；
- [ ] active corpus 可以回查主仓固定 commit、契约版本和构建版本；
- [ ] fork PR 和普通内容任务不能读取任何部署或运行 Secret；
- [ ] GitHub Project 不参与源码同步、构建或部署。

## 16. 尚待确认项的处理规范

以下四项继续以 `PLAN-1` 第 20 节为准：

1. Trace 排序分数默认展开程度；
2. 华为云部署恢复时间、SWR→ECS 流水线具体采用的 CI 身份认证、灰度和回滚方式，以及指标证明需要后才评估的 PostgreSQL、Qdrant、对象存储、独立离线任务和 GitHub App；
3. 账号注销、历史提前删除和数据导出规则；
4. 跨课程正式开放门槛、同时课程数量和提示文案。

处理方式：

- 在代码中只保留接口、配置、feature flag、Mock 或禁用态；
- 在进入依赖它的真实迭代前请求确认；
- 已确认的四组 BYOK 供应商／模型和 endpoint 写入固定目录；只有完成 AEAD 与受控调用验收、且当前会话已保存对应 Key 的启用项可以进入可选列表，不开放任意模型、地址或供应商；
- 没有符合条件的选项时明确不可用，不做隐式替代。

## 17. 当前明确不进入本 SOP 的实现

- 重复 SCUT_CS 的资料导航；
- 独立自动复习路线产品；
- 每日学习计划；
- 课程推荐；
- 考试重点预测；
- 自动或 3D 知识图谱；
- 前端可提取的共享 Key；
- 默认池以外的模型代付；
- 前端直连模型主链路；
- 多 Agent 自主执行平台；
- 用户反馈自动修改知识库；
- 未经人工审核自动发布语料；
- 另建与 SCUT_CS 并列、需要双写或承接主要开发入口的应用源码仓；
- 用 GitHub Project 代替 Repository 保存代码、继承 Star 或承担部署；
- 让每次 App CI 或 Docker 构建完整拉取全部原始资料和无关 LFS 对象；
- 模型 CoT、完整提示词或敏感载荷展示；
- 资料阶段的哈希血缘、bbox、复杂 Canonical Element 或多解析器跑分体系；
- 独立学术诚信分类器和考试场景防御模块。

## 18. 下一次代码对话的启动清单

迭代 0 已完成；迭代 1 的本地／测试代码切片已经闭合，真实供应商实网、真实 GitHub 凭据回调和生产部署证据仍明确缺失。下一次实际编码先按外部条件分流：

```markdown
- [ ] 只读审计当前分支、工作区、未提交迭代 1 差异和运行配置
- [ ] 确认 PLAN-1 v1.11 和本 SOP v1.7 仍是最新版本
- [ ] 保持 `DEPLOYMENT_ENABLED=false`，不创建或修改华为云资源
- [ ] 确认聊天中公开过的 OpenRouter Key 已在控制台撤销／轮换
- [ ] 若用户选择实网联调，在真实 HTTPS／GitHub OAuth 测试环境中由用户通过四张卡片分别保存自己的 Key；项目方不代购供应商账号
- [ ] 暂无真实凭据时保留 `partial_fail_closed` 与未验证说明，不重复实现 BYOK，不重新加入已移除供应商
- [ ] 进入迭代 2 前确认一小批人工 `passed` Markdown、固定主仓 commit 和 locator 契约可用
- [ ] 冻结的 Bilibili 聚焦词与唯一匿名搜索入口保持不变；不建立具体视频资产，真实 Runtime 到迭代 3 接入
- [ ] 保存实网验证结果或缺失原因、测试结果、未确认项和下一期进入条件
```

GitHub OAuth、平台默认模型池和 BYOK 的本地／测试实现已在迭代 1 接入；真实凭据回调、供应商实网与生产 HTTPS 仍按证据单独标注。真实 Workflow Runtime 到迭代 3 完成。不得因为 HTTP 替身或本地页面可运行，就提前宣称实网上线。
