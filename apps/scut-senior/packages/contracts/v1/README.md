# SCUT 老学长共享契约 V1

本目录冻结迭代 0 中语料校验、课程注册、Mock Workflow 和评测 Fixture 共同使用的最小契约。`v1` 表示字段语义版本，不代表真实 OAuth、真实模型、生产检索或课程已经开放。

## 课程注册

`courses.json` 是课程 ID、显示名、别名、仓库目录、开放开关和 Fixture 可用性的事实源。课程解析执行 Unicode NFKC、大小写折叠和空白移除，然后进行完整字符串匹配；禁止子串匹配。`course_id`、显示名和别名都可作为完整输入，解析结果始终是 `course_id`。

全部课程初始 `is_open=false`。只有 `linear_algebra` 的 `fixture_available=true`，它只说明存在合成测试数据，不表示真实课程资料可用。

## 枚举

`enums.json` 冻结五个 Workflow、回答方式、表达风格、知识范围、课程范围、模型来源、运行/回答/证据/Trace 状态、回答块来源类型、题目帮助层级，以及 manifest、locator 和 Bilibili 匿名搜索状态。Bilibili 状态只允许 `unreviewed_live_search`，不保留人工视频审核状态。Python、Worker 与 Vue 都有一致性测试；调用方不得通过自由字符串扩展枚举。

## Workflow 最小结构

请求字段固定为：

```text
workflow_type
course_scope
course_id
allowed_course_ids[]
conversation_id
model_source
provider_id
model_id
user_input
answer_mode
tone
knowledge_scope
include_bilibili_resources
context_refs
attachments[]
workflow_payload
```

`course_scope=single` 时必须提供一个 `course_id` 且 `allowed_course_ids=[]`；`course_scope=cross` 时 `course_id=null`，只能使用用户显式给出的至少两项 `allowed_course_ids[]`。`course_only` 必须令 `include_bilibili_resources=false`。

`workflow_payload` 由外层 `workflow_type` 判别，内部不重复 `kind`，且拒绝额外字段：

```text
knowledge_qa:
  question: string

exam_review:
  syllabus?: string | null
  exam_date?: date | null
  available_hours?: number | null
  goals: string[]
  weak_topics: string[]

problem_tutor:
  problem: string
  user_answer?: string | null
  help_level: concept | approach | step_by_step | full_explanation | answer_analysis
  problem_source?: string | null

mistake_review:
  problem: string
  original_answer: string
  reference_answer?: string | null
  review_focus?: string | null

temporary_material_reading:
  material_title?: string | null
  material_text: string
  reading_goal?: string | null
```

Runtime 只把与 `workflow_type` 匹配的分型 `workflow_payload` 作为检索与模型执行权威；外层 `user_input` 只保留原始用户消息和历史展示语义，冲突时不会进入检索查询或供应商 prompt。前端会把 `exam_review` 的主复习请求去重后放入 `goals[]` 供回答理解，但检索权威仍只取 `syllabus + weak_topics`；API 调用方不得只填写外层字段而省略对应的分型内容。

结果字段固定为：

```text
workflow_run_id
conversation_id
message_id
answer_id
run_status
answer_status
workflow_type
course_scope
course_ids[]
repository_answer
general_supplement
answer_blocks[]
workflow_output
evidence_status
citations[]
related_topics[]
related_questions[]
external_resources[]
coverage_gaps[]
trace[]
corpus_version
course_pack_version
workflow_version
model_source
model
availability_status
```

`answer_blocks[]` 每块使用字段 `type` 表示 `answer_block_type` 枚举值。`citations[]` 必须带 `course_id/course_title`，来源名称和 locator 由后端已验证元数据生成；`locator_type=none` 时不得补造页码或题号。`trace[].result` 使用拒绝额外字段的学生可见白名单，不接受 Key、token、prompt、堆栈或内部路径字段。

`schemas/workflow-request.schema.json`、`schemas/workflow-result.schema.json` 与 `schemas/workflow-stream-event.schema.json` 由可执行 Pydantic 模型生成，导出器同时补入 `model_validator` 中可由标准 JSON Schema 表达的 Workflow/scope/附件、Citation locator、Bilibili 资源和流事件 kind/payload/run 状态跨字段规则；修改 API 契约后必须重新生成，并运行 `make check-contracts` 防止提交陈旧 Schema。Pydantic 仍是运行时规范实现，例如 locator 的 `end >= start`、Bilibili 搜索 URL 的唯一 `keyword` 参数，以及流事件外层与 result 内层 `workflow_run_id` 相等关系由它执行；最后一项无法用标准 Draft 2020-12 的跨值相等关键字表达，前端流解析器也会再次校验。

Bilibili 资源只能进入 `external_resources[]`，不能进入 `citations[]` 或提高 `evidence_status`。本次模型只提供 0～3 个聚焦词；清洗后关键词非空时，后端只固定生成 1 条 `search.bilibili.com/all?keyword=...` 匿名搜索入口，不返回具体视频直链。搜索入口必须是 `resource_type=search`、`resource_id=null`、`review_status=unreviewed_live_search`，URL 不能来自模型或前端。项目不建设、审核或维护任何具体 Bilibili 视频资产。

## Manifest 和 Markdown

Manifest 表头及顺序固定为：

```text
source_id,course,title,original_path,format,document_role,year,output_md,locator_type,method,ocr_used,ocr_confidence,ocr_warning,status,reviewer,notes
```

状态只允许 `pending`、`passed`、`needs_fix`、`rejected`。只有结构校验通过且状态为 `passed` 的行进入 `searchable_sources`。

Markdown frontmatter 的规范课程字段是 `course_id`。为兼容资料流程，允许旧字段 `course`；如果两者同时出现，`course_id` 优先且二者必须解析到同一课程。其余规范字段为 `source_id`、`title`、`original_file`、`document_role`、可选 `year` 和 `locator_type`。`document_role` 与 `year` 不确定时允许留空，但不得臆测；frontmatter 仍需保留 `document_role` 字段。

- `page`、`slide` 必须是正整数并严格递增；
- `question` 在单文件内唯一；
- H1-H6 相邻向下展开时不能跳级，向上收束允许跨级；
- `locator_type=none` 表示没有可靠精确定位，后续只能退化显示资料名或标题；
- `source_id`、课程、标题和原始路径必须与 manifest 一致；
- `source_title` 只取自 manifest 的 `title`；
- 校验器只读取 `output_md`，不会打开 `original_path` 指向的真实原件。

## Fixture 与评测

`tests/fixtures/corpus/` 只包含合成线性代数内容。测试 manifest 中的 `passed` 只用于验证允许路径，不对应任何真实资料。

评测 case 的七类最小覆盖固定为：

1. `course_knowledge`；
2. `past_paper_question`；
3. `sparse_general_supplement`；
4. `insufficient_evidence`；
5. `multi_turn_followup`；
6. `cross_course_scope`；
7. `source_marking`。

`schemas/evaluation-case.schema.json` 和 `schemas/evaluation-runner.schema.json` 分别约束单个 case 与 runner 配置。它们在迭代 0 只冻结契约样例，尚未实现评测执行器，也不表示七类预期已经跑通。Bilibili 运行时只遵守上文的 search-only Workflow 结果契约；不再规划具体视频目录及其维护契约。

评测 case 的 `course_id` 与 `allowed_course_ids[]` 直接复用 Workflow 请求不变量：`single` 使用一个 `course_id` 和空数组，`cross` 使用 `course_id=null` 和显式课程集合；评测 runner 不得自行扩大课程范围。
