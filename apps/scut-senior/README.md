# SCUT 老学长

这里是 SCUT 老学长的唯一应用源码目录。当前只完成迭代 0 的契约与 Mock 工程基座，目的是验证：

```text
选择课程与 Workflow
→ 合成 passed Fixture
→ 确定性 Mock 回答
→ 保存回答、citation、external_resources 和真实节点 Trace
→ 重启后重新读取
```

当前页面、身份、模型、检索、Bilibili 目录和 SQLite 都是本地测试适配器。它们不是正式 GitHub OAuth、真实大模型、生产检索、正式视频目录或云端数据库；生产环境会拒绝以 Mock 配置启动。

## 目录

- `web/`：Vue 3 学生端 Mock 界面；
- `api/`：FastAPI 契约、端口、Mock 运行链路和本地 SQLite 适配器；
- `worker/`：manifest/frontmatter/locator 校验入口；
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

- 真实 GitHub OAuth、默认模型池和 BYOK：迭代 1；
- 真实 `passed` Markdown、candidate/active 和索引：迭代 2；
- 真实 Workflow Runtime 与流式 Trace：迭代 3；
- PostgreSQL、向量索引、对象存储、任务系统、GitHub App、SWR 认证、ECS 灰度/回滚：只保留可替换边界；
- 跨课程：契约已冻结，feature flag 默认关闭；
- Bilibili：仅有 `fixture_only` 测试目录，正式目录和 fallback 未确认；
- 正式在线 Chat：迭代 4 验收前不提供地址。

迭代 0 的基线、测试证据和未确认项见 [ITERATION_0_STATUS.md](ITERATION_0_STATUS.md)。

