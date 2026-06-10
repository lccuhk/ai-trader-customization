<template>
  <div class="market-news">
    <div class="page-header">
      <h1 class="page-title">&gt; {{ t('market.news').toUpperCase() }}.EXE</h1>
      <div class="status-bar">
        <span class="status-indicator online">● {{ t('market.feedLive') }}</span>
        <span class="status-item">{{ t('market.lastUpdated') }}: {{ lastUpdated }}</span>
      </div>
    </div>

    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">{{ t('market.category') }}:</span>
        <button
          class="filter-btn"
          :class="{ active: activeCategory === 'all' }"
          @click="activeCategory = 'all'"
        >{{ t('common.all') }}</button>
        <button
          class="filter-btn"
          :class="{ active: activeCategory === 'crypto' }"
          @click="activeCategory = 'crypto'"
        >{{ t('market.crypto') }}</button>
        <button
          class="filter-btn"
          :class="{ active: activeCategory === 'stocks' }"
          @click="activeCategory = 'stocks'"
        >{{ t('market.stocks') }}</button>
        <button
          class="filter-btn"
          :class="{ active: activeCategory === 'macro' }"
          @click="activeCategory = 'macro'"
        >{{ t('market.macro') }}</button>
        <button
          class="filter-btn"
          :class="{ active: activeCategory === 'regulation' }"
          @click="activeCategory = 'regulation'"
        >{{ t('market.regulation') }}</button>
      </div>
      <div class="filter-group">
        <span class="filter-label">{{ t('market.importance') }}:</span>
        <button
          class="filter-btn"
          :class="{ active: activeImportance === 'all' }"
          @click="activeImportance = 'all'"
        >{{ t('common.all') }}</button>
        <button
          class="filter-btn"
          :class="{ active: activeImportance === 'high' }"
          @click="activeImportance = 'high'"
        >{{ t('market.high') }}</button>
        <button
          class="filter-btn"
          :class="{ active: activeImportance === 'medium' }"
          @click="activeImportance = 'medium'"
        >{{ t('market.medium') }}</button>
        <button
          class="filter-btn"
          :class="{ active: activeImportance === 'low' }"
          @click="activeImportance = 'low'"
        >{{ t('market.low') }}</button>
      </div>
    </div>

    <div class="news-grid">
      <div class="news-card" v-for="item in filteredNews" :key="item.id">
        <div class="news-header">
          <span class="news-source">{{ item.source }}</span>
          <span class="news-importance" :class="item.importance">{{ t('market.' + item.importance) }}</span>
          <span class="news-category">{{ t('market.' + item.category) }}</span>
        </div>
        <h3 class="news-title">{{ item.title }}</h3>
        <p class="news-summary">{{ item.summary }}</p>
        <div class="news-tags">
          <span class="news-tag" v-for="tag in item.tags" :key="tag">${{ tag }}</span>
        </div>
        <div class="news-footer">
          <span class="news-time">{{ item.time }}</span>
          <button class="btn-read" @click="readNews(item)">[ {{ t('market.readMore').toUpperCase() }} ]</button>
        </div>
      </div>
    </div>

    <div class="empty-state" v-if="filteredNews.length === 0">
      // {{ t('common.noData') }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

const lastUpdated = ref(new Date().toLocaleString())
const activeCategory = ref('all')
const activeImportance = ref('all')

// 中文新闻数据
const zhNews = [
  {
    id: 1,
    source: 'COINDESK',
    importance: 'high',
    category: 'crypto',
    title: '比特币突破 50,000 美元关口',
    summary: '比特币价格强势突破 50,000 美元，机构需求强劲和 ETF 资金持续流入推动上涨。',
    tags: ['BTC', 'ETF', '机构'],
    time: '5 分钟前'
  },
  {
    id: 2,
    source: 'BLOOMBERG',
    importance: 'high',
    category: 'macro',
    title: '美联储维持利率不变',
    summary: '美联储宣布维持当前利率水平不变，暗示今年晚些时候可能降息。',
    tags: ['美联储', '利率', '宏观'],
    time: '15 分钟前'
  },
  {
    id: 3,
    source: 'REUTERS',
    importance: 'medium',
    category: 'stocks',
    title: '英伟达业绩超预期',
    summary: '英伟达公布创纪录营收，AI 芯片需求持续爆发，盘后股价上涨 8%。',
    tags: ['NVDA', 'AI', '财报'],
    time: '32 分钟前'
  },
  {
    id: 4,
    source: 'THE_BLOCK',
    importance: 'medium',
    category: 'regulation',
    title: 'SEC 批准新加密货币 ETF',
    summary: '美国 SEC 批准现货以太坊 ETF 申请，为下月交易铺平道路。',
    tags: ['ETH', 'ETF', 'SEC', '监管'],
    time: '1 小时前'
  },
  {
    id: 5,
    source: 'COINTELEGRAPH',
    importance: 'low',
    category: 'crypto',
    title: 'Solana 生态增长 25%',
    summary: 'Solana DeFi 生态 TVL 在过去一个月增长 25%，生态项目持续扩展。',
    tags: ['SOL', 'DeFi', 'TVL'],
    time: '2 小时前'
  },
  {
    id: 6,
    source: 'WSJ',
    importance: 'high',
    category: 'macro',
    title: 'CPI 数据表明通胀放缓',
    summary: '消费者价格指数同比上涨 2.1%，创 2021 年以来最低水平。',
    tags: ['CPI', '通胀', '经济'],
    time: '3 小时前'
  },
  {
    id: 7,
    source: 'BLOOMBERG',
    importance: 'medium',
    category: 'stocks',
    title: '特斯拉交付量超预期',
    summary: '特斯拉第四季度交付超 50 万辆，超出分析师预期。',
    tags: ['TSLA', '交付', '电动汽车'],
    time: '4 小时前'
  },
  {
    id: 8,
    source: 'COINDESK',
    importance: 'low',
    category: 'crypto',
    title: '以太坊合并进展顺利',
    summary: '以太坊开发者宣布合并过渡的最终测试网已完成测试。',
    tags: ['ETH', '合并', '升级'],
    time: '5 小时前'
  }
]

