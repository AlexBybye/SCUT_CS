<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { getTemporaryMaterial, listContributions, listTemporaryMaterials, previewContribution, savePrivateKnowledge } from "../api";
import type { ContributionConfirmations, ContributionPreview, ContributionRecord, TemporaryMaterialRecord } from "../contracts";
import { useAppStore } from "../composables/useAppStore";
import { deletePrivateKnowledge, exportPersonalContribution, exportPrivateKnowledge, getPersonalContribution, getPrivateKnowledge, listPrivateKnowledge, renewPrivateKnowledge, sendPersonalContribution, type PersonalContributionDetail, type PrivateKnowledgeDetail, type PrivateKnowledgeRecord } from "../personalContentApi";
import { clearContentHandoff, contentHandoff, isValidContributorEmail, readContentHandoff, readContributorEmail, saveContributorEmail, type ContentHandoff } from "../personalContentSession";

const props = defineProps<{ initialTab?: "contributions" | "private"; initialMaterialId?: string }>();
const emit = defineEmits<{ back: []; "tab-change": [tab: "contributions" | "private"] }>();
const store = useAppStore();
const tab = ref<"contributions" | "private">(props.initialTab ?? "contributions");
const email = ref("");
const emailInput = ref("");
const editingEmail = ref(false);
const emailError = ref("");
const error = ref("");
const notice = ref("");
const loading = ref(false);
const busy = ref(false);
const detailLoading = ref(false);
const contributions = ref<ContributionRecord[]>([]);
const materials = ref<TemporaryMaterialRecord[]>([]);
const privateItems = ref<PrivateKnowledgeRecord[]>([]);
const privateDetail = ref<PrivateKnowledgeDetail | null>(null);
const contributionDetail = ref<PersonalContributionDetail | null>(null);
const privateFilter = ref("");
const hasMorePrivate = ref(false);
const privateLoading = ref(false);
const selectedId = ref("");
const deletingId = ref("");
const composing = ref(true);
const privateCreating = ref(false);
const title = ref("");
const courseId = ref("");
const content = ref("");
const materialId = ref("");
const originalMaterialContent = ref("");
const supplementary = ref("");
const handoff = ref<ContentHandoff | null>(null);
const preview = ref<ContributionPreview | null>(null);
const newPrivateTitle = ref("");
const newPrivateCourse = ref("");
const newPrivateContent = ref("");
const emptyConfirmations = (): ContributionConfirmations => ({ course_confirmed: false, source_confirmed: false, public_share_rights_confirmed: false, no_sensitive_info_confirmed: false, public_pr_visibility_acknowledged: false });
const confirmations = ref(emptyConfirmations());
const confirmed = computed(() => Object.values(confirmations.value).every(Boolean));
const canPreview = computed(() => !!courseId.value && !!content.value.trim() && !!title.value.trim());
const courses = computed(() => store.courses.filter(course => course.selectable));
const userId = computed(() => store.currentUser?.user_id ?? "");
const stateLabels: Record<string, string> = { submitted: "待审核", pr_open: "PR 已创建", merged: "已合并", rejected: "未采纳", expired: "已过期" };
const date = (value: string) => new Date(value).toLocaleString("zh-CN", { hour12: false });
const courseName = (id: string) => store.courses.find(course => course.course_id === id)?.display_name ?? id;
const readableError = (cause: unknown) => cause instanceof Error ? cause.message : "操作失败，请重试。";
let accountEpoch = 0;
let detailEpoch = 0;
let privateEpoch = 0;
let composeEpoch = 0;
let disposed = false;
const current = (epoch: number) => !disposed && epoch === accountEpoch;

