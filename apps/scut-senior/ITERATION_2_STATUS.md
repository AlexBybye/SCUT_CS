# 迭代 2 状态：Markdown candidate、检索和课程包

日期：2026-08-16

开发分支：`codex/scut-senior-iteration-2`

固定开发基座：`4bf65df7c2f84ca194b6679783ca91aaf6ef9619`

状态：`in_progress_activation_blocked`；允许在当前固定基座上开发和验证 candidate 兼容性，但来源提交合并 `master` 前不得激活 corpus，也不能宣称迭代 2 闭环完成。

固定开发基座只绑定本分支的起点，不代表当前工作区差异已经进入该提交。真实 candidate 只能从后续包含这些差异、且构建输入保持干净的固定提交生成。

## 已确认的资料边界

- 首批课程注册表固定为 10 门；大学物理实验与 SRP 不进入知识 manifest 或检索语料。
- `information-security-intro-001` 和 `cpp-001` 已由 `Klosure` 人工审核，manifest 状态为 `passed`。
- manifest 当前共 23 份资料：上述 2 份为 `passed`，其余 21 份保持 `pending`。
- 8 份纯图片资料继续保持 `pending`：`linear-algebra-001`～`005`、`engineering-mathematical-analysis-1-001`、`engineering-mathematical-analysis-2-001`、`discrete-mathematics-001`。
- `review_artifacts/` 只保留脱敏后的必要审核证据，不作为检索语料或 candidate 输入。

## 当前发布门

开发和发布是两条不同的路径：

```text
当前固定基座上的实现与测试
→ 将审核结果与实现形成干净的固定提交
→ 该固定提交上的 candidate 构建与验证
→ 人工审查并合并 master
→ 证明 candidate 的 source_commit 已进入受信 master
→ 才允许单独执行 active 激活
```

- corpus CI 必须校验仓库真实的 `knowledge/manifest.csv`，只读取 `passed` Markdown 和必要 assets，在临时目录构建并再次验证 candidate。
- CI 不上传、不提交 candidate 派生产物，并明确断言构建过程没有生成 `active.json`；`active.json` 也不得进入 Git。
- 合成 Fixture 校验继续保留，不能用真实资料替代测试 Fixture，也不能把 Fixture 的 `passed` 当成人工审核结论。
- `worker`、chunker、索引 schema、manifest／locator 契约或语料构建器变化必须同时经过 App CI 和 corpus CI。纯 `knowledge/**` 内容变化只构建、验证 candidate，不触发 Web/API 部署。
- 默认运行继续使用 Fixture；没有配置并验证受信 active store 时必须故障安全关闭真实检索。

## 本地已实现与验证

- builder 已实现干净固定提交绑定、只读取 `passed` Markdown、确定性 chunk、必要 assets 复制、candidate／引用完整性复验和课程包生成。
- 两份真实 `passed` Markdown 已在临时干净 Git 提交中完成 candidate 构建与再次验证：2 个 source、55 个 chunk，课程为 `cpp` 和 `information_security_intro`；记录到 1 个完整 fenced block 超长例外，未生成 `active.json`。这只证明本地 candidate 兼容性，不是激活或上线证据。
- 本地检索适配器已实现单课程硬过滤、确定性排序、请求内 `[S1]` 映射和来源回查；默认仍为 Fixture，缺少受信 active store 时故障安全关闭。
- 受信 `master` 祖先校验、逐课程开关、上一有效版本回退已通过临时合成仓库测试；真实资料 candidate 在当前分支没有执行激活。
- 当前工作区验证结果为 Python 248 项通过；Web 29 项通过，typecheck 与 production build 通过。这些是本地自动化证据，不能替代远端 CI、合并或运行环境验收。

## 尚缺迭代 2 退出证据

- 将当前差异形成干净固定提交，并由远端 App CI 与 corpus CI 在实际提交上通过。
- 人工审查后合并 `master`，再证明真实 candidate 的 `source_commit` 已进入受信 `master`。
- 合并后单独完成真实 candidate 的 active → 单课程检索 → 来源回查 → 上一有效版本回退闭环，并保留可复核证据。

因此，在远端 CI、合并后激活与真实回退证据齐全前，不宣称真实 corpus 已上线或迭代 2 已完成。
