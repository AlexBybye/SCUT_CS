<script setup lang="ts">
import { canManageByokCredentials } from "../byokSession";
import { formatCredentialExpiry } from "../appConfig";
import { useAppStore } from "../composables/useAppStore";

const store = useAppStore();
</script>

<template>
  <section class="account-section" aria-label="使用自己的 API Key">
    <div class="account-section-head">
      <h3>使用自己的 API Key</h3>
      <span class="chip chip-ok">会话级加密</span>
    </div>
    <p class="account-note">
      Key 只在密码输入框中短暂存在，保存请求结束即清空；不会写入浏览器存储、URL、历史或模型目录。
    </p>

    <p v-if="store.isLoadingByokCredentials" class="note note-plain" role="status">
      正在读取当前登录会话的脱敏凭据状态。
    </p>
    <p
      v-else-if="store.byokMessage"
      class="note"
      :class="store.byokMessageIsError ? 'note-bad' : 'note-ok'"
      :role="store.byokMessageIsError ? 'alert' : 'status'"
    >
      {{ store.byokMessage }}
    </p>

    <div class="byok">
      <article
        v-for="provider in store.byokProvidersForDisplay"
        :key="provider.provider_id"
        class="byok-card"
        :class="{ 'byok-card-off': !store.byokRuntimeAvailable || !provider.enabled }"
      >
        <header class="byok-card-head">
          <strong>{{ provider.display_name }}</strong>
          <span class="chip" :class="store.byokRuntimeAvailable && provider.enabled ? 'chip-ok' : ''">
            {{ store.byokRuntimeAvailable && provider.enabled ? "已启用" : "未开启" }}
          </span>
        </header>

        <div v-if="provider.models[0]" class="byok-model">
          <span>固定模型</span>
          <strong>{{ provider.models[0].company }} · {{ provider.models[0].display_name }}</strong>
          <code>{{ provider.models[0].model_id }}</code>
        </div>

        <div v-if="store.byokCredentialStatus(provider.provider_id)?.configured" class="byok-state">
          <strong>当前会话已配置</strong>
          <span>{{ store.byokCredentialStatus(provider.provider_id)?.masked_key || "Key 已脱敏" }}</span>
          <span v-if="store.byokCredentialStatus(provider.provider_id)?.expires_at">
            到期 {{ formatCredentialExpiry(store.byokCredentialStatus(provider.provider_id)?.expires_at || "") }}
          </span>
          <span v-if="!store.byokCredentialWritable(provider.provider_id)">只读：当前会话不可替换或删除</span>
        </div>

        <p v-if="store.byokProviderDisabledReason(provider)" class="note note-warn">
          {{ store.byokProviderDisabledReason(provider) }}
        </p>

        <form class="byok-form" @submit.prevent="store.submitByokCredential(provider)">
          <label :for="`byok-key-${provider.provider_id}`" class="field-hint">API Key</label>
          <input
            :id="`byok-key-${provider.provider_id}`"
            v-model="store.byokKeyDrafts[provider.provider_id]"
            type="password"
            autocomplete="new-password"
            autocapitalize="none"
            spellcheck="false"
            maxlength="512"
            placeholder="输入后仅提交给本站后端"
            :disabled="
              !canManageByokCredentials(store.currentUser) ||
              !store.byokRuntimeAvailable ||
              !provider.enabled ||
              store.byokIsBusy
            "
          />
          <div class="byok-form-acts">
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="!store.canSaveByokCredential(provider)"
            >
              {{
                store.savingByokProviderId === provider.provider_id
                  ? "保存中"
                  : store.byokCredentialStatus(provider.provider_id)?.configured
                    ? "替换"
                    : "保存"
              }}
            </button>
            <button
              v-if="store.byokCredentialStatus(provider.provider_id)?.configured"
              type="button"
              class="btn btn-danger"
              :disabled="!store.canDeleteByokCredential(provider.provider_id)"
              @click="store.removeByokCredential(provider)"
            >
              {{ store.deletingByokProviderId === provider.provider_id ? "删除中" : "删除" }}
            </button>
          </div>
        </form>
      </article>
    </div>
  </section>
</template>

<style>
.account-note {
  margin: 0 0 10px;
  color: var(--text-muted);
  font-size: var(--fs-xs);
  line-height: 1.55;
}

.byok {
  display: grid;
  gap: 8px;
}

.byok-card {
  display: grid;
  gap: 7px;
  padding: 9px;
  border: 1px solid var(--line);
  border-radius: var(--r-sm);
  background: var(--raised);
}

.byok-card-off {
  border-style: dashed;
}

.byok-card-head {
  display: flex;
  align-items: baseline;
  gap: 7px;
}

.byok-card-head strong {
  font-size: var(--fs-xs);
  font-weight: 650;
}

.byok-card-head > span:last-child {
  margin-left: auto;
}

.byok-model {
  display: grid;
  gap: 1px;
  padding: 6px 8px;
  border-radius: var(--r-sm);
  background: var(--sunken);
  font-size: var(--fs-2xs);
}

.byok-model > span {
  color: var(--text-muted);
}

.byok-model > strong {
  font-size: var(--fs-2xs);
  font-weight: 650;
  overflow-wrap: anywhere;
}

.byok-model > code {
  overflow: hidden;
  color: var(--text-muted);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.byok-state {
  display: grid;
  gap: 1px;
  padding: 6px 8px;
  border-radius: var(--r-sm);
  background: var(--ok-wash);
  color: var(--ok-text);
  font-size: var(--fs-2xs);
}

.byok-state > strong {
  font-size: var(--fs-2xs);
  font-weight: 650;
}

.byok-form {
  display: grid;
  gap: 5px;
}

.byok-form-acts {
  display: flex;
  gap: 5px;
}

.byok-form-acts .btn {
  flex: 1 1 auto;
}
</style>
