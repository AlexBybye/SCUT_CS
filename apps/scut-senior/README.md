# SCUT 老学长

这里是 SCUT 老学长的唯一应用源码目录。迭代 0 的契约与 Mock 工程基座、迭代 1 的本地／测试身份与模型通道、迭代 2 的 candidate／本地检索适配器均已形成代码基座。迭代 3 已在本地／测试环境实现五类 Workflow 共用 Runtime、严格 NDJSON 事件流、同一 run 的运行中／终态持久化、取消与中断、引用和 humanizer Guard、四类回答块以及 Bilibili search-only 降级链路。默认运行仍使用合成 Fixture；在受信 `master` 上生成并激活真实 corpus 之前，迭代 3 只能称为“本地实现与验证完成”，不能称为正式退出。真实 GitHub 凭据回调、用户真实 Key 的供应商实网响应和生产 HTTPS／部署也仍未形成证据。

```text
选择课程与 Workflow
→ 创建并保存 running run
→ 权威 Workflow 输入聚焦与课程内检索
→ 模型结构化回答
→ 引用／回答块／humanizer 安全校验
→ 可选 Bilibili 匿名搜索入口
→ 同一 run 的 Trace、answer_delta 与终态事件
→ 保存并从历史恢复
```

默认配置仍使用 Mock 身份、Mock 模型、Fixture 检索和本地 SQLite。显式 `github_oauth` 模式已经在本地／测试中闭合 OAuth `state`、GitHub 数字 ID 映射、7 天服务端会话、安全 Cookie、登出／到期、受保护接口、资源所有权以及 SQLite 重启／备份恢复；测试使用可注入回调和替身，不等于已用真实 GitHub 凭据完成线上联调。模型会在同一次结构化回答中给出 0～3 个聚焦词；关键词清洗后非空时，后端只固定生成 1 条 Bilibili 匿名搜索链接，不返回视频直链，不访问 Bilibili API，也不抓取搜索结果。项目不建设、审核或维护任何具体 Bilibili 视频资产。生产环境在真实 HTTPS、凭据和部署边界未验收前继续拒绝启动。

平台每日免费额度目录固定登记三项模型，页面显示公司名并由用户显式选择：

- Google · Gemma 4 26B A4B；
- Dots Studio · Dots3 Note Preview；
- NVIDIA · Nemotron 3 Super 120B A12B。

该通道每日刷新但不是无限额度。额度耗尽、分钟限流或上游繁忙会分别报错，不会自动切换模型、用户 Key 或付费端点。

BYOK 首批每家只保留一个固定目录模型：

- OpenRouter：`deepseek/deepseek-v4-flash-0731`（当日 OpenRouter 周榜第 1）；
- DeepSeek：`deepseek-v4-flash`（官方稳定别名）；
- 硅基流动（SiliconFlow）：`Pro/zai-org/GLM-4.7`（2026-08-16 官方 Chat Completions 默认示例）；
- 智谱（Zhipu）：`glm-5.2`（2026-08-16 当前可调用旗舰与 OpenAI 兼容示例；GLM-5.3 当日仍未开放 API）。

四家卡片始终显示，地址和模型均由服务端固定，不需要也不允许用户选择地区或地址、填写 `base_url` 或修改 `model_id`。服务端满足 GitHub OAuth、SQLite 和 AES-256-GCM 主密钥条件后将四家标记为启用；只有当前登录会话已保存对应 Key 的模型才进入可选列表，保存 Key 后也不会自动切换模型。Key 密文绑定 `user_id + auth_session_id + provider_id`，不晚于 7 天登录会话到期，并在删除、登出、到期或备份恢复失效会话时清理。自动化测试通过注入 HTTP 替身验证固定路由和安全错误边界，不代表已持有用户供应商账号或形成真实 Key 的实网证据。

## 目录

- `web/`：Vue 3 学生端及严格流事件客户端；
- `api/`：FastAPI 契约、本地／测试 OAuth 与会话链路、Workflow Runtime、SQLite 和本地 corpus 检索适配器；
- `worker/`：manifest/frontmatter/locator 校验及 candidate 构建、验证、激活门与回退工具；
- `packages/`：V1 枚举、课程注册表、Workflow 和评测契约；
- `infra/`：不含真实 Secret 的 SWR→ECS 部署骨架；
- `tests/`：纯合成 Fixture、单元测试和端到端契约测试。

`学科资料/` 不会被应用测试读取，也不会被 Docker build context 包含。测试中的 `passed` 仅描述合成 Fixture，不代表任何真实课程资料已经通过人工审核。

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

