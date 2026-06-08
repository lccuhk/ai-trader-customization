<template>
  <div class="market-indicators">
    <div class="page-header">
      <h1 class="page-title">> ECONOMIC_INDICATORS.EXE</h1>
      <div class="status-bar">
        <span class="status-indicator online">● DATA_LIVE</span>
        <span class="status-item">LAST_UPDATED: {{ lastUpdated }}</span>
      </div>
    </div>

    <div class="indicators-grid">
      <div class="indicator-card" v-for="indicator in indicators" :key="indicator.id">
        <div class="indicator-header">
          <span class="indicator-name">{{ indicator.name }}</span>
          <span class="indicator-country">{{ indicator.country }}</span>
        </div>
        <div class="indicator-value" :class="indicator.trend">
          {{ indicator.value }}<span class="indicator-unit">{{ indicator.unit }}</span>
        </div>
        <div class="indicator-change" :class="indicator.changeClass">
          <span class="change-arrow">{{ indicator.change > 0 ? '▲' : indicator.change < 0 ? '▼' : '—' }}</span>
          <span class="change-value">{{ Math.abs(indicator.change) }}%</span>
          <span class="change-period">{{ indicator.period }}</span>
        </div>
        <div class="indicator-chart">
          <div class="chart-bars">
            <div class="chart-bar" v-for="(bar, i) in indicator.history" :key="i" 
                 :style="{ height: bar + '%' }" :class="bar > 50 ? 'positive' : 'negative'">
            </div>
          </div>
        </div>
        <div class="indicator-footer">
          <span class="indicator-next">NEXT: {{ indicator.nextRelease }}</span>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">> INDICATOR_COMPARISON</span>
      </div>
      <div class="panel-body">
        <table class="comparison-table">
          <thead>
            <tr>
              <th>INDICATOR</th>
              <th>COUNTRY</th>
              <th>CURRENT</th>
              <th>PREVIOUS</th>
              <th>FORECAST</th>
              <th>CHANGE</th>
              <th>TREND</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in comparisonData" :key="row.id">
              <td class="td-name">{{ row.name }}</td>
              <td class="td-country">{{ row.country }}</td>
              <td class="td-value">{{ row.current }}</td>
              <td class="td-value">{{ row.previous }}</td>
              <td class="td-value">{{ row.forecast }}</td>
              <td class="td-change" :class="row.changeClass">{{ row.change }}</td>
              <td class="td-trend">
                <span class="trend-indicator" :class="row.trend"></span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const lastUpdated = ref(new Date().toLocaleTimeString())

const indicators = ref([
  {
    id: 1,
    name: 'CPI_INFLATION',
    country: 'US',
    value: '2.1',
    unit: '%',
    change: -0.1,
    changeClass: 'positive',
    trend: 'down',
    period: 'MoM',
    nextRelease: 'Feb 15, 2024',
    history: [65, 72, 68, 55, 48, 42, 38, 35, 32, 28]
  },
  {
    id: 2,
    name: 'UNEMPLOYMENT',
    country: 'US',
    value: '3.7',
    unit: '%',
    change: 0.1,
    changeClass: 'negative',
    trend: 'up',
    period: 'MoM',
    nextRelease: 'Feb 02, 2024',
    history: [30, 32, 31, 33, 35, 34, 36, 37, 38, 37]
  },
  {
    id: 3,
    name: 'GDP_GROWTH',
    country: 'US',
    value: '3.3',
    unit: '%',
    change: 0.5,
    changeClass: 'positive',
    trend: 'up',
    period: 'QoQ',
    nextRelease: 'Feb 28, 2024',
    history: [20, 25, 28, 30, 28, 32, 35, 33, 36, 38]
  },
  {
    id: 4,
    name: 'FED_FUNDS_RATE',
    country: 'US',
    value: '5.25',
    unit: '%',
    change: 0,
    changeClass: 'neutral',
    trend: 'stable',
    period: '—',
    nextRelease: 'Jan 31, 2024',
    history: [0, 0, 10, 25, 40, 55, 65, 70, 72, 72]
  },
  {
    id: 5,
    name: 'RETAIL_SALES',
    country: 'US',
    value: '+0.4',
    unit: '%',
    change: 0.2,
    changeClass: 'positive',
    trend: 'up',
    period: 'MoM',
    nextRelease: 'Feb 15, 2024',
    history: [20, 25, 22, 30, 28, 35, 32, 38, 40, 42]
  },
  {
    id: 6,
    name: 'PPI',
    country: 'US',
    value: '+0.4',
    unit: '%',
    change: 0.3,
    changeClass: 'negative',
    trend: 'up',
    period: 'MoM',
    nextRelease: 'Feb 16, 2024',
    history: [10, 15, 12, 18, 22, 25, 28, 30, 32, 35]
  }
])

