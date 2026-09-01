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

function clamp01(value: number): number {
  return Math.min(1, Math.max(0, value));
}

// ── 明暗主题滑块（三档，可拖拽） ──────────────────────────────
const trackEl = ref<HTMLDivElement | null>(null);
// 拖动中记录 0..1 的原始比例；松手后吸附到最近档位。null 表示不在拖动。
const dragRatio = ref<number | null>(null);

// 滑块中心位置：三等分格心在 1/6、3/6、5/6；拖动时把原始比例映射到同一区间。
const thumbPosition = computed(() => {
  if (dragRatio.value === null) return (store.themeMode + 0.5) / 3;
  return clamp01(dragRatio.value) * (2 / 3) + 1 / 6;
});

const ariaValueText = computed(() => THEME_MODE_LABELS[store.themeMode]);

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

// ── 检索方式滑块（两档，可拖拽） ──────────────────────────────
const searchTrackEl = ref<HTMLDivElement | null>(null);
const searchDragRatio = ref<number | null>(null);

const searchThumbPosition = computed(() => {
  if (searchDragRatio.value === null) return store.crossCourseSearchEnabled ? 1 : 0;
  return clamp01(searchDragRatio.value);
});

const searchModeHelp = computed(() =>
  store.crossCourseSearchEnabled
    ? "可在当前对话中选择多个课程插件进行检索。私人知识库材料较多时，跨课程检索可能明显变慢。"
    : "仅检索当前对话所属课程，范围更集中、响应更稳定；如需联合多个课程，请切换到跨学科检索。",
);

function searchRatioFromPointer(event: PointerEvent): number {
  const track = searchTrackEl.value;
  if (!track) return 0;
  const rect = track.getBoundingClientRect();
  if (rect.width <= 0) return 0;
  return clamp01((event.clientX - rect.left) / rect.width);
}

function onSearchPointerDown(event: PointerEvent): void {
  if (event.pointerType === "mouse" && event.button !== 0) return;
  searchTrackEl.value?.setPointerCapture(event.pointerId);
  searchDragRatio.value = searchRatioFromPointer(event);
}

function onSearchPointerMove(event: PointerEvent): void {
  if (searchDragRatio.value === null) return;
  searchDragRatio.value = searchRatioFromPointer(event);
}

function onSearchPointerFinish(): void {
  if (searchDragRatio.value === null) return;
  store.crossCourseSearchEnabled = searchDragRatio.value >= 0.5;
  searchDragRatio.value = null;
}

function toggleCrossCourse(): void {
  store.crossCourseSearchEnabled = !store.crossCourseSearchEnabled;
}

// ── 品牌色滑块（两档渐变色，可拖拽） ─────────────────────────
const accentTrackEl = ref<HTMLDivElement | null>(null);
const accentDragRatio = ref<number | null>(null);

const accentThumbPosition = computed(() => {
  if (accentDragRatio.value === null) return store.accentTheme === "indigo" ? 0 : 1;
  return clamp01(accentDragRatio.value);
});

const accentValueText = computed(() =>
  store.accentTheme === "indigo" ? "靛青" : "朱砂",
);

function accentRatioFromPointer(event: PointerEvent): number {
  const track = accentTrackEl.value;
  if (!track) return 0;
  const rect = track.getBoundingClientRect();
  if (rect.width <= 0) return 0;
  return clamp01((event.clientX - rect.left) / rect.width);
}

function onAccentPointerDown(event: PointerEvent): void {
  if (event.pointerType === "mouse" && event.button !== 0) return;
  accentTrackEl.value?.setPointerCapture(event.pointerId);
  accentDragRatio.value = accentRatioFromPointer(event);
}

function onAccentPointerMove(event: PointerEvent): void {
  if (accentDragRatio.value === null) return;
  accentDragRatio.value = accentRatioFromPointer(event);
}

function onAccentPointerFinish(): void {
  if (accentDragRatio.value === null) return;
  store.setAccentTheme(accentDragRatio.value >= 0.5 ? "vermilion" : "indigo");
  accentDragRatio.value = null;
}

function onAccentKeydown(event: KeyboardEvent): void {
  const toIndigo =
    event.key === "ArrowLeft" || event.key === "ArrowDown" || event.key === "Home";
  const toVermilion =
    event.key === "ArrowRight" || event.key === "ArrowUp" || event.key === "End";
  if (toIndigo) store.setAccentTheme("indigo");
  else if (toVermilion) store.setAccentTheme("vermilion");
  else return;
  event.preventDefault();
}
</script>

