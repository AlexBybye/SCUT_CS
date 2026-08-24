# SCUT 老学长 语料维护操作手册（Maintainer Runbook）

版本：1.1（2026-08-24）

> 1.1 修订：§6.4/§7.1 依据 2026-08-24 首次真实发布修正——激活与回滚后 API 经指针键控
> 缓存自动切换、无需重启；补记「新课程开关默认关闭，激活后须显式启用」与 rollback
> 后 course_switches 重建行为；检索抽查改用 `/api/v1/courses`（无独立 search 端点）。

读者：维护者（内容审核人与语料发布人）

适用范围：从「贡献者提交资料」到「应用可检索」的完整内容贡献链：
**审核 PR → 确定性转换 → AI 语义归一化 → 人工审核 → 构建验证 → 激活发布**，
以及上线后的观测、课程开关与回滚。

配套文档：`MATERIAL_TO_MARKDOWN_SOP.md`（转换 SOP，给资料负责人）、
`CODE_ITERATION_SOP.md`（代码迭代 SOP）、`tools.md`（工具与配置）。

---

## 0. 概念速览

### 0.1 资料状态机（manifest `status` 列）

| 状态 | 含义 | 谁能置此状态 |
|---|---|---|
| `pending` | AI/转换器产出，等待人工审核 | AI/转换器/资料负责人 |
| `passed` | 已人工审核通过，可进入语料 | **只有人工**（SOP 红线） |
| `needs_fix` | 审核不过，需返工（必须写 `notes`） | 人工 |
| `rejected` | 审核不过，拒绝收录（必须写 `notes`） | 人工 |

附加列 `preview`（空白 / `false` / `page-image`）：`page-image` 表示该
`passed` 源是维护者批准的纯图扫描件，按整页图片预览保留——**零文本 chunk、
不可文本检索、图片资产保留**，只能配 `passed`。

### 0.2 仓库关键路径

| 路径 | 内容 |
|---|---|
| `apps/scut-senior/knowledge/` | 已转换 Markdown + 资产（唯一事实源） |
| `apps/scut-senior/knowledge/manifest.csv` | 资料清单（17 列，含 `preview`） |
| `apps/scut-senior/.local/corpus-store/` | 语料构建产物：`candidates/<version>/` + `active.json`（**不提交 Git**） |
| `apps/scut-senior/worker/` | `corpus_builder` / `corpus_validator` |
| `apps/scut-senior/api/` | FastAPI 服务，读 `active.json` 提供检索 |
| `apps/tools/material_converter/` | 转换器 + AI 归一化管线 |
| `.cache/glm4v.env` | GLM-4V 凭证（`GLM_API_KEY` / `GLM_BASE_URL` / `GLM_MODEL`），不入 Git |
| `.ai_jobs/`（converter 下，gitignored） | AI 作业包与转写结果，不入 Git |
| `学科资料/` | 原始资料（不参与 CI、不入知识目录） |

### 0.3 铁律（本手册其余内容都围绕它们）

1. **只有人工审核能置 `passed`**；AI/转换器产出一律 `pending`。
2. **AI 只转写/恢复/提议，绝不发明/总结/改写**（SOP 4.2）。
3. **构建产物不可变**：candidate 一经写出不可改，激活只是原子切换 `active.json` 指针。
4. **激活只认 master**：`source_commit` 必须是 `refs/heads/master`（本地或远端）的后代提交。
5. **不破解加密 zip**：加密素材一律退回贡献者要解密版（SOP 红线）。
6. **manifest 列与 `convert.FIELDS` 单一事实源**：任何写 manifest 的代码都从
   `convert.FIELDS` 取列，禁止硬编码字段列表（事故 #5）。

---

## 1. 端到端流程总览

```
贡献者提交资料/PR
      │
      ▼
┌─────────────────────┐
│ ① 审核 PR（§2）      │  隐私前置、SOP 合规、CI 门禁
└─────────────────────┘
      │ 通过
      ▼
┌─────────────────────┐
│ ② 确定性转换（§3）    │  converter → knowledge/*.md + manifest 行（pending）
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│ ③ AI 语义归一化（§4） │  emit-ai-jobs → vision-run → vision-propagate → finalize
└─────────────────────┘  （公式图 → LaTeX；状态保持 pending）
      │
      ▼
┌─────────────────────┐
│ ④ 人工审核（§5）      │  对照原件抽查 → 置 passed（或 needs_fix/rejected）
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│ ⑤ 构建与验证（§6）    │  corpus_builder build + validate + 测试（本地 CI 等效）
└─────────────────────┘
      │ 合并 master 后
      ▼
┌─────────────────────┐
│ ⑥ 激活发布（§6.4）    │  activate → 启用新课程 → 健康检查
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│ ⑦ 观测/开关/回滚（§7） │  课程开关、rollback、事故台账
└─────────────────────┘
```

