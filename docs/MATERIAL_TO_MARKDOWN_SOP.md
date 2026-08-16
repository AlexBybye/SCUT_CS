# SCUT 老学长 V3 资料转 Markdown SOP

版本：1.5

基座：`docs/PLAN-1.md` v1.11（2026-08-16）

适用对象：资料 A、资料 B、资料贡献审核者

性质：重复执行的资料处理规范，不包含应用切块、索引或问答代码

> 1.5 修订：转换前先做轻量去重；误放到其他学科目录的重复件不按错误目录入库，答案版已完整包含题面且无答案版没有新增知识时只保留答案版。1.4 的排除项、轻量验证和 1.3 的全链路身份脱敏门禁继续生效。

## 1. 文档效力

本 SOP 只把 `PLAN-1` 已确认的资料转换要求改写为可执行步骤，不新增产品范围或工程防御。

- 本 SOP 与 `PLAN-1` 冲突时，以 `PLAN-1` 为准；
- `docs/tools.md` 只可作为工具能力参考；其中与 `PLAN-1` 冲突的复杂 manifest、哈希、排期或质量体系不采用；
- 工具、Skill 或 AI 的输出都不是最终结论，最终是否入库由人工审核决定；
- 学生／贡献者姓名、班级、学号的脱敏是强制发布门槛，不能用工具转换成功或内容审核通过代替；
- 不制定日历排期，以单文件完成和单课程闭环为单位推进。

## 2. 目标与完成定义

除人工事先决定不处理的文件外，所有候选学习资料都统一尝试转换成 Markdown。

以下资料不属于学科 Markdown 候选：

- `你需要知道的/` 下的 SRP 教程、结题报告和相关经验材料；
- 大学物理实验／大物实验报告、实验模板及实验合辑（大学物理理论课复习资料不在此排除项内）。

它们如被隐私扫描命中，仍须清理源文件名、正文、嵌图和元数据中的学生／贡献者姓名、班级、学号等身份信息，但不写入 `knowledge/` 或课程 manifest，不进入插件粗转、规范化、`pending`、`passed` 等学科转换统计。已经生成的插件粗稿只作为待清理中间产物，不继续规范化。

一份资料只有同时满足以下条件，才算完成转换交付：

1. 原文件没有被转换中间产物覆盖；拟公开工作树中的源文件若含学生／贡献者身份信息，已经由渲染核验后的脱敏版替换，未脱敏原件只可留在仓库外的本地隔离区；
2. 已生成符合本 SOP 的 Markdown；
3. 必要的图片资产和审核中间产物已落到规定目录；
4. `manifest.csv` 已填写最小字段；
5. 存在可靠 page、slide、question 或 heading 定位时能够回到原件；没有可靠 locator 时已记录退化状态，只保留资料名或标题且不补造精确定位；
6. 已由人工对照原件审核；
7. 文件名、Markdown 正文、frontmatter/title、assets 文件名、manifest 和拟公开 review artifacts 已按本 SOP 完成学生／贡献者身份脱敏，并检查 DOCX/PDF 可见属性及作者、最后修改者等元数据；
8. 状态已经明确为 `passed`、`needs_fix` 或 `rejected`。

`passed` 只表示资料内容审核通过。转换结果还必须通过 GitHub PR 人工合并到主分支；只有主分支中状态为 `passed` 的固定版本，才可以由华为云后端拉取并构建 candidate corpus。

## 3. 角色与课程主责

| 负责人 | 首批课程主责 | 格式专项 |
|---|---|---|
| 资料 A | 工数 I、概率论、离散数学、英语、信息安全、大物上、计算机科学概论 | PDF、扫描页 OCR、公式、表格 |
| 资料 B | 工数 II、线性代数、C++ 上及下 | DOCX、PPTX、旧 DOC、旧 PPT |

协作规则：

- 一门课程只有一名主负责人，负责清点、转换、返工和问题闭环；
- 计算机科学概论归资料 A，其旧 PPT 由资料 B 提供转换方案并重点复核；
- 全仓其余课程清点完成后，仍按“整门课程只归一人”分配，不拆分单门课程；
- 资料 A、资料 B 可以互相提供格式处理方案，但不能因此模糊课程主责；
- 修复后的高风险资料由另一位资料负责人交叉复核；
- 通用模型知识补充、chunk、向量、检索和回答均由应用代码负责，不属于资料转换任务。
- 项目不建设、审核或维护具体 Bilibili 视频资产；视频或字幕不按本 SOP 转成课程证据。匿名搜索入口只由应用运行时根据聚焦词固定生成，与资料转换流程无关。