默认 API 为 `http://127.0.0.1:8000`，Vite 开发服务器会代理 `/api`。本地 SQLite 写入 `apps/scut-senior/.local/`，不会提交到 Git。

### 检索模式边界

默认 `SCUT_SENIOR_RETRIEVAL_MODE=fixture`，继续读取合成测试语料。`local_corpus` 不能直接读取当前迭代分支生成的 candidate；只有 candidate 的 `source_commit` 已进入受信 `master`、且通过单独激活门后，才可将 `SCUT_SENIOR_CORPUS_STORE_PATH` 配置为该 corpus store 的绝对路径。缺少有效 `active.json`、课程未启用或版本绑定不完整时，本地语料检索会故障安全关闭，不回退到跨课程或未审核资料。

### 本地验证 OpenRouter 平台通道

先在 OpenRouter 控制台创建一枚新的服务端 Key，并只通过本机环境变量提供；不要把 Key 写入 `.env.example`、Git、前端或聊天记录。真实平台通道会消耗共享额度，因此开发环境也必须同时启用 GitHub OAuth 与正式 SQLite 身份存储，不能搭配匿名 Mock 身份：

```bash
export SCUT_SENIOR_APP_ENV=development
export SCUT_SENIOR_IDENTITY_MODE=github_oauth
export SCUT_SENIOR_STORAGE_MODE=sqlite
export SCUT_SENIOR_DATABASE_PATH='.local/iteration-one.db'
export SCUT_SENIOR_GITHUB_CLIENT_ID='<GITHUB_CLIENT_ID>'
export SCUT_SENIOR_GITHUB_CLIENT_SECRET='<GITHUB_CLIENT_SECRET>'
export SCUT_SENIOR_GITHUB_CALLBACK_URL='https://<YOUR_HTTPS_HOST>/api/v1/auth/github/callback'
export SCUT_SENIOR_POST_LOGIN_REDIRECT_URL='https://<YOUR_HTTPS_HOST>/'
export SCUT_SENIOR_MODEL_MODE=openrouter_platform
export SCUT_SENIOR_OPENROUTER_API_KEY='<ROTATED_SERVER_SIDE_KEY>'
make dev-api
```

默认 `mock` 模式不读取该变量。`openrouter_platform` 暂时只供受认证的本地开发验证，检索仍是合成 Fixture；模型在公开目录中通过“仍存在、文本输入输出价格为零、支持结构化输出”的健康检查并记录 `last_checked_at` 后才可选择。`SCUT_SENIOR_APP_ENV=production` 仍会拒绝启动。

### 本地验证 BYOK

项目方不需要持有四家供应商账号或余额。服务端只需在真实 GitHub 登录、SQLite 和 HTTPS 边界上额外配置一枚稳定的 32 字节 AES 主密钥；普通用户随后只在页面对应卡片中提交自己的供应商 API Key：

```bash
openssl rand -base64 32
export SCUT_SENIOR_BYOK_MASTER_KEY='<PASTE_THE_BASE64_VALUE>'
export SCUT_SENIOR_BYOK_KEY_VERSION=1
```

主密钥不能使用供应商 API Key 代替，也不能提交到 Git、写入浏览器或随意更换；正式部署时应进入受保护的运行 Secret。配置满足后四家卡片会显示为“服务端已启用”，但模型仍要等当前登录会话保存对应用户 Key 后才可选择。用户 Key 只通过 `PUT /api/v1/model-credentials/{provider_id}` 提交，返回值只有脱敏状态与到期时间；真实调用只会发往代码内固定的四个地址。没有用户 Key 时不能验证该用户账户的余额、权限或供应商实网响应，但这不影响固定路由、加密、清理和泄漏边界的自动化验收。

## 在线部署：本地运行 + HTTPS 隧道（当前启用路径）

当前启用路径是**本机运行 + HTTPS 隧道**：前端与 API 由同一进程提供，隧道把本机端口暴露成公网 HTTPS 域名，满足 GitHub OAuth 回调与 Secure Cookie 要求。**华为云 SWR→ECS 部署设计原样保留**（见下文“明确关闭或待确认”），预算获批后作为后续可选目标切换，不需要改动应用代码。

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
```

BYOK 真实调用另需稳定的 32 字节 AES 主密钥（见上文“本地验证 BYOK”）。`SCUT_SENIOR_APP_ENV=production` 仍拒绝启动；迭代 4 验收与实网联调使用 `development`。

### 4. 验收清单

- [ ] `https://<隧道域名>/` 能打开 SPA；
- [ ] GitHub 登录回调完成（`/api/v1/auth/github/callback` 302 到首页）；
- [ ] 登录后 `/api/v1/models` 显示平台三模型或已保存 Key 的 BYOK；
- [ ] 一次真实模型 Workflow run 返回 `run_status=completed`；
- [ ] `/api/v1/feedback` 提交与列表可用。

