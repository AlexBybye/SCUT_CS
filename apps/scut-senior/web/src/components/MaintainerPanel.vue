<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  exportMaintainerContribution,
  getMaintainerContribution,
  getCourses,
  listMaintainerContributions,
  listMaintainerFeedback,
  transitionMaintainerContribution,
} from "../api";
import type { ContributionRecord, FeedbackRecord } from "../contracts";

const items = ref<ContributionRecord[]>([]);
const feedback = ref<FeedbackRecord[]>([]);
const courseNames = ref<Record<string, string>>({});
const activeQueue = ref<"contributions" | "feedback">("contributions");
const selectedFeedbackType = ref<string | null>(null);
const selectedContribution = ref<ContributionRecord | null>(null);
const detail = ref<ContributionRecord | null>(null);
const loading = ref(true);
const detailLoading = ref(false);
const error = ref("");
const busyId = ref("");
const feedbackLabels: Record<string, string> = {
  helpful: "有帮助",
  not_helpful: "没帮助",
  knowledge_error: "知识错误",
  did_not_answer: "没有回答",
};
const feedbackColors = ["#d9573f", "#d39a3d", "#557a95", "#7f8c69"];

const feedbackStats = computed(() => {
  const counts = new Map<string, number>();
  for (const item of feedback.value) counts.set(item.feedback_type, (counts.get(item.feedback_type) || 0) + 1);
  return [...counts.entries()].map(([type, count], index) => ({ type, count, color: feedbackColors[index % feedbackColors.length] }));
});
const totalFeedback = computed(() => feedback.value.length);
const filteredFeedback = computed(() => selectedFeedbackType.value ? feedback.value.filter((item) => item.feedback_type === selectedFeedbackType.value) : feedback.value);
const courseName = (id: string) => courseNames.value[id] || id;
function polar(angle: number): [number, number] {
  const radians = (angle - 90) * Math.PI / 180;
  return [50 + 39 * Math.cos(radians), 50 + 39 * Math.sin(radians)];
}
function sectorPath(start: number, end: number): string {
  if (end - start >= 359.9) return "M 50 11 A 39 39 0 1 1 49.99 11 Z";
  const [sx, sy] = polar(start); const [ex, ey] = polar(end);
  return `M 50 50 L ${sx} ${sy} A 39 39 0 ${end - start > 180 ? 1 : 0} 1 ${ex} ${ey} Z`;
}
const sectors = computed(() => {
  let cursor = 0;
  return feedbackStats.value.map((item) => {
    const start = cursor;
    cursor += totalFeedback.value ? item.count / totalFeedback.value * 360 : 0;
    return { ...item, path: sectorPath(start, cursor) };
  });
});
async function selectContribution(item: ContributionRecord): Promise<void> {
  selectedContribution.value = item; detail.value = null; detailLoading.value = true;
  try { detail.value = await getMaintainerContribution(item.contribution_id); }
  catch { detail.value = item; }
  finally { detailLoading.value = false; }
}
async function review(id: string, action: "mark_pr_open" | "merge" | "reject"): Promise<void> {
  const prUrl = action === "mark_pr_open" ? window.prompt("请输入 GitHub PR URL")?.trim() : undefined;
  if (action === "mark_pr_open" && !prUrl) return;
  busyId.value = id; error.value = "";
  try {
    const updated = await transitionMaintainerContribution(id, action, action === "reject" ? "维护者审核拒绝" : undefined, prUrl);
    items.value = items.value.map((item) => item.contribution_id === id ? updated : item);
    if (selectedContribution.value?.contribution_id === id) await selectContribution(updated);
  } catch (cause) { error.value = cause instanceof Error ? cause.message : "审核操作失败。"; }
  finally { busyId.value = ""; }
}
async function exportItem(id: string): Promise<void> {
  busyId.value = id;
  try {
    const payload = await exportMaintainerContribution(id);
    const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }));
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = `contribution-${id}.json`; anchor.click(); URL.revokeObjectURL(url);
  } catch (cause) { error.value = cause instanceof Error ? cause.message : "导出失败。"; }
  finally { busyId.value = ""; }
}
onMounted(async () => {
  try {
    const [contributions, reports, courses] = await Promise.all([listMaintainerContributions(), listMaintainerFeedback(), getCourses()]);
    items.value = contributions; feedback.value = reports;
    courseNames.value = Object.fromEntries(courses.courses.map((course) => [course.course_id, course.display_name]));
  } catch (cause) { error.value = cause instanceof Error ? cause.message : "无法加载维护队列。"; }
  finally { loading.value = false; }
});
</script>

