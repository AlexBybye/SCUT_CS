<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from "vue";
import type {
  AnswerBlock,
  AnswerBlockType,
  AnswerMode,
  Citation,
  FeedbackType,
  Tone,
  WorkflowRunResult,
} from "../contracts";
import { submitFeedback } from "../api";
import { copyWorkflowOutput, formatWorkflowOutputForCopy } from "../workflowOutputCopy";
import {
  examReviewPathLabel,
  locatorLabel as examLocatorLabel,
  parseExamReviewPlan,
  priorityStepLabel,
} from "../examReviewPlan";
import { renderAnswerMarkdown } from "../markdown";
import { createBottomFollower } from "../scrollFollow";
import type { WorkflowStreamState } from "../workflowStream";

const props = defineProps<{
  result: WorkflowRunResult | null;
  isRunning: boolean;
  streamState: WorkflowStreamState | null;
  answerMode?: AnswerMode | null;
  tone?: Tone | null;
}>();

const emit = defineEmits<{
  (event: "migrate", result: WorkflowRunResult): void;
  (event: "save-private", result: WorkflowRunResult): void;
}>();

const feedbackType = ref<FeedbackType | null>(null);
const feedbackNote = ref("");
const feedbackSubmitted = ref(false);
const feedbackError = ref("");
const feedbackBusy = ref(false);
const copyMessage = ref("");
const copyError = ref("");
let copyMessageTimer: number | null = null;

async function copyCurrentOutput(): Promise<void> {
  const text = formatWorkflowOutputForCopy(answerBlocks.value, citations.value);
  copyError.value = "";
  copyMessage.value = "";
  try {
    await copyWorkflowOutput(text);
    copyMessage.value = "已复制";
    if (copyMessageTimer !== null) window.clearTimeout(copyMessageTimer);
    copyMessageTimer = window.setTimeout(() => {
      copyMessage.value = "";
      copyMessageTimer = null;
    }, 1800);
  } catch (error) {
    copyError.value = error instanceof Error ? error.message : "复制失败，请手动选择回答文本。";
  }
}

async function sendFeedback(): Promise<void> {
  if (!props.result || !feedbackType.value) return;
  feedbackBusy.value = true;
  feedbackError.value = "";
  try {
    await submitFeedback(
      props.result.workflow_run_id,
      feedbackType.value,
      feedbackNote.value,
    );
    feedbackSubmitted.value = true;
  } catch (error) {
    feedbackError.value = error instanceof Error ? error.message : "反馈提交失败。";
  } finally {
    feedbackBusy.value = false;
  }
}

function resetFeedback(): void {
  feedbackType.value = null;
  feedbackNote.value = "";
  feedbackSubmitted.value = false;
  feedbackError.value = "";
}

const feedbackOptions = [
  ["helpful", "有帮助"],
  ["not_helpful", "没帮助"],
  ["knowledge_error", "知识错误"],
  ["did_not_answer", "没回答问题"],
] as const;

const citations = computed(() => props.result?.citations ?? []);
const externalResources = computed(() => props.result?.external_resources ?? []);
const coverageGaps = computed(() => props.result?.coverage_gaps ?? []);
// 迭代 5：备考复习计划（系统生成）。形状不符时为 null，面板整体隐藏。
const examPlan = computed(() =>
  parseExamReviewPlan(props.result?.workflow_output?.exam_review ?? null),
);
const trace = computed(() => props.result?.trace ?? props.streamState?.traceEvents ?? []);
const streamError = computed(() => props.result ? null : props.streamState?.error ?? null);
const streamPhase = computed(() => props.result?.run_status ?? props.streamState?.phase ?? "idle");
const hasStreamActivity = computed(() => Boolean(
  props.streamState && (
    props.streamState.phase !== "idle" ||
    props.streamState.answerBlocks.length ||
    props.streamState.traceEvents.length
  ),
));

// 打字机：生成中逐字缓慢揭示正文最后一块；结果落定后若尚未打完则继续打完，
// 历史加载（无实时生成）则直接显示完整。目标文本缓存为 computed。
const typewriterTarget = computed<string>(() => {
  const blocks = props.result?.answer_blocks.length
    ? props.result.answer_blocks
    : (props.streamState?.answerBlocks ?? []);
  const last = blocks[blocks.length - 1];
  return last ? last.content : "";
});
const typedLength = ref(0);
let typeTimer: number | null = null;
let typewriterFinishing = false;

