<template>
  <div class="market-events">
    <div class="page-header">
      <h1 class="page-title">> MARKET_EVENTS.EXE</h1>
      <div class="status-bar">
        <span class="status-indicator online">● EVENTS_LIVE</span>
        <span class="status-item">UPCOMING: {{ upcomingCount }}</span>
      </div>
    </div>

    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">TIMEFRAME:</span>
        <button class="filter-btn" :class="{ active: activeTimeframe === 'today' }" @click="activeTimeframe = 'today'">TODAY</button>
        <button class="filter-btn" :class="{ active: activeTimeframe === 'week' }" @click="activeTimeframe = 'week'">THIS_WEEK</button>
        <button class="filter-btn" :class="{ active: activeTimeframe === 'month' }" @click="activeTimeframe = 'month'">THIS_MONTH</button>
      </div>
      <div class="filter-group">
        <span class="filter-label">IMPORTANCE:</span>
        <button class="filter-btn" :class="{ active: activeImportance === 'all' }" @click="activeImportance = 'all'">ALL</button>
        <button class="filter-btn" :class="{ active: activeImportance === 'high' }" @click="activeImportance = 'high'">HIGH</button>
        <button class="filter-btn" :class="{ active: activeImportance === 'medium' }" @click="activeImportance = 'medium'">MEDIUM</button>
      </div>
    </div>

    <div class="events-timeline">
      <div class="event-item" v-for="event in filteredEvents" :key="event.id" :class="{ 'event-past': event.isPast, 'event-ongoing': event.isOngoing }">
        <div class="event-time">
          <span class="event-date">{{ event.date }}</span>
          <span class="event-time-text">{{ event.time }}</span>
          <span class="event-status" v-if="event.isOngoing">● LIVE</span>
        </div>
        <div class="event-content">
          <div class="event-header">
            <span class="event-importance" :class="event.importance">{{ event.importance.toUpperCase() }}</span>
            <span class="event-category">{{ event.category }}</span>
          </div>
          <h3 class="event-title">{{ event.title }}</h3>
          <p class="event-desc">{{ event.description }}</p>
          <div class="event-meta">
            <span class="event-meta-item">
              <span class="meta-label">EXPECTED:</span>
              <span class="meta-value">{{ event.expected }}</span>
            </span>
            <span class="event-meta-item" v-if="event.previous">
              <span class="meta-label">PREVIOUS:</span>
              <span class="meta-value">{{ event.previous }}</span>
            </span>
            <span class="event-meta-item" v-if="event.actual">
              <span class="meta-label">ACTUAL:</span>
              <span class="meta-value" :class="event.actualClass">{{ event.actual }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="empty-state" v-if="filteredEvents.length === 0">
      // NO_EVENTS_FOUND
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const activeTimeframe = ref('today')
const activeImportance = ref('all')

const events = ref([
  {
    id: 1,
    date: 'TODAY',
    time: '10:00_EST',
    importance: 'high',
    category: 'ECONOMIC',
    title: 'US_CPI_REPORT',
    description: 'Consumer Price Index for all urban consumers, measuring inflation.',
    expected: '+2.1% YoY',
    previous: '+2.2% YoY',
    actual: '+2.0% YoY',
    actualClass: 'positive',
    isPast: false,
    isOngoing: true
  },
  {
    id: 2,
    date: 'TODAY',
    time: '14:30_EST',
    importance: 'high',
    category: 'EARNINGS',
    title: 'NVDA_EARNINGS_CALL',
    description: 'NVIDIA Q4 earnings conference call and results announcement.',
    expected: 'EPS $4.50',
    previous: 'EPS $3.20',
    actual: null,
    actualClass: '',
    isPast: false,
    isOngoing: false
  },
  {
    id: 3,
    date: 'TODAY',
    time: '16:00_EST',
    importance: 'medium',
    category: 'FED',
    title: 'FED_MINUTES_RELEASE',
    description: 'Federal Open Market Committee meeting minutes release.',
    expected: 'Hawkish tone',
    previous: 'Dovish',
    actual: null,
    actualClass: '',
    isPast: false,
    isOngoing: false
  },
  {
    id: 4,
    date: 'TOMORROW',
    time: '08:30_EST',
    importance: 'high',
    category: 'ECONOMIC',
    title: 'US_RETAIL_SALES',
    description: 'Monthly retail sales data, measuring consumer spending.',
    expected: '+0.4% MoM',
    previous: '+0.2% MoM',
    actual: null,
    actualClass: '',
    isPast: false,
    isOngoing: false
  },
  {
    id: 5,
    date: 'TOMORROW',
    time: '12:00_EST',
    importance: 'medium',
    category: 'CRYPTO',
    title: 'BTC_ETF_DECISION',
    description: 'SEC decision on Bitcoin spot ETF applications.',
    expected: 'Approval',
    previous: 'Pending',
    actual: null,
    actualClass: '',
    isPast: false,
    isOngoing: false
  },
  {
    id: 6,
    date: 'YESTERDAY',
    time: '10:00_EST',
    importance: 'medium',
    category: 'ECONOMIC',
    title: 'PPI_REPORT',
    description: 'Producer Price Index measuring wholesale inflation.',
    expected: '+0.3% MoM',
    previous: '+0.1% MoM',
    actual: '+0.4% MoM',
    actualClass: 'negative',
    isPast: true,
    isOngoing: false
  }
])

const filteredEvents = computed(() => {
  return events.value.filter(item => {
    let timeframeMatch = true
    if (activeTimeframe.value === 'today') {
      timeframeMatch = item.date === 'TODAY' || item.date === 'TOMORROW'
    } else if (activeTimeframe.value === 'week') {
      timeframeMatch = true
    }
    const importanceMatch = activeImportance.value === 'all' || item.importance === activeImportance.value
    return timeframeMatch && importanceMatch
  })
})

const upcomingCount = computed(() => {
  return events.value.filter(e => !e.isPast).length
})
</script>

<style scoped>
.market-events {
  padding: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid var(--text-primary);
  padding-bottom: 16px;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  letter-spacing: 2px;
}

.status-bar {
  display: flex;
  gap: 24px;
  font-size: 12px;
  font-family: var(--font-mono);
}

.status-indicator.online {
  color: var(--success-color);
}

.status-item {
  color: var(--text-secondary);
}

.filters {
  display: flex;
  gap: 32px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.filter-label {
  font-size: 11px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  margin-right: 8px;
}

.filter-btn {
  padding: 6px 16px;
  border: 2px solid var(--text-primary);
  background: transparent;
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.1s ease;
}

.filter-btn:hover,
.filter-btn.active {
  background: var(--text-primary);
  color: var(--bg-primary);
}

.events-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.event-item {
  display: grid;
  grid-template-columns: 150px 1fr;
  gap: 24px;
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
  padding: 20px;
  transition: all 0.1s ease;
}

.event-item:hover {
  transform: translate(-2px, -2px);
  box-shadow: 4px 4px 0 var(--text-primary);
}

.event-item.event-past {
  opacity: 0.6;
}

.event-item.event-ongoing {
  border-color: var(--success-color);
  box-shadow: 0 0 0 2px var(--success-color);
}

.event-time {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-family: var(--font-mono);
}

.event-date {
  font-size: 12px;
  font-weight: 700;
}

.event-time-text {
  font-size: 11px;
  color: var(--text-secondary);
}

.event-status {
  font-size: 10px;
  color: var(--success-color);
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.3; }
}

.event-header {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.event-importance {
  font-size: 9px;
  padding: 2px 6px;
  border: 1px solid currentColor;
  font-family: var(--font-mono);
}

.event-importance.high {
  color: var(--danger-color);
  border-color: var(--danger-color);
}

.event-importance.medium {
  color: var(--warning-color);
  border-color: var(--warning-color);
}

.event-category {
  font-size: 9px;
  padding: 2px 6px;
  background: var(--bg-secondary);
  font-family: var(--font-mono);
}

.event-title {
  font-family: var(--font-mono);
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 8px;
}

.event-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.event-meta {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.event-meta-item {
  font-size: 11px;
  font-family: var(--font-mono);
}

.meta-label {
  color: var(--text-secondary);
  margin-right: 4px;
}

.meta-value {
  font-weight: 700;
}

.meta-value.positive {
  color: var(--success-color);
}

.meta-value.negative {
  color: var(--danger-color);
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  font-size: 14px;
  border: 2px dashed var(--border-color);
}

@media (max-width: 768px) {
  .event-item {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .filters {
    flex-direction: column;
    gap: 16px;
  }
}
</style>
