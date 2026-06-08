<template>
  <div class="notifications-view">
    <div class="view-header">
      <div class="header-content">
        <h1>通知中心</h1>
        <p>查看所有系统通知和消息</p>
      </div>
      <button 
        v-if="notificationStore.unreadCount > 0"
        class="btn btn-outline"
        @click="markAllAsRead"
      >
        全部标为已读
      </button>
    </div>

    <div class="filter-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.key"
        class="tab-btn"
        :class="{ active: activeFilter === tab.key }"
        @click="activeFilter = tab.key"
      >
        {{ tab.label }}
        <span v-if="tab.key === 'unread' && notificationStore.unreadCount > 0" class="tab-badge">
          {{ notificationStore.unreadCount }}
        </span>
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="filteredNotifications.length === 0" class="empty-state">
      <div class="empty-icon">🔔</div>
      <p class="empty-title">暂无通知</p>
      <p class="empty-text">{{ activeFilter === 'unread' ? '没有未读通知' : '还没有任何通知' }}</p>
    </div>

    <div v-else class="notifications-list">
      <div 
        v-for="notification in filteredNotifications" 
        :key="notification.id" 
        class="notification-item"
        :class="{ unread: !notification.is_read }"
        @click="handleNotificationClick(notification)"
      >
        <div class="notification-icon" :class="notification.type || notification.notification_type">
          {{ getTypeIcon(notification.type || notification.notification_type) }}
        </div>
        <div class="notification-content">
          <div class="notification-header">
            <span class="notification-title">{{ notification.title }}</span>
            <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
          </div>
          <p class="notification-message">{{ notification.message }}</p>
          <div class="notification-actions" v-if="!notification.is_read">
            <button class="action-link" @click.stop="markAsRead(notification.id)">
              标为已读
            </button>
          </div>
        </div>
        <div v-if="!notification.is_read" class="unread-dot"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import { useNotificationStore } from '@/stores/notification'
import type { Notification } from '@/types'

dayjs.extend(relativeTime)

const notificationStore = useNotificationStore()

const activeFilter = ref('all')
const loading = ref(false)

const tabs = [
  { key: 'all', label: '全部' },
  { key: 'unread', label: '未读' }
]

const filteredNotifications = computed(() => {
  if (activeFilter.value === 'unread') {
    return notificationStore.notifications.filter(n => !n.is_read)
  }
  return notificationStore.notifications
})

onMounted(() => {
  fetchNotifications()
})

async function fetchNotifications() {
  loading.value = true
  try {
    await notificationStore.fetchNotifications(50)
  } finally {
    loading.value = false
  }
}

async function markAsRead(id: number) {
  try {
    await notificationStore.markAsRead(id)
  } catch (e) {
    console.error('标记已读失败', e)
  }
}

async function markAllAsRead() {
  try {
    await notificationStore.markAllAsRead()
  } catch (e) {
    console.error('全部标记已读失败', e)
  }
}

function handleNotificationClick(notification: Notification) {
  if (!notification.is_read) {
    markAsRead(notification.id)
  }
  if (notification.related_url) {
    window.open(notification.related_url, '_blank')
  }
}

function getTypeIcon(type: string | undefined) {
  const icons: Record<string, string> = {
    'signal': '📈',
    'comment': '💬',
    'like': '👍',
    'follow': '⭐',
    'system': '🔔',
    'alert': '⚠️',
    'news': '📰'
  }
  return icons[type || 'system'] || '🔔'
}

function formatTime(date: string | undefined) {
  if (!date) return ''
  return dayjs(date).fromNow()
}
</script>

<style scoped>
.notifications-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 20px;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-content h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.header-content p {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

.btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
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

.filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  background: var(--bg-secondary);
  padding: 6px;
  border-radius: 12px;
  width: fit-content;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--accent-color);
  color: white;
}

.tab-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: var(--text-muted);
  font-size: 14px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.empty-text {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.notification-item:hover {
  border-color: var(--accent-color);
  background: var(--bg-secondary);
}

.notification-item.unread {
  background: rgba(99, 102, 241, 0.05);
  border-color: rgba(99, 102, 241, 0.2);
}

.notification-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.notification-icon.signal {
  background: rgba(99, 102, 241, 0.1);
}

.notification-icon.comment {
  background: rgba(59, 130, 246, 0.1);
}

.notification-icon.like {
  background: rgba(236, 72, 153, 0.1);
}

.notification-icon.follow {
  background: rgba(245, 158, 11, 0.1);
}

.notification-icon.system {
  background: rgba(107, 114, 128, 0.1);
}

.notification-icon.alert {
  background: rgba(239, 68, 68, 0.1);
}

.notification-icon.news {
  background: rgba(34, 197, 94, 0.1);
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 4px;
}

.notification-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
}

.notification-time {
  font-size: 12px;
  color: var(--text-muted);
  flex-shrink: 0;
}

.notification-message {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 8px 0;
  line-height: 1.5;
}

.notification-actions {
  display: flex;
  gap: 12px;
}

.action-link {
  background: none;
  border: none;
  color: var(--accent-color);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  padding: 0;
}

.action-link:hover {
  text-decoration: underline;
}

.unread-dot {
  width: 8px;
  height: 8px;
  background: var(--accent-color);
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 8px;
}

@media (max-width: 768px) {
  .view-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-content h1 {
    font-size: 24px;
  }
  
  .notification-item {
    padding: 12px;
  }
  
  .notification-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
