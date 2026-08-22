# 技能：学科资料转 Markdown（material-to-markdown）

> 收录于仓库 `apps/tools/material_converter/SKILL.md`。此技能描述“如何用 AI 把 `学科资料/`
> 下的文件转成合格的知识库 Markdown”，并指明 AI 能做什么、绝不能做什么。

## 能做什么

- 按 `apps/scut-senior/docs/MATERIAL_TO_MARKDOWN_SOP.md` v1.7 走完整转换流程；
- 调用确定性抽取工具 `apps/tools/material_converter` 拿到忠实骨架（标题/段落/表格/图片、
  原生 OMML→LaTeX、page/slide/heading 锚点、manifest 记录）；
- **AI 语义归一化**（工具不含、需要由 AI/模型完成）：
  - 扫描稿/手写稿的 OCR 校正、版面与阅读顺序恢复；
  - 把 MathType/OLE **公式预览图**转成 LaTeX（只转能逐项对得上原件的）；
  - 给出历年题的题目边界候选，供人工确认；
  - 对低置信 OCR 位置做重点检查并写 `notes`。

## 不做什么（SOP §4 红线）

- 不总结、缩写、解释、纠错、补写、或根据常识/答案猜公式、数字、单位、术语、代码；
- 不把工具或 AI 输出直接标 `passed`；最终结论由人工审核决定；
- 不改动原文；原资料疑似有错时原样保留，在 `notes` 说明；
- 不破解加密 zip（准入判断跳过），不上传第三方云解析，不执行宏。

## 执行流程

1. **课程接入**：先确认 `packages/contracts/v1/courses.json` 已注册该课程（`course_id`/
   `aliases`/`repository_paths`）。
2. **隐私前置**：含学生/贡献者姓名、班级、学号的文件名先 `git mv` 脱敏；元数据/正文真实
   身份信息清除或记 `notes`；试卷密封线模板字段保留。
3. **确定性抽取**：
   ```bash
   cd apps/tools/material_converter
   .venv/bin/python -m material_converter.main --course <文件夹名> --validate
   ```
4. **AI 语义归一化**：
   ```bash
   # 4a. 导出作业包（公式图清单 + OCR 页清单）
   .venv/bin/python -m material_converter.main --emit-ai-jobs
   # 4b. GLM-4V 视觉转写公式图（三道闸：三票多数决 → 确定性校验 → mathtext 渲染闸；
   #     凭证放仓库根 .cache/glm4v.env，见 README；未过闸的自动保留 PNG）
   .venv/bin/python -m material_converter.main --vision-run --vision-workers 4
   #    先试小样: --vision-run 20
   # 4c. 按内容哈希传播转写结果到全部作业包（同一张图只转一次）
   .venv/bin/python -m material_converter.main --vision-propagate
   # 4d. 应用回知识库（替换为 $...$、清理已用资产、状态保持 pending）
   .venv/bin/python -m material_converter.main --finalize
   ```
   无视觉模型时跳过 4b/4c，直接人工回填 formulas.json 后执行 4d。
5. **人工审核**：逐文件对照原件，确认公式/题界/顺序/隐私，然后才把该行置 `passed`。

## 关键约定

- `manifest.title` 是 `source_title` 的事实源；`course`/`title`/frontmatter 必须一致；
- 每份资料归一门课；同资料误放其他目录只处理一份规范来源；无答案版是答案版严格子集时只转答案版；
- 无文本层/乱码 PDF 采用整页图片方案（本仓库既定模式），`notes` 注明“待人工决定 OCR”；
- 转换中间产物（`.work/`、`.ai_jobs/`、staging、调试 HTML）不入 Git；`knowledge/` 不留临时产物。

## 六条红线（每条都有真实事故背书，跑批前必读）

1. 修复必须进管线代码+回归用例；禁止对生成物做一次性脚本后处理（复发过）。
2. soffice 等模块级配置在使用点惰性解析；每个调用点自检（曾静默 kept-as-vector=1024）。
3. 从 manifest 的 course 拼磁盘路径一律经 `knowledge_dir()`（probability 是 legacy 目录，
   直接拼 course_id 会静默扑空、误删文件）。
4. 过滤条件先打印 distinct 值核对再执行；删除类操作先输出将删清单（字段值写错过三次）。
5. 清→跑→验证压缩进单次调用；破坏性操作前先 tar 快照（备份两次挽救误删）。
6. 题目锚点：试卷类用强+弱信号（中文序号/第X题/阿拉伯顿号 + 数字点号/括号号，排除小数），
   练习解答类只用强信号防列表误标；锚点是工具提议，须人工确认。

## 相关文件

- 工具：`apps/tools/material_converter/`（README.md：命令、新增课程、两段式说明）
- 大一批次审核记录：`apps/scut-senior/docs/review_artifacts/2026-08-22-agent-batch-review.md`
