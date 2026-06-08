<template>
  <div class="history-view">
    <div class="page-header">
      <h1>📜 浏览历史</h1>
      <button v-if="historyStore.history.length > 0" class="btn btn-secondary" @click="historyStore.clearHistory">
        清空历史
      </button>
    </div>
    
    <div v-if="historyStore.history.length > 0" class="history-list">
      <div v-for="item in historyStore.history" :key="item.id" class="history-item">
        <div class="history-type-icon">
          {{ getTypeIcon(item.type) }}
        </div>
        <div class="history-content">
          <router-link :to="item.url" class="history-title">{{ item.title }}</router-link>
          <span class="history-time">{{ formatTime(item.timestamp) }}</span>
        </div>
        <button class="remove-btn" @click="historyStore.removeHistoryItem(item.id)">
          ✕
        </button>
      </div>
    </div>
    
    <div v-else class="empty-state">
      <div class="empty-icon">📄</div>
      <h3>还没有浏览记录</h3>
      <p>开始探索平台，你的浏览记录会显示在这里！</p>
      <router-link to="/" class="btn btn-primary">开始探索</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useHistoryStore } from '@/stores/history'

const historyStore = useHistoryStore()

function getTypeIcon(type: string) {
  const icons: Record<string, string> = {
    signal: '📈',
    market: '🌐',
    trading: '💹',
    ai: '🤖',
    portfolio: '💼',
    profile: '👤',
    notifications: '🔔'
  }
  return icons[type] || '📄'
}

function formatTime(timestamp: string) {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}
</script>

<style scoped>
.history-view {
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.2s;
}

.history-item:hover {
  border-color: var(--accent-color);
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);
}

.history-type-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.history-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.history-title {
  text-decoration: none;
  color: var(--text-primary);
  font-weight: 500;
  font-size: 15px;
  transition: color 0.2s;
}

.history-title:hover {
  color: var(--accent-color);
}

.history-time {
  color: var(--text-muted);
  font-size: 13px;
  flex-shrink: 0;
}

.remove-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.remove-btn:hover {
  background: var(--bg-secondary);
  color: #ef4444;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-state p {
  margin: 0 0 24px 0;
  font-size: 16px;
  color: var(--text-muted);
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  background: var(--accent-color);
  color: white;
}

.btn-primary:hover {
  background: var(--accent-hover);
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
}
</style>
