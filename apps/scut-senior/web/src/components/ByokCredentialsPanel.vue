<script setup lang="ts">
import { reactive, ref, watch } from "vue";
import { canManageByokCredentials } from "../byokSession";
import { formatCredentialExpiry } from "../appConfig";
import type { ByokCredentialStatus, ByokModel } from "../contracts";
import { useAppStore } from "../composables/useAppStore";

const store = useAppStore();
const connectionId = ref("");
const newDraft = reactive({
  display_name: "", base_url: "", model_id: "", api_key: "",
  models: [{ model_id: "", display_name: "", context_length: 0, max_tokens: null }] as ByokModel[],
});
type ConnectionDraft = { display_name: string; base_url: string; model_id: string; api_key: string; models: ByokModel[] };
const drafts = reactive<Record<string, ConnectionDraft>>({});
const discovered = ref<ByokModel[]>([]);
const discoveredFor = ref("");
const isDiscovering = ref(false);
const selectedDiscovered = ref<Set<string>>(new Set());
const idPattern = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
function draftFor(providerId: string): ConnectionDraft { return drafts[providerId]!; }

function cloneModels(models: ByokModel[]): ByokModel[] { return models.map((model) => ({ ...model, model_id: model.model_id.trim(), display_name: model.display_name.trim() || model.model_id.trim() })); }
function ensureDraft(status: ByokCredentialStatus): void {
  if (drafts[status.provider_id]) return;
  drafts[status.provider_id] = { display_name: status.display_name, base_url: status.base_url, model_id: status.model_id, api_key: "", models: cloneModels(status.models ?? [{ model_id: status.model_id, display_name: status.model_id, context_length: 0, max_tokens: null }]) };
}
watch(() => store.byokCredentialStatuses, (statuses) => statuses.forEach(ensureDraft), { immediate: true });
function validModels(models: ByokModel[]): boolean {
  const ids = models.map((model) => model.model_id.trim()).filter(Boolean);
  return ids.length > 0 && ids.length === new Set(ids).size && models.every((model) => Boolean(model.model_id.trim()));
}
function addModel(models: ByokModel[]): void { models.push({ model_id: "", display_name: "", context_length: 0, max_tokens: null }); }
function removeModel(models: ByokModel[], index: number): void { if (models.length > 1) models.splice(index, 1); }
async function discoverModels(key: string, draft: { base_url: string; api_key: string }): Promise<void> {
  discoveredFor.value = key;
  isDiscovering.value = true;
  try {
    const found = await store.discoverByokConnectionModels({ base_url: draft.base_url.trim(), protocol: "openai_chat_completions", ...(key === "__new__" ? {} : { provider_id: key }), ...(draft.api_key.trim() ? { api_key: draft.api_key.trim() } : {}) });
    discovered.value = found;
    selectedDiscovered.value = new Set(found.map((model) => model.model_id));
  } finally {
    isDiscovering.value = false;
  }
}
function adoptDiscovered(models: ByokModel[]): void {
  const existing = new Map(models.filter((model) => model.model_id.trim()).map((model) => [model.model_id.trim(), model]));
  discovered.value.forEach((model) => { if (selectedDiscovered.value.has(model.model_id)) existing.set(model.model_id, { ...model }); });
  models.splice(0, models.length, ...existing.values());
  discovered.value = [];
  discoveredFor.value = "";
}
function toggleDiscovered(modelId: string): void {
  const next = new Set(selectedDiscovered.value);
  if (next.has(modelId)) next.delete(modelId); else next.add(modelId);
  selectedDiscovered.value = next;
}
function createDisabled(): boolean {
  return !canManageByokCredentials(store.currentUser) || !store.byokRuntimeAvailable || store.byokIsBusy || !idPattern.test(connectionId.value) || !newDraft.display_name.trim() || !newDraft.base_url.trim() || !newDraft.api_key.trim() || !validModels(newDraft.models);
}
async function createConnection(): Promise<void> {
  if (createDisabled()) return;
  const saved = await store.saveByokConnection(connectionId.value, { display_name: newDraft.display_name.trim(), base_url: newDraft.base_url.trim(), model_id: newDraft.model_id.trim() || newDraft.models[0]!.model_id.trim(), protocol: "openai_chat_completions", api_key: newDraft.api_key.trim(), models: cloneModels(newDraft.models) });
  if (!saved) return;
  connectionId.value = ""; newDraft.display_name = ""; newDraft.base_url = ""; newDraft.model_id = ""; newDraft.api_key = "";
  newDraft.models.splice(0, newDraft.models.length, { model_id: "", display_name: "", context_length: 0, max_tokens: null });
}
async function updateConnection(status: ByokCredentialStatus): Promise<void> {
  const draft = draftFor(status.provider_id);
  if (!validModels(draft.models) || !draft.base_url.trim() || !draft.display_name.trim()) return;
  await store.saveByokConnection(status.provider_id, { display_name: draft.display_name.trim(), base_url: draft.base_url.trim(), model_id: draft.model_id.trim() || draft.models[0]!.model_id.trim(), protocol: "openai_chat_completions", ...(draft.api_key.trim() ? { api_key: draft.api_key.trim() } : {}), models: cloneModels(draft.models) });
  draft.api_key = "";
}
</script>

