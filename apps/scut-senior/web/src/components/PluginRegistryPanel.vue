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

const pluginStateChip: Record<string, string> = {
  active: "chip-ok",
  fixture_only: "chip-warn",
  registered: "",
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
  <div class="plugins">
    <p v-if="loading" class="note note-plain" role="status">正在读取插件注册表。</p>
    <p v-else-if="errorMessage" class="note note-bad" role="alert">{{ errorMessage }}</p>

    <template v-else-if="registry">
      <p class="inspector-note">
        注册表 {{ registry.registry_version }} · 检索
        {{ registry.retrieval_mode === "local_corpus" ? "本地语料" : "Fixture" }}
      </p>

      <section class="plugin-group" aria-labelledby="courses-heading">
        <div class="inspector-head">
          <h3 id="courses-heading">课程插件</h3>
          <span class="chip">{{ registry.courses.length }}</span>
        </div>
        <p class="inspector-note">
          状态由检索可用性与装载状态共同决定；卸载后课程不可建会话、不可运行。
        </p>
        <article v-for="course in registry.courses" :key="course.course_id" class="plugin-row">
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
        <p v-if="!canManagePlugins" class="inspector-note">
          装载与卸载需要真实 GitHub 登录；当前只读展示。
        </p>
      </section>

      <section class="plugin-group" aria-labelledby="presets-heading">
        <div class="inspector-head">
          <h3 id="presets-heading">Agent Preset</h3>
          <span class="chip">{{ registry.agent_presets.length }}</span>
        </div>
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
      </section>

      <section class="plugin-group" aria-labelledby="tools-heading">
        <div class="inspector-head">
          <h3 id="tools-heading">受控工具</h3>
          <span class="chip">{{ registry.controlled_tools.length }}</span>
        </div>
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
      </section>
    </template>
  </div>
</template>