一次内容更新（新增/修改/删除任何 knowledge 内容）都走完 ①→⑥；只修代码/测试不碰
knowledge 时走 ⑤ 的测试部分即可。

---

## 2. 阶段①：审核 PR（贡献接收）

贡献者以 PR 提交：`学科资料/` 原始文件 + `apps/scut-senior/knowledge/` 转换产物 +
manifest 行。审核清单：

1. **CI 门禁**：`corpus-ci.yml` 会在 PR 上跑（见 §6.1）。要求全绿：
   - manifest 校验 0 错误（`corpus_validator`）
   - 真实 candidate 构建 + `validate` 通过（`validation.ok == true`）
   - corpus 生命周期/契约/fixture 测试通过
2. **隐私前置**（SOP §步骤9）：manifest 与 md 不得残留学生/贡献者姓名、班级、学号；
   原始文件名含身份信息的必须已 `git mv` 脱敏。
3. **SOP 合规**：frontmatter 与 manifest 一致（source_id/title/original_path/
   document_role/year/locator_type）；`locator_type` 不猜测；无文本层纯图文件走
   `preview=page-image` 流程（§3.3），不擅自置 passed。
4. **规模与结构**：转换产物是 md + assets（资产目录与 md 相邻）；`.ai_jobs/`、
   `.work/`、`active.json`、`corpus-store/` 等中间产物不允许出现在 PR 里。
5. **确认制**：合并前维护者显式确认贡献者已按 SOP 自查（ITERATION_7 决策：不使用
   OAuth 自动建 PR，也不自动合并）。

审核通过 → merge（内容改动建议走 `design/*` 或 `maintenance/*` 分支，合并进
`master` 前先做 §6.3 的 CI 等效本地构建）。

---

## 3. 阶段②：确定性转换（管道转化）

转换器：`apps/tools/material_converter/`，只做确定性抽取（文本/标题/表格/图片、
OMML→LaTeX、页码/幻灯片标记），**不做任何 AI 工作**。

### 3.1 前置

- 课程已注册：`apps/scut-senior/packages/contracts/v1/courses.json` 有该课程
  `course_id`/`aliases`/`repository_paths`；manifest 列顺序与 `convert.FIELDS` 一致。
- 环境：LibreOffice（`MMD_SOFFICE`）、仓库根 `.venv`（含 python-docx 等依赖）、
  隐私 prepass 完成。

### 3.2 转换命令

```bash
cd apps/tools/material_converter
PYTHONPATH=<repo>/apps/tools/material_converter <repo>/.venv/bin/python \
  -m material_converter.main --course <学科资料文件夹名> --validate
```

- 只处理 `学科资料/` 下该文件夹内的文件；已在 manifest（`original_path` 相同）的
  自动跳过；产出行一律 `pending`。
- 转换中自动做：OMML→LaTeX、表格、隐私 prepass、`add_question_markers` 等确定性步骤。
- `--dry` 先跑一遍看报告；`--file <路径>` 只转单个文件。

### 3.3 纯图片扫描件（无可提取文本层）

- 转换器从 docx 的 `mc:AlternateContent` 分支提取整页图片（事故 #2 修复后），产出
  纯图片 md + assets。
- 该行 `notes` 写明「纯图无文本层」，**状态保持 `pending`**，等人工决定：
  - 批准保留 → 置 `passed` + `preview=page-image`（不产出文本 chunk）；
  - 不批准 → 保持 `pending`，等 OCR 补文本层后重新审核（图片 OCR 三道闸迭代 8 关闭）。
- 切勿把零 chunk 的普通 passed 源混进来：构建器只对 `preview=page-image` 且有资产的
  源放行零 chunk（事故 #3、#4）。

### 3.4 转换后自查