<template>
  <section class="account-section" aria-label="使用自己的 API Key">
    <div class="account-section-head"><h3>使用自己的 API Key</h3><span class="chip chip-ok">Key 加密保存</span></div>
    <p class="account-note">支持 OpenAI Chat Completions 兼容网关、自部署服务和一个连接下的多个模型。Key 不会写入浏览器存储、URL、历史或 Trace。</p>
    <p v-if="store.isLoadingByokCredentials" class="note note-plain" role="status">正在读取已保存连接。</p>
    <p v-else-if="store.byokMessage" class="note" :class="store.byokMessageIsError ? 'note-bad' : 'note-ok'" :role="store.byokMessageIsError ? 'alert' : 'status'">{{ store.byokMessage }}</p>
    <p v-if="store.byokProviderDisabledReason()" class="note note-warn">{{ store.byokProviderDisabledReason() }}</p>

    <div class="byok">
      <article v-for="connection in store.byokCredentialStatuses" :key="connection.provider_id" class="byok-card">
        <header class="byok-card-head"><strong>{{ connection.display_name }}</strong><code>{{ connection.provider_id }}</code></header>
        <form class="byok-form" @submit.prevent="updateConnection(connection)">
          <label class="field-hint">显示名称</label><input v-model="draftFor(connection.provider_id).display_name" maxlength="100" :disabled="!connection.writable || store.byokIsBusy" />
          <label class="field-hint">API Base URL</label><input v-model="draftFor(connection.provider_id).base_url" maxlength="2048" :disabled="!connection.writable || store.byokIsBusy" />
          <label class="field-hint">默认模型</label><select v-model="draftFor(connection.provider_id).model_id" :disabled="!connection.writable || store.byokIsBusy"><option v-for="model in draftFor(connection.provider_id).models" :key="model.model_id" :value="model.model_id">{{ model.display_name || model.model_id }}</option></select>
          <div class="model-list-head"><span class="field-hint">模型目录</span><button type="button" class="btn btn-quiet btn-small" @click="addModel(draftFor(connection.provider_id).models)">添加模型</button></div>
          <div v-for="(model, index) in draftFor(connection.provider_id).models" :key="`${connection.provider_id}-${index}`" class="model-row"><input v-model="model.model_id" placeholder="模型 ID" maxlength="100" :disabled="!connection.writable || store.byokIsBusy" /><input v-model="model.display_name" placeholder="显示名称（可选）" maxlength="200" :disabled="!connection.writable || store.byokIsBusy" /><button type="button" class="btn btn-quiet btn-small" :disabled="draftFor(connection.provider_id).models.length <= 1" @click="removeModel(draftFor(connection.provider_id).models, index)">移除</button></div>
          <label class="field-hint">替换 API Key（留空则保留现有 Key）</label><input v-model="draftFor(connection.provider_id).api_key" type="password" autocomplete="new-password" maxlength="8192" placeholder="留空则不修改" :disabled="!connection.writable || store.byokIsBusy" />
          <button type="button" class="btn btn-quiet" :disabled="!connection.writable || store.byokIsBusy || isDiscovering" @click="discoverModels(connection.provider_id, draftFor(connection.provider_id))">{{ isDiscovering && discoveredFor === connection.provider_id ? "读取中" : "从端点获取模型（可选）" }}</button>
          <div v-if="discovered.length && discoveredFor === connection.provider_id" class="discovery-card"><div class="model-list-head"><strong>选择要加入的模型</strong><button type="button" class="btn btn-primary btn-small" @click="adoptDiscovered(draftFor(connection.provider_id).models)">加入所选</button></div><label v-for="model in discovered" :key="model.model_id" class="discovery-row"><input type="checkbox" :checked="selectedDiscovered.has(model.model_id)" @change="toggleDiscovered(model.model_id)" /><span>{{ model.display_name }} <code>{{ model.model_id }}</code></span></label></div>
          <div class="byok-form-acts"><button type="submit" class="btn btn-primary" :disabled="!connection.writable || store.byokIsBusy || !validModels(draftFor(connection.provider_id).models)">保存连接配置</button><button type="button" class="btn btn-danger" :disabled="!store.canDeleteByokCredential(connection.provider_id)" @click="store.removeByokCredential(connection)">删除连接</button></div>
        </form>
        <div class="byok-state"><strong>{{ connection.masked_key }}</strong><span v-if="connection.expires_at">到期 {{ formatCredentialExpiry(connection.expires_at) }}</span><span v-if="!connection.writable">只读：当前会话不可替换或删除</span></div>
      </article>

      <article class="byok-card byok-create">
        <header class="byok-card-head"><strong>添加自定义供应商</strong></header>
        <form class="byok-form byok-create-grid" @submit.prevent="createConnection">
          <label class="field-hint" for="byok-connection-id">连接 ID</label><input id="byok-connection-id" v-model="connectionId" placeholder="my-provider" maxlength="64" /><small>以小写字母开头，只使用小写字母、数字和连字符。</small>
          <label class="field-hint" for="byok-display-name">显示名称</label><input id="byok-display-name" v-model="newDraft.display_name" placeholder="我的模型供应商" maxlength="100" />
          <label class="field-hint" for="byok-base-url">API Base URL</label><input id="byok-base-url" v-model="newDraft.base_url" placeholder="https://api.example.com/v1" maxlength="2048" />
          <div class="model-list-head"><span class="field-hint">模型目录</span><button type="button" class="btn btn-quiet btn-small" @click="addModel(newDraft.models)">添加模型</button></div>
          <div v-for="(model, index) in newDraft.models" :key="`new-${index}`" class="model-row"><input v-model="model.model_id" placeholder="模型 ID" maxlength="100" /><input v-model="model.display_name" placeholder="显示名称（可选）" maxlength="200" /><button type="button" class="btn btn-quiet btn-small" :disabled="newDraft.models.length <= 1" @click="removeModel(newDraft.models, index)">移除</button></div>
          <label class="field-hint" for="byok-new-key">API Key</label><input id="byok-new-key" v-model="newDraft.api_key" type="password" autocomplete="new-password" maxlength="8192" placeholder="sk-..." />
          <button type="button" class="btn btn-quiet" :disabled="store.byokIsBusy || isDiscovering || !newDraft.base_url.trim() || !newDraft.api_key.trim()" @click="discoverModels('__new__', newDraft)">{{ isDiscovering && discoveredFor === '__new__' ? "读取中" : "从端点获取模型（可选）" }}</button>
          <div v-if="discovered.length && discoveredFor === '__new__'" class="discovery-card"><div class="model-list-head"><strong>选择要加入的模型</strong><button type="button" class="btn btn-primary btn-small" @click="adoptDiscovered(newDraft.models)">加入所选</button></div><label v-for="model in discovered" :key="model.model_id" class="discovery-row"><input type="checkbox" :checked="selectedDiscovered.has(model.model_id)" @change="toggleDiscovered(model.model_id)" /><span>{{ model.display_name }} <code>{{ model.model_id }}</code></span></label></div>
          <button type="submit" class="btn btn-primary" :disabled="createDisabled()">保存连接</button>
        </form>
      </article>
    </div>
  </section>
