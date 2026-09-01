<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
  exportMaintainerContribution,
  listMaintainerContributions,
  transitionMaintainerContribution,
} from "../api";
import type { ContributionRecord } from "../contracts";

const items = ref<ContributionRecord[]>([]);
const loading = ref(true);
const error = ref("");
const busyId = ref("");
async function review(id: string, action: "mark_pr_open" | "merge" | "reject"): Promise<void> {
  const prUrl = action === "mark_pr_open" ? window.prompt("请输入 GitHub PR URL")?.trim() : undefined;
  if (action === "mark_pr_open" && !prUrl) return;
  busyId.value = id;
  error.value = "";
  try {
    await transitionMaintainerContribution(id, action, action === "reject" ? "维护者审核拒绝" : undefined, prUrl);
    items.value = await listMaintainerContributions();
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "审核操作失败。";
  } finally {
    busyId.value = "";
  }
}
async function exportItem(id: string): Promise<void> {
  try {
    const payload = await exportMaintainerContribution(id);
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `contribution-${id}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "导出失败。";
  }
}
onMounted(async () => {
  try {
    items.value = await listMaintainerContributions();
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "无法加载维护队列。";
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <main class="maintainer-page">
    <header><h1>维护者中台</h1><p>仅固定 GitHub allowlist 成员可访问。</p></header>
    <p v-if="loading">正在加载贡献队列……</p>
    <p v-else-if="error" role="alert">{{ error }}</p>
    <section v-else aria-label="贡献队列">
      <p v-if="!items.length">当前没有待处理贡献。</p>
      <article v-for="item in items" :key="item.contribution_id" class="maintainer-card">
        <strong>{{ item.title }}</strong>
        <span>{{ item.course_id }} · {{ item.state }} · {{ item.created_at }}</span>
        <small>{{ item.char_count }} 字</small>
        <div class="actions">
          <button type="button" :disabled="busyId === item.contribution_id" @click="exportItem(item.contribution_id)">导出审核包</button>
          <button v-if="item.state === 'submitted'" type="button" :disabled="busyId === item.contribution_id" @click="review(item.contribution_id, 'reject')">拒绝</button>
          <button v-if="item.state === 'submitted'" type="button" :disabled="busyId === item.contribution_id" @click="review(item.contribution_id, 'mark_pr_open')">标记 PR</button>
          <button v-if="item.state === 'pr_open'" type="button" :disabled="busyId === item.contribution_id" @click="review(item.contribution_id, 'merge')">标记采纳</button>
        </div>
      </article>
    </section>
  </main>
</template>

<style scoped>
.maintainer-page { max-width: 920px; margin: 0 auto; padding: 32px; }
.maintainer-page header { margin-bottom: 24px; }
.maintainer-page h1 { margin: 0 0 8px; }
.maintainer-card { display: grid; gap: 6px; padding: 16px; margin: 10px 0; border: 1px solid var(--line, #ddd); border-radius: 10px; }
.maintainer-card span, .maintainer-card small { color: var(--muted, #666); }
</style>
