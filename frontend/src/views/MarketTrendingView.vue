<template>
  <div class="market-trending">
    <div class="page-header">
      <h1 class="page-title">> TRENDING_MARKETS.EXE</h1>
      <div class="status-bar">
        <span class="status-indicator online">● PRICES_LIVE</span>
        <span class="status-item">LAST_UPDATED: {{ lastUpdated }}</span>
      </div>
    </div>

    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">MARKET:</span>
        <button class="filter-btn" :class="{ active: activeMarket === 'all' }" @click="activeMarket = 'all'">ALL</button>
        <button class="filter-btn" :class="{ active: activeMarket === 'crypto' }" @click="activeMarket = 'crypto'">CRYPTO</button>
        <button class="filter-btn" :class="{ active: activeMarket === 'stocks' }" @click="activeMarket = 'stocks'">STOCKS</button>
        <button class="filter-btn" :class="{ active: activeMarket === 'forex' }" @click="activeMarket = 'forex'">FOREX</button>
      </div>
      <div class="filter-group">
        <span class="filter-label">SORT:</span>
        <button class="filter-btn" :class="{ active: activeSort === 'gainers' }" @click="activeSort = 'gainers'">TOP_GAINERS</button>
        <button class="filter-btn" :class="{ active: activeSort === 'losers' }" @click="activeSort = 'losers'">TOP_LOSERS</button>
        <button class="filter-btn" :class="{ active: activeSort === 'volume' }" @click="activeSort = 'volume'">VOLUME</button>
      </div>
    </div>

    <div class="trending-grid">
      <div class="trending-panel">
        <div class="panel-header gainers">
          <span class="panel-title">> TOP_GAINERS</span>
          <span class="panel-icon">▲</span>
        </div>
        <div class="panel-body">
          <div class="trending-item" v-for="(item, index) in topGainers" :key="item.id">
            <span class="item-rank">{{ index + 1 }}</span>
            <div class="item-info">
              <span class="item-symbol">${{ item.symbol }}</span>
              <span class="item-name">{{ item.name }}</span>
            </div>
            <div class="item-price">${{ item.price.toLocaleString() }}</div>
            <div class="item-change positive">+{{ item.changePercent }}%</div>
          </div>
        </div>
      </div>

      <div class="trending-panel">
        <div class="panel-header losers">
          <span class="panel-title">> TOP_LOSERS</span>
          <span class="panel-icon">▼</span>
        </div>
        <div class="panel-body">
          <div class="trending-item" v-for="(item, index) in topLosers" :key="item.id">
            <span class="item-rank">{{ index + 1 }}</span>
            <div class="item-info">
              <span class="item-symbol">${{ item.symbol }}</span>
              <span class="item-name">{{ item.name }}</span>
            </div>
            <div class="item-price">${{ item.price.toLocaleString() }}</div>
            <div class="item-change negative">{{ item.changePercent }}%</div>
          </div>
        </div>
      </div>

      <div class="trending-panel">
        <div class="panel-header volume">
          <span class="panel-title">> TOP_VOLUME</span>
          <span class="panel-icon">📊</span>
        </div>
        <div class="panel-body">
          <div class="trending-item" v-for="(item, index) in topVolume" :key="item.id">
            <span class="item-rank">{{ index + 1 }}</span>
            <div class="item-info">
              <span class="item-symbol">${{ item.symbol }}</span>
              <span class="item-name">{{ item.name }}</span>
            </div>
            <div class="item-volume">${{ formatVolume(item.volume) }}</div>
            <div class="item-change" :class="item.changePercent >= 0 ? 'positive' : 'negative'">
              {{ item.changePercent >= 0 ? '+' : '' }}{{ item.changePercent }}%
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">> FULL_MARKET_DATA</span>
      </div>
      <div class="panel-body">
        <table class="market-table">
          <thead>
            <tr>
              <th>RANK</th>
              <th>SYMBOL</th>
              <th>NAME</th>
              <th class="text-right">PRICE</th>
              <th class="text-right">CHANGE_24H</th>
              <th class="text-right">MARKET_CAP</th>
              <th class="text-right">VOLUME_24H</th>
              <th class="text-right">SUPPLY</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in filteredMarketData" :key="item.id">
              <td class="td-rank">{{ index + 1 }}</td>
              <td class="td-symbol">${{ item.symbol }}</td>
              <td class="td-name">{{ item.name }}</td>
              <td class="td-price text-right">${{ item.price.toLocaleString() }}</td>
              <td class="td-change text-right" :class="item.changePercent >= 0 ? 'positive' : 'negative'">
                {{ item.changePercent >= 0 ? '+' : '' }}{{ item.changePercent }}%
              </td>
              <td class="td-marketcap text-right">${{ formatVolume(item.marketCap) }}</td>
              <td class="td-volume text-right">${{ formatVolume(item.volume) }}</td>
              <td class="td-supply text-right">{{ formatVolume(item.supply) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const lastUpdated = ref(new Date().toLocaleTimeString())
const activeMarket = ref('all')
const activeSort = ref('gainers')

const marketData = ref([
  { id: 1, symbol: 'BTC', name: 'Bitcoin', price: 52345.67, changePercent: 8.45, marketCap: 1025000000000, volume: 45600000000, supply: 19600000, market: 'crypto' },
  { id: 2, symbol: 'ETH', name: 'Ethereum', price: 2845.32, changePercent: 5.23, marketCap: 342000000000, volume: 23400000000, supply: 120000000, market: 'crypto' },
  { id: 3, symbol: 'SOL', name: 'Solana', price: 142.56, changePercent: 12.34, marketCap: 62000000000, volume: 5600000000, supply: 435000000, market: 'crypto' },
  { id: 4, symbol: 'NVDA', name: 'NVIDIA', price: 875.43, changePercent: -2.15, marketCap: 2160000000000, volume: 32000000000, supply: 2467000000, market: 'stocks' },
  { id: 5, symbol: 'TSLA', name: 'Tesla', price: 215.67, changePercent: -5.43, marketCap: 685000000000, volume: 18500000000, supply: 3175000000, market: 'stocks' },
  { id: 6, symbol: 'AAPL', name: 'Apple', price: 185.32, changePercent: 1.23, marketCap: 2890000000000, volume: 28000000000, supply: 15600000000, market: 'stocks' },
  { id: 7, symbol: 'ADA', name: 'Cardano', price: 0.4523, changePercent: -3.21, marketCap: 15800000000, volume: 890000000, supply: 35000000000, market: 'crypto' },
  { id: 8, symbol: 'DOT', name: 'Polkadot', price: 7.82, changePercent: 4.56, marketCap: 10200000000, volume: 560000000, supply: 1300000000, market: 'crypto' },
  { id: 9, symbol: 'MSFT', name: 'Microsoft', price: 412.56, changePercent: 0.87, marketCap: 3080000000000, volume: 21000000000, supply: 7469000000, market: 'stocks' },
  { id: 10, symbol: 'GOOGL', name: 'Alphabet', price: 156.78, changePercent: -1.34, marketCap: 1960000000000, volume: 15600000000, supply: 12500000000, market: 'stocks' },
  { id: 11, symbol: 'XRP', name: 'Ripple', price: 0.5234, changePercent: 2.34, marketCap: 28500000000, volume: 1200000000, supply: 54500000000, market: 'crypto' },
  { id: 12, symbol: 'AVAX', name: 'Avalanche', price: 38.45, changePercent: 7.89, marketCap: 14800000000, volume: 780000000, supply: 385000000, market: 'crypto' }
])

const filteredMarketData = computed(() => {
  let data = [...marketData.value]
  
  if (activeMarket.value !== 'all') {
    data = data.filter(item => item.market === activeMarket.value)
  }
  
  if (activeSort.value === 'gainers') {
    data.sort((a, b) => b.changePercent - a.changePercent)
  } else if (activeSort.value === 'losers') {
    data.sort((a, b) => a.changePercent - b.changePercent)
  } else if (activeSort.value === 'volume') {
    data.sort((a, b) => b.volume - a.volume)
  }
  
  return data
})

const topGainers = computed(() => {
  return [...marketData.value]
    .filter(item => activeMarket.value === 'all' || item.market === activeMarket.value)
    .sort((a, b) => b.changePercent - a.changePercent)
    .slice(0, 5)
})

const topLosers = computed(() => {
  return [...marketData.value]
    .filter(item => activeMarket.value === 'all' || item.market === activeMarket.value)
    .sort((a, b) => a.changePercent - b.changePercent)
    .slice(0, 5)
})

const topVolume = computed(() => {
  return [...marketData.value]
    .filter(item => activeMarket.value === 'all' || item.market === activeMarket.value)
    .sort((a, b) => b.volume - a.volume)
    .slice(0, 5)
})

function formatVolume(value: number): string {
  if (value >= 1e12) return (value / 1e12).toFixed(2) + 'T'
  if (value >= 1e9) return (value / 1e9).toFixed(2) + 'B'
  if (value >= 1e6) return (value / 1e6).toFixed(2) + 'M'
  if (value >= 1e3) return (value / 1e3).toFixed(2) + 'K'
  return value.toString()
}

let updateInterval: number

onMounted(() => {
  updateInterval = window.setInterval(() => {
    lastUpdated.value = new Date().toLocaleTimeString()
    marketData.value.forEach(item => {
      const change = (Math.random() - 0.5) * 0.02 * item.price
      item.price = Math.max(0.0001, item.price + change)
      item.changePercent += (Math.random() - 0.5) * 0.5
      item.changePercent = Math.round(item.changePercent * 100) / 100
    })
  }, 5000)
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
})
</script>

<style scoped>
.market-trending {
  padding: 24px;
  max-width: 1600px;
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

.trending-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.trending-panel {
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 2px solid var(--text-primary);
  color: var(--bg-primary);
}

.panel-header.gainers {
  background: var(--success-color);
  border-color: var(--success-color);
}

.panel-header.losers {
  background: var(--danger-color);
  border-color: var(--danger-color);
}

.panel-header.volume {
  background: var(--text-primary);
  border-color: var(--text-primary);
}

.panel-title {
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 1px;
}

.panel-icon {
  font-size: 14px;
}

.panel-body {
  padding: 0;
}

.trending-item {
  display: grid;
  grid-template-columns: 30px 1fr auto auto;
  gap: 12px;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  transition: background 0.1s ease;
}

.trending-item:hover {
  background: var(--bg-secondary);
}

.trending-item:last-child {
  border-bottom: none;
}

.item-rank {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 14px;
  color: var(--text-secondary);
}

.item-info {
  display: flex;
  flex-direction: column;
}

.item-symbol {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 13px;
}

.item-name {
  font-size: 10px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
}

.item-price,
.item-volume {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 13px;
  text-align: right;
}

.item-change {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 13px;
  text-align: right;
  min-width: 70px;
}

.item-change.positive {
  color: var(--success-color);
}

.item-change.negative {
  color: var(--danger-color);
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
  padding: 0;
  overflow-x: auto;
}

.market-table {
  width: 100%;
  border-collapse: collapse;
}

.market-table th,
.market-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  font-family: var(--font-mono);
  font-size: 12px;
}

.market-table th {
  background: var(--bg-secondary);
  font-weight: 700;
  font-size: 10px;
  letter-spacing: 1px;
  color: var(--text-secondary);
}

.market-table tbody tr:hover {
  background: var(--bg-secondary);
}

.text-right {
  text-align: right;
}

.td-rank {
  color: var(--text-secondary);
  font-weight: 700;
}

.td-symbol {
  font-weight: 700;
}

.td-name {
  color: var(--text-secondary);
}

.td-change.positive {
  color: var(--success-color);
}

.td-change.negative {
  color: var(--danger-color);
}

@media (max-width: 1024px) {
  .trending-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
    gap: 16px;
  }
}
</style>
