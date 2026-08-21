<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";
import WorkflowResult from "./WorkflowResult.vue";
import {
  courseAvailabilitySummary,
  courseRuntimeDescription,
} from "../courseAvailability";
import type { AnswerMode, Tone, WorkflowRunResult } from "../contracts";
import { useAppStore } from "../composables/useAppStore";

const store = useAppStore();

type TranscriptTurn = {
  id: string;
  ask: string;
  result: WorkflowRunResult | null;
  answerMode: AnswerMode;
  tone: Tone;
  live: boolean;
};

// 统一回合列表：进行中的回合与已完成回合放进同一个 v-for，用 workflow_run_id 作 key。
// 这样运行完成时，live 回合直接"原地"变成 completed 回合（key 不变），Vue 复用同一个
// <WorkflowResult> 实例，打字机的 typedLength / typeTimer 不丢失，尾巴能继续打完而非整段泄洪。
const turns = computed<TranscriptTurn[]>(() => {
  const completed: TranscriptTurn[] = store.completedTurns.map((turn) => ({
    id: turn.id,
    ask: turn.ask,
    result: turn.result,
    answerMode: turn.answerMode,
    tone: turn.tone,
    live: false,
  }));

  if (!store.isRunning) return completed;

  const liveRunId = store.workflowStreamState?.workflowRunId ?? null;
  const liveIndex = liveRunId ? completed.findIndex((turn) => turn.id === liveRunId) : -1;

  // applyConversationDetail 之后、isRunning=false 之前，run 可能已进入 completedTurns，
  // 复用那份而不是重复追加，避免同一 key 出现两次。
  if (liveIndex >= 0) {
    const existing = completed[liveIndex]!;
    completed[liveIndex] = { ...existing, live: true };
    return completed;
  }

  completed.push({
    id: liveRunId ?? "__live__",
    ask: store.transcriptAsk,
    result: null,
    answerMode: store.answerMode,
    tone: store.tone,
    live: true,
  });

  return completed;
});

// 自动滚动：内容更新后（新回合、流式事件、打字机增长）把记录区滚动到底部，
// 用 nextTick 确保 DOM 更新完成后再执行 scrollTop = scrollHeight。
const transcriptEl = ref<HTMLElement | null>(null);
let transcriptScrollTimer: number | null = null;

function scrollTranscriptToBottom(): void {
  void nextTick(() => {
    const el = transcriptEl.value;
    if (el) el.scrollTop = el.scrollHeight;
  });
}

const transcriptContentSignature = computed(() => ({
  turns: store.completedTurns
    .map((turn) => `${turn.id}:${turn.result?.answer_blocks.length ?? 0}`)
    .join("|"),
  running: store.isRunning,
  events: store.workflowStreamState?.traceEvents.length ?? 0,
  blocks: store.workflowStreamState?.answerBlocks.length ?? 0,
  result: store.result?.workflow_run_id ?? "",
}));

watch(transcriptContentSignature, () => {
  scrollTranscriptToBottom();
});

watch(
  () => store.isRunning,
  (running) => {
    if (transcriptScrollTimer !== null) {
      window.clearInterval(transcriptScrollTimer);
      transcriptScrollTimer = null;
    }
    if (running) {
      // 生成期间持续跟随最新内容（打字机逐字增长时也保持到底）。
      transcriptScrollTimer = window.setInterval(scrollTranscriptToBottom, 1000);
      return;
    }
    // 运行结束后的加速收尾约 18 tick × 70ms ≈ 1.26s，这里再补滚 2 次，
    // 让最后这段揭示也保持在视野底部，而不是在折叠线下悄悄打完。
    let graceTicks = 2;
    transcriptScrollTimer = window.setInterval(() => {
      scrollTranscriptToBottom();
      graceTicks -= 1;
      if (graceTicks <= 0) {
        if (transcriptScrollTimer !== null) {
          window.clearInterval(transcriptScrollTimer);
          transcriptScrollTimer = null;
        }
      }
    }, 650);
  },
  { immediate: true },
);

onBeforeUnmount(() => {
  if (transcriptScrollTimer !== null) {
    window.clearInterval(transcriptScrollTimer);
    transcriptScrollTimer = null;
  }
});
</script>

