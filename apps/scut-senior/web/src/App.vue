<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import {
  createConversation,
  getConversation,
  getCourses,
  runWorkflow,
} from "./api";
import WorkflowResult from "./components/WorkflowResult.vue";
import {
  ANSWER_MODES,
  HELP_LEVELS,
  TONES,
  WORKFLOW_TYPES,
  type AnswerMode,
  type Conversation,
  type Course,
  type HelpLevel,
  type KnowledgeScope,
  type Tone,
  type WorkflowRunRequest,
  type WorkflowRunResult,
  type WorkflowType,
} from "./contracts";
import { buildWorkflowRequest } from "./workflowRequest";

const workflowCopy: Record<
  WorkflowType,
  { label: string; description: string; inputLabel: string; placeholder: string }
> = {
  knowledge_qa: {
    label: "知识答疑",
    description: "解释课程概念、原理、差异和常见误区。",
    inputLabel: "课程问题",
    placeholder: "例如：为什么矩阵可逆等价于行列式不为 0？",
  },
  exam_review: {
    label: "备考复习",
    description: "结合大纲、目标和薄弱点整理复习请求。",
    inputLabel: "复习请求",
    placeholder: "例如：请按剩余时间整理一份线性代数复习重点。",
  },
  problem_tutor: {
    label: "题目辅导",
    description: "按指定帮助层级分析文本题目。",
    inputLabel: "题干",
    placeholder: "粘贴题目文本。",
  },
  mistake_review: {
    label: "错题复盘",
    description: "定位错误原因并给出下次检查动作。",
    inputLabel: "原题",
    placeholder: "粘贴需要复盘的题目。",
  },
  temporary_material_reading: {
    label: "临时材料精读",
    description: "读取本次会话中的临时文本或 Markdown。",
    inputLabel: "临时材料",
    placeholder: "粘贴需要精读的文本或 Markdown。",
  },
};

const answerModeLabels: Record<AnswerMode, string> = {
  concise: "简短",
  detailed: "详细",
  example: "举例",
  step_by_step: "分步骤",
};

const toneLabels: Record<Tone, string> = {
  teaching_assistant: "助教式",
  study_partner: "复习搭子",
  senior_student: "学长聊天",
};

const helpLevelLabels: Record<HelpLevel, string> = {
  concept: "只讲知识点",
  approach: "给出思路",
  step_by_step: "分步骤提示",
  full_explanation: "完整讲解",
  answer_analysis: "分析我的答案",
};

const courses = ref<Course[]>([]);
const selectedCourseId = ref("");
const workflowType = ref<WorkflowType>("knowledge_qa");
const answerMode = ref<AnswerMode>("detailed");
const tone = ref<Tone>("teaching_assistant");
const knowledgeScope = ref<KnowledgeScope>("course_first");
const includeBilibiliResources = ref(true);
const userInput = ref("");

const syllabus = ref("");
const examDate = ref("");
const availableHours = ref<number | undefined>();
const goalsText = ref("");
const weakTopicsText = ref("");
const userAnswer = ref("");
const helpLevel = ref<HelpLevel>("step_by_step");
const problemSource = ref("");
const originalAnswer = ref("");
const referenceAnswer = ref("");
const reviewFocus = ref("");
const readingGoal = ref("");

const conversationId = ref("");
const conversationSnapshot = ref<Conversation | null>(null);
const result = ref<WorkflowRunResult | null>(null);
const isLoadingCourses = ref(true);
const isRunning = ref(false);
const isReloading = ref(false);
const errorMessage = ref("");
const noticeMessage = ref("");

const selectedCourse = computed(() =>
  courses.value.find((course) => course.course_id === selectedCourseId.value),
);
const activeWorkflow = computed(() => workflowCopy[workflowType.value]);

