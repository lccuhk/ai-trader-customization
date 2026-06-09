<template>
  <div class="market-view">
    <div class="view-header">
      <h1>市场动态</h1>
      <p>实时追踪全球金融市场动态</p>
    </div>

    <div class="market-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.key"
        class="tab-btn"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p class="error-text">❌ {{ error }}</p>
      <button class="btn btn-primary" @click="retry">重试</button>
    </div>

    <div v-else class="market-content">
      <div v-if="activeTab === 'news'" class="news-section">
        <div v-if="news.length === 0" class="empty-state">
          <p class="empty-text">📰 暂无市场新闻</p>
        </div>
        <div v-else class="news-list">
          <div v-for="item in news" :key="item.id" class="news-card">
            <div class="news-header">
              <span class="news-source">{{ item.source }}</span>
              <span class="news-time">{{ formatTime(item.published_at) }}</span>
            </div>
            <h3 class="news-title">{{ item.title }}</h3>
            <p class="news-summary">{{ item.summary }}</p>
            <div class="news-tags" v-if="item.symbols?.length">
              <span class="tag" v-for="symbol in item.symbols" :key="symbol">{{ symbol }}</span>
            </div>
            <a v-if="item.url" :href="item.url" target="_blank" class="news-link">
              阅读原文 →
            </a>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'events'" class="events-section">
        <div v-if="events.length === 0" class="empty-state">
          <p class="empty-text">📅 暂无市场事件</p>
        </div>
        <div v-else class="events-list">
          <div v-for="event in events" :key="event.id" class="event-card">
            <div class="event-date">
              <span class="event-day">{{ formatDate(event.event_date) }}</span>
              <span class="event-time">{{ formatTime(event.event_date) }}</span>
            </div>
            <div class="event-content">
              <h3 class="event-title">{{ event.title }}</h3>
              <p class="event-desc">{{ event.description }}</p>
              <div class="event-meta">
                <span class="event-impact" :class="event.impact">
                  {{ getImpactLabel(event.impact) }}
                </span>
                <span class="event-market">{{ event.symbol }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'indicators'" class="indicators-section">
        <div v-if="indicators.length === 0" class="empty-state">
          <p class="empty-text">📊 暂无经济指标</p>
        </div>
        <div v-else class="indicators-grid">
          <div v-for="indicator in indicators" :key="indicator.id" class="indicator-card">
            <div class="indicator-header">
              <span class="indicator-name">{{ indicator.name }}</span>
              <span class="indicator-country">{{ indicator.country }}</span>
            </div>
            <div class="indicator-values">
              <div class="value-item">
                <span class="value-label">实际值</span>
                <span class="value-actual">{{ indicator.value || '--' }}</span>
              </div>
              <div class="value-item">
                <span class="value-label">预期值</span>
                <span class="value-expected">{{ indicator.forecast_value || '--' }}</span>
              </div>
              <div class="value-item">
                <span class="value-label">前值</span>
                <span class="value-previous">{{ indicator.previous_value || '--' }}</span>
              </div>
            </div>
            <div class="indicator-footer">
              <span class="indicator-date">{{ formatDate(indicator.release_date) }}</span>
              <span class="indicator-impact" :class="indicator.impact">
                {{ getImpactLabel(indicator.impact) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import dayjs from 'dayjs'
import { useSignalStore } from '@/stores/signal'
import type { MarketNews, MarketEvent, EconomicIndicator } from '@/types'

const signalStore = useSignalStore()

const activeTab = ref('news')
const loading = ref(false)
const error = ref<string | null>(null)

const news = ref<MarketNews[]>([])
const events = ref<MarketEvent[]>([])
const indicators = ref<EconomicIndicator[]>([])

const tabs = [
  { key: 'news', label: '市场新闻' },
  { key: 'events', label: '财经事件' },
  { key: 'indicators', label: '经济指标' }
]

onMounted(() => {
  fetchData()
})

watch(activeTab, () => {
  fetchData()
})

async function fetchData() {
  loading.value = true
  error.value = null
  try {
    if (activeTab.value === 'news') {
      const response = await signalStore.fetchMarketNews()
      news.value = response
    } else if (activeTab.value === 'events') {
      const response = await signalStore.fetchMarketEvents()
      events.value = response
    } else if (activeTab.value === 'indicators') {
      const response = await signalStore.fetchEconomicIndicators()
      indicators.value = response
    }
  } catch (e: any) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function retry() {
  fetchData()
}

function formatTime(date: string | undefined) {
  if (!date) return ''
  return dayjs(date).format('HH:mm')
}

function formatDate(date: string | undefined) {
  if (!date) return ''
  return dayjs(date).format('MM-DD')
}

function getImpactLabel(level: string | undefined) {
  const labels: Record<string, string> = {
    'low': '低影响',
    'medium': '中影响',
    'high': '高影响'
  }
  return labels[level || 'medium'] || level
}
</script>

<style scoped>
.market-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 32px 20px;
}

.view-header {
  text-align: center;
  margin-bottom: 32px;
}

.view-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.view-header p {
  font-size: 16px;
  color: var(--text-muted);
  margin: 0;
}

.market-tabs {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 32px;
  background: var(--bg-secondary);
  padding: 6px;
  border-radius: 12px;
  width: fit-content;
  margin-left: auto;
  margin-right: auto;
}

.tab-btn {
  padding: 10px 24px;
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

.loading-state,
.error-state,
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

.loading-state p,
.empty-text {
  color: var(--text-muted);
  font-size: 14px;
}

.error-text {
  color: var(--danger-color);
  font-size: 14px;
  margin-bottom: 16px;
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

.news-list,
.events-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.news-card,
.event-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s;
}

.news-card:hover,
.event-card:hover {
  border-color: var(--accent-color);
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.news-source {
  font-size: 12px;
  color: var(--accent-color);
  font-weight: 500;
}

.news-time {
  font-size: 12px;
  color: var(--text-muted);
}

.news-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.news-summary {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 12px 0;
}

.news-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.tag {
  padding: 4px 10px;
  background: var(--bg-secondary);
  border-radius: 4px;
  font-size: 12px;
  color: var(--accent-color);
  font-weight: 500;
}

.news-link {
  font-size: 14px;
  color: var(--accent-color);
  text-decoration: none;
  font-weight: 500;
}

.news-link:hover {
  text-decoration: underline;
}

.event-card {
  display: flex;
  gap: 20px;
}

.event-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 60px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
  height: fit-content;
}

.event-day {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.event-time {
  font-size: 12px;
  color: var(--text-muted);
}

.event-content {
  flex: 1;
}

.event-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.event-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.event-meta {
  display: flex;
  gap: 12px;
}

.event-impact,
.indicator-impact {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.event-impact.high,
.indicator-impact.high {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.event-impact.medium,
.indicator-impact.medium {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.event-impact.low,
.indicator-impact.low {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.event-market {
  font-size: 12px;
  color: var(--text-muted);
}

.indicators-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.indicator-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s;
}

.indicator-card:hover {
  border-color: var(--accent-color);
}

.indicator-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.indicator-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.indicator-country {
  font-size: 12px;
  color: var(--text-muted);
}

.indicator-values {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.value-item {
  text-align: center;
}

.value-label {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.value-actual,
.value-expected,
.value-previous {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.indicator-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.indicator-date {
  font-size: 12px;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .view-header h1 {
    font-size: 24px;
  }
  
  .market-tabs {
    width: 100%;
    overflow-x: auto;
  }
  
  .tab-btn {
    padding: 8px 16px;
    font-size: 13px;
    white-space: nowrap;
  }
  
  .event-card {
    flex-direction: column;
  }
  
  .event-date {
    flex-direction: row;
    justify-content: center;
    gap: 12px;
    width: 100%;
  }
  
  .indicators-grid {
    grid-template-columns: 1fr;
  }
}
</style>
