<script setup lang="ts">
import { computed } from "vue";
import {
  COURSE_CATEGORY_LABEL,
  COURSE_CATEGORY_RANK,
  courseAvailabilitySummary,
} from "../courseAvailability";
import { modelKey } from "../modelSelection";
import { availabilityLabel, billingLabel, answerModeLabels, toneLabels } from "../appConfig";
import { ANSWER_MODES, TONES } from "../contracts";
import WorkflowDrawer from "./WorkflowDrawer.vue";
import OptionPicker, { type OptionItem } from "./OptionPicker.vue";
import { useAppStore } from "../composables/useAppStore";
import { parseExamReviewPlan } from "../examReviewPlan";

const store = useAppStore();

// 课程：可搜索、按统一分类分组、带状态点，避免原生 select 的 55 行超长又超宽。
// 分类与个人中心插件面板共用同一套真值（course.category），二者不再分叉。
const rankByLabel: Record<string, number> = {
  [COURSE_CATEGORY_LABEL.enabled]: COURSE_CATEGORY_RANK.enabled,
  [COURSE_CATEGORY_LABEL.not_enabled]: COURSE_CATEGORY_RANK.not_enabled,
  [COURSE_CATEGORY_LABEL.no_data]: COURSE_CATEGORY_RANK.no_data,
};
const courseOptions = computed<OptionItem[]>(() => {
  const options: OptionItem[] = store.courses.map((course) => {
    const category = course.category;
    return {
      value: course.course_id,
      label: course.display_name,
      hint: courseAvailabilitySummary(course),
      disabled: category !== "enabled",
      dot: category === "enabled" ? "ok" : category === "not_enabled" ? "warn" : "",
      group: COURSE_CATEGORY_LABEL[category],
    };
  });
  // 稳定排序：已启用 → 未启用 → 无数据；组内保持 API 顺序。
  return options.sort(
    (a, b) =>
      (rankByLabel[a.group ?? ""] ?? 9) - (rankByLabel[b.group ?? ""] ?? 9),
  );
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
const answerModeOptions = computed<OptionItem[]>(() => ANSWER_MODES.map((mode) => ({ value: mode, label: answerModeLabels[mode] })));
const toneOptions = computed<OptionItem[]>(() => TONES.map((item) => ({ value: item, label: toneLabels[item] })));
const pendingExamPlan = computed(() =>
  parseExamReviewPlan(store.pendingExamPlan?.plan ?? null),
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

      <!-- 配置条只保留运行前必须显式选择的课程和模型。 -->
      <div class="composer-bar">
        <OptionPicker
          v-if="!store.crossCourseSearchEnabled"
          v-model="store.selectedCourseId"
          :options="courseOptions"
          :disabled="courseDisabled"
          :placeholder="coursePlaceholder"
          searchable
          placement="up"
          aria-label="课程"
        />
        <OptionPicker
          v-else
          v-model="store.selectedCourseIds"
          :options="courseOptions"
          :disabled="courseDisabled"
          :placeholder="coursePlaceholder"
          :multiple="true"
          searchable
          placement="up"
          aria-label="本次检索课程（可多选）"
        />

        <OptionPicker
          v-model="store.answerMode"
          :options="answerModeOptions"
          :disabled="store.isRunning"
          :searchable="false"
          placement="up"
          aria-label="讲解形式"
        />
        <OptionPicker
          v-model="store.tone"
          :options="toneOptions"
          :disabled="store.isRunning"
          :searchable="false"
          placement="up"
          aria-label="输出风格"
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

        <span class="route-status" :class="{ 'is-manual': store.workflowRouteIsManual }">
          {{ store.workflowRouteIsManual ? "已纠正" : "自动识别" }} · {{ store.activeWorkflow.label }}
        </span>

        <button
          type="button"
          class="btn btn-quiet"
          :aria-expanded="store.drawerOpen ? 'true' : 'false'"
          aria-controls="composer-drawer"
          @click="store.drawerOpen = !store.drawerOpen"
        >
          {{ store.drawerOpen ? "收起字段" : store.workflowHasExtraFields ? "补充字段" : "查看识别" }}
        </button>
      </div>

      <!-- 抽屉：自动路由结果、纠正入口和 Workflow 专属字段。 -->
      <Transition name="drawer-pop">
        <WorkflowDrawer v-if="store.drawerOpen" />
      </Transition>

      <section v-if="pendingExamPlan" class="exam-plan-preview" aria-live="polite">
        <div class="exam-plan-preview-head">
          <strong>复习计划预览</strong>
          <span>{{ pendingExamPlan.path === "with_syllabus" ? "按大纲安排" : "按历年题安排" }}</span>
        </div>
        <p>{{ pendingExamPlan.scope_statement }}</p>
        <ul>
          <li v-for="point in pendingExamPlan.knowledge_points.slice(0, 6)" :key="point.topic">
            {{ point.topic }}
          </li>
        </ul>
        <div class="exam-plan-preview-actions">
          <button type="button" class="btn btn-primary" :disabled="store.isRunning" @click="store.submitWorkflow">
            确认并开始
          </button>
          <button type="button" class="btn btn-quiet" :disabled="store.isRunning" @click="store.rejectExamPlan">
            放弃计划
          </button>
        </div>
      </section>

      <div class="composer-box">
        <label class="visually-hidden" for="user-input">统一任务输入</label>
        <textarea
          id="user-input"
          v-model="store.userInput"
          rows="3"
          placeholder="输入课程问题、题目、错题、复习需求，或粘贴临时材料。"
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
              {{ store.isPreviewingExamPlan ? "正在生成计划" : store.pendingExamPlan ? "已生成计划" : store.isRunning ? "正在运行" : store.selectedModelIsMock ? "运行 Mock" : "运行" }}
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

.exam-plan-preview {
  border: 1px solid var(--line);
  padding: 10px 12px;
  background: var(--panel-muted, var(--panel));
}

.exam-plan-preview-head,
.exam-plan-preview-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.exam-plan-preview-head {
  justify-content: space-between;
}

.exam-plan-preview p { margin: 6px 0; }
.exam-plan-preview ul { margin: 6px 0 10px; padding-left: 20px; }

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

.composer-select {
  display: inline-flex;
  flex: 0 1 auto;
  min-width: 0;
}
.composer-select select {
  box-sizing: border-box;
  width: 132px;
  min-height: 34px;
  max-width: 200px;
  border: 1px solid var(--line);
  border-radius: var(--r-sm);
  padding: 0 28px 0 10px;
  color: var(--text);
  background: var(--sunken);
  font-size: var(--fs-2xs);
  cursor: pointer;
}
.composer-select select:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

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

.route-status {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 8px;
  border: 1px solid var(--line);
  border-radius: var(--r-xs);
  color: var(--text-soft);
  background: var(--sunken);
  font-size: var(--fs-2xs);
  white-space: nowrap;
}

.route-status.is-manual {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-wash);
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

  .composer-bar .op,
  .composer-select {
    flex: 1 1 120px;
  }

  .composer-select select {
    width: 100%;
    max-width: none;
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
