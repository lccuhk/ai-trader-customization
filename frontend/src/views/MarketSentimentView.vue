<template>
  <div class="market-sentiment">
    <div class="page-header">
      <h1 class="page-title">> MARKET_SENTIMENT.EXE</h1>
      <div class="status-bar">
        <span class="status-indicator online">● ANALYSIS_LIVE</span>
        <span class="status-item">LAST_UPDATED: {{ lastUpdated }}</span>
      </div>
    </div>

    <div class="sentiment-overview">
      <div class="sentiment-meter">
        <div class="meter-label">GLOBAL_MARKET_SENTIMENT</div>
        <div class="meter-scale">
          <div class="scale-label extreme-fear">EXTREME_FEAR</div>
          <div class="scale-label fear">FEAR</div>
          <div class="scale-label neutral">NEUTRAL</div>
          <div class="scale-label greed">GREED</div>
          <div class="scale-label extreme-greed">EXTREME_GREED</div>
        </div>
        <div class="meter-bar">
          <div class="meter-fill" :style="{ width: sentimentValue + '%' }" :class="sentimentClass">
            <div class="meter-pointer" :style="{ left: sentimentValue + '%' }"></div>
          </div>
        </div>
        <div class="meter-value" :class="sentimentClass">{{ sentimentValue }}</div>
        <div class="meter-status" :class="sentimentClass">{{ sentimentStatus }}</div>
      </div>
    </div>

    <div class="sentiment-grid">
      <div class="sentiment-card" v-for="item in sentimentData" :key="item.id">
        <div class="card-header">
          <span class="card-symbol">${{ item.symbol }}</span>
          <span class="card-name">{{ item.name }}</span>
        </div>
        <div class="card-score" :class="item.class">
          {{ item.score }}<span class="score-label">/100</span>
        </div>
        <div class="card-bar">
          <div class="bar-fill" :style="{ width: item.score + '%' }" :class="item.class"></div>
        </div>
        <div class="card-details">
          <div class="detail-item">
            <span class="detail-label">SOCIAL:</span>
            <span class="detail-value" :class="item.social.class">{{ item.social.value }}%</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">NEWS:</span>
            <span class="detail-value" :class="item.news.class">{{ item.news.value }}%</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">TECHNICAL:</span>
            <span class="detail-value" :class="item.technical.class">{{ item.technical.value }}%</span>
          </div>
        </div>
      </div>
    </div>

    <div class="content-grid">
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">> SENTIMENT_HISTORY</span>
        </div>
        <div class="panel-body">
          <div class="chart-container">
            <div class="chart-placeholder">
              <div class="chart-area">
                <div class="chart-line">
                  <div class="chart-point" v-for="(point, i) in historyData" :key="i"
                       :style="{ left: (i * 10) + '%', bottom: point.value + '%' }"
                       :class="point.class">
                  </div>
                </div>
              </div>
              <div class="chart-labels">
                <span v-for="i in 10" :key="i">{{ i * 10 }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">> TOPIC_ANALYSIS</span>
        </div>
        <div class="panel-body">
          <div class="topic-item" v-for="topic in topics" :key="topic.id">
            <div class="topic-info">
              <span class="topic-name">{{ topic.name }}</span>
              <span class="topic-count">{{ topic.count }}_mentions</span>
            </div>
            <div class="topic-bar">
              <div class="topic-bar-fill" :style="{ width: topic.percent + '%' }" :class="topic.class"></div>
            </div>
            <div class="topic-sentiment" :class="topic.class">{{ topic.sentiment }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const lastUpdated = ref(new Date().toLocaleTimeString())
const sentimentValue = ref(65)

const sentimentClass = computed(() => {
  if (sentimentValue.value < 25) return 'extreme-fear'
  if (sentimentValue.value < 45) return 'fear'
  if (sentimentValue.value < 55) return 'neutral'
  if (sentimentValue.value < 75) return 'greed'
  return 'extreme-greed'
})

const sentimentStatus = computed(() => {
  const statuses: Record<string, string> = {
    'extreme-fear': 'EXTREME_FEAR',
    'fear': 'FEAR',
    'neutral': 'NEUTRAL',
    'greed': 'GREED',
    'extreme-greed': 'EXTREME_GREED'
  }
  return statuses[sentimentClass.value]
})

const sentimentData = ref([
  {
    id: 1, symbol: 'BTC', name: 'Bitcoin', score: 72, class: 'greed',
    social: { value: 78, class: 'positive' },
    news: { value: 65, class: 'positive' },
    technical: { value: 73, class: 'positive' }
  },
  {
    id: 2, symbol: 'ETH', name: 'Ethereum', score: 68, class: 'greed',
    social: { value: 72, class: 'positive' },
    news: { value: 62, class: 'positive' },
    technical: { value: 70, class: 'positive' }
  },
  {
    id: 3, symbol: 'SOL', name: 'Solana', score: 58, class: 'greed',
    social: { value: 65, class: 'positive' },
    news: { value: 52, class: 'neutral' },
    technical: { value: 57, class: 'neutral' }
  },
  {
    id: 4, symbol: 'NVDA', name: 'NVIDIA', score: 82, class: 'extreme-greed',
    social: { value: 88, class: 'positive' },
    news: { value: 78, class: 'positive' },
    technical: { value: 80, class: 'positive' }
  },
  {
    id: 5, symbol: 'TSLA', name: 'Tesla', score: 45, class: 'neutral',
    social: { value: 52, class: 'neutral' },
    news: { value: 42, class: 'negative' },
    technical: { value: 41, class: 'negative' }
  },
  {
    id: 6, symbol: 'AAPL', name: 'Apple', score: 55, class: 'neutral',
    social: { value: 58, class: 'neutral' },
    news: { value: 52, class: 'neutral' },
    technical: { value: 55, class: 'neutral' }
  }
])

const historyData = ref([
  { value: 45, class: 'neutral' },
  { value: 48, class: 'neutral' },
  { value: 52, class: 'neutral' },
  { value: 55, class: 'neutral' },
  { value: 58, class: 'greed' },
  { value: 62, class: 'greed' },
  { value: 60, class: 'greed' },
  { value: 63, class: 'greed' },
  { value: 67, class: 'greed' },
  { value: 65, class: 'greed' }
])

const topics = ref([
  { id: 1, name: 'BTC_ETF', count: 12453, percent: 85, class: 'positive', sentiment: '+78%' },
  { id: 2, name: 'FED_RATES', count: 8921, percent: 65, class: 'neutral', sentiment: '+12%' },
  { id: 3, name: 'AI_BOOM', count: 7654, percent: 58, class: 'positive', sentiment: '+65%' },
  { id: 4, name: 'REGULATION', count: 5432, percent: 42, class: 'negative', sentiment: '-23%' },
  { id: 5, name: 'INFLATION', count: 4321, percent: 35, class: 'neutral', sentiment: '-5%' }
])

let updateInterval: number

onMounted(() => {
  updateInterval = window.setInterval(() => {
    lastUpdated.value = new Date().toLocaleTimeString()
    sentimentValue.value = Math.floor(Math.random() * 20) + 55
  }, 10000)
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
})
</script>

<style scoped>
.market-sentiment {
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

.sentiment-overview {
  margin-bottom: 32px;
}

.sentiment-meter {
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
  padding: 32px;
  text-align: center;
}

.meter-label {
  font-family: var(--font-mono);
  font-size: 14px;
  letter-spacing: 2px;
  margin-bottom: 24px;
}

.meter-scale {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 9px;
  font-family: var(--font-mono);
  color: var(--text-secondary);
}

.meter-bar {
  height: 20px;
  background: linear-gradient(to right, 
    var(--danger-color) 0%, 
    var(--danger-color) 25%, 
    var(--warning-color) 25%, 
    var(--warning-color) 45%, 
    var(--text-secondary) 45%, 
    var(--text-secondary) 55%, 
    var(--success-color) 55%, 
    var(--success-color) 75%, 
    #00ff00 75%, 
    #00ff00 100%
  );
  position: relative;
  margin-bottom: 16px;
}

.meter-fill {
  height: 100%;
  position: relative;
  transition: width 0.5s ease;
}

.meter-pointer {
  position: absolute;
  top: -8px;
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 12px solid var(--text-primary);
  transform: translateX(-50%);
  transition: left 0.5s ease;
}

.meter-value {
  font-size: 48px;
  font-weight: 700;
  font-family: var(--font-mono);
  margin-bottom: 8px;
}

.meter-status {
  font-size: 18px;
  font-family: var(--font-mono);
  letter-spacing: 2px;
}

.meter-value.extreme-fear,
.meter-status.extreme-fear {
  color: var(--danger-color);
}

.meter-value.fear,
.meter-status.fear {
  color: var(--warning-color);
}

.meter-value.neutral,
.meter-status.neutral {
  color: var(--text-secondary);
}

.meter-value.greed,
.meter-status.greed {
  color: var(--success-color);
}

.meter-value.extreme-greed,
.meter-status.extreme-greed {
  color: #00ff00;
}

.sentiment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.sentiment-card {
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-symbol {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 16px;
}

.card-name {
  font-size: 11px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
}

.card-score {
  font-size: 36px;
  font-weight: 700;
  font-family: var(--font-mono);
  margin-bottom: 12px;
}

.score-label {
  font-size: 16px;
  color: var(--text-secondary);
}

.card-score.greed {
  color: var(--success-color);
}

.card-score.extreme-greed {
  color: #00ff00;
}

.card-score.neutral {
  color: var(--text-secondary);
}

.card-score.fear {
  color: var(--warning-color);
}

.card-bar {
  height: 8px;
  background: var(--bg-secondary);
  margin-bottom: 16px;
}

.bar-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.bar-fill.greed {
  background: var(--success-color);
}

.bar-fill.extreme-greed {
  background: #00ff00;
}

.bar-fill.neutral {
  background: var(--text-secondary);
}

.bar-fill.fear {
  background: var(--warning-color);
}

.card-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  font-family: var(--font-mono);
}

.detail-label {
  color: var(--text-secondary);
}

.detail-value.positive {
  color: var(--success-color);
}

.detail-value.negative {
  color: var(--danger-color);
}

.detail-value.neutral {
  color: var(--text-secondary);
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.panel {
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
}

.panel-header {
  padding: 12px 16px;
  border-bottom: 2px solid var(--text-primary);
  background: var(--text-primary);
  color: var(--bg-primary);
}

.panel-title {
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 1px;
}

.panel-body {
  padding: 16px;
}

.chart-container {
  height: 200px;
  position: relative;
}

.chart-placeholder {
  height: 100%;
  position: relative;
  border-left: 2px solid var(--text-primary);
  border-bottom: 2px solid var(--text-primary);
  padding: 20px;
}

.chart-area {
  position: relative;
  height: 100%;
}

.chart-line {
  position: relative;
  height: 100%;
}

.chart-point {
  position: absolute;
  width: 8px;
  height: 8px;
  transform: translate(-50%, 50%);
}

.chart-point.greed {
  background: var(--success-color);
}

.chart-point.neutral {
  background: var(--text-secondary);
}

.chart-labels {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  padding: 4px 20px;
  font-size: 9px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
}

.topic-item {
  display: grid;
  grid-template-columns: 1fr 1fr 80px;
  gap: 12px;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.topic-item:last-child {
  border-bottom: none;
}

.topic-info {
  display: flex;
  flex-direction: column;
}

.topic-name {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 13px;
}

.topic-count {
  font-size: 10px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
}

.topic-bar {
  height: 8px;
  background: var(--bg-secondary);
}

.topic-bar-fill {
  height: 100%;
}

.topic-bar-fill.positive {
  background: var(--success-color);
}

.topic-bar-fill.negative {
  background: var(--danger-color);
}

.topic-bar-fill.neutral {
  background: var(--text-secondary);
}

.topic-sentiment {
  text-align: right;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 13px;
}

.topic-sentiment.positive {
  color: var(--success-color);
}

.topic-sentiment.negative {
  color: var(--danger-color);
}

.topic-sentiment.neutral {
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .topic-item {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .topic-sentiment {
    text-align: left;
  }
}
</style>
