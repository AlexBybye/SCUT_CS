# 二期迭代决策记录（PLAN-2 补充）

本文件记录 PLAN-2 执行过程中由用户明确拍板的、对 PLAN-2 的补充或覆盖。
PLAN-2.md 仍是唯一基准文档；本文件只登记**用户直接决策**，不重新推导计划。

## D1 · embedding 采用本地 ONNX，最终排序采用规则重排

- **决策**：embedding 不采用云端 API 或 Ollama，改为本机 CPU 推理的
  ONNX `bge-small-zh-v1.5`；最终排序不依赖模型 reranker，使用确定性规则重排。
- **影响**：
  - 阶段一 步骤 3 dense 腿使用 `bge-small-zh-v1.5` ONNX，输出维度 512。
  - 阶段一 步骤 5 使用 BM25F 优先、dense 仅补位的规则重排，不允许 dense
    无条件推翻明确的词法命中。
- **部署边界不变**：仍是一台小机器 + 一组文件，不引入 Ollama、Qdrant 或其他常驻推理服务。
- **落地状态**：ONNX 适配器走 `CPUExecutionProvider`；缺少本地模型文件时回退
  BM25F，不发起网络请求。

## D2 · 当前 46 门 P0 标注作为已审核验收基线

- **决策**：当前 46 门课程、每门 30 条的 P0 查询与目标 chunk 已由维护者审核，按
  现有内容固定为阶段一评测基线；纯图片、零文本来源（包括 `java_programming`）
  不进入本次 active 语料或评测。
- **影响**：后续 BM25F 与 Hybrid 对比以该基线为准，不再把它描述为自动候选或观察数据。
  换 candidate 或 embedding 模型时仍须重新校验目标 chunk 与对应 corpus_version。

## D3 · 本地 Hybrid 资产随仓库版本化，不上传运行 Secret

- **原决策**：active Hybrid candidate、回退 candidate、ONNX 模型和向量索引随仓库
  版本化，并排除运行 Secret；本条关于回退 candidate 和 Git LFS 的部分已由 D4 及
  当前普通 Git 资产策略覆盖。
- **仍然有效的边界**：`.local/env.online`、SQLite 运行数据库、WAL/SHM、日志和缓存
  继续忽略；API Key、OAuth Secret 与 BYOK 主密钥只从运行环境读取，绝不进入 Git。

## D4 · 阶段一只保留 active Hybrid candidate

- **决策**：阶段一提交只保留当前 active Hybrid candidate、ONNX 模型和向量索引，
  不再随仓库维护 lexical rollback candidate；这些阶段一资产按普通 Git 文件提交，
  不使用新增的 Git LFS 规则。
- **影响**：`active.json.previous_corpus_version` 设为 `null`；本地即时 rollback
  不再承诺。需要回退时使用 Git 版本回退，或从课程资料重新构建 candidate。
- **边界**：active candidate 的完整校验、课程开关、版本绑定和 fail-closed 行为
  保持不变；运行数据库、环境文件、日志和缓存仍不提交。
