# 迭代 0 退出记录

状态：代码与本地验收完成；Docker 实构建和远端 GitHub Actions 待验证，不进入迭代 1

进入日期：2026-08-14（Asia/Shanghai）

本地验收日期：2026-08-14（Asia/Shanghai）

> 2026-08-15 后续产品边界更新：迭代 0 当时创建的 Bilibili 合成目录／Fixture 仅作为历史测试证据保留，不再作为维护契约或后续迭代输入；当前产品只采用模型聚焦词与后端固定匿名搜索入口。

## 进入检查

- 进入分支：`master`；实施分支：`codex/scut-senior-iteration-0`；
- 固定基线 commit：`3daeafd388317fa9b7f11df1cfb350f091b87220`；
- 进入时工作区：仅已有的 `?? .DS_Store`；
- clone：非 shallow、非 sparse；76 个 LFS 对象已在本机物化；
- 现有 `apps/`、`knowledge/`、App CI、corpus CI、Docker、迁移和应用测试：均不存在；
- `docs/PLAN-1.md` v1.5 与 `docs/CODE_ITERATION_SOP.md` v1.1 是本地设计输入，但整个 `docs/` 被 `.gitignore` 忽略，未绑定到上述 commit；本轮未擅自改变其公开纳管状态；
- 本期没有读取、复制或改写真实课程资料，也没有对真实资料作 `passed` 裁决。

本期同时触及应用、Worker、manifest/locator/Schema 契约和语料构建兼容性，因此 App CI 与 corpus CI 都必须运行。

## 本期契约与 Fixture

- 契约版本：`v1`；
- Workflow 版本：`workflow-contract-v1`；
- 合成语料版本：`fixture-corpus-v1`；
- 课程包：未实现；
- 模型：`mock/deterministic-fixture-v1`，不调用真实供应商；
- 身份：固定 Mock 用户；
- 持久化：本地 `sqlite_mock` 适配器，只是关系存储端口的开发实现，不是云端选型；
- Fixture：仅位于 `tests/fixtures/` 的合成 Markdown、manifest、历年题、当时的 Bilibili 合成目录和评测契约样例；
- `cases.json` 与 `runner.json` 只冻结 Schema 和七类样例。迭代 0 没有实现评测执行器，Mock retrieval 也不按 query 评估相关性，因此不能称七类评测已执行或通过。

## 已实现能力

- 单一主仓应用目录 `apps/scut-senior/`，包含 `web/`、`api/`、`worker/`、`packages/`、`infra/`、`tests/` 和本地迁移；
- 11 门首批课程注册表，包含显示名、别名、仓库路径和课程开关。别名只做 Unicode NFKC、大小写折叠、空白移除后的完整等值匹配，不做子串匹配；
- 五个 Workflow 分型 payload，以及回答方式、风格、知识范围、课程范围、模型来源、运行/回答/证据/Trace 状态和帮助层级枚举；
- 可执行 Pydantic 请求/结果契约及生成的 `workflow-request.schema.json`、`workflow-result.schema.json`；Python、Worker 和 Vue 会与共享 `enums.json` 交叉校验；
- `citations[]`、`external_resources[]` 和 Trace 分离。Citation 的课程名来自课程注册表，资料名来自 manifest，页面同时组合展示页码/幻灯片、题号和章节；`locator_type=none` 时退化为资料名，不补造定位；
- Trace 来自实际 Mock 节点，`result` 使用拒绝额外字段的学生可见白名单；Mock 身份事件不保存 `user_id`，Key、token、prompt、堆栈和内部路径字段会被契约拒绝；
- manifest/frontmatter/page/slide/question/heading 校验器：只让结构有效的 `passed` 行进入检索，允许不确定的 `document_role/year` 留空，拒绝额外 CSV 列、路径逃逸、无效 locator、倒序/重复定位和标题跳级；
- 迭代 0 当时实现了 Bilibili 合成目录的 Schema、审核状态和确定性课程／关键词匹配；该历史测试资产已被 2026-08-15 的 search-only 决策废止，不进入后续产品计划；
- Mock 身份、Mock 模型、合成检索与 SQLite 的可持久化闭环：选课与 Workflow → 运行 → 保存回答/来源/外部资源/Trace → 重启或 GET 后恢复；
- 模型、关系存储、向量索引、对象存储、任务系统和 GitHub App 的可替换端口；未确认能力保持 disabled；
- Vue 3 单页 Mock 界面，五个 Workflow 共用一套 Chat 控制层，明确标注 Mock/合成 Fixture/无正式在线地址；
- App CI、corpus CI、受保护部署门和 Docker 骨架。检出使用 `blob:none` + sparse checkout + `GIT_LFS_SKIP_SMUDGE=1`，Docker context 固定为 `apps/scut-senior/`；
- 部署工作流提供默认 `validation_only=true` 的可执行人工验证模式，只做受限检出和镜像构建，不绑定生产 Environment、不读取 Secret、不接触 SWR/ECS；
- 真实部署任务只允许主仓 `master` 或显式人工触发并绑定 `scut-senior-production`。未确认 SWR/ECS 方案前，即使误开变量也会在本地镜像构建后明确失败，不读取或使用部署 Secret。

