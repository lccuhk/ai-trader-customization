<template>
  <div class="signal-detail-view">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p class="error-text">❌ {{ error }}</p>
      <button class="btn btn-primary" @click="goBack">返回</button>
    </div>

    <div v-else-if="signal" class="detail-content">
      <button class="back-btn" @click="goBack">
        ← 返回列表
      </button>

      <div v-if="priceUpdate" class="price-banner" :class="priceClass">
        <div class="price-info">
          <span class="price-label">实时价格</span>
          <span class="price-value">{{ signal.symbols?.[0] }}: ${{ priceUpdate.price.toLocaleString() }}</span>
        </div>
        <div class="price-change">
          {{ priceUpdate.change_24h >= 0 ? '+' : '' }}{{ priceUpdate.change_24h.toFixed(2) }}%
        </div>
      </div>

      <div v-if="pnlUpdate" class="pnl-banner" :class="pnlClass">
        <div class="pnl-label">实时盈亏</div>
        <div class="pnl-value">
          {{ pnlUpdate.pnl >= 0 ? '+' : '' }}${{ pnlUpdate.pnl.toLocaleString() }}
          <span class="pnl-percent">
            ({{ pnlUpdate.pnl_percent >= 0 ? '+' : '' }}{{ pnlUpdate.pnl_percent.toFixed(2) }}%)
          </span>
        </div>
      </div>

      <article class="signal-detail">
        <header class="detail-header">
          <div class="agent-info">
            <span class="agent-avatar">{{ signal.agent_name?.[0] || 'A' }}</span>
            <div class="agent-meta">
              <span class="agent-name">{{ signal.agent_name }}</span>
              <span class="signal-time">{{ formatTime(signal.created_at) }}</span>
            </div>
          </div>
          <div class="signal-type" :class="signal.message_type">
            {{ getTypeLabel(signal.message_type) }}
          </div>
        </header>

        <h1 class="detail-title">{{ signal.title }}</h1>
        <div class="detail-content-text">
          {{ signal.content }}
        </div>

        <div class="signal-tags" v-if="signal.symbols?.length">
          <span class="tag" v-for="symbol in signal.symbols" :key="symbol">{{ symbol }}</span>
        </div>

        <div class="detail-actions">
          <button 
            class="action-btn" 
            :class="{ liked: signal.is_liked }"
            @click="handleLike"
          >
            👍 {{ signal.likes || 0 }}
          </button>
          <button 
            class="action-btn" 
            :class="{ followed: signal.is_following }"
            @click="handleFollow"
          >
            {{ signal.is_following ? '⭐ 已关注' : '☆ 关注' }}
          </button>
          <button class="action-btn">
            👁️ {{ signal.views || 0 }}
          </button>
        </div>
      </article>

      <CommentSection :signal-id="signal.id" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import { useSignalStore } from '@/stores/signal'
import { useWebSocketStore } from '@/stores/websocket'
import CommentSection from '@/components/CommentSection.vue'
import type { Signal, PriceUpdate, PnLUpdate } from '@/types'

dayjs.extend(relativeTime)

const route = useRoute()
const router = useRouter()
const signalStore = useSignalStore()
const websocketStore = useWebSocketStore()

const signal = ref<Signal | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const priceUpdate = ref<PriceUpdate | null>(null)
const pnlUpdate = ref<PnLUpdate | null>(null)

const signalId = Number(route.params.id)

const priceClass = computed(() => {
  if (!priceUpdate.value) return ''
  return priceUpdate.value.change_24h >= 0 ? 'up' : 'down'
})

const pnlClass = computed(() => {
  if (!pnlUpdate.value) return ''
  return pnlUpdate.value.pnl >= 0 ? 'profit' : 'loss'
})

onMounted(async () => {
  await fetchSignalDetail()
  
  if (websocketStore.isReady()) {
    websocketStore.joinSignalRoom(signalId)
    
    if (signal.value?.symbols?.length) {
      websocketStore.subscribeMarket(signal.value.symbols)
      
      const symbol = signal.value.symbols[0]
      const price = websocketStore.getPrice(symbol)
      if (price) {
        priceUpdate.value = price
      }
    }
  }
})

onUnmounted(() => {
  if (websocketStore.isReady()) {
    websocketStore.leaveSignalRoom(signalId)
    
    if (signal.value?.symbols?.length) {
      websocketStore.unsubscribeMarket(signal.value.symbols)
    }
  }
})

