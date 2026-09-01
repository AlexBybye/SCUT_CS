<script setup lang="ts">
import { computed, ref } from "vue";
import { THEME_MODE_LABELS, type ThemeMode } from "../themePreference";
import { useAppStore } from "../composables/useAppStore";

const store = useAppStore();

// 三档停靠点：0 Auto（跟随系统）· 1 太阳恒亮 · 2 月亮恒暗。
const STOPS: { mode: ThemeMode; label: string }[] = [
  { mode: 0, label: THEME_MODE_LABELS[0] },
  { mode: 1, label: THEME_MODE_LABELS[1] },
  { mode: 2, label: THEME_MODE_LABELS[2] },
];

const trackEl = ref<HTMLDivElement | null>(null);
// 拖动中记录 0..1 的原始比例；松手后吸附到最近档位。null 表示不在拖动。
const dragRatio = ref<number | null>(null);

// 滑块中心位置：三等分格心在 1/6、3/6、5/6；拖动时把原始比例映射到同一区间。
const thumbPosition = computed(() => {
  if (dragRatio.value === null) return (store.themeMode + 0.5) / 3;
  return clamp01(dragRatio.value) * (2 / 3) + 1 / 6;
});

const ariaValueText = computed(() => THEME_MODE_LABELS[store.themeMode]);
const searchModeHelp = computed(() =>
  store.crossCourseSearchEnabled
    ? "可在当前对话中选择多个课程插件进行检索。私人知识库材料较多时，跨课程检索可能明显变慢。"
    : "仅检索当前对话所属课程，范围更集中、响应更稳定；如需联合多个课程，请切换到跨学科检索。",
);

function clamp01(value: number): number {
  return Math.min(1, Math.max(0, value));
}

function ratioFromPointer(event: PointerEvent): number {
  const track = trackEl.value;
  if (!track) return 0;
  const rect = track.getBoundingClientRect();
  if (rect.width <= 0) return 0;
  return clamp01((event.clientX - rect.left) / rect.width);
}

function onPointerDown(event: PointerEvent): void {
  // 非鼠标左键（触屏/笔）同样允许拖动；仅忽略鼠标右键。
  if (event.pointerType === "mouse" && event.button !== 0) return;
  // setPointerCapture 后移出轨道也能继续收到 move/up，拖动不中断。
  trackEl.value?.setPointerCapture(event.pointerId);
  dragRatio.value = ratioFromPointer(event);
}

function onPointerMove(event: PointerEvent): void {
  if (dragRatio.value === null) return;
  dragRatio.value = ratioFromPointer(event);
}

function onPointerFinish(): void {
  if (dragRatio.value === null) return;
  store.setThemeMode(Math.round(clamp01(dragRatio.value) * 2));
  dragRatio.value = null;
}

function onKeydown(event: KeyboardEvent): void {
  switch (event.key) {
    case "ArrowLeft":
    case "ArrowDown":
      store.setThemeMode(store.themeMode - 1);
      break;
    case "ArrowRight":
    case "ArrowUp":
      store.setThemeMode(store.themeMode + 1);
      break;
    case "Home":
      store.setThemeMode(0);
      break;
    case "End":
      store.setThemeMode(2);
      break;
    default:
      return;
  }
  event.preventDefault();
}
</script>

