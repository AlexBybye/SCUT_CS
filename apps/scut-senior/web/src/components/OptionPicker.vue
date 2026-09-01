<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";

/**
 * OptionPicker · 可搜索下拉
 *
 * 用自定义「combobox」替换原生 <select>，解决项目里课程/模型下拉
 * 「又长又宽、行数多、无搜索、无分组」的体验问题：
 *   - 触发钮只显示当前值 + 一个状态点，绝不撑宽配置条；
 *   - 面板含搜索框（按 label / hint 过滤）、内滚限高、可用性分组；
 *   - 完整键盘导航（↑ ↓ / Enter / Esc / Home / End）与 ARIA combobox 语义；
 *   - 面板用 fixed 定位并钳制在视口内；默认向上弹出（composer 贴在底部）。
 */

export type OptionDot = "ok" | "warn" | "accent" | "";

export interface OptionItem {
  value: string;
  label: string;
  hint?: string;
  disabled?: boolean;
  dot?: OptionDot;
  group?: string;
}

const props = withDefaults(
  defineProps<{
    modelValue: string | string[];
    options: OptionItem[];
    multiple?: boolean;
    placeholder?: string;
    searchable?: boolean;
    maxVisible?: number;
    ariaLabel?: string;
    placement?: "down" | "up";
    disabled?: boolean;
  }>(),
  {
    placeholder: "请选择",
    searchable: true,
    maxVisible: 8,
    multiple: false,
    placement: "down",
    disabled: false,
  },
);

const emit = defineEmits<{
  (e: "update:modelValue", value: string | string[]): void;
  (e: "change", value: string | string[]): void;
}>();

const root = ref<HTMLElement | null>(null);
const trigger = ref<HTMLButtonElement | null>(null);
const searchEl = ref<HTMLInputElement | null>(null);
const listboxEl = ref<HTMLUListElement | null>(null);
const panelRoot = ref<HTMLDivElement | null>(null);

const open = ref(false);
const query = ref("");
const activeIndex = ref(-1);
const panelStyle = ref<Record<string, string>>({});
const panelReady = ref(false);

const selectedValues = computed<string[]>(() =>
  Array.isArray(props.modelValue) ? props.modelValue : props.modelValue ? [props.modelValue] : [],
);
const selected = computed(() =>
  props.options.find((option) => option.value === selectedValues.value[0]),
);
const selectedLabel = computed(() => {
  if (!props.multiple) return selected.value?.label ?? props.placeholder;
  const labels = props.options
    .filter((option) => selectedValues.value.includes(option.value))
    .map((option) => option.label);
  if (!labels.length) return props.placeholder;
  return labels.length === 1 ? labels[0] : `${labels[0]} 等 ${labels.length} 门`;
});

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase();
  if (!q) return props.options;
  return props.options.filter(
    (option) =>
      option.label.toLowerCase().includes(q) ||
      (option.hint ? option.hint.toLowerCase().includes(q) : false),
  );
});

// 渲染行：无搜索且有分组时插入组头；搜索时会拍平。
type Row =
  | { type: "group"; label: string }
  | { type: "option"; option: OptionItem; flatIndex: number };

const rows = computed<Row[]>(() => {
  const out: Row[] = [];
  let lastGroup = "";
  filtered.value.forEach((option, index) => {
    if (!query.value) {
      const group = option.group ?? "";
      if (group !== lastGroup) {
        lastGroup = group;
        if (group) out.push({ type: "group", label: group });
      }
    }
    out.push({ type: "option", option, flatIndex: index });
  });
  return out;
});

// 仅可聚焦（非分组、非禁用）的行在 rows 里的下标。
const focusableRowIndexes = computed(() =>
  rows.value.reduce<number[]>((acc, row, index) => {
    if (row.type === "option" && !row.option.disabled) acc.push(index);
    return acc;
  }, []),
);

function openPanel(): void {
  if (open.value) return;
  open.value = true;
  panelReady.value = false;
  query.value = "";
  activeIndex.value = -1;
  updatePanelPosition();
  nextTick(() => {
    if (props.searchable) searchEl.value?.focus();
    else scrollRowIntoView(activeIndex.value);
  });
}