<template>
  <section class="account-section" aria-label="助手设置">
    <div class="account-section-head">
      <h3>回答偏好</h3>
    </div>

    <div class="search-mode-field">
      <span class="field-label">检索方式</span>
      <div
        ref="searchTrackEl"
        class="search-mode-slider"
        :class="{ 'is-cross': store.crossCourseSearchEnabled, 'is-dragging': searchDragRatio !== null }"
        role="switch"
        tabindex="0"
        :aria-checked="store.crossCourseSearchEnabled ? 'true' : 'false'"
        aria-label="检索方式"
        :style="{ '--thumb-pos': String(searchThumbPosition) }"
        @pointerdown="onSearchPointerDown"
        @pointermove="onSearchPointerMove"
        @pointerup="onSearchPointerFinish"
        @pointercancel="onSearchPointerFinish"
        @keydown.space.prevent="toggleCrossCourse"
        @keydown.enter.prevent="toggleCrossCourse"
      >
        <span class="search-mode-thumb" aria-hidden="true"></span>
        <span class="search-mode-stop" :class="{ 'is-active': !store.crossCourseSearchEnabled }">单学科检索</span>
        <span class="search-mode-stop" :class="{ 'is-active': store.crossCourseSearchEnabled }">跨学科检索</span>
      </div>
      <small class="search-mode-help">
        {{ searchModeHelp }}
      </small>
    </div>

    <div class="knowledge-settings">
      <span class="field-label">知识范围</span>
      <div class="knowledge-options" role="radiogroup" aria-label="知识范围">
        <label class="knowledge-card" :class="{ 'is-active': store.knowledgeScope === 'course_first' }">
          <input v-model="store.knowledgeScope" type="radio" name="knowledge-scope" value="course_first" />
          <span class="knowledge-card-title">资料优先</span>
          <span class="knowledge-card-desc">允许标记的通用补充</span>
        </label>
        <label class="knowledge-card" :class="{ 'is-active': store.knowledgeScope === 'course_only' }">
          <input v-model="store.knowledgeScope" type="radio" name="knowledge-scope" value="course_only" />
          <span class="knowledge-card-title">仅课程资料</span>
          <span class="knowledge-card-desc">证据不足即停</span>
        </label>
      </div>
      <label class="knowledge-bilibili" :class="{ 'is-disabled': store.knowledgeScope === 'course_only' }">
        <input v-model="store.includeBilibiliResources" type="checkbox" :disabled="store.knowledgeScope === 'course_only'" />
        <span class="knowledge-bilibili-copy">
          <strong>返回 B站延伸学习</strong>
          <small>模型给出聚焦词后只返回匿名搜索链接，不返回具体视频直链。仅课程资料模式强制关闭。</small>
        </span>
      </label>
    </div>

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
        <span class="chip chip-accent">{{ accentValueText }}</span>
      </div>
      <div class="accent-slider-wrap">
        <div
          ref="accentTrackEl"
          class="accent-slider-track"
          :class="{ 'is-dragging': accentDragRatio !== null }"
          role="slider"
          tabindex="0"
          aria-label="品牌色"
          :aria-valuemin="0"
          :aria-valuemax="1"
          :aria-valuenow="store.accentTheme === 'indigo' ? 0 : 1"
          :aria-valuetext="accentValueText"
          :style="{ '--thumb-pos': String(accentThumbPosition) }"
          @pointerdown="onAccentPointerDown"
          @pointermove="onAccentPointerMove"
          @pointerup="onAccentPointerFinish"
          @pointercancel="onAccentPointerFinish"
          @keydown="onAccentKeydown"
        >
          <span class="accent-slider-thumb" aria-hidden="true"></span>
        </div>
        <div class="accent-slider-labels"><span>靛青</span><span>朱砂</span></div>
      </div>
    </div>

    <p class="note note-plain theme-storage-note">
      当前保存在本机浏览器（localStorage），换设备不同步；后续将作为用户设置字段与 API Key 一同存储到服务器。
    </p>

    <a
      v-if="store.currentUser && !store.currentUser.is_mock"
      class="maintainer-entry"
      href="/maintainer"
    >
      <span>
        <strong>维护中台（beta）</strong>
        <small>查看反馈与课程资料贡献</small>
      </span>
      <span class="beta-mark">beta</span>
    </a>
  </section>
</template>

<style>
/* ── 回答偏好 · 检索方式 ─────────────────────────────────── */
.search-mode-field {
  display: grid;
  gap: 6px;
  margin-bottom: 14px;
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
  touch-action: none;
  user-select: none;
  -webkit-user-select: none;
}

.search-mode-slider.is-dragging {
  cursor: grabbing;
}

.search-mode-slider:focus-visible {
  outline: 3px solid color-mix(in srgb, var(--focus) 34%, transparent);
  outline-offset: 2px;
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
  box-shadow: var(--shadow-panel);
  transform: translateX(calc(var(--thumb-pos, 0) * 100%));
  transition: transform 180ms ease;
}

