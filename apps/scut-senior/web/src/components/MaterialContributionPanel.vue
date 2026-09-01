<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import type {
  ContributionPreview,
  ContributionRecord,
  ContributionState,
  TemporaryMaterialRecord,
} from "../contracts";
import {
  deleteTemporaryMaterial,
  getTemporaryMaterial,
  listContributions,
  listTemporaryMaterials,
  previewContribution,
  saveTemporaryMaterial,
  submitContribution,
} from "../api";
import { useAppStore } from "../composables/useAppStore";

const store = useAppStore();

// 贡献提交通道暂时对 UI 封闭（后端契约、队列与 TTL 保持原样）：
// 上线时把 CONTRIBUTION_SUBMIT_CLOSED 改回 false 即可整体恢复。
const CONTRIBUTION_SUBMIT_CLOSED = false;
const SUBMIT_CLOSED_TIP = "提交前请完成全部确认。";

// 封闭入口的点击反馈：toast 比原生 title 即时且在触屏上也可用。
const toastMessage = ref("");
let toastTimer: ReturnType<typeof setTimeout> | undefined;
function showToast(message: string): void {
  toastMessage.value = message;
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (toastMessage.value = ""), 2200);
}

// 临时材料与贡献面板：只在临时材料精读 Workflow 下展示。
// 材料正文取当前输入框内容；保存后 7 天自动过期（服务端物理删除）。
const materials = ref<TemporaryMaterialRecord[]>([]);
const contributions = ref<ContributionRecord[]>([]);
const busy = ref(false);
const panelMessage = ref("");

const preview = ref<ContributionPreview | null>(null);
const previewMaterialId = ref<string | null>(null);

const confirmations = ref({
  course_confirmed: false,
  source_confirmed: false,
  public_share_rights_confirmed: false,
  no_sensitive_info_confirmed: false,
  public_pr_visibility_acknowledged: false,
});

const allConfirmed = computed(() =>
  Object.values(confirmations.value).every((value) => value),
);

const stateLabels: Record<ContributionState, string> = {
  draft: "草稿",
  submitted: "待审核（维护者队列）",
  pr_open: "PR 已创建",
  merged: "已合并",
  rejected: "已拒绝",
  expired: "已过期",
};

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString("zh-CN", { hour12: false });
}

async function refresh(): Promise<void> {
  if (!store.currentUser) return;
  try {
    materials.value = await listTemporaryMaterials();
    contributions.value = await listContributions();
  } catch {
    // 列表刷新失败不打断输入；下次操作会再次尝试。
  }
}

onMounted(() => void refresh());

async function onSaveMaterial(): Promise<void> {
  panelMessage.value = "";
  if (!store.conversationId) {
    panelMessage.value = "请先开始一个会话，再保存临时材料。";
    return;
  }
  const content = store.userInput.trim();
  if (!content) {
    panelMessage.value = "请先在输入框粘贴要精读的文本或 Markdown。";
    return;
  }
  busy.value = true;
  try {
    await saveTemporaryMaterial({
      conversation_id: store.conversationId,
      course_id: store.selectedCourseId,
      title: store.materialTitle || null,
      content,
    });
    panelMessage.value = "已保存为临时材料，7 天后自动删除。";
    await refresh();
  } catch (error) {
    panelMessage.value = error instanceof Error ? error.message : "保存失败。";
  } finally {
    busy.value = false;
  }
}

async function onDeleteMaterial(materialId: string): Promise<void> {
  busy.value = true;
  try {
    await deleteTemporaryMaterial(materialId);
    if (previewMaterialId.value === materialId) {
      preview.value = null;
      previewMaterialId.value = null;
    }
    await refresh();
  } catch (error) {
    panelMessage.value = error instanceof Error ? error.message : "删除失败。";
  } finally {
    busy.value = false;
  }
}

async function onPreview(materialId: string): Promise<void> {
  panelMessage.value = "";
  busy.value = true;
  try {
    // 预览需要原文；列表记录不含全文，先从详情端点取。
    const detail = await getTemporaryMaterial(materialId);
    preview.value = await previewContribution({
      course_id: store.selectedCourseId,
      title: detail.title,
      content: detail.content,
    });
    previewMaterialId.value = materialId;
  } catch (error) {
    preview.value = null;
    previewMaterialId.value = null;
    panelMessage.value = error instanceof Error ? error.message : "预览失败。";
  } finally {
    busy.value = false;
  }
}

