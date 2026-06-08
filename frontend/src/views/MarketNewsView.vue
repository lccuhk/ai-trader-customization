<template>
  <div class="market-news">
    <div class="page-header">
      <h1 class="page-title">> MARKET_NEWS.EXE</h1>
      <div class="status-bar">
        <span class="status-indicator online">● FEED_LIVE</span>
        <span class="status-item">LAST_UPDATED: {{ lastUpdated }}</span>
      </div>
    </div>

    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">CATEGORY:</span>
        <button class="filter-btn" :class="{ active: activeCategory === 'all' }" @click="activeCategory = 'all'">ALL</button>
        <button class="filter-btn" :class="{ active: activeCategory === 'crypto' }" @click="activeCategory = 'crypto'">CRYPTO</button>
        <button class="filter-btn" :class="{ active: activeCategory === 'stocks' }" @click="activeCategory = 'stocks'">STOCKS</button>
        <button class="filter-btn" :class="{ active: activeCategory === 'macro' }" @click="activeCategory = 'macro'">MACRO</button>
        <button class="filter-btn" :class="{ active: activeCategory === 'regulation' }" @click="activeCategory = 'regulation'">REGULATION</button>
      </div>
      <div class="filter-group">
        <span class="filter-label">IMPORTANCE:</span>
        <button class="filter-btn" :class="{ active: activeImportance === 'all' }" @click="activeImportance = 'all'">ALL</button>
        <button class="filter-btn" :class="{ active: activeImportance === 'high' }" @click="activeImportance = 'high'">HIGH</button>
        <button class="filter-btn" :class="{ active: activeImportance === 'medium' }" @click="activeImportance = 'medium'">MEDIUM</button>
        <button class="filter-btn" :class="{ active: activeImportance === 'low' }" @click="activeImportance = 'low'">LOW</button>
      </div>
    </div>

    <div class="news-grid">
      <div class="news-card" v-for="news in filteredNews" :key="news.id">
        <div class="news-header">
          <span class="news-source">{{ news.source }}</span>
          <span class="news-importance" :class="news.importance">{{ news.importance.toUpperCase() }}</span>
          <span class="news-category">{{ news.category.toUpperCase() }}</span>
        </div>
        <h3 class="news-title">{{ news.title }}</h3>
        <p class="news-summary">{{ news.summary }}</p>
        <div class="news-tags">
          <span class="news-tag" v-for="tag in news.tags" :key="tag">${{ tag }}</span>
        </div>
        <div class="news-footer">
          <span class="news-time">{{ news.time }}</span>
          <button class="btn-read" @click="readNews(news)">[ READ_MORE ]</button>
        </div>
      </div>
    </div>

    <div class="empty-state" v-if="filteredNews.length === 0">
      // NO_NEWS_FOUND
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const lastUpdated = ref(new Date().toLocaleTimeString())
const activeCategory = ref('all')
const activeImportance = ref('all')

