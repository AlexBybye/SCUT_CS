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

## 追加（2026-08-23）：全量课程注册 + 大二批次转化

### 课程注册表扩展（10 → 55 门）

- `packages/contracts/v1/courses.json` 新增 45 门，全部 `is_open=false, fixture_available=false`
  （注册≠开放：检索仅吃 `passed` 行，新课程在人工审核通过前不进入语料）。
- 覆盖：大二 15 门（数据结构/数字逻辑/计组/编译/算法/数据库/嵌入式/AI导论/智能算法/
  大物III（二）/电工学/电工实验/信号与通信/Java/Python）、大三及以上（操作系统/软工/计网/
  软测/计算方法/数学建模/图形学/移动开发/群体智能/信安数基/Web前端等）、思政通识
  （思修/马原/毛概/习概/近代史/国史）、大物实验（一）（二）（仅注册；PLAN-0 的语料排除不变）。
- 明确**不注册**（非课程）：优秀寒招资料模板、华工大一开学选拔考试资料、NUS人工智能研学资料、
  高中物理化学高度总结笔记（家教用）、雅思、通选课、IT前沿技术、人工智能入门：千方百智。
- 契约测试同步：`test_contract_assets.EXPECTED_COURSE_IDS` 扩展为 55 门有序清单；
  `test_registry` / `test_harness_registry` 计数断言更新并诚实化测试名；
  「信息安全数学基础」由“被排除名”改为正式课程（相应断言更新）。
  Python 全量 **522 passed**。

### 大二批次转化（14 门，全部 pending）

- 数据结构 35 · 数字逻辑 8 · 计算机组成原理 73 · 编译原理 56 · 算法设计与分析 43（另去重跳过 1）·
  数据库 6 · 嵌入式系统 21 · 人工智能导论 59 · 智能算法及应用 37 · 大学物理 III（二）20 ·
  电工学 9 · 电工实验 8 · 信号处理与通信基础 25 · Java 程序设计 1 —— 共 **380 行新增**。
- manifest 总量：**575 行 = 22 passed + 553 pending**；`corpus_validator` 全量 **0 错误**。
- 批次修复：
  - `soffice_convert` 惰性自解析（此前 main 的 `global SOFFICE` 只改了自身模块绑定，
    doc/ppt 链路会假性失败）;
  - image-only 分支 format 点号不一致导致空产出（`StopIteration` 被吞成空错误）;
  - 无答案子集匹配对无 `sid` 的普通文件 dict 取键崩溃（嵌入式目录触发）。
- 隐私：正文双扫描零学号命中；`database-001` class-label 命中经复核为 SQL 例题中的示例班级名，
  决议记入 notes 保留原文。
- 待办：553 条 pending 人工审核；`--emit-ai-jobs` 当前可导出 134 个 AI 归一化作业包
  （公式图→LaTeX / OCR 页），按 SKILL 流程回填后仍保持 `pending`。

## 追加（2026-08-23）：GLM-4V 公式视觉转写全量执行

### 管线与可靠性闸门

- 接入 `glm-4v-flash`（免费额度，凭证在 gitignored `.cache/glm4v.env`），新增
  `vision_worker.py`（转写）+ `propagate_vision.py`（哈希传播）。
- 三道闸：**三票多数决**（同图独立读三次，≥2 票一致才采纳）→ **确定性校验**
  （括号配平/无中文散文/长度合理/粘连命令拆分如 `\partialz`）→ **mathtext 渲染闸**
  （必须真实可渲染；矩阵类环境逐单元格校验）。任一不过 → 保留 PNG（SOP 4.2 回退态）。
- 应用层重写为**逐引用保守替换**：只替换有 LaTeX 的引用；整行 `$$..$$` 仅当该行
  只剩单一公式；无 LaTeX 的引用永不引入 `$`。应用前全库 tar 备份，可整体回滚。

### 结果

- 唯一公式图 **1327** 张：**接受 899（71.0%）**，弃权 368
  （UNSURE 难图 / 图中本无数学表达式如真值表结构图 / 双读不一致 / 渲染不过）。
- 哈希传播后实际填充 **1374 个公式位、44 个文件**；知识库剩余 PNG 公式引用 731 个。
- 全库数学串现状：约 3000 处 `$...$`（含首批 OMML 原生转换）；顺序解析验证
  **0 处图片被困进数学区**；`corpus_validator` 全量 **0 错误**；状态保持 `pending`。
- 已知残留：compiler 课程源文本含字面 `$`（FOLLOW 集终结符），为既有内容非本次引入。