async function onSubmit(materialId: string, asDraft: boolean): Promise<void> {
  panelMessage.value = "";
  if (!allConfirmed.value && !asDraft) {
    panelMessage.value = "提交前请逐项勾选确认。";
    return;
  }
  busy.value = true;
  try {
    await submitContribution({
      material_id: materialId,
      course_id: store.selectedCourseId,
      title: store.materialTitle || null,
      as_draft: asDraft,
      confirmations: confirmations.value,
    });
    panelMessage.value = asDraft
      ? "草稿已保存。提交进入待审队列仍需完整确认。"
      : "已提交到维护者待处理队列；合并前还会经过人工审核与语料验证。";
    confirmations.value = {
      course_confirmed: false,
      source_confirmed: false,
      public_share_rights_confirmed: false,
      no_sensitive_info_confirmed: false,
      public_pr_visibility_acknowledged: false,
    };
    await refresh();
  } catch (error) {
    panelMessage.value = error instanceof Error ? error.message : "提交失败。";
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <div class="material-panel" aria-label="临时材料保存与贡献">
    <div v-if="toastMessage" class="panel-toast" role="status">{{ toastMessage }}</div>
    <p class="drawer-hint drawer-span">
      粘贴的材料只属于你，默认不进入公共索引或课程包；普通材料 7
      天后由服务端实际删除。贡献需人工审核通过后才会进入公共知识库。
    </p>
    <div class="drawer-span material-actions">
      <button
        type="button"
        class="btn"
        :disabled="busy"
        @click="onSaveMaterial"
      >
        把当前输入保存为临时材料
      </button>
    </div>

    <p v-if="panelMessage" class="drawer-span field-hint">{{ panelMessage }}</p>

    <ul v-if="materials.length" class="drawer-span material-list">
      <li v-for="item in materials" :key="item.material_id" class="material-item">
        <div class="material-meta">
          <strong>{{ item.title || "未命名材料" }}</strong>
          <small>{{ item.char_count }} 字 · 过期于 {{ formatDate(item.expires_at) }}</small>
        </div>
        <div class="material-buttons">
          <button type="button" class="btn btn-quiet" :disabled="busy" @click="onPreview(item.material_id)">
            预览转换结果
          </button>
          <span
            class="hover-tip"
            :class="{ closed: CONTRIBUTION_SUBMIT_CLOSED }"
            @click="CONTRIBUTION_SUBMIT_CLOSED && showToast(SUBMIT_CLOSED_TIP)"
          >
            <button
              type="button"
              class="btn btn-quiet"
              :disabled="CONTRIBUTION_SUBMIT_CLOSED || busy"
              @click="onSubmit(item.material_id, true)"
            >
              存为贡献草稿
            </button>
            <span v-if="CONTRIBUTION_SUBMIT_CLOSED" class="hover-bubble" aria-hidden="true">
              {{ SUBMIT_CLOSED_TIP }}
            </span>
          </span>
          <button type="button" class="btn btn-danger" :disabled="busy" @click="onDeleteMaterial(item.material_id)">
            删除
          </button>
        </div>
      </li>
    </ul>

    <section
      v-if="preview"
      class="drawer-span material-preview"
      aria-label="贡献预览"
    >
      <h4>转换结果预览（确定性规范化，不改写语义）</h4>
      <p class="field-hint">
        提交落点：<code>{{ preview.proposed_repo_path || "（由维护者导出时确定）" }}</code>
        · 提议来源编号：<code>{{ preview.proposed_source_id }}</code>
        （最终编号以人工审核为准）
        · 题目标记 {{ preview.question_marker_count }} 处
      </p>
      <ul v-if="preview.warnings.length" class="material-warnings">
        <li v-for="warning in preview.warnings" :key="warning">{{ warning }}</li>
      </ul>
      <pre>{{ preview.normalized_content.slice(0, 2000) }}{{ preview.normalized_content.length > 2000 ? "\n…（预览截断）" : "" }}</pre>

      <fieldset class="material-confirm">
        <legend>提交前确认（公开 PR 可能长期公开）</legend>
        <label><input v-model="confirmations.course_confirmed" type="checkbox" /> 我确认归属课程正确。</label>
        <label><input v-model="confirmations.source_confirmed" type="checkbox" /> 我确认材料来源真实、未篡改。</label>
        <label><input v-model="confirmations.public_share_rights_confirmed" type="checkbox" /> 我拥有公开分享该材料的权利。</label>
        <label><input v-model="confirmations.no_sensitive_info_confirmed" type="checkbox" /> 材料不含个人隐私或敏感信息。</label>
        <label><input v-model="confirmations.public_pr_visibility_acknowledged" type="checkbox" /> 我了解公开仓库中的 PR 可能长期可见。</label>
      </fieldset>

      <div class="material-buttons">
        <span
          class="hover-tip"
          :class="{ closed: CONTRIBUTION_SUBMIT_CLOSED }"
          @click="CONTRIBUTION_SUBMIT_CLOSED && showToast(SUBMIT_CLOSED_TIP)"
        >
          <button
            type="button"
            class="btn"
            :disabled="
              CONTRIBUTION_SUBMIT_CLOSED || busy || !allConfirmed || !previewMaterialId
            "
            @click="previewMaterialId && onSubmit(previewMaterialId, false)"
          >
            提交到待审队列
          </button>
          <span v-if="CONTRIBUTION_SUBMIT_CLOSED" class="hover-bubble" aria-hidden="true">
            {{ SUBMIT_CLOSED_TIP }}
          </span>
        </span>
      </div>
    </section>

    <section v-if="contributions.length" class="drawer-span" aria-label="我的贡献">
      <h4>我的贡献</h4>
      <ul class="material-list">
        <li v-for="item in contributions" :key="item.contribution_id" class="material-item">
          <div class="material-meta">
            <strong>{{ item.title }}</strong>
            <small>
              {{ stateLabels[item.state] }}
              <template v-if="item.proposed_repo_path"> · 目标 <code>{{ item.proposed_repo_path }}</code></template>
              <template v-if="item.pr_url"> ·
                <a :href="item.pr_url" target="_blank" rel="noreferrer">查看 PR</a>
              </template>
              <template v-if="item.maintainer_note"> · 备注：{{ item.maintainer_note }}</template>
            </small>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>

<style>
.material-panel {
  display: grid;
  gap: 8px;
}

.material-actions {
  display: flex;
  gap: 8px;
}

.material-list {
  display: grid;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.material-item {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 6px;
  padding: 7px 9px;
  border: 1px solid var(--line);
  border-radius: var(--r-sm);
  background: var(--raised);
}

.material-meta {
  display: grid;
  gap: 1px;
  min-width: 0;
}

.material-meta small {
  color: var(--text-muted);
  font-size: var(--fs-2xs);
}

.material-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* 封闭中的入口：悬停立即显示气泡，点击弹 toast。
   禁用按钮会吞掉指针事件，这里显式放行给外层 wrapper。 */
.hover-tip {
  position: relative;
  display: inline-flex;
}

.hover-tip.closed {
  cursor: help;
}

.hover-tip.closed .btn:disabled {
  pointer-events: none;
  opacity: 0.6;
}

.hover-bubble {
  position: absolute;
  bottom: calc(100% + 6px);
  left: 0;
  z-index: 60;
  padding: 5px 9px;
  border-radius: 6px;
  background: rgba(24, 24, 30, 0.94);
  color: #fff;
  font-size: var(--fs-2xs);
  white-space: nowrap;
  opacity: 0;
  transform: translateY(2px);
  transition:
    opacity 0.12s ease,
    transform 0.12s ease;
  pointer-events: none;
}

.hover-tip.closed:hover .hover-bubble,
.hover-tip.closed:focus-within .hover-bubble {
  opacity: 1;
  transform: translateY(0);
}

.panel-toast {
  position: fixed;
  bottom: 22px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 200;
  padding: 9px 16px;
  border-radius: 8px;
  background: rgba(24, 24, 30, 0.94);
  color: #fff;
  font-size: var(--fs-xs);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25);
}

.material-preview {
  display: grid;
  gap: 7px;
  padding: 9px;
  border: 1px dashed var(--line);
  border-radius: var(--r-sm);
}

.material-preview h4 {
  margin: 0;
  font-size: var(--fs-xs);
}

.material-preview pre {
  max-height: 220px;
  overflow: auto;
  padding: 8px;
  border-radius: var(--r-sm);
  background: var(--sunken);
  font-size: var(--fs-2xs);
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.material-warnings {
  margin: 0;
  padding-left: 18px;
  color: var(--warn-text);
  font-size: var(--fs-2xs);
}

.material-confirm {
  display: grid;
  gap: 4px;
  border: none;
  padding: 0;
  margin: 0;
}

.material-confirm legend {
  font-size: var(--fs-2xs);
  font-weight: 650;
  color: var(--text-muted);
}

.material-confirm label {
  display: flex;
  gap: 6px;
  align-items: baseline;
  font-size: var(--fs-xs);
}
</style>