## 未实现或关闭能力

- 真实 GitHub OAuth、真实模型、平台默认模型池、BYOK、生产检索、candidate/active、课程包和真实历史期限清理；
- Bilibili search-only 真实 Workflow Runtime；
- 跨课程执行；
- PostgreSQL、向量索引、对象存储、离线任务和 GitHub App；
- SWR 认证、镜像推送、ECS 更新、灰度、健康检查与回滚；
- 评测 runner 和七类 case 的实际执行；
- 正式在线地址。

## 测试结果

本地通过：

```text
api/.venv/bin/pytest tests/python -q
83 passed, 1 warning in 0.78s

UV_CACHE_DIR=/private/tmp/scut-senior-uv-cache make validate-fixtures
ok: true; errors: []; 仅 synthetic passed 行进入 searchable_sources

UV_CACHE_DIR=/private/tmp/scut-senior-uv-cache make check-contracts
通过；两份生成 Schema 无漂移

npm run test
2 files / 8 tests passed

npm run typecheck
通过

npm run build
通过；dist JS 88.30 kB（gzip 33.82 kB），CSS 13.75 kB（gzip 3.51 kB）

actionlint 1.7.7 .github/workflows/*.yml
三份工作流通过

git diff --check
通过
```

浏览器端到端复验：

- `GET /api/v1/courses` 200、创建会话 201、两次 Workflow run 201、重新读取会话 200；
- 恢复后的回答、Citation 和 Trace 与保存结果一致；
- 来源卡显示课程名、manifest 标题、页码、题号和章节组合；
- `course_only` 下 Bilibili 开关为 `checked=false, disabled=true`，结果返回 0 条外部资源；
- 8 个 Trace 事件包含模型调用前的 `source_authorization_guard`；可见 payload 未出现 `user_id`、`token`、`prompt`、`stack` 或 `internal_path`；
- 390×844 视口无横向溢出；浏览器控制台 warning/error 为 0。

仓库与部署边界：

- 独立临时 partial+sparse clone 实测工作树约 904 KB，不包含 `学科资料/`；
- 本地没有对应未提交提交的远端 GitHub Actions 运行，不能称 App CI/corpus CI 已在 GitHub 通过；
- Docker 命令已尝试，但本机 daemon 未启动，原始结果为 `Cannot connect to the Docker daemon`。因此镜像实构建仍待可用 daemon 或远端 App CI 验证。

唯一测试警告来自第三方 Starlette/httpx 兼容层弃用提示，不是应用断言失败。

## 数据迁移

仅包含本地 Mock SQLite 的 `0001_iteration_zero.sql`；无真实数据库迁移。迁移已由垂直链路测试在临时数据库执行。

## 尚待确认项

1. 平台默认模型池首批供应商与模型；
2. BYOK 首批供应商与模型；
3. Trace 排序分数默认展开程度；
4. 华为云内关系存储、向量索引、对象存储、离线任务、GitHub App，以及 SWR→ECS 认证、灰度和回滚方式；
5. 账号注销、历史提前删除和数据导出；
6. 跨课程正式开放门槛、最大课程数和提示文案；
7. GitHub `scut-senior-production` Environment、required reviewers 和 `DEPLOYMENT_ENABLED` 的实际仓库配置。

## 已知降级

- Mock retrieval 只从合成 `passed` Fixture 取确定性结果并故意忽略 query，不衡量真实检索质量；
- Mock model 只拼装确定性回答，不衡量模型能力；
- 本地规划文档未被 Git 跟踪，基线只能绑定其版本号，不能绑定文件内容；
- 当前课程全部 `is_open=false`；只有线性代数设置 `fixture_available=true` 以闭合测试链路；
- 部署工作流的 validation-only 路径可执行；真实发布路径仍是故障安全骨架，不会登录 SWR、推送镜像或修改 ECS；
- Docker 实构建和远端 Actions 尚无成功证据。

## 下一期可依赖的稳定契约

- `packages/contracts/v1/courses.json` 与 `enums.json`；
- 五种 `workflow_payload`、`WorkflowRunRequest`、`WorkflowResult` 及对应生成 Schema；
- Citation、ExternalResource、Trace 安全白名单和 `course_only` 强制规则；
- manifest/frontmatter/locator 和 evaluation case/runner Schema；
- 本地 SQLite 迁移与 Mock 垂直链路；
- App CI/corpus CI 的路径边界、受保护部署门和受限 Docker context。

在 Docker/远端 CI 证据补齐、迭代 1 决策门完成前，不把后续 OAuth、真实模型、BYOK、生产检索或云端部署视为可用。