function splitList(value: string): string[] {
  return value
    .split(/[，,\n]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function toMessage(error: unknown): string {
  return error instanceof Error ? error.message : "请求失败，请检查 Mock API 是否运行。";
}

function makeRequest(activeConversationId: string): WorkflowRunRequest {
  const common = {
    courseId: selectedCourseId.value,
    conversationId: activeConversationId,
    userInput: userInput.value,
    answerMode: answerMode.value,
    tone: tone.value,
    knowledgeScope: knowledgeScope.value,
    includeBilibiliResources: includeBilibiliResources.value,
  };

  switch (workflowType.value) {
    case "knowledge_qa":
      return buildWorkflowRequest({
        ...common,
        workflowType: "knowledge_qa",
        workflowPayload: { question: userInput.value },
      });
    case "exam_review":
      return buildWorkflowRequest({
        ...common,
        workflowType: "exam_review",
        workflowPayload: {
          syllabus: syllabus.value,
          exam_date: examDate.value,
          available_hours: availableHours.value,
          goals: splitList(goalsText.value),
          weak_topics: splitList(weakTopicsText.value),
        },
      });
    case "problem_tutor":
      return buildWorkflowRequest({
        ...common,
        workflowType: "problem_tutor",
        workflowPayload: {
          problem: userInput.value,
          user_answer: userAnswer.value,
          help_level: helpLevel.value,
          problem_source: problemSource.value,
        },
      });
    case "mistake_review":
      return buildWorkflowRequest({
        ...common,
        workflowType: "mistake_review",
        workflowPayload: {
          problem: userInput.value,
          original_answer: originalAnswer.value,
          reference_answer: referenceAnswer.value,
          review_focus: reviewFocus.value,
        },
      });
    case "temporary_material_reading":
      return buildWorkflowRequest({
        ...common,
        workflowType: "temporary_material_reading",
        workflowPayload: {
          material_text: userInput.value,
          reading_goal: readingGoal.value,
        },
      });
  }
}

function validateForm(): string | null {
  if (!selectedCourseId.value) return "请先选择课程。";
  if (!selectedCourse.value?.mock_available) return "该课程的 Mock Fixture 尚不可用。";
  if (!userInput.value.trim()) return `请填写${activeWorkflow.value.inputLabel}。`;
  if (workflowType.value === "mistake_review" && !originalAnswer.value.trim()) {
    return "错题复盘需要填写原答案。";
  }
  return null;
}

async function loadCourses(): Promise<void> {
  isLoadingCourses.value = true;
  errorMessage.value = "";
  try {
    courses.value = await getCourses();
    const firstMockCourse = courses.value.find((course) => course.mock_available);
    selectedCourseId.value = firstMockCourse?.course_id ?? courses.value[0]?.course_id ?? "";
  } catch (error) {
    errorMessage.value = toMessage(error);
  } finally {
    isLoadingCourses.value = false;
  }
}

async function submitWorkflow(): Promise<void> {
  errorMessage.value = "";
  noticeMessage.value = "";
  const validationError = validateForm();
  if (validationError) {
    errorMessage.value = validationError;
    return;
  }

  isRunning.value = true;
  try {
    let activeConversationId = conversationId.value;
    if (!activeConversationId) {
      const conversation = await createConversation(selectedCourseId.value);
      activeConversationId = conversation.conversation_id;
      conversationId.value = activeConversationId;
      conversationSnapshot.value = conversation;
    }

    const request = makeRequest(activeConversationId);
    result.value = await runWorkflow(request);
    noticeMessage.value = "Mock 运行已保存，可以重新读取会话验证持久化。";
  } catch (error) {
    errorMessage.value = toMessage(error);
  } finally {
    isRunning.value = false;
  }
}

async function reloadConversation(): Promise<void> {
  if (!conversationId.value) return;
  errorMessage.value = "";
  noticeMessage.value = "";
  isReloading.value = true;
  try {
    const conversation = await getConversation(conversationId.value);
    conversationSnapshot.value = conversation;
    const runs = conversation.runs ?? [];
    result.value = runs[runs.length - 1] ?? result.value;
    noticeMessage.value = "会话已从 GET 接口重新读取。";
  } catch (error) {
    errorMessage.value = toMessage(error);
  } finally {
    isReloading.value = false;
  }
}

watch(knowledgeScope, (scope) => {
  if (scope === "course_only") includeBilibiliResources.value = false;
});

watch(selectedCourseId, () => {
  conversationId.value = "";
  conversationSnapshot.value = null;
  result.value = null;
  noticeMessage.value = "";
});

onMounted(loadCourses);
</script>

<template>
  <div class="app-frame">
    <header class="topbar">
      <a href="#main-content" class="skip-link">跳到主内容</a>
      <div class="brand-lockup">
        <span class="brand-mark" aria-hidden="true">S</span>
        <div>
          <strong>SCUT 老学长</strong>
          <span>课程 Workflow 契约验证</span>
        </div>
      </div>
      <div class="runtime-facts" aria-label="固定 Mock 运行配置">
        <span>provider: mock</span>
        <span>model: deterministic-fixture-v1</span>
      </div>
    </header>

    <aside class="mock-notice" role="note">
      <strong>迭代 0 Mock，不是正式 OAuth / 模型 / 检索</strong>
      <span>当前页面只验证请求、持久化、来源分离和 Trace 契约。</span>
    </aside>

    <main id="main-content" class="workspace">
      <section class="control-shell" aria-labelledby="control-heading">
        <div class="control-intro">
          <p class="section-kicker">发起一次 Mock 运行</p>
          <h1 id="control-heading">选择课程与 Workflow</h1>
          <p>正式课程均保持关闭，只有带 Fixture 的课程可用于本轮契约验证。</p>
        </div>

        <div v-if="isLoadingCourses" class="inline-state" role="status">正在读取课程注册表。</div>

        <form v-else class="workflow-form" @submit.prevent="submitWorkflow">
          <div class="field-group">
            <label for="course">课程</label>
            <select id="course" v-model="selectedCourseId" :disabled="isRunning || !courses.length">
              <option v-if="!courses.length" value="">暂无课程</option>
              <option
                v-for="course in courses"
                :key="course.course_id"
                :value="course.course_id"
                :disabled="!course.mock_available"
              >
                {{ course.display_name }}{{ course.mock_available ? " / Mock 可用" : " / Mock 未配置" }}
              </option>
            </select>
            <div v-if="selectedCourse" class="course-status">
              <span :class="selectedCourse.mock_available ? 'status-available' : 'status-closed'">
                Mock：{{ selectedCourse.mock_available ? "可用" : "关闭" }}
              </span>
              <span class="status-closed">正式开放：{{ selectedCourse.is_open ? "是" : "否" }}</span>
            </div>
          </div>

          <fieldset class="field-group">
            <legend>Workflow</legend>
            <div class="workflow-options">
              <label v-for="type in WORKFLOW_TYPES" :key="type" class="workflow-option">
                <input v-model="workflowType" type="radio" name="workflow" :value="type" />
                <span>
                  <strong>{{ workflowCopy[type].label }}</strong>
                  <small>{{ workflowCopy[type].description }}</small>
                </span>
              </label>
            </div>
          </fieldset>

          <div class="field-group">
            <label for="user-input">{{ activeWorkflow.inputLabel }}</label>
            <textarea
              id="user-input"
              v-model="userInput"
              rows="5"
              :placeholder="activeWorkflow.placeholder"
              required
            ></textarea>
          </div>

          <section v-if="workflowType === 'exam_review'" class="workflow-fields" aria-label="备考复习专属字段">
            <div class="field-group full-width">
              <label for="syllabus">考试大纲（可选）</label>
              <textarea id="syllabus" v-model="syllabus" rows="3" placeholder="粘贴大纲或范围说明。"></textarea>
            </div>
            <div class="field-group">
              <label for="exam-date">考试日期（可选）</label>
              <input id="exam-date" v-model="examDate" type="date" />
            </div>
            <div class="field-group">
              <label for="available-hours">可投入小时（可选）</label>
              <input id="available-hours" v-model.number="availableHours" type="number" min="0" step="0.5" />
            </div>
            <div class="field-group">
              <label for="goals">目标</label>
              <input id="goals" v-model="goalsText" type="text" placeholder="逗号或换行分隔" />
            </div>
            <div class="field-group">
              <label for="weak-topics">薄弱知识点</label>
              <input id="weak-topics" v-model="weakTopicsText" type="text" placeholder="逗号或换行分隔" />
            </div>
          </section>

          <section v-if="workflowType === 'problem_tutor'" class="workflow-fields" aria-label="题目辅导专属字段">
            <div class="field-group full-width">
              <label for="user-answer">我的作答（可选）</label>
              <textarea id="user-answer" v-model="userAnswer" rows="3"></textarea>
            </div>
            <div class="field-group">
              <label for="help-level">帮助层级</label>
              <select id="help-level" v-model="helpLevel">
                <option v-for="level in HELP_LEVELS" :key="level" :value="level">{{ helpLevelLabels[level] }}</option>
              </select>
            </div>
            <div class="field-group">
              <label for="problem-source">题目来源（可选）</label>
              <input id="problem-source" v-model="problemSource" type="text" placeholder="例如：2023 期末 A 卷" />
            </div>
          </section>

          <section v-if="workflowType === 'mistake_review'" class="workflow-fields" aria-label="错题复盘专属字段">
            <div class="field-group full-width">
              <label for="original-answer">原答案</label>
              <textarea id="original-answer" v-model="originalAnswer" rows="3" required></textarea>
            </div>
            <div class="field-group">
              <label for="reference-answer">参考答案（可选）</label>
              <textarea id="reference-answer" v-model="referenceAnswer" rows="3"></textarea>
            </div>
            <div class="field-group">
              <label for="review-focus">复盘重点（可选）</label>
              <textarea id="review-focus" v-model="reviewFocus" rows="3"></textarea>
            </div>
          </section>

          <section v-if="workflowType === 'temporary_material_reading'" class="workflow-fields" aria-label="临时材料精读专属字段">
            <div class="field-group full-width">
              <label for="reading-goal">精读目标（可选）</label>
              <input id="reading-goal" v-model="readingGoal" type="text" placeholder="例如：提取考试范围并指出与课程资料的冲突" />
            </div>
          </section>

          <div class="control-grid">
            <div class="field-group">
              <label for="answer-mode">回答方式</label>
              <select id="answer-mode" v-model="answerMode">
                <option v-for="mode in ANSWER_MODES" :key="mode" :value="mode">{{ answerModeLabels[mode] }}</option>
              </select>
            </div>
            <div class="field-group">
              <label for="tone">表达风格</label>
              <select id="tone" v-model="tone">
                <option v-for="item in TONES" :key="item" :value="item">{{ toneLabels[item] }}</option>
              </select>
            </div>
          </div>

          <fieldset class="field-group scope-fieldset">
            <legend>知识范围</legend>
            <label>
              <input v-model="knowledgeScope" type="radio" value="course_first" />
              <span><strong>资料优先</strong><small>允许明确标记的通用补充</small></span>
            </label>
            <label>
              <input v-model="knowledgeScope" type="radio" value="course_only" />
              <span><strong>仅课程资料</strong><small>证据不足时停止猜测</small></span>
            </label>
          </fieldset>

          <label class="checkbox-field" :class="{ disabled: knowledgeScope === 'course_only' }">
            <input
              v-model="includeBilibiliResources"
              type="checkbox"
              :disabled="knowledgeScope === 'course_only'"
            />
            <span>
              <strong>返回 B站延伸学习</strong>
              <small>仅课程资料模式会在请求构造阶段强制关闭。</small>
            </span>
          </label>

          <div v-if="errorMessage" class="form-message error-message" role="alert">{{ errorMessage }}</div>
          <div v-if="noticeMessage" class="form-message success-message" role="status">{{ noticeMessage }}</div>

          <div class="form-actions">
            <button type="submit" class="primary-button" :disabled="isRunning || isLoadingCourses">
              {{ isRunning ? "正在运行" : "运行 Mock Workflow" }}
            </button>
            <button
              type="button"
              class="secondary-button"
              :disabled="!conversationId || isReloading || isRunning"
              @click="reloadConversation"
            >
              {{ isReloading ? "正在读取" : "重新读取会话" }}
            </button>
          </div>

          <dl class="contract-facts">
            <div>
              <dt>course_scope</dt>
              <dd>single</dd>
            </div>
            <div>
              <dt>conversation_id</dt>
              <dd>{{ conversationId || "首次运行时创建" }}</dd>
            </div>
            <div>
              <dt>allowed_course_ids</dt>
              <dd>[]</dd>
            </div>
          </dl>
        </form>
      </section>

      <WorkflowResult :result="result" :is-running="isRunning" />
    </main>
  </div>
</template>
