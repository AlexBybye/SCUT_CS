# 学科资料 → Markdown 转换工具（material_converter）

依据 `apps/scut-senior/docs/MATERIAL_TO_MARKDOWN_SOP.md` v1.7 与 `PLAN-1.md` v1.11。
把散落在各批次里的转换逻辑固化为一个可重复、增量、可测的工具包，供后续大一／大二／大三
课程接入以及“各科新资料上传后增量入库”反复使用。

> 一句话：**在 `学科资料/` 下新增或替换文件后，跑一次本工具，它就按 SOP 生成/跳过对应
> Markdown + 图片资产 + manifest 记录（状态一律 `pending`），并自动过 validator。**

## 前置依赖

- Python 3.11+（建议 3.13/3.14）
- LibreOffice（处理旧 `.doc`//`.ppt` 与 WMF/EMF 公式预览图），可用以下任一：
  - 已安装到 `/Applications/LibreOffice.app` 或 `~/Applications/LibreOffice.app`；
  - 环境变量 `MMD_SOFFICE=/绝对路径/soffice`；
  - 或已放在 `repo/.cache/LibreOffice.app`。

### 首次准备

```bash
cd apps/tools/material_converter
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
# 校验
./.venv/bin/python -m material_converter.main --dry
```

## 常用命令

```bash
cd apps/tools/material_converter
V=.venv/bin/python

$V -m material_converter.main                      # 全量增量：把 学科资料/ 全部课程中未入库、且非重复的候选转成 pending
$V -m material_converter.main --course 线性代数     # 只处理某门课（参数用 学科资料/ 文件夹名）
$V -m material_converter.main --file 学科资料/概率论/往年卷/xxx.docx   # 单文件
$V -m material_converter.main --dry                # 只报告，不写文件、不动 manifest
$V -m material_converter.main --validate           # 转换后自动跑 corpus validator
```

行为要点：

- **增量**：`original_path` 已在 `knowledge/manifest.csv` 的候选一律跳过（不重转、不覆盖）。
- **去重**（SOP 步骤 1.7）：字节级重复、跨目录同名内容重复、以及「无答案版 ⊂ 答案版」的
  子集件都会自动判去重并给出原因；已入库规范件优先。
- **隐私前置**：文件名含身份信息需先在 `学科资料/` 里 `git mv` 脱敏后再跑；文档元数据
  中匹配 `PRIVACY_IDENTITY_PATTERNS` 的 author/creator 会被就地清空；正文中的学号/班级
  模式会写入 `notes` 警告，试卷密封线模板字段自动标注为非个人数据。
- **状态**：所有 AI 生成结果一律 `pending`，`reviewer` 留空。人工对照原件审核后
  手工改为 `passed` 并填 `reviewer`，再走 PR 流程。

## 新增课程（大二／大三课程接入流程）

1. 在 `apps/scut-senior/packages/contracts/v1/courses.json` 注册课程（`course_id`/`display_name`/
   `aliases`/`repository_paths`），并确认 `is_open`/`fixture_available`；
2. 把资料放入 `学科资料/<文件夹名>/`（目录名即 `repository_paths` 的 `学科资料/` 后缀）；
3. 运行 `--course <文件夹名> --validate`。工具自动：读 courses.json、分配 source_id 前缀
   （`course_id.replace('_','-')`，已有 10 门用 `LEGACY_SOURCE_PREFIX` 保留历史前缀）、
   生成知识目录（既有目录优先，默认 `course_id`）、写入 manifest；
4. 应用侧 corpus builder 需要 `courses.json` 里有该课程才能通过 validator —— 所以**先注册课程**。

## 输入→产出映射

| 原格式              | 处理                                                            | 定位         | method 记录                           |
| ------------------- | --------------------------------------------------------------- | ------------ | ------------------------------------- |
| DOCX                | 本地 OOXML 提取 + omml2latex；MathType/OLE 公式→PNG 预览图回退 | heading      | local OOXML extraction + omml2latex… |
| 旧 DOC              | LibreOffice→docx 后同上                                        | heading      | libreoffice doc->docx…               |
| PPTX                | python-pptx 逐页                                                | slide        | python-pptx slide extraction          |
| 旧 PPT              | LibreOffice→pptx 后同上                                        | slide        | libreoffice ppt->pptx…               |
| 原生文本 PDF        | PyMuPDF 分页文本                                                | page         | pymupdf text-layer…                  |
| 无文本层 / 乱码 PDF | 整页渲染 JPEG 资产（无 OCR）                                    | page         | pymupdf page rendering…              |
| TXT/CPP/MD/图片     | 规范化 / 单图资产                                               | heading/none | …normalization                       |

## 常见问题

- **`LibreOffice doc->docx failed`**：没找到 soffice。装 LibreOffice 或设 `MMD_SOFFICE`；
  旧 `.doc`//`.ppt` 与 WMF/EMF 公式预览图都依赖它。
- **结果全是 `pending`**：正确。AI 输出不能标记 `passed`（SOP §4），需人工审核。
- **敏感文件**：加密 zip 不会破解，也不入链；如需处理请先解密并核对身份信息。
- **占位符**：`md` 里的 `{ASSETS_DIR}` 在生成时替换为实际相对路径 `assets/<sid>`。

## 与本工具相关的其它职责

- 应用侧 chunk / 向量 / 检索 / 题目索引不在本工具职责内（SOP §5 步骤 10）。
- `course` / `title` / `source_title` 事实源是 manifest；本工具不手工维护 chunk 字段。
- 发布顺序：`pending → 人工审核 → passed → GitHub PR 人工合并 → 华为云构建 candidate → 验证 → active`。

## 两段式：确定性抽取 + AI 归一化（重要）

按 `MATERIAL_TO_MARKDOWN_SOP.md`，转换是**AI 深度参与的**。`material_converter` 本身只做
**确定性结构抽取**（SOP 允许“工具可做”的部分：识别文字、恢复标题层级、转写原生 OMML 公式、
保留图片/表格、加 page/slide 锚点），**不包含 AI 语义归一化**。AI 负责的工作不在工具里：

- 扫描页/手写页 **OCR**（工具只整页渲染成 JPEG 图片，OCR 结论需人工决议）；
- **公式图 → LaTeX 转写**（MathType/OLE 预览图，工具仅保留为 PNG 预览，不猜写）；
- **阅读顺序/标题层级恢复**、**题目边界候选**（工具只给出简单正则候选）。

### AI 阶段工作流

```bash
cd apps/tools/material_converter
# 1) 导出需要 AI 的作业包（每文件一个目录，含公式图清单/OCR页清单/原文）
.venv/bin/python -m material_converter.main --emit-ai-jobs          # 或 --emit-ai-jobs <课程>
# 2) AI（或人工）逐文件回填：
#    .ai_jobs/<sid>/formulas.json  -> {image_name: "\\frac{...}{...}"}（能可靠识别的才填）
#    .ai_jobs/<sid>/notes.md       -> 追加到 manifest notes
#    （可选）OCR 结论写到 notes.md
# 3) 应用结果（替换公式图→LaTeX、删无用公式资产、追加 notes、保持 pending）
.venv/bin/python -m material_converter.main --finalize <课程或省略>
```

**AI 阶段守则（SOP §4）**：只能转写/恢复/提议，绝不总结、缩写、解释、纠错、补写或凭常识猜公式。
凡是不能与原件逐项对应的公式一律留下 PNG 预览并写 `notes`；状态保持 `pending`，由人工复核。
