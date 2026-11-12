> 收录规则和提交方式见上一级的 README。提 PR 时，写清这个 Skill 能帮人做哪件事、做到哪一步就该自己接手。链接挂了、描述对不上，也欢迎顺手修一下。

## 🏫 本院开发

SCUTCSer 自己开发并开源的 Skill 放这里。

### Skill Optimizer（skill-for-skills）

[AlexBybye/skill-for-skills](https://github.com/AlexBybye/skill-for-skills) · MIT-NC · Python 3.10+

一套 Skill 要长期维护，最烦的是改完觉得顺眼了，换个用例却退步了。Skill Optimizer 会先冻结基线，让候选版本和原版跑同一批用例。该不该路由到这个 Skill、叫到它之后能不能把活做对，两件事分开测。候选确实更好才替换，这就是这里的 Compare-and-Swap。它支持 Claude、Codex、GLM 等宿主，创建、优化、验证、发布和回退也都管得到。

这套流程按工业级维护的需求做得很重，跑起来也费 Token。控制平面按确定的规则走，业务需求合不合理还得你自己判断。要是只想给自己起草一份小 Skill，别从这套开始，往下看 Skill Forge。

### Skill Forge

[AlexBybye/skill-forge](https://github.com/AlexBybye/skill-forge) · MIT-NC · Python 3.10+，只用标准库

从 Skill Optimizer 里拆出来的轻量版，独立版本从 0.1.0 起。手头已经有个 Skill，但在一个真实任务上翻了车，用 `optimize` 针对那次失败改。还没写，可以先用 `no_skill`，看看直接交给模型能不能做。跑过用例，有证据说明值得加，再用 `create`。

我觉得 `no_skill` 最有意思。现在模型能直接做的事越来越多，Skill 也能写得越来越短。“这活儿到底用不用写 Skill？”这一步反而经常被跳过。

它全程没有网络调用，交到你手里的是候选包。安装、发布、commit 和 release 都得单独授权。个人用先选这个，需要把发布和回退也纳入流程再上 Skill Optimizer。两个功能有重叠，**选一个装就行**。

### Code Analyzer（codebase-learning-skill）

[AlexBybye/codebase-learning-skill](https://github.com/AlexBybye/codebase-learning-skill) · 插件式布局，`SKILL.md` 在 `skills/code-analyzer/`

接到学长留下的课设代码，光看目录还不知道从哪儿读，可以先让它在目标仓库的 `doc/analysis/` 下写一份学习地图。它先扫一遍，看看涉及 Web、Mobile、Backend、Data/Infra、AI 里的哪些领域，再加载对应的分析约定。没涉及的领域直接跳过，省得留一堆空模板。碰到几个领域混在一起的仓库，至少会梳理一条端到端路径，每一跳都附证据。

我觉得最值得看的是每条结论旁边那个 `source`。源码里的符号能直接证明，就标 `code`。靠配置、schema 或 migration 证明，标 `config`。要推断，得拿出至少两个独立锚点，把怎么推的写清楚，再标 `inferred`。证据接不上就标 `unavailable`，交代查到哪儿、还差哪一环。引用只用相对目标仓库根目录的 `path#symbol` 或行号锚点。

拿来读开源项目，或者给 `软件工程`、`操作系统课程设计` 先摸清代码结构，都挺合适。想只讲一个文件、做 code review、查修 bug、单画架构图，或者做安全和许可审计，就另开任务。它不改业务源码，默认也不跑应用、测试或构建，不装依赖、不联网。线上部署、运行性能、模型质量和能不能上生产，单凭静态结构答不了，一律标 `unavailable`。

README 还有个细节值得学。里面说行数、字节少了多少，量的是文件和指令合同的体积。实跑消耗多少 Token、花多长时间、答得好不好，得另测。

### jargon-codec-zh

[AlexBybye/jargon-codec-zh](https://github.com/AlexBybye/jargon-codec-zh) · 插件式布局，`SKILL.md` 在 `skills/jargon-codec-zh/`

“把人话压进 PPT，也把 PPT 放回人间。”实习 JD 或群里学长发的那段话，读了两遍还不知道谁要干什么，可以先拿它翻回普通话。碰上“赋能、抓手、闭环、拉通、沉淀、链路”，就把人、事、时间和验收说清楚。产品、运营、商业、研发、管理里的说法都能转，RAG、Agent、MCP、Eval 这些 AI 术语也走同一套。

反过来写也行。`自然` 档每句放一两个真能说得更准的术语，工作里用得上。`无所不用其极` 档就把密度拉满，还能叠 `bilingual`，一句混一两个英文词。你没选档位，它会先问。

写 SRP 结题报告、竞赛答辩或者简历，有时确实用得上那套话术。别顺手把没做过的事写进去。项目做到了哪一步、有哪些上下游、数据从哪来、业绩和指标是多少、谁有权限、承诺了什么，都照原文走。负责人和截止时间也得留着。“计划”不能改成“完成”，“可能”不能写成“保证”，做了一小段也别写成“端到端、全链路”。

它接的是有原文的双向转换。普通润色、摘要、外语翻译、事实核查、技术问答、写代码和猜动机都不在范围里。没有原文，它也不会凭空给你攒一段黑话。在此，致敬酥神（doge.）

### humanizer-zh（humanizer-CN）

[AlexBybye/humanizer-CN](https://github.com/AlexBybye/humanizer-CN)

给 GPT、Claude 用的一套中文编辑规则，这个文件夹里的两份文档都过了一遍。遇到翻译腔、模板腔，或者正文里混进了聊天时的客套话，可以拿它理一遍。它会看信息该先说哪句、主语清不清楚、词搭得顺不顺、这话放在这个场合合不合适，没必要照着一份词语黑名单挨个换。原文的事实、主张、归因、立场、限制条件和不确定程度都得留住，文体也一样。

交给它润色，就按润色来。摘要、扩写、事实核查、来源验证、抄袭检测是另外的事，它也不会判断一段话是不是 AI 写的。拿它改自己写的东西挺合适。至于拿来降 AI 率，~~至少不应该是这么用吧？~~ 想给自己都没读过的内容润色一下再交，先去看 README 第二节最后一条和主仓库的「请诚信学习」。

### Craft Frontend（design-skills）

[AlexBybye/design-skills](https://github.com/AlexBybye/design-skills)

`web开发前端技术基础` 的课设、大作业演示、社团活动页，需要先做出一个能跑的页面，可以从这儿上手。给它一个页面主题就能开工。手头已有页面要改版，它会先看路由、API、表单、状态和键盘操作，别改完好看了，原来能用的东西反而坏了。

中文界面文案也一起改。客户、数字和运营承诺得有出处，点个按钮只改了本地 DOM，就别写“订阅成功”。它管的是页面，组件库、脚手架、后端、部署和整套产品开发要另外做。课设 demo 用不着按工业项目那套接，跟 taste-skill 比，我更愿意用它少花点 Token，把页面做得像样些。

### material-to-markdown（学科资料转 Markdown）

[AlexBybye/SCUT_CS](https://github.com/AlexBybye/SCUT_CS) · 本仓库内置 · `apps/tools/material_converter/`（`SKILL.md` 在 `apps/tools/material_converter/SKILL.md`）

大二大三开了新课，或者有同学又传了一批课件，想给知识库和复习助手补资料，可以跑这个。它按 `apps/scut-senior/docs/MATERIAL_TO_MARKDOWN_SOP.md`，把 `学科资料/` 里的 DOCX、DOC、PDF、PPTX、PPT、代码和笔记转成 Markdown 条目。转完会带上 frontmatter、图片、page/slide/heading 锚点和 manifest 记录，回头还能找到对应的原件。

转换分两步。先用程序抽取 OOXML、PDF、PPT 里的文本、标题和表格，把原生 OMML 公式转成 LaTeX，同时做去重和隐私预处理。再用 `--emit-ai-jobs` 和 `--finalize` 处理 OCR 校正、公式预览图转 LaTeX、恢复阅读顺序，以及找出可能的题目边界。跑过的 `original_path` 会自动跳过，字节或内容重复的资料，以及重复的「无答案子集」，也会去重。加新课就在 `courses.json` 登记，再跑 `--course <文件夹> --validate`。

原件写了什么就转什么。它不总结、缩写、解释、纠错，也不凭记忆补字。公式没法和原件逐项对上，就留 PNG 预览，在 `notes` 里记一笔。工具和 AI 跑完也不能直接标 `passed`，按 SOP §4，得人工审过才算入库。加密 zip 不破解，文件不传第三方云解析，也不执行宏。

### task-orchestrator

[AlexBybye/subtask_skill](https://github.com/AlexBybye/subtask_skill) · `SKILL.md` 位于仓库根目录

一件活同时牵涉 API、UI、数据库、测试和文档，有些部分确实可以分头做。这时可以先用它把谁做哪块、哪块得等谁、最后怎么验收理清楚。它会先看能不能找出至少两条真正独立的工作流，以及省下的时间值不值派发和合并的工夫。值得拆才交给多个 subagent，最后统一合并、验证。多模块实现、迁移、批处理和多来源研究，都有用得上的时候。

单文件小改、必须一步接一步的调试、范围还没摸清的探索，直接做更省事。几个任务要改同一份契约或同一处可变状态，也先别分头动。文件多、步骤多，本身不够成为拆任务的理由。默认拆 3 到 8 个子任务，只派一层，失败的子任务最多重试一次。

## 🌐 外部工具

这里只收同学实际用过的。安利的时候，说一句你会在什么情况下用它。

### Skill Scanner

[cisco-ai-defense/skill-scanner](https://github.com/cisco-ai-defense/skill-scanner) · Apache-2.0 · Cisco AI Defense 维护 · `pip install cisco-ai-skill-scanner`

装第三方 Skill 前，花一条命令先扫一下。这份清单里，我会建议大家都装的就这一款。它查提示词注入、数据外传和恶意代码模式，用到 YAML + YARA 规则、LLM-as-a-judge 和行为数据流分析，还有个 meta-analyzer 帮着压误报。

平时可以挂在 pre-commit 上，也能输出 SARIF 给 GitHub Code Scanning。Codex Skills、Cursor Agent Skills 都支持。加 `--lenient` 还能扫 Claude Code 的 `.claude/commands/*.md`，或者把 Skill 直接平铺成 Markdown 文件的仓库。做 `信息安全` 或 `面向互联网+的数据安全` 课程作业，也可以拿它当个实践对象。

Cisco 对覆盖范围的说法是 best-effort。**扫完没报问题，安全性仍得另外判断。**

## 📌 待补

下面两件事欢迎认领。平时用仓库还有什么地方觉得绕，也欢迎提。

- **本仓库检索 / 按课程 sparse-checkout 助手**。主 README 第 96–99 行现在还在教大家装 Chrome 插件、手动点 `view raw`。取一点资料也要先琢磨怎么从 15G 的仓库里拿出来，这事可以做成 Skill。输个课程名，告诉你这门课有哪些资料、哪些是 LFS 大文件，再给一条只拉这门课的 git 命令。这个得按咱们仓库的目录来，适合我们自己写。
- **单科复习规划**。先把 🟢 最低目标落到每门课的 README 里，写清考察制度、老师评价和备考建议。有了这些结构化的课程信息再做，省得它连这门课怎么考都不知道，就开始给人排复习日程。