<template>
  <div class="comment-section">
    <h3 class="section-title">评论 ({{ replies.length }})</h3>

    <div class="comment-form">
      <textarea
        v-model="newComment"
        class="comment-input"
        placeholder="写下你的评论..."
        rows="3"
        @keydown.ctrl.enter="submitComment"
      ></textarea>
      <div class="form-actions">
        <span class="hint">Ctrl + Enter 发布</span>
        <button 
          class="btn btn-primary" 
          :disabled="!newComment.trim() || submitting"
          @click="submitComment"
        >
          {{ submitting ? '发布中...' : '发布评论' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载评论中...</p>
    </div>

    <div v-else-if="replies.length === 0" class="empty-state">
      <p class="empty-text">💬 暂无评论，来抢沙发吧！</p>
    </div>

    <div v-else class="comments-list">
      <div 
        v-for="reply in replies" 
        :key="reply.id" 
        class="comment-item"
      >
        <div class="comment-avatar">
          {{ reply.user_name?.[0] || 'U' }}
        </div>
        <div class="comment-content">
          <div class="comment-header">
            <span class="comment-author">{{ reply.user_name }}</span>
            <span class="comment-time">{{ formatTime(reply.created_at) }}</span>
          </div>
          <p class="comment-text">{{ reply.content }}</p>
          <div class="comment-actions">
            <button 
              class="action-btn" 
              :class="{ liked: reply.is_liked }"
              @click="handleLike(reply)"
            >
              👍 {{ reply.likes || 0 }}
            </button>
            <button class="action-btn" @click="replyTo(reply)">
              💬 回复
            </button>
          </div>

          <div v-if="replyingTo === reply.id" class="reply-form">
            <textarea
              v-model="replyContent"
              class="reply-input"
              placeholder="回复评论..."
              rows="2"
            ></textarea>
            <div class="reply-actions">
              <button class="btn btn-outline" @click="cancelReply">取消</button>
              <button 
                class="btn btn-primary" 
                :disabled="!replyContent.trim() || submitting"
                @click="submitReply(reply.id)"
              >
                {{ submitting ? '发布中...' : '回复' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import { useSignalStore } from '@/stores/signal'
import type { SignalReply } from '@/types'

dayjs.extend(relativeTime)

const props = defineProps<{
  signalId: number
}>()

const signalStore = useSignalStore()

const replies = ref<SignalReply[]>([])
const newComment = ref('')
const replyContent = ref('')
const replyingTo = ref<number | null>(null)
const loading = ref(false)
const submitting = ref(false)

onMounted(() => {
  fetchReplies()
})

async function fetchReplies() {
  loading.value = true
  try {
    await signalStore.fetchReplies(props.signalId)
    replies.value = signalStore.replies
  } finally {
    loading.value = false
  }
}

async function submitComment() {
  if (!newComment.value.trim() || submitting.value) return
  
  submitting.value = true
  try {
    await signalStore.addReply(props.signalId, newComment.value.trim())
    replies.value = signalStore.replies
    newComment.value = ''
  } finally {
    submitting.value = false
  }
}

async function submitReply(parentId: number) {
  if (!replyContent.value.trim() || submitting.value) return
  
  submitting.value = true
  try {
    await signalStore.addReply(props.signalId, replyContent.value.trim(), parentId)
    replies.value = signalStore.replies
    replyContent.value = ''
    replyingTo.value = null
  } finally {
    submitting.value = false
  }
}

async function handleLike(reply: SignalReply) {
  try {
    await signalStore.likeReply(props.signalId, reply.id)
    const target = replies.value.find(r => r.id === reply.id)
    if (target) {
      target.is_liked = !target.is_liked
      target.likes = (target.likes || 0) + (target.is_liked ? 1 : -1)
    }
  } catch (e) {
    console.error('点赞失败', e)
  }
}

function replyTo(reply: SignalReply) {
  replyingTo.value = reply.id
  replyContent.value = `@${reply.user_name} `
}

function cancelReply() {
  replyingTo.value = null
  replyContent.value = ''
}

function formatTime(date: string | undefined) {
  if (!date) return ''
  return dayjs(date).fromNow()
}
</script>

<style scoped>
.comment-section {
  margin-top: 32px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 20px 0;
}

.comment-form {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 24px;
}

.comment-input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  transition: all 0.2s;
  box-sizing: border-box;
}

.comment-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.hint {
  font-size: 12px;
  color: var(--text-muted);
}

.btn {
  padding: 8px 20px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--accent-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-hover);
}

.btn-outline {
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-outline:hover {
  background: var(--bg-secondary);
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p,
.empty-text {
  color: var(--text-muted);
  font-size: 14px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.comment-item {
  display: flex;
  gap: 12px;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.comment-content {
  flex: 1;
  min-width: 0;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.comment-author {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
}

.comment-time {
  font-size: 12px;
  color: var(--text-muted);
}

.comment-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 8px 0;
  word-wrap: break-word;
}

.comment-actions {
  display: flex;
  gap: 16px;
}

.action-btn {
  padding: 4px 8px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 13px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.action-btn.liked {
  color: var(--accent-color);
}

.reply-form {
  margin-top: 12px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.reply-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 13px;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
  margin-bottom: 8px;
}

.reply-input:focus {
  outline: none;
  border-color: var(--accent-color);
}

.reply-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
