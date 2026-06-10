<template>
  <div class="market-intelligence">
    <div class="page-title">&gt; 市场情报</div>

    <div class="tabs">
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

    <!-- Quotes -->
    <div v-if="activeTab === 'quotes'" class="panel">
      <div class="panel-header">
        <span class="panel-title">&gt; 实时行情</span>
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            class="search-input"
            placeholder="搜索标的..."
          />
          <span v-if="searchQuery" class="search-clear" @click="searchQuery = ''">✕</span>
        </div>
      </div>
      <div class="panel-body">
        <!-- Quotes Table -->
        <table class="data-table">
          <thead>
            <tr>
              <th>标的</th>
              <th>价格</th>
              <th>24h 涨跌</th>
              <th>成交量</th>
              <th>详情</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="q in filteredQuotes"
              :key="q.symbol"
              class="quote-row"
              :class="{ selected: selectedSymbol === q.symbol }"
              @click="toggleDetail(q.symbol)"
            >
              <td class="symbol">{{ q.symbol }}</td>
              <td class="price">${{ toLocale(q.price) }}</td>
              <td :class="q.change24h >= 0 ? 'positive' : 'negative'">
                {{ q.change24h >= 0 ? '+' : '' }}{{ q.change24h }}%
              </td>
              <td class="volume">{{ q.volume }}</td>
              <td>
                <span class="detail-arrow">{{ selectedSymbol === q.symbol ? '▲' : '▼' }}</span>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!filteredQuotes.length" class="empty">未找到匹配的标的</div>

        <!-- Technical Indicator Detail Panel with SVG Charts -->
        <transition name="expand">
          <div v-if="selectedSymbol && indicators" class="detail-panel">
            <div class="detail-header">
              <div class="detail-header-left">
                <span class="detail-symbol">{{ selectedSymbol }}</span>
                <span class="detail-label">技术面分析</span>
              </div>
              <span class="detail-rec" :class="recClass">{{ indicators.recommendation }}</span>
            </div>

            <div class="chart-grid">
              <!-- RSI Gauge Chart -->
              <div class="chart-card">
                <div class="chart-title">RSI (14) — {{ indicators.rsi.toFixed(1) }}</div>
                <svg :viewBox="'0 0 200 60'" class="chart-svg">
                  <!-- Background bar -->
                  <rect x="10" y="20" width="180" height="20" rx="2" fill="var(--bg-primary)" stroke="var(--border-color)" stroke-width="1" />
                  <!-- Overbought zone (70-100) -->
                  <rect x="10" y="20" width="54" height="20" rx="2" fill="rgba(255,51,51,0.15)" />
                  <!-- Oversold zone (0-30) -->
                  <rect x="136" y="20" width="54" height="20" rx="2" fill="rgba(0,255,65,0.15)" />
                  <!-- Mid lines -->
                  <line x1="10" y1="30" x2="190" y2="30" stroke="var(--border-color)" stroke-width="0.5" />
                  <!-- Labels -->
                  <text x="10" y="14" font-size="8" fill="var(--text-secondary)">0</text>
                  <text x="95" y="14" font-size="8" fill="var(--text-secondary)">50</text>
                  <text x="185" y="14" font-size="8" fill="var(--text-secondary)">100</text>
                  <!-- RSI indicator arrow -->
                  <polygon
                    :points="rsiArrowPoints"
                    :fill="rsiArrowColor"
                  />
                </svg>
                <div class="chart-footer">
                  <span>超卖区 &lt; 30</span>
                  <span>超买区 &gt; 70</span>
                </div>
              </div>

              <!-- MACD Chart -->
              <div class="chart-card">
                <div class="chart-title">MACD</div>
                <svg :viewBox="'0 0 200 60'" class="chart-svg">
                  <!-- Baseline -->
                  <line x1="0" y1="30" x2="200" y2="30" stroke="var(--border-color)" stroke-width="0.5" />
                  <!-- DIF line -->
                  <path d="M20,42 L60,38 L100,25 L140,20 L180,22" stroke="var(--success-color)" stroke-width="1.5" fill="none" />
                  <!-- DEA line -->
                  <path d="M20,44 L60,40 L100,30 L140,26 L180,27" stroke="var(--danger-color)" stroke-width="1.5" fill="none" />
                  <!-- Bars -->
                  <rect x="35" y="32" width="8" height="8" :fill="indicators.macd.histogram.startsWith('+') ? 'var(--success-color)' : 'var(--danger-color)'" />
                  <rect x="75" y="28" width="8" height="12" :fill="indicators.macd.histogram.startsWith('+') ? 'var(--success-color)' : 'var(--danger-color)'" />
                  <rect x="115" y="22" width="8" height="18" :fill="indicators.macd.histogram.startsWith('+') ? 'var(--success-color)' : 'var(--danger-color)'" />
                  <rect x="155" y="24" width="8" height="16" :fill="indicators.macd.histogram.startsWith('+') ? 'var(--success-color)' : 'var(--danger-color)'" />
                  <!-- Legend -->
                  <text x="10" y="56" font-size="7" fill="var(--success-color)">DIF {{ indicators.macd.value }}</text>
                  <text x="100" y="56" font-size="7" fill="var(--danger-color)">DEA {{ indicators.macd.signal }}</text>
                </svg>
              </div>

              <!-- MA Cross Chart -->
              <div class="chart-card">
                <div class="chart-title">移动平均线</div>
                <svg :viewBox="'0 0 200 60'" class="chart-svg">
                  <!-- Grid lines -->
                  <line x1="0" y1="15" x2="200" y2="15" stroke="var(--border-color)" stroke-width="0.3" />
                  <line x1="0" y1="30" x2="200" y2="30" stroke="var(--border-color)" stroke-width="0.3" />
                  <line x1="0" y1="45" x2="200" y2="45" stroke="var(--border-color)" stroke-width="0.3" />
                  <!-- Price line -->
                  <path d="M20,35 L55,32 L90,25 L125,20 L180,22" stroke="var(--text-primary)" stroke-width="1.5" fill="none" />
                  <!-- MA(20) line -->
                  <path d="M20,38 L55,36 L90,30 L125,26 L180,28" stroke="var(--info-color)" stroke-width="1.5" fill="none" stroke-dasharray="3,2" />
                  <!-- MA(50) line -->
                  <path d="M20,42 L55,42 L90,38 L125,36 L180,36" stroke="#ff9900" stroke-width="1.5" fill="none" stroke-dasharray="2,3" />
                  <!-- Legend -->
                  <text x="10" y="56" font-size="7" fill="var(--text-primary)">价格</text>
                  <text x="70" y="56" font-size="7" fill="var(--info-color)">MA20 {{ toLocale(indicators.ma20) }}</text>
                  <text x="140" y="56" font-size="7" fill="#ff9900">MA50 {{ toLocale(indicators.ma50) }}</text>
                </svg>
              </div>

              <!-- Bollinger Bands Chart -->
              <div class="chart-card">
                <div class="chart-title">布林带</div>
                <svg :viewBox="'0 0 200 60'" class="chart-svg">
                  <!-- Bollinger band area -->
                  <defs>
                    <linearGradient id="bbGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stop-color="var(--info-color)" stop-opacity="0.15" />
                      <stop offset="100%" stop-color="var(--info-color)" stop-opacity="0.02" />
                    </linearGradient>
                  </defs>
                  <!-- Upper band -->
                  <path d="M20,14 L55,12 L90,10 L125,12 L180,14" stroke="var(--text-secondary)" stroke-width="1" fill="none" />
                  <!-- Middle band -->
                  <path d="M20,30 L55,28 L90,24 L125,24 L180,26" stroke="var(--info-color)" stroke-width="1.5" fill="none" />
                  <!-- Lower band -->
                  <path d="M20,46 L55,44 L90,38 L125,36 L180,38" stroke="var(--text-secondary)" stroke-width="1" fill="none" />
                  <!-- Fill area between upper and lower -->
                  <path d="M20,14 L55,12 L90,10 L125,12 L180,14 L180,38 L125,36 L90,38 L55,44 L20,46 Z" fill="url(#bbGrad)" />
                  <!-- Price dot -->
                  <circle :cx="bollingerDotX" cy="26" r="3" fill="var(--text-primary)" stroke="var(--bg-primary)" stroke-width="1" />
                  <!-- Legend -->
                  <text x="10" y="56" font-size="7" fill="var(--text-secondary)">上轨 {{ toLocale(indicators.bollinger.upper) }}</text>
                  <text x="105" y="56" font-size="7" fill="var(--info-color)">中 {{ toLocale(indicators.bollinger.middle) }}</text>
                  <text x="170" y="56" font-size="7" fill="var(--text-secondary)">下 {{ toLocale(indicators.bollinger.lower) }}</text>
                </svg>
              </div>
            </div>

            <!-- Text summary below charts -->
            <div class="detail-summary">
              <div class="summary-item">
                <span class="summary-key">24h 最高/最低</span>
                <span class="summary-val">${{ toLocale(indicators.high24h) }} / ${{ toLocale(indicators.low24h) }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-key">成交量 24h</span>
                <span class="summary-val">{{ indicators.volume24h }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-key">市值</span>
                <span class="summary-val">{{ indicators.marketCap }}</span>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <!-- News -->
    <div v-if="activeTab === 'news'" class="panel">
      <div class="panel-header"><span class="panel-title">&gt; 市场新闻</span></div>
      <div class="panel-body">
        <div v-for="n in news" :key="n.id" class="news-item">
          <div class="news-importance" :class="n.importance">
            {{ n.importance === 'high' ? '重要' : n.importance === 'medium' ? '一般' : '低' }}
          </div>
          <div class="news-content">
            <div class="news-title">{{ n.title }}</div>
            <div class="news-time">{{ n.time }}</div>
          </div>
        </div>
        <div v-if="!news.length" class="empty">暂无新闻</div>
      </div>
    </div>

    <!-- Events -->
    <div v-if="activeTab === 'events'" class="panel">
      <div class="panel-header"><span class="panel-title">&gt; 事件日历</span></div>
      <div class="panel-body">
        <table class="data-table">
          <thead>
            <tr>
              <th>日期</th>
              <th>事件</th>
              <th>重要性</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="e in events" :key="e.event">
              <td class="date">{{ e.date }}</td>
              <td>{{ e.event }}</td>
              <td>
                <span class="impact" :class="e.impact">
                  {{ e.impact === 'high' ? '高' : e.impact === 'medium' ? '中' : '低' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Indicators -->
    <div v-if="activeTab === 'indicators'" class="panel">
      <div class="panel-header"><span class="panel-title">&gt; 经济指标</span></div>
      <div class="panel-body">
        <table class="data-table">
          <thead>
            <tr>
              <th>指标</th>
              <th>当前值</th>
              <th>变动</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ind in economicIndicators" :key="ind.name">
              <td class="indicator-name">{{ ind.name }}</td>
              <td class="value">{{ ind.value }}</td>
              <td :class="ind.change.startsWith('+') ? 'positive' : 'negative'">
                {{ ind.change }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Gainers / Losers -->
    <div v-if="activeTab === 'gainers'" class="gainers-losers">
      <div class="panel">
        <div class="panel-header"><span class="panel-title">&gt; 涨幅榜</span></div>
        <div class="panel-body">
          <div v-for="g in gainersLosers.gainers" :key="g.symbol" class="gl-item">
            <span class="symbol">{{ g.symbol }}</span>
            <span class="positive">+{{ g.change }}%</span>
          </div>
        </div>
      </div>
      <div class="panel">
        <div class="panel-header"><span class="panel-title">&gt; 跌幅榜</span></div>
        <div class="panel-body">
          <div v-for="l in gainersLosers.losers" :key="l.symbol" class="gl-item">
            <span class="symbol">{{ l.symbol }}</span>
            <span class="negative">{{ l.change }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  marketQuotes, news, events,
  economicIndicators, gainersLosers,
  technicalIndicators,
} from '@/data/mockData'

const activeTab = ref('quotes')
const searchQuery = ref('')
const selectedSymbol = ref<string | null>(null)

const tabs = [
  { key: 'quotes', label: '行情' },
  { key: 'news', label: '新闻' },
  { key: 'events', label: '事件日历' },
  { key: 'indicators', label: '经济指标' },
  { key: 'gainers', label: '涨跌榜' },
]

const filteredQuotes = computed(() => {
  if (!searchQuery.value.trim()) return marketQuotes
  const q = searchQuery.value.toUpperCase()
  return marketQuotes.filter(item =>
    item.symbol.toUpperCase().includes(q)
  )
})

const indicators = computed(() => {
  if (!selectedSymbol.value) return null
  return technicalIndicators[selectedSymbol.value] || null
})

function toggleDetail(symbol: string) {
  selectedSymbol.value = selectedSymbol.value === symbol ? null : symbol
}

function toLocale(n: number): string {
  return n.toLocaleString()
}

function maClass(ma: number, otherMa: number): string {
  if (ma > otherMa) return 'positive'
  if (ma < otherMa) return 'negative'
  return ''
}

// RSI arrow position (SVG coordinate)
const rsiArrowPoints = computed(() => {
  if (!indicators.value) return '0,0 0,0 0,0'
  const rsi = Math.min(100, Math.max(0, indicators.value.rsi))
  const x = 10 + (rsi / 100) * 180
  return `${x},16 ${x-5},24 ${x+5},24`
})

const rsiArrowColor = computed(() => {
  if (!indicators.value) return 'var(--text-secondary)'
  const rsi = indicators.value.rsi
  if (rsi >= 70) return 'var(--danger-color)'
  if (rsi <= 30) return 'var(--success-color)'
  return 'var(--text-primary)'
})

// Bollinger Band: where the price dot sits (map price to SVG X coordinate within band range)
const bollingerDotX = computed(() => {
  if (!indicators.value) return 100
  const bb = indicators.value.bollinger
  const range = bb.upper - bb.lower
  if (range <= 0) return 100
  // We need a current price. Use the market quote for this symbol or estimate from mid band + offset
  // Estimate from middle band position
  const quote = filteredQuotes.value.find(q => q.symbol === selectedSymbol.value)
  const price = quote ? quote.price : bb.middle
  const ratio = (price - bb.lower) / range
  return 20 + ratio * 160 // map to SVG x range 20-180
})

const rsiClass = computed(() => {
  if (!indicators.value) return ''
  const rsi = indicators.value.rsi
  if (rsi >= 70) return 'positive'
  if (rsi <= 30) return 'negative'
  return ''
})

const recClass = computed(() => {
  if (!indicators.value) return ''
  const rec = indicators.value.recommendation
  if (rec === '买入') return 'rec-buy'
  if (rec === '持有' || rec === '观望') return 'rec-hold'
  if (rec === '卖出') return 'rec-sell'
  return ''
})
</script>

<style scoped>
.market-intelligence {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.tabs {
  display: flex;
  gap: 4px;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 0;
}

.tab-btn {
  padding: 8px 20px;
  border: 2px solid var(--border-color);
  border-bottom: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin-bottom: -2px;
  transition: all 0.1s ease;
}
.tab-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}
.tab-btn.active {
  background: var(--bg-primary);
  color: var(--text-primary);
  border-bottom: 2px solid var(--bg-primary);
}

.panel {
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 2px solid var(--border-color);
  background: var(--bg-secondary);
}

.panel-title {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 4px;
}

.search-input {
  padding: 4px 10px;
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 12px;
  outline: none;
  width: 180px;
}
.search-input:focus {
  border-color: var(--success-color);
}
.search-input::placeholder {
  color: var(--text-secondary);
}

.search-clear {
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 12px;
  padding: 2px 6px;
}
.search-clear:hover {
  color: var(--text-primary);
}

.panel-body {
  padding: 12px 16px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.data-table th {
  text-align: left;
  padding: 8px 10px;
  border-bottom: 2px solid var(--border-color);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--text-secondary);
  font-weight: 600;
}

.data-table td {
  padding: 8px 10px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

/* Clickable quote row */
.quote-row {
  cursor: pointer;
  transition: background 0.1s ease;
}
.quote-row:hover {
  background: var(--bg-secondary);
}
.quote-row.selected {
  background: rgba(0, 255, 65, 0.04);
}

.symbol {
  font-weight: 700;
}

.price {
  font-family: var(--font-mono, monospace);
}

.volume {
  color: var(--text-secondary);
  font-family: var(--font-mono, monospace);
}

.detail-arrow {
  font-size: 10px;
  color: var(--text-secondary);
}

.positive { color: var(--success-color); font-weight: 600; }
.negative { color: var(--danger-color); font-weight: 600; }

.impact {
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid currentColor;
}
.impact.high { color: var(--danger-color); }
.impact.medium { color: var(--text-primary); }
.impact.low { color: var(--text-secondary); }

.value {
  font-family: var(--font-mono, monospace);
}

.indicator-name {
  font-weight: 600;
}

/* News */
.news-item {
  display: flex;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}
.news-item:last-child {
  border-bottom: none;
}

.news-importance {
  flex-shrink: 0;
  padding: 2px 8px;
  font-size: 10px;
  font-weight: 600;
  border: 1px solid currentColor;
  height: fit-content;
  margin-top: 2px;
}
.news-importance.high { color: var(--danger-color); }
.news-importance.medium { color: var(--text-primary); }
.news-importance.low { color: var(--text-secondary); }

.news-content {
  flex: 1;
}

.news-title {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.4;
  margin-bottom: 4px;
}

.news-time {
  font-size: 11px;
  color: var(--text-secondary);
}

.date {
  font-family: var(--font-mono, monospace);
  font-size: 11px;
}

/* Gainers / Losers */
.gainers-losers {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 900px) {
  .gainers-losers {
    grid-template-columns: 1fr;
  }
}

.gl-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color);
  font-size: 13px;
}
.gl-item:last-child {
  border-bottom: none;
}

.empty {
  text-align: center;
  padding: 32px;
  color: var(--text-secondary);
  font-size: 13px;
}

/* ===== Technical Detail Panel with SVG Charts ===== */
.detail-panel {
  margin-top: 16px;
  border: 2px solid var(--border-color);
  background: var(--bg-secondary);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 2px solid var(--border-color);
  background: var(--bg-primary);
}

.detail-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-symbol {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.03em;
}

.detail-label {
  font-size: 11px;
  color: var(--text-secondary);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.detail-rec {
  padding: 2px 12px;
  font-size: 12px;
  font-weight: 700;
  border: 2px solid currentColor;
}
.detail-rec.rec-buy {
  color: var(--success-color);
}
.detail-rec.rec-hold {
  color: var(--text-primary);
}
.detail-rec.rec-sell {
  color: var(--danger-color);
}

/* Chart Grid */
.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 16px;
}

@media (max-width: 900px) {
  .chart-grid {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  padding: 12px;
}

.chart-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 8px;
}

.chart-svg {
  width: 100%;
  height: auto;
}

.chart-footer {
  display: flex;
  justify-content: space-between;
  font-size: 9px;
  color: var(--text-secondary);
  margin-top: 4px;
}

/* Detail Summary */
.detail-summary {
  display: flex;
  gap: 24px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-primary);
}

.summary-item {
  display: flex;
  gap: 8px;
  font-size: 11px;
}

.summary-key {
  color: var(--text-secondary);
}

.summary-val {
  font-weight: 600;
  color: var(--text-primary);
}

/* Expand transition */
.expand-enter-active {
  transition: all 0.2s ease;
}
.expand-leave-active {
  transition: all 0.15s ease;
}
.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