function selectTab(value: "contributions" | "private"): void {
  tab.value = value; error.value = ""; notice.value = ""; emit("tab-change", value);
}
watch(() => props.initialTab, value => { if (value) tab.value = value; });
watch([title, courseId, content, materialId, email, supplementary], () => {
  preview.value = null; confirmations.value = emptyConfirmations(); ++composeEpoch;
}, { flush: "sync" });
function registerEmail(): void {
  emailError.value = "";
  if (!isValidContributorEmail(emailInput.value)) { emailError.value = "请填写有效的邮箱，例如 name@example.com。"; return; }
  try { saveContributorEmail(userId.value, emailInput.value); email.value = emailInput.value.trim(); editingEmail.value = false; }
  catch (cause) { emailError.value = readableError(cause); }
}
function newContribution(): void {
  ++detailEpoch; composing.value = true; selectedId.value = ""; contributionDetail.value = null;
  title.value = ""; content.value = ""; materialId.value = ""; originalMaterialContent.value = "";
  supplementary.value = ""; handoff.value = null; courseId.value = store.selectedCourseId;
}
function applyHandoff(): void {
  const value = readContentHandoff(userId.value);
  if (!value) return;
  newContribution(); handoff.value = value; title.value = value.title;
  content.value = value.content; courseId.value = value.course_id; tab.value = "contributions";
}
watch(contentHandoff, applyHandoff);
async function loadMaterial(id: string): Promise<void> {
  if (!id || !userId.value || busy.value) return;
  const epoch = accountEpoch;
  const request = ++detailEpoch;
  busy.value = true; error.value = "";
  try {
    const value = await getTemporaryMaterial(id);
    if (!current(epoch) || request !== detailEpoch) return;
    newContribution(); title.value = value.title || "未命名材料"; content.value = value.content;
    courseId.value = value.course_id; materialId.value = id; originalMaterialContent.value = value.content;
  } catch (cause) { if (current(epoch)) error.value = readableError(cause); }
  finally { if (current(epoch)) busy.value = false; }
}
watch(() => props.initialMaterialId, id => { if (id && userId.value) void loadMaterial(id); });
async function loadPrivate(more = false): Promise<void> {
  if (!userId.value) return;
  const request = ++privateEpoch;
  const epoch = accountEpoch;
  privateLoading.value = true;
  try {
    const items = await listPrivateKnowledge(privateFilter.value, more ? privateItems.value.length : 0);
    if (!current(epoch) || request !== privateEpoch) return;
    privateItems.value = more ? [...privateItems.value, ...items] : items;
    hasMorePrivate.value = items.length === 30;
  } catch (cause) { if (current(epoch) && request === privateEpoch) error.value = readableError(cause); }
  finally { if (current(epoch) && request === privateEpoch) privateLoading.value = false; }
}
watch(privateFilter, () => { privateItems.value = []; privateDetail.value = null; ++detailEpoch; void loadPrivate(); });
async function refresh(): Promise<void> {
  if (!userId.value || loading.value) return;
  const epoch = accountEpoch;
  loading.value = true; error.value = "";
  const results = await Promise.allSettled([listContributions(), listTemporaryMaterials(), loadPrivate()]);
  if (!current(epoch)) return;
  if (results[0].status === "fulfilled") contributions.value = results[0].value;
  else error.value = readableError(results[0].reason);
  if (results[1].status === "fulfilled") materials.value = results[1].value;
  else error.value = readableError(results[1].reason);
  loading.value = false;
}
watch(userId, () => {
  ++accountEpoch; ++detailEpoch; ++privateEpoch;
  contributions.value = []; materials.value = []; privateItems.value = [];
  privateDetail.value = null; contributionDetail.value = null; selectedId.value = "";
  loading.value = false; busy.value = false; privateLoading.value = false; detailLoading.value = false;
  error.value = ""; notice.value = ""; deletingId.value = "";
  newPrivateTitle.value = ""; newPrivateContent.value = ""; privateCreating.value = false;
  email.value = readContributorEmail(userId.value); emailInput.value = email.value; editingEmail.value = false;
  newContribution(); newPrivateCourse.value = store.selectedCourseId;
  if (userId.value) { applyHandoff(); void refresh(); if (props.initialMaterialId) void loadMaterial(props.initialMaterialId); }
}, { immediate: true });
onBeforeUnmount(() => { disposed = true; ++accountEpoch; });

