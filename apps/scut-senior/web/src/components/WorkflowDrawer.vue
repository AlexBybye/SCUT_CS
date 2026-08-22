<script setup lang="ts">
import { ANSWER_MODES, HELP_LEVELS, TONES } from "../contracts";
import {
  answerModeLabels,
  availabilityLabel,
  billingLabel,
  helpLevelLabels,
  toneLabels,
} from "../appConfig";
import { useAppStore } from "../composables/useAppStore";
import MaterialContributionPanel from "./MaterialContributionPanel.vue";

const store = useAppStore();
</script>

<template>
  <div id="composer-drawer" class="drawer">
    <section
      v-if="store.workflowType === 'exam_review'"
      class="drawer-grid"
      aria-label="备考复习专属字段"
    >
      <p class="drawer-hint drawer-span">
        填了大纲：按“用户大纲 &gt; 课程资料 &gt; 历年题”组织；不填大纲：按“历年题
        &gt; 课程资料”组织，并明确声明不是官方范围、不构成考试重点预测。
      </p>
      <div class="field drawer-span">
        <label for="syllabus">考试大纲（可选）</label>
        <textarea
          id="syllabus"
          v-model="store.syllabus"
          rows="2"
          placeholder="粘贴大纲或范围说明。"
        ></textarea>
      </div>
      <div class="field">
        <label for="exam-date">考试日期（可选）</label>
        <input id="exam-date" v-model="store.examDate" type="date" />
      </div>
      <div class="field">
        <label for="available-hours">可投入小时（可选）</label>
        <input
          id="available-hours"
          v-model.number="store.availableHours"
          type="number"
          min="0"
          step="0.5"
        />
      </div>
      <div class="field">
        <label for="goals">目标</label>
        <input id="goals" v-model="store.goalsText" type="text" placeholder="逗号或换行分隔" />
      </div>
      <div class="field">
        <label for="weak-topics">薄弱知识点</label>
        <input
          id="weak-topics"
          v-model="store.weakTopicsText"
          type="text"
          placeholder="逗号或换行分隔"
        />
      </div>
    </section>

    <section
      v-if="store.workflowType === 'problem_tutor'"
      class="drawer-grid"
      aria-label="题目辅导专属字段"
    >
      <div class="field drawer-span">
        <label for="user-answer">我的作答（可选）</label>
        <textarea id="user-answer" v-model="store.userAnswer" rows="2"></textarea>
      </div>
      <div class="field">
        <label for="help-level">帮助层级</label>
        <select id="help-level" v-model="store.helpLevel">
          <option v-for="level in HELP_LEVELS" :key="level" :value="level">
            {{ helpLevelLabels[level] }}
          </option>
        </select>
      </div>
      <div class="field">
        <label for="problem-source">题目来源（可选）</label>
        <input
          id="problem-source"
          v-model="store.problemSource"
          type="text"
          placeholder="例如：2023 期末 A 卷"
        />
      </div>
    </section>

    <section
      v-if="store.workflowType === 'mistake_review'"
      class="drawer-grid"
      aria-label="错题复盘专属字段"
    >
      <div class="field drawer-span">
        <label for="original-answer">原答案</label>
        <textarea id="original-answer" v-model="store.originalAnswer" rows="2" required></textarea>
      </div>
      <div class="field">
        <label for="reference-answer">参考答案（可选）</label>
        <textarea id="reference-answer" v-model="store.referenceAnswer" rows="2"></textarea>
      </div>
      <div class="field">
        <label for="review-focus">复盘重点（可选）</label>
        <textarea id="review-focus" v-model="store.reviewFocus" rows="2"></textarea>
      </div>
    </section>

    <section
      v-if="store.workflowType === 'temporary_material_reading'"
      class="drawer-grid"
      aria-label="临时材料精读专属字段"
    >
      <div class="field">
        <label for="material-title">材料标题（可选）</label>
        <input
          id="material-title"
          v-model="store.materialTitle"
          type="text"
          maxlength="200"
          placeholder="例如：特征值与特征向量复习提纲"
        />
      </div>
      <div class="field">
        <label for="reading-goal">精读目标（可选）</label>
        <input
          id="reading-goal"
          v-model="store.readingGoal"
          type="text"
          placeholder="例如：提取考试范围并指出与课程资料的冲突"
        />
      </div>
      <MaterialContributionPanel />
    </section>

    <div class="drawer-grid">
      <div class="field">
        <label for="answer-mode">回答方式</label>
        <select id="answer-mode" v-model="store.answerMode">
          <option v-for="mode in ANSWER_MODES" :key="mode" :value="mode">
            {{ answerModeLabels[mode] }}
          </option>
        </select>
      </div>
      <div class="field">
        <label for="tone">表达风格</label>
        <select id="tone" v-model="store.tone">
          <option v-for="item in TONES" :key="item" :value="item">
            {{ toneLabels[item] }}
          </option>
        </select>
      </div>
      <fieldset class="field drawer-span">
        <legend>知识范围</legend>
        <div class="seg">
          <label class="seg-item">
            <input v-model="store.knowledgeScope" type="radio" value="course_first" />
            <span>资料优先，允许标记的通用补充</span>
          </label>
          <label class="seg-item">
            <input v-model="store.knowledgeScope" type="radio" value="course_only" />
            <span>仅课程资料，证据不足即停</span>
          </label>
        </div>
      </fieldset>
      <label class="check drawer-span">
        <input
          v-model="store.includeBilibiliResources"
          type="checkbox"
          :disabled="store.knowledgeScope === 'course_only'"
        />
        <span>
          <strong>返回 B站延伸学习</strong>
          <small>
            模型给出聚焦词后只返回匿名搜索链接，不返回具体视频直链。仅课程资料模式强制关闭。
          </small>
        </span>
      </label>
    </div>

    <div v-if="store.selectedModel" class="field">
      <span class="drawer-sub">当前模型</span>
      <p class="field-hint">
        {{ store.selectedModel.company }} · {{ store.selectedModel.display_name }}
        {{ store.selectedModel.is_preview ? "（Preview）" : "" }} ·
        {{ billingLabel(store.selectedModel) }} · 状态 {{ availabilityLabel(store.selectedModel) }}
        <template v-if="store.selectedModel.last_checked_at">
          · 健康检查
          {{ new Date(store.selectedModel.last_checked_at).toLocaleString("zh-CN") }}
        </template>
      </p>
      <p class="field-hint">{{ store.modelCatalog.quota_notice }}</p>
    </div>
  </div>
