# 迭代 6 退出记录（资料转换与工具沉淀）

状态：确定性抽取工具、AI 语义层钩子与可再生 skill 完成；首批 10 门知识库已补全，
新产出全部 `pending` 待人工对照原件审核，未进入 candidate / active。

进入日期：2026-08-22（Asia/Shanghai）

完成日期：2026-08-23（Asia/Shanghai）

> 本期不是应用功能迭代，而是**知识生产管线**：把此前用一次就丢的「学科资料 → Markdown」
> 逻辑固化为可重复、增量、可测的工具包，并重新审视既有 `passed` 记录的质量。
> 依据 `docs/MATERIAL_TO_MARKDOWN_SOP.md` v1.7 与 `docs/PLAN-1.md` v1.11 §2（首批 10 门）。

## 知识库补全结果

- `knowledge/manifest.csv`：195 行 = **22 passed + 173 pending**。
- 首批 10 门清点 194 个候选（不含 zips／图片），去重后新增/重做 171 份；含跨课程误放、
  「无答案 ⊂ 答案」子集、字节/内容重复三类去重（SOP 步骤 1.7）。
- 每门课 pending 数（含既有重做）：C++ 43 · 工数 I 23 · 工数 II 42 · 线性代数 18 ·
  概率论 18 · 大物上 11 · 计概 8 · 离散 6 · 英语 2 · 信安 1。
- 转换方法按格式记录在 `manifest.method`：DOCX（本地 OOXML + omml2latex；OLE 公式→PNG 预览）、
  DOC/PPT（LibreOffice 26.2 转换后同链）、PDF（原生文本分页 / 无文本层与乱码层整页渲染）、
  代码/笔记（fenced code / 规范化）。

## 既有 passed 记录的重审（对应“草率审核”问题）

- 发现工作树残留上次未提交的损坏产物（乱码正文、frontmatter 与 manifest 不一致），
  已恢复至 Git HEAD 后重新处理。
- `probability-theory-010`：原 passed 版仅把 243 个公式对象中的 97 个转为 LaTeX（约 128 个公式
  内容缺失），已用新管线整体重生成（139 OMML→LaTeX + 104 OLE→PNG 预览），回退 `pending`。
- 7 个文本层损坏（乱码）PDF：转换为整页图片并在 `notes` 注明。
- 全库资产链接校验 + 路径修正；`manifest`/frontmatter/locator 全量通过 corpus_validator。

## 隐私处理

- 文件名脱敏（`git mv`）：`大物上/速通指南-来自buguoshixc.md` → `大物上-速通指南01.md`；
  `wjq.txt` → `C++-07.txt`。
- 文档元数据脱敏（源文件就地替换，原件建议另行隔离）：`工数上期末.pptx`、
  `工数1~3章知识点及对应真题(1).pptx`（creator 王杭/杭 王）、`2023级工科数学分析下 A/B.pdf`（Chinois_Li）。
- 真实身份泄露修复：`cpp-006`（10.8测试.ppt）含姓名+班级+学号，输出 md 已删除、源 .ppt 已用
  去标识版重建、原件移至本地隔离；**Git 历史仍含旧版本，需另行授权 history rewrite**。
- 加密 zip（范围内科目 4 个）按准入判断不破解、不入链；待提供密码后另行处理。
- 试卷密封线上空白「姓名/学号」栏为原卷模板内容，予以保留；代码内 `"姓名："` 字符串与样例输出为程序/虚构数据，非身份信息。

## 工具沉淀（apps/tools/material_converter）

两段式转换，按 SOP §4 边界分权：

1. **确定性抽取**：OOXML/PDF/PPT 文本、标题层级、表格、图片、原生 OMML→LaTeX、
   page/slide/heading 锚点、manifest 记录、去重、隐私预处理。不含 AI。
2. **AI 语义归一化**：`--emit-ai-jobs` 导出作业包（`formulas.json`（公式预览图→LaTeX）、
   `ocr_pages.json`（整页图片待 OCR）、`source.md`）；`--finalize` 回填公式 LaTeX、删除
   无用公式资产、追加 notes，状态保持 `pending`（SOP 4.2）。
3. **人工审核** → `passed`（唯一入库状态）。

关键实现：

- `courses.py` 读 `packages/contracts/v1/courses.json` 驱动——新增课程零改码；
  `repo_root()` 向上扫描 `apps`+`学科资料` 标志目录定位仓库根（位置无关，修复了包被迁移后
  路径断裂的问题）。
- 增量幂等：已入库 `original_path` 跳过；优先识别已入库规范件（按哈希 / 核心词基线 /
  同目录前缀），字节/内容/无答案子集自动去重。
- 乱码文本层 PDF 自动回退整页图片；Obsidian callout 保留；`question:` 边界仅给候选并提醒人工确认。
- 守护：缺失 LibreOffice 时 DOC/PPT/矢量公式明确报错，不静默丢内容；`status` 一律 `pending`。

验证：`corpus_validator` 全量 **0 错误**；全量 dry-run `candidates=15 去重=15 converted=0`
（增量完全幂等）；`--emit-ai-jobs` 定位 46 个待 AI 文件；AI 冒烟：`--finalize` 把单个公式图
替换为 LaTeX，`validator` 仍 0 错误（测试产物已还原）。

## 验收清单

- [x] `knowledge/` 首批 10 门补齐；`manifest` 195 行，`corpus_validator` 0 错误
- [x] 既有 `passed` 重审与重点回退（probability-theory-010、乱码 PDF）
- [x] 隐私：文件名/元数据/正文身份处理；cpp-006 历史身份明确标注待授权
- [x] 工具包 `apps/tools/material_converter/`：README / SKILL.md / bootstrap.sh / requirements.txt
- [x] 技能登记：`SCUT_SKILL及模版/Summary_Skill.md`「本院开发」区新增 `material-to-markdown`
- [ ] 173 条 `pending` 人工对照原件审核（重点：OLE 公式 LaTeX 替换、题目边界、PPT 备注）
- [ ] cpp-006 Git 历史身份信息的历史重写授权
- [ ] 4 个加密 zip 提供密码后转（及文件名 `Note（来源MWX）.zip` 解包时同步脱敏）

## 遗留与边界

- AI 语义层未在本期执行批量**OCR / 公式图→LaTeX**：前者依赖 OCR 引擎（SOP 定位为后续迭代，
  见 `CODE_ITERATION_SOP.md` 迭代 8「图片 OCR 与复杂图片理解」），后者按 SOP 只能转能与
  原件逐项对应的公式，建模/视觉能力受限时留 PNG 预览并 `notes` 标注，交由人工。
- 未把任何 AI 产物直接标 `passed`；未手工构建 candidate（corpus_builder 有洁净树门禁，
  由后续提交再触发）。Bilibili 合成资源、chunk/向量/索引不属于本工具职责（SOP §5 步骤 10）。

## 基线

- 本机：LibreOffice 26.2.4（`apps/tools/material_converter/.work` 外的 `.cache/LibreOffice.app`）、
  Python venv（mammoth / python-docx / python-pptx / pymupdf / pyyaml / olefile）。
- 转换中间产物（`staging`、`.work/`、`.ai_jobs/`、`*_debug.html`）不进入 Git；`knowledge/`
  无插件调试产物。