const comparisonData = ref([
  { id: 1, name: 'CPI', country: 'US', current: '2.1%', previous: '2.2%', forecast: '2.1%', change: '-0.1%', changeClass: 'positive', trend: 'down' },
  { id: 2, name: 'CPI', country: 'EU', current: '2.4%', previous: '2.6%', forecast: '2.3%', change: '-0.2%', changeClass: 'positive', trend: 'down' },
  { id: 3, name: 'CPI', country: 'UK', current: '2.8%', previous: '3.0%', forecast: '2.7%', change: '-0.2%', changeClass: 'positive', trend: 'down' },
  { id: 4, name: 'UNEMPLOYMENT', country: 'US', current: '3.7%', previous: '3.6%', forecast: '3.7%', change: '+0.1%', changeClass: 'negative', trend: 'up' },
  { id: 5, name: 'UNEMPLOYMENT', country: 'EU', current: '6.1%', previous: '6.0%', forecast: '6.1%', change: '+0.1%', changeClass: 'negative', trend: 'up' },
  { id: 6, name: 'GDP', country: 'US', current: '3.3%', previous: '2.8%', forecast: '3.0%', change: '+0.5%', changeClass: 'positive', trend: 'up' },
  { id: 7, name: 'GDP', country: 'CN', current: '5.2%', previous: '4.9%', forecast: '5.0%', change: '+0.3%', changeClass: 'positive', trend: 'up' },
  { id: 8, name: 'INTEREST_RATE', country: 'US', current: '5.25%', previous: '5.25%', forecast: '5.25%', change: '0.00%', changeClass: 'neutral', trend: 'stable' },
  { id: 9, name: 'INTEREST_RATE', country: 'EU', current: '4.00%', previous: '4.00%', forecast: '4.00%', change: '0.00%', changeClass: 'neutral', trend: 'stable' }
])

let updateInterval: number

onMounted(() => {
  updateInterval = window.setInterval(() => {
    lastUpdated.value = new Date().toLocaleTimeString()
  }, 60000)
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
})
</script>

<style scoped>
.market-indicators {
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

.indicators-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.indicator-card {
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
  padding: 20px;
}

.indicator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.indicator-name {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 13px;
}

.indicator-country {
  font-size: 10px;
  padding: 2px 6px;
  background: var(--bg-secondary);
  font-family: var(--font-mono);
}

.indicator-value {
  font-size: 36px;
  font-weight: 700;
  font-family: var(--font-mono);
  margin-bottom: 8px;
}

.indicator-value.up {
  color: var(--danger-color);
}

.indicator-value.down {
  color: var(--success-color);
}

.indicator-unit {
  font-size: 16px;
  color: var(--text-secondary);
  margin-left: 4px;
}

.indicator-change {
  display: flex;
  align-items: center;
  gap: 4px;
  font-family: var(--font-mono);
  font-size: 12px;
  margin-bottom: 16px;
}

.indicator-change.positive {
  color: var(--success-color);
}

.indicator-change.negative {
  color: var(--danger-color);
}

.indicator-change.neutral {
  color: var(--text-secondary);
}

.change-period {
  color: var(--text-secondary);
  margin-left: 4px;
}

.indicator-chart {
  height: 60px;
  margin-bottom: 12px;
}

.chart-bars {
  display: flex;
  align-items: flex-end;
  height: 100%;
  gap: 2px;
}

.chart-bar {
  flex: 1;
  background: var(--text-secondary);
  min-height: 4px;
  transition: height 0.3s ease;
}

.chart-bar.positive {
  background: var(--success-color);
}

.chart-bar.negative {
  background: var(--danger-color);
}

.indicator-footer {
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.indicator-next {
  font-size: 10px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
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

.comparison-table {
  width: 100%;
  border-collapse: collapse;
}

.comparison-table th,
.comparison-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  font-family: var(--font-mono);
  font-size: 12px;
}

.comparison-table th {
  background: var(--bg-secondary);
  font-weight: 700;
  font-size: 10px;
  letter-spacing: 1px;
  color: var(--text-secondary);
}

.comparison-table tbody tr:hover {
  background: var(--bg-secondary);
}

.td-name {
  font-weight: 700;
}

.td-country {
  color: var(--text-secondary);
}

.td-change.positive {
  color: var(--success-color);
}

.td-change.negative {
  color: var(--danger-color);
}

.td-change.neutral {
  color: var(--text-secondary);
}

.trend-indicator {
  display: inline-block;
  width: 0;
  height: 0;
}

.trend-indicator.up {
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-bottom: 10px solid var(--danger-color);
}

.trend-indicator.down {
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 10px solid var(--success-color);
}

.trend-indicator.stable {
  width: 12px;
  height: 3px;
  background: var(--text-secondary);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .indicators-grid {
    grid-template-columns: 1fr;
  }
}
</style>
