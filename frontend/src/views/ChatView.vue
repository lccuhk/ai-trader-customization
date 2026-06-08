<template>
  <div class="chat-view">
    <div class="chat-header">
      <div class="user-info" v-if="otherUser">
        <div class="avatar">
          {{ otherUser.display_name?.charAt(0) || otherUser.username?.charAt(0) }}
        </div>
        <div>
          <div class="name">{{ otherUser.display_name || otherUser.username }}</div>
          <div class="username">@{{ otherUser.username }}</div>
        </div>
      </div>
    </div>

    <div class="messages-container" ref="messagesContainer">
      <div v-if="socialStore.loading" class="loading">
        加载中...
      </div>
      <div v-else-if="socialStore.messages.length === 0" class="empty-state">
        暂无消息，开始聊天吧
      </div>
      <div 
        v-for="msg in socialStore.messages" 
        :key="msg.id" 
        class="message-item"
        :class="{ sent: msg.sender_id === currentUserId }"
      >
        <div class="message-avatar" v-if="msg.sender_id !== currentUserId">
          {{ msg.sender?.display_name?.charAt(0) || msg.sender?.username?.charAt(0) }}
        </div>
        <div class="message-content">
          <div class="message-bubble">
            {{ msg.content }}
          </div>
          <div class="message-time">
            {{ formatTime(msg.created_at) }}
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input">
      <input 
        type="text" 
        v-model="messageText" 
        placeholder="输入消息..."
        @keyup.enter="sendMessage"
      />
      <button @click="sendMessage" :disabled="!messageText.trim()">
        发送
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useSocialStore } from '@/stores/social'
import { useUserStore } from '@/stores/user'
import { useToast } from '@/composables/useToast'
import type { User } from '@/types'

const route = useRoute()
const socialStore = useSocialStore()
const userStore = useUserStore()
const toast = useToast()

const messageText = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const otherUser = ref<User | null>(null)

const currentUserId = computed(() => userStore.user?.id)

async function loadMessages() {
  const userId = parseInt(route.params.userId as string)
  if (userId) {
    await socialStore.loadMessages(userId)
    
    const response = await socialStore.loadUserProfile(userId)
    if (response.success && response.data) {
      otherUser.value = response.data.user
    }
    
    await nextTick()
    scrollToBottom()
  }
}

async function sendMessage() {
  if (!messageText.value.trim() || !otherUser.value) return

  try {
    await socialStore.sendMessage(otherUser.value.id, messageText.value.trim())
    messageText.value = ''
    await nextTick()
    scrollToBottom()
  } catch (e: any) {
    toast.error(e.message || '发送失败')
  }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function formatTime(time: string) {
  return new Date(time).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadMessages()
})

watch(() => route.params.userId, () => {
  loadMessages()
})
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: white;
}

.name {
  font-weight: 600;
  color: var(--text-primary);
}

.username {
  font-size: 13px;
  color: var(--text-secondary);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.loading, .empty-state {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.message-item {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-item.sent {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
}

.message-item.sent .message-content {
  text-align: right;
}

.message-bubble {
  display: inline-block;
  padding: 12px 16px;
  border-radius: 16px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  word-break: break-word;
}

.message-item.sent .message-bubble {
  background: var(--primary);
  color: white;
}

.message-time {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.chat-input {
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  gap: 12px;
}

.chat-input input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 24px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
}

.chat-input input:focus {
  outline: none;
  border-color: var(--primary);
}

.chat-input button {
  padding: 12px 24px;
  border: none;
  background: var(--primary);
  color: white;
  border-radius: 24px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.chat-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