## 4. AI 和工具的使用边界

AI、OCR 和文档工具可以用于：

- 识别文字；
- 转写公式、表格和代码；
- 恢复标题层级和阅读顺序；
- 生成排版规范的 Markdown；
- 提出疑似题目边界，供人工确认。

AI 和工具不得：

- 总结、缩写或解释原资料；
- 补写缺失内容；
- 根据常识修正原文；
- 擅自修改公式、数字、单位、术语或代码；
- 在没有可靠定位时猜测页码、幻灯片或题号；
- 把工具输出直接标为 `passed`。

如果原资料本身疑似有错，忠实保留原内容，在 `notes` 中说明，不能静默改正。

### 4.1 VS Code 插件的限定用途

本机已安装的 VS Code `Markdown to Word` 插件同时提供 Word → Markdown 功能。它只用于生成第一版粗稿，不替代 Docling、LibreOffice、OCR、定位补录或人工审核。

- 插件标识为 `markdowntoword.markdown-to-word`；`method` 记录实际使用的插件版本，不把当前安装版本当成永久约定；
- 插件实际 Word 主链只可靠接收 DOCX。旧 DOC 必须先由 LibreOffice 转为 `converted.docx`，同时生成固定 `rendered.pdf`，再对 staging 中的 DOCX 做粗抽取；
- 插件只能处理复制到 `review_artifacts/<source_id>/staging/` 的副本，禁止直接对 `学科资料/` 原目录执行单文件或批量转换；
- 插件生成的同名 Markdown、`*_debug.html` 和临时 `images/` 都是审核中间产物，不是规范知识文件；
- 插件可能重排标题、列表、代码和空白，也可能遗漏图片、公式或复杂表格。显示“转换成功”只表示粗稿文件已生成，不表示内容完整，更不表示可以 `passed`；
- 插件不得改变隐私门槛：staging 仅限本地审核，任何含未脱敏学生／贡献者身份信息的粗稿、图片或调试 HTML 均不得进入 `knowledge/`、公开分支或 PR。

## 5. 总流程

```text
清点文件和课程归属
→ 检查并处理文件名、正文和文档元数据中的学生／贡献者身份信息
→ 判断是否允许处理
→ 在 manifest 建立 pending 记录
→ 将允许处理的文件复制到隔离 staging
→ 按格式选择转换路径并生成粗稿
→ 生成 Markdown、assets 和必要审核产物
→ 写入 page / slide / question / heading 定位
→ 执行工具预检与 OCR 告警
→ 人工对照原件审核并再次执行隐私检查
→ passed / needs_fix / rejected
→ passed 转换结果通过 GitHub PR 人工合并主分支
→ 华为云拉取固定提交并构建 candidate
→ 验证通过后才可切换 active
```

任何一步发现问题，都先保留原件和当前产物，再通过 `notes` 记录，不另建复杂状态体系。

## 6. 单文件操作步骤

### 步骤 1：清点与归属

1. 确认原始文件路径和格式；
2. 如果文件名直接包含学生／贡献者姓名、班级或学号，直接按“学科名 + 编号”重命名，例如 `计算机科学概论-01.docx`；编号只用于去身份化和区分文件，不复用原学号。压缩包内部成员名、导出目录名和插件生成的派生文件名适用同一规则；
3. 如果 `original_path` 自身仍会泄露上述身份信息，必须先完成重命名，再把新路径写入 manifest；不得把泄露身份的旧路径写入 manifest、公开分支或 PR；
4. 按 `PLAN-1` 当前课程范围确认所属课程，使用课程注册表中的规范 `course_id`，不自行创造别名；
5. 确认该课程的主负责人；
6. 按当前 manifest 约定分配 `source_id`；具体命名和变更规则由迭代 0 的资料契约冻结，本 SOP 不另定算法；
7. 在生成新粗稿前做轻量去重：同一资料误放到其他学科目录时按正文实际课程归属，只处理一份规范来源；答案版完整包含题面且无答案版只是其严格子集、没有新增知识时，只转换答案版。被跳过的重复件不分配 manifest 记录，不计入规范化 Markdown 数；
8. 检查 DOCX/PDF 的可见属性以及作者、最后修改者等元数据；发现学生／贡献者姓名、班级或学号时，先在本地隔离环境中完成脱敏；
9. 在 `manifest.csv` 建立记录，状态设为 `pending`；
10. `document_role` 或 `year` 无法从原件确定时留空，不推测。

