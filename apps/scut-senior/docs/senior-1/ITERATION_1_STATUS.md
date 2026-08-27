# 迭代 1 状态：身份、平台模型、BYOK 与历史

日期：2026-08-16

分支：`codex/scut-senior-iteration-1`

进入基座：`987d1dab2c44d232bab3bf45c708855a766fca94`
状态：`partial_fail_closed`；本地／测试主链路已闭合，尚未宣称生产或供应商实网可用

## 本轮已完成

- 本地／测试 GitHub OAuth：一次性 `state`、GitHub 不可变数字 ID、7 天服务端会话、`HttpOnly + Secure + SameSite=Lax` Cookie、登出／到期和跨用户所有权检查；不长期保存 GitHub access token。
- SQLite 历史：跨进程重启、重新登录、在线备份／恢复、30 天启动／访问触发清理、重命名、删除、重新生成并保留旧 attempt；备份恢复后旧登录会话与 BYOK 密文失效。
- SQLite 安全升级：新建和既有数据库、WAL／SHM、备份与恢复文件收紧为 `0600`；既有旧迁移通过后续表重建升级，不删除本地数据库规避迁移；符号链接不会被跟随执行 `chmod`。
- OpenRouter 平台每日免费额度通道：只登记 Google · Gemma 4 26B A4B、Dots Studio · Dots3 Note Preview、NVIDIA · Nemotron 3 Super 120B A12B，用户显式选择；20 RPM、本地每日额度锁存和固定额度耗尽文案均不自动切换到其他模型、用户 Key 或付费端点。
- 平台目录健康检查：固定读取 Key 状态和公开模型目录，检查模型存在、全部价格字段为零及 Structured Outputs 参数并记录 `last_checked_at`；测试环境未注入 transport 时默认禁止外网。
- Bilibili search-only：同一次回答只提供 0～3 个聚焦词，后端做 NFKC、控制字符、空白、去重、数量与长度校验；清洗后非空时必须且只生成一条 `https://search.bilibili.com/all?keyword=...`，不抓搜索结果、不返回视频直链、不建设人工视频单或 Fixture。

## BYOK v4 固定目录

前端始终展示四家卡片，每家只有一个固定模型：

| 供应商 | 固定模型 | 服务端固定请求地址 |
|---|---|---|
| OpenRouter | `deepseek/deepseek-v4-flash-0731` | `https://openrouter.ai/api/v1/chat/completions` |
| DeepSeek | `deepseek-v4-flash` | `https://api.deepseek.com/chat/completions` |
| 硅基流动 SiliconFlow | `Pro/zai-org/GLM-4.7` | `https://api.siliconflow.cn/v1/chat/completions` |
| 智谱 Zhipu | `glm-5.2` | `https://open.bigmodel.cn/api/paas/v4/chat/completions` |

- 2026-08-16 01:05 CST 核验：硅基流动官方 Chat Completions 默认示例使用 `Pro/zai-org/GLM-4.7`；其公开页面没有调用量排名，因此不声称“已证明调用量最高”。智谱当前可调用旗舰与 OpenAI 兼容示例使用 `glm-5.2`；更新一代模型的官方页面当时明确 API 尚未上线，因此未进入目录。官方链接见 `docs/PLAN-1.md` v1.10 第 3.1 节。
- 四家均为固定 endpoint，不提供地区、地址或模型输入。请求／响应、数据库、迁移、Schema 和前端中均不存在可选地址配置字段；未知供应商、任意 `base_url`、任意 `model_id` 和额外请求字段均被拒绝。
- 运维侧只配置稳定的 32 字节 AES 主密钥和版本；用户侧只通过 `PUT /api/v1/model-credentials/{provider_id}` 提交自己的 `api_key`。Key 禁止首尾空白及 C0／DEL 控制字符。
- Key 使用 AES-256-GCM 加密，AAD 绑定 `user_id + auth_session_id + provider_id`；密文、nonce、算法和版本只进入凭据专表，最长随当前登录会话保留 7 天。查询只返回固定掩码与到期时间；删除、登出、撤销、到期和备份恢复失效会话都会物理清理。
- 四家卡片始终可见；只有后端 `enabled=true`、当前登录会话已保存 Key 且凭据模型与 v4 固定目录一致时，模型才进入可选列表。保存 Key 后仍不自动选择模型。
- 真实调用只会发送用户明确选择的单一固定模型。OpenRouter 使用 strict JSON Schema；其余三家使用官方兼容的 JSON Object 模式并在后端校验响应。401／403、402、429、超时、上游异常与无效响应映射为不含上游 body、Key 或内部地址的安全错误。
- 模型调用（平台与 BYOK）、OpenRouter 目录健康检查、GitHub OAuth 三类 urllib transport 均拒绝任何 3xx，不会把 `Authorization`、项目 Key、用户 Key、GitHub client secret 或 access token 跟随到第二地址。
- 同步检索或模型调用失败会保存安全的 `run_status=failed`、`answer_status=error` attempt 与白名单 Trace；不会保存 Key、上游 body、堆栈或内部提示词。会话在上游调用期间被撤销时，成功和失败结果都不会迟到落库。

