# 迭代 7 退出记录（SOP §12：临时材料精读治理与贡献待处理队列）

状态：**本地／测试实现与验证完成**。文本／Markdown 精读链路沿用迭代 3 Runtime；
本期补齐迭代 7 专属的治理层：临时材料 7 天 TTL 与物理清理、贡献六态状态机、
确定性转换预览、提交前强制确认、维护者待处理队列接口。
GitHub App 决策门未确认，**不实现自动 PR**，也不使用用户 OAuth token 冒充。

进入日期：2026-08-23（Asia/Shanghai，`iteration-7` 分支自 `iteration-5` HEAD `0790d20a` 切出）

## 进入检查记录（SOP 4.1）

- 基线分支：`iteration-5`（含迭代 0–6 全部工作）；工作区干净。
- 契约版本：`workflow-contract-v1`；Fixture 语料 `fixture-corpus-v1`。
- 本期只触及 App 运行代码与 SQLite 迁移，不触及 chunker／索引 schema／manifest
  契约，故运行 App CI 全量测试；corpus 兼容性由既有 candidate 校验器覆盖，
  本期未改动任何语料构建输入。
- 本期不包含人工资料转写与 `passed` 裁决。

## 已实现能力

### 后端（全部为增量，不改现有链路行为）

- **契约**（`api/src/scut_senior_api/contracts.py`）：
  - `TemporaryMaterialCreate/Record/Detail`：会话内私有材料，标题 ≤200 字符、正文 ≤100k 字符。
  - `ContributionState` 六态：`draft / submitted / pr_open / merged / rejected / expired`。
  - `ContributionConfirmations`：五项显式确认（课程归属、来源真实、公开分享权利、
    无敏感信息、已知 PR 长期公开），任一缺失即契约拒绝（422），无法提交贡献。
  - `ContributionPreview`：确定性预览结果；`MaintainerContributionTransition`：
    维护者动作仅 `mark_pr_open / merge / reject` 三种。
- **纯规则模块**（`contributions.py`，无 I/O 无模型调用）：
  - `normalize_contribution_markdown`：换行统一、行尾空白、压缩连续空行、单一结尾换行；
    不改写公式、术语与段落语义。
  - `build_contribution_preview`：H1 标题检测、题目标记计数、过短／HTML 残留警告、
    提议来源 ID（`<course>-contribution-<sha256 前 8 位>`，最终编号仍归人工审核分配）。
  - 状态机与反向迁移表：merge 只能从 `pr_open` 进入——没有 PR 就没有可合并对象，
    待处理队列永远不自动合并；`expired/merged/rejected` 为终态。
  - `validate_github_pr_url`：只接受 `https://github.com/<owner>/<repo>/pull/<n>` 固定形态，
    拒绝其他 host、查询串、fragment、userinfo。
- **存储**（迁移 `0008_temporary_materials_contributions.sql`）：
  - `temporary_materials` 表：TTL 固定 7 天，到期整行物理删除。
  - `contributions` 表：`content_snapshot` 是“必要待审副本”，30 天上限；到期清理时
    载荷与 `char_count` 实际清零、未决状态置 `expired`（不能只在 UI 隐藏）。
    draft 继承材料 7 天期限；submitted 及之后使用 30 天期限。
  - 清理任务挂接到仓储初始化（与既有 auth/history 清理同一时机），支持可注入时钟验证。
- **服务层**：保存／列表／详情／删除临时材料、预览、提交（直接提交或草稿）、
  草稿推进、我的贡献列表、维护者队列与状态推进。所有读取按 `user_id` 硬绑定，
  他人资源等同不存在（404）。`mark_pr_open` 必须携带合法 GitHub PR 链接。
- **Runtime 语义**（`workflow_focus.py`，仅 temporary_material_reading 分支追加指令）：
  “材料写了什么”以材料原文优先复述；“材料说得对不对”依据本次仓库资料候选核验并给引用；
  冲突分别陈述、不得混写、不得替材料补造页码。repository／user_material 回答块
  的分离继续由迭代 3 Guard 强制（user_material 块仅允许本 Workflow 使用）。
- **API**：`POST/GET/DELETE /api/v1/temporary-materials[/{id}]`、
  `POST /api/v1/contributions/preview|/|{id}/submit`、`GET /api/v1/contributions[/{id}]`、
  `GET /api/v1/maintainer/contributions`、`POST /api/v1/maintainer/contributions/{id}/transition`。
  维护者端点要求真实 GitHub 登录（mock 身份返回 401）。受保护路径已并入
  `Cache-Control: private, no-store` 中间件。health 端点迭代标记升到 7，
  capabilities 如实登记 `temporary_material_ttl_7d=true`、
  `contribution_maintainer_queue=true`、`github_app_auto_pr=false`。

### 前端

- 新组件 `MaterialContributionPanel.vue`（挂在 WorkflowDrawer 临时材料区块）：
  把当前输入保存为临时材料、查看过期时间、删除；对任一材料做“预览转换结果”
  （展示规范化文本前 2000 字、提议来源编号、警告）；五项确认逐项勾选后才可
  提交待审队列（或先存草稿）；“我的贡献”列表展示状态与 PR 链接。
- `contracts.ts` 类型、`api.ts` 客户端函数同步新增。

## 决策门处理（SOP 12.2）

- 对象存储／离线任务最终实现：**未确认**。本期只支持文本／Markdown 粘贴
  （SOP §12 本就限定文本），不引入对象存储依赖。
