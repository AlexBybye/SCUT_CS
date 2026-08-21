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
