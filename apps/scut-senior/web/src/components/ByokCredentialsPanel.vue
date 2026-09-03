<script setup lang="ts">
import { computed, ref } from "vue";
import { canManageByokCredentials } from "../byokSession";
import { formatCredentialExpiry } from "../appConfig";
import { useAppStore } from "../composables/useAppStore";

const store = useAppStore();
const connectionId = ref("");
const displayName = ref("");
const baseUrl = ref("");
const modelId = ref("");
const apiKey = ref("");
const idPattern = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;

const createDisabled = computed(() =>
  !canManageByokCredentials(store.currentUser) ||
  !store.byokRuntimeAvailable ||
  store.byokIsBusy ||
  !idPattern.test(connectionId.value) ||
  !displayName.value.trim() ||
  !baseUrl.value.trim() ||
  !modelId.value.trim() ||
  !apiKey.value.trim(),
);

async function createConnection(): Promise<void> {
  if (createDisabled.value) return;
  const saved = await store.saveByokConnection(connectionId.value, {
    display_name: displayName.value.trim(),
    base_url: baseUrl.value.trim(),
    model_id: modelId.value.trim(),
    protocol: "openai_chat_completions",
    api_key: apiKey.value.trim(),
  });
  apiKey.value = "";
  if (!saved) return;
  connectionId.value = "";
  displayName.value = "";
  baseUrl.value = "";
  modelId.value = "";
}
</script>

<template>
  <section class="account-section" aria-label="自定义模型连接">
    <div class="account-section-head">
      <h3>自定义模型连接</h3>
      <span class="chip chip-ok">Key 加密保存</span>
    </div>
    <p class="account-note">
      添加兼容 OpenAI Chat Completions 的供应商。Key 不会写入浏览器存储、URL、历史或 Trace。
    </p>

    <p v-if="store.isLoadingByokCredentials" class="note note-plain" role="status">
      正在读取已保存连接。
    </p>
    <p
      v-else-if="store.byokMessage"
      class="note"
      :class="store.byokMessageIsError ? 'note-bad' : 'note-ok'"
      :role="store.byokMessageIsError ? 'alert' : 'status'"
    >
      {{ store.byokMessage }}
    </p>
    <p v-if="store.byokProviderDisabledReason()" class="note note-warn">
      {{ store.byokProviderDisabledReason() }}
    </p>

    <div class="byok">
      <article
        v-for="connection in store.byokCredentialStatuses"
        :key="connection.provider_id"
        class="byok-card"
      >
        <header class="byok-card-head">
          <strong>{{ connection.display_name }}</strong>
          <code>{{ connection.provider_id }}</code>
        </header>
        <div class="byok-model">
          <span>OpenAI Chat Completions</span>
          <strong>{{ connection.model_id }}</strong>
          <code>{{ connection.base_url }}</code>
        </div>
        <div class="byok-state">
          <strong>{{ connection.masked_key }}</strong>
          <span v-if="connection.expires_at">
            到期 {{ formatCredentialExpiry(connection.expires_at) }}
          </span>
          <span v-if="!connection.writable">只读：当前会话不可替换或删除</span>
        </div>
        <form class="byok-form" @submit.prevent="store.submitByokCredential(connection)">
          <label :for="`byok-key-${connection.provider_id}`" class="field-hint">替换 API Key</label>
          <input
            :id="`byok-key-${connection.provider_id}`"
            v-model="store.byokKeyDrafts[connection.provider_id]"
            type="password"
            autocomplete="new-password"
            maxlength="8192"
            placeholder="留空则不修改"
            :disabled="!connection.writable || store.byokIsBusy"
          />
          <div class="byok-form-acts">
            <button type="submit" class="btn btn-primary" :disabled="!store.canSaveByokCredential(connection)">
              {{ store.savingByokProviderId === connection.provider_id ? "保存中" : "替换 Key" }}
            </button>
            <button
              type="button"
              class="btn btn-danger"
              :disabled="!store.canDeleteByokCredential(connection.provider_id)"
              @click="store.removeByokCredential(connection)"
            >
              {{ store.deletingByokProviderId === connection.provider_id ? "删除中" : "删除连接" }}
            </button>
          </div>
        </form>
      </article>

      <article class="byok-card byok-create">
        <header class="byok-card-head"><strong>添加供应商</strong></header>
        <form class="byok-form byok-create-grid" @submit.prevent="createConnection">
          <label class="field-hint" for="byok-connection-id">连接 ID</label>
          <input id="byok-connection-id" v-model="connectionId" placeholder="my-provider" maxlength="64" />
          <small>以小写字母开头，只使用小写字母、数字和连字符。</small>

          <label class="field-hint" for="byok-display-name">显示名称</label>
          <input id="byok-display-name" v-model="displayName" placeholder="我的模型供应商" maxlength="100" />

          <label class="field-hint" for="byok-base-url">API Base URL</label>
          <input id="byok-base-url" v-model="baseUrl" placeholder="https://api.example.com/v1" maxlength="2048" />

          <label class="field-hint" for="byok-model-id">模型 ID</label>
          <input id="byok-model-id" v-model="modelId" placeholder="provider/model-name" maxlength="100" />

          <label class="field-hint" for="byok-new-key">API Key</label>
          <input id="byok-new-key" v-model="apiKey" type="password" autocomplete="new-password" maxlength="8192" placeholder="sk-..." />

          <button type="submit" class="btn btn-primary" :disabled="createDisabled">
            {{ store.savingByokProviderId === connectionId ? "保存中" : "保存连接" }}
          </button>
        </form>
      </article>
    </div>
  </section>
</template>

<style>
.account-note { margin: 0 0 10px; color: var(--text-muted); font-size: var(--fs-xs); line-height: 1.55; }
.byok { display: grid; gap: 8px; }
.byok-card { display: grid; gap: 7px; padding: 9px; border: 1px solid var(--line); border-radius: var(--r-sm); background: var(--raised); }
.byok-create { border-style: dashed; }
.byok-card-head { display: flex; align-items: baseline; gap: 7px; }
.byok-card-head strong { font-size: var(--fs-xs); font-weight: 650; }
.byok-card-head code { margin-left: auto; color: var(--text-muted); font-size: var(--fs-2xs); }
.byok-model, .byok-state { display: grid; gap: 1px; padding: 6px 8px; border-radius: var(--r-sm); font-size: var(--fs-2xs); }
.byok-model { background: var(--sunken); }
.byok-model > span, .byok-model > code, .byok-create-grid small { color: var(--text-muted); }
.byok-model > strong, .byok-state > strong { font-size: var(--fs-2xs); font-weight: 650; overflow-wrap: anywhere; }
.byok-model > code { overflow-wrap: anywhere; }
.byok-state { background: var(--ok-wash); color: var(--ok-text); }
.byok-form { display: grid; gap: 5px; }
.byok-form-acts { display: flex; gap: 5px; }
.byok-form-acts .btn { flex: 1 1 auto; }
.byok-create-grid small { font-size: var(--fs-2xs); }
</style>
