# SCUT 老学长

SCUT 老学长是面向华南理工大学计算机相关课程的学习对话助手。应用源码、API、语料校验工具、前端、契约和测试均位于本目录。PLAN-3 已完成，应用现在同时提供单课程问答、按本次运行生效的跨课程检索、回答结果操作、公共资料贡献、用户绑定的私人知识沉淀和独立维护者审核平台。

## 核心流程

```text
GitHub 登录或本地开发身份
→ 选择课程插件与 Workflow
→ 构造本次运行的课程检索范围
→ 课程内或跨课程 Hybrid Retrieval
→ 模型生成结构化回答
→ 引用、课程边界与输出安全校验
→ NDJSON 流式展示
→ 保存运行结果与历史
→ 复制、迁出、反馈、公共贡献或私人知识沉淀
```

## 功能说明

### PLAN-1：可追溯的课程学习基座

PLAN-1 建立了课程学习助手的基础能力和边界：

- 面向首批 10 门课程组织经过校验的课程资料与历年题，回答可以关联具体资料、页码、幻灯片或题号；
- 提供 `knowledge_qa`、`exam_review`、`problem_tutor`、`mistake_review` 和 `temporary_material_reading` 五类固定 Workflow，覆盖知识答疑、备考、题目讲解、错题复盘和临时材料精读；
- 所有问答绑定 GitHub 登录身份，并保存可追溯的会话、运行记录、真实执行 Trace、反馈和错题历史；
- 平台每日免费额度模型与用户自带 Key（BYOK）分为独立通道，模型、供应商和调用路由均由服务端受控；
- 模型输出必须经过课程范围、来源、引用和安全回答块校验，资料不足时明确标记证据边界，不将通用知识伪装为课程资料结论。

### PLAN-2：统一输入、混合检索与受限 Agent Runtime

PLAN-2 在一期课程边界与校验机制之上，增强检索质量和运行过程的可控性：

- 统一 Composer 会以确定性规则自动路由到五类 Workflow；低置信度时可回退知识答疑并允许用户纠正；
- 检索采用 BM25F、本地 CPU ONNX `bge-small-zh-v1.5` dense 检索、RRF 融合与确定性规则重排；dense 模型或向量资产缺失时自动退回 BM25F，不发起网络请求；
- 使用已审核的 P0 检索评测基线持续验证召回效果、精确匹配和课程边界，候选、引用与 `corpus_version` 可回查；
- EventStream Agent Loop 以事件、Reducer 和动作白名单执行受限单步决策，服务端负责工具执行与 Guard 校验；取消、超时、越权、预算耗尽和失败都会收敛到明确终态；
- `exam_review` 根据大纲、考试时间、目标和薄弱点生成确定性复习计划，支持先预览、再确认或修改，并不额外消耗模型调用。

### PLAN-3：课程协同检索与知识共建

PLAN-3 将一期、二期已建立的课程边界、检索与运行时能力扩展为可控的协同学习与知识沉淀闭环：

- 用户可在明确开启开关后，为单次运行选择多门课程；课程范围只在该次运行内生效，模型不能自行扩大检索范围；
- `knowledge_qa` 与 `problem_tutor` 支持跨课程 Hybrid Retrieval，并在回答中同时展示选择范围和实际产生引用的课程；
- 回答完成后可复制、迁出为新对话草稿、提交反馈、贡献公共资料或加入私人知识库，原会话和运行记录保持不变；
- 公共贡献以本轮输出为单位提交到审核队列，支持补充文本或原始附件，由维护者下载、审核、整理后决定是否纳入公共课程资料；
- 私人知识库材料绑定用户和课程，保留 7 天，仅在用户本人、本次选择课程和材料未过期等条件同时满足时参与检索；
- 独立维护者平台负责处理反馈和公共贡献，维护者权限与普通用户权限隔离，平台不自动创建 GitHub PR、提交仓库或激活公共语料。

### 课程插件与跨课程检索

课程插件负责声明课程是否可用以及是否有可检索语料；对话框中的课程选择负责决定本次运行使用哪些课程。两者职责分离：插件管理不会替代本次对话的课程选择。

个人中心的助手设置中有“允许跨课程检索”开关：

