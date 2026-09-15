<script setup lang="ts">
import { ref, watch } from "vue";
import type { TemporaryMaterialRecord } from "../contracts";
import { deleteTemporaryMaterial, listTemporaryMaterials, saveTemporaryMaterial } from "../api";
import { useAppStore } from "../composables/useAppStore";

const store = useAppStore();
const emit = defineEmits<{ "open-personal": [value: { tab: "contributions"; materialId: string }] }>();
const materials = ref<TemporaryMaterialRecord[]>([]);
const busy = ref(false);
const loading = ref(false);
const message = ref("");
const error = ref("");
const deletingId = ref("");
let epoch = 0;
async function refresh(): Promise<void> {
  const userId = store.currentUser?.user_id;
  const request = ++epoch;
  if (!userId) { materials.value = []; loading.value = false; return; }
  loading.value = true;
  try {
    const result = await listTemporaryMaterials();
    if (request === epoch && store.currentUser?.user_id === userId) materials.value = result;
  } catch (cause) {
    if (request === epoch) error.value = cause instanceof Error ? cause.message : "材料读取失败，请重试。";
  } finally { if (request === epoch) loading.value = false; }
}
watch(() => store.currentUser?.user_id, () => {
  materials.value = []; message.value = ""; error.value = ""; deletingId.value = "";
  void refresh();
}, { immediate: true });
async function save(): Promise<void> {
  if (busy.value) return;
  error.value = ""; message.value = "";
  if (!store.currentUser) { error.value = "请先登录。"; return; }
  if (!store.conversationId) { error.value = "请先开始一个会话，再保存临时材料。"; return; }
  const content = store.userInput.trim();
  if (!content) { error.value = "请先在输入框粘贴文本或 Markdown。"; return; }
  const userId = store.currentUser.user_id;
  busy.value = true;
  try {
    await saveTemporaryMaterial({ conversation_id: store.conversationId, course_id: store.selectedCourseId, title: store.materialTitle || null, content });
    if (store.currentUser?.user_id !== userId) return;
    message.value = "已保存，7 天后自动删除。可在「个人知识平台」中准备贡献。";
    await refresh();
  } catch (cause) { if (store.currentUser?.user_id === userId) error.value = cause instanceof Error ? cause.message : "保存失败。"; }
  finally { busy.value = false; }
}
async function remove(id: string): Promise<void> {
  if (busy.value) return;
  const userId = store.currentUser?.user_id;
  busy.value = true; error.value = "";
  try {
    await deleteTemporaryMaterial(id);
    if (store.currentUser?.user_id !== userId) return;
    materials.value = materials.value.filter(item => item.material_id !== id);
    deletingId.value = ""; message.value = "临时材料已删除，无法恢复。";
  } catch (cause) { if (store.currentUser?.user_id === userId) error.value = cause instanceof Error ? cause.message : "删除失败。"; }
  finally { busy.value = false; }
}
function openPersonal(event: MouseEvent, materialId: string): void {
  if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  event.preventDefault();
  emit("open-personal", { tab: "contributions", materialId });
}
</script>

<template>
  <section class="material-panel" aria-label="临时材料">
    <p class="material-hint">材料仅对你可见，保存 7 天。贡献审核与公开分享确认统一在「个人知识平台」中完成。</p>
    <div class="material-actions">
      <button type="button" class="btn btn-primary" :disabled="busy || !store.currentUser" @click="save">{{ busy ? "处理中…" : "保存当前输入为临时材料" }}</button>
      <button type="button" class="btn btn-quiet" :disabled="loading || busy" @click="refresh">刷新</button>
    </div>
    <p v-if="message" role="status">{{ message }}</p>
    <p v-if="error" class="note note-bad" role="alert">{{ error }}</p>
    <p v-if="loading" role="status">正在读取临时材料…</p>
    <p v-else-if="!materials.length" class="material-hint">还没有临时材料。保存后可在这里继续使用。</p>
    <ul v-else class="material-list">
      <li v-for="item in materials" :key="item.material_id" class="material-item">
        <div class="material-meta"><strong>{{ item.title || "未命名材料" }}</strong><small>{{ item.char_count }} 字 · {{ new Date(item.expires_at).toLocaleDateString("zh-CN") }} 到期</small></div>
        <div class="material-actions">
          <a class="btn btn-quiet" :href="'/personal?tab=contributions&material=' + encodeURIComponent(item.material_id)" @click="openPersonal($event, item.material_id)">准备贡献</a>
          <button v-if="deletingId !== item.material_id" type="button" class="btn btn-quiet" :disabled="busy" @click="deletingId = item.material_id">删除</button>
          <template v-else><span>删除后无法恢复。</span><button type="button" class="btn btn-danger" :disabled="busy" @click="remove(item.material_id)">确认删除</button><button type="button" class="btn btn-quiet" :disabled="busy" @click="deletingId = ''">取消</button></template>
        </div>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.material-panel { display: grid; gap: 12px; padding: 12px; border: 1px solid var(--line); border-radius: var(--r-md); background: var(--raised); font-size: var(--fs-xs); }
.material-panel p { margin: 0; }
.material-hint, .material-meta small { color: var(--text-muted); line-height: 1.6; }
.material-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
.material-list { display: grid; gap: 8px; padding: 0; margin: 0; list-style: none; }
.material-item { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px; padding: 10px; border-radius: var(--r-sm); background: var(--sunken); }
.material-meta { display: grid; gap: 3px; min-width: 0; overflow-wrap: anywhere; }
</style>