```bash
# manifest 校验（必须 0 errors）
PYTHONPATH=apps/scut-senior/worker/src \
  apps/scut-senior/api/.venv/bin/python -m scut_senior_worker.corpus_validator \
  --manifest apps/scut-senior/knowledge/manifest.csv \
  --knowledge-root apps/scut-senior/knowledge
```

抽查 1～2 份 md 对照原件：标题层级、表格、公式、页码标记无误。

---

## 4. 阶段③：AI 语义归一化

只对 `pending` 行执行；产出保持 `pending`。四段式（`SKILL.md` 亦载明）：

```bash
cd apps/tools/material_converter

# 4a. 导出作业包：扫描 pending md 的公式图（![formula-object]...png）与 OCR 页
PYTHONPATH=<repo>/apps/tools/material_converter <repo>/.venv/bin/python \
  -m material_converter.main --emit-ai-jobs [--course <课程id或文件夹名>]

# 4b. GLM-4V 视觉转写公式图（先小样 --vision-run 20 再全量）
PYTHONPATH=<repo>/apps/tools/material_converter <repo>/.venv/bin/python \
  -m material_converter.main --vision-run all --vision-workers 4

# 4c. 按内容哈希传播（同一张图只转一次，去重）
PYTHONPATH=<repo>/apps/tools/material_converter <repo>/.venv/bin/python \
  -m material_converter.main --vision-propagate

# 4d. 应用回 knowledge：替换 $...$、清理已用资产、notes 标记，状态保持 pending
PYTHONPATH=<repo>/apps/tools/material_converter <repo>/.venv/bin/python \
  -m material_converter.main --finalize [--course <课程id或文件夹名>]
```

要点：

- **凭证**：`.cache/glm4v.env` 提供 `GLM_API_KEY`（智谱 open.bigmodel.cn，
  `glm-4v-flash`）。`max_tokens` 不得超过 1024（事故 #7）。
- **三道闸**：三票多数决 → 确定性校验（括号配平/无 CJK/命令白名单）→ mathtext
  渲染闸。未过闸的公式**自动保留 PNG 图片**，绝不强行替换。
- **范围限定**：`vision-run` 转写的是 `.ai_jobs/_unique_images.json` 里列出的图；
  该文件按内容哈希覆盖目标作业包的公式图。只想处理某批课程时，先重建该文件只含
  对应课程的公式资产（§4.1）。
- **`--finalize` 必须限定课程**（或确认 `.ai_jobs/` 无陈旧作业包）：不限定会把
  历史遗留作业包应用到已 `passed` 行并打回 `pending`（SOP 有意为之，但非本次意图）。
- finalize 会按 `convert.FIELDS` 重写整个 manifest（事故 #5 后已修复）——改 manifest
  列的代码必须同步 `convert.FIELDS`，禁止别处再硬编码字段清单。

### 4.1 重建唯一图清单（限定新批次时）

```python
# .ai_jobs/_unique_images.json 格式：{md5hex: [绝对路径...]}
# 只收集目标 source_id 的 formula PNG 资产，按内容哈希分组后写回。
# vision_worker 会跳过 _vision_results.jsonl 中已 done 的路径，可断点续跑。
```

### 4.2 无视觉模型时的降级路径

跳过 4b/4c，人工在 `.ai_jobs/<sid>/formulas.json` 里填 LaTeX，再执行 4d。

---

## 5. 阶段④：人工审核与 passed 裁决

**唯一能把 `pending` 置为 `passed` 的是人。** AI 转写越多，这一步越不能省。

1. **逐份对照原件**：抽查转换 md vs `学科资料/` 原始文件——标题层级、正文完整性、
   表格行列、页码连续性。
2. **公式抽查**：被 AI 转写的 `$...$` LaTeX（manifest notes 会带
   `AI-transcribed ... pending human re-check per SOP 4.2`）优先抽查；多份批量转写的
   挑量大的 1～2 份整体过一遍。未过闸仍是 PNG 的公式：可接受现状，或人工补 LaTeX
   进 formulas.json 后重跑 `--finalize`。
3. **题界与顺序**：`add_question_markers` 产生的题号边界与原文一致；题目顺序无错位。
4. **隐私终检**：整份 md 与 manifest 无姓名/班级/学号。
5. **裁决**：
   - 通过 → manifest 该行置 `passed` + `reviewer` 填审核人；纯图扫描件同时置
     `preview=page-image`；
   - 需返工 → `needs_fix` + `notes` 写具体问题；
   - 拒绝 → `rejected` + `notes` 写理由。