<template>
  <div id="transcript" ref="transcriptEl" class="transcript">
    <p v-if="store.authMessage" class="note note-bad" role="alert">{{ store.authMessage }}</p>

    <!-- 空态用排版承载，不套卡片：说明运行边界与当前配置。 -->
    <div v-if="!store.completedTurns.length && !store.isRunning" class="transcript-blank">
      <h2>{{ store.activeWorkflow.label }}</h2>
      <p>{{ store.activeWorkflow.description }} {{ courseRuntimeDescription(store.retrievalMode) }}</p>
      <dl>
        <div>
          <dt>课程状态</dt>
          <dd v-if="store.selectedCourse">
            {{ courseAvailabilitySummary(store.selectedCourse) }} · 插件
            {{ store.selectedCourse.plugin_loaded ? "已加载" : "未加载" }}
          </dd>
          <dd v-else>{{ store.isLoadingCourses ? "正在读取课程注册表" : "请先选择课程" }}</dd>
        </div>
        <div>
          <dt>模型</dt>
          <dd>
            {{
              store.selectedModel
                ? `${store.selectedModel.company} · ${store.selectedModel.display_name}`
                : store.isLoadingModels
                  ? "正在读取模型目录"
                  : "模型目录不可用"
            }}
          </dd>
        </div>
        <div>
          <dt>目录版本</dt>
          <dd>{{ store.modelCatalog.catalog_version }}</dd>
        </div>
      </dl>
    </div>

    <div v-else class="transcript-inner">
      <article
        v-for="turn in turns"
        :key="turn.id"
        class="turn"
        :class="{ 'turn-live': turn.live }"
      >
        <div class="turn-ask">
          <div class="turn-ask-head">
            <span>{{ store.activeWorkflow.inputLabel }}</span>
          </div>
          <p>{{ turn.ask }}</p>
        </div>
        <WorkflowResult
          :result="turn.result"
          :is-running="turn.live"
          :stream-state="turn.live ? store.workflowStreamState : null"
          :answer-mode="turn.answerMode"
          :tone="turn.tone"
        />
      </article>
    </div>
  </div>
</template>

<style>
.transcript {
  min-height: 0;
  overflow-y: auto;
  padding: 16px;
  scroll-behavior: smooth;
}

.transcript-inner {
  display: grid;
  gap: 14px;
  width: 100%;
  margin: 0 auto;
}

/* 空态：没有卡片框，只有排版。 */
.transcript-blank {
  display: grid;
  align-content: center;
  gap: 10px;
  min-height: 100%;
  width: min(560px, 100%);
  margin: 0 auto;
  padding: 32px 0;
}

.transcript-blank h2 {
  font-size: var(--fs-xl);
  font-weight: 650;
  letter-spacing: -0.02em;
}

.transcript-blank p {
  max-width: 52ch;
  color: var(--text-muted);
  font-size: var(--fs-sm);
  line-height: 1.7;
}

.transcript-blank dl {
  display: grid;
  gap: 7px;
  margin-top: 6px;
  padding-top: 14px;
  border-top: 1px solid var(--line);
}

.transcript-blank dl > div {
  display: grid;
  grid-template-columns: 92px minmax(0, 1fr);
  gap: 10px;
  align-items: baseline;
}

.transcript-blank dt {
  color: var(--text);
  font-size: var(--fs-xs);
  font-weight: 650;
}

.transcript-blank dd {
  color: var(--text-muted);
  font-size: var(--fs-xs);
}

/* 连续对话：每一轮（提问 + 回答）作为一个区块。 */
.turn {
  display: grid;
  gap: 10px;
  min-width: 0;
}

/* 用户提问：右侧收缩气泡，与回答形成对话节奏。 */
.turn-ask {
  justify-self: end;
  max-width: 80%;
  padding: 8px 11px;
  border: 1px solid var(--line);
  border-radius: var(--r-md);
  background: var(--raised);
}

.turn-ask-head {
  display: flex;
  align-items: baseline;
  gap: 7px;
  margin-bottom: 3px;
  color: var(--text-muted);
  font-size: var(--fs-2xs);
}

.turn-ask p {
  white-space: pre-wrap;
  font-size: var(--fs-sm);
  line-height: 1.65;
  overflow-wrap: anywhere;
}

@media (max-width: 719px) {
  .transcript {
    padding-inline: 11px;
  }

  .turn-ask {
    max-width: 92%;
  }
}

/* 低矮窗口：保证记录区可滚动。 */
@media (max-height: 640px) {
  .transcript {
    padding-block: 10px;
  }
}
</style>