<template>
  <main class="maintainer-page">
    <header class="maintainer-hero">
      <div><p class="eyebrow">SCUT 老学长</p><h1>把每一条反馈，变成下一次更好的回答</h1><p>这里集中处理课程资料贡献和题目反馈。内容会经过人工审核，不会自动写入公共资料库。</p></div>
      <div class="hero-note"><strong>{{ items.length + feedback.length }}</strong><span>待查看记录</span></div>
    </header>
    <nav class="queue-tabs" aria-label="维护队列">
      <button type="button" :class="{ active: activeQueue === 'contributions' }" @click="activeQueue = 'contributions'">资料贡献 <span>{{ items.length }}</span></button>
      <button type="button" :class="{ active: activeQueue === 'feedback' }" @click="activeQueue = 'feedback'">题目反馈 <span>{{ feedback.length }}</span></button>
    </nav>
    <p v-if="loading" class="state">正在整理记录...</p>
    <p v-else-if="error" class="state error" role="alert">{{ error }}</p>
    <template v-else-if="activeQueue === 'feedback'">
      <section class="feedback-overview" aria-label="反馈类型统计">
        <div class="chart-wrap">
          <svg class="feedback-chart" viewBox="0 0 100 100" role="img" aria-label="反馈类型饼状图">
            <path v-for="sector in sectors" :key="sector.type" :d="sector.path" :fill="sector.color" :class="{ selected: selectedFeedbackType === sector.type }" @click="selectedFeedbackType = selectedFeedbackType === sector.type ? null : sector.type" />
            <circle cx="50" cy="50" r="22" /><text x="50" y="48" text-anchor="middle" class="chart-total">{{ totalFeedback }}</text><text x="50" y="59" text-anchor="middle" class="chart-caption">条反馈</text>
          </svg>
        </div>
        <div class="legend"><h2>反馈概览</h2><p>点击图例或饼图颜色，可以只查看一种反馈。</p><button v-for="item in feedbackStats" :key="item.type" type="button" class="legend-item" :class="{ selected: selectedFeedbackType === item.type }" @click="selectedFeedbackType = selectedFeedbackType === item.type ? null : item.type"><i :style="{ background: item.color }"></i><span>{{ feedbackLabels[item.type] || item.type }}</span><strong>{{ item.count }}</strong></button><button v-if="selectedFeedbackType" type="button" class="clear-filter" @click="selectedFeedbackType = null">显示全部反馈</button></div>
      </section>
      <section class="report-list" aria-label="题目反馈报告"><div class="section-heading"><h2>{{ selectedFeedbackType ? feedbackLabels[selectedFeedbackType] : '全部反馈' }}</h2><span>{{ filteredFeedback.length }} 条</span></div><p v-if="!filteredFeedback.length" class="empty">当前筛选下没有反馈。</p><article v-for="item in filteredFeedback" :key="item.feedback_id" class="report-card"><div class="report-card-head"><strong>{{ feedbackLabels[item.feedback_type] || item.feedback_type }}</strong><span>{{ courseName(item.course_id) }}</span></div><p>{{ item.note || "用户没有补充文字，但这条反馈仍值得结合原回答复核。" }}</p><dl><div><dt>回答类型</dt><dd>{{ item.workflow_type }}</dd></div><div><dt>回答状态</dt><dd>{{ item.answer_status }}</dd></div><div><dt>提交时间</dt><dd>{{ new Date(item.created_at).toLocaleString('zh-CN') }}</dd></div></dl></article></section>
    </template>
    <template v-else>
      <section class="content-grid"><div class="contribution-list"><div class="section-heading"><h2>资料贡献</h2><span>{{ items.length }} 条记录</span></div><p v-if="!items.length" class="empty">还没有待处理的资料贡献。</p><button v-for="item in items" :key="item.contribution_id" type="button" class="contribution-row" :class="{ selected: selectedContribution?.contribution_id === item.contribution_id }" @click="selectContribution(item)"><span><strong>{{ item.title }}</strong><small>{{ courseName(item.course_id) }} · {{ item.state }}</small></span><small>{{ new Date(item.created_at).toLocaleDateString('zh-CN') }}</small></button></div><aside class="detail-panel" aria-label="贡献详情"><p v-if="!detail && !selectedContribution" class="empty">选择左侧一条贡献，查看正文和审核信息。</p><template v-else><div class="detail-head"><div><p class="eyebrow">贡献详情</p><h2>{{ (detail || selectedContribution)?.title }}</h2></div><span class="status">{{ (detail || selectedContribution)?.state }}</span></div><dl class="detail-facts"><div><dt>课程</dt><dd>{{ courseName((detail || selectedContribution)!.course_id) }}</dd></div><div><dt>字数</dt><dd>{{ (detail || selectedContribution)?.char_count }}</dd></div><div><dt>创建时间</dt><dd>{{ new Date((detail || selectedContribution)!.created_at).toLocaleString('zh-CN') }}</dd></div></dl><p v-if="detailLoading" class="state">正在读取详情...</p><p class="detail-copy">当前列表只返回审核所需的基本信息。正文请通过“导出审核包”下载后核对，避免在队列页面误展示未审核内容。</p><div class="actions"><button type="button" :disabled="busyId === selectedContribution?.contribution_id" @click="exportItem(selectedContribution!.contribution_id)">导出审核包</button><button v-if="selectedContribution?.state === 'submitted'" type="button" :disabled="busyId === selectedContribution?.contribution_id" @click="review(selectedContribution!.contribution_id, 'reject')">拒绝</button><button v-if="selectedContribution?.state === 'submitted'" type="button" :disabled="busyId === selectedContribution?.contribution_id" @click="review(selectedContribution!.contribution_id, 'mark_pr_open')">标记 PR</button><button v-if="selectedContribution?.state === 'pr_open'" type="button" :disabled="busyId === selectedContribution?.contribution_id" @click="review(selectedContribution!.contribution_id, 'merge')">标记采纳</button></div></template></aside></section>
    </template>
  </main>