## 单独检出应用目录

仓库含大量普通 Git 大文件和 LFS 对象，仅设置 `GIT_LFS_SKIP_SMUDGE=1` 不足以避免下载。轻量开发应同时使用 partial clone 与 sparse checkout：

```bash
git clone --filter=blob:none --no-checkout git@github.com:AlexBybye/SCUT_CS.git SCUT_CS-app
cd SCUT_CS-app
git sparse-checkout init --cone
git sparse-checkout set apps/scut-senior .github README.md .gitignore .gitattributes
GIT_LFS_SKIP_SMUDGE=1 git checkout master
```

## 明确关闭或待确认

- 迭代 4 切片（进行中）：多轮上下文已接入——服务端从会话历史派生最多 6 轮已完成尝试作为模型上下文，历史不改变当前请求的课程、Workflow 或知识范围；回答反馈已闭环——`POST/GET /api/v1/feedback` 绑定运行归属并随 30 天历史清理，反馈只进入列表、不自动修改知识库；评测执行器 `scut-senior-eval` 已可执行 7 类 fixture case 并输出逐课程报告，当前 fixture+mock 仅覆盖 answered/repository/page 契约，其余期望须待真实 corpus 与真实模型（不伪造通过）；
- OpenRouter 三模型平台目录、显式选择、目录健康检查和本地开发调用适配器：迭代 1 已实现；健康检查不发起推理，不能当作真实回答可用性证据；
- BYOK 固定目录、会话级 AES-256-GCM 保存／替换／删除／清理、四家固定调用和安全错误映射：迭代 1 已在本地／测试实现；未使用真实用户 Key 做四家实网联调；
- GitHub OAuth：本地／测试适配器、7 天会话、所有权和 SQLite 恢复已实现；真实 GitHub 凭据回调、生产 HTTPS 与部署尚未联调，生产继续 fail-closed；
- 平台限流状态目前是单进程内存态；多 worker 共享限流、周期清理任务和生产启用仍未完成；
- 首批课程固定为 10 门；本轮不改 manifest 的 reviewer 或 `passed/pending`，也不把用户的 Markdown 公式替换等同于 corpus 激活。当前没有正式 `active.json`，默认检索仍是 Fixture，远端 CI 与受信 `master` 上的真实 active／回退证据仍缺失；
- Workflow Runtime 与严格 NDJSON Trace：迭代 3 已完成本地／测试实现；供应商回答会先完整通过结构化解析与 Guard，再按安全回答块发送 `answer_delta`，不是上游 token 原样透传；页面断开会停止后续节点并保存 `interrupted`，但同步 urllib 调用在返回或超时前不能保证终止上游推理或计费；
- 华为云部署：**设计原样保留，作为后续可选目标**；预算获批前保持 validation-only／fail-closed，不创建资源；未来首发基线为华南-广州优先的 1C2G、40GB、1～2Mbps，不在 ECS 部署大模型。当前启用路径为“本机运行 + HTTPS 隧道”（见上文“在线部署”节）；
- PostgreSQL、Qdrant、对象存储、任务系统、GitHub App、SWR 认证、ECS 灰度/回滚：首发不购买或只保留可替换边界；
- 跨课程：契约已冻结，feature flag 默认关闭；
- Bilibili：只保留 0～3 个聚焦词和关键词非空时由后端生成的唯一匿名搜索链接；不建设或维护具体视频资产，不返回或抓取具体视频；
- 正式在线 Chat：迭代 4 验收前不提供对外地址；联调地址由本机 + HTTPS 隧道提供。

迭代 0 的完整基线见 [ITERATION_0_STATUS.md](ITERATION_0_STATUS.md)；平台模型切片和仍未完成的迭代 1 边界见 [ITERATION_1_STATUS.md](ITERATION_1_STATUS.md)；迭代 2 的开发门与激活限制见 [ITERATION_2_STATUS.md](ITERATION_2_STATUS.md)；迭代 3 的实现、验证和正式退出阻塞见 [ITERATION_3_STATUS.md](ITERATION_3_STATUS.md)。
