# material_converter · 学科资料 → 知识库 Markdown 管线

把 `学科资料/` 下的 DOCX / DOC / PDF / PPTX / PPT / TXT / CPP / MD / 散图，
按 `apps/scut-senior/docs/MATERIAL_TO_MARKDOWN_SOP.md` v1.7 转成带 frontmatter、
图片资产、page/slide/heading 锚点、manifest 记录的知识库条目。

**两段式架构**：

```
确定性抽取（本工具，无 AI）          AI 语义归一化（GLM-4V 视觉转写）
├─ 文本/标题层级/表格/图片    ──►   ├─ 公式预览图 → LaTeX（三道闸）
├─ 原生 OMML 公式 → LaTeX           └─ 未过闸自动保留 PNG（SOP 4.2 回退）
├─ WMF/EMF 矢量公式 → PNG
├─ PDF 分页 / 扫描页整页渲染        人工审核（唯一 passed 入口，SOP §4）
├─ 去重 / 准入判断 / 隐私预处理
└─ manifest.csv 记录
```

> 红线：工具与 AI 都**不总结、不纠错、不猜写**；AI 输出永远 `pending`；
> 只有对照过原件的人才能置 `passed`。

---

## 一、环境要求

| 组件 | 必需性 | 说明 |
|---|---|---|
| Python **3.10+** | 必需 | 建议 3.11/3.12 |
| LibreOffice 26.x | doc/ppt/矢量公式需要 | 纯 docx/pptx/pdf 课程可不装 |
| GLM-4V API Key | 仅视觉转写需要 | 智谱开放平台 `glm-4v-flash` 有免费额度 |
| Git Bash / PowerShell | 运行脚本 | Windows 推荐 PowerShell |

依赖清单见 `requirements.txt`（mammoth、python-docx、python-pptx、pymupdf、
pyyaml、olefile、matplotlib）。全部装进仓库根的 `.venv`，不污染系统。

## 二、安装

### macOS / Linux

```bash
cd 仓库根目录
bash apps/tools/material_converter/bootstrap.sh      # 建 .venv + 装依赖
# LibreOffice：brew install --cask libreoffice 或从官网 DMG 安装
```

### Windows（PowerShell）

```powershell
cd 仓库根目录
powershell -ExecutionPolicy Bypass -File apps\tools\material_converter\bootstrap.ps1
# LibreOffice：https://www.libreoffice.org 下载安装（默认路径可被自动识别）
```

脚本会自动探测 soffice 并写入用户环境变量 `MMD_SOFFICE`；重开终端生效。
手动设置：`setx MMD_SOFFICE "C:\Program Files\LibreOffice\program\soffice.exe"`

### 视觉转写凭证（可选）

仓库根建 `.cache/glm4v.env`（已被 gitignore）：

```
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
GLM_MODEL=glm-4v-flash
GLM_API_KEY=<你的key>
```

> 注意：视觉转写会把试卷图片上传到智谱云。内容为课程资料且身份信息已脱敏。

---

## 三、快速开始

```bash
cd apps/tools/material_converter

# macOS/Linux                                # Windows PowerShell
$PY = ../../../.venv/bin/python               $PY = ..\..\..\.venv\Scripts\python.exe

$PY -m material_converter.main --dry                    # 全量预演（不改任何文件）
$PY -m material_converter.main --course 线性代数         # 只跑某课程
$PY -m material_converter.main                          # 全量增量（幂等，已入库自动跳过）
$PY -m material_converter.main --validate               # 结束后跑 corpus_validator
$PY -m material_converter.main --file "学科资料/xx.pdf"  # 单文件调试
```

Windows 下若提示找不到 soffice：先 `$env:MMD_SOFFICE="C:\Program Files\LibreOffice\program\soffice.exe"` 再运行。
所有命令都在 `apps/tools/material_converter` 目录下执行（包内路径自定位，放哪都能跑，
但**不要**把包挪出 `apps/tools/`，README/SKILL/CI 引用均以此为准）。

---

## 四、完整工作流（新学科入库）

### 第 1 步 · 课程注册（先注册再转换）

编辑 `apps/scut-senior/packages/contracts/v1/courses.json`，追加：

```json
{ "course_id": "data_structure", "display_name": "数据结构",
  "aliases": ["数据结构与算法"], "repository_paths": ["学科资料/数据结构"],
  "is_open": false, "fixture_available": false }
```

- `repository_paths` 指向 `学科资料/<文件夹>`（相对仓库根）
- 同步更新冻结测试计数：`tests/python/test_registry.py`、`test_harness_registry.py`
  的 `len==N`，以及 `test_contract_assets.py` 的 `EXPECTED_COURSE_IDS`
- 跑一遍：`uv run --project api pytest tests/python -q` 应全绿

### 第 2 步 · 隐私前置

文件名含真实姓名/学号/班级 → 先 `git mv` 脱敏；docx/pptx/pdf 元数据工具会自动清洗；
正文身份泄露由 `scan_privacy` 标记进 notes，人工决议后保留或删除。

### 第 3 步 · 确定性抽取

```bash
$PY -m material_converter.main --course 数据结构 --validate
```

输出行含义：`candidates=候选 already_in_manifest=已入库 dedup_skipped=去重
converted=新增 skipped=复用 errors=失败`。**errors 必须为 0** 再继续。

### 第 4 步 · AI 视觉转写（可选，需 glm4v.env）

