<script setup lang="ts">
import PluginRegistryPanel from "./PluginRegistryPanel.vue";
import ByokCredentialsPanel from "./ByokCredentialsPanel.vue";
import AssistantSettingsPanel from "./AssistantSettingsPanel.vue";
import { useAppStore } from "../composables/useAppStore";

const store = useAppStore();
</script>

<template>
  <div class="account-menu" role="menu">
    <div class="account-menu-head">
      <span class="account-menu-title">个人中心</span>
      <span class="chip chip-mono">
        {{ store.selectedModel?.display_name ?? (store.isLoadingModels ? "模型目录加载中" : "模型目录不可用") }}
      </span>
    </div>
    <div class="account-tabs" role="tablist">
      <button
        type="button"
        class="account-tab"
        role="tab"
        :aria-selected="store.accountTab === 'credentials'"
        @click="store.openAccountTab('credentials')"
      >
        我的 Key
      </button>
      <button
        type="button"
        class="account-tab"
        role="tab"
        :aria-selected="store.accountTab === 'plugins'"
        @click="store.openAccountTab('plugins')"
      >
        插件
      </button>
      <button
        type="button"
        class="account-tab"
        role="tab"
        :aria-selected="store.accountTab === 'assistant'"
        @click="store.openAccountTab('assistant')"
      >
        助手设置
      </button>
    </div>

    <div class="account-scroll">
      <ByokCredentialsPanel v-if="store.accountTab === 'credentials'" />
      <AssistantSettingsPanel v-else-if="store.accountTab === 'assistant'" />
      <section v-else class="account-section" aria-label="内部插件管理">
        <div class="account-section-head">
          <h3>内部插件管理</h3>
        </div>
        <PluginRegistryPanel
          :can-manage-plugins="Boolean(store.currentUser && !store.currentUser.is_mock)"
          @changed="store.onPluginChanged"
        />
      </section>
    </div>

    <button
      v-if="store.currentUser && !store.currentUser.is_mock"
      type="button"
      class="btn btn-quiet account-signout"
      @click="store.signOut"
    >
      退出登录
    </button>
  </div>
</template>

<style>
.account-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  z-index: 40;
  width: min(420px, calc(100vw - 24px));
  max-height: min(76vh, 680px);
  display: flex;
  flex-direction: column;
  border: 1px solid var(--line);
  border-radius: var(--r-md);
  background: var(--panel);
  box-shadow: var(--shadow-float);
}

.account-menu-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 12px 14px;
  border-bottom: 1px solid var(--line);
}

.account-menu-title {
  font-size: var(--fs-sm);
  font-weight: 700;
}

.account-tabs {
  display: flex;
  gap: 4px;
  padding: 8px 10px 0;
  border-bottom: 1px solid var(--line);
}

.account-tab {
  padding: 8px 12px;
  border: 0;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: var(--text-muted);
  font-size: var(--fs-sm);
  cursor: pointer;
}

.account-tab[aria-selected="true"] {
  border-bottom-color: var(--accent);
  color: var(--text);
  font-weight: 650;
}

.account-scroll {
  overflow-y: auto;
  padding: 12px 14px;
}

.account-section-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.account-section-head h3 {
  margin: 0;
  font-size: var(--fs-md);
}

.account-signout {
  width: 100%;
  border-top: 1px solid var(--line);
  border-radius: 0 0 var(--r-md) var(--r-md);
  justify-content: center;
}
</style>
