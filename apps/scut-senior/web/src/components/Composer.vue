<script setup lang="ts">
import { computed } from "vue";
import { WORKFLOW_TYPES } from "../contracts";
import { courseAvailabilitySummary } from "../courseAvailability";
import { modelKey } from "../modelSelection";
import { availabilityLabel, billingLabel, workflowCopy } from "../appConfig";
import WorkflowDrawer from "./WorkflowDrawer.vue";
import OptionPicker, { type OptionItem } from "./OptionPicker.vue";
import { useAppStore } from "../composables/useAppStore";

const store = useAppStore();

// 课程：可搜索、按可用性分组、带状态点，避免原生 select 的 55 行超长又超宽。
const courseOptions = computed<OptionItem[]>(() => {
  const options: OptionItem[] = store.courses.map((course) => {
    const available = course.retrieval_available && course.plugin_loaded;
    return {
      value: course.course_id,
      label: course.display_name,
      hint: courseAvailabilitySummary(course),
      disabled: !course.selectable,
      dot: available ? "ok" : course.retrieval_availability === "fixture" ? "warn" : "",
      group: course.selectable ? "可选用" : "暂不可用",
    };
  });
  // 暂不可用统一沉底：可选用在前、暂不可用在后；稳定排序保证组内保持 API 顺序。
  return options.sort((a, b) => (a.group === b.group ? 0 : a.group === "可选用" ? -1 : 1));
});

const courseDisabled = computed(
  () => store.isRunning || !store.courses.length,
);
const coursePlaceholder = computed(() => {
  if (store.isLoadingCourses) return "正在读取课程";
  if (!store.courses.length) return "暂无课程";
  return store.hasSelectableCourse ? "选课程" : "暂无可用课程";
});

// 模型：同样可搜索 + 分组 + 状态点；目录加载失败 / 进行中时禁用。
const modelOptions = computed<OptionItem[]>(() =>
  store.modelsForSelection.map((model) => ({
    value: modelKey(model),
    label: `${model.company} · ${model.display_name}${model.is_preview ? "（Preview）" : ""}`,
    hint: `${billingLabel(model)} · ${availabilityLabel(model)}`,
    disabled: !model.user_selectable,
    dot: model.user_selectable ? "ok" : "",
    group: model.user_selectable ? "可选" : "暂不可选",
  })),
);

const modelDisabled = computed(
  () => store.isRunning || store.isLoadingModels || !store.modelCatalogLoadSucceeded,
);
const modelPlaceholder = computed(() => {
  if (store.isLoadingModels) return "正在读取模型目录";
  if (!store.modelCatalogLoadSucceeded) return "模型待选择";
  return "请选择模型";
});

// Workflow：固定五种，无需搜索。
const workflowOptions = computed<OptionItem[]>(() =>
  WORKFLOW_TYPES.map((type) => ({
    value: type,
    label: workflowCopy[type].label,
    hint: workflowCopy[type].description,
    dot: "",
  })),
);
</script>