function stopTypeTimer(): void {
  if (typeTimer !== null) {
    window.clearInterval(typeTimer);
    typeTimer = null;
  }
  typewriterFinishing = false;
}

watch(
  () => [props.isRunning, typewriterTarget.value] as const,
  ([running, target]) => {
    if (!target) {
      typedLength.value = 0;
      stopTypeTimer();
      return;
    }
    if (running) {
      typewriterFinishing = false;
      if (typedLength.value > target.length) typedLength.value = target.length;
      if (typeTimer === null && typedLength.value < target.length && typeof window !== "undefined") {
        typeTimer = window.setInterval(() => {
          const full = typewriterTarget.value.length;
          if (typedLength.value < full) {
            if (typewriterFinishing) {
              // 收尾阶段：按剩余量加速，约 18 个 tick（≈1.26s）内打完，
              // 避免运行已结束却还以 2 字/70ms 慢爬一段很长的 backlog。
              const remaining = full - typedLength.value;
              typedLength.value = Math.min(
                full,
                typedLength.value + Math.max(2, Math.ceil(remaining / 18)),
              );
            } else {
              typedLength.value = Math.min(full, typedLength.value + 2);
            }
          }
          if (typedLength.value >= full) stopTypeTimer();
        }, 70);
      }
    } else if (typeTimer !== null) {
      // 不在生成但定时器仍在跑（刚结束）：标记收尾中，不打断让它继续打完。
      typewriterFinishing = true;
    } else if (!typewriterFinishing) {
      // 不在生成、没有进行中的打字、且不在收尾中：直接完整显示（历史/初始）。
      typedLength.value = target.length;
    }
  },
  { immediate: true },
);

onBeforeUnmount(() => {
  stopTypeTimer();
  if (copyMessageTimer !== null) window.clearTimeout(copyMessageTimer);
});

// 流动 trace：运行中真实事件逐步展示（每步随机停留 ≤2s、不跳步）；
// 运行一结束就停止逐条揭示，立刻完整展示全部 trace（见 visibleFlowTrace）。
const flowTrace = computed(() => props.result?.trace ?? props.streamState?.traceEvents ?? []);
const flowStep = ref(0);
let flowTimer: number | null = null;
let flowAdvanceAt = 0;
let flowStepDelay = 0;

// trace 内滚跟随：与大滚动条同一套贴底机制，0.5s 节流——步进再密也至多
// 半秒写一次 scrollTop。是否跟随只看 tracePinned，而它只在用户真实的
// scroll 事件里重估：内容追加不触发 scroll，pinned 不会被新步骤挤掉，
// 流式期间因此能稳定追到最新一步；上翻阅读即解除跟随，滚回底部自动恢复。
const traceListEl = ref<HTMLElement | null>(null);
const tracePinned = ref(true);

function onTraceScroll(): void {
  const el = traceListEl.value;
  if (!el) return;
  tracePinned.value = el.scrollHeight - el.scrollTop - el.clientHeight < 32;
}

const traceFollower = createBottomFollower(() => traceListEl.value, 500, {
  shouldFollow: () => tracePinned.value,
});

function stopFlowTimer(): void {
  if (flowTimer !== null) {
    window.clearInterval(flowTimer);
    flowTimer = null;
  }
}

function advanceFlowStep(): void {
  if (flowStep.value < flowTrace.value.length - 1) {
    flowStep.value += 1;
    flowAdvanceAt = Date.now();
    flowStepDelay = Math.random() * 2000;
  } else {
    stopFlowTimer();
  }
}

watch(
  () => props.isRunning,
  (running) => {
    stopFlowTimer();
    traceFollower.stop();
    if (!running) {
      // 生成结束：全部 trace 立刻渲染并强制回到最新步骤；盒子限高内滚，
      // 整段插入不会撑高页面造成滚动跳动。
      tracePinned.value = true;
      traceFollower.force();
      return;
    }
    // 开始生成：重置并启动揭示定时器与内滚跟随（新一轮默认贴底跟随）。
    flowStep.value = 0;
    tracePinned.value = true;
    flowAdvanceAt = Date.now();
    flowStepDelay = Math.random() * 2000;
    flowTimer = window.setInterval(() => {
      if (Date.now() - flowAdvanceAt >= flowStepDelay) advanceFlowStep();
    }, 200);
    traceFollower.start();
  },
  { immediate: true },
);

