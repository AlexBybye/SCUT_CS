<script setup lang="ts">
import { computed, ref } from "vue";
import type {
  AnswerBlock,
  AnswerBlockType,
  Citation,
  FeedbackType,
  WorkflowRunResult,
} from "../contracts";
import { submitFeedback } from "../api";
import type { WorkflowStreamState } from "../workflowStream";

const props = defineProps<{
  result: WorkflowRunResult | null;
  isRunning: boolean;
  streamState: WorkflowStreamState | null;
}>();

const feedbackType = ref<FeedbackType | null>(null);
const feedbackNote = ref("");
const feedbackSubmitted = ref(false);
const feedbackError = ref("");
const feedbackBusy = ref(false);

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

const citations = computed(() => props.result?.citations ?? []);
const externalResources = computed(() => props.result?.external_resources ?? []);
const coverageGaps = computed(() => props.result?.coverage_gaps ?? []);
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
          if (typedLength.value >= full) {
            stopTypeTimer();
          }
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

onBeforeUnmount(stopTypeTimer);

// 流动 trace：真实 trace 事件逐步展示；每步停留 0-2s 随机时长，
// 当前步展示满该时长且下一步已到达时立刻前进一格（不跳到最新、不跳步）。
const flowTrace = computed(() => props.result?.trace ?? props.streamState?.traceEvents ?? []);
const flowStep = ref(0);
let flowTimer: number | null = null;
let flowAdvanceAt = 0;
let flowStepDelay = 0;

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
    if (!running) {
      // 生成结束：不打断，让定时器继续逐条揭示剩余 trace。
      return;
    }
    // 开始生成：重置并启动定时器。
    stopFlowTimer();
    flowStep.value = 0;
    flowAdvanceAt = Date.now();
    flowStepDelay = Math.random() * 2000;
    flowTimer = window.setInterval(() => {
      if (Date.now() - flowAdvanceAt >= flowStepDelay) advanceFlowStep();
    }, 200);
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

onBeforeUnmount(stopFlowTimer);

// 运行中或收尾中逐步揭示（未到的框不显示）；历史数据直接展示全部。
const visibleFlowTrace = computed(() => {
  if (!props.isRunning && flowTimer === null) return flowTrace.value;
  return flowTrace.value.slice(0, flowStep.value + 1);
});

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