</template>

<style scoped>
.maintainer-page {
  min-height: 100vh;
  padding: 44px clamp(20px, 5vw, 72px);
  color: var(--text);
  background: var(--page);
  font-family: var(--font-ui);
}

.maintainer-hero {
  display: flex;
  justify-content: space-between;
  gap: 32px;
  max-width: 1180px;
  margin: 0 auto 34px;
  padding-bottom: 28px;
  border-bottom: 1px solid var(--line);
}

.maintainer-hero h1 {
  max-width: 690px;
  margin: 5px 0 12px;
  font-size: clamp(30px, 4vw, 52px);
  line-height: 1.06;
  letter-spacing: -0.04em;
  font-weight: 760;
}

.maintainer-hero p:not(.eyebrow) {
  max-width: 620px;
  margin: 0;
  color: var(--text-muted);
  line-height: 1.7;
}

.eyebrow {
  margin: 0;
  color: var(--accent);
  font-size: 11px;
  font-weight: 750;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.hero-note {
  display: grid;
  align-content: end;
  min-width: 130px;
  color: var(--text-muted);
}

.hero-note strong {
  color: var(--accent);
  font-size: 42px;
  line-height: 1;
}

.hero-note span {
  margin-top: 8px;
}

.queue-tabs {
  display: flex;
  gap: 8px;
  max-width: 1180px;
  margin: 0 auto 26px;
}

.queue-tabs button {
  padding: 10px 16px;
  border: 1px solid var(--line);
  border-radius: var(--r-sm);
  color: var(--text-muted);
  background: var(--raised);
  cursor: pointer;
}

.queue-tabs button.active {
  border-color: var(--accent);
  color: var(--accent-on);
  background: var(--accent);
}

.queue-tabs span {
  margin-left: 6px;
  font-weight: 700;
}

.feedback-overview,
.content-grid {
  display: grid;
  grid-template-columns: minmax(260px, 0.8fr) minmax(0, 1.5fr);
  gap: 28px;
  max-width: 1180px;
  margin: 0 auto 34px;
}

.feedback-overview {
  align-items: center;
  padding: 24px;
  border: 1px solid var(--line);
  border-radius: var(--r-md);
  background: var(--panel);
}

.chart-wrap {
  display: grid;
  place-items: center;
}

.feedback-chart {
  width: min(260px, 80vw);
  overflow: visible;
}

.feedback-chart path {
  cursor: pointer;
  stroke: var(--panel);
  stroke-width: 1.3;
  transition: opacity 0.2s, transform 0.2s;
  transform-origin: 50% 50%;
}

.feedback-chart path:hover,
.feedback-chart path.selected {
  opacity: 0.72;
  transform: scale(1.04);
}

.feedback-chart circle {
  fill: var(--panel);
}

.chart-total {
  fill: var(--text);
  font-size: 15px;
  font-weight: 750;
}

.chart-caption {
  fill: var(--text-muted);
  font-size: 5px;
}

.legend {
  display: grid;
  gap: 8px;
}

.legend h2,
.section-heading h2,
.detail-head h2 {
  margin: 0;
  font-size: 22px;
  letter-spacing: -0.025em;
}

.legend p {
  margin: 0 0 8px;
  color: var(--text-muted);
}

.legend-item {
  display: grid;
  grid-template-columns: 12px 1fr auto;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border: 0;
  border-radius: var(--r-sm);
  text-align: left;
  color: var(--text);
  background: transparent;
  cursor: pointer;
}

.legend-item:hover,
.legend-item.selected {
  background: var(--sunken);
}

.legend-item i {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.clear-filter {
  justify-self: start;
  border: 0;
  color: var(--accent);
  background: none;
  cursor: pointer;
}

.report-list,
.contribution-list,
.detail-panel {
  max-width: 1180px;
  margin: 0 auto;
}

.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 12px;
}

.section-heading span,
.report-card-head span,
.contribution-row small,
.detail-facts dt {
  color: var(--text-soft);
  font-size: 13px;
}

.report-card {
  padding: 18px 0;
  border-top: 1px solid var(--line);
}

.report-card-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.report-card p {
  margin: 10px 0;
  line-height: 1.6;
}

.report-card dl,
.detail-facts {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin: 0;
}

.report-card dl div,
.detail-facts div {
  display: grid;
  gap: 3px;
}

.report-card dt,
.report-card dd,
.detail-facts dt,
.detail-facts dd {
  margin: 0;
}

.report-card dd,
.detail-facts dd {
  font-size: 13px;
}

.content-grid {
  grid-template-columns: minmax(280px, 0.9fr) minmax(0, 1.1fr);
  align-items: start;
}

.contribution-row {
  display: flex;
  justify-content: space-between;
  width: 100%;
  padding: 15px 0;
  border: 0;
  border-top: 1px solid var(--line);
  text-align: left;
  color: var(--text);
  background: transparent;
  cursor: pointer;
}

.contribution-row span {
  display: grid;
  gap: 5px;
}

.contribution-row.selected strong {
  color: var(--accent);
}

.detail-panel {
  min-height: 290px;
  padding: 24px;
  border: 1px solid var(--line);
  border-radius: var(--r-md);
  background: var(--panel);
}

.detail-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.detail-head h2 {
  margin-top: 6px;
}

.status {
  padding: 5px 9px;
  border-radius: var(--r-sm);
  color: var(--accent);
  background: var(--accent-wash);
  font-size: 12px;
}

.detail-facts {
  margin: 22px 0;
}

.detail-copy {
  color: var(--text-muted);
  line-height: 1.7;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 20px;
}

.actions button {
  padding: 9px 12px;
  border: 1px solid var(--line-strong);
  border-radius: var(--r-sm);
  color: var(--text);
  background: var(--raised);
  cursor: pointer;
}

.actions button:first-child {
  border-color: var(--accent);
  color: var(--accent);
}

.state,
.empty {
  color: var(--text-soft);
}

.error {
  color: var(--bad-text);
}

.state,
.empty,
.report-list,
.content-grid {
  max-width: 1180px;
  margin-left: auto;
  margin-right: auto;
}

@media (max-width: 720px) {
  .maintainer-page {
    padding: 28px 16px;
  }

  .maintainer-hero {
    display: grid;
  }

  .feedback-overview,
  .content-grid {
    grid-template-columns: 1fr;
    padding: 16px;
  }

  .hero-note {
    align-content: start;
  }

  .detail-panel {
    padding: 18px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .feedback-chart path {
    transition: none;
  }
}
</style>