.search-mode-slider.is-dragging .search-mode-thumb {
  transition: none;
}

.search-mode-stop {
  z-index: 1;
  padding: 7px 10px;
  color: var(--text-soft);
  font-size: var(--fs-xs);
  text-align: center;
  transition: color 180ms ease;
  pointer-events: none;
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

/* ── 知识范围 ───────────────────────────────────────────── */
.knowledge-settings {
  display: grid;
  gap: 8px;
  margin: 0 0 20px;
}

.knowledge-options {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.knowledge-card {
  position: relative;
  display: grid;
  gap: 2px;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: var(--r-sm);
  background: var(--raised);
  cursor: pointer;
  transition:
    border-color var(--dur-fast) ease,
    background var(--dur-fast) ease,
    box-shadow var(--dur-fast) ease;
}

.knowledge-card:hover {
  border-color: var(--line-strong);
}

.knowledge-card.is-active {
  border-color: var(--accent);
  background: var(--accent-wash);
  box-shadow: 0 0 0 1px var(--accent);
}

.knowledge-card input {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
}

.knowledge-card input:focus-visible + .knowledge-card-title {
  outline: 3px solid color-mix(in srgb, var(--focus) 34%, transparent);
  outline-offset: 2px;
}

.knowledge-card-title {
  font-size: var(--fs-xs);
  font-weight: 650;
}

.knowledge-card-desc {
  color: var(--text-muted);
  font-size: var(--fs-2xs);
  line-height: 1.5;
}

.knowledge-bilibili {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  padding: 10px 12px;
  border: 1px dashed var(--line-strong);
  border-radius: var(--r-sm);
  cursor: pointer;
}

.knowledge-bilibili.is-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.knowledge-bilibili input {
  margin-top: 3px;
  accent-color: var(--accent);
}

.knowledge-bilibili-copy {
  display: grid;
  gap: 3px;
}

.knowledge-bilibili-copy strong {
  font-size: var(--fs-xs);
  font-weight: 650;
}

.knowledge-bilibili-copy small {
  color: var(--text-muted);
  line-height: 1.5;
}

@media (max-width: 520px) {
  .knowledge-options {
    grid-template-columns: 1fr;
  }
}

/* ── 明暗主题滑块 ───────────────────────────────────────── */
.theme-picker {
  display: grid;
  gap: 6px;
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

/* ── 品牌色（渐变色滑块） ───────────────────────────────── */
.accent-picker {
  display: grid;
  gap: 6px;
  margin-top: 14px;
}

.accent-slider-wrap {
  display: grid;
  gap: 6px;
}

.accent-slider-track {
  position: relative;
  height: 32px;
  border: 1px solid var(--line-strong);
  border-radius: 999px;
  background: linear-gradient(90deg, #3a5a8c, #a83b22);
  cursor: pointer;
  touch-action: none;
  user-select: none;
  -webkit-user-select: none;
}

.accent-slider-track.is-dragging {
  cursor: grabbing;
}

.accent-slider-track:focus-visible {
  outline: 3px solid color-mix(in srgb, var(--focus) 34%, transparent);
  outline-offset: 2px;
}

.accent-slider-thumb {
  position: absolute;
  top: 50%;
  left: calc(var(--thumb-pos, 0) * (100% - 22px) + 11px);
  width: 22px;
  height: 22px;
  transform: translate(-50%, -50%);
  border: 2px solid var(--raised);
  border-radius: 50%;
  background: var(--raised);
  box-shadow: var(--shadow-panel);
  transition: left 140ms ease;
  pointer-events: none;
}

.accent-slider-track.is-dragging .accent-slider-thumb {
  transition: none;
}

.accent-slider-labels {
  display: flex;
  justify-content: space-between;
  color: var(--text-soft);
  font-size: var(--fs-2xs);
}

/* ── 维护中台入口（助手设置底部） ────────────────────────── */
.maintainer-entry {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 14px;
  padding: 12px 14px;
  border: 1px solid var(--line);
  border-radius: var(--r-md);
  color: var(--text);
  text-decoration: none;
  background: color-mix(in srgb, var(--accent) 8%, var(--panel));
}

.maintainer-entry:hover {
  border-color: var(--accent);
}

.maintainer-entry span:first-child {
  display: grid;
  gap: 3px;
}

.maintainer-entry strong {
  font-size: var(--fs-sm);
}

.maintainer-entry small {
  color: var(--text-muted);
}

.beta-mark {
  border-radius: 999px;
  padding: 3px 7px;
  color: var(--accent);
  background: color-mix(in srgb, var(--accent) 14%, transparent);
  font-size: 11px;
  font-weight: 700;
}

.theme-storage-note {
  margin-top: 10px;
}
</style>