async function selectItem(id: string, kind: "contributions" | "private"): Promise<void> {
  const epoch = accountEpoch;
  const request = ++detailEpoch;
  selectedId.value = id; composing.value = false; privateCreating.value = false;
  privateDetail.value = null; contributionDetail.value = null; deletingId.value = "";
  detailLoading.value = true; error.value = "";
  try {
    if (kind === "private") {
      const value = await getPrivateKnowledge(id);
      if (current(epoch) && request === detailEpoch) privateDetail.value = value;
    } else {
      const value = await getPersonalContribution(id);
      if (current(epoch) && request === detailEpoch) contributionDetail.value = value;
    }
  } catch (cause) { if (current(epoch) && request === detailEpoch) error.value = readableError(cause); }
  finally { if (current(epoch) && request === detailEpoch) detailLoading.value = false; }
}
async function makePreview(): Promise<void> {
  if (busy.value || !canPreview.value) return;
  const epoch = accountEpoch; const revision = composeEpoch;
  busy.value = true; error.value = "";
  try {
    const value = await previewContribution({ title: title.value, course_id: courseId.value, content: content.value });
    if (current(epoch) && revision === composeEpoch) preview.value = value;
  } catch (cause) { if (current(epoch)) error.value = readableError(cause); }
  finally { if (current(epoch)) busy.value = false; }
}
async function submit(): Promise<void> {
  if (busy.value || !preview.value || !confirmed.value || !email.value || !canPreview.value) return;
  const epoch = accountEpoch;
  busy.value = true; error.value = ""; notice.value = "";
  try {
    const value = await sendPersonalContribution({
      ...(materialId.value && content.value === originalMaterialContent.value ? { material_id: materialId.value } : { content: content.value }),
      course_id: courseId.value, title: title.value.trim(), github_email: email.value,
      supplementary_text: supplementary.value.trim() || undefined,
      ...(handoff.value ? { run_id: handoff.value.run_id, workflow_type: handoff.value.workflow_type, citation_metadata: handoff.value.citation_metadata, corpus_metadata: handoff.value.corpus_metadata } : {}),
      confirmations: { ...confirmations.value },
    });
    if (!current(epoch)) return;
    clearContentHandoff(userId.value); newContribution();
    contributions.value = [value, ...contributions.value.filter(item => item.contribution_id !== value.contribution_id)];
    notice.value = "已提交到维护者队列。你可以在这里查看审核进度。";
    await selectItem(value.contribution_id, "contributions");
  } catch (cause) { if (current(epoch)) error.value = readableError(cause); }
  finally { if (current(epoch)) busy.value = false; }
}
async function privateAction(action: "delete" | "renew"): Promise<void> {
  if (busy.value || !privateDetail.value) return;
  const epoch = accountEpoch; const id = privateDetail.value.knowledge_id;
  busy.value = true; error.value = "";
  try {
    if (action === "delete") {
      await deletePrivateKnowledge(id);
      if (!current(epoch)) return;
      if (privateDetail.value?.knowledge_id === id) privateDetail.value = null;
      privateItems.value = privateItems.value.filter(item => item.knowledge_id !== id);
      deletingId.value = ""; notice.value = "私人知识已删除，无法恢复。";
    } else {
      const item = await renewPrivateKnowledge(id);
      if (!current(epoch)) return;
      if (privateDetail.value?.knowledge_id === id) privateDetail.value = { ...privateDetail.value, ...item };
      privateItems.value = privateItems.value.map(value => value.knowledge_id === id ? item : value);
      notice.value = "已续期，从现在起保留 7 天。";
    }
  } catch (cause) { if (current(epoch)) error.value = readableError(cause); }
  finally { if (current(epoch)) busy.value = false; }
}
async function download(id: string, kind: "contributions" | "private"): Promise<void> {
  if (busy.value) return;
  const epoch = accountEpoch; busy.value = true; error.value = "";
  try {
    const value = kind === "private" ? await exportPrivateKnowledge(id) : await exportPersonalContribution(id);
    if (!current(epoch)) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: "application/json;charset=utf-8" }));
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = `${kind}-${id}.json`;
    document.body.appendChild(anchor); anchor.click(); anchor.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    notice.value = "导出文件已生成。";
  } catch (cause) { if (current(epoch)) error.value = readableError(cause); }
  finally { if (current(epoch)) busy.value = false; }
}
async function createPrivate(): Promise<void> {
  if (busy.value || !newPrivateCourse.value || !newPrivateContent.value.trim()) return;
  const epoch = accountEpoch; busy.value = true; error.value = "";
  try {
    await savePrivateKnowledge({ course_id: newPrivateCourse.value, title: newPrivateTitle.value || null, content: newPrivateContent.value });
    if (!current(epoch)) return;
    newPrivateContent.value = ""; newPrivateTitle.value = ""; privateCreating.value = false;
    notice.value = "已加入私人知识库，默认保留 7 天。"; await loadPrivate();
  } catch (cause) { if (current(epoch)) error.value = readableError(cause); }
  finally { if (current(epoch)) busy.value = false; }
}
function safePrUrl(value: string | null): string | undefined {
  try { const url = new URL(value ?? ""); return url.protocol === "https:" && url.hostname === "github.com" ? url.href : undefined; }
  catch { return undefined; }
}
</script>

