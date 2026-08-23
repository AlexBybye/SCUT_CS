# 迭代 2 状态：Markdown candidate、检索和课程包

日期：2026-08-16

开发分支：`codex/scut-senior-iteration-2`

固定开发基座：`4bf65df7c2f84ca194b6679783ca91aaf6ef9619`

状态：`completed`（2026-08-23 结题，见文末附录）；历史状态为 `in_progress_activation_blocked`——当时来源提交合并 `master` 前不得激活 corpus。该激活门现已在受信 master 上满足并留有可复核证据。

固定开发基座只绑定本分支的起点，不代表当前工作区差异已经进入该提交。真实 candidate 只能从后续包含这些差异、且构建输入保持干净的固定提交生成。

## 已确认的资料边界

- 首批课程注册表固定为 10 门；大学物理实验与 SRP 不进入知识 manifest 或检索语料。
- `information-security-intro-001` 和 `cpp-001` 已由 `Klosure` 人工审核，manifest 状态为 `passed`。
- manifest 当前共 23 份资料：上述 2 份为 `passed`，其余 21 份保持 `pending`。
- 8 份纯图片资料继续保持 `pending`：`linear-algebra-001`～`005`、`engineering-mathematical-analysis-1-001`、`engineering-mathematical-analysis-2-001`、`discrete-mathematics-001`。
- `docs/review_artifacts/` 只保留脱敏后的必要审核证据，不作为检索语料或 candidate 输入。

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

- corpus CI 必须校验仓库真实的 `apps/scut-senior/knowledge/manifest.csv`，只读取 `passed` Markdown 和必要 assets，在临时目录构建并再次验证 candidate。
- CI 不上传、不提交 candidate 派生产物，并明确断言构建过程没有生成 `active.json`；`active.json` 也不得进入 Git。
- 合成 Fixture 校验继续保留，不能用真实资料替代测试 Fixture，也不能把 Fixture 的 `passed` 当成人工审核结论。
- `worker`、chunker、索引 schema、manifest／locator 契约或语料构建器变化必须同时经过 App CI 和 corpus CI。纯 `apps/scut-senior/knowledge/**` 内容变化只构建、验证 candidate，不触发 Web/API 部署。
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

## 结题附录（迭代 7.5，2026-08-23）：candidate 激活门在受信 master 上满足

本文件此前停留在 `in_progress_activation_blocked`，缺的是三件外部证据：干净固定提交、
合并 master、以及合并后的激活与回退闭环。迭代 7.5（插入期）已全部补齐：

1. **固定提交**：资产修复与全部 7.5 改动经 `iteration-7.5-Insertion` 分支合入本地 master，
   合并提交 `06e1cb6338f6ad2e3946893e413d3f7081c47dfd` 即构建时 `refs/heads/master` 的 HEAD；
   构建前以 `git status --porcelain --untracked-files=all -- apps/scut-senior/knowledge
   apps/scut-senior/worker apps/scut-senior/packages/contracts/v1` 验证构建输入零差异。
   历史 candidate 的 `source_commit=14b63e204eb3…` 与本次 `06e1cb63…` 均为 master 祖先
   （`git merge-base --is-ancestor` 验证通过）。
2. **重建与激活**：在该固定提交上执行 `scut-senior-corpus-store build`：1701 个 passed 源、
   24237 chunk、43 门课程，candidate 复验 `ok=true`；随后 `activate --trusted-master-ref
   refs/heads/master` 成功，active 指向 `corpus-06e1cb6338f6-…`，上一有效版本保留为
   `corpus-8e7b56f39427-…`。
3. **回退演练**：`rollback` 成功回到 `corpus-8e7b56f39427-…`，再次 `activate` 恢复
   `corpus-06e1cb6338f6-…`；全程命令与结果记录于
   `resources/corpus/iteration-7.5-activation-drill.json`。
4. **逐课程检索闭环**：43 门启用课程逐门执行 检索 → `[S#]` 编号映射完整性校验
   （chunk_id／来源标题／正文非空），全部通过（其中 `english`、`network_application_architecture`
   两门以内容派生探针复测后命中），证据见
   `resources/corpus/iteration-7.5-activation-retrieval-drill.json`。

至此本文件"尚缺迭代 2 退出证据"清单中的本地链路全部闭合；远端 CI 在固定提交上的通过
记录仍属分组 A 外部证据，按使用者同日确认记录现状。