文件重命名是 manifest 建立前的隐私预处理，不改变课程知识正文。新路径确定后，转换工具不得覆盖源文件；但身份脱敏不受“源文件只读”保护：如果拟公开工作树中的源文件正文或元数据仍含上述身份信息，必须先在仓库外保留隔离工作副本，再用已完成全文搜索、元数据检查和渲染核验的脱敏版替换拟公开文件。未脱敏原件不得继续留在拟公开工作树中。

如果姓名、班级或学号是在转换途中才被发现，立即停止当前文件的后续处理，并同步清理已经生成的 staging 副本、Markdown 粗稿、`*_debug.html`、图片／assets 文件名、manifest 字段和其他派生物；不得只修最终 Markdown。清理完成并重新检查后，才允许继续转换。

普通删除或重命名不能清除 Git 历史中的身份信息。发现身份信息已经进入提交历史时，当前转换先保持 `needs_fix`，另行取得历史重写和远端强制更新授权后处理；不得把“工作树已删除”描述成“历史已清除”。

### 步骤 2：准入判断

出现以下情况时，不进入正常转换主链：

- 文件加密且无法正常读取；
- 来源不明；
- 是否包含个人信息无法确认；
- 学生／贡献者姓名、班级或学号尚未完成脱敏；
- 不适合公开处理或公开入库；
- 需要破解加密才能读取；
- 必须执行宏、嵌入脚本或其他主动内容才能打开；
- 只能通过未经允许的第三方云服务处理。

处理方式：

- 不破解加密；
- 不执行宏或嵌入脚本；
- 不默认上传第三方云解析；
- 能在不改变课程知识内容的前提下完成身份脱敏时，先记为 `needs_fix`，脱敏后重新人工审核；
- 无法可靠脱敏或无法确认是否仍有上述身份信息时，记为 `rejected`，并在 `notes` 写明人工裁决原因；
- 未完成脱敏的资料不得进入 `knowledge/`，不得标为 `passed`。

本隐私规则只针对学生／贡献者身份。课程正文中的历史人物、学者、理论提出者等姓名属于知识内容，不按本规则删除。

本 SOP 不定义“难以辨认”的自动阈值，也不通过字符重合度决定准入。可辨认性和最终质量由人工审核裁决。

### 步骤 3：按格式选择转换路径

| 原格式 | 主处理路径 | 定位方式 | 必要说明 |
|---|---|---|---|
| Markdown / TXT | 整理编码和标题层级 | heading | 没有可靠页码时不得补造 page |
| 原生文本 PDF | Docling 等主提取工具转 Markdown | page | 保留页面切换标记 |
| DOCX | 在隔离 staging 中用 VS Code `Markdown to Word` 插件生成粗稿，再人工规范化；明显异常时使用 Docling 等工具辅助 | 固定 PDF 的 page，或 heading | 需要稳定页码时先渲染固定 PDF；否则只用 heading；插件粗稿不能直接入库 |
| PPTX | Docling 等主提取工具转 Markdown | slide | 保留原幻灯片编号 |
| 扫描 PDF / 图片页 / 手写页 | PaddleOCR 等 OCR 后人工校正 | 扫描 PDF 用 page；独立图片有可靠页序时用 page，否则用 heading 或资料名 | OCR 分数只作预警，不为独立图片补造页码 |
| 旧 DOC | LibreOffice 在隔离 staging 中转 `converted.docx`，同时渲染固定 `rendered.pdf`；再用 VS Code 插件生成粗稿并人工规范化 | 固定 `rendered.pdf` 的 page | 插件不直接处理旧 DOC；原 DOC 仍是来源身份，不被转换文件替代 |
| 旧 PPT | LibreOffice 转 PPTX，同时渲染 PDF，再提取 Markdown | 原 slide | 转换产物只用于提取与审核 |

异常辅助规则：

- 只有主提取结果明显异常时，才使用 Tika 或 Unstructured 辅助核对是否遗漏大段文本；
- 不要求每份资料并行运行多个解析器；
- MinerU 或相关 Skill 只用于已经确认允许外部处理的样本效果比较；
- 未经确认，不把全仓资料上传到外部服务；
- 无论采用什么工具，原文件都保持只读。