- 默认关闭。
- 设置跟随 GitHub 用户保存到服务端账户偏好。
- 关闭时，对话框课程列表为单选。
- 开启时，对话框课程列表支持多选。
- 多选结果只对本次运行生效，同一会话的下一次运行可以重新选择。
- 本次运行选择多少课程插件，就检索多少课程插件。
- 未启用、不可用或未被选择的课程不会参与检索。
- 模型不能自行扩大课程范围。
- 没有有效证据的课程不会被强行写入回答。

跨课程检索下方会提示：私人知识库材料较多时，跨课程检索可能明显变慢。回答结果会显示本次选择的课程和实际产生引用的课程，便于确认检索范围。

跨课程第一版开放 `knowledge_qa` 和 `problem_tutor`；其他 Workflow 保持各自既有课程边界和输入合同。

### Workflow

当前保留五类受控 Workflow：

- `knowledge_qa`：课程知识问答；
- `exam_review`：根据大纲、考试时间、目标和薄弱点生成确定性复习计划；
- `problem_tutor`：按用户指定的帮助程度讲解题目；
- `mistake_review`：分析原答案、参考答案和错误重点；
- `temporary_material_reading`：对用户提供的临时材料进行精读。

前端使用确定性路由和统一 Composer，后端使用严格的 `WorkflowRunRequest` 合同。模型只负责受控的回答生成，课程范围、工具、引用和回答块由服务端校验。

### 检索与回答

本地语料模式使用 BM25F 与本地 CPU ONNX `bge-small-zh-v1.5` 的 Hybrid Retrieval，并使用确定性规则重排。dense 模型文件或向量资产缺失时，检索自动退回 BM25F，不发起网络请求。

回答输出经过兼容解析、来源 Guard、引用 Guard 和安全回答块处理后，才通过 NDJSON 流发送到前端。流式事件包括 Trace、回答增量、Agent 进度、终态结果和错误事件。运行中的取消、断线、预算耗尽和上游错误都有明确终态，并保存可恢复的运行记录。

### 回答结果操作

回答完成后，结果区域提供以下操作：

- **复制本轮输出**：复制当前回答的可读正文和必要引用，不复制内部 Trace、模型原始响应、凭据或内部控制字段；
- **迁出当前分支到新对话**：创建新的会话并把当前回答填入可编辑的对话草稿，原会话和原运行保持不变，不自动触发模型调用；
- **我要反馈**：对本轮回答标记有帮助、没帮助、知识错误或没有回答问题，并可补充说明；
- **我要贡献**：将本轮输出提交到公共贡献队列；
- **加入私人知识库**：将当前内容绑定到用户和课程，在限定时间内供该用户后续对话检索。

### 公共资料贡献

“我要贡献”只提交本轮对话输出，不默认提交完整历史对话。用户提交时需要：

- 填写材料总结标题；
- 填写 GitHub 绑定邮箱；
- 确认课程、来源、公开分享权、敏感信息和公开可见性；
- 预览最终提交内容；
- 根据需要补充文本或上传原始文件。

支持的常见资料格式包括：

```text
.pdf
.png / .jpg / .jpeg / .webp
.doc / .docx
.ppt / .pptx
.xls / .xlsx
.csv
.md / .txt
```

文件按原始附件保存，不在维护平台中渲染。维护者通过下载按钮取得文件，在本地完成审核、整理、格式转换和仓库提交。平台不自动创建 GitHub PR、不自动 commit、不自动激活公共语料。

附件使用独立上传接口，采用随机文件 ID 保存，不进入静态资源目录；下载接口执行权限校验并以附件方式返回。压缩包、在线预览、OCR、自动 Office/PDF 解析和附件直接检索不属于当前贡献流程。

### 私人知识库

私人知识库材料绑定当前用户，保留 7 天，到期由服务端物理清理。私人材料不进入公共索引、公共课程包或其他用户的检索结果，也不提供手动查看、删除和用户导出入口。

材料按照课程插件名或课程 ID归属。检索时同时满足以下条件才会使用：

```text
user_id == 当前用户
course_id 属于本次运行选择的课程
对应课程插件已启用且可用
expires_at > 当前时间
visibility == private
```