### 待人工复核

- 44 个已转写文件建议优先对照原件抽查 LaTeX 正确性（notes 已标注清单）；
  弃权的 368 张保留 PNG，可后续换更强视觉模型重跑（队列 `_unique_images.json` 保留）。

## 追加（2026-08-23）：管线沉淀 Windows 化 + passed 清零重跑

### 工具沉淀（apps/tools/material_converter）

- 视觉转写正式入包：`vision_worker.py`（三道闸转写）/ `propagate_vision.py`（哈希传播），
  CLI 接线 `--vision-run [N]` / `--vision-workers N` / `--vision-propagate`，
  与 `--emit-ai-jobs` / `--finalize` 构成完整 AI 阶段；SKILL.md 流程同步更新。
- **Windows 适配**：`find_soffice()` 增加 ProgramFiles/LibreOffice/soffice.exe 与 Linux
  路径探测；LibreOffice profile 改 `Path.as_uri()`（修复 Windows 下 file:// 非法）；
  新增 `bootstrap.ps1`；`bootstrap.sh` 改为仓库根 `.venv` 并自动探测 soffice；
  requirements.txt 补 matplotlib（渲染闸依赖）。README 全面重写（跨平台安装、
  完整工作流、命令参考、去重规则、隐私红线、跨设备事项、FAQ、回滚）。

### passed 清零重跑

- 备份后删除全部 **22 条 passed**（manifest 行 + md + assets；快照
  `.cache/knowledge_backup_pre_passed_purge_20260823_0320.tar.gz`），涉及 10 门课程。
- 用现有管线重新生成：新增 **26 行**（含此前被 dedup 抑制的 3 个候选恢复入库；
  cpp 两组同标题行经核为不同源文件 .doc/.ppt、签到1/签到2，非重复）。
- 现状：**599 行全部 pending**（22 条旧 passed 出库）；`corpus_validator` **0 错误**。
- AI 阶段：重生成件多为手写扫描/试卷页（OCR 属后续迭代）；公式槽位剩余
  **523 个（唯一 387 张）**——即上一轮被闸门弃权的集合，同一模型+同闸门重试无增益，
  队列 `_unique_images.json` 已重建保留，待更强视觉模型时一键补转。

## 追加（2026-08-23 续）：概率论重生成回归修复 + 视觉补转

重跑暴露三个批一时期"一次性脚本修复未进管线"的回归，本次全部管线化修复：

1. **双重资产前缀**：docx2md 模板自带 `assets/`，main 再替换 `assets/<sid>` →
   `assets/assets/<sid>/`。修复：占位符只替换 sid；另加双前缀净化器兜底。
2. **flush_vector_png 静默跳过**：与 soffice_convert 同款的跨模块 SOFFICE 绑定问题 +
   file:// profile URI。修复：惰性自解析 + as_uri()。
3. **propagate/清扫的目录映射**：probability 是唯一 legacy 目录课程
   （course_id=`probability_theory` ≠ 目录名`probability`），按 course_id 拼路径会静默
   扑空；孤儿清扫曾因此误删 010-027，已从备份精确恢复。

概率论 7 份往年卷最终干净重生成：956 个公式引用全部单前缀 PNG（WMF 转换 1170/1170）；
视觉转写 607 张唯一图 **接受 450（74.1%）**，传播后填充 762 位、finalize 应用 9 文件。
全库终态：**599 行全部 pending**；$数学$ 约 2880 处、公式 PNG 回退 964 处；
顺序解析 0 坏行；`corpus_validator` **0 错误**。

同源对比（旧 passed vs 新管线）：概率论2013A 旧 111 处未校验手打公式 vs 新 82 处
过闸 LaTeX + 24 张难图回退；工数I 乱码PDF 旧 827 字符整页图 vs 新 6060 字符真文本；
手写扫描类两者等价（内容在图中）。

## 教训沉淀（2026-08-23，六条红线）

以下每条都有本轮真实事故背书，后续任何批次转换前必须过一遍：

1. **一次性修复必须管线化**。双资产前缀 bug 在批一用临时脚本修掉，重跑即复发。
   规则：任何修复必须落在管线代码里并配回归用例，禁止对生成物做一次性后处理。
2. **跨模块可变配置只能惰性解析**。`main.py` 的 `global SOFFICE` 只绑定了自己的副本，
   `flush_vector_png` 静默跳过转换（kept-as-vector=1024）。
   规则：模块级配置在使用点惰性解析或经属主模块赋值；每个 soffice 调用点都要自检。