<template>
  <section class="account-section" aria-label="助手设置">
    <div class="account-section-head">
      <h3>回答偏好</h3>
    </div>
    <div class="assistant-preference-grid">
      <div class="search-mode-field">
        <span class="field-label">检索方式</span>
        <div
          class="search-mode-slider"
          :class="{ 'is-cross': store.crossCourseSearchEnabled }"
          role="switch"
          tabindex="0"
          :aria-checked="store.crossCourseSearchEnabled ? 'true' : 'false'"
          aria-label="检索方式"
          @click="store.crossCourseSearchEnabled = !store.crossCourseSearchEnabled"
          @keydown.space.prevent="store.crossCourseSearchEnabled = !store.crossCourseSearchEnabled"
          @keydown.enter.prevent="store.crossCourseSearchEnabled = !store.crossCourseSearchEnabled"
        >
          <span class="search-mode-thumb" aria-hidden="true"></span>
          <span class="search-mode-stop" :class="{ 'is-active': !store.crossCourseSearchEnabled }">单学科检索</span>
          <span class="search-mode-stop" :class="{ 'is-active': store.crossCourseSearchEnabled }">跨学科检索</span>
        </div>
        <small class="search-mode-help">
          {{ searchModeHelp }}
        </small>
      </div>
    </div>

    <fieldset class="knowledge-settings">
      <legend>知识范围</legend>
      <label class="knowledge-option">
        <input v-model="store.knowledgeScope" type="radio" value="course_first" />
        <span>资料优先，允许标记的通用补充</span>
      </label>
      <label class="knowledge-option">
        <input v-model="store.knowledgeScope" type="radio" value="course_only" />
        <span>仅课程资料，证据不足即停</span>
      </label>
      <label class="knowledge-option knowledge-option-check">
        <input v-model="store.includeBilibiliResources" type="checkbox" :disabled="store.knowledgeScope === 'course_only'" />
        <span><strong>返回 B站延伸学习</strong><small>模型给出聚焦词后只返回匿名搜索链接，不返回具体视频直链。仅课程资料模式强制关闭。</small></span>
      </label>
    </fieldset>

    <div class="account-section-head">
      <h3>外观主题</h3>
      <span class="chip chip-accent">{{ ariaValueText }}</span>
    </div>
    <p class="account-note">
      默认 Auto 跟随系统主题
    </p>

    <div class="theme-picker">
      <div
        ref="trackEl"
        class="theme-slider"
        :class="{ 'is-dragging': dragRatio !== null }"
        role="slider"
        tabindex="0"
        aria-label="主题模式"
        :aria-valuemin="0"
        :aria-valuemax="2"
        :aria-valuenow="store.themeMode"
        :aria-valuetext="ariaValueText"
        :style="{ '--thumb-pos': String(thumbPosition) }"
        @pointerdown="onPointerDown"
        @pointermove="onPointerMove"
        @pointerup="onPointerFinish"
        @pointercancel="onPointerFinish"
        @keydown="onKeydown"
      >
        <span class="theme-slider-thumb" aria-hidden="true"></span>
        <span class="theme-slider-stops" aria-hidden="true">
          <!-- 半明半暗：Auto -->
          <span class="theme-slider-icon" :class="{ 'is-active': store.themeMode === 0 }">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
              <circle cx="12" cy="12" r="9" />
              <path d="M12 3a9 9 0 0 1 0 18Z" fill="currentColor" stroke="none" />
            </svg>
          </span>
          <!-- 太阳：恒亮色 -->
          <span class="theme-slider-icon" :class="{ 'is-active': store.themeMode === 1 }">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
              <circle cx="12" cy="12" r="4" />
              <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
            </svg>
          </span>
          <!-- 月亮：恒暗色 -->
          <span class="theme-slider-icon" :class="{ 'is-active': store.themeMode === 2 }">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z" />
            </svg>
          </span>
        </span>
      </div>
      <div class="theme-slider-labels">
        <span
          v-for="stop in STOPS"
          :key="stop.mode"
          :class="{ 'is-active': store.themeMode === stop.mode }"
        >
          {{ stop.label }}
        </span>
      </div>
    </div>

    <div class="accent-picker">
      <div class="account-section-head">
        <h3>品牌色</h3>
        <span class="chip chip-accent">{{ store.accentTheme === 'indigo' ? '靛青' : '朱砂' }}</span>
      </div>
      <div class="accent-slider-wrap">
        <input
          class="accent-slider"
          type="range"
          min="0"
          max="1"
          step="1"
          :value="store.accentTheme === 'indigo' ? 0 : 1"
          aria-label="品牌色"
          aria-valuemin="0"
          aria-valuemax="1"
          :aria-valuenow="store.accentTheme === 'indigo' ? 0 : 1"
          :aria-valuetext="store.accentTheme === 'indigo' ? '靛青' : '朱砂'"
          @input="store.setAccentTheme(($event.target as HTMLInputElement).value === '0' ? 'indigo' : 'vermilion')"
        />
        <div class="accent-slider-labels"><span>靛青</span><span>朱砂</span></div>
      </div>
    </div>

    <p class="note note-plain theme-storage-note">
      当前保存在本机浏览器（localStorage），换设备不同步；后续将作为用户设置字段与 API Key 一同存储到服务器。
    </p>
  </section>
</template>