watch(
  () => flowTrace.value.length,
  () => {
    if (!props.isRunning || !flowTrace.value.length) return;
    if (flowStep.value < flowTrace.value.length - 1 && Date.now() - flowAdvanceAt >= flowStepDelay) {
      advanceFlowStep();
    }
  },
);

onBeforeUnmount(() => {
  stopFlowTimer();
  traceFollower.stop();
});

// 运行中只显示已揭示的步骤；一旦不在运行（回答输出完成/历史加载），立刻展示全部。
const visibleFlowTrace = computed(() =>
  props.isRunning ? flowTrace.value.slice(0, flowStep.value + 1) : flowTrace.value,
);

function traceStepHint(event: { node: string; status: string }): string {
  const text = `${event.node} ${event.status}`.toLowerCase();
  if (text.includes("retriev") || text.includes("检索")) {
    return event.status === "completed" ? "检索完成" : "正在检索";
  }
  if (text.includes("guard") || text.includes("evidence") || text.includes("证据")) {
    return text.includes("retry") || text.includes("重试") ? "发现证据不足，正在补充" : "正在检查证据";
  }
  if (text.includes("generat") || text.includes("answer") || text.includes("回答")) {
    return event.status === "completed" ? "回答完成" : "正在生成回答";
  }
  if (text.includes("finish") || text.includes("完成")) return "步骤完成";
  return event.status === "completed" ? "已完成" : "处理中";
}

const answerBlocks = computed<AnswerBlock[]>(() => {
  if (props.result?.answer_blocks.length) return props.result.answer_blocks;
  if (props.streamState?.answerBlocks.length) {
    return props.streamState.answerBlocks.filter((block) => block.content.length > 0);
  }
  const legacyBlocks: AnswerBlock[] = [];
  if (props.result?.repository_answer) {
    legacyBlocks.push({ type: "repository", content: props.result.repository_answer });
  }
  if (props.result?.general_supplement) {
    legacyBlocks.push({ type: "general", content: props.result.general_supplement });
  }
  return legacyBlocks;
});

const answerBlockLabels: Record<AnswerBlockType, string> = {
  repository: "课程资料回答",
  user_material: "用户材料",
  general: "通用知识补充",
  personalized_analysis: "个性化分析",
};

const answerModeLabels: Record<AnswerMode, string> = {
  concise: "简短",
  detailed: "详细",
  example: "举例",
  step_by_step: "分步骤",
};

const answerModeLabel = computed(() => (
  props.answerMode ? answerModeLabels[props.answerMode] : null
));

const toneLabels: Record<Tone, string> = {
  teaching_assistant: "助教",
  senior_student: "学长",
  study_partner: "复习搭子",
};

const toneLabel = computed(() => (
  props.tone ? toneLabels[props.tone] : null
));

const answerBlockNotes: Record<AnswerBlockType, string> = {
  repository: "结论受仓库引用与证据状态约束",
  user_material: "仅基于你在本次 Workflow 提供的材料",
  general: "不作为课程仓库证据，也不附仓库引用",
  personalized_analysis: "结合本次作答或学习目标生成",
};

function renderedAnswer(content: string): string {
  return renderAnswerMarkdown(content);
}

function displayedBlockContent(block: AnswerBlock, index: number): string {
  if (index === answerBlocks.value.length - 1 && typedLength.value < block.content.length) {
    return block.content.slice(0, typedLength.value);
  }
  return block.content;
}

function citationLocator(citation: Citation): string {
  const parts: string[] = [];
  if (citation.locator_start !== undefined && citation.locator_start !== null) {
    const end = citation.locator_end;
    const range = end !== undefined && end !== null && end !== citation.locator_start
      ? `${citation.locator_start}-${end}`
      : `${citation.locator_start}`;
    if (citation.locator_type === "page") parts.push(`页码 ${range}`);
    if (citation.locator_type === "slide") parts.push(`幻灯片 ${range}`);
    if (citation.locator_type === "question" && !citation.question_id) parts.push(`题号 ${range}`);
    if (citation.locator_type === "heading" && !citation.heading_path?.length) parts.push(`章节 ${range}`);
  }
  if (citation.question_id) parts.push(`题号 ${citation.question_id}`);
  if (citation.heading_path?.length) {
    parts.push(`章节 ${citation.heading_path.join(" / ")}`);
  }
  return parts.length ? parts.join(" · ") : "资料名定位";
}