#### VS Code Word → Markdown 粗抽取步骤

1. 在文件名和原始路径完成身份脱敏后，把允许处理的 DOCX 复制到 `review_artifacts/<source_id>/staging/`；旧 DOC 则先在这里生成 `converted.docx` 和 `rendered.pdf`；
2. 只对 staging 中的 DOCX 使用“转换为Markdown”；不在原资料目录使用插件默认的同目录输出；
3. 将插件输出视为 `rough.md`，同时保留本次审核实际用到的调试 HTML 和临时图片，但它们不得进入 `knowledge/`；
4. 对照原件恢复正确阅读顺序、标题、列表、公式、表格、代码和图片，不根据常识补写；
5. 把需要保留的知识图片迁移到 `knowledge/<course_id>/assets/<source_id>/`，使用不含学生／贡献者身份且稳定的文件名，并重写 Markdown 引用；
6. 补齐规范 frontmatter 和可靠 locator；无法维护精确定位时使用 `locator_type: none`，不得猜测；
7. 完成人工审核后，确保 `knowledge/` 中没有插件的 `*_debug.html`、时间戳图片目录、同目录粗稿或其他临时产物。staging 中不再需要的含身份中间产物按本地审核策略清理，不提交 Git。

### 步骤 4：生成规范化 Markdown

Markdown 必须：

- 忠实保留原文阅读顺序；
- 保留合理的标题层级；
- 公式使用 LaTeX；
- 代码使用 fenced code block；
- 简单表格使用 Markdown；
- 复杂表格可以使用 HTML；
- 无法可靠文字化但包含知识信息的图片保存到 `assets/`，并在 Markdown 中引用；
- 不得加入原文没有的总结、解释、纠错或补全文字。

#### 最小 frontmatter

```yaml
---
source_id: linear-algebra-001
course_id: linear_algebra
title: 矩阵与线性方程组
original_file: 学科资料/线性代数/复习资料.doc
document_role: note
year:
locator_type: page
---
```

要求：

- `source_id` 与 manifest 完全一致；
- `course_id` 使用课程注册表中的规范 ID，不在单文件中自造别名；manifest 继续使用当前契约规定的 `course` 列；
- frontmatter 的 `title` 必须与 `manifest.title` 一致；学生端资料名称的事实源是 `manifest.title`；
- `original_file` 能回到仓库中的原始来源；
- `document_role`、`year` 不确定时留空；
- `locator_type` 只写实际能够维护的 `page`、`slide` 或 `heading`；没有可靠精确定位时明确写 `none`。

应用侧会把 manifest/frontmatter 规范化为 `course_id` 和 `source_title`；frontmatter 以 `course_id` 为规范字段，旧 `course` 字段只用于兼容既有资料。资料人员不手工维护 chunk 字段。`source_title` 固定来自 `manifest.title`，不由回答模型生成。

### 步骤 5：写入来源定位

#### PDF 和固定版 Word

```markdown
<!-- page: 12 -->

## 矩阵的秩

正文……
```

- 每次进入新页时写 page 标记；
- DOC/DOCX 只有存在固定渲染 PDF 时才能引用 page；
- 旧 DOC 的页码始终指本次审核使用的固定 `rendered.pdf`；
- 没有固定页码依据时退化为 heading。

#### PPT / PPTX

```markdown
<!-- slide: 8 -->

## 进程调度

正文……
```

- 每张幻灯片保留原 slide 编号；
- 旧 PPT 优先使用原幻灯片号，不用转换后 PDF 页码替代学生端 slide 定位。

#### Markdown / TXT

- 使用 H1-H6 标题层级形成 heading 路径；
- 没有原始页码时只提供标题定位；
- 不为了显示更精确而伪造页码。

#### 无可靠精确定位

- frontmatter 与 manifest 均填写 `locator_type: none`；
- 正文可以保留合理标题，但不能补造 page、slide 或 question；
- 学生端后续只能退化显示资料名或标题。

#### 历年题

```markdown
<!-- page: 12 -->

<!-- question: 2023-final-A-Q5 -->

### 第 5 题

题目正文……
```

规则：

- `question` 标记在题目开始处出现；
- 保留原资料中的题号；
- 工具或 AI 只能提出题目边界候选；
- 资料人员必须对照原卷确认边界和原始题号；
- 跨页题继续写新的 page 标记，同时保持当前 question 归属；
- 下一题开始时再写新的 question 标记；
- 未经人工确认的自动拆题结果不能标为 `passed`。

