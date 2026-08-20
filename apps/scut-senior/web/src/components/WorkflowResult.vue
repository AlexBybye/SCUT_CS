<script setup lang="ts">
import { computed, ref } from "vue";
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
import { renderAnswerMarkdown } from "../markdown";
import type { WorkflowStreamState } from "../workflowStream";

const props = defineProps<{
  result: WorkflowRunResult | null;
  isRunning: boolean;
  streamState: WorkflowStreamState | null;
  answerMode?: AnswerMode | null;
  tone?: Tone | null;
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

const feedbackOptions = [
  ["helpful", "有帮助"],
  ["not_helpful", "没帮助"],
  ["knowledge_error", "知识错误"],
  ["did_not_answer", "没回答问题"],
] as const;

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
          <div class="markdown-body" v-html="renderedAnswer(block.content)"></div>
          <span v-if="isRunning && !result" class="caret" aria-hidden="true"></span>
        </div>
      </article>
      <p v-if="!answerBlocks.length" class="empty-line">
        {{ isRunning ? "Workflow 已开始，正在等待回答内容。" : "本次没有返回回答内容。" }}
      </p>

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
                  <small>{{ resource.matched_topic }} / 匿名搜索 / 结果未审核</small>
                </span>
                <span aria-hidden="true">查看搜索结果</span>
              </a>
            </div>
            <p v-else class="empty-line">本次没有返回外部资源。</p>
          </div>
        </details>

        <details class="evidence-group">
          <summary>
            <span>Trace</span>
            <span class="chip">{{ trace.length }}</span>
          </summary>
          <p class="evidence-group-note">仅展示后端返回的安全字段。</p>
          <div class="evidence-body">
            <ol v-if="trace.length" class="trace">
              <li v-for="(event, index) in trace" :key="event.event_id">
                <span class="trace-n">{{ String(index + 1).padStart(2, "0") }}</span>
                <div class="trace-main">
                  <strong>{{ event.node }}</strong>
                  <span>
                    {{ event.status }}<template v-if="event.duration_ms !== undefined"> / {{ event.duration_ms }} ms</template>
                  </span>
                  <details v-if="event.result && Object.keys(event.result).length">
                    <summary>查看安全结果</summary>
                    <pre>{{ JSON.stringify(event.result, null, 2) }}</pre>
                  </details>
                </div>
              </li>
            </ol>
            <p v-else class="empty-line">
              {{ isRunning ? "正在等待第一个安全 Trace 事件。" : "本次没有 Trace 事件。" }}
            </p>
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