const news = ref([
  {
    id: 1,
    source: 'COINDESK',
    importance: 'high',
    category: 'crypto',
    title: 'BTC_BREAKS_$50K_RESISTANCE',
    summary: 'Bitcoin surges past $50,000 amid strong institutional demand and positive ETF flows.',
    tags: ['BTC', 'ETF', 'INSTITUTIONAL'],
    time: '5m_ago'
  },
  {
    id: 2,
    source: 'BLOOMBERG',
    importance: 'high',
    category: 'macro',
    title: 'FED_HOLDS_RATES_STEADY',
    summary: 'Federal Reserve maintains interest rates, signals potential cuts later this year.',
    tags: ['FED', 'INTEREST_RATES', 'MACRO'],
    time: '15m_ago'
  },
  {
    id: 3,
    source: 'REUTERS',
    importance: 'medium',
    category: 'stocks',
    title: 'NVDA_EARNINGS_BEAT_EXPECTATIONS',
    summary: 'NVIDIA reports record revenue driven by AI chip demand, stock up 8% after hours.',
    tags: ['NVDA', 'AI', 'EARNINGS'],
    time: '32m_ago'
  },
  {
    id: 4,
    source: 'THE_BLOCK',
    importance: 'medium',
    category: 'regulation',
    title: 'SEC_APPROVES_NEW_CRYPTO_ETFS',
    summary: 'SEC approves spot Ethereum ETF applications, paving way for trading next month.',
    tags: ['ETH', 'ETF', 'SEC', 'REGULATION'],
    time: '1h_ago'
  },
  {
    id: 5,
    source: 'COINTELEGRAPH',
    importance: 'low',
    category: 'crypto',
    title: 'SOLANA_ECOSYSTEM_GROWS_25%',
    summary: 'Solana DeFi ecosystem sees 25% growth in TVL over past month.',
    tags: ['SOL', 'DeFi', 'TVL'],
    time: '2h_ago'
  },
  {
    id: 6,
    source: 'WSJ',
    importance: 'high',
    category: 'macro',
    title: 'CPI_DATA_SHOWS_INFLATION_COOLING',
    summary: 'Consumer Price Index rises 2.1% YoY, lowest since 2021.',
    tags: ['CPI', 'INFLATION', 'ECONOMY'],
    time: '3h_ago'
  },
  {
    id: 7,
    source: 'BLOOMBERG',
    importance: 'medium',
    category: 'stocks',
    title: 'TSLA_DELIVERIES_EXCEED_FORECASTS',
    summary: 'Tesla delivers record 500K+ vehicles in Q4, beating analyst estimates.',
    tags: ['TSLA', 'DELIVERIES', 'EV'],
    time: '4h_ago'
  },
  {
    id: 8,
    source: 'COINDESK',
    importance: 'low',
    category: 'crypto',
    title: 'ETH_MERGE_COMPLETION_NEAR',
    summary: 'Ethereum developers announce final testnet for merge transition.',
    tags: ['ETH', 'MERGE', 'UPGRADE'],
    time: '5h_ago'
  }
])

const filteredNews = computed(() => {
  return news.value.filter(item => {
    const categoryMatch = activeCategory.value === 'all' || item.category === activeCategory.value
    const importanceMatch = activeImportance.value === 'all' || item.importance === activeImportance.value
    return categoryMatch && importanceMatch
  })
})

function readNews(newsItem: any) {
  console.log('Reading news:', newsItem.title)
  window.open('#', '_blank')
}

let updateInterval: number

onMounted(() => {
  updateInterval = window.setInterval(() => {
    lastUpdated.value = new Date().toLocaleTimeString()
  }, 30000)
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
})
</script>

<style scoped>
.market-news {
  padding: 24px;
  max-width: 1400px;
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

.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 16px;
}

.news-card {
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
  padding: 20px;
  transition: all 0.1s ease;
}

.news-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: 4px 4px 0 var(--text-primary);
}

.news-header {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.news-source {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 11px;
  color: var(--text-secondary);
}

.news-importance {
  font-size: 9px;
  padding: 2px 6px;
  border: 1px solid currentColor;
  font-family: var(--font-mono);
}

.news-importance.high {
  color: var(--danger-color);
  border-color: var(--danger-color);
}

.news-importance.medium {
  color: var(--warning-color);
  border-color: var(--warning-color);
}

.news-importance.low {
  color: var(--text-secondary);
  border-color: var(--text-secondary);
}

.news-category {
  font-size: 9px;
  padding: 2px 6px;
  background: var(--bg-secondary);
  font-family: var(--font-mono);
}

.news-title {
  font-family: var(--font-mono);
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 12px;
  line-height: 1.4;
}

.news-summary {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 16px;
}

.news-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.news-tag {
  font-size: 10px;
  font-family: var(--font-mono);
  color: var(--success-color);
}

.news-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.news-time {
  font-size: 10px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
}

.btn-read {
  padding: 6px 12px;
  border: 1px solid var(--text-primary);
  background: transparent;
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 10px;
  cursor: pointer;
}

.btn-read:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
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
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .news-grid {
    grid-template-columns: 1fr;
  }
  
  .filters {
    flex-direction: column;
    gap: 16px;
  }
}
</style>