6. **批量改状态**用 python `csv` 逐行读写（不要用整文件 DictWriter 重写，会破坏
   引号转义——事故 #8），改完跑 §3.4 的校验器确认 0 errors。

---

## 6. 阶段⑤⑥：构建、验证与激活

### 6.1 CI 在做什么（`corpus-ci.yml`）

PR（knowledge/worker/packages/tests 相关路径）与 `master` push 时触发，sparse
checkout（不含 `学科资料/`、`web/`、`api/`）后依次：

1. `corpus_validator` 校验仓库 manifest（0 errors）；
2. `corpus_builder build` 真实构建一个 candidate（临时 store，**不激活**）；
3. 断言恰好生成 1 个 candidate；`corpus_builder validate` 通过；
4. 断言未生成 `active.json`；
5. pytest：corpus 生命周期 + validator + 契约资产测试；
6. fixture manifest 校验。

任何一步红 → PR 不允许合并。

### 6.2 本地 CI 等效构建（提交前必跑）

```bash
git worktree add /tmp/ci-wt <full-sha>          # 全 40 位 SHA（事故 #6）
cd /tmp/ci-wt
PYTHONPATH=apps/scut-senior/worker/src \
  /Users/bilibili/Documents/SCUT_CS/apps/scut-senior/api/.venv/bin/python \
  -m scut_senior_worker.corpus_builder build \
  --manifest apps/scut-senior/knowledge/manifest.csv \
  --knowledge-root apps/scut-senior/knowledge \
  --store-root /tmp/ci-store \
  --source-commit "$(git rev-parse HEAD)" \
  --repository-root .
```

核对 metadata：`source_count`、`chunk_count`、`available_courses` 与预期一致；
`validate` 输出 `ok: true`。构建后清理 worktree：

```bash
git worktree remove /tmp/ci-wt --force && rm -rf /tmp/ci-store
```

### 6.3 全量测试（改了 worker/validator/转换器时）

```bash
cd apps/scut-senior && api/.venv/bin/python -m pytest tests/python -q
# 契约检查
api/.venv/bin/python -m scut_senior_api.export_contracts --check
```

### 6.4 激活发布（只在 master 上）

candidate 的 `source_commit` 必须已合入 `refs/heads/master`（本地或远端），
否则 `activate` 拒绝（`_verify_commit_on_trusted_master`）。

```bash
cd <repo> && git checkout master && git pull --ff-only

# 主仓 .local store 构建（CI 只构建不激活，本地这步负责真激活）
PYTHONPATH=apps/scut-senior/worker/src \
  apps/scut-senior/api/.venv/bin/python -m scut_senior_worker.corpus_builder build \
  --manifest apps/scut-senior/knowledge/manifest.csv \
  --knowledge-root apps/scut-senior/knowledge \
  --store-root apps/scut-senior/.local/corpus-store \
  --source-commit "$(git rev-parse HEAD)" \
  --repository-root .

# 找到生成的 candidate 版本号，然后原子激活
CORPUS_VERSION=<candidates/ 下的目录名>
PYTHONPATH=apps/scut-senior/worker/src \
  apps/scut-senior/api/.venv/bin/python -m scut_senior_worker.corpus_builder activate \
  --store-root apps/scut-senior/.local/corpus-store \
  --corpus-version "$CORPUS_VERSION" \
  --repository-root . \
  --trusted-master-ref refs/heads/master
```

激活只是原子写 `active.json`（新版本 + 保留 `course_switches` + `previous` 指向旧版
本）。之后：

1. **API 自动切换，无需重启**（2026-08-24 实测）：本地语料读取走指针键控校验缓存，
   `active.json` 指针变更后下一次请求自然失效重载。仅当本次同时改了 API 代码本身
   才需要重启 uvicorn。
2. **显式启用新课程**（重要，易漏）：`activate_candidate` 里新课程的开关继承旧指针
   的值，**新课程默认 `false`（关闭）**，所以激活后 selectable 数不会自动增加。
   必须对每一门本次新增的课程执行 §6.5 的 `course` 开关置 `true`，否则课程可构建
   但不可选。
3. 健康检查：

```bash
curl -s http://127.0.0.1:8000/api/v1/health
# 期望：retrieval_mode=local_corpus、local_corpus_available=true、
# formal_exit_blocked=false、selectable_course_count = 启用课程数（含新课程）
```