跨课程关闭时，只检索当前单课程的私人材料；跨课程开启时，检索本次选择课程范围内的私人材料。跨课程开关不会自动扩展到全部课程。

私人知识库与公共贡献共用内容校验和记录抽象，但公共待审核内容与私人材料的权限、状态和检索范围严格分离。

### 维护者平台

维护者平台使用独立路由，与普通对话助手分离。只有固定维护者 allowlist 中的账号可以访问维护接口和页面；普通 GitHub 登录用户不自动拥有维护者权限。

维护平台提供：

- 反馈队列；
- 公共贡献队列；
- 贡献详情；
- 用户、课程、Workflow、标题、提交时间和状态查看；
- 文本内容和附件下载；
- 采纳、拒绝、要求补充和标记已处理。

维护者平台不承担在线文档渲染，也不执行仓库写操作。维护者下载后自行审核和整理，并根据用户填写的 GitHub 邮箱处理 `Co-authored-by` 信息。

## 目录

- `web/`：Vue 3 学生端、回答展示、课程选择、设置、贡献入口和严格流事件客户端；
- `api/`：FastAPI API、OAuth 与会话、Workflow Runtime、检索、引用 Guard、SQLite 和维护者接口；
- `worker/`：manifest、frontmatter、locator 校验以及 candidate 构建、验证和激活工具；
- `packages/`：V1 枚举、课程注册表、Workflow、流事件和评测契约；
- `infra/`：不含真实 Secret 的部署骨架；
- `tests/`：API、前端、契约、检索、运行时、贡献和维护边界测试。

`学科资料/` 不会被应用测试读取，也不会被 Docker build context 包含。公共语料必须经过课程 manifest、frontmatter、locator、candidate 和人工审核链路后才能进入 active corpus。

## 本地运行

