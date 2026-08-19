<script setup lang="ts">
import { onMounted, ref } from "vue";
import { getPluginRegistry, loadCoursePlugin, unloadCoursePlugin } from "../api";
import type { CoursePluginEntry, PluginRegistry } from "../contracts";

const props = defineProps<{
  canManagePlugins: boolean;
}>();

const registry = ref<PluginRegistry | null>(null);
const loading = ref(true);
const errorMessage = ref("");
const busyCourseId = ref("");

const stateLabel: Record<string, string> = {
  active: "可用",
  fixture_only: "仅 Fixture",
  registered: "已登记",
};

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

async function togglePlugin(course: CoursePluginEntry): Promise<void> {
  if (!props.canManagePlugins || busyCourseId.value) return;
  busyCourseId.value = course.course_id;
  errorMessage.value = "";
  try {
    await (course.loaded
      ? unloadCoursePlugin(course.course_id)
      : loadCoursePlugin(course.course_id));
    registry.value = await getPluginRegistry();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "装载/卸载失败。";
  } finally {
    busyCourseId.value = "";
  }
}
</script>

<template>
  <section class="plugin-panel" aria-labelledby="plugin-panel-heading">
    <header class="plugin-panel-header">
      <div>
        <h2 id="plugin-panel-heading">内部插件管理</h2>
        <p v-if="registry">
          注册表版本 {{ registry.registry_version }} · 检索模式
          {{ registry.retrieval_mode === "local_corpus" ? "本地语料" : "Fixture" }}
          · 课程插件可装载与卸载
        </p>
      </div>
      <span v-if="registry" class="plugin-count-badge">
        {{ registry.agent_presets.length }} 预设 · {{ registry.controlled_tools.length }} 工具 ·
        {{ registry.courses.length }} 课程
      </span>
    </header>

    <div v-if="loading" class="inline-state" role="status">正在读取插件注册表。</div>
    <div v-else-if="errorMessage" class="inline-state" role="alert">{{ errorMessage }}</div>

    <template v-else-if="registry">
      <div class="plugin-columns">
        <section class="plugin-card" aria-labelledby="presets-heading">
          <div class="plugin-card-heading">
            <h3 id="presets-heading">Agent Preset（与 Workflow 一一对应）</h3>
            <span>{{ registry.agent_presets.length }}</span>
          </div>
          <p class="plugin-card-note">
            每个 Workflow 由且仅由一个预设描述能力与工具边界；预设不含提示词。
          </p>
          <div class="plugin-rows">
            <article
              v-for="preset in registry.agent_presets"
              :key="preset.preset_id"
              class="plugin-row"
            >
              <div class="plugin-row-main">
                <strong>{{ preset.display_name }}</strong>
                <code>{{ preset.workflow_type }}</code>
                <span>v{{ preset.preset_version }} · {{ preset.focus_strategy }}</span>
              </div>
              <div class="plugin-row-meta">
                <span>工具：{{ presetTools(preset.preset_id).join("、") || "无" }}</span>
                <span>
                  模态：{{ preset.required_input_modalities.join("/") }} ·
                  结构化输出：{{ preset.requires_structured_outputs ? "必需" : "否" }}
                </span>
              </div>
            </article>
          </div>
        </section>

        <section class="plugin-card" aria-labelledby="courses-heading">
          <div class="plugin-card-heading">
            <h3 id="courses-heading">课程插件</h3>
            <span>{{ registry.courses.length }}</span>
          </div>
          <p class="plugin-card-note">
            状态由检索可用性与插件装载状态共同决定；卸载后课程不可建会话、不可运行。
          </p>
          <div class="plugin-rows">
            <article
              v-for="course in registry.courses"
              :key="course.course_id"
              class="plugin-row"
            >
              <div class="plugin-row-main">
                <strong>{{ course.display_name }}</strong>
                <code>{{ course.course_id }}</code>
              </div>
              <div class="plugin-row-meta">
                <span
                  class="plugin-state"
                  :class="course.loaded ? `plugin-state-${course.state}` : 'plugin-state-registered'"
                >
                  {{ course.loaded ? stateLabel[course.state] : "已卸载" }}
                </span>
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
              <div v-if="canManagePlugins" class="plugin-row-actions">
                <button
                  type="button"
                  class="secondary-button plugin-action-button"
                  :disabled="busyCourseId !== ''"
                  @click="togglePlugin(course)"
                >
                  {{ busyCourseId === course.course_id ? "处理中" : course.loaded ? "卸载" : "装载" }}
                </button>
              </div>
            </article>
          </div>
          <p v-if="!canManagePlugins" class="plugin-card-note">
            装载/卸载需要真实 GitHub 登录；当前只读展示。
          </p>
        </section>
      </div>

      <div class="plugin-columns">
        <section class="plugin-card" aria-labelledby="tools-heading">
          <div class="plugin-card-heading">
            <h3 id="tools-heading">受控工具</h3>
            <span>{{ registry.controlled_tools.length }}</span>
          </div>
          <p class="plugin-card-note">
            全部由服务端编排，模型不可直接调用（model_callable=false）。
          </p>
          <div class="plugin-rows">
            <article
              v-for="tool in registry.controlled_tools"
              :key="tool.tool_id"
              class="plugin-row"
            >
              <div class="plugin-row-main">
                <strong>{{ tool.display_name }}</strong>
                <code>{{ tool.tool_id }}</code>
              </div>
              <p class="plugin-row-description">{{ tool.description }}</p>
            </article>
          </div>
        </section>
      </div>
    </template>
  </section>
</template>