<template>
  <main class="personal-content">
    <header class="personal-header"><a href="/" class="btn btn-quiet" @click.prevent="emit('back')">返回对话</a><h1>个人知识平台</h1><p>管理自己的学习资料，参与课程资源共建。</p></header>
    <nav class="personal-tabs" aria-label="内容分类"><button type="button" :aria-current="tab === 'contributions' ? 'page' : undefined" @click="selectTab('contributions')">我的贡献</button><button type="button" :aria-current="tab === 'private' ? 'page' : undefined" @click="selectTab('private')">私人知识</button></nav>
    <p v-if="store.isLoadingAuth" class="personal-empty" role="status">正在确认登录状态…</p>
    <section v-else-if="!store.currentUser" class="personal-empty"><h2>让学习资料有个自己的位置</h2><p>登录后即可管理私人知识和贡献内容，无需维护者权限。</p><button type="button" class="btn btn-primary" @click="store.startGithubLogin()">使用 GitHub 登录</button></section>
    <template v-else>
      <p v-if="error" class="note note-bad" role="alert">{{ error }} <button type="button" class="btn btn-quiet" :disabled="loading" @click="refresh">刷新列表</button></p>
      <p v-if="notice" class="note note-ok" role="status">{{ notice }}</p>
      <section v-if="tab === 'contributions' && (!email || editingEmail)" class="personal-welcome" aria-labelledby="contributor-welcome-title">
        <div class="personal-invitation"><span class="personal-wordmark">SCUT_CS</span><h2 id="contributor-welcome-title">欢迎加入<br />SCUT_CS 开源计划</h2><p>把你整理的一份好资料，留给下一位同学。</p></div>
        <form class="personal-email-form" @submit.prevent="registerEmail"><h3>{{ email ? '修改贡献署名邮箱' : '先留下你的贡献署名' }}</h3><label for="contributor-email">GitHub 关联邮箱</label><input id="contributor-email" v-model="emailInput" type="email" maxlength="254" autocomplete="email" required placeholder="name@example.com" :aria-invalid="!!emailError" aria-describedby="contributor-email-help" /><p id="contributor-email-help">请填写已关联 GitHub 的邮箱，也支持 GitHub noreply 邮箱。维护者会用它填写 Co-authored-by；贡献被采纳后，邮箱可能随公开提交长期可见。</p><p>邮箱仅保存在本浏览器会话中，可随时修改；这不会验证或更改你的 GitHub 账户。</p><p v-if="emailError" class="personal-error" role="alert">{{ emailError }}</p><div class="personal-actions"><button class="btn btn-primary" type="submit">{{ email ? '保存邮箱' : '开始贡献' }}</button><button v-if="email" type="button" class="btn btn-quiet" @click="editingEmail = false">取消</button></div></form>
      </section>
      <template v-else-if="tab === 'contributions'">
        <div class="personal-toolbar"><p>署名邮箱 <strong>{{ email }}</strong><button type="button" class="btn btn-quiet" :disabled="busy" @click="emailInput = email; editingEmail = true">修改</button></p><button type="button" class="btn btn-quiet" :disabled="loading || busy" @click="refresh">刷新</button></div>
        <div class="personal-split">
          <aside class="personal-list" aria-label="贡献记录"><button type="button" class="btn btn-primary personal-new" :disabled="busy" @click="newContribution">准备新贡献</button><p v-if="loading" class="personal-skeleton" role="status">正在读取贡献记录…</p><p v-else-if="!contributions.length" class="personal-list-empty">还没有提交过贡献。可以粘贴文本，也可以选择已保存的临时材料。</p><button v-for="item in contributions" :key="item.contribution_id" type="button" class="personal-list-item" :class="{ selected: selectedId === item.contribution_id && !composing }" :disabled="busy" @click="selectItem(item.contribution_id, 'contributions')"><strong>{{ item.title }}</strong><span>{{ courseName(item.course_id) }}</span><small>{{ stateLabels[item.state] ?? item.state }} · {{ new Date(item.created_at).toLocaleDateString('zh-CN') }}</small></button></aside>
          <section class="personal-detail" aria-label="贡献内容">
            <form v-if="composing" class="personal-form" @submit.prevent="submit"><h2>准备贡献</h2><fieldset class="personal-fields" :disabled="busy"><label v-if="materials.length">使用已保存的临时材料<select :value="materialId" @change="loadMaterial(($event.target as HTMLSelectElement).value)"><option value="">直接编辑文本</option><option v-for="item in materials" :key="item.material_id" :value="item.material_id">{{ item.title || '未命名材料' }} ({{ courseName(item.course_id) }})</option></select></label><div class="personal-form-row"><label>归属课程<select v-model="courseId" required><option value="" disabled>选择课程</option><option v-for="course in courses" :key="course.course_id" :value="course.course_id">{{ course.display_name }}</option></select></label><label>资料标题<input v-model="title" required maxlength="200" placeholder="例如：操作系统进程同步学习笔记" /></label></div><label>贡献正文<textarea v-model="content" required rows="12" maxlength="100000" placeholder="粘贴文本或 Markdown，或从每轮回答后的「我要贡献」带入内容。" /></label><label>给维护者的补充说明（选填）<textarea v-model="supplementary" rows="2" maxlength="4000" placeholder="说明来源、修订内容或建议收录位置。" /></label><p class="personal-help">提交前会显示转换预览。审核通过后才会进入公共资料库。</p><button type="button" class="btn btn-quiet" :disabled="!canPreview" @click="makePreview">{{ busy ? '处理中…' : '检查并预览' }}</button></fieldset>
              <section v-if="preview" class="personal-preview"><h3>提交预览</h3><p v-if="preview.question_marker_count">识别到 {{ preview.question_marker_count }} 处题目标记</p><p v-for="warning in preview.warnings" :key="warning" class="note note-warn">{{ warning }}</p><details><summary>查看转换后的正文</summary><pre>{{ preview.normalized_content }}</pre></details><fieldset class="personal-confirmations" :disabled="busy"><legend>公开提交前，请逐项确认</legend><label><input v-model="confirmations.course_confirmed" type="checkbox" /> 归属课程正确</label><label><input v-model="confirmations.source_confirmed" type="checkbox" /> 来源真实，内容未被篡改</label><label><input v-model="confirmations.public_share_rights_confirmed" type="checkbox" /> 我拥有公开分享这些内容的权利</label><label><input v-model="confirmations.no_sensitive_info_confirmed" type="checkbox" /> 内容不含隐私或敏感信息</label><label><input v-model="confirmations.public_pr_visibility_acknowledged" type="checkbox" /> 我了解公开 PR 及署名邮箱可能长期可见</label></fieldset><button type="submit" class="btn btn-primary" :disabled="busy || !confirmed">{{ busy ? '正在提交…' : '提交给维护者' }}</button></section>
            </form>
            <p v-else-if="detailLoading" class="personal-skeleton" role="status">正在读取贡献详情…</p>
            <article v-else-if="contributionDetail" class="personal-form"><h2>{{ contributionDetail.title }}</h2><p>{{ stateLabels[contributionDetail.state] ?? contributionDetail.state }} · {{ courseName(contributionDetail.course_id) }}</p><p v-if="contributionDetail.github_email">提交时署名邮箱：{{ contributionDetail.github_email }}</p><p v-if="contributionDetail.maintainer_note" class="note">维护者备注：{{ contributionDetail.maintainer_note }}</p><div class="personal-actions"><button type="button" class="btn btn-quiet" :disabled="busy" @click="download(contributionDetail.contribution_id, 'contributions')">导出 JSON</button><a v-if="safePrUrl(contributionDetail.pr_url)" class="btn btn-quiet" :href="safePrUrl(contributionDetail.pr_url)" target="_blank" rel="noopener noreferrer">查看 GitHub PR</a></div><pre v-if="contributionDetail.content_snapshot">{{ contributionDetail.content_snapshot }}</pre><p v-else class="personal-help">正文已到期清理，审核记录仍可查看。</p><details v-if="contributionDetail.attachments.length"><summary>附件 {{ contributionDetail.attachments.length }} 个</summary><p v-for="attachment in contributionDetail.attachments" :key="attachment.attachment_id">{{ attachment.original_filename }} ({{ attachment.byte_size }} 字节)</p></details></article>
            <p v-else class="personal-empty">选择一条贡献查看详情，或准备新贡献。</p>
          </section>
        </div>
      </template>
      <template v-else>
        <div class="personal-toolbar"><p>仅对你可见，默认保留 7 天。到期前可以手动续期或导出。</p><button type="button" class="btn btn-quiet" :disabled="privateLoading || busy" @click="loadPrivate()">刷新</button></div>
        <div class="personal-split"><aside class="personal-list" aria-label="私人知识列表"><button type="button" class="btn btn-primary personal-new" :disabled="busy" @click="privateCreating = true; privateDetail = null; newPrivateCourse = store.selectedCourseId">添加私人知识</button><label class="personal-filter">课程筛选<select v-model="privateFilter"><option value="">全部课程</option><option v-for="course in store.courses" :key="course.course_id" :value="course.course_id">{{ course.display_name }}</option></select></label><p v-if="privateLoading && !privateItems.length" class="personal-skeleton" role="status">正在读取私人知识…</p><p v-else-if="!privateItems.length" class="personal-list-empty">这里还没有资料。可以手动添加，也可以在每轮回答后选择「加入私人知识库」。</p><button v-for="item in privateItems" :key="item.knowledge_id" type="button" class="personal-list-item" :class="{ selected: privateDetail?.knowledge_id === item.knowledge_id }" :disabled="busy" @click="selectItem(item.knowledge_id, 'private')"><strong>{{ item.title || '未命名知识' }}</strong><span>{{ courseName(item.course_id) }}</span><small>{{ item.char_count }} 字 · {{ new Date(item.expires_at).toLocaleDateString('zh-CN') }} 到期</small></button><button v-if="hasMorePrivate" type="button" class="btn btn-quiet" :disabled="privateLoading" @click="loadPrivate(true)">{{ privateLoading ? '正在读取…' : '加载更多' }}</button></aside>
          <section class="personal-detail" aria-label="私人知识内容"><form v-if="privateCreating" class="personal-form" @submit.prevent="createPrivate"><h2>添加私人知识</h2><fieldset class="personal-fields" :disabled="busy"><label>归属课程<select v-model="newPrivateCourse" required><option value="" disabled>选择课程</option><option v-for="course in courses" :key="course.course_id" :value="course.course_id">{{ course.display_name }}</option></select></label><label>标题（选填）<input v-model="newPrivateTitle" maxlength="200" /></label><label>正文<textarea v-model="newPrivateContent" required rows="14" maxlength="100000" /></label><p class="personal-help">仅在自己的课程学习中使用，不会进入公共索引；7 天后自动删除。</p><button type="submit" class="btn btn-primary" :disabled="!newPrivateCourse || !newPrivateContent.trim()">{{ busy ? '正在保存…' : '保存到私人知识库' }}</button></fieldset></form><p v-else-if="detailLoading" class="personal-skeleton" role="status">正在读取私人知识详情…</p><article v-else-if="privateDetail" class="personal-form"><h2>{{ privateDetail.title || '未命名知识' }}</h2><p>{{ courseName(privateDetail.course_id) }} · {{ privateDetail.char_count }} 字</p><p>到期时间：{{ date(privateDetail.expires_at) }}</p><div class="personal-actions"><button type="button" class="btn btn-quiet" :disabled="busy" @click="privateAction('renew')">从现在起续期 7 天</button><button type="button" class="btn btn-quiet" :disabled="busy" @click="download(privateDetail.knowledge_id, 'private')">导出 JSON</button><button type="button" class="btn btn-quiet" :disabled="busy" @click="deletingId = privateDetail.knowledge_id">删除</button></div><div v-if="deletingId === privateDetail.knowledge_id" class="note note-warn"><p>删除后正文无法恢复，建议先导出需要保留的内容。</p><div class="personal-actions"><button type="button" class="btn btn-danger" :disabled="busy" @click="privateAction('delete')">确认删除</button><button type="button" class="btn btn-quiet" :disabled="busy" @click="deletingId = ''">取消</button></div></div><pre>{{ privateDetail.content }}</pre></article><div v-else class="personal-empty"><h2>你的学习资料，由你管理</h2><p>选择左侧资料查看全文、导出、续期或删除。</p></div></section>
        </div>
      </template>
    </template>
  </main>
