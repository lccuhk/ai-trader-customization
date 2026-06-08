<template>
  <div class="signal-list">
    <div class="list-header">
      <h2 class="list-title">{{ title }}</h2>
      <div class="list-filters">
        <select v-model="selectedType" class="filter-select" @change="handleFilterChange">
          <option value="">全部类型</option>
          <option value="long">做多</option>
          <option value="short">做空</option>
          <option value="info">资讯</option>
          <option value="alert">预警</option>
          <option value="analysis">分析</option>
        </select>
        <select v-model="selectedMarket" class="filter-select" @change="handleFilterChange">
          <option value="">全部市场</option>
          <option value="crypto">加密货币</option>
          <option value="stock">股票</option>
          <option value="forex">外汇</option>
          <option value="futures">期货</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p class="error-text">❌ {{ error }}</p>
      <button class="btn btn-primary" @click="retry">重试</button>
    </div>

    <div v-else-if="signals.length === 0" class="empty-state">
      <p class="empty-text">📭 暂无信号</p>
    </div>

    <div v-else class="cards-container">
      <SignalCard 
        v-for="signal in signals" 
        :key="signal.id" 
        :signal="signal"
        @follow="handleFollow"
      />
    </div>

    <div v-if="hasMore && !loading" class="load-more">
      <button class="btn btn-outline" @click="loadMore">加载更多</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSignalStore } from '@/stores/signal'
import SignalCard from './SignalCard.vue'
import type { Signal } from '@/types'

const props = withDefaults(defineProps<{
  title?: string
  autoLoad?: boolean
}>(), {
  title: '信号广场',
  autoLoad: true
})

const signalStore = useSignalStore()

const signals = ref<Signal[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const selectedType = ref('')
const selectedMarket = ref('')
const hasMore = ref(true)
const limit = ref(20)

onMounted(() => {
  if (props.autoLoad) {
    fetchSignals()
  }
})

async function fetchSignals() {
  loading.value = true
  error.value = null
  try {
    await signalStore.fetchSignals(limit.value, selectedType.value, selectedMarket.value)
    signals.value = signalStore.signals
    hasMore.value = signals.value.length >= limit.value
  } catch (e: any) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function handleFilterChange() {
  limit.value = 20
  fetchSignals()
}

function loadMore() {
  limit.value += 20
  fetchSignals()
}

function retry() {
  fetchSignals()
}

function handleFollow(signalId: number) {
  const signal = signals.value.find(s => s.id === signalId)
  if (signal) {
    signal.is_following = !signal.is_following
  }
}
</script>

<style scoped>
/* IT 极简风格信号列表 */
.signal-list {
  max-width: 900px;
  margin: 0 auto;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--border-color);
}

.list-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.list-title::before {
  content: '> ';
  color: var(--success-color);
}

.list-filters {
  display: flex;
  gap: 8px;
}

.filter-select {
  padding: 6px 12px;
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.1s ease;
  font-family: inherit;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  outline: none;
}

.filter-select:hover {
  border-color: var(--success-color);
}

.filter-select:focus {
  border-color: var(--success-color);
  box-shadow: 2px 2px 0 var(--success-color);
}

.cards-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 20px;
  text-align: center;
  border: 2px dashed var(--border-light);
}

/* 终端风格加载动画 */
.spinner {
  width: 8px;
  height: 8px;
  background: var(--success-color);
  animation: blink 0.5s step-end infinite;
  margin-bottom: 16px;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.loading-state p,
.empty-text {
  color: var(--text-muted);
  font-size: 13px;
  font-family: inherit;
}

.loading-state p::before {
  content: '// ';
  color: var(--success-color);
}

.empty-text::before {
  content: '// ';
  color: var(--text-muted);
}

.error-text {
  color: var(--danger-color);
  font-size: 13px;
  margin-bottom: 16px;
  font-weight: 500;
}

.error-text::before {
  content: 'ERROR: ';
  font-weight: 700;
}

.load-more {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.btn {
  padding: 8px 20px;
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
  border: 2px solid var(--border-color);
  transition: all 0.1s ease;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: inherit;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.btn-primary {
  background: var(--success-color);
  color: var(--bg-primary);
  border-color: var(--success-color);
}

.btn-primary:hover {
  background: var(--text-primary);
  border-color: var(--text-primary);
  color: var(--bg-primary);
}

.btn-outline {
  background: transparent;
  color: var(--text-primary);
  border: 2px solid var(--border-color);
}

.btn-outline:hover {
  background: var(--danger-color);
  border-color: var(--danger-color);
  color: var(--bg-primary);
}
</style>
