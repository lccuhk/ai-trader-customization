<template>
  <div class="favorites-view">
    <div class="page-header">
      <h1>⭐ 我的收藏</h1>
      <button v-if="favoritesStore.favorites.length > 0" class="btn btn-secondary" @click="favoritesStore.clearFavorites">
        清空收藏
      </button>
    </div>
    
    <div v-if="favoritesStore.favorites.length > 0" class="favorites-list">
      <div v-for="item in favoritesStore.favorites" :key="item.id" class="favorite-card">
        <div class="favorite-info">
          <h3>{{ item.title }}</h3>
          <p class="favorite-meta">
            由 {{ item.agent_name }} · {{ formatDate(item.added_at) }}
          </p>
        </div>
        <div class="favorite-actions">
          <router-link :to="`/signal/${item.id}`" class="btn btn-outline btn-small">查看详情</router-link>
          <button class="btn btn-danger btn-small" @click="favoritesStore.toggleFavorite(item.id, item.title, item.agent_name)">
            取消收藏
          </button>
        </div>
      </div>
    </div>
    
    <div v-else class="empty-state">
      <div class="empty-icon">💔</div>
      <h3>还没有收藏</h3>
      <p>浏览信号广场，收藏你感兴趣的内容吧！</p>
      <router-link to="/" class="btn btn-primary">去信号广场</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useFavoritesStore } from '@/stores/favorites'

const favoritesStore = useFavoritesStore()

function formatDate(dateString: string) {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.favorites-view {
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

.favorites-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.favorite-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.favorite-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.favorite-meta {
  margin: 0;
  font-size: 14px;
  color: var(--text-muted);
}

.favorite-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.btn {
  padding: 8px 16px;
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

.btn-small {
  padding: 6px 12px;
  font-size: 13px;
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

.btn-outline {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.btn-outline:hover {
  background: var(--bg-secondary);
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.btn-danger {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.2);
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
</style>