<style>
.knowledge-settings {
  display: grid;
  gap: 8px;
  margin: 14px 0 20px;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: var(--r-md);
}
.knowledge-settings legend { padding: 0 4px; font-weight: 700; }
.knowledge-option { display: flex; gap: 8px; align-items: flex-start; }
.knowledge-option span { display: grid; gap: 3px; }
.knowledge-option small { color: var(--muted); line-height: 1.5; }
.accent-slider-wrap { display: grid; gap: 6px; }
.accent-slider {
  width: 100%;
  height: 10px;
  accent-color: var(--accent);
  cursor: grab;
  background: linear-gradient(90deg, #3a5a8c, #a83b22);
}
.accent-slider:active { cursor: grabbing; }
.accent-slider-labels { display: flex; justify-content: space-between; color: var(--muted); font-size: 12px; }

.theme-picker {
  display: grid;
  gap: 6px;
}

.search-mode-field {
  display: grid;
  gap: 6px;
  grid-column: 1 / -1;
}

.field-label {
  color: var(--text-soft);
  font-size: var(--fs-xs);
  font-weight: 650;
}

.search-mode-slider {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  min-height: 42px;
  padding: 3px;
  border: 1px solid var(--line-strong);
  border-radius: 999px;
  background: var(--sunken);
  cursor: pointer;
  isolation: isolate;
}

.search-mode-thumb {
  position: absolute;
  z-index: 0;
  top: 3px;
  bottom: 3px;
  left: 3px;
  width: calc(50% - 3px);
  border-radius: 999px;
  background: var(--raised);
  box-shadow: var(--shadow-sm);
  transition: transform 180ms ease;
}

.search-mode-slider.is-cross .search-mode-thumb {
  transform: translateX(100%);
}

.search-mode-stop {
  z-index: 1;
  padding: 7px 10px;
  color: var(--text-soft);
  font-size: var(--fs-xs);
  text-align: center;
  transition: color 180ms ease;
}

.search-mode-stop.is-active {
  color: var(--text);
  font-weight: 700;
}

.search-mode-help {
  color: var(--text-soft);
  font-size: var(--fs-2xs);
  line-height: 1.5;
}

.assistant-preference-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 14px;
}

@media (max-width: 520px) {
  .assistant-preference-grid {
    grid-template-columns: 1fr;
  }
}

/* 轨道：整条可拖、可点、可聚焦；44px 满足触屏命中。 */
.theme-slider {
  position: relative;
  height: 44px;
  border: 1px solid var(--line);
  border-radius: var(--r-sm);
  background: var(--sunken);
  cursor: pointer;
  touch-action: none;
  user-select: none;
  -webkit-user-select: none;
}

.theme-slider.is-dragging {
  cursor: grabbing;
}

.theme-slider:focus-visible {
  outline: 3px solid color-mix(in srgb, var(--focus) 34%, transparent);
  outline-offset: 2px;
}

/* 滑块：宽度为三等分之一，中心沿 --thumb-pos（0..1）滑动，两端恰好对齐格心。 */
.theme-slider-thumb {
  position: absolute;
  top: 3px;
  bottom: 3px;
  left: calc(var(--thumb-pos, 0.1667) * 100%);
  width: calc(100% / 3 - 6px);
  transform: translateX(-50%);
  border: 1px solid var(--line-strong);
  border-radius: var(--r-xs);
  background: var(--raised);
  box-shadow: var(--shadow-panel);
  transition: left 140ms ease;
  pointer-events: none;
}

.theme-slider.is-dragging .theme-slider-thumb {
  transition: none;
}

/* 图标层：三等分格心摆放，浮在滑块之上；点击穿透给轨道统一处理。 */
.theme-slider-stops {
  position: absolute;
  inset: 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  pointer-events: none;
}

.theme-slider-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--text-soft);
  transition: color 90ms ease;
}

.theme-slider-icon svg {
  width: 18px;
  height: 18px;
}

.theme-slider-icon.is-active {
  color: var(--accent);
}

.theme-slider-labels {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  color: var(--text-soft);
  font-size: var(--fs-2xs);
  text-align: center;
}

.theme-slider-labels .is-active {
  color: var(--accent);
  font-weight: 650;
}

.theme-storage-note {
  margin-top: 10px;
}

/* 品牌色（强调色）选择器：两枚色卡单选，与明暗模式互不干扰。 */
.accent-picker {
  display: grid;
  gap: 6px;
}

.accent-picker-label {
  color: var(--text);
  font-size: var(--fs-xs);
  font-weight: 650;
}

.accent-swatches {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px;
}

.accent-swatch {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border: 1px solid var(--line);
  border-radius: var(--r-sm);
  background: var(--raised);
  cursor: pointer;
  transition:
    border-color var(--dur-fast) ease,
    background var(--dur-fast) ease,
    box-shadow var(--dur-fast) ease;
}

.accent-swatch:hover {
  border-color: var(--line-strong);
}

.accent-swatch.is-active {
  border-color: var(--accent);
  background: var(--accent-wash);
  box-shadow: 0 0 0 1px var(--accent);
}

.accent-swatch input {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
}

.accent-swatch input:focus-visible + .accent-dot {
  outline: 3px solid color-mix(in srgb, var(--focus) 34%, transparent);
  outline-offset: 2px;
}

.accent-dot {
  width: 16px;
  height: 16px;
  flex: 0 0 auto;
  border-radius: 50%;
  box-shadow: inset 0 0 0 1px rgb(0 0 0 / 0.12);
}

.accent-name {
  font-size: var(--fs-xs);
  font-weight: 600;
}
</style>