3. **路径拼接必须走统一入口 `knowledge_dir()`**。probability 是唯一 legacy 目录课程
   （course_id=`probability_theory` ≠ 目录名`probability`），按 course_id 拼路径导致
   传播静默扑空、孤儿清扫误删 18 个健康文件。
   规则：凡从 manifest 拿到 course 后拼磁盘路径，一律经 knowledge_dir()。
4. **过滤字段要用事实源核对**。连三个脚本把 course 字段写成 `'probability'`
   （实际 `probability_theory`），"删除0行/行数0"的假象掩盖了真实状态。
   规则：写过滤条件前先打印 distinct 值；删除类操作必须先输出将删清单再执行。
5. **批量操作前先快照、操作后在同一调用内验证**。备份+回滚演练两次挽救了误删；
   跨调用状态漂移曾造成连续误判。
   规则：清→跑→验证压缩进单次调用；任何破坏性操作先 tar 快照。
6. **validator 不查的不等于没问题**。坏引用（assets/assets/、未转 WMF）通过校验入库。
   已补 `scan_asset_integrity()` 进 --validate 流程；题目锚点覆盖率缺口同步修复
   （QUESTION_RX 扩展至阿拉伯数字/第X题/括号序号，练习类只用强信号防列表误标）。

## 追加（2026-08-23 终）：剩余学科全量入库

- 29 门剩余课程程序化入队（subject_dirs 排除已转与大物实验），**新增约 1100 行**，
  知识库 **599 → 1705 行，全部 pending**，覆盖 44 门有产出的课程。
- 新批视觉转写 285 张唯一图 **接受 209（73.3%）**；题目锚点扩展后新批 **759 个**
  （阿拉伯数字/第X题/括号序号），全库锚点 426 → **1185**。
- 全库终态：`$数学$` 3818 处、公式 PNG 回退 790 处、坏引用 **0**、向量残留 **0**、
  `corpus_validator` **0 错误**。
- 本轮新修三缺陷：propagate 后写空条目会覆盖先前的接受结果（改为非空优先）；
  vision_worker 对队列值类型的隐式假设（str/list 兼容）；计算方法 35 行错位
  （清行重跑修复，重跑 errors=0）。
- 未入册说明：加密 zip（等密码）、数据集 xml/jpg（非知识材料）、html 讲义
  （转换器暂不支持）、大物实验合辑（PLAN-1 排除）——均属预期外范围。

## 追加（2026-08-23 终²）：锚点重打与激活前置条件

- 题目锚点按扩展规则全库重打（剥旧→重打）：**1185 → 3840 个**，179 文件更新，
  validator 通过。旧库锚点少的原因：旧正则只认中文序号`一、`且练习类角色完全不打。
- 语料库重建尝试暴露并修复 9 文件非本地图片引用：datauri 内嵌图提取、25 张外链图
  （飞书/gitee）下载转本地资产、12 处死链注记替换；`scan_asset_integrity` 升级为
  全量图片引用检查（不再只查 assets/ 前缀）。
- 构建器已验证全部 1705 行资产合格，但**索引仅收录 status=passed 的行**——当前
  全库 pending（旧 22 条 passed 已按指令清除），故激活暂缓。这是设计行为：
  检索只服务人工复核过的内容。
- 人工审核出首批 passed 后，一键重建激活：
  `PYTHONPATH=worker/src python -m scut_senior_worker.corpus_builder build \
    --manifest knowledge/manifest.csv --knowledge-root knowledge \
    --store-root .local/corpus-store --source-commit <HEAD> \
    --repository-root <repo根>` 然后 `activate --store-root ... --corpus-version <build输出>`。

## 追加（2026-08-23 终³）：语料库激活

- iteration-7 审核分支并入 master（零冲突自动合并：knowledge 取 master 的图片修复，
  manifest 取审核状态，web 并入）。终态 **1701 passed + 4 pending**。
- 构建器口径精判零 chunk 文件仅 4 个（电工学×2/Java/移动开发，纯图无文本层，
  已退回 pending 待 OCR）——此前自造的"<40字符"代理规则误杀 905 个，已回滚；
  教训：判定标准必须复用构建器自己的函数，禁止代理启发式直接改状态。
- 新语料库已构建并激活：`corpus-8e7b56f3…`，**24237 chunks**，其中 **4544 个携带
  question_id**——题目级定位正式进入检索索引；43 门课程全部开启。
- 回滚方式：`rollback --store-root .local/corpus-store --repository-root <repo根>`。
