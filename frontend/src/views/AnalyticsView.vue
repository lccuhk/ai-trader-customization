<template>
  <div class="analytics-view">
    <div class="analytics-header">
      <h1>数据分析</h1>
      <div class="period-selector">
        <button 
          v-for="p in periods" 
          :key="p.value" 
          :class="{ active: selectedPeriod === p.value }"
          @click="selectedPeriod = p.value; loadData()"
        >
          {{ p.label }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      加载中...
    </div>

    <div v-else class="analytics-content">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">总交易次数</div>
          <div class="stat-value">{{ analytics?.performance?.total_trades || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">胜率</div>
          <div class="stat-value">{{ (analytics?.performance?.win_rate || 0).toFixed(2) }}%</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">总盈亏</div>
          <div class="stat-value" :class="{ positive: (analytics?.performance?.total_pnl || 0) >= 0 }">
            {{ (analytics?.performance?.total_pnl || 0) >= 0 ? '+' : '' }}${{ (analytics?.performance?.total_pnl || 0).toLocaleString() }}
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">盈亏比</div>
          <div class="stat-value">{{ (analytics?.performance?.profit_factor || 0).toFixed(2) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">夏普比率</div>
          <div class="stat-value">{{ (analytics?.performance?.sharpe_ratio || 0).toFixed(2) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">最大回撤</div>
          <div class="stat-value" class="negative">-{{ (analytics?.performance?.max_drawdown || 0).toFixed(2) }}%</div>
        </div>
      </div>

      <div class="charts-section">
        <div class="chart-card">
          <h3>每日盈亏</h3>
          <div class="chart-container">
            <div class="bar-chart">
              <div 
                v-for="(day, index) in analytics?.daily_stats || []" 
                :key="index" 
                class="bar-item"
              >
                <div 
                  class="bar" 
                  :class="{ positive: day.pnl >= 0, negative: day.pnl < 0 }"
                  :style="{ height: getBarHeight(day.pnl) + '%' }"
                ></div>
                <div class="bar-label">{{ day.date.slice(5) }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <h3>交易分布</h3>
          <div class="pie-chart-container">
            <div class="pie-chart">
              <div class="pie-segment winning" :style="{ '--percent': winPercent + '%' }"></div>
              <div class="pie-segment losing" :style="{ '--percent': (100 - winPercent) + '%' }"></div>
              <div class="pie-center">
                <div class="pie-value">{{ winPercent.toFixed(1) }}%</div>
                <div class="pie-label">胜率</div>
              </div>
            </div>
            <div class="pie-legend">
              <div class="legend-item">
                <span class="legend-dot winning"></span>
                <span>盈利: {{ analytics?.performance?.winning_trades || 0 }}</span>
              </div>
              <div class="legend-item">
                <span class="legend-dot losing"></span>
                <span>亏损: {{ analytics?.performance?.losing_trades || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="details-section">
        <div class="detail-card">
          <h3>交易表现</h3>
          <div class="detail-list">
            <div class="detail-item">
              <span>平均盈利</span>
              <span class="positive">${{ (analytics?.performance?.avg_win || 0).toLocaleString() }}</span>
            </div>
            <div class="detail-item">
              <span>平均亏损</span>
              <span class="negative">${{ (analytics?.performance?.avg_loss || 0).toLocaleString() }}</span>
            </div>
            <div class="detail-item">
              <span>最大单笔盈利</span>
              <span class="positive">${{ (analytics?.performance?.best_trade || 0).toLocaleString() }}</span>
            </div>
            <div class="detail-item">
              <span>最大单笔亏损</span>
              <span class="negative">${{ (analytics?.performance?.worst_trade || 0).toLocaleString() }}</span>
            </div>
          </div>
        </div>

        <div class="detail-card">
          <h3>交易行为</h3>
          <div class="detail-list">
            <div class="detail-item">
              <span>交易品种数</span>
              <span>{{ analytics?.behavior?.symbols_traded?.length || 0 }}</span>
            </div>
            <div class="detail-item">
              <span>最常交易</span>
              <span>{{ analytics?.behavior?.most_traded_symbol || '-' }}</span>
            </div>
            <div class="detail-item">
              <span>平均交易间隔</span>
              <span>{{ formatTimeInterval(analytics?.behavior?.avg_time_between_trades_seconds || 0) }}</span>
            </div>
            <div class="detail-item">
              <span>活跃会话数</span>
              <span>{{ analytics?.behavior?.session_count || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { analyticsService } from '@/services/analytics'
import { useToast } from '@/composables/useToast'
import type { UserAnalytics } from '@/types'

const { error: toastError } = useToast()
const loading = ref(false)
const selectedPeriod = ref(30)
const analytics = ref<UserAnalytics | null>(null)

const periods = [
  { label: '7天', value: 7 },
  { label: '30天', value: 30 },
  { label: '90天', value: 90 },
  { label: '180天', value: 180 }
]

const winPercent = computed(() => {
  const perf = analytics.value?.performance
  if (!perf) return 0
  return perf.win_rate || 0
})

function getBarHeight(value: number) {
  const maxPnl = Math.max(...(analytics.value?.daily_stats?.map(d => Math.abs(d.pnl)) || [1]))
  return Math.min(100, Math.max(5, (Math.abs(value) / maxPnl) * 80))
}

function formatTimeInterval(seconds: number) {
  if (seconds < 60) return `${seconds.toFixed(0)}秒`
  if (seconds < 3600) return `${(seconds / 60).toFixed(0)}分钟`
  if (seconds < 86400) return `${(seconds / 3600).toFixed(1)}小时`
  return `${(seconds / 86400).toFixed(1)}天`
}

async function loadData() {
  loading.value = true
  try {
    const response = await analyticsService.getUserAnalytics({ days: selectedPeriod.value })
    if (response.success && response.data) {
      analytics.value = response.data
    }
  } catch (e: any) {
    toastError(e.message || '加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.analytics-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.analytics-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.period-selector {
  display: flex;
  gap: 4px;
  background: var(--bg-secondary);
  padding: 4px;
  border-radius: 8px;
}

.period-selector button {
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;
}

.period-selector button.active {
  background: var(--primary);
  color: white;
}

.loading {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-value.positive {
  color: var(--success);
}

.stat-value.negative {
  color: var(--danger);
}

.charts-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

@media (max-width: 900px) {
  .charts-section {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
}

.chart-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 20px 0;
}

.chart-container {
  height: 250px;
  display: flex;
  align-items: flex-end;
}

.bar-chart {
  display: flex;
  gap: 4px;
  align-items: flex-end;
  height: 100%;
  width: 100%;
  padding: 0 8px;
}

.bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
}

.bar {
  width: 100%;
  max-width: 24px;
  border-radius: 4px 4px 0 0;
  transition: height 0.3s;
}

.bar.positive {
  background: var(--success);
}

.bar.negative {
  background: var(--danger);
}

.bar-label {
  font-size: 10px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.pie-chart-container {
  display: flex;
  align-items: center;
  gap: 24px;
}

.pie-chart {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: conic-gradient(
    var(--success) 0% var(--percent),
    var(--danger) var(--percent) 100%
  );
  position: relative;
  flex-shrink: 0;
}

.pie-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: var(--bg-card);
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.pie-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.pie-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-secondary);
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot.winning {
  background: var(--success);
}

.legend-dot.losing {
  background: var(--danger);
}

.details-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.detail-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
}

.detail-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.detail-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item span:first-child {
  color: var(--text-secondary);
}

.detail-item span:last-child {
  font-weight: 500;
  color: var(--text-primary);
}

.positive {
  color: var(--success) !important;
}

.negative {
  color: var(--danger) !important;
}
</style>