function closePanel(): void {
  open.value = false;
  query.value = "";
}

function toggle(): void {
  if (props.disabled) return;
  if (open.value) closePanel();
  else openPanel();
}

function selectOption(option: OptionItem): void {
  if (option.disabled) return;
  if (props.multiple) {
    const next = selectedValues.value.includes(option.value)
      ? selectedValues.value.filter((value) => value !== option.value)
      : [...selectedValues.value, option.value];
    emit("update:modelValue", next);
    emit("change", next);
    return;
  }
  emit("update:modelValue", option.value);
  emit("change", option.value);
  closePanel();
}

function moveActive(delta: number): void {
  focusableRowIndexes.value;
  const indexes = focusableRowIndexes.value;
  if (!indexes.length) return;
  const currentPos = indexes.indexOf(activeIndex.value);
  let pos = currentPos < 0 ? (delta > 0 ? -1 : 0) : currentPos + delta;
  if (pos < 0) pos = indexes.length - 1;
  if (pos >= indexes.length) pos = 0;
  activeIndex.value = indexes[pos]!;
  scrollRowIntoView(activeIndex.value);
}

function scrollRowIntoView(index: number): void {
  if (index < 0) return;
  const list = listboxEl.value;
  const item = list?.querySelector<HTMLElement>(`[data-row-index="${index}"]`);
  item?.scrollIntoView({ block: "nearest" });
}

function onTriggerKeydown(event: KeyboardEvent): void {
  if (open.value) {
    // 面板已展开：方向键在触发钮上移动高亮（非可搜索、焦点仍在触发钮时也通用）。
    if (event.key === "ArrowDown") {
      event.preventDefault();
      moveActive(1);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      moveActive(-1);
    } else if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      if (activeIndex.value >= 0) {
        const row = rows.value[activeIndex.value];
        if (row?.type === "option") selectOption(row.option);
      }
    } else if (event.key === "Escape") {
      closePanel();
    }
    return;
  }
  if (event.key === "ArrowDown" || event.key === "ArrowUp" || event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    openPanel();
  } else if (event.key === "Escape") {
    closePanel();
  }
}

function onPanelKeydown(event: KeyboardEvent): void {
  switch (event.key) {
    case "ArrowDown":
      event.preventDefault();
      moveActive(1);
      break;
    case "ArrowUp":
      event.preventDefault();
      moveActive(-1);
      break;
    case "Home":
      event.preventDefault();
      activeIndex.value = focusableRowIndexes.value[0] ?? -1;
      scrollRowIntoView(activeIndex.value);
      break;
    case "End":
      event.preventDefault();
      {
        const indexes = focusableRowIndexes.value;
        activeIndex.value = indexes.length ? indexes[indexes.length - 1]! : -1;
      }
      scrollRowIntoView(activeIndex.value);
      break;
    case "Enter":
      event.preventDefault();
      if (activeIndex.value >= 0) {
        const row = rows.value[activeIndex.value];
        if (row?.type === "option") selectOption(row.option);
      }
      break;
    case "Escape":
      event.preventDefault();
      closePanel();
      break;
    case "Tab":
      closePanel();
      break;
    default:
      return;
  }
}

function updatePanelPosition(): void {
  const trg = trigger.value;
  if (!trg) return;
  const rect = trg.getBoundingClientRect();
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const up = props.placement === "up";
  const width = Math.max(220, Math.min(320, rect.width, vw - 16));

  let left = rect.left;
  if (rect.right + width > vw - 8) left = rect.right - width;
  left = Math.max(8, Math.min(left, vw - width - 8));

  const style: Record<string, string> = { left: `${left}px`, width: `${width}px` };
  if (up) {
    // 向上弹出（composer 贴在底部）：锚定面板底边在触发钮上沿，高度向上生长。
    style.bottom = `${Math.max(0, vh - rect.top + 8)}px`;
    style.maxHeight = `${Math.max(200, rect.top - 12)}px`;
  } else {
    style.top = `${rect.bottom + 8}px`;
    style.maxHeight = `${Math.max(200, vh - rect.bottom - 12)}px`;
  }
  panelStyle.value = style;
  panelReady.value = true;
}

function onDocumentPointerDown(event: PointerEvent): void {
  const target = event.target;
  const contains =
    target instanceof Node &&
    (root.value?.contains(target) || panelRoot.value?.contains(target));
  if (!contains) closePanel();
}

watch(open, (isOpen) => {
  if (isOpen) {
    document.addEventListener("pointerdown", onDocumentPointerDown, true);
  } else {
    document.removeEventListener("pointerdown", onDocumentPointerDown, true);
  }
});

watch(() => props.modelValue, () => {
  // 面板开着时选中项被外部刷新，滚动到对应行。
  if (open.value) {
    const index = focusableRowIndexes.value.find((i) => {
      const row = rows.value[i];
      return row?.type === "option" && row.option.value === props.modelValue;
    });
    if (index !== undefined) activeIndex.value = index;
  }
});

onBeforeUnmount(() => {
  document.removeEventListener("pointerdown", onDocumentPointerDown, true);
});
</script>

<template>
  <div ref="root" class="op">
    <button
      ref="trigger"
      type="button"
      class="op-trigger"
      :aria-label="ariaLabel"
      role="combobox"
      :aria-expanded="open ? 'true' : 'false'"
      aria-haspopup="listbox"
      aria-controls="op-listbox"
      :disabled="props.disabled"
      @click="toggle"
      @keydown="onTriggerKeydown"
    >
      <span v-if="selected?.dot" class="op-dot" :class="`is-${selected.dot}`" aria-hidden="true"></span>
      <span class="op-trigger-label truncate">{{ selectedLabel }}</span>
      <svg class="op-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path :d="open ? 'm6 15 6-6 6 6' : 'm6 9 6 6 6-6'" />
      </svg>
    </button>

    <Teleport to="body">
      <Transition name="op-pop">
        <div
          v-if="open && panelReady"
          ref="panelRoot"
          class="op-panel"
          :style="panelStyle"
          @keydown="onPanelKeydown"
        >
          <div v-if="searchable" class="op-search">
            <svg class="op-search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="11" cy="11" r="7" />
              <path d="m20 20-3.5-3.5" />
            </svg>
            <input
              ref="searchEl"
              v-model="query"
              type="text"
              class="op-search-input"
              placeholder="搜索…"
              role="combobox"
              aria-autocomplete="list"
              aria-controls="op-listbox"
              :aria-expanded="'true'"
              @keydown="onPanelKeydown"
            />
          </div>

          <ul ref="listboxEl" id="op-listbox" class="op-list" role="listbox" :aria-label="ariaLabel" :style="{ '--max-visible': String(maxVisible) }">
            <template v-for="(row, index) in rows" :key="row.type === 'group' ? row.label : row.option.value">
              <li
                v-if="row.type === 'group'"
                class="op-group"
                role="presentation"
              >
                {{ row.label }}
              </li>
              <li
                v-else
                class="op-option"
                :data-row-index="index"
                :class="{ 'is-active': activeIndex === index, 'is-disabled': row.option.disabled }"
                role="option"
                :aria-selected="selectedValues.includes(row.option.value) ? 'true' : 'false'"
                :aria-disabled="row.option.disabled ? 'true' : undefined"
                @click="selectOption(row.option)"
                @mouseenter="activeIndex = index"
              >
                <span v-if="row.option.dot" class="op-dot" :class="`is-${row.option.dot}`" aria-hidden="true"></span>
                <span class="op-option-main">
                  <span class="op-option-label truncate">{{ row.option.label }}</span>
                  <span v-if="row.option.hint" class="op-option-hint truncate">{{ row.option.hint }}</span>
                </span>
                <svg
                  v-if="selectedValues.includes(row.option.value)"
                  class="op-check"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  aria-hidden="true"
                >
                  <path d="m5 13 4 4L19 7" />
                </svg>
              </li>
            </template>

            <li v-if="!rows.length" class="op-empty" role="presentation">没有匹配项</li>
          </ul>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style>
.op {
  position: relative;
  min-width: 0;
  display: inline-flex;
}

/* 触发钮：配置条里的紧凑控件，width 由父级 .composer-bar 控制。 */
.op-trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  height: 28px;
  padding: 0 8px;
  border: 1px solid var(--line);
  border-radius: var(--r-sm);
  background: var(--sunken);
  color: var(--text);
  font-size: var(--fs-2xs);
  cursor: pointer;
  transition:
    border-color var(--dur-fast) ease,
    background var(--dur-fast) ease,
    box-shadow var(--dur-fast) ease;
}

.op-trigger:hover {
  border-color: var(--line-strong);
}

.op-trigger:focus-visible {
  outline: 3px solid color-mix(in srgb, var(--focus) 34%, transparent);
  outline-offset: 2px;
}

.op-trigger:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.op-trigger-label {
  flex: 1 1 auto;
  min-width: 0;
  max-width: 100%;
  color: var(--text);
}

.op-caret {
  width: 14px;
  height: 14px;
  flex: 0 0 auto;
  color: var(--text-soft);
  transition: transform var(--dur) var(--ease-out);
}

/* 状态点：默认隐藏，有值才显示。 */
.op-dot {
  width: 7px;
  height: 7px;
  flex: 0 0 auto;
  border-radius: 50%;
  background: var(--text-soft);
}

.op-dot.is-ok {
  background: var(--ok-line);
}

.op-dot.is-warn {
  background: var(--warn-line);
}

.op-dot.is-accent {
  background: var(--accent);
}

/* 面板：fixed 定位，JS 钳制在视口内，向下弹出默认、本组件多用向上。 */
.op-panel {
  position: fixed;
  display: flex;
  flex-direction: column;
  z-index: 70;
  overflow: hidden;
  border: 1px solid var(--line-strong);
  border-radius: var(--r-md);
  background: var(--raised);
  box-shadow: var(--shadow-float);
}

.op-panel:focus-visible {
  outline: 3px solid color-mix(in srgb, var(--focus) 34%, transparent);
  outline-offset: 2px;
}

.op-search {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 8px;
  border-bottom: 1px solid var(--line);
}

.op-search-icon {
  width: 15px;
  height: 15px;
  flex: 0 0 auto;
  color: var(--text-soft);
}

/* 搜索输入：压过全局 input[type="text"]（44px + 边框 + 底色），保持内嵌无边框。 */
.op-search input.op-search-input {
  min-height: 28px;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--text);
  font-size: var(--fs-xs);
}

.op-search input.op-search-input::placeholder {
  color: var(--text-soft);
}

.op-search input.op-search-input:focus {
  outline: none;
  border-color: transparent;
  background: transparent;
  box-shadow: none;
}

.op-list {
  flex: 1 1 auto;
  min-height: 0;
  max-height: calc(var(--max-visible, 8) * 34px);
  overflow-y: auto;
  padding: 5px;
  margin: 0;
  list-style: none;
}

.op-group {
  padding: 6px 8px 3px;
  color: var(--text-soft);
  font-size: var(--fs-2xs);
  font-weight: 650;
}

.op-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 8px;
  border-radius: var(--r-sm);
  cursor: pointer;
}

.op-option.is-active {
  background: var(--accent-wash);
}

.op-option.is-disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.op-option-main {
  display: grid;
  gap: 1px;
  min-width: 0;
  flex: 1 1 auto;
}

.op-option-label {
  color: var(--text);
  font-size: var(--fs-xs);
  font-weight: 600;
}

.op-option-hint {
  color: var(--text-muted);
  font-size: var(--fs-2xs);
}

.op-check {
  width: 16px;
  height: 16px;
  flex: 0 0 auto;
  color: var(--accent);
}

.op-empty {
  padding: 8px;
  color: var(--text-soft);
  font-size: var(--fs-xs);
  text-align: center;
}

/* 弹出动画：淡入 + 轻微上移（向上弹出时取反）。 */
.op-pop-enter-active,
.op-pop-leave-active {
  transition:
    opacity var(--dur) var(--ease-out),
    transform var(--dur) var(--ease-out);
}

.op-pop-enter-from,
.op-pop-leave-to {
  opacity: 0;
  transform: translateY(4px) scale(0.98);
}

@media (prefers-reduced-motion: reduce) {
  .op-pop-enter-active,
  .op-pop-leave-active {
    transition: none;
  }
}
</style>
