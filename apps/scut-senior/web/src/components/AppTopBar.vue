<script setup lang="ts">
import AccountMenu from "./AccountMenu.vue";
import { useAppStore } from "../composables/useAppStore";

const store = useAppStore();
</script>

<template>
  <header class="topbar">
    <button
      type="button"
      class="btn btn-quiet rail-toggle"
      :aria-expanded="store.railOpen ? 'true' : 'false'"
      aria-controls="conversation-rail"
      @click="store.railOpen = !store.railOpen"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true">
        <path d="M4 6h16M4 12h16M4 18h10" />
      </svg>
      历史记录
    </button>

    <a
      class="brand"
      href="https://github.com/AlexBybye/SCUT_CS"
      target="_blank"
      rel="noopener"
      title="前往 GitHub 仓库"
    >
      <img class="brand-icon" src="/icon.jpeg" alt="SCUT 老学长" />
      <span class="brand-name">SCUT 老学长</span>
    </a>

    <span class="topbar-spacer"></span>

    <div class="account">
      <span v-if="store.isLoadingAuth" class="account-muted">正在确认登录状态</span>
      <template v-else-if="store.currentUser">
        <button
          type="button"
          class="account-button"
          :aria-expanded="store.accountMenuOpen ? 'true' : 'false'"
          @click="store.accountMenuOpen = !store.accountMenuOpen"
        >
          <img v-if="store.githubAvatarUrl()" class="avatar" :src="store.githubAvatarUrl()" alt="" />
          <span class="account-name">
            {{ store.currentUser.is_mock ? "本地 Mock" : `@${store.currentUser.github_login}` }}
          </span>
          <svg class="account-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="m6 9 6 6 6-6" />
          </svg>
        </button>

        <AccountMenu v-if="store.accountMenuOpen" />
      </template>
      <button v-else type="button" class="btn btn-primary" @click="store.startGithubLogin">
        使用 GitHub 登录
      </button>
    </div>
  </header>
</template>

<style>
.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  text-decoration: none;
  color: var(--text);
}

.brand-icon {
  width: 34px;
  height: 34px;
  flex: 0 0 auto;
  border-radius: var(--r-md);
  object-fit: cover;
  box-shadow: var(--shadow-panel);
}

.brand-name {
  font-size: var(--fs-md);
  font-weight: 800;
  letter-spacing: -0.01em;
  white-space: nowrap;
}

.account {
  position: relative;
  display: flex;
  align-items: center;
  flex: 0 0 auto;
}

.account-muted {
  color: var(--text-muted);
  font-size: var(--fs-xs);
}

.account-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 9px 5px 5px;
  border: 1px solid var(--line);
  border-radius: var(--r-sm);
  background: var(--raised);
  color: var(--text);
  cursor: pointer;
}

.account-button:hover {
  border-color: var(--line-strong);
}

.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
}

.account-name {
  font-size: var(--fs-sm);
  font-weight: 650;
}

.account-caret {
  width: 16px;
  height: 16px;
  color: var(--text-soft);
}

/* 窄窗口：顶栏只留图标与头像。 */
@media (max-width: 899px) {
  .brand-name,
  .account-name {
    display: none;
  }

  .account-button {
    padding: 4px;
  }
}
</style>
