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

## D5 · 阶段二先落地受限单步决策内核

- **决策**：阶段二第一切片实现纯 Python 的 AgentState reducer、动作白名单和
  死循环预算，并以内核方式接入现有一次性检索→生成链路；该链路继续作为兼容
  降级路径，不引入独立 Planner、ReAct 框架或第二套事件承载机制。
- **原因**：当前已有 EventStream、取消和终态持久化，但尚未具备
  `decision_produced → action → observation_recorded` 的闭环。当前运行已在检索前、
  模型尝试前和成功终态处使用 reducer，后续再逐步把模型决策结果接入动作协议，
  不改变一期本地运行边界。

## D6 · 统一输入自动路由，回答偏好归入助手设置

- **决策**：Composer 不再把 Workflow 作为主操作要求用户预先选择；根据统一输入以
  确定性规则识别五类 Workflow，并继续生成现有合同要求的
  `workflow_type + typed_payload`。识别结果允许在字段抽屉中纠正。
- **字段边界**：题目作答、错题原答案、考试范围和临时材料等任务字段只在识别到对应
  Workflow 后展示；`讲解形式` 与 `输出风格` 移入个人中心的助手设置，并持久化在
  本机浏览器。
- **复杂度边界**：当前路由不调用模型、不引入新服务；普通课程提问稳定回退知识答疑，
  后端请求 schema 和五类受控 Workflow 保持不变。

## D7 · 兼容模型全角引用并收紧 B 站元数据交付

- **决策**：模型输出的 `【S1】` 与 `[S1]` 均归一化为同一请求内引用；未知编号、越权课程、重复编号仍由 Guard 拒绝。
- **决策**：选择 B 站延伸学习时，模型必须返回 `scut-meta` 中的核心知识点与搜索词组合；元数据缺失时保留确定性回退，并去除考试时间、泛化学习请求等噪声短语。
- **原因**：实际运行曾出现 5 个候选全部通过来源授权，但模型使用全角编号导致引用接受数为 0；同次运行 B 站回退为整句用户问题，搜索词质量不足。

## D8 · B 站搜索固定带课程上下文

- **决策**：B 站匿名搜索的最终关键词按“课程名 + 模型搜索词或聚焦知识点”拼接；模型词缺失时仍使用确定性问题提炼，并保留课程名。
- **边界**：课程名和搜索词只用于外部补充搜索，不进入仓库引用、回答证据或课程范围判断；关键词仍受现有长度、数量和 URL 安全校验约束。