## 验证证据

- 后端安全专项：`115 passed`；覆盖四家固定目录／地址、凭据 CRUD、AAD 篡改、会话隔离、撤销／到期／恢复清理、并发 upsert、既有迁移升级、旧文件权限升级、控制字符拒绝、三类 transport 禁止重定向及测试环境外网 fail-closed。
- Python 全量：`232 passed, 1 warning`；唯一 warning 是 FastAPI TestClient 对当前 httpx 兼容层的第三方弃用提示。
- Vue/Vitest：`7 files, 29 tests passed`。
- Vue typecheck：通过。
- Vue production build：通过，Vite 产物为 20 modules；主 JS `113.92 kB`（gzip `41.59 kB`），主 CSS `22.70 kB`（gzip `4.86 kB`）。
- `uv lock --check`、Python `compileall`、生成式契约漂移检查、合成 corpus Fixture、App／corpus CI 边界测试和 `git diff --check`：通过。
- 源码、契约与文档（排除本地测试缓存）中的旧供应商、废弃 BYOK 地址配置标识和真实 OpenRouter Key 特征扫描：0 命中。
- Browser 本地稳定树：恰好显示 OpenRouter、DeepSeek、硅基流动、智谱四张卡；Mock／未登录状态下四个 Key 保存按钮均禁用，模型下拉不混入未配置 BYOK，历史恢复与唯一 Bilibili 匿名搜索入口可见。`390×844` 下四卡单列、控件均未越界且页面无水平溢出；控制台 0 warning／error，验收后已恢复默认 viewport。

## 尚未完成，不能宣称上线

- 没有使用任何真实用户供应商 Key 发起实网推理。项目方不需要购买四家账号或额度；自动化测试通过注入 HTTP 替身验证完整请求路由，用户账户的余额、权限、模型可用性和真实上游响应只能在用户主动保存自己的 Key 后验证。
- GitHub OAuth 使用注入替身闭合，没有真实 GitHub Client ID／Secret 与公网 HTTPS 回调证据。
- OpenRouter 健康检查是“Key 状态 + 模型目录”检查，不发起真实推理；运行时 5xx／429 不会反向改写目录状态，不能把健康检查称为回答可用性证明。
- 20 RPM 与每日额度锁存是单进程内存状态，多 worker 不共享且重启会丢失；生产扩 worker 前需要共享 limiter。
- 会话、凭据和历史已经能在启动及相关访问时物理清理，但还没有独立周期调度器；严格的到点清理仍待生产任务边界确认。
- 当前 Workflow 仍是同步 Fixture Runtime。真实流式取消、页面断开和 `interrupted` 落库按 PLAN 的依赖关系在迭代 3 验收，不以合成状态冒充完成。
- 当前课程检索仍是合成 Fixture；真实 `passed` Markdown、candidate／active 与课程索引属于迭代 2。
- 生产模式继续拒绝启动；没有创建或修改华为云资源，没有登录 SWR 或推送镜像。华为云继续按预算延期，未来首发仍为华南-广州优先的 1C2G、40GB、1～2Mbps且不部署大模型。
- Docker daemon 未在本轮启用，镜像实构建未验证。
- 聊天中曾公开的 OpenRouter Key 已视为泄露；仓库零残留不能代替在 OpenRouter 控制台撤销／轮换。当前没有外部撤销完成证据。

## 下一步

1. 用户先在 OpenRouter 控制台撤销／轮换已公开的旧 Key，后续只在页面密码框提交新 Key。
2. 预算继续延期期间不做华为云部署；如需实网联调，先提供真实 GitHub OAuth／HTTPS 测试环境，再由用户分别保存自己的供应商 Key。
3. 迭代 2 接入真实审核后 Markdown 与 candidate／active；迭代 3 再完成流式 Runtime、真实 `interrupted` 和周期运行边界。