### 步骤 6：执行 OCR 预检

默认 OCR 告警阈值为 `0.85`。

- 页级或区域置信度低于 `0.85`：标记 `ocr_warning`，加入重点人工检查；
- 高于或等于 `0.85`：不代表自动通过；
- 低于 `0.85`：不代表自动拒绝；
- 不同 OCR 引擎的分数不能直接横向比较；
- 最终结论仍由人工对照原件给出。

不得根据低置信 OCR 内容用语言模型强行补全。看不清或无法确认时，在 `notes` 记录并进入 `needs_fix` 或由人工决定 `rejected`。

### 步骤 7：人工审核

普通原生文本 PDF／DOCX 采用一次自动全量结构、链接和隐私检查，再人工抽查：

1. 开头；
2. 中间；
3. 结尾；
4. 所有工具告警位置；
5. 至少一个具有代表性的公式、表格、代码或图片特殊块（如存在）。

不得为同一未变化生成物重复做全页视觉检查。只改文件名或文档元数据且正文、关系和媒体 payload 已证明逐项未变时，可以用包结构／payload 对比代替重复渲染。OCR、旧 DOC、旧 PPT、身份信息嵌图和已经出现明显错序／遗漏的文件属于高风险项，每个文件都要执行上述审核，并按问题位置加查；不要求无差别逐页复核。历年题还要检查：

- 题目边界；
- 原始题号；
- page/slide 与 question 的组合；
- 跨页题是否保持同一 question 归属。

使用 VS Code 插件生成粗稿的每个 Word 文件还要逐一检查：

- 标题和列表是否被启发式重排；
- 代码缩进、换行和 fenced code block 是否正确；
- 公式、复杂表格、图片和嵌入对象是否遗漏或改变含义；
- 插件是否在回退路径中忽略图片；
- `knowledge/` 是否只保留规范化 Markdown 和稳定 assets，不含 debug HTML、粗稿或时间戳目录。

人工审核必须回答：

- Markdown 是否基本完整保留原内容和顺序；
- 公式、数字、单位、代码和表格是否没有影响知识含义的明显错误；
- 已存在的 page、slide、question 或 heading 是否能回到原件；没有可靠 locator 时是否正确退化为资料名／标题且没有补造；
- 是否没有 AI 擅自补写、概括、纠错或补全；
- assets 链接是否有效；
- 课程归属是否正确；
- 文件名、Markdown 正文、frontmatter/title、assets 文件名、manifest 和拟公开 review artifacts 的路径是否已经移除学生／贡献者姓名、班级和学号；
- DOCX/PDF 的可见属性以及作者、最后修改者等元数据是否已经检查并完成上述身份脱敏；
- 是否保留了课程正文中的历史人物、学者等知识性姓名，没有把隐私清理扩大成删除课程知识。

字体、换行或少量不影响含义的排版差异，可以在 `notes` 说明后通过。

### 步骤 8：给出状态

状态只允许四种：

| 状态 | 含义 | 后续动作 |
|---|---|---|
| `pending` | 尚未完成人工审核 | 继续审核，不得入库 |
| `passed` | 人工确认内容具备入库资格 | 通过 GitHub PR 人工合并；不能直接修改 candidate/active |
| `needs_fix` | 存在可修复问题 | 修复后重新进入人工审核 |
| `rejected` | 人工决定不进入知识库 | 在 `notes` 写明原因 |

不得增加“基本通过”“低质量通过”等重叠等级。

修复后由人工判定为高风险的资料，由另一位资料负责人交叉复核后再决定是否 `passed`；不额外建立自动“高风险”分类器。

### 步骤 9：落盘和更新 manifest

最小目录：

```text
knowledge/
├── manifest.csv
└── <course_id>/
    ├── <source_id>.md
    └── assets/<source_id>/...

review_artifacts/
└── <source_id>/
    ├── staging/                 # 本地隔离粗抽取；不提交 Git
    │   ├── input.docx 或 converted.docx
    │   ├── rough.md
    │   ├── rough_debug.html
    │   └── images/...
    ├── converted.docx 或 converted.pptx
    └── rendered.pdf
```

