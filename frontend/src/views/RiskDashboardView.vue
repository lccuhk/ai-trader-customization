<template>
  <div class="risk-dashboard">
    <div class="page-header">
      <h1 class="page-title">> RISK_DASHBOARD.EXE</h1>
      <div class="status-bar">
        <span class="status-indicator online">● SYSTEM_ONLINE</span>
        <span class="status-item">RISK_LEVEL: <span :class="riskLevelClass">{{ riskLevel }}</span></span>
        <span class="status-item">LAST_UPDATED: {{ lastUpdated }}</span>
      </div>
    </div>

    <div class="metrics-grid">
      <div class="metric-card" v-for="metric in metrics" :key="metric.id">
        <div class="metric-header">
          <span class="metric-label">// {{ metric.label }}</span>
          <span class="metric-badge" :class="metric.status">{{ metric.status.toUpperCase() }}</span>
        </div>
        <div class="metric-value" :class="metric.status">
          {{ metric.value }}<span class="metric-unit">{{ metric.unit }}</span>
        </div>
        <div class="metric-bar">
          <div class="metric-bar-fill" :style="{ width: metric.percent + '%' }" :class="metric.status"></div>
        </div>
        <div class="metric-threshold">
          <span>THRESHOLD: {{ metric.threshold }}</span>
        </div>
      </div>
    </div>

    <div class="content-grid">
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">> EXPOSURE_BREAKDOWN</span>
        </div>
        <div class="panel-body">
          <div class="exposure-item" v-for="item in exposure" :key="item.symbol">
            <div class="exposure-info">
              <span class="exposure-symbol">${{ item.symbol }}</span>
              <span class="exposure-name">{{ item.name }}</span>
            </div>
            <div class="exposure-bar">
              <div class="exposure-bar-fill" :style="{ width: item.percent + '%' }"></div>
            </div>
            <div class="exposure-value">{{ item.percent }}%</div>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">> ACTIVE_ALERTS</span>
          <span class="alert-count">{{ activeAlerts.length }}</span>
        </div>
        <div class="panel-body">
          <div class="alert-item" v-for="alert in activeAlerts" :key="alert.id">
            <span class="alert-icon" :class="alert.severity">●</span>
            <div class="alert-content">
              <span class="alert-title">{{ alert.title }}</span>
              <span class="alert-desc">{{ alert.description }}</span>
            </div>
            <span class="alert-time">{{ alert.time }}</span>
          </div>
          <div class="empty-state" v-if="activeAlerts.length === 0">
            // NO_ACTIVE_ALERTS
          </div>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">> HISTORICAL_RISK_METRICS</span>
      </div>
      <div class="panel-body">
        <div class="chart-container">
          <div class="chart-placeholder">
            <div class="chart-line">
              <div class="chart-point" v-for="(point, i) in chartData" :key="i" 
                   :style="{ left: (i * 10) + '%', bottom: point + '%' }">
              </div>
            </div>
            <div class="chart-labels">
              <span v-for="i in 10" :key="i">{{ i * 10 }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

// @ts-ignore: unused variable for i18n
const { t } = useI18n()

const lastUpdated = ref(new Date().toLocaleTimeString())

const riskLevel = ref('MODERATE')
const riskLevelClass = computed(() => ({
  'status-good': riskLevel.value === 'LOW',
  'status-warning': riskLevel.value === 'MODERATE',
  'status-danger': riskLevel.value === 'HIGH'
}))

const metrics = ref([
  { id: 1, label: 'CONCENTRATION_RISK', value: '28.5', unit: '%', status: 'warning', percent: 71, threshold: '40%' },
  { id: 2, label: 'NET_EXPOSURE', value: '45.2', unit: 'K', status: 'good', percent: 45, threshold: '100K' },
  { id: 3, label: 'MAX_DRAWDOWN', value: '-12.3', unit: '%', status: 'warning', percent: 61, threshold: '-20%' },
  { id: 4, label: 'WIN_RATE', value: '68.4', unit: '%', status: 'good', percent: 68, threshold: '50%' },
  { id: 5, label: 'SHARPE_RATIO', value: '1.85', unit: '', status: 'good', percent: 74, threshold: '1.5' },
  { id: 6, label: 'VAR_95', value: '-8.2', unit: '%', status: 'warning', percent: 59, threshold: '-10%' }
])

const exposure = ref([
  { symbol: 'BTC', name: 'Bitcoin', percent: 35 },
  { symbol: 'ETH', name: 'Ethereum', percent: 25 },
  { symbol: 'SOL', name: 'Solana', percent: 15 },
  { symbol: 'ADA', name: 'Cardano', percent: 12 },
  { symbol: 'DOT', name: 'Polkadot', percent: 8 },
  { symbol: 'USDT', name: 'Tether', percent: 5 }
])

const activeAlerts = ref([
  { id: 1, severity: 'warning', title: 'BTC_EXPOSURE_HIGH', description: 'Bitcoin position exceeds 30% of portfolio', time: '2m_ago' },
  { id: 2, severity: 'info', title: 'VOLATILITY_SPIKE', description: 'Market volatility increased 45% in last hour', time: '15m_ago' }
])

const chartData = ref([15, 22, 18, 25, 30, 28, 35, 42, 38, 45])

setInterval(() => {
  lastUpdated.value = new Date().toLocaleTimeString()
}, 5000)
</script>

<style scoped>
.risk-dashboard {
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
}

.page-header {
  border-bottom: 2px solid var(--text-primary);
  padding-bottom: 16px;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  letter-spacing: 2px;
  margin-bottom: 12px;
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

.status-good {
  color: var(--success-color);
}

.status-warning {
  color: var(--warning-color);
}

.status-danger {
  color: var(--danger-color);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.metric-card {
  border: 2px solid var(--text-primary);
  padding: 20px;
  background: var(--bg-primary);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.metric-label {
  font-size: 11px;
  color: var(--text-secondary);
  letter-spacing: 1px;
}

.metric-badge {
  font-size: 10px;
  padding: 2px 8px;
  border: 1px solid currentColor;
  font-family: var(--font-mono);
}

.metric-value {
  font-size: 36px;
  font-weight: 700;
  font-family: var(--font-mono);
  margin-bottom: 12px;
}

.metric-unit {
  font-size: 16px;
  color: var(--text-secondary);
  margin-left: 4px;
}

.metric-bar {
  height: 8px;
  background: var(--bg-secondary);
  margin-bottom: 8px;
}

.metric-bar-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.metric-bar-fill.good {
  background: var(--success-color);
}

.metric-bar-fill.warning {
  background: var(--warning-color);
}

.metric-bar-fill.danger {
  background: var(--danger-color);
}

.metric-threshold {
  font-size: 10px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.panel {
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.alert-count {
  background: var(--danger-color);
  color: var(--bg-primary);
  padding: 2px 8px;
  font-size: 11px;
  font-family: var(--font-mono);
}

.panel-body {
  padding: 16px;
}

.exposure-item {
  display: grid;
  grid-template-columns: 150px 1fr 60px;
  gap: 12px;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color);
}

.exposure-item:last-child {
  border-bottom: none;
}

.exposure-info {
  display: flex;
  flex-direction: column;
}

.exposure-symbol {
  font-family: var(--font-mono);
  font-weight: 700;
}

.exposure-name {
  font-size: 11px;
  color: var(--text-secondary);
}

.exposure-bar {
  height: 8px;
  background: var(--bg-secondary);
}

.exposure-bar-fill {
  height: 100%;
  background: var(--success-color);
}

.exposure-value {
  text-align: right;
  font-family: var(--font-mono);
  font-weight: 700;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.alert-item:last-child {
  border-bottom: none;
}

.alert-icon.warning {
  color: var(--warning-color);
}

.alert-icon.danger {
  color: var(--danger-color);
}

.alert-icon.info {
  color: var(--text-secondary);
}

.alert-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.alert-title {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 13px;
}

.alert-desc {
  font-size: 11px;
  color: var(--text-secondary);
}

.alert-time {
  font-size: 10px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  font-size: 12px;
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

.chart-line {
  position: relative;
  height: 100%;
  border-bottom: 1px dashed var(--border-color);
}

.chart-point {
  position: absolute;
  width: 8px;
  height: 8px;
  background: var(--success-color);
  transform: translate(-50%, 50%);
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

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .exposure-item {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .exposure-value {
    text-align: left;
  }
}
</style>
