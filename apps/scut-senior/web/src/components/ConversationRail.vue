<script setup lang="ts">
import { formatHistoryTime } from "../appConfig";
import { useAppStore } from "../composables/useAppStore";

const store = useAppStore();
</script>

<template>
  <aside id="conversation-rail" class="rail" aria-labelledby="history-heading">
    <header class="rail-head">
      <button
        type="button"
        class="btn btn-primary rail-new"
        :disabled="!store.currentUser || store.historyIsBusy"
        @click="store.startNewConversation"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
          <path d="M12 5v14M5 12h14" />
        </svg>
        新会话
      </button>
    </header>

    <div class="rail-scroll">
      <p
        v-if="store.historyMessage"
        class="note rail-msg"
        :class="store.historyMessageIsError ? 'note-bad' : 'note-ok'"
        :role="store.historyMessageIsError ? 'alert' : 'status'"
      >
        {{ store.historyMessage }}
      </p>

      <p v-if="!store.currentUser" class="rail-empty">登录后可恢复最近会话和全部回答尝试。</p>
      <p v-else-if="store.isLoadingHistory" class="rail-empty" role="status">正在读取历史记录。</p>
      <p v-else-if="!store.historyFolders.length" class="rail-empty">还没有会话。运行后按课程归档，保留 30 天。</p>

      <div v-else class="folders">
        <section v-for="folder in store.historyFolders" :key="folder.courseId" class="folder">
          <div class="folder-row">
            <button
              type="button"
              class="folder-toggle"
              :aria-expanded="store.folderIsOpen(folder.courseId) ? 'true' : 'false'"
              @click="store.toggleFolder(folder.courseId)"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z" />
              </svg>
              <span class="folder-name">{{ folder.label }}</span>
              <span class="chip">{{ folder.conversations.length }}</span>
            </button>
            <button
              type="button"
              class="btn btn-quiet folder-new"
              aria-label="在该课程下新建会话"
              :disabled="store.historyIsBusy"
              @click="store.startNewConversationInCourse(folder.courseId)"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
                <path d="M12 5v14M5 12h14" />
              </svg>
            </button>
          </div>

          <ul v-if="store.folderIsOpen(folder.courseId)" class="folder-list">
            <li
              v-for="conversation in folder.conversations"
              :key="conversation.conversation_id"
              class="convo"
              :class="{ 'convo-open': store.conversationId === conversation.conversation_id }"
            >
              <button
                type="button"
                class="convo-pick"
                :aria-current="store.conversationId === conversation.conversation_id ? 'page' : undefined"
                :disabled="store.historyIsBusy"
                @click="store.loadConversationFromHistory(conversation.conversation_id)"
              >
                <strong class="truncate">{{ conversation.title }}</strong>
                <span class="convo-meta">
                  <time>
                    {{
                      store.loadingConversationId === conversation.conversation_id
                        ? "读取中"
                        : formatHistoryTime(conversation.updated_at)
                    }}
                  </time>
                </span>
              </button>

              <div class="convo-acts">
                <button type="button" class="btn btn-quiet" :disabled="store.historyIsBusy" @click="store.beginRename(conversation)">
                  重命名
                </button>
                <button type="button" class="btn btn-quiet" :disabled="store.historyIsBusy" @click="store.beginDelete(conversation.conversation_id)">
                  删除
                </button>
              </div>

              <form
                v-if="store.editingConversationId === conversation.conversation_id"
                class="convo-form"
                @submit.prevent="store.saveConversationTitle"
              >
                <label :for="`history-title-${conversation.conversation_id}`" class="field-hint">
                  会话名称
                </label>
                <input
                  :id="`history-title-${conversation.conversation_id}`"
                  v-model="store.conversationTitleDraft"
                  type="text"
                  maxlength="100"
                  :disabled="store.renamingConversationId === conversation.conversation_id"
                  required
                />
                <div class="convo-form-row">
                  <button
                    type="submit"
                    class="btn btn-primary"
                    :disabled="store.renamingConversationId === conversation.conversation_id"
                  >
                    {{ store.renamingConversationId === conversation.conversation_id ? "保存中" : "保存" }}
                  </button>
                  <button
                    type="button"
                    class="btn"
                    :disabled="Boolean(store.renamingConversationId)"
                    @click="store.cancelRename"
                  >
                    取消
                  </button>
                </div>
              </form>

              <div v-else-if="store.deleteConfirmId === conversation.conversation_id" class="convo-danger">
                <span>会同时删除全部回答，确定吗？</span>
                <div class="convo-form-row">
                  <button
                    type="button"
                    class="btn btn-danger"
                    :disabled="store.deletingConversationId === conversation.conversation_id"
                    @click="store.confirmDeleteConversation(conversation.conversation_id)"
                  >
                    {{ store.deletingConversationId === conversation.conversation_id ? "删除中" : "确认删除" }}
                  </button>
                  <button
                    type="button"
                    class="btn"
                    :disabled="Boolean(store.deletingConversationId)"
                    @click="store.cancelDelete"
                  >
                    取消
                  </button>
                </div>
              </div>
            </li>
          </ul>
        </section>
      </div>
    </div>
  </aside>