`review_artifacts` 只保存实际生成并用于审核的中间产物，不要求为不存在的产物创建空文件。`staging/` 是本地隔离区，不进入 Git、公开分支或 PR；确需公开提交的 review artifact 必须使用不含学生／贡献者姓名、班级、学号的路径，并先检查其可见内容和文档元数据已经完成同类脱敏。

`manifest.csv` 只保留以下字段：

```text
source_id
course
title
original_path
format
document_role
year
output_md
locator_type
method
ocr_used
ocr_confidence
ocr_warning
status
reviewer
notes
```

填写规则：

- 不擅自加入 SHA-256、bbox、复杂质量分、向量或 chunk 字段；
- `output_md` 必须指向实际 Markdown；
- `method` 记录本次实际采用的主转换路径；
- 使用 VS Code 插件时，`method` 记录实际版本，例如 `vscode-markdown-to-word@0.1.67`；旧 DOC 记录实际链路，例如 `libreoffice+vscode-markdown-to-word@0.1.67`，版本号以执行时安装版本为准；
- 没有使用 OCR 时如实填写 `ocr_used`；
- `ocr_confidence` 只保存工具实际提供且可解释的结果；
- `reviewer` 填写完成人工审核的人；
- 所有拒绝、返工或忠实保留的疑似原文错误写入 `notes`；OCR 低置信优先使用 `ocr_confidence` 和 `ocr_warning`，只有需要补充上下文时再写 `notes`。
- manifest 的 `original_path`、`title`、`notes` 和其他拟公开字段不得残留学生／贡献者姓名、班级或学号；原路径泄露时先重命名，再填写新路径。

### 步骤 10：仓库发布与应用构建交接

资料负责人只提交 `passed` Markdown、assets、manifest 和必要的审核产物，不生成：

- chunk；
- chunk ID；
- 向量；
- 题目检索索引；
- 课程包；
- 来源编号 `[S1]`；
- 回答或复杂 QA 产物。

发布顺序固定为：

```text
passed 转换结果
→ GitHub 分支和 PR
→ 维护者人工审核并合并主分支
→ 华为云拉取固定 commit
→ candidate 构建和校验
→ 验证通过后替换 active
```

资料负责人不能直接修改 candidate 或 active；PR 创建和 `passed` 状态都不等于已经对学生可检索。

应用构建会继续检查：

- `source_id` 存在且为 `passed`；
- course、title 与 manifest 一致；
- 已提供的 page、slide、question、heading 真实存在且顺序有效；没有可靠 locator 时只保留资料名或标题；
- `source_title` 能确定性取自 `manifest.title`。

candidate 校验失败时不能替换 active index。相关失败项经人工核对和修复后重新走审核，不能由程序自动把资料改成 `passed`；具体返工协作接口由迭代 0 契约确定。

## 7. 用户贡献资料的附加流程

用户主动提交临时材料后，同样使用本 SOP 转换和审核。提交动作必须来自有效 GitHub 登录会话。进入转换前必须完成：

1. 用户确认课程；
2. 用户说明来源；
3. 用户确认有权公开分享；
4. 用户确认不含个人敏感信息。

随后：

```text
预检和转 Markdown
→ 用户人工预览转换结果
→ 已确认 GitHub App／机器人时在隔离分支创建 PR；否则进入维护者待处理队列并手动创建 PR
→ 维护者按本 SOP 审核
→ 人工合并
→ candidate 构建与验证
→ 验证通过后进入 active index
```

边界：

- PR 不自动合并；
- PR 创建不等于进入知识库；
- 公开仓库 PR 可能长期公开，提交前必须向用户明确提示；
- 默认使用机器人和不透明贡献 ID；公开展示贡献者 GitHub login 前另行取得同意；
- GitHub App／机器人只使用目标仓库最小 Contents 与 Pull Requests 权限，不使用用户 OAuth token，服务端凭证不进入数据库或日志；
- 不适合公开的教材、课件、个人信息、密钥或来源不明材料不能走自动 PR；
- PR 描述只包含课程、来源类型、原格式、页数、OCR 预检、贡献 ID 和审核清单，不写 API Key、完整私密载荷或不必要个人信息；
- 被拒绝、待审、私有或过期材料不能被其他用户检索；
- 普通临时原件仍按 7 天清理；主动提交后生成的必要待审附件／图片副本最多保留 30 天；
- 合并后的公开 Markdown/manifest 按仓库规则管理。

## 8. 每份资料的审核清单

以下清单是可选操作模板，用于减少人工漏检；它不属于必须提交的独立 QA 产物，也不扩展最小输出契约：