4. 抽查新课程可用性（无独立 search REST 端点，检索在对话流内完成）：

```bash
curl -s http://127.0.0.1:8000/api/v1/courses | python3 -c \
  "import json,sys; [print(c['course_id'], c['retrieval_available']) \
   for c in json.load(sys.stdin)['courses'] if c['course_id'] in ('<新课程1>','<新课程2>')]"
# 期望全部 true；纯图预览课程（preview=page-image）可选但检索返回空，属预期
```

5. 确认 `active.json` 状态与回滚路径：`previous_corpus_version` 指向旧版
   （§7.1 回滚依赖它），`course_switches` 含全部启用课程。

### 6.5 课程级开关

```bash
PYTHONPATH=apps/scut-senior/worker/src \
  apps/scut-senior/api/.venv/bin/python -m scut_senior_worker.corpus_builder course \
  --store-root apps/scut-senior/.local/corpus-store \
  --course-id <course_id> \
  --enabled true|false
```

不重建语料即可上下架单门课；开关记录在 `active.json` 的 `course_switches`。

---

## 7. 阶段⑦：上线后观测、回滚与故障排查

### 7.1 回滚（原子交换 active ↔ previous）

```bash
PYTHONPATH=apps/scut-senior/worker/src \
  apps/scut-senior/api/.venv/bin/python -m scut_senior_worker.corpus_builder rollback \
  --store-root apps/scut-senior/.local/corpus-store \
  --repository-root . \
  --trusted-master-ref refs/heads/master
```

回滚目标（`previous_corpus_version`）必须是已通过 `validate` 的不可变 candidate，
`source_commit` 同样必须落在 master。回滚后 API 自动切换（同 §6.4，无需重启），
随后健康检查确认 selectable 回到旧版本课程数。注意：回滚会把 `course_switches`
按旧版本的课程集重建，旧版本里没有的课程（本次新增的）开关会变成 `false`——如需
保留，回滚后按 §6.5 重新启用。

### 7.2 常见故障排查表

| 症状 | 可能原因 | 处置 |
|---|---|---|
| API 检索慢/卡死 | 僵尸 uvicorn 进程抢占端口；可用性检查并发饿死线程池（事故 #1） | 先 `lsof -i :8000` 查旧进程，杀掉重复实例；本地语料读取走指针键控缓存，确认 active.json 指向的 candidate 可 validate |
| CI 报 passed 源零 chunk | 源是纯图 md 但 manifest 未标 `preview=page-image`（事故 #3/#4） | 人工裁决：置 preview 或补文本层 |
| 转换后 md 是空壳/图片全丢 | docx 图片包在 `mc:AlternateContent`（事故 #2） | 用修复后的 docx2md 重新转换（Choice 分支提取） |
| `--finalize` 后 manifest 列错乱 | `_save_rows` 硬编码字段缺列（事故 #5，已修） | 恢复 manifest 到上一提交，确认 `convert.FIELDS` 含全部列 |
| build 报 `source_commit must be a full 40-character` | 传了短 SHA（事故 #6） | `git rev-parse HEAD` 取全 40 位 |
| GLM 转写 HTTP 400 | `max_tokens>1024`（事故 #7） | 保持 ≤1024；429 是限流，管线自动退避续跑 |
| 课程可选但检索全空 | 该课全零 chunk（纯图预览，或构建回归） | 确认是 `preview=page-image` 预期行为；否则查构建 chunk 计数 |
| 资料是加密 zip | SOP 禁止破解（红线 5） | 退回贡献者要解密版 |

### 7.3 事故台账（教训即文档）

1. **僵尸 uvicorn + 可用性检查饿死线程池**（修复 `accc54d1`）：55×3.9s 可用性检查
   占满线程池，导致插件注册表读不到课程、BYOK 过期不变、课程非中文。修复：本地语料
   读取改为指针键控校验缓存，可用性检查按指针缓存，不再每次全量校验。
2. **docx2md 丢失 `mc:AlternateContent` 内图片**：扫描式 docx 每页图包在
   AlternateContent（Choice/Fallback），旧 `_run` 只处理 `w:r` 直接子节点 → 图片全丢、
   md 空壳 → CI 零 chunk 失败。修复：识别 `AlternateContent` 且只取 Choice 分支
   （防 rId 重复提取），连续图片引用拆行。
