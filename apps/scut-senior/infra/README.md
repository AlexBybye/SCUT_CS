# SCUT 老学长部署骨架

当前部署状态是**显式关闭**。应用镜像未来进入华为云 SWR，再由 ECS 部署；真实认证、灰度与回滚方式尚未确认，本目录不会用占位命令冒充可用部署。部署工作流提供默认的 `validation_only=true` 人工模式，只验证受限检出和镜像构建，成功后停止，不接触 SWR 或 ECS。

预算获批前不创建或修改任何华为云资源，`DEPLOYMENT_ENABLED` 必须保持未设置或 `false`。未来首发基线已经缩减为华南-广州优先的 1 vCPU／2GB、40GB 系统盘、1～2Mbps；ECS 只承载 Web、API、生产 SQLite 和轻量检索，不部署大模型，也不承担 OCR、embedding、全量索引或课程包构建。包年购买前应先用按需实例验证 OpenRouter、DeepSeek、硅基流动和智谱四家固定 endpoint 的出站连通性。

当前镜像只用于本地和 CI 的开发验证，仍包含 Mock 身份、Fixture 检索与 SQLite Mock 存储，不能作为线上服务运行。即使配置了 OpenRouter 平台模型，当前 API 也会在 `SCUT_SENIOR_APP_ENV=production` 下拒绝启动。未来 ECS 的 OpenRouter 项目 Key、BYOK 加密主密钥和 OAuth Secret 只能进入受保护的运行 Secret，不能写入镜像、仓库、构建日志或前端。

## 已冻结的安全边界

- 部署工作流只接受 `master` push 或人工 `workflow_dispatch`，不监听 pull request；
- 工作流额外校验仓库必须是 `AlexBybye/SCUT_CS`，fork 中不会进入部署任务；
- 部署任务绑定 `scut-senior-production` Environment；启用前必须在 GitHub 仓库设置中为它配置 required reviewers 等保护规则；
- 仓库配置变量 `vars.DEPLOYMENT_ENABLED` 不是字符串 `true` 时，部署任务保持 skipped；
- checkout 在取出工作树前同时启用 `filter: blob:none` 与 sparse checkout，并以 `GIT_LFS_SKIP_SMUDGE=1` 保持 LFS 下载关闭；
- Docker build context 固定为 `apps/scut-senior/`，不读取仓库根的 `学科资料/`；`knowledge/` 虽已移入 context 目录内，但由 `.dockerignore` 排除，镜像不包含真实语料；
- 普通 App CI 和 corpus CI 只使用 `contents: read`，不读取部署 Secret。

## 当前故障安全行为

人工触发默认只运行 validation-only job，可成功验证当前骨架；它不绑定生产 Environment，也不读取 Secret。即使误把 `DEPLOYMENT_ENABLED` 设为 `true`，真实部署门也只会构建本地镜像，随后明确失败，不会登录 SWR、推送镜像或修改 ECS。只有以下事项经过单独确认和审查后，才能替换该失败步骤：

1. GitHub Actions 到 SWR 的认证方式与最小权限；
2. SWR registry、namespace、repository 和镜像标签规则；
3. ECS 目标、部署身份和网络边界；
4. 灰度、健康检查、失败回滚和上一有效镜像保留方式；
5. 受保护 Environment 的审批人和 Secret／Variable 清单。

在这些事项冻结前，`DEPLOYMENT_ENABLED` 必须保持未设置或 `false`。

> `actions/checkout@v4` 的 `filter` 会覆盖其 `sparse-checkout` 输入。三个工作流因此使用显式的 partial clone → sparse checkout → checkout 顺序，避免先懒加载整个资料树再收窄工作区。

## 本地镜像验证

从仓库根目录执行：

```bash
docker build \
  --file apps/scut-senior/Dockerfile \
  --tag scut-senior:local \
  apps/scut-senior
```