要求：Python 3.12+、[uv](https://docs.astral.sh/uv/)、Node.js 20+ 与 npm。

```bash
cd apps/scut-senior
make sync
make test
make build-web
make dev-api
```

另开终端启动前端：

```bash
cd apps/scut-senior/web
npm run dev
```

默认 API 为 `http://127.0.0.1:8000`，Vite 开发服务器代理 `/api`。本地 SQLite、上传附件、日志和缓存写入 `apps/scut-senior/.local/`，不会提交到 Git。

## 常用命令

```bash
make test              # Python 与 Web 测试、类型检查
make build-web         # 前端类型检查并构建 dist
make validate-fixtures # 校验合成语料
make check-contracts   # 检查导出契约
make serve-online      # 启动前端与 API 的同进程服务
```

## 检索模式

默认配置使用 Mock 身份、Mock 模型、Fixture 检索和本地 SQLite，适合开发与自动化测试。使用本地语料时：

```bash
export SCUT_SENIOR_RETRIEVAL_MODE=local_corpus
export SCUT_SENIOR_CORPUS_STORE_PATH='.local/corpus-store'
make dev-api
```

本地语料模式要求 corpus store 具有有效的 active candidate、课程启用状态和版本绑定。缺少任一必要资产时，系统故障安全关闭，不回退到未审核资料或未选择课程。

## 真实身份与模型通道

真实 GitHub OAuth 使用 HTTPS 回调地址、服务端 SQLite 和安全 Cookie。平台模型和 BYOK 凭据由服务端固定目录管理；用户 Key 使用服务端 AES-256-GCM 主密钥加密，前端只接收脱敏状态。凭据、OAuth Secret、数据库、附件和日志不进入 Git、前端构建产物或 Docker 镜像。

本地测试仍推荐使用 Mock 配置。真实平台模型调用必须启用 GitHub OAuth 和正式 SQLite 身份存储，并通过环境变量提供服务端 Secret。模型供应商适配遵循 `ModelGateway` 与 `UserKeyModelGateway` 接口，新增 Terra 等供应商时只需接入固定目录和对应适配器，不改变课程、引用、权限和流式协议边界。


## 在线部署：本地运行 + HTTPS 隧道（当前启用路径）

当前启用路径是**本机运行 + HTTPS 隧道**：前端与 API 由同一进程提供，隧道把本机端口暴露成公网 HTTPS 域名，满足 GitHub OAuth 回调与 Secure Cookie 要求。**华为云 SWR→ECS 部署设计原样保留**，预算获批后作为后续可选目标切换，不需要改动应用代码。

> ⚠️ 会话 Cookie 为 `Secure`，**OAuth 联调必须通过隧道的 HTTPS 域名访问，不能走 `http://127.0.0.1`**。

### 1. 构建前端并启动服务

```bash
cd apps/scut-senior
make build-web
make serve-online   # uvicorn 0.0.0.0:8000，前端与 API 同一进程
```

### 2. 暴露公网 HTTPS（二选一，都免费）

**Tailscale Funnel（推荐，零域名成本、URL 稳定）：**

```bash
tailscale up
tailscale funnel 8000
# 得到稳定地址：https://<machine-name>.ts.net  （重启后不变）
```

**Cloudflare 命名隧道（需要你控制的域名）：**

```bash
cloudflared tunnel login
cloudflared tunnel create scut-senior
cloudflared tunnel route dns scut-senior <your-domain>
# config.yml: 将 https://<your-domain> 转发到 http://localhost:8000
cloudflared tunnel run scut-senior
```

### 3. 创建 GitHub OAuth App 并配置环境变量

GitHub 设置 → Developer settings → OAuth Apps → New OAuth App：

- **Homepage URL**：`https://<隧道域名>/`
- **Authorization callback URL**：`https://<隧道域名>/api/v1/auth/github/callback`

启动前导出（不要提交到 Git）：

```bash
export SCUT_SENIOR_APP_ENV=development
export SCUT_SENIOR_IDENTITY_MODE=github_oauth
export SCUT_SENIOR_STORAGE_MODE=sqlite
export SCUT_SENIOR_DATABASE_PATH='.local/online.db'
export SCUT_SENIOR_GITHUB_CLIENT_ID='<GITHUB_CLIENT_ID>'
export SCUT_SENIOR_GITHUB_CLIENT_SECRET='<GITHUB_CLIENT_SECRET>'
export SCUT_SENIOR_GITHUB_CALLBACK_URL='https://<隧道域名>/api/v1/auth/github/callback'
export SCUT_SENIOR_POST_LOGIN_REDIRECT_URL='https://<隧道域名>/'
export SCUT_SENIOR_MODEL_MODE=openrouter_platform
export SCUT_SENIOR_OPENROUTER_API_KEY='<服务端项目 Key>'
# 可选：智谱 bigmodel 免费模型（GLM-4.7-Flash / GLM-4-Flash-250414 / GLM-4.6V-Flash）
export SCUT_SENIOR_ZHIPU_API_KEY='<智谱免费 Key>'
# 可选：发布阶段二决策/动作/观察事件；默认关闭以兼容旧客户端
export SCUT_SENIOR_AGENT_EVENT_STREAM_ENABLED=true
```

BYOK 真实调用另需稳定的 32 字节 AES 主密钥（见上文“本地验证 BYOK”）。`SCUT_SENIOR_APP_ENV=production` 仍拒绝启动；迭代 4 验收与实网联调使用 `development`。

### 4. 验收清单

- [ ] `https://<隧道域名>/` 能打开 SPA；
- [ ] GitHub 登录回调完成（`/api/v1/auth/github/callback` 302 到首页）；
- [ ] 登录后 `/api/v1/models` 显示平台三模型或已保存 Key 的 BYOK；
- [ ] 一次真实模型 Workflow run 返回 `run_status=completed`；
- [ ] `/api/v1/feedback` 提交与列表可用。

## 单独检出应用目录

仓库含大量普通 Git 大文件。轻量开发可使用 partial clone 与 sparse checkout：

```bash
git clone --filter=blob:none --no-checkout git@github.com:AlexBybye/SCUT_CS.git SCUT_CS-app
cd SCUT_CS-app
git sparse-checkout init --cone
git sparse-checkout set apps/scut-senior .github README.md .gitignore .gitattributes
git checkout master
```
维护清理由进程内调度器执行，启动时补扫并按固定间隔清理到期会话、历史、反馈、私人材料、贡献记录和额度事件。清理步骤彼此隔离，单个存储步骤异常不会阻断同一轮其他步骤。