</template>

<style scoped>
.personal-content { width: min(1240px, 100%); margin: 0 auto; padding: 28px 32px 64px; color: var(--text); font-family: var(--font-ui); }
.personal-header { margin-bottom: 22px; }
.personal-header > .btn { margin-left: -10px; }
.personal-header h1 { margin: 20px 0 8px; font-size: 28px; letter-spacing: -.025em; }
.personal-header p, .personal-toolbar p, .personal-help, .personal-email-form p { color: var(--text-muted); line-height: 1.7; margin: 0; }
.personal-tabs { display: flex; gap: 26px; border-bottom: 1px solid var(--line-strong); margin-bottom: 24px; }
.personal-tabs button { padding: 10px 0 14px; border: 0; border-bottom: 3px solid transparent; background: transparent; color: var(--text-muted); cursor: pointer; font-weight: 650; }
.personal-tabs button[aria-current] { color: var(--accent); border-color: var(--accent); }
.personal-toolbar, .personal-actions { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.personal-toolbar { margin-bottom: 18px; font-size: var(--fs-sm); }
.personal-toolbar strong { font-weight: 550; color: var(--text); overflow-wrap: anywhere; }
.personal-actions { justify-content: flex-start; }
.personal-welcome { display: grid; grid-template-columns: 1fr 1.1fr; border: 1px solid var(--line); border-radius: var(--r-md); overflow: hidden; background: var(--panel); }
.personal-invitation { padding: 44px 36px; background: var(--accent-wash); }
.personal-wordmark { font-family: var(--font-mono); color: var(--accent); font-size: 16px; font-weight: 700; }
.personal-invitation h2 { font-size: clamp(24px, 2.6vw, 34px); line-height: 1.45; letter-spacing: -.03em; margin: 40px 0 18px; }
.personal-invitation p { margin: 0; color: var(--text-muted); line-height: 1.8; }
.personal-email-form { display: grid; align-content: center; gap: 14px; padding: 36px; font-size: var(--fs-sm); }
.personal-email-form h3 { margin: 0 0 6px; font-size: 19px; }
.personal-email-form input { width: 100%; }
.personal-split { display: grid; grid-template-columns: minmax(220px, 300px) minmax(0, 1fr); border: 1px solid var(--line); border-radius: var(--r-md); overflow: hidden; background: var(--panel); min-height: 560px; }
.personal-list { padding: 16px; border-right: 1px solid var(--line); background: var(--page); display: flex; flex-direction: column; gap: 8px; align-self: stretch; }
.personal-new { width: 100%; margin-bottom: 12px; }
.personal-list-item { display: grid; text-align: left; gap: 6px; width: 100%; padding: 13px 12px; background: transparent; border: 1px solid transparent; border-radius: var(--r-sm); color: var(--text); cursor: pointer; overflow-wrap: anywhere; }
.personal-list-item.selected { background: var(--accent-wash); border-color: var(--accent); }
.personal-list-item:hover { background: var(--raised); }
.personal-list-item.selected:hover { background: var(--accent-wash); }
.personal-list-item span, .personal-list-item small { color: var(--text-muted); font-size: var(--fs-2xs); line-height: 1.5; }
.personal-list-item strong { font-size: var(--fs-sm); line-height: 1.5; font-weight: 650; }
.personal-list-empty { color: var(--text-muted); line-height: 1.8; font-size: var(--fs-sm); padding: 8px; }
.personal-detail { padding: 28px; min-width: 0; }
.personal-form { display: grid; gap: 18px; }
.personal-form h2 { margin: 0; font-size: 21px; line-height: 1.5; overflow-wrap: anywhere; }
.personal-form p { margin: 0; line-height: 1.7; }
.personal-fields { display: grid; gap: 18px; padding: 0; margin: 0; border: 0; min-width: 0; }
.personal-form label, .personal-filter { display: grid; gap: 8px; font-size: var(--fs-sm); color: var(--text); min-width: 0; }
.personal-form-row { display: grid; grid-template-columns: 1fr 1.3fr; gap: 16px; }
.personal-form input, .personal-form textarea, .personal-form select, .personal-filter select { width: 100%; min-width: 0; }
.personal-form textarea { resize: vertical; line-height: 1.7; }
.personal-help { font-size: var(--fs-xs); }
.personal-fields > .btn { justify-self: start; }
.personal-preview { display: grid; gap: 16px; border-top: 1px solid var(--line); padding-top: 20px; }
.personal-preview h3 { margin: 0; font-size: 17px; }
.personal-preview > .btn { justify-self: start; }
.personal-confirmations { display: grid; gap: 12px; padding: 0; border: 0; margin: 4px 0; }
.personal-confirmations legend { padding: 0; margin-bottom: 16px; font-size: var(--fs-sm); font-weight: 650; }
.personal-confirmations label { display: flex; flex-direction: row; align-items: flex-start; line-height: 1.6; }
.personal-confirmations input { width: auto; flex-shrink: 0; margin-top: 4px; accent-color: var(--accent); }
.personal-content pre { margin: 0; padding: 18px; border-radius: var(--r-sm); background: var(--sunken); line-height: 1.8; font-size: var(--fs-sm); white-space: pre-wrap; overflow-wrap: anywhere; max-height: 560px; overflow-y: auto; }
.personal-content details summary { cursor: pointer; padding: 8px 0; font-size: var(--fs-sm); }
.personal-empty { padding: 64px 24px; color: var(--text-muted); text-align: center; line-height: 1.8; }
.personal-empty h2 { font-size: 20px; color: var(--text); }
.personal-empty .btn { margin-top: 12px; }
.personal-skeleton { padding: 22px 14px; background: var(--sunken); border-radius: var(--r-sm); color: var(--text-muted); font-size: var(--fs-sm); }
.personal-error { color: var(--bad-text) !important; }
.personal-content > .note { margin-bottom: 18px; }
.personal-content button:focus-visible, .personal-content a:focus-visible, .personal-content summary:focus-visible { outline: 2px solid var(--focus); outline-offset: 3px; }
.personal-content .btn { white-space: nowrap; }
@media (max-width: 768px) { .personal-content { padding: 20px 16px 40px; } .personal-welcome, .personal-split { grid-template-columns: 1fr; } .personal-invitation, .personal-email-form { padding: 28px 24px; } .personal-invitation h2 { margin-top: 22px; } .personal-list { border-right: 0; border-bottom: 1px solid var(--line); max-height: 340px; overflow-y: auto; } .personal-detail { padding: 22px 18px; } .personal-form-row { grid-template-columns: 1fr; } .personal-empty { padding: 36px 12px; } }
</style>