</template>

<style>
.account-note { margin: 0 0 10px; color: var(--text-muted); font-size: var(--fs-xs); line-height: 1.55; }
.byok { display: grid; gap: 8px; }
.byok-card, .discovery-card { display: grid; gap: 7px; padding: 9px; border: 1px solid var(--line); border-radius: var(--r-sm); background: var(--raised); }
.byok-create { border-style: dashed; }
.byok-card-head, .model-list-head { display: flex; align-items: center; gap: 7px; }
.byok-card-head strong { font-size: var(--fs-xs); font-weight: 650; }
.byok-card-head code { margin-left: auto; color: var(--text-muted); font-size: var(--fs-2xs); }
.byok-form { display: grid; gap: 5px; }
.model-list-head .btn { margin-left: auto; }
.model-row { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) auto; gap: 5px; }
.model-row input { min-width: 0; }
.byok-form-acts { display: flex; gap: 5px; }
.byok-form-acts .btn { flex: 1 1 auto; }
.byok-state { display: grid; gap: 1px; padding: 6px 8px; border-radius: var(--r-sm); background: var(--ok-wash); color: var(--ok-text); font-size: var(--fs-2xs); }
.byok-state strong { font-size: var(--fs-2xs); }
.byok-create-grid small { color: var(--text-muted); font-size: var(--fs-2xs); }
.btn-small { padding: 3px 6px; font-size: var(--fs-2xs); }
.discovery-card { background: var(--sunken); }
.discovery-row { display: flex; align-items: center; gap: 7px; font-size: var(--fs-xs); }
.discovery-row code { color: var(--text-muted); }
@media (max-width: 520px) { .model-row { grid-template-columns: 1fr; } }
</style>