// 英文新闻数据
const enNews = [
  {
    id: 1,
    source: 'COINDESK',
    importance: 'high',
    category: 'crypto',
    title: 'BTC Breaks $50K Resistance',
    summary: 'Bitcoin surges past $50,000 amid strong institutional demand and positive ETF flows.',
    tags: ['BTC', 'ETF', 'INSTITUTIONAL'],
    time: '5m ago'
  },
  {
    id: 2,
    source: 'BLOOMBERG',
    importance: 'high',
    category: 'macro',
    title: 'Fed Holds Rates Steady',
    summary: 'Federal Reserve maintains interest rates, signals potential cuts later this year.',
    tags: ['FED', 'INTEREST_RATES', 'MACRO'],
    time: '15m ago'
  },
  {
    id: 3,
    source: 'REUTERS',
    importance: 'medium',
    category: 'stocks',
    title: 'NVDA Earnings Beat Expectations',
    summary: 'NVIDIA reports record revenue driven by AI chip demand, stock up 8% after hours.',
    tags: ['NVDA', 'AI', 'EARNINGS'],
    time: '32m ago'
  },
  {
    id: 4,
    source: 'THE_BLOCK',
    importance: 'medium',
    category: 'regulation',
    title: 'SEC Approves New Crypto ETFs',
    summary: 'SEC approves spot Ethereum ETF applications, paving way for trading next month.',
    tags: ['ETH', 'ETF', 'SEC', 'REGULATION'],
    time: '1h ago'
  },
  {
    id: 5,
    source: 'COINTELEGRAPH',
    importance: 'low',
    category: 'crypto',
    title: 'Solana Ecosystem Grows 25%',
    summary: 'Solana DeFi ecosystem sees 25% growth in TVL over past month.',
    tags: ['SOL', 'DeFi', 'TVL'],
    time: '2h ago'
  },
  {
    id: 6,
    source: 'WSJ',
    importance: 'high',
    category: 'macro',
    title: 'CPI Data Shows Inflation Cooling',
    summary: 'Consumer Price Index rises 2.1% YoY, lowest since 2021.',
    tags: ['CPI', 'INFLATION', 'ECONOMY'],
    time: '3h ago'
  },
  {
    id: 7,
    source: 'BLOOMBERG',
    importance: 'medium',
    category: 'stocks',
    title: 'TSLA Deliveries Exceed Forecasts',
    summary: 'Tesla delivers record 500K+ vehicles in Q4, beating analyst estimates.',
    tags: ['TSLA', 'DELIVERIES', 'EV'],
    time: '4h ago'
  },
  {
    id: 8,
    source: 'COINDESK',
    importance: 'low',
    category: 'crypto',
    title: 'ETH Merge Completion Near',
    summary: 'Ethereum developers announce final testnet for merge transition.',
    tags: ['ETH', 'MERGE', 'UPGRADE'],
    time: '5h ago'
  }
]

const newsList = computed(() => {
  return locale.value === 'zh-CN' ? zhNews : enNews
})

const filteredNews = computed(() => {
  return newsList.value.filter(item => {
    const categoryMatch = activeCategory.value === 'all' || item.category === activeCategory.value
    const importanceMatch = activeImportance.value === 'all' || item.importance === activeImportance.value
    return categoryMatch && importanceMatch
  })
})

function readNews(newsItem: any) {
  console.log('Reading news:', newsItem.title, newsItem)
}

let updateInterval: number

onMounted(() => {
  updateInterval = window.setInterval(() => {
    lastUpdated.value = new Date().toLocaleString()
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
  flex-wrap: wrap;
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
