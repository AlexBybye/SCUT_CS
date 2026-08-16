<script setup lang="ts">
import { computed } from "vue";
import type { Citation, WorkflowRunResult } from "../contracts";

const props = defineProps<{
  result: WorkflowRunResult | null;
  isRunning: boolean;
}>();

const citations = computed(() => props.result?.citations ?? []);
const externalResources = computed(() => props.result?.external_resources ?? []);
const trace = computed(() => props.result?.trace ?? []);

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
        <p class="section-kicker">契约返回</p>
        <h2 id="result-heading">回答、来源与 Trace</h2>
      </div>
      <div v-if="result" class="status-pair" aria-label="运行状态">
        <span>{{ result.run_status }}</span>
        <span>{{ result.answer_status }}</span>
      </div>
    </header>

    <div v-if="isRunning" class="result-loading" role="status">
      <span class="skeleton-line skeleton-line-long"></span>
      <span class="skeleton-line"></span>
      <span class="skeleton-line skeleton-line-short"></span>
      <p>正在执行确定性 Mock 链路并保存结果。</p>
    </div>

    <div v-else-if="!result" class="result-empty">
      <p>尚未运行 Workflow。</p>
      <span>提交左侧表单后，这里会分别呈现回答、仓库引用、外部资源和真实 Mock Trace。</span>
    </div>

    <template v-else>
      <article class="answer-block">
        <div class="answer-meta">
          <span>课程资料回答</span>
          <span v-if="result.evidence_status">证据状态：{{ result.evidence_status }}</span>
        </div>
        <p class="answer-copy">{{ result.repository_answer || "本次没有仓库资料回答。" }}</p>
      </article>

      <article v-if="result.general_supplement" class="supplement-block">
        <h3>通用补充</h3>
        <p>{{ result.general_supplement }}</p>
      </article>

      <section class="result-section" aria-labelledby="citations-heading">
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
        <p v-else class="section-empty">本次 Mock 没有仓库引用。</p>
      </section>

      <section class="result-section external-section" aria-labelledby="resources-heading">
        <div class="result-section-heading">
          <div>
            <h3 id="resources-heading">B站延伸学习</h3>
            <p>外部资源不属于仓库引用，也不改变证据状态。</p>
          </div>
          <span>{{ externalResources.length }} 条</span>
        </div>
        <div v-if="externalResources.length" class="resource-list">
          <a
            v-for="resource in externalResources"
            :key="resource.resource_id || resource.url"
            :href="resource.url"
            target="_blank"
            rel="noreferrer"
            class="resource-item"
          >
            <span>
              <strong>{{ resource.title }}</strong>
              <small>{{ resource.matched_topic }} / {{ resource.review_status }}</small>
            </span>
            <span aria-hidden="true">打开</span>
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
          <li v-for="(event, index) in trace" :key="`${event.node}-${index}`">
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
        <p v-else class="section-empty">本次没有 Trace 事件。</p>
      </section>
    </template>
  </section>
</template>