```markdown
### <source_id> 审核记录

- [ ] 课程归属已确认
- [ ] 原文件保持只读
- [ ] 含学生／贡献者姓名、班级或学号的文件名已先改为“学科名 + 编号”，original_path 使用脱敏后的新路径
- [ ] Markdown 正文、frontmatter/title、assets 文件名、manifest 和拟公开 review artifacts 路径已移除学生／贡献者姓名、班级和学号
- [ ] DOCX/PDF 可见属性以及作者、最后修改者等元数据已检查并完成身份脱敏
- [ ] 课程正文中的历史人物、学者姓名得到保留
- [ ] 来源和公开处理条件已确认
- [ ] 未破解加密、未执行宏或嵌入脚本
- [ ] 已选择正确格式路径
- [ ] VS Code 插件只在隔离 staging 中生成粗稿，未直接处理原资料目录（如适用）
- [ ] 旧 DOC 已先转 converted.docx 和 rendered.pdf，插件只处理 staging 中的 DOCX（如适用）
- [ ] frontmatter 与 manifest 一致
- [ ] 内容顺序和标题层级基本完整
- [ ] 公式、数字、单位、代码、表格已检查
- [ ] assets 已保存且链接有效
- [ ] knowledge 中没有插件 debug HTML、粗稿、时间戳图片目录或其他临时产物
- [ ] 已提供的 page / slide / question / heading 能回到原件；无可靠 locator 时已正确退化且未补造
- [ ] 历年题题界和原始题号已人工确认（如适用）
- [ ] OCR < 0.85 的位置已重点检查（如适用）
- [ ] AI 没有总结、补写、解释或纠错原文
- [ ] 开头、中间、结尾和全部工具告警已核对
- [ ] 高风险返工已由另一位负责人复核（如适用）
- [ ] manifest 状态、reviewer 和 notes 已更新

最终状态：pending / passed / needs_fix / rejected
```

## 9. 与资料流程有关的尚待确认项

以下事项继续由 `PLAN-1` 第 20 节和对应代码迭代决定，资料人员不得自行选型：

- GitHub App 的最终实现；没有 App 时使用维护者待处理队列；
- 华为云对象存储和离线任务系统的最终选型；

这些事项不影响人工忠实转换和审核，但会影响贡献 PR 或附件存放的具体操作方式。

## 10. 禁止事项

资料转换阶段不做：

- SHA-256 血缘体系；
- bbox 和复杂 Canonical Element；
- 复杂 JSON Schema；
- chunk 和向量字段；
- 多级自动质量评分；
- 每份资料的复杂 QA；
- 每份资料的多解析器竞赛式跑分；
- 默认上传第三方云解析；
- 直接在 `学科资料/` 原目录运行 VS Code Word → Markdown 单文件或批量转换；
- 把插件“转换成功”或 validator 通过当成人工内容验收；
- 未完成学生／贡献者身份脱敏就写入 `knowledge/`、标记 `passed` 或提交公开 PR；
- AI 自动修正文义；
- 未经人工审核自动发布知识库。

## 11. SOP 完成标准

一次资料批次只有满足以下条件，才可交付给应用负责人：

- 批次中每份候选资料都有四种状态之一；
- 只有已经通过 PR 人工合并到 GitHub 主分支且状态为 `passed` 的资料位于待构建集合；
- manifest、Markdown、assets 和审核产物路径有效；
- 人工审核没有发现影响知识含义的大段遗漏、重复或错序；
- 数字、公式、单位、代码和表格没有明显语义错误；
- 抽查已有定位能够回到原件；没有可靠 locator 的资料正确退化且没有补造；
- AI 没有擅自补写或改写；
- 学生／贡献者姓名、班级、学号已经从文件名、Markdown 正文、frontmatter/title、assets 文件名、manifest 和拟公开 review artifacts 路径中移除；DOCX/PDF 可见属性及作者、最后修改者等元数据已经检查；课程正文中的历史人物、学者姓名未被误删；
- VS Code 插件仅用于隔离 staging 粗抽取，最终知识目录不含 debug HTML、粗稿、时间戳图片目录或其他插件临时产物；
- OCR `< 0.85` 的位置已全部进入重点人工复核；
- 历年题的题目边界和题号已经人工确认（如适用）；
- 尚未解决的问题全部留在 `needs_fix` 或 `rejected`，没有带病标为 `passed`。