</script>

<template>
  <section class="run" aria-labelledby="result-heading" aria-live="polite">
    <header class="run-head">
      <h2 id="result-heading" class="run-head-label">回答、来源与 Trace</h2>
      <template v-if="result || hasStreamActivity">
        <span class="chip chip-accent">{{ streamPhase }}</span>
        <span class="chip">
          {{ result?.answer_status ?? (isRunning ? "streaming" : streamError?.code ?? "partial") }}
        </span>
        <span v-if="result" class="chip">证据状态：{{ result.evidence_status }}</span>
        <span v-if="answerModeLabel" class="chip">输出偏好：{{ answerModeLabel }}</span>
        <span v-if="toneLabel" class="chip">表达风格：{{ toneLabel }}</span>
      </template>
    </header>

    <div v-if="isRunning || flowTrace.length" class="flow" aria-live="polite">
      <div v-if="isRunning" class="flow-head">
        <span class="flow-dots" aria-hidden="true"><i></i><i></i><i></i></span>
        <span class="flow-label">思考中</span>
      </div>
      <ol
        v-if="visibleFlowTrace.length"
        ref="traceListEl"
        class="flow-trace"
        @scroll="onTraceScroll"
      >
        <li
          v-for="(event, index) in visibleFlowTrace"
          :key="event.event_id"
          class="flow-step"
          :class="{ 'flow-step-on': isRunning && index === flowStep }"
        >
          <div class="flow-step-row">
            <strong>{{ event.node }} · {{ traceStepHint(event) }}</strong>
            <span>{{ isRunning && index === flowStep ? "运行中" : event.status }}</span>
            <details v-if="event.result && Object.keys(event.result).length" class="flow-result">
              <summary>查看安全结果</summary>
              <pre>{{ JSON.stringify(event.result, null, 2) }}</pre>
            </details>
          </div>
        </li>
      </ol>
      <p v-else-if="isRunning" class="flow-wait">正在等待第一个安全 Trace 事件。</p>
    </div>

    <div v-if="isRunning && !hasStreamActivity" class="skeleton" role="status">
      <span></span>
      <span></span>
      <span></span>
      <p>正在建立 Workflow 事件流。</p>
    </div>

    <p v-else-if="!result && !hasStreamActivity" class="empty-line">
      本次会话还没有回答记录。
    </p>

    <template v-else>
      <p
        v-if="streamError"
        class="note"
        :class="streamPhase === 'interrupted' ? 'note-warn' : 'note-bad'"
        role="alert"
      >
        {{ streamError.detail }}
      </p>

      <article
        v-for="(block, index) in answerBlocks"
        :key="`${block.type}-${index}`"
        class="block"
        :class="`block-${block.type}`"
      >
        <div class="block-head">
          <strong>{{ answerBlockLabels[block.type] }}</strong>
          <span class="block-note">{{ answerBlockNotes[block.type] }}</span>
          <span v-if="isRunning && !result" class="chip chip-accent">生成中</span>
        </div>
        <div class="block-body">
          <div class="markdown-body" v-html="renderedAnswer(displayedBlockContent(block, index))"></div>
          <span v-if="isRunning && !result" class="caret" aria-hidden="true"></span>
        </div>
      </article>
      <p v-if="!answerBlocks.length" class="empty-line">
        {{ isRunning ? "Workflow 已开始，正在等待回答内容。" : "本次没有返回回答内容。" }}
      </p>

      <div v-if="result && !isRunning && answerBlocks.length" class="result-actions" aria-label="本轮回答操作">
        <button type="button" class="btn btn-quiet" @click="copyCurrentOutput">复制本轮输出</button>
        <button type="button" class="btn btn-quiet" @click="emit('migrate', result)">迁出到新对话</button>
        <button type="button" class="btn btn-quiet" @click="emit('save-private', result)">加入私人知识库</button>
        <span v-if="copyMessage" class="note note-ok" role="status">{{ copyMessage }}</span>
        <span v-if="copyError" class="note note-bad" role="alert">{{ copyError }}</span>
      </div>

      <section
        v-if="coverageGaps.length"
        class="note note-warn"
        aria-labelledby="coverage-gap-heading"
      >
        <h3 id="coverage-gap-heading">资料覆盖说明</h3>
        <ul>
          <li v-for="gap in coverageGaps" :key="gap">{{ gap }}</li>
        </ul>
      </section>

      <div class="evidence">
        <details v-if="result" class="evidence-group">
          <summary>
            <span>仓库引用</span>
            <span class="chip">{{ citations.length }}</span>
          </summary>
          <div class="evidence-body">
            <div v-if="citations.length" class="cites">
              <article v-for="citation in citations" :key="citation.citation_id" class="cite">
                <strong>{{ citation.source_title }}</strong>
                <span>{{ citation.course_title }}</span>
                <span>{{ citationLocator(citation) }}</span>
                <code>{{ citation.citation_id }}</code>
              </article>
            </div>
            <p v-else class="empty-line">本次没有仓库引用。</p>
          </div>
        </details>

        <details v-if="result && examPlan" class="evidence-group">
          <summary>
            <span>备考复习计划（系统生成）</span>
            <span class="chip">{{ examPlan.knowledge_points.length }}</span>
          </summary>
          <p class="evidence-group-note">{{ examPlan.scope_statement }}</p>
          <div class="evidence-body exam-plan" aria-label="备考复习计划详情">
            <p class="exam-plan-path">
              <strong>{{ examReviewPathLabel(examPlan.path) }}</strong>
              <span v-if="examPlan.priority_order.length" class="exam-plan-chain">
                证据顺序：{{ examPlan.priority_order.map(priorityStepLabel).join(" → ") }}
              </span>
            </p>
            <div v-if="examPlan.past_exam_stats.question_count" class="exam-plan-stats">
              <p>
                样本年份 {{ examPlan.past_exam_stats.sample_years.join("、") }}
                （{{ examPlan.past_exam_stats.year_count }} 个年份、{{
                  examPlan.past_exam_stats.question_count
                }}
                道题，客观出现次数）
              </p>
              <ul v-if="examPlan.past_exam_stats.year_coverage.length">
                <li v-for="item in examPlan.past_exam_stats.year_coverage" :key="item.year">
                  {{ item.year }}：{{ item.count }} 题
                </li>
              </ul>
              <ul v-if="examPlan.past_exam_stats.type_distribution.length">
                <li v-for="item in examPlan.past_exam_stats.type_distribution" :key="item.key">
                  {{ item.label }}：{{ item.count }} 次
                </li>
              </ul>
            </div>
            <ol v-if="examPlan.knowledge_points.length" class="exam-plan-points">
              <li v-for="(point, index) in examPlan.knowledge_points" :key="point.topic + index">
                <strong>【第 {{ point.layer }} 层】{{ point.topic }}</strong>
                <small v-if="point.order_reasons.length">
                  （{{ point.order_reasons.join("、") }}）
                </small>
                <ul>
                  <li v-for="(loc, locIndex) in point.material_locations.slice(0, 3)" :key="locIndex">
                    《{{ loc.source_title }}》{{ examLocatorLabel(loc.locator_type, loc.locator_start) }}
                  </li>
                  <li v-for="question in point.questions.slice(0, 4)" :key="question.question_id">
                    真题 {{ question.question_id }}<template v-if="question.year">（{{ question.year }}）</template>
                  </li>
                </ul>
              </li>
            </ol>
            <div
              v-else-if="examPlan.past_exam_stats.question_groups.length"
              class="exam-plan-groups"
            >
              <p class="empty-line">
                当前历年题语料没有可按知识点归组的标题；以下题组是仅有的客观结构，题型不是知识点。
              </p>
              <ul>
                <li v-for="group in examPlan.past_exam_stats.question_groups" :key="group.source_id">
                  《{{ group.source_title }}》
                  <template v-if="group.year">（{{ group.year }}）</template>
                  ：共 {{ group.question_count || group.questions.length }} 题
                  <small v-if="group.questions.length">
                    代表题号：{{ group.questions.map((q) => q.question_id).join("、") }}
                  </small>
                </li>
              </ul>
            </div>
            <ul v-if="examPlan.review_suggestions.length" class="exam-plan-suggestions">
              <li v-for="suggestion in examPlan.review_suggestions" :key="suggestion">
                {{ suggestion }}
              </li>
            </ul>
            <div v-if="examPlan.uncovered_items.length" class="note note-warn exam-plan-uncovered">
              <h4>未覆盖内容</h4>
              <ul>
                <li v-for="item in examPlan.uncovered_items" :key="item">{{ item }}</li>
              </ul>
            </div>
            <p class="exam-plan-boundary">{{ examPlan.ai_sample_policy }}</p>
          </div>
        </details>

        <details v-if="result" class="evidence-group">
          <summary>
            <span>B站延伸学习</span>
            <span class="chip">{{ externalResources.length }}</span>
          </summary>
          <p class="evidence-group-note">
            聚焦词只生成 B站匿名搜索入口；搜索结果未经本项目审核，也不属于仓库引用或回答证据。
          </p>
          <div class="evidence-body">
            <div v-if="externalResources.length" class="links">
              <a
                v-for="resource in externalResources"
                :key="resource.resource_id || resource.url"
                :href="resource.url"
                target="_blank"
                rel="noopener noreferrer"
                class="link-row"
              >
                <span>
                  <strong>{{ resource.title }}</strong>
                  <small>{{ resource.matched_topic }} </small>
                </span>
                <span aria-hidden="true">查看搜索结果</span>
              </a>
            </div>
            <p v-else class="empty-line">本次没有返回外部资源。</p>
          </div>
        </details>
      </div>

      <details v-if="result && !isRunning" class="evidence-group" aria-labelledby="feedback-heading">
        <summary>
          <span id="feedback-heading">回答反馈</span>
          <span v-if="feedbackSubmitted" class="chip chip-ok">已提交</span>
        </summary>
        <p class="evidence-group-note">反馈只进入待处理列表，不会自动修改知识库或后续回答。</p>
        <div class="evidence-body">
          <div v-if="!feedbackSubmitted" class="fb">
            <div class="seg" role="group" aria-label="回答反馈类型">
              <label v-for="option in feedbackOptions" :key="option[0]" class="seg-item">
                <input
                  v-model="feedbackType"
                  type="radio"
                  name="feedback-type"
                  :value="option[0]"
                />
                <span>{{ option[1] }}</span>
              </label>
            </div>
            <label class="visually-hidden" for="feedback-note">反馈说明</label>
            <textarea
              id="feedback-note"
              v-model="feedbackNote"
              class="fb-note"
              rows="2"
              maxlength="2000"
              placeholder="可选：简短说明，例如具体错误位置"
            ></textarea>
            <div class="fb-row">
              <button
                type="button"
                class="btn btn-primary"
                :disabled="!feedbackType || feedbackBusy"
                @click="sendFeedback"
              >
                {{ feedbackBusy ? "提交中" : "提交反馈" }}
              </button>
              <span v-if="feedbackError" class="note note-bad" role="alert">
                {{ feedbackError }}
              </span>
            </div>
          </div>
          <div v-else class="fb-row">
            <p class="empty-line">感谢反馈。修复问题后重新运行会生成新的回答尝试。</p>
            <button type="button" class="btn btn-quiet" @click="resetFeedback">再提交一条</button>
          </div>
        </div>
      </details>
    </template>
  </section>