</template>

<style>
.rail-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 9px 10px 9px 12px;
  border-bottom: 1px solid var(--line);
}

.rail-head .btn svg {
  width: 16px;
  height: 16px;
}

.rail-new {
  flex: 1 1 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.rail-scroll {
  min-height: 0;
  overflow-y: auto;
  padding: 6px;
}

.rail-msg {
  margin: 0 6px 6px;
}

.rail-empty {
  padding: 12px 8px;
  color: var(--text-muted);
  font-size: var(--fs-xs);
  line-height: 1.6;
}

.folders {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.folder {
  border: 1px solid var(--line);
  border-radius: var(--r-md);
  background: var(--panel);
  overflow: hidden;
}

.folder-row {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px;
}

.folder-toggle {
  flex: 1 1 auto;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  padding: 9px 8px;
  border: 0;
  background: transparent;
  color: var(--text);
  font-size: var(--fs-sm);
  font-weight: 700;
  text-align: left;
  cursor: pointer;
  border-radius: var(--r-sm);
}

.folder-toggle:hover {
  background: var(--sunken);
}

.folder-toggle svg {
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
  color: var(--accent);
}

.folder-name {
  flex: 1 1 auto;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.folder-new {
  flex: 0 0 auto;
  width: 30px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.folder-new svg {
  width: 16px;
  height: 16px;
}

.folder-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 0;
  padding: 0 8px 8px;
  list-style: none;
}

.folder-list .convo {
  display: block;
  border: 1px solid var(--line);
  border-radius: var(--r-md);
  background: var(--raised);
}

.folder-list .convo-open {
  border-color: var(--accent);
  background: var(--accent-wash);
}

.folder-list .convo-pick {
  padding: 10px;
}

.convo {
  border-radius: var(--r-sm);
}

.convo + .convo {
  margin-top: 1px;
}

.convo-open {
  background: var(--accent-wash);
}

.convo-pick {
  display: grid;
  gap: 1px;
  width: 100%;
  padding: 6px 8px;
  border: 0;
  border-radius: var(--r-sm);
  background: transparent;
  text-align: left;
}

.convo-pick:hover:not(:disabled) {
  background: var(--sunken);
}

.convo-open .convo-pick:hover:not(:disabled) {
  background: transparent;
}

.convo-pick strong {
  font-size: var(--fs-sm);
  font-weight: 600;
}

.convo-meta {
  display: flex;
  gap: 6px;
  color: var(--text-muted);
  font-size: var(--fs-2xs);
}

.convo-meta > time {
  flex: 0 0 auto;
  font-family: var(--font-mono);
}

.convo-acts {
  display: flex;
  gap: 2px;
  padding: 0 6px 5px;
}

.convo:not(.convo-open) .convo-acts {
  visibility: hidden;
}

.convo:hover .convo-acts,
.convo:focus-within .convo-acts {
  visibility: visible;
}

.convo-form {
  display: grid;
  gap: 5px;
  padding: 6px 8px 8px;
}

.convo-form-row {
  display: flex;
  gap: 5px;
}

.convo-danger {
  display: grid;
  gap: 6px;
  padding: 6px 8px 8px;
  color: var(--bad-text);
  font-size: var(--fs-2xs);
  line-height: 1.5;
}

/* 触屏：会话操作始终可见。 */
@media (pointer: coarse) {
  .convo-acts {
    visibility: visible;
  }
}
</style>