const answerBlockNotes: Record<AnswerBlockType, string> = {
  repository: "结论受仓库引用与证据状态约束",
  user_material: "仅基于你在本次 Workflow 提供的材料",
  general: "不作为课程仓库证据，也不附仓库引用",
  personalized_analysis: "结合本次作答或学习目标生成",
};

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
  <section class="result-shell" aria-labelledby="result-heading" aria-live="polite">
    <header class="result-header">
      <div>
        <h2 id="result-heading">回答、来源与 Trace</h2>
      </div>
      <div v-if="result || hasStreamActivity" class="status-pair" aria-label="运行状态">
        <span>{{ streamPhase }}</span>
        <span>{{ result?.answer_status ?? (isRunning ? "streaming" : streamError?.code ?? "partial") }}</span>
        <span v-if="result">证据状态：{{ result.evidence_status }}</span>
      </div>
    </header>

    <div v-if="isRunning && !hasStreamActivity" class="result-loading" role="status">
      <span class="skeleton-line skeleton-line-long"></span>
      <span class="skeleton-line"></span>
      <span class="skeleton-line skeleton-line-short"></span>
      <p>正在建立 Workflow 事件流。</p>
    </div>

    <div v-else-if="!result && !hasStreamActivity" class="result-empty">
      <p>尚未运行 Workflow。</p>
      <span>提交左侧表单后，这里会分别呈现回答、仓库引用、外部资源和安全 Trace。</span>
    </div>

    <template v-else>
      <p
        v-if="streamError"
        class="stream-message"
        :class="streamPhase === 'interrupted' ? 'stream-message-interrupted' : 'stream-message-error'"
        role="alert"
      >
        {{ streamError.detail }}
      </p>

      <section class="answer-stack" aria-label="回答内容">
        <article
          v-for="(block, index) in answerBlocks"
          :key="`${block.type}-${index}`"
          class="semantic-answer-block"
          :class="`semantic-answer-block-${block.type}`"
        >
          <div class="answer-meta">
            <span>{{ answerBlockLabels[block.type] }}</span>
            <span v-if="isRunning && !result">生成中</span>
          </div>
          <p class="answer-block-note">{{ answerBlockNotes[block.type] }}</p>
          <p class="answer-copy">
            {{ block.content }}
            <span
              v-if="isRunning && !result"
              class="stream-caret"
              aria-hidden="true"
            ></span>
          </p>
        </article>
        <p v-if="!answerBlocks.length" class="section-empty answer-pending">
          {{ isRunning ? "Workflow 已开始，正在等待回答内容。" : "本次没有返回回答内容。" }}
        </p>
      </section>

      <section
        v-if="coverageGaps.length"
        class="coverage-gap-block"
        aria-labelledby="coverage-gap-heading"
      >
        <h3 id="coverage-gap-heading">资料覆盖说明</h3>
        <ul>
          <li v-for="gap in coverageGaps" :key="gap">{{ gap }}</li>
        </ul>
      </section>

      <section v-if="result" class="result-section" aria-labelledby="citations-heading">
        <div class="result-section-heading">
          <h3 id="citations-heading">仓库引用</h3>
          <span>{{ citations.length }} 条</span>
        </div>
        <div v-if="citations.length" class="citation-list">
          <article v-for="citation in citations" :key="citation.citation_id" class="citation-item">
            <strong>{{ citation.source_title }}</strong>
            <span>{{ citation.course_title }}</span>
            <span>{{ citationLocator(citation) }}</span>
            <code>{{ citation.citation_id }}</code>
          </article>
        </div>
        <p v-else class="section-empty">本次没有仓库引用。</p>
      </section>

      <section v-if="result" class="result-section external-section" aria-labelledby="resources-heading">
        <div class="result-section-heading">
          <div>
            <h3 id="resources-heading">B站延伸学习</h3>
            <p>聚焦词只生成 B站匿名搜索入口；搜索结果未经本项目审核，也不属于仓库引用或回答证据。</p>
          </div>
          <span>{{ externalResources.length }} 条</span>
        </div>
        <div v-if="externalResources.length" class="resource-list">
          <a
            v-for="resource in externalResources"
            :key="resource.resource_id || resource.url"
            :href="resource.url"
            target="_blank"
            rel="noopener noreferrer"
            class="resource-item"
          >
            <span>
              <strong>{{ resource.title }}</strong>
              <small>{{ resource.matched_topic }} / 匿名搜索 / 结果未审核</small>
            </span>
            <span aria-hidden="true">查看搜索结果</span>
          </a>
        </div>
        <p v-else class="section-empty">本次没有返回外部资源。</p>
      </section>

      <section class="result-section" aria-labelledby="trace-heading">
        <div class="result-section-heading">
          <div>
            <h3 id="trace-heading">Trace</h3>
            <p>仅展示后端返回的安全字段。</p>
          </div>
          <span>{{ trace.length }} 个节点</span>
        </div>
        <ol v-if="trace.length" class="trace-list">
          <li v-for="(event, index) in trace" :key="event.event_id">
            <span class="trace-index">{{ String(index + 1).padStart(2, "0") }}</span>
            <div>
              <strong>{{ event.node }}</strong>
              <span>{{ event.status }}<template v-if="event.duration_ms !== undefined"> / {{ event.duration_ms }} ms</template></span>
              <details v-if="event.result && Object.keys(event.result).length">
                <summary>查看安全结果</summary>
                <pre>{{ JSON.stringify(event.result, null, 2) }}</pre>
              </details>
            </div>
          </li>
        </ol>
        <p v-else class="section-empty">
          {{ isRunning ? "正在等待第一个安全 Trace 事件。" : "本次没有 Trace 事件。" }}
        </p>
      </section>

      <section v-if="result && !isRunning" class="result-section feedback-section" aria-labelledby="feedback-heading">
        <div class="result-section-heading">
          <div>
            <h3 id="feedback-heading">回答反馈</h3>
            <p>反馈只进入待处理列表，不会自动修改知识库或后续回答。</p>
          </div>
          <span v-if="feedbackSubmitted" class="feedback-ok">已提交</span>
        </div>
        <div v-if="!feedbackSubmitted" class="feedback-form">
          <div class="feedback-buttons" role="group" aria-label="回答反馈类型">
            <button
              v-for="option in ([
                ['helpful', '有帮助'],
                ['not_helpful', '没帮助'],
                ['knowledge_error', '知识错误'],
                ['did_not_answer', '没回答问题'],
              ] as const)"
              :key="option[0]"
              type="button"
              :class="['feedback-button', { 'feedback-button-active': feedbackType === option[0] }]"
              :aria-pressed="feedbackType === option[0]"
              @click="feedbackType = feedbackType === option[0] ? null : option[0]"
            >
              {{ option[1] }}
            </button>
          </div>
          <textarea
            v-model="feedbackNote"
            class="feedback-note"
            rows="2"
            maxlength="2000"
            placeholder="可选：简短说明（如具体错误位置）"
          ></textarea>
          <div class="feedback-actions">
            <button
              type="button"
              class="feedback-submit"
              :disabled="!feedbackType || feedbackBusy"
              @click="sendFeedback"
            >
              {{ feedbackBusy ? "提交中…" : "提交反馈" }}
            </button>
            <span v-if="feedbackError" class="feedback-error" role="alert">{{ feedbackError }}</span>
          </div>
        </div>
        <div v-else class="feedback-done">
          <p>感谢反馈。修复问题后重新运行会生成新的回答尝试。</p>
          <button type="button" class="feedback-again" @click="resetFeedback">再提交一条</button>
        </div>
      </section>
    </template>
  </section>
</template>

<style>
.run {
  display: grid;
  gap: 10px;
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

/* 低矮窗口：trace 列表限制高度。 */
@media (max-height: 640px) {
  .flow-trace {
    max-height: 22vh;
    overflow-y: auto;
  }
}
</style>