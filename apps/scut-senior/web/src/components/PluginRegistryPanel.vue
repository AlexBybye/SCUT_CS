<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { getPluginRegistry, loadCoursePlugin, unloadCoursePlugin } from "../api";
import type { CoursePluginEntry, PluginRegistry } from "../contracts";

const props = defineProps<{
  canManagePlugins: boolean;
}>();

const emit = defineEmits<{
  changed: [];
}>();

const registry = ref<PluginRegistry | null>(null);
const loading = ref(true);
const errorMessage = ref("");
const busyCourseId = ref("");

// 分组开合：课程插件默认收起，避免进入个人中心时一次渲染全部课程插件。
const coursesOpen = ref(false);
const presetsOpen = ref(false);
const toolsOpen = ref(false);
const courseQuery = ref("");

const stateLabel: Record<string, string> = {
  active: "可用",
  fixture_only: "仅 Fixture",
  registered: "已登记",
};

const pluginStateChip: Record<string, string> = {
  active: "chip-ok",
  fixture_only: "chip-warn",
  registered: "",
};

const PLUGIN_TELEMETRY_KEY = "scut-senior.plugin-management-events";

function recordPluginTelemetry(course: CoursePluginEntry, loaded: boolean): void {
  const event = {
    event: "course_plugin_state_changed",
    course_id: course.course_id,
    loaded,
    recorded_at: new Date().toISOString(),
  };
  try {
    const previous = JSON.parse(localStorage.getItem(PLUGIN_TELEMETRY_KEY) || "[]");
    const events = Array.isArray(previous) ? previous.slice(-99) : [];
    events.push(event);
    localStorage.setItem(PLUGIN_TELEMETRY_KEY, JSON.stringify(events));
  } catch {
    // 埋点失败不影响插件状态操作。
  }
}

onMounted(async () => {
  try {
    registry.value = await getPluginRegistry();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "插件注册表读取失败。";
  } finally {
    loading.value = false;
  }
});

function presetTools(presetId: string): string[] {
  const preset = registry.value?.agent_presets.find(
    (entry) => entry.preset_id === presetId,
  );
  return preset?.allowed_tools ?? [];
}

// 课程插件：已装载的浮到最前，其余按名称排；再按搜索词过滤。
const visibleCourses = computed<CoursePluginEntry[]>(() => {
  const list = registry.value?.courses ?? [];
  const q = courseQuery.value.trim().toLowerCase();
  return list
    .filter((course) => {
      if (!q) return true;
      return (
        course.display_name.toLowerCase().includes(q) ||
        course.course_id.toLowerCase().includes(q)
      );
    })
    .sort((a, b) => {
      if (a.loaded !== b.loaded) return a.loaded ? -1 : 1;
      return a.display_name.localeCompare(b.display_name, "zh-Hans");
    });
});

const loadedCourseCount = computed(
  () => registry.value?.courses.filter((course) => course.loaded).length ?? 0,
);

// 「全部展开 / 全部收起」的联动状态与开关。
const allGroupsOpen = computed(
  () => coursesOpen.value && presetsOpen.value && toolsOpen.value,
);

function toggleAllGroups(): void {
  const next = !allGroupsOpen.value;
  coursesOpen.value = next;
  presetsOpen.value = next;
  toolsOpen.value = next;
}

async function togglePlugin(course: CoursePluginEntry): Promise<void> {
  if (!props.canManagePlugins || busyCourseId.value) return;
  busyCourseId.value = course.course_id;
  errorMessage.value = "";
  try {
    const nextLoaded = !course.loaded;
    await (course.loaded
      ? unloadCoursePlugin(course.course_id)
      : loadCoursePlugin(course.course_id));
    if (registry.value) {
      registry.value = {
        ...registry.value,
        courses: registry.value.courses.map((item) =>
          item.course_id === course.course_id
            ? {
                ...item,
                loaded: nextLoaded,
                enabled_workflows: nextLoaded ? item.enabled_workflows : [],
              }
            : item,
        ),
      };
    }
    recordPluginTelemetry(course, nextLoaded);
    emit("changed");
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "装载/卸载失败。";
  } finally {
    busyCourseId.value = "";
  }
}
</script>

<template>
  <div class="plugins">
    <p v-if="loading" class="note note-plain" role="status">正在读取插件注册表。</p>
    <p v-else-if="errorMessage" class="note note-bad" role="alert">{{ errorMessage }}</p>

    <template v-else-if="registry">
      <p class="registry-meta">
        <span class="chip chip-mono">v{{ registry.registry_version }}</span>
        <span>
          检索：{{ registry.retrieval_mode === "local_corpus" ? "本地语料" : "Fixture" }}
        </span>
        <button type="button" class="btn btn-quiet registry-toggle-all" @click="toggleAllGroups">
          {{ allGroupsOpen ? "全部收起" : "全部展开" }}
        </button>
      </p>

      <!-- 课程插件：默认收起；用户展开后再渲染课程列表。 -->
      <section class="plugin-group" aria-labelledby="courses-heading">
        <button
          type="button"
          class="group-toggle"
          :aria-expanded="coursesOpen ? 'true' : 'false'"
          aria-controls="courses-body"
          @click="coursesOpen = !coursesOpen"
        >
          <span class="group-toggle-title">
            课程插件
            <span class="chip">{{ registry.courses.length }} 门</span>
            <span v-if="loadedCourseCount" class="chip chip-ok">已装载 {{ loadedCourseCount }}</span>
          </span>
          <svg
            class="group-caret"
            :class="{ 'is-open': coursesOpen }"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="m6 9 6 6 6-6" />
          </svg>
        </button>

        <div v-if="coursesOpen" id="courses-body" class="group-body">
          <div class="group-filter">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="11" cy="11" r="7" />
              <path d="m20 20-3.5-3.5" />
            </svg>
            <input
              v-model="courseQuery"
              type="text"
              class="group-filter-input"
              placeholder="搜索课程名或别名…"
              aria-label="搜索课程插件"
            />
          </div>

          <div v-if="visibleCourses.length" class="plugin-sheet">
            <article
              v-for="course in visibleCourses"
              :key="course.course_id"
              class="plugin-row"
            >
              <div class="plugin-row-top">
                <strong>{{ course.display_name }}</strong>
                <span
                  class="chip"
                  :class="course.loaded ? pluginStateChip[course.state] : ''"
                >
                  {{ course.loaded ? stateLabel[course.state] : "已卸载" }}
                </span>
              </div>
              <div class="plugin-row-meta">
                <code>{{ course.course_id }}</code>
                <span>
                  {{
                    course.loaded
                      ? course.enabled_workflows.length
                        ? `支持 ${course.enabled_workflows.length} 个 Workflow`
                        : "未启用 Workflow"
                      : "插件未装载"
                  }}
                </span>
              </div>
              <div v-if="canManagePlugins" class="plugin-row-acts">
                <button
                  type="button"
                  class="btn btn-quiet"
                  :disabled="busyCourseId !== ''"
                  @click="togglePlugin(course)"
                >
                  {{ busyCourseId === course.course_id ? "处理中" : course.loaded ? "卸载" : "装载" }}
                </button>
              </div>
            </article>
          </div>
          <p v-else class="inspector-note">没有匹配「{{ courseQuery }}」的课程。</p>

          <p v-if="!canManagePlugins" class="inspector-note">
            装载与卸载需要真实 GitHub 登录；当前只读展示。
          </p>
        </div>
      </section>

      <!-- Agent Preset：信息性列表，默认收起。 -->
      <section class="plugin-group" aria-labelledby="presets-heading">
        <button
          type="button"
          class="group-toggle"
          :aria-expanded="presetsOpen ? 'true' : 'false'"
          aria-controls="presets-body"
          @click="presetsOpen = !presetsOpen"
        >
          <span class="group-toggle-title">
            Agent Preset
            <span class="chip">{{ registry.agent_presets.length }} 个</span>
          </span>
          <svg
            class="group-caret"
            :class="{ 'is-open': presetsOpen }"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="m6 9 6 6 6-6" />
          </svg>
        </button>

        <div v-if="presetsOpen" id="presets-body" class="group-body">
          <p class="inspector-note">
            每个 Workflow 由且仅由一个预设描述能力与工具边界；预设不含提示词。
          </p>
          <article v-for="preset in registry.agent_presets" :key="preset.preset_id" class="plugin-row">
            <div class="plugin-row-top">
              <strong>{{ preset.display_name }}</strong>
              <span class="chip chip-mono">v{{ preset.preset_version }}</span>
            </div>
            <div class="plugin-row-meta">
              <code>{{ preset.workflow_type }}</code>
              <span>聚焦：{{ preset.focus_strategy }}</span>
              <span>工具：{{ presetTools(preset.preset_id).join("、") || "无" }}</span>
              <span>
                模态：{{ preset.required_input_modalities.join("/") }} ·
                结构化输出：{{ preset.requires_structured_outputs ? "必需" : "否" }}
              </span>
            </div>
          </article>
        </div>
      </section>

      <!-- 受控工具：信息性列表，默认收起。 -->
      <section class="plugin-group" aria-labelledby="tools-heading">
        <button
          type="button"
          class="group-toggle"
          :aria-expanded="toolsOpen ? 'true' : 'false'"
          aria-controls="tools-body"
          @click="toolsOpen = !toolsOpen"
        >
          <span class="group-toggle-title">
            受控工具
            <span class="chip">{{ registry.controlled_tools.length }} 个</span>
          </span>
          <svg
            class="group-caret"
            :class="{ 'is-open': toolsOpen }"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="m6 9 6 6 6-6" />
          </svg>
        </button>

        <div v-if="toolsOpen" id="tools-body" class="group-body">
          <p class="inspector-note">
            全部由服务端编排，模型不可直接调用（model_callable=false）。
          </p>
          <article v-for="tool in registry.controlled_tools" :key="tool.tool_id" class="plugin-row">
            <div class="plugin-row-top">
              <strong>{{ tool.display_name }}</strong>
            </div>
            <div class="plugin-row-meta">
              <code>{{ tool.tool_id }}</code>
              <span>{{ tool.description }}</span>
            </div>
          </article>
        </div>
      </section>
    </template>
  </div>
</template>

<style>
.plugins {
  display: grid;
  gap: 8px;
}

.registry-meta {
  display: flex;
  align-items: center;
  gap: 7px;
  color: var(--text-muted);
  font-size: var(--fs-2xs);
}

.registry-toggle-all {
  margin-left: auto;
  height: 24px;
  flex: 0 0 auto;
}

.plugin-group {
  display: grid;
  gap: 4px;
  border: 1px solid var(--line);
  border-radius: var(--r-md);
  background: var(--raised);
}

/* 组头：整行可点的开合按钮。
   首行 sticky：浏览某个展开组的内容时，组头钉在滚动条上方不随内容滚走。
   （.plugin-group 不再 overflow:hidden，否则 sticky 会失效。） */
.group-toggle {
  position: sticky;
  top: 0;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  width: 100%;
  padding: 9px 11px;
  border: 0;
  border-radius: var(--r-md);
  background: var(--raised);
  color: var(--text);
  cursor: pointer;
  transition: background var(--dur-fast) ease;
}

/* 展开时：头部只圆上角，内容区圆下角（由 .group-body 负责）。 */
.plugin-group:has(.group-body) .group-toggle {
  border-radius: var(--r-md) var(--r-md) 0 0;
}

.group-toggle:hover {
  background: var(--sunken);
}

.group-toggle:focus-visible {
  outline: 3px solid color-mix(in srgb, var(--focus) 34%, transparent);
  outline-offset: -2px;
}

.group-toggle-title {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-width: 0;
  font-size: var(--fs-xs);
  font-weight: 700;
}

.group-caret {
  width: 16px;
  height: 16px;
  flex: 0 0 auto;
  color: var(--text-soft);
  transition: transform var(--dur) var(--ease-out);
}

.group-caret.is-open {
  transform: rotate(180deg);
}

/* 组内容：课程用内滚限高，其余随内容自然展开；底部圆角补上（组容器不再裁剪）。 */
.group-body {
  display: grid;
  gap: 6px;
  padding: 6px 11px 11px;
  border-top: 1px solid var(--line);
  border-radius: 0 0 var(--r-md) var(--r-md);
}

.group-filter {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 0 9px;
  height: 32px;
  border: 1px solid var(--line);
  border-radius: var(--r-sm);
  background: var(--sunken);
  transition: border-color var(--dur-fast) ease, box-shadow var(--dur-fast) ease;
}

.group-filter:focus-within {
  border-color: var(--focus);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--focus) 18%, transparent);
}

.group-filter svg {
  width: 15px;
  height: 15px;
  flex: 0 0 auto;
  color: var(--text-soft);
}

/* 搜索输入：必须压过全局 input[type="text"]（min-height 44px + 边框 + 底色），
   否则会在 .group-filter 外框内再套一层原生表单盒子，出现「两层覆盖」。 */
.group-filter input.group-filter-input {
  min-height: 28px;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--text);
  font-size: var(--fs-xs);
}

.group-filter input.group-filter-input::placeholder {
  color: var(--text-soft);
}

.group-filter input.group-filter-input:focus {
  outline: none;
  border-color: transparent;
  background: transparent;
  box-shadow: none;
}

/* 课程清单：限高内滚，绝不再把面板撑成无限长。 */
.plugin-sheet {
  display: grid;
  gap: 5px;
  max-height: 300px;
  overflow-y: auto;
}

.plugin-row {
  display: grid;
  gap: 3px;
  padding: 7px 9px;
  border: 1px solid var(--line);
  border-radius: var(--r-sm);
  background: var(--panel);
}

.plugin-row-top {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 5px 7px;
  min-width: 0;
}

.plugin-row-top strong {
  font-size: var(--fs-xs);
  font-weight: 650;
}

.plugin-row-top code {
  color: var(--text-muted);
  font-size: var(--fs-2xs);
  overflow-wrap: anywhere;
}

.plugin-row-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 3px 10px;
  color: var(--text-muted);
  font-size: var(--fs-2xs);
  line-height: 1.55;
}

.plugin-row-acts {
  display: flex;
  justify-content: flex-end;
}

.inspector-head {
  display: flex;
  align-items: baseline;
  gap: 7px;
}

.inspector-head h3 {
  font-size: var(--fs-xs);
  font-weight: 650;
}

.inspector-head > span:last-child {
  margin-left: auto;
}

.inspector-note {
  color: var(--text-muted);
  font-size: var(--fs-2xs);
  line-height: 1.6;
}
</style>
