<script setup lang="ts">
import { WORKFLOW_TYPES } from "../contracts";
import { courseOptionLabel } from "../courseAvailability";
import { modelKey } from "../modelSelection";
import { modelOptionLabel, workflowCopy } from "../appConfig";
import WorkflowDrawer from "./WorkflowDrawer.vue";
import { useAppStore } from "../composables/useAppStore";

const store = useAppStore();
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
        <label class="visually-hidden" for="course">课程</label>
        <select id="course" v-model="store.selectedCourseId" :disabled="store.isRunning || !store.courses.length">
          <option v-if="!store.courses.length" value="">暂无课程</option>
          <option v-else-if="!store.hasSelectableCourse" value="" disabled>暂无可用课程</option>
          <option
            v-for="course in store.courses"
            :key="course.course_id"
            :value="course.course_id"
            :disabled="!course.selectable"
          >
            {{ courseOptionLabel(course) }}
          </option>
        </select>

        <label class="visually-hidden" for="model">模型</label>
        <select
          id="model"
          v-model="store.selectedModelKey"
          :disabled="store.isRunning || store.isLoadingModels || !store.modelCatalogLoadSucceeded"
        >
          <option v-if="store.isLoadingModels" :value="store.selectedModelKey">正在读取模型目录</option>
          <option v-else-if="!store.modelCatalogLoadSucceeded" value="">模型目录不可用</option>
          <template v-else>
            <option value="" disabled>请选择模型</option>
            <option
              v-for="model in store.modelsForSelection"
              :key="modelKey(model)"
              :value="modelKey(model)"
              :disabled="!model.user_selectable"
            >
              {{ modelOptionLabel(model) }}
            </option>
          </template>
        </select>

        <span class="composer-bar-sep" aria-hidden="true"></span>

        <label class="visually-hidden" for="workflow-select">Workflow</label>
        <select id="workflow-select" v-model="store.workflowType" :disabled="store.isRunning">
          <option v-for="type in WORKFLOW_TYPES" :key="type" :value="type">
            {{ workflowCopy[type].label }}
          </option>
        </select>

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
      <WorkflowDrawer v-if="store.drawerOpen" />

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

/* 配置条：一行紧凑控件，取代原先的整块表单。 */
.composer-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 5px;
}

.composer-bar select {
  height: 26px;
  width: auto;
  max-width: 190px;
  padding: 0 6px;
  border-color: var(--line);
  background: var(--sunken);
  font-size: var(--fs-2xs);
}

.composer-bar select:focus {
  border-color: var(--focus);
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

  .composer-bar select {
    max-width: 100%;
    flex: 1 1 120px;
  }

  .composer-bar-sep {
    display: none;
  }
}

/* 窄窗口：输入条控件压缩。 */
@media (max-width: 899px) {
  .composer-bar select {
    max-width: 160px;
  }
}

/* 更窄窗口：输入条更紧凑。 */
@media (max-width: 639px) {
  .composer-bar select {
    max-width: 132px;
    flex: 1 1 96px;
  }
}

/* 低矮窗口：composer 不被挤没。 */
@media (max-height: 640px) {
  .composer-inner {
    padding-block: 6px;
  }
}
</style>
