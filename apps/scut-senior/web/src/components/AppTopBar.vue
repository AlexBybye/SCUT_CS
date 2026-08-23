<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from "vue";
import AccountMenu from "./AccountMenu.vue";
import { useAppStore } from "../composables/useAppStore";

const store = useAppStore();

// 个人中心浮层的根：开关按钮与浮层面板都在其中，点它们不算“外部”。
const accountRoot = ref<HTMLElement | null>(null);

// 点击个人中心（含其子组件）以外的任意位置时收回浮层。
function onDocumentPointerDown(event: PointerEvent): void {
  const root = accountRoot.value;
  const target = event.target;
  if (!root || !(target instanceof Node) || root.contains(target)) return;
  store.accountMenuOpen = false;
}

// 浮层展开时才挂全局监听，收起即摘除；capture 保证先于其他 click 逻辑。
watch(
  () => store.accountMenuOpen,
  (open) => {
    if (open) {
      document.addEventListener("pointerdown", onDocumentPointerDown, true);
    } else {
      document.removeEventListener("pointerdown", onDocumentPointerDown, true);
    }
  },
);

onBeforeUnmount(() => {
  document.removeEventListener("pointerdown", onDocumentPointerDown, true);
});
</script>

<template>
  <header class="topbar">
    <button
      type="button"
      class="btn btn-quiet rail-toggle"
      :aria-expanded="store.railOpen ? 'true' : 'false'"
      aria-controls="conversation-rail"
      aria-label="历史记录"
      @click="store.railOpen = !store.railOpen"
    >
      <!-- 侧栏开合图标：展开时箭头朝左（收起），折叠时朝右（展开）。 -->
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <rect x="3" y="4.5" width="18" height="15" rx="2" />
        <path d="M9.5 4.5v15" />
        <path v-if="store.railOpen" d="m16 9.5-2.5 2.5L16 14.5" />
        <path v-else d="m11.5 9.5 2.5 2.5-2.5 2.5" />
      </svg>
      <span class="rail-toggle-label">历史记录</span>
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

    <div ref="accountRoot" class="account">
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

        <Transition name="menu-pop">
          <AccountMenu v-if="store.accountMenuOpen" />
        </Transition>
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
  /* 品牌名任何窗口宽度都不消失、不被压缩截断。 */
  flex: 0 0 auto;
}

.rail-toggle-label {
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

/* 窄窗口：账号名收进头像；品牌名始终保留，只做缩放让位。 */
@media (max-width: 899px) {
  .account-name {
    display: none;
  }

  .account-button {
    padding: 4px;
  }
}

/* 极窄窗口：进一步压缩非品牌元素，保住“SCUT 老学长”完整可读。 */
@media (max-width: 479px) {
  .topbar {
    gap: 7px;
    padding: 0 10px;
  }

  .rail-toggle {
    font-size: 0;
    gap: 0;
    padding: 0 8px;
  }

  .rail-toggle .btn,
  .rail-toggle svg {
    width: 18px;
    height: 18px;
  }

  .rail-toggle-label {
    display: none;
  }

  .brand {
    gap: 7px;
  }

  .brand-name {
    font-size: var(--fs-sm);
  }

  .brand-icon {
    width: 30px;
    height: 30px;
  }
}
</style>
