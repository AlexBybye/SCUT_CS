<script setup lang="ts">
import { computed, ref } from "vue";
import {
  ACCENT_LABELS,
  THEME_MODE_LABELS,
  type AccentTheme,
  type ThemeMode,
} from "../themePreference";
import { useAppStore } from "../composables/useAppStore";

const store = useAppStore();

// 两套可选品牌色：靛青（默认）/ 朱砂。与明暗模式相互独立。
const ACCENT_OPTIONS: { accent: AccentTheme; label: string; swatch: string }[] = [
  { accent: "indigo", label: ACCENT_LABELS.indigo, swatch: "#3a5a8c" },
  { accent: "vermilion", label: ACCENT_LABELS.vermilion, swatch: "#a83b22" },
];

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

    <div class="accent-picker" role="radiogroup" aria-label="品牌色">
      <span class="accent-picker-label">品牌色</span>
      <div class="accent-swatches">
        <label
          v-for="option in ACCENT_OPTIONS"
          :key="option.accent"
          class="accent-swatch"
          :class="{ 'is-active': store.accentTheme === option.accent }"
        >
          <input
            v-model="store.accentTheme"
            type="radio"
            name="accent"
            :value="option.accent"
          />
          <span class="accent-dot" :style="{ background: option.swatch }" aria-hidden="true"></span>
          <span class="accent-name">{{ option.label }}</span>
        </label>
      </div>
    </div>

    <p class="note note-plain theme-storage-note">
      当前保存在本机浏览器（localStorage），换设备不同步；后续将作为用户设置字段与 API Key 一同存储到服务器。
    </p>
  </section>
</template>

<style>
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