- GitHub App 实现方式与权限：**未确认**。按 PLAN 允许进入维护者待处理队列；
  `ContributionPublisher` 保持迭代 0 的 `DisabledCapability("github_app")` 占位，
  不用用户 OAuth token 创建 PR。PR 由维护者人工创建后在队列中登记链接，
  应用内不存在任何自动创建或自动合并路径。
- 账号注销／提前删除／导出中与临时材料有关的部分：注销规则整体仍未确认（PLAN 第 20 节），
  但临时材料自身的 7 天／30 天期限清理本期已实际生效。

## 测试命令与结果

```text
cd apps/scut-senior
.venv/bin/python -m pytest tests/python      # 539 passed（含新增 17 项）
python -m scut_senior_api.export_contracts --check   # OK（本次新增模型不影响已导出 schema）
npm --prefix web run test                    # 94 passed（14 files）
npm --prefix web run typecheck               # 通过
npm --prefix web run build                   # 成功
```

新增 `tests/python/test_iteration_7_materials_contributions.py` 覆盖：

- 契约：确认项缺一即拒；预览确定性（同输入同输出、含来源 ID）；规范化不丢语义内容。
- 状态机：全部非法迁移被拒（submitted→merge、draft→pr_open、终态再迁移等）。
- PR 链接：七类变形（http、伪域名、pulls、#0、query、fragment、userinfo）全拒绝。
- TTL：7 天到期材料行物理删除（SQL 计数为 0）；30 天到期贡献副本载荷与字数清零、
  状态置 expired；draft 继承 7 天期限。
- API 全流程：保存→列表→详情→预览→缺确认被拒→提交→draft 推进→重复提交 409。
- 隔离：oauth 双用户下 Bob 读／删 Alice 材料与贡献均 404、列表为空。
- 维护者边界：mock 身份访问队列 401；无 PR 直接 merge 409；mark_pr_open 缺链接 409；
  pr_open→merged→终态后不再接受迁移并退出默认队列；reject 附带备注回传作者视图。
- 泄漏：贡献记录序列化结果不含正文标记词与 credential 类字段。
- 检索隔离：临时材料工作流运行后，全部 citations 来自课程语料，不含用户私有文本标记。

同步更新两个既有“迭代推进”断言：health 迭代号（5→7）、迁移账本（追加 0008）。

## 已知限制与降级

- 自动 PR 未实现（决策门未确认）：贡献进入本地待处理队列，维护者手工在仓库侧
  建 PR 并回填链接。“公开展示贡献者 login 前另行取得同意”在自动 PR 落地时
  才产生实际暴露面；当前 UI 不展示任何用户 login，贡献 ID 为不透明 UUID。
- “会话内临时切分”沿用现有聚焦检索（材料标题＋正文锚点生成权威查询，与课程
  语料联合检索），没有为单次请求建立独立的会话级向量子索引；这是实现方式选择，
  不改变隔离语义（私有材料永不成为检索候选）。
- merged 只是应用内状态标记；内容真正进入 active 语料仍必须走
  仓库 PR → 人工 `passed` → candidate 构建/验证 → 激活的既有发布链，应用侧无法也
  不允许绕过。
- 维护者端点沿用既有 `require_github_user` 边界（任意真实登录用户），未建独立
  维护者角色体系；这与 plugin-registry 现状一致，属既有边界而非本期引入。

## 尚待确认项（延续 PLAN-1 第 20 节）

1. GitHub App 实现方式与最小权限（Contents+Pull Requests）、机器人身份；
2. 对象存储与离线任务最终实现（图片／附件属迭代 8）;
3. 账号注销、提前删除与导出规则中涉及贡献副本的部分；
4. Trace 排序分数默认展开程度等其他未确认项不变。

## 下一期可依赖的稳定契约

- `temporary-materials` 与 `contributions` 两组 REST 端点及其响应模型；
- `ContributionState` 六态及迁移规则（submit/mark_pr_open/merge/reject 动作词表）；
- 迁移 0008 表结构（后续如加索引只增不改）；
- 清理入口 `cleanup_material_records()` 可注入时钟，便于迭代 8 复用做附件 TTL。

## 基线

- Python 3.14.6（仓库 `.venv`）；FastAPI/TestClient；Vue 3 + vitest。
- 本期未触碰：worker、knowledge/**、corpus builder、BYOK、OAuth、Bilibili 链路。

## 追加（同日）：add file 落点语义与维护者导出包

按使用者反馈把贡献目标明确为「学科资料源文件新增」而非直接写知识库：

- 课程 → 学科资料目录映射复用 `courses.json` 既有 `repository_paths`；
  未登记路径的课程退到 `学科资料/_待归类/<course_id>/`，不误入错误学科。
- 提交/预览即返回确定性 `proposed_repo_path`
  （`derive_proposed_repo_path`：注册表路径 + 标题派生安全文件名，
  Markdown 痕迹嗅探 `.md`/`.txt` 扩展名，非法字符清洗）。
- 迁移 `0009_contributions_repo_path.sql`：`contributions.proposed_repo_path` 列。
- 新端点 `GET /api/v1/maintainer/contributions/{id}/export`
  （`MaintainerContributionExport`）：返回 repo_path、内容快照、建议分支名与
  分步 git 命令；**应用不自动写工作树、不执行 git、不推送**——"add file"
  的最后一步永远由维护者人工完成，符合 SOP 的 candidate/人工审核前置门。
- 前端预览与“我的贡献”展示提交落点。

测试增量：落点映射、文件名清洗与扩展名嗅探、导出包内容/命令/鉴权
（Python 全量 542 通过；web vitest 94 + typecheck 通过）。