</template>

<style>
/* 抽屉：Workflow 专属字段与输出偏好，默认收起。
   高度封顶并内部滚动：内容再长也只压缩自己，
   不把下方输入框的发送区挤出可视范围。 */
.drawer {
  display: grid;
  align-content: start;
  gap: 12px;
  padding: 11px;
  border: 1px solid var(--line);
  border-radius: var(--r-md);
  background: var(--sunken);
  max-height: min(46vh, 480px);
  overflow-y: auto;
  overscroll-behavior: contain;
}

/* 低矮窗口：进一步压低抽屉上限，保住输入框可用高度。 */
@media (max-height: 560px) {
  .drawer {
    max-height: 34vh;
  }
}

.drawer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.drawer-span {
  grid-column: 1 / -1;
}

.drawer-sub {
  color: var(--text-muted);
  font-size: var(--fs-2xs);
  font-weight: 650;
  letter-spacing: 0.02em;
}

.drawer-hint {
  color: var(--text-muted);
  font-size: var(--fs-2xs);
  line-height: 1.55;
}

.check {
  display: flex;
  align-items: flex-start;
  gap: 7px;
}

.check input {
  flex: 0 0 auto;
  width: 14px;
  height: 14px;
  margin: 2px 0 0;
}

.check > span {
  display: grid;
  gap: 1px;
}

.check strong {
  font-size: var(--fs-xs);
  font-weight: 650;
}

.check small {
  color: var(--text-muted);
  font-size: var(--fs-2xs);
  line-height: 1.5;
}
</style>
