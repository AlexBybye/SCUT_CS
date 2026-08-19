<script setup lang="ts">
import { onMounted, ref } from "vue";
import { getPluginRegistry } from "../api";
import type { PluginRegistry } from "../contracts";

const registry = ref<PluginRegistry | null>(null);
const loading = ref(true);
const errorMessage = ref("");

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
</script>

<template>
  <section class="plugin-panel" aria-labelledby="plugin-panel-heading">
    <header class="plugin-panel-header">
      <div>
        <h2 id="plugin-panel-heading">内部插件管理（只读）</h2>
        <p v-if="registry">
          注册表版本 {{ registry.registry_version }} · 检索模式
          {{ registry.retrieval_mode === "local_corpus" ? "本地语料" : "Fixture" }}
        </p>
      </div>
      <span v-if="registry" class="plugin-count-badge">
        {{ registry.agent_presets.length }} 预设 · {{ registry.controlled_tools.length }} 工具 ·
        {{ registry.maintainer_skills.length }} 技能 · {{ registry.courses.length }} 课程
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
            <h3 id="courses-heading">课程插件状态</h3>
            <span>{{ registry.courses.length }}</span>
          </div>
          <p class="plugin-card-note">
            状态由当前检索适配器实际可用性派生；未激活课程不声明可用 Workflow。
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
                  :class="`plugin-state-${course.state}`"
                >
                  {{ stateLabel[course.state] }}
                </span>
                <span>
                  {{
                    course.enabled_workflows.length
                      ? `支持 ${course.enabled_workflows.length} 个 Workflow`
                      : "未启用 Workflow"
                  }}
                </span>
              </div>
            </article>
          </div>
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

        <section class="plugin-card" aria-labelledby="skills-heading">
          <div class="plugin-card-heading">
            <h3 id="skills-heading">维护者技能</h3>
            <span>{{ registry.maintainer_skills.length }}</span>
          </div>
          <p class="plugin-card-note">
            仅登记契约元数据；技能不能自行把资料标记为 passed 或 active。
          </p>
          <div class="plugin-rows">
            <article
              v-for="skill in registry.maintainer_skills"
              :key="skill.skill_id"
              class="plugin-row"
            >
              <div class="plugin-row-main">
                <strong>{{ skill.display_name }}</strong>
                <code>{{ skill.skill_id }}@{{ skill.version }}</code>
                <span>状态：{{ skill.status }} · 需人工审核：{{ skill.human_review_required ? "是" : "否" }}</span>
              </div>
              <p class="plugin-row-description">{{ skill.description }}</p>
            </article>
          </div>
        </section>
      </div>
    </template>
  </section>
</template>