</template>

<style>
.run {
  display: grid;
  gap: 10px;
}

.result-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.result-actions .note {
  margin: 0;
  padding: 4px 8px;
  font-size: var(--fs-2xs);
}

.run-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 5px;
  padding-bottom: 7px;
  border-bottom: 1px solid var(--line);
}

.run-head-label {
  margin-right: auto;
  color: var(--text-muted);
  font-size: var(--fs-2xs);
  font-weight: 650;
}

/* 回答块：左侧色条区分证据来源，无卡片框。 */
.block {
  padding: 2px 0 2px 12px;
  border-left: 2px solid var(--line-strong);
}

.block-repository {
  border-left-color: var(--accent);
}

.block-user_material {
  border-left-color: var(--warn-line);
}

.block-personalized_analysis {
  border-left-color: var(--ok-line);
}

.block-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 7px;
  margin-bottom: 2px;
}

.block-head strong {
  font-size: var(--fs-xs);
  font-weight: 650;
}

.block-note {
  color: var(--text-soft);
  font-size: var(--fs-2xs);
}

.block-body {
  font-size: var(--fs-md);
  line-height: 1.75;
  overflow-wrap: anywhere;
}

.markdown-body > :first-child {
  margin-top: 0;
}

.markdown-body > :last-child {
  margin-bottom: 0;
}

