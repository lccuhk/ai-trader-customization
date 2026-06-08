<template>
  <div class="messages-view">
    <div class="messages-header">
      <h1>消息</h1>
    </div>

    <div class="messages-content">
      <div class="conversations-list">
        <div v-if="socialStore.loading" class="loading">
          加载中...
        </div>
        <div v-else-if="socialStore.conversations.length === 0" class="empty-state">
          暂无会话
        </div>
        <div 
          v-for="conv in socialStore.conversations" 
          :key="conv.user.id" 
          class="conversation-item"
          :class="{ active: selectedUserId === conv.user.id }"
          @click="selectConversation(conv.user.id)"
        >
          <div class="avatar">
            {{ conv.user.display_name?.charAt(0) || conv.user.username?.charAt(0) }}
          </div>
          <div class="conv-info">
            <div class="conv-header">
              <span class="name">{{ conv.user.display_name || conv.user.username }}</span>
              <span class="time" v-if="conv.last_message">
                {{ formatTime(conv.last_message.created_at) }}
              </span>
            </div>
            <div class="conv-preview">
              <span v-if="conv.last_message?.is_sent">你: </span>
              {{ conv.last_message?.content || '暂无消息' }}
            </div>
          </div>
          <div class="unread-badge" v-if="conv.unread_count > 0">
            {{ conv.unread_count }}
          </div>
        </div>
      </div>

      <div class="chat-area" v-if="selectedUserId">
        <router-view />
      </div>
      <div v-else class="chat-placeholder">
        <div class="placeholder-content">
          <div class="icon">💬</div>
          <p>选择一个会话开始聊天</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSocialStore } from '@/stores/social'

const route = useRoute()
const router = useRouter()
const socialStore = useSocialStore()

const selectedUserId = ref<number | null>(null)

function selectConversation(userId: number) {
  selectedUserId.value = userId
  router.push(`/messages/${userId}`)
}

function formatTime(time: string) {
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

onMounted(async () => {
  await socialStore.loadConversations()
  
  const userId = route.params.userId
  if (userId) {
    selectedUserId.value = parseInt(userId as string)
  }
})

watch(() => route.params.userId, (userId) => {
  if (userId) {
    selectedUserId.value = parseInt(userId as string)
  } else {
    selectedUserId.value = null
  }
})
</script>

<style scoped>
.messages-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  height: calc(100vh - 80px);
  display: flex;
  flex-direction: column;
}

.messages-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 20px 0;
}

.messages-content {
  display: flex;
  flex: 1;
  gap: 20px;
  overflow: hidden;
}

.conversations-list {
  width: 320px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow-y: auto;
  flex-shrink: 0;
}

.loading, .empty-state {
  padding: 40px;
  text-align: center;
  color: var(--text-secondary);
}

.conversation-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  cursor: pointer;
  border-bottom: 1px solid var(--border-color);
  transition: all 0.2s;
  align-items: center;
}

.conversation-item:hover {
  background: var(--bg-secondary);
}

.conversation-item.active {
  background: var(--bg-secondary);
  border-left: 3px solid var(--primary);
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}

.conv-info {
  flex: 1;
  min-width: 0;
}

.conv-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.name {
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.time {
  font-size: 12px;
  color: var(--text-secondary);
  flex-shrink: 0;
  margin-left: 8px;
}

.conv-preview {
  font-size: 13px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.unread-badge {
  background: var(--primary);
  color: white;
  font-size: 12px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
  flex-shrink: 0;
}

.chat-area {
  flex: 1;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.chat-placeholder {
  flex: 1;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-content {
  text-align: center;
  color: var(--text-secondary);
}

.placeholder-content .icon {
  font-size: 48px;
  margin-bottom: 16px;
}
</style>