3. **通用「纯图片文档」判定误伤 908 源/3 门课**：最初让构建器把所有纯图片 md 当
   preview，导致 machine_learning、circuit_and_electronics_lab、
   electrical_engineering_lab 整门变零 chunk 空课。修复：preview 语义只对 manifest
   显式 `preview=page-image` 的行生效，其余文档 chunk 行为与历史逐字节一致；补回归
   测试（非 preview 纯图源仍产 chunk）。
4. **图片型 passed 源让 CI 失败**：零 chunk passed 源被构建器硬拒绝。修复：仅当
   `preview=page-image` 且有资产时放行，否则仍然失败关闭。
5. **`ai_stage._save_rows` 硬编码字段缺 `preview` 列**：一旦 `--finalize` 就会重写
   整份 manifest 丢掉 preview 状态。修复：改为从 `convert.FIELDS`（单一事实源）取列；
   并同步 `main.py` 新行写入。
6. **短 SHA 被 `_require_commit` 拒绝**：CI 等效构建必须传 `git rev-parse HEAD` 的
   完整 40 位。
7. **GLM-4V `max_tokens=2048` → HTTP 400**：公式转写通道上限 1024。
8. **csv 整文件 DictWriter 重写破坏引号转义**：批量改 manifest 用 `csv.reader` 逐行
   读 + `csv.writer` 逐行写，禁止整文件重构。

---

## 8. 红线清单（每条都有事故背书）

1. 修复必须进管线代码 + 回归用例；禁止对生成物做一次性脚本后处理。
2. 只有人工审核置 `passed`；AI 产出永远 `pending`。
3. AI 只转写/恢复/提议，不发明/总结/改写；未过闸的内容保留原样（如 PNG 公式）。
4. 不破解加密 zip；加密素材退回贡献者。
5. 不提交中间产物：`active.json`、`corpus-store/`、`.ai_jobs/`、`.work/`。
6. 不改 `convert.FIELDS` 之外的另一份 manifest 字段清单（单一事实源）。
7. 构建激活只认 master 后代提交；candidate 不可变，激活原子。
8. manifest 与 md 不得残留学生/贡献者姓名、班级、学号。

---

## 9. 命令速查表

| 目的 | 命令（均在仓库根或注明目录执行） |
|---|---|
| 转换单课程 | `cd apps/tools/material_converter && PYTHONPATH=... .venv/bin/python -m material_converter.main --course <文件夹名> --validate` |
| manifest 校验 | `PYTHONPATH=apps/scut-senior/worker/src apps/scut-senior/api/.venv/bin/python -m scut_senior_worker.corpus_validator --manifest apps/scut-senior/knowledge/manifest.csv --knowledge-root apps/scut-senior/knowledge` |
| 导出 AI 作业包 | `... material_converter.main --emit-ai-jobs [--course ...]` |
| 视觉转写 | `... material_converter.main --vision-run all --vision-workers 4` |
| 传播转写 | `... material_converter.main --vision-propagate` |
| 应用 AI 结果 | `... material_converter.main --finalize [--course ...]` |
| 构建 candidate | `... corpus_builder build --manifest ... --knowledge-root ... --store-root ... --source-commit "$(git rev-parse HEAD)" --repository-root .` |
| 校验 candidate | `... corpus_builder validate --candidate <path>` |
| 激活 | `... corpus_builder activate --store-root apps/scut-senior/.local/corpus-store --corpus-version <v> --repository-root . --trusted-master-ref refs/heads/master` |
| 回滚 | `... corpus_builder rollback --store-root apps/scut-senior/.local/corpus-store --repository-root . --trusted-master-ref refs/heads/master` |
| 课程开关 | `... corpus_builder course --store-root apps/scut-senior/.local/corpus-store --course-id <id> --enabled true` |
| 全量测试 | `cd apps/scut-senior && api/.venv/bin/python -m pytest tests/python -q` |
| 契约检查 | `cd apps/scut-senior && api/.venv/bin/python -m scut_senior_api.export_contracts --check` |
| 健康检查 | `curl -s http://127.0.0.1:8000/api/v1/health` |

> 路径说明：`<repo>/...` 中的 `<repo>` 指仓库根；本机已验证的绝对路径为
> `/Users/bilibili/Documents/SCUT_CS`。converter 依赖仓库根 `.venv`；worker 相关命令
> 用 `apps/scut-senior/api/.venv`（其内装好 worker 依赖，可直接 import）。