```bash
$PY -m material_converter.main --emit-ai-jobs            # 导出作业包 .ai_jobs/<sid>/
$PY -m material_converter.main --vision-run 20           # 先抽 20 张验质量
$PY -m material_converter.main --vision-run              # 全量（约 2-3 次/张调用）
$PY -m material_converter.main --vision-propagate        # 内容哈希去重传播
$PY -m material_converter.main --finalize                # 应用：图片引用→ $LaTeX$
```

- 三道闸：三票多数决 → 确定性校验（配平/禁散文/粘连拆分）→ mathtext 渲染闸
  （矩阵类环境逐单元格校验）。任一不过 → 自动保留 PNG，绝不猜写
- 断点续跑：进度落在 `.ai_jobs/_vision_results.jsonl`，中断后重跑只补缺
- 无视觉模型时：跳过 vision 两步，人工直接填 `.ai_jobs/<sid>/formulas.json`
  （格式 `{图片名: "latex"}`，没把握的留空串）后再 `--finalize`

### 第 5 步 · 人工审核 → passed

对照原件逐文件检查公式/题界/顺序/隐私，确认后把 manifest 该行 `status` 改
`passed` 并填 `reviewer`。**这是唯一入库入口。**

### 第 6 步 · 构建 candidate（应用侧）

由 corpus builder 在洁净树上另行执行，不在本工具范围。

---

## 五、命令参考

| 命令 | 作用 |
|---|---|
| `--course <文件夹名>` | 只处理指定课程 |
| `--file <路径>` | 单文件转换调试 |
| `--dry` | 预演统计，不写任何文件 |
| `--validate` | 结束后运行 corpus validator |
| `--emit-ai-jobs [课程]` | 导出 AI 作业包（pending 行；公式图/OCR页清单）|
| `--finalize [课程]` | 应用 formulas.json/notes.md，状态保持 pending |
| `--vision-run [N]` | GLM-4V 转写（N=张数限制；省略=全量）|
| `--vision-workers N` | 转写并发数（默认 4）|
| `--vision-propagate` | 转写结果按内容哈希传播 |

`.ai_jobs/<sid>/` 结构：`source.md`（当前草稿）、`formulas.json`（待转公式）、
`ocr_pages.json`（扫描页清单，OCR 属后续迭代）、`meta.json`。

## 六、去重与准入规则（SOP 1.7）

1. 已入库 `original_path` 直接跳过（增量幂等的基础）
2. 字节级 md5 相同 → 复用
3. 核心词基线相同（剥掉 无答案/答案/解答/题解/评分标准 后同名）→ 识别规范来源
4. 「无答案」是「答案」版严格子集（容忍 ≤30% 差异）→ 只转答案版
5. 跨课程误放（如概率论卷子放在工数 I 目录）→ 归属内容所在课程，只转一份
6. 加密 zip 不破解不入库，等待密码

## 七、隐私红线

- 文件名/元数据/正文的真实姓名、班级、学号必须脱敏或记录决议
- 试卷密封线的空白「姓名/学号」栏是原卷模板，保留
- SQL 例题里的示例班级名等**非身份**命中，复核后记 notes 保留

## 八、跨设备注意事项

- 本工具路径自定位（向上扫描 `apps`+`学科资料`），克隆到任何位置都能跑；
  但**保持包在 `apps/tools/material_converter/`**，文档与 CI 引用以该路径为准
- Windows：LibreOffice 默认安装路径自动识别；绿色版请设 `MMD_SOFFICE`
- `.cache/glm4v.env` 与 `.venv/`、`apps/tools/material_converter/.work|/.ai_jobs/`
  均 gitignored——换设备需重建（glm4v.env 别提交）
- 中断恢复：转换天然幂等（重跑跳过已入库）；视觉转写看 `_vision_results.jsonl` 行数

## 九、故障排查

| 症状 | 处理 |
|---|---|
| `LibreOffice doc->docx failed` | 设 `MMD_SOFFICE` 指向 soffice 可执行文件 |
| `soffice=yes` 但 doc 仍失败 | 杀掉残留 soffice 进程；删 `.cache/lo_profile` 重试 |
| PNG 大批 error 且 reason 为空 | 升级到含 image-only 分支修复的版本（fmt 点号问题）|
| 视觉转写全 reject | 看 `_vision_results.jsonl` 的 `why` 字段；api-error 检查 key/网络 |
| validator 报 title 不一致 | 数字型标题需引号（YAML 会把 `000` 解析成整数）|
| matplotlib 缓存目录警告 | 设 `MPLCONFIGDIR`（CLI 已自动指到 `.cache/mpl`）|

## 十、回滚

任何批量操作前先备份：

```bash
tar czf .cache/knowledge_backup_$(date +%Y%m%d_%H%M).tar.gz apps/scut-senior/knowledge
# 回滚：
tar xzf .cache/knowledge_backup_<时间戳>.tar.gz
```

## 十一、相关文件

- SOP：`apps/scut-senior/docs/MATERIAL_TO_MARKDOWN_SOP.md`
- 技能卡：本目录 `SKILL.md`（已登记 `SCUT_SKILL及模版/Summary_Skill.md`）
- 批次审核记录：`apps/scut-senior/docs/review_artifacts/2026-08-22-agent-batch-review.md`
- 迭代记录：`apps/scut-senior/ITERATION_6_STATUS.md`
