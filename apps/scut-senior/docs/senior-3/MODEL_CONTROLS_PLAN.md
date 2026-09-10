# SCUT 老学长：模型强度与思考控制计划

版本：0.1

状态：计划已记录，尚未修改 Workflow 请求合同或前端交互。

## 1. 目标与边界

在平台模型或自定义 BYOK 模型明确支持时，向前端开放两类可选推理参数：

- **模型强度**：例如 `low / medium / high`，用于表达供应商声明的推理强度、计算强度或回答深度档位；
- **思考控制**：例如 `disabled / enabled` 或供应商支持的离散档位，用于控制是否启用扩展推理能力。

本能力必须遵循“服务端声明、前端按能力展示、服务端再次校验”的闭环。前端不得根据显示名称、模型 ID 字符串或 Base URL 猜测支持情况；未知自定义 OpenAI-compatible endpoint 默认不开放任何高级控制。

本计划不要求展示或保存模型私有思维链，不把 `reasoning_content` 直接返回给学生，也不放宽现有引用、课程范围和输出 Guard。

## 2. 能力合同

服务端为每个可选模型返回关闭式能力元数据：

```json
{
  "inference_controls": {
    "strength": {
      "supported": true,
      "values": ["low", "medium", "high"],
      "default": "medium"
    },
    "reasoning": {
      "supported": true,
      "values": ["disabled", "enabled"],
      "default": "enabled"
    }
  }
}
```

约束：

1. 不支持时字段为 `null` 或 `supported=false`，前端不渲染对应控件；
2. 能力来自服务端维护的 adapter/capability registry；
3. 自定义 BYOK 连接只有命中服务端确认的 `(protocol, normalized_base_url, model_id)` 能力条目时才获得控制项；
4. 能力值必须是服务端声明的有限枚举，不能由前端自由输入；
5. 能力元数据不包含 API Key、模型私有响应或供应商账户信息。

## 3. 请求合同与服务端校验

在 `WorkflowRunRequest` 中增加可选字段：

```json
{
  "model_options": {
    "strength": "medium",
    "reasoning": "enabled"
  }
}
```

服务端在任何 provider I/O 前依次执行：

```text
解析实际选中模型/连接
→ 读取服务端能力声明
→ 校验字段是否受支持
→ 校验值是否属于 allowlist
→ 映射到具体供应商参数
→ 发起模型请求
```

如果请求携带模型不支持的选项，返回 422 并使用稳定错误码，不静默忽略，也不自动改写为其他档位。未携带 `model_options` 时使用服务端声明的默认值，保持旧客户端兼容。

Provider adapter 负责最终映射。例如某些模型可映射为 `reasoning_effort`，另一些模型可能使用不同字段；公共 Workflow 合同不能直接泄漏供应商专有字段。

## 4. 前端交互

前端在模型选择区域执行：

1. 读取选中模型的 `inference_controls`；
2. 只渲染被明确支持的“模型强度”和“思考控制”；
3. 使用服务端返回的枚举生成选择项；
4. 切换模型后立即清理旧模型不再支持的值；
5. catalog 或连接加载失败时关闭控件，不使用本地猜测值；
6. 提交前再次确认当前选项仍属于所选模型的能力范围；
7. 在 UI 中说明这些选项会影响延迟、token 和费用，但不会展示模型私有思维链。

建议落点：

- 后端目录：`model_catalog.py`；
- BYOK 状态合同：`contracts.py#ModelCredentialStatus`；
- Workflow 请求：`contracts.py#WorkflowRunRequest`；
- Web 类型：`web/src/contracts.ts`；
- 请求组装：`web/src/workflowRequest.ts`、`web/src/composables/useAppStore.ts`；
- 控件：`web/src/components/AssistantSettingsPanel.vue`；
- Provider 映射：各模型 adapter 的请求构造函数。

## 5. 自定义 BYOK 的能力识别

自定义连接允许任意公开 HTTPS OpenAI-compatible endpoint，因此不能默认认为其支持推理参数。第一阶段只为服务端已确认的组合开放能力：

```text
protocol=openai_chat_completions
+ normalized_base_url
+ model_id
→ server-owned capability profile
```

DeepSeek 直连能力识别不得依赖用户填写的 `connection_id`。连接 ID 只是用户侧别名，不是供应商身份或安全边界。

未命中能力 profile 时：

- 连接仍可完成普通问答；
- 前端不显示强度/思考控件；
- 服务端拒绝该连接携带高级 `model_options`。

## 6. 运行预算

当前独立 BYOK 分支的运行预算口径为：

- 硬运行上限：**180 秒**；
- 软水位：硬上限的 75%，即 **135 秒**；
- 首次回答调用不受软水位阻断；
- 软水位后停止可选 provider 重试、Guard 修复调用和 Humanizer；
- BYOK 单次请求 timeout 取 provider 配置上限与当前 run 剩余硬时间的较小值；
- plan/execute 长任务不再被旧 120 秒上限提前终止。

后续开放高强度推理时不能绕过这套预算。若某档位预计无法在剩余硬时间完成，服务端应拒绝或要求用户降低档位，而不是无限延长运行时间。

## 7. 验收标准

1. 不支持高级控制的模型，前端完全不显示对应控件；
2. 切换模型不会把旧模型参数带给新模型；
3. 伪造 unsupported/out-of-range 参数在 provider I/O 前被拒绝；
4. DeepSeek 等已确认模型的映射参数与 capability profile 一致；
5. Trace 只记录安全档位和能力版本，不记录思维链；
6. 旧客户端不传 `model_options` 时行为保持兼容；
7. 180 秒硬上限和 135 秒软水位在所有档位下继续生效；
8. 前后端 schema、类型检查、adapter 单测和端到端请求测试全部通过。

## 8. 推荐实施顺序

```text
能力 Schema 与 server-owned registry
→ 平台模型能力目录
→ BYOK 已确认模型能力映射
→ WorkflowRunRequest.model_options
→ 服务端 fail-closed 校验
→ Provider adapter 参数映射
→ 前端条件渲染与切换清理
→ 契约/单测/端到端回归
→ 小流量验证延迟、token、成本和答案质量
```