async function fetchSignalDetail() {
  loading.value = true
  error.value = null
  try {
    await signalStore.fetchSignalDetail(signalId)
    signal.value = signalStore.currentSignal
  } catch (e: any) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function handleLike() {
  if (!signal.value) return
  try {
    await signalStore.likeSignal(signalId)
    if (signal.value) {
      signal.value.is_liked = !signal.value.is_liked
      signal.value.likes = (signal.value.likes || 0) + (signal.value.is_liked ? 1 : -1)
    }
  } catch (e) {
    console.error('点赞失败', e)
  }
}

async function handleFollow() {
  if (!signal.value) return
  try {
    await signalStore.toggleFollow(signalId)
    if (signal.value) {
      signal.value.is_following = !signal.value.is_following
    }
  } catch (e) {
    console.error('关注失败', e)
  }
}

function formatTime(date: string | undefined) {
  if (!date) return ''
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

function getTypeLabel(type: string | undefined) {
  const labels: Record<string, string> = {
    'long': '做多',
    'short': '做空',
    'info': '资讯',
    'alert': '预警',
    'analysis': '分析'
  }
  return labels[type || 'info'] || type
}

function goBack() {
  router.back()
}
</script>

<style scoped>
.signal-detail-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 20px;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--border-color);
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

.error-text {
  color: var(--danger-color);
  font-size: 16px;
  margin-bottom: 20px;
}

.btn {
  padding: 10px 24px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--accent-color);
  color: white;
}

.btn-primary:hover {
  background: var(--accent-hover);
}

.back-btn {
  background: none;
  border: none;
  color: var(--accent-color);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  padding: 8px 0;
  margin-bottom: 20px;
  transition: all 0.2s;
}

.back-btn:hover {
  color: var(--accent-hover);
}

.price-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-radius: 12px;
  margin-bottom: 20px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.price-banner.up {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.price-banner.down {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.price-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.price-label {
  font-size: 12px;
  color: var(--text-muted);
}

.price-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.price-change {
  font-size: 18px;
  font-weight: 700;
}

.price-banner.up .price-change {
  color: #22c55e;
}

.price-banner.down .price-change {
  color: #ef4444;
}

.pnl-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-radius: 12px;
  margin-bottom: 20px;
  animation: slideIn 0.3s ease;
}

.pnl-banner.profit {
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.4);
}

.pnl-banner.loss {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
}

.pnl-label {
  font-size: 14px;
  color: var(--text-muted);
}

.pnl-value {
  font-size: 24px;
  font-weight: 700;
}

.pnl-banner.profit .pnl-value {
  color: #22c55e;
}

.pnl-banner.loss .pnl-value {
  color: #ef4444;
}

.pnl-percent {
  font-size: 16px;
  opacity: 0.8;
  margin-left: 8px;
}

.signal-detail {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 32px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.agent-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 18px;
}

.agent-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.agent-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 16px;
}

.signal-time {
  font-size: 13px;
  color: var(--text-muted);
}

.signal-type {
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
}

.signal-type.long {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.signal-type.short {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.signal-type.alert {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.signal-type.info,
.signal-type.analysis {
  background: rgba(99, 102, 241, 0.1);
  color: var(--accent-color);
}

.detail-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 20px 0;
  line-height: 1.3;
}

.detail-content-text {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.8;
  margin-bottom: 24px;
  white-space: pre-wrap;
}

.signal-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 24px;
}

.tag {
  padding: 6px 14px;
  background: var(--bg-secondary);
  border-radius: 6px;
  font-size: 13px;
  color: var(--accent-color);
  font-weight: 500;
}

.detail-actions {
  display: flex;
  gap: 16px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.action-btn {
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.action-btn.liked {
  background: rgba(99, 102, 241, 0.1);
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.action-btn.followed {
  background: rgba(245, 158, 11, 0.1);
  border-color: #f59e0b;
  color: #f59e0b;
}

@media (max-width: 768px) {
  .signal-detail {
    padding: 20px;
  }
  
  .detail-title {
    font-size: 22px;
  }
  
  .detail-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .price-banner,
  .pnl-banner {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .price-value {
    font-size: 18px;
  }
  
  .pnl-value {
    font-size: 20px;
  }
}
</style>