<template>
  <div class="composer">
    <div class="composer-inner">
      <div v-if="store.errorMessage || store.noticeMessage || store.modelCatalogMessage" class="composer-msgs">
        <p v-if="store.errorMessage" class="note note-bad" role="alert">{{ store.errorMessage }}</p>
        <p v-if="store.noticeMessage" class="note note-ok" role="status">{{ store.noticeMessage }}</p>
        <p v-if="store.modelCatalogMessage" class="note note-warn" role="alert">
          {{ store.modelCatalogMessage }}
        </p>
      </div>

      <!-- 配置条：课程、模型、Workflow 收在输入框上沿。 -->
      <div class="composer-bar">
        <OptionPicker
          v-model="store.selectedCourseId"
          :options="courseOptions"
          :disabled="courseDisabled"
          :placeholder="coursePlaceholder"
          searchable
          placement="up"
          aria-label="课程"
        />

        <OptionPicker
          v-model="store.selectedModelKey"
          :options="modelOptions"
          :disabled="modelDisabled"
          :placeholder="modelPlaceholder"
          searchable
          placement="up"
          aria-label="模型"
        />

        <span class="composer-bar-sep" aria-hidden="true"></span>

        <OptionPicker
          v-model="store.workflowType"
          :options="workflowOptions"
          :disabled="store.isRunning"
          placeholder="选择 Workflow"
          :searchable="false"
          placement="up"
          aria-label="Workflow"
        />

        <button
          type="button"
          class="btn btn-quiet"
          :aria-expanded="store.drawerOpen ? 'true' : 'false'"
          aria-controls="composer-drawer"
          @click="store.drawerOpen = !store.drawerOpen"
        >
          {{ store.drawerOpen ? "收起选项" : store.workflowHasExtraFields ? "更多选项与字段" : "更多选项" }}
        </button>
      </div>

      <!-- 抽屉：Workflow 专属字段 + 输出偏好，默认收起以保住记录区高度。 -->
      <Transition name="drawer-pop">
        <WorkflowDrawer v-if="store.drawerOpen" />
      </Transition>

      <div class="composer-box">
        <label class="visually-hidden" for="user-input">{{ store.activeWorkflow.inputLabel }}</label>
        <textarea
          id="user-input"
          v-model="store.userInput"
          rows="3"
          :placeholder="store.activeWorkflow.placeholder"
          :disabled="store.isRunning"
          @keydown="store.onComposerKeydown"
        ></textarea>
        <div class="composer-foot">
          <span class="composer-foot-hint">
            Enter 运行，Shift + Enter 换行
          </span>
          <div class="composer-foot-acts">
            <button
              v-if="store.isRunning && store.canCancelWorkflow"
              type="button"
              class="btn btn-danger"
              @click="store.cancelWorkflow"
            >
              取消运行
            </button>
            <button
              v-else
              type="button"
              class="btn"
              :disabled="!store.conversationId || store.isReloading || store.isRunning"
              @click="store.reloadConversation"
            >
              {{ store.isReloading ? "正在读取" : "重新读取" }}
            </button>
            <button
              type="button"
              class="btn btn-primary"
              :disabled="!store.canSubmitWorkflow"
              @click="store.submitWorkflow"
            >
              {{ store.isRunning ? "正在运行" : store.selectedModelIsMock ? "运行 Mock" : "运行" }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.composer {
  border-top: 1px solid var(--line);
  background: var(--panel);
}

.composer-inner {
  display: grid;
  gap: 8px;
  width: 100%;
  margin: 0 auto;
  padding: 10px 16px 12px;
}

.composer-msgs {
  display: grid;
  gap: 5px;
}

/* 抽屉展开：高度 + 淡入。高度过渡需测量，这里退化为不透明度 + 位移。 */
.drawer-pop-enter-active,
.drawer-pop-leave-active {
  transition:
    opacity var(--dur) var(--ease-out),
    transform var(--dur) var(--ease-out);
}

.drawer-pop-enter-from,
.drawer-pop-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (prefers-reduced-motion: reduce) {
  .drawer-pop-enter-active,
  .drawer-pop-leave-active {
    transition: none;
  }
}

/* 配置条：一行紧凑控件，取代原先的整块表单。 */
.composer-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 5px;
}

/* OptionPicker 在配置条里的收窄：只显示当前值，绝不撑宽。 */
.composer-bar .op {
  flex: 0 1 auto;
  min-width: 0;
}

.composer-bar .op-trigger {
  max-width: 200px;
  font-size: var(--fs-2xs);
}

.composer-bar-sep {
  width: 1px;
  height: 16px;
  background: var(--line);
}

.composer-box {
  display: grid;
  border: 1px solid var(--line-strong);
  border-radius: var(--r-md);
  background: var(--raised);
}

.composer-box:focus-within {
  border-color: var(--focus);
}

.composer-box textarea {
  min-height: 62px;
  max-height: 210px;
  padding: 9px 11px 5px;
  border: 0;
  border-radius: var(--r-md) var(--r-md) 0 0;
  background: transparent;
  font-size: var(--fs-md);
}

.composer-box textarea:focus {
  outline: none;
}

.composer-foot {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 5px 7px 6px 11px;
}

.composer-foot-hint {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-soft);
  font-size: var(--fs-2xs);
}

.composer-foot-acts {
  display: flex;
  gap: 5px;
  margin-left: auto;
}

@media (max-width: 719px) {
  .composer-inner {
    padding-inline: 11px;
  }

  .composer-bar .op {
    flex: 1 1 120px;
  }

  .composer-bar .op-trigger {
    max-width: none;
  }

  .composer-bar-sep {
    display: none;
  }
}

/* 窄窗口：输入条控件压缩。 */
@media (max-width: 899px) {
  .composer-bar .op-trigger {
    max-width: 160px;
  }
}

/* 更窄窗口：输入条更紧凑。 */
@media (max-width: 639px) {
  .composer-bar .op-trigger {
    max-width: 132px;
  }
}

/* 低矮窗口：composer 不被挤没。 */
@media (max-height: 640px) {
  .composer-inner {
    padding-block: 6px;
  }

  /* 输入框上限同步压低，保证发送按钮行始终留在可视范围内。 */
  .composer-box textarea {
    min-height: 48px;
    max-height: 140px;
  }
}
</style>
