<script setup lang="ts">
import { onBeforeUnmount, onMounted } from "vue";
import AppTopBar from "./components/AppTopBar.vue";
import ConversationRail from "./components/ConversationRail.vue";
import TranscriptPanel from "./components/TranscriptPanel.vue";
import Composer from "./components/Composer.vue";
import { useAppStore } from "./composables/useAppStore";
import MaintainerPanel from "./components/MaintainerPanel.vue";

const store = useAppStore();
const isMaintainerRoute = window.location.pathname === "/maintainer";

// 浮层态的左轨与检查器需要 Escape 退出，否则窄屏下只能靠再次点按钮。
function onGlobalKeydown(event: KeyboardEvent): void {
  if (event.key !== "Escape") return;
  if (store.accountMenuOpen) {
    store.accountMenuOpen = false;
  } else if (store.railOpen && window.innerWidth < 640) {
    store.railOpen = false;
  }
}

function onWindowResize(): void {
  // 窗口缩到手机宽度时强制收起左轨；放大后保持用户当前状态。
  if (window.innerWidth < 640) store.railOpen = false;
}

onMounted(() => {
  void store.loadAuth();
  void store.loadCourses();
  void store.loadModels();
  window.addEventListener("keydown", onGlobalKeydown);
  window.addEventListener("resize", onWindowResize);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", onGlobalKeydown);
  window.removeEventListener("resize", onWindowResize);
  store.abortActiveWorkflow("页面已离开，运行已取消。");
});
</script>

<template>
  <MaintainerPanel v-if="isMaintainerRoute" />
  <div v-else class="shell">
    <a href="#transcript" class="skip-link">跳到运行记录</a>

    <AppTopBar />

    <div class="shell-body" :data-rail="store.railOpen ? 'open' : 'closed'">
      <!-- 窄屏浮层的点击遮罩；宽屏下由 CSS 隐藏，不参与布局。 -->
      <button
        type="button"
        class="scrim"
        :data-rail="store.railOpen ? 'open' : 'closed'"
        aria-label="关闭浮层"
        @click="store.railOpen = false"
      ></button>

      <ConversationRail />

      <main class="main">
        <div class="main-head">
          <h1>{{ store.conversationSnapshot?.title || "新会话" }}</h1>
          <div class="main-head-facts">
            <span class="chip">{{ store.selectedCourse?.display_name ?? "未选课程" }}</span>
            <span class="chip">{{ store.activeWorkflow.label }}</span>
          </div>
        </div>

        <TranscriptPanel />
        <Composer />
      </main>
    </div>
  </div>
</template>