.markdown-body p,
.markdown-body ul,
.markdown-body ol,
.markdown-body pre,
.markdown-body blockquote {
  margin: 0.55em 0;
}

.markdown-body blockquote {
  padding: 0.5rem 0.75rem;
  border-inline-start: 3px solid var(--accent);
  border-radius: var(--r-sm);
  background: var(--accent-wash);
  color: var(--text);
}

.markdown-body blockquote > p {
  margin: 0;
}

.markdown-body pre,
.markdown-body code {
  font-family: var(--font-mono);
}

.markdown-body pre {
  padding: 0.6rem 0.75rem;
  overflow-x: auto;
  background: var(--sunken);
  border: 1px solid var(--line);
  border-radius: var(--r-sm);
}

.markdown-body :not(pre) > code {
  padding: 0.08em 0.3em;
  background: var(--sunken);
  border-radius: var(--r-xs);
}

.markdown-body .katex-display {
  overflow-x: auto;
  overflow-y: hidden;
  margin: 0.75em 0;
}

.caret {
  display: inline-block;
  width: 2px;
  height: 1em;
  margin-left: 2px;
  vertical-align: -0.14em;
  background: var(--accent);
}

.caret[hidden] {
  display: none;
}

/* 骨架屏：形状对齐最终回答，不是转圈。 */
.skeleton {
  display: grid;
  gap: 8px;
  padding-left: 12px;
  border-left: 2px solid var(--line);
}

