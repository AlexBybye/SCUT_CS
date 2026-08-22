# Skill 开源清单

> 收录规则和提交方式见 [README.md](README.md)。
> 每条必须写清**能做什么**和**不做什么**。发现链接失效或描述不符，欢迎提 PR 改掉。

---

## 🏫 本院开发（SCUTCSer后续开发开源的skill放置于此）

### Skill Optimizer（skill-for-skills）

[AlexBybye/skill-for-skills](https://github.com/AlexBybye/skill-for-skills) · MIT-NC · Python 3.10+

以证据驱动的方式创建、优化、验证、发布与回退可复用的 LLM Agent Skill。走不可变基线加 Compare-and-Swap 迭代：先冻结基线，再让候选版本和基线在同一批用例上比，确实变好了才替换。双平面（路由 / 执行）评估，跨 Claude、Codex、GLM 等多个宿主。

**不做什么**：不是快速起草 skill 的提示词模板；控制平面是确定性的，不替你判断业务需求合不合理。

**适合谁**：想认真维护一套自己的 skill，而不是每次重写提示词的同学。但需要注意的是，此仓库是工业级别规范skill,如果自用skill切勿使用此优化/创建器，极耗token、庞大。

### Skill Forge

[AlexBybye/skill-forge](https://github.com/AlexBybye/skill-forge) · MIT-NC · Python 3.10+，纯标准库无依赖

上面 Skill Optimizer 抽出来的轻量版，独立版本线从 0.1.0 起。三个模式：`optimize`（针对一个真实失败改进现有 skill）、`no_skill`（先测不用 skill 行不行）、`create`（有证据支持才新建）。第二个模式最有意思 —— 大多数人跳过了"这个任务到底需不需要 skill"这一步。而在大模型日趋完善，skill篇幅大为减少的当下，弥足珍贵。

**不做什么**：不做安装、发布、commit、release，这些要单独授权，它只交付候选包。无网络调用。

**和上一条的关系**：功能重叠。想个人上手选这个，需要完整生命周期管理再上 Skill Optimizer。⚠️**别两个同时装。**

### Code Analyzer（codebase-learning-skill）

[AlexBybye/codebase-learning-skill](https://github.com/AlexBybye/codebase-learning-skill) · 插件式布局，`SKILL.md` 在 `skills/code-analyzer/`

读懂一个陌生仓库，产出一份有边界的学习地图（写到目标仓库的 `doc/analysis/` 下）。覆盖 Web、Mobile、Backend、Data/Infra、AI 五个域：先做一次浅层发现定路由，只加载相关域的合同，空的域直接跳过不生成空模板。混合仓库至少给一条逐跳有证据的端到端路径。

真正有用的是它的证据分级 —— 每条结论都要标 `source`：`code`（源码符号直接证明）、`config`（配置/schema/migration 证明）、`inferred`（至少两个独立锚点，并写出推断过程）、`unavailable`（边界闭不上，说明查了哪儿、缺哪一环）。证据只能用相对目标根目录的 `path#symbol` 或行号锚点。

**不做什么**：不做单文件讲解、code review、bug 诊断修复、只要架构图、安全或许可审计，也不改业务源码。默认不跑目标应用/测试/构建、不装依赖、不联网。不从静态结构推断线上部署状态、运行性能、模型质量或生产就绪 —— 这些一律标 `unavailable`。

**适合谁**：接手学长的课设代码、读开源项目、`软件工程` / `操作系统课程设计` 之类要先看懂再动手的活。作者在 README 里注明了一点值得学：那些行数、字节的下降幅度衡量的是文件和指令合同，**不是实测 Token、运行时间或回答质量**。

### jargon-codec-zh

[AlexBybye/jargon-codec-zh](https://github.com/AlexBybye/jargon-codec-zh) · 插件式布局，`SKILL.md` 在 `skills/jargon-codec-zh/`

"把人话压进 PPT，也把 PPT 放回人间。" 普通话和互联网大厂黑话之间的双向转换，覆盖产品、运营、商业、研发、管理和 AI 语境（RAG、Agent、MCP、Eval 这些也算黑话，不另设模式）。

- **黑话 → 普通话**：把"赋能、抓手、闭环、拉通、沉淀、链路"还原成谁做什么、何时完成、如何验收。
- **普通话 → 黑话**：两个档位。`自然`（真实工作可用，每句只引入一两个真正增加精度的术语）和 `无所不用其极`（密度拉满，可叠加 `bilingual`，每句混一到两个英文词）。用户没指定档位时它只问，不偷偷代选。

**不做什么**：不做普通润色、摘要、外语翻译、事实核查、技术问答、代码任务、动机判断，也不在没有原文的情况下随机生成黑话。**黑话可以拉满，事实不能缩水** —— 不新增项目阶段、上下游、数据来源、业绩、指标、权限或承诺，不把"计划、可能"升级成"完成、保证"，不删改负责人和截止时间。原文只覆盖小范围时不给你写"端到端、全链路"。

**适合谁**：读实习 JD 和大厂技术文章、写 SRP 结题报告和竞赛答辩、看不懂群里学长在说什么。反向用法也实在 —— 简历和答辩稿有时确实需要那套话术，只要别顺手把没做过的事写进去。在此，致敬酥神（doge.）

### humanizer-zh（humanizer-CN）

[AlexBybye/humanizer-CN](https://github.com/AlexBybye/humanizer-CN)

一套给 GPT、Claude 用的中文编辑规则，处理翻译腔、模板腔和聊天残留。改写时保留原文的事实、主张、归因、立场、限制条件和不确定程度。本土化落在信息顺序、主语、搭配和语域上，不靠词语黑名单。

**不做什么**：不判断一段文字是否由 AI 生成，不会把普通润色悄悄变成摘要、扩写、事实核查、来源验证或抄袭检测，不会为了"更像真人"改掉原意、作者立场或文体。

**说明**：它是**中文写作质量**工具，不是降 AI 率工具~~至少不应该是？~~ —— 这两件事经常被混为一谈。用它改自己写的东西可以；用它包装自己没读过的内容，参见 README 第二节最后一条和主仓库的「请诚信学习」。本文件夹的两份文档都过了一遍它的规则。

### Craft Frontend（design-skills）

[AlexBybye/design-skills](https://github.com/AlexBybye/design-skills)

页面级前端 Skill。把"做一个什么主题的页面"直接变成可运行前端，或者在不破坏既有行为的前提下改版 —— 改版前会先核对路由、API、表单、状态和键盘行为。中文界面文案也一起管：不虚构客户、数字或运营承诺，也不把本地 DOM 变化写成"订阅成功"。

**不做什么**：不是组件库或脚手架，不负责后端、部署和完整产品开发。

**适合谁**：`web开发前端技术基础` 的课设、大作业演示页、社团活动页等一系列需要网站等前端开发的项目demo，好处相比于taste-skill是更便宜，更省token的情况下得到较有品味的设计，因为不需要工业级别的接轨。

---

## 🌐 外部工具（SCUTCSer安利的skill放置于此）

> 只收实际用过的。每条带一句结论，不做无判断的搬运。

### Skill Scanner

[cisco-ai-defense/skill-scanner](https://github.com/cisco-ai-defense/skill-scanner) · Apache-2.0 · Cisco AI Defense 维护 · `pip install cisco-ai-skill-scanner`

Agent Skill 安全扫描器，检测提示词注入、数据外传和恶意代码模式。三种引擎结合：规则匹配（YAML + YARA）、LLM-as-a-judge、行为数据流分析，另有 meta-analyzer 压误报。支持 SARIF 输出接 GitHub Code Scanning，可做 pre-commit hook。支持 Codex Skills、Cursor Agent Skills，加 `--lenient` 也能扫 Claude Code 的 `.claude/commands/*.md` 和扁平 markdown skill 仓库。

**不做什么**：官方明确写了这是 best-effort 检测，**不是完整覆盖 —— 扫出来没问题不等于这个 skill 安全**。

**结论**：装任何第三方 skill 前先扫一遍，一条命令的成本。本清单里唯一建议所有人都装的工具。也是 `信息安全` / `面向互联网+的数据安全` 课程作业不错的实践对象。

---

## 📌 待补

这一栏欢迎认领，也欢迎直接提你觉得该有的：

- **本仓库检索 / 按课程 sparse-checkout 助手** —— 主 README 第 96-99 行现在靠装 Chrome 插件和手动 view raw 来解决 15G 仓库的取用问题，这件事可以做成 skill：输入课程名，输出该课有什么、哪些是 LFS 大文件、以及只拉这门课的 git 命令。依赖本仓库目录结构，只有我们能写。
- **单科复习规划** —— 依赖 🟢 最低目标（每门课的 README：考察制度 / 老师评价 / 备考建议）先落地，没有结构化课程元数据的话它只能瞎猜。