.skeleton span {
  display: block;
  height: 9px;
  border-radius: var(--r-sm);
  background: var(--sunken);
}

.skeleton span:nth-child(1) {
  width: 100%;
}

.skeleton span:nth-child(2) {
  width: 82%;
}

.skeleton span:nth-child(3) {
  width: 54%;
}

.skeleton p {
  color: var(--text-muted);
  font-size: var(--fs-xs);
}

/* 动效有动机：shimmer 表示「正在生成」，光标表示「还在流」。两者都门控。 */
@media (prefers-reduced-motion: no-preference) {
  .skeleton span {
    background: linear-gradient(
      100deg,
      var(--sunken) 42%,
      color-mix(in srgb, var(--sunken) 55%, var(--line)) 50%,
      var(--sunken) 58%
    );
    background-size: 220% 100%;
    animation: shimmer 1.5s ease-in-out infinite;
  }

  @keyframes shimmer {
    from {
      background-position: 130% 0;
    }
    to {
      background-position: -90% 0;
    }
  }

  .caret {
    animation: caret 1.1s steps(2, jump-none) infinite;
  }

  @keyframes caret {
    50% {
      opacity: 0.2;
    }
  }
}

/* 证据区：可折叠，默认收起，避免抢走回答的注意力。 */
.evidence {
  display: grid;
  gap: 2px;
}

.evidence-group {
  border-top: 1px solid var(--line);
}

.evidence-group > summary {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 7px 2px;
  color: var(--text-muted);
  font-size: var(--fs-xs);
  font-weight: 600;
  list-style: none;
}

.evidence-group > summary::-webkit-details-marker {
  display: none;
}

.evidence-group > summary::before {
  content: "";
  width: 0;
  height: 0;
  flex: 0 0 auto;
  border-top: 4px solid transparent;
  border-bottom: 4px solid transparent;
  border-left: 5px solid currentColor;
}

.evidence-group[open] > summary::before {
  transform: rotate(90deg);
}

.evidence-group > summary:hover {
  color: var(--text);
}

.evidence-group-note {
  padding: 0 2px 8px;
  color: var(--text-soft);
  font-size: var(--fs-2xs);
  line-height: 1.55;
}

.evidence-body {
  padding-bottom: 10px;
}

/* 备考复习计划：系统生成的结构化统计，紧凑列表，不做落地页造型。 */
.exam-plan {
  display: grid;
  gap: 9px;
  font-size: var(--fs-xs);
}

.exam-plan-path {
  display: grid;
  gap: 2px;
}

.exam-plan-chain {
  color: var(--text-muted);
  font-size: var(--fs-2xs);
}

.exam-plan-stats ul,
.exam-plan-points ul,
.exam-plan-suggestions {
  margin: 4px 0 0;
  padding-left: 18px;
  display: grid;
  gap: 3px;
  color: var(--text-soft);
}

.exam-plan-points > li + li,
.exam-plan-suggestions li + li {
  margin-top: 5px;
}

/* 题组：语料没有知识点标题时的客观回退结构。 */
.exam-plan-groups ul {
  margin: 4px 0 0;
  padding-left: 18px;
  display: grid;
  gap: 4px;
  color: var(--text-soft);
}

.exam-plan-groups small {
  color: var(--text-muted);
}

.exam-plan-uncovered h4 {
  font-size: var(--fs-xs);
  font-weight: 650;
  margin-bottom: 4px;
}

.exam-plan-boundary {
  color: var(--text-muted);
  font-size: var(--fs-2xs);
  line-height: 1.55;
}

/* 引用：两列网格，紧凑。 */
.cites {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(232px, 1fr));
  gap: 6px;
}

.cite {
  display: grid;
  gap: 2px;
  min-width: 0;
  padding: 7px 9px;
  border-radius: var(--r-sm);
  background: var(--sunken);
}

.cite strong {
  font-size: var(--fs-xs);
  font-weight: 650;
}

.cite span {
  color: var(--text-muted);
  font-size: var(--fs-2xs);
}

.cite code {
  color: var(--text-soft);
  font-size: var(--fs-2xs);
  overflow-wrap: anywhere;
}

/* 外部资源：行式链接。 */
.links {
  display: grid;
  gap: 4px;
}

.link-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 7px 9px;
  border: 1px solid var(--line);
  border-radius: var(--r-sm);
  background: var(--raised);
  text-decoration: none;
}

.link-row:hover {
  border-color: var(--accent);
}

.link-row > span:first-child {
  display: grid;
  gap: 1px;
  min-width: 0;
}

.link-row strong {
  font-size: var(--fs-xs);
  font-weight: 650;
}

.link-row small,
.link-row > span:last-child {
  color: var(--text-muted);
  font-size: var(--fs-2xs);
}

.link-row > span:last-child {
  flex: 0 0 auto;
  margin-left: auto;
  color: var(--accent);
}

.empty-line {
  color: var(--text-muted);
  font-size: var(--fs-xs);
}

/* 反馈：一行分段 + 可选备注。 */
.fb {
  display: grid;
  gap: 7px;
}

.fb-row {
  display: flex;
  align-items: center;
  gap: 7px;
}

.fb-note {
  min-height: 46px;
}

/* ── 流动 trace ─────────────────────────────────────── */

.flow {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 12px 0;
  padding: 10px 12px;
  border: 1px solid var(--accent-wash);
  border-radius: var(--r-md);
  background: var(--accent-wash);
  color: var(--accent);
}

.flow-head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.flow-dots {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.flow-dots i {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
  animation: flow-dot-breathe 1.2s ease-in-out infinite;
}

.flow-dots i:nth-child(2) {
  animation-delay: 0.2s;
}

.flow-dots i:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes flow-dot-breathe {
  0%,
  100% {
    opacity: 0.25;
    transform: translateY(0);
  }
  50% {
    opacity: 1;
    transform: translateY(-2px);
  }
}

.flow-label {
  font-size: var(--fs-xs);
  font-weight: 700;
  white-space: nowrap;
}

.flow-trace {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 0;
  list-style: none;
  /* 限高内滚：完成瞬间整段揭示全部 trace，也不会把记录区顶得一泻千里地跳动；
     滚到边界不 chaining，内滚不会突然带动整页。 */
  max-height: 240px;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.flow-step {
  border: 1px solid transparent;
  border-radius: var(--r-sm);
  padding: 6px 8px;
  color: var(--text-muted);
  font-size: var(--fs-xs);
}

.flow-step-on {
  border-color: color-mix(in srgb, var(--accent) 30%, transparent);
  background: var(--raised);
  color: var(--text);
}

.flow-step-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.flow-step-row strong {
  font-family: var(--font-mono);
  font-weight: 650;
}

.flow-step-row > span {
  color: var(--text-soft);
}

.flow-result {
  flex-basis: 100%;
}

.flow-result summary {
  cursor: pointer;
  color: var(--accent);
  font-size: var(--fs-xs);
}

.flow-result pre {
  margin: 6px 0 0;
  padding: 8px;
  border-radius: var(--r-sm);
  background: var(--sunken);
  color: var(--text);
  font-family: var(--font-mono);
  font-size: var(--fs-2xs);
  overflow: auto;
  white-space: pre-wrap;
}

.flow-wait {
  margin: 0;
  color: var(--text-muted);
  font-size: var(--fs-xs);
}

@media (max-width: 719px) {
  .cites {
    grid-template-columns: 1fr;
  }
}

/* 低矮窗口：trace 列表限高更紧。 */
@media (max-height: 640px) {
  .flow-trace {
    max-height: 22vh;
  }
}
</style>
