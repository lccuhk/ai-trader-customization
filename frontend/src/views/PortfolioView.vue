<template>
  <div class="portfolio-view">
    <div class="portfolio-header">
      <h1>{{ t('portfolio.title') }}</h1>
      <div class="mode-toggle">
        <button 
          :class="{ active: isSimulation }" 
          @click="switchMode(true)"
        >
          {{ t('trading.simulation') }}
        </button>
        <button 
          :class="{ active: !isSimulation }" 
          @click="switchMode(false)"
        >
          {{ t('trading.real') }}
        </button>
      </div>
    </div>

    <div v-if="tradingStore.loading" class="loading">
      {{ t('common.loading') }}
    </div>

    <div v-else-if="tradingStore.error" class="error">
      {{ tradingStore.error }}
    </div>

    <div v-else class="portfolio-content">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">{{ t('portfolio.totalAssets') }}</div>
          <div class="stat-value">${{ (tradingStore.portfolio?.total_value || 0).toLocaleString() }}</div>
          <div class="stat-change" :class="{ positive: (tradingStore.portfolio?.total_pnl || 0) >= 0 }">
            {{ (tradingStore.portfolio?.total_pnl || 0) >= 0 ? '+' : '' }}${{ (tradingStore.portfolio?.total_pnl || 0).toLocaleString() }}
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-label">{{ t('portfolio.availableBalance') }}</div>
          <div class="stat-value">${{ (tradingStore.portfolio?.total_balance || 0).toLocaleString() }}</div>
        </div>

        <div class="stat-card">
          <div class="stat-label">{{ t('portfolio.positionValue') }}</div>
          <div class="stat-value">${{ tradingStore.totalPositionValue.toLocaleString() }}</div>
        </div>

        <div class="stat-card">
          <div class="stat-label">{{ t('trading.unrealizedPnl') }}</div>
          <div class="stat-value" :class="{ positive: tradingStore.totalUnrealizedPnl >= 0, negative: tradingStore.totalUnrealizedPnl < 0 }">
            {{ tradingStore.totalUnrealizedPnl >= 0 ? '+' : '' }}${{ tradingStore.totalUnrealizedPnl.toLocaleString() }}
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-label">{{ t('risk.winRate') }}</div>
          <div class="stat-value">{{ (tradingStore.portfolio?.win_rate || 0).toFixed(2) }}%</div>
        </div>

        <div class="stat-card">
          <div class="stat-label">{{ t('portfolio.totalTrades') }}</div>
          <div class="stat-value">{{ tradingStore.portfolio?.total_trades || 0 }}</div>
        </div>
      </div>

      <div class="portfolio-sections">
        <div class="section">
          <div class="section-header">
            <h2>{{ t('trading.positions') }}</h2>
            <span class="count">{{ tradingStore.positions.length }} {{ t('common.total') }}</span>
          </div>
          <div v-if="tradingStore.positions.length === 0" class="empty-state">
            {{ t('common.noData') }}
          </div>
          <div v-else class="positions-table">
            <table>
              <thead>
                <tr>
                  <th>{{ t('trading.symbol') }}</th>
                  <th>{{ t('trading.quantity') }}</th>
                  <th>{{ t('trading.averagePrice') }}</th>
                  <th>{{ t('trading.currentPrice') }}</th>
                  <th>{{ t('trading.marketValue') }}</th>
                  <th>{{ t('trading.unrealizedPnl') }}</th>
                  <th>{{ t('trading.pnlPercent') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="position in tradingStore.positions" :key="position.id">
                  <td class="symbol">{{ position.symbol }}</td>
                  <td>{{ position.quantity }}</td>
                  <td>${{ position.avg_price.toLocaleString() }}</td>
                  <td>${{ (position.current_price || 0).toLocaleString() }}</td>
                  <td>${{ ((position.current_price || 0) * position.quantity).toLocaleString() }}</td>
                  <td :class="{ positive: (position.unrealized_pnl || 0) >= 0, negative: (position.unrealized_pnl || 0) < 0 }">
                    {{ (position.unrealized_pnl || 0) >= 0 ? '+' : '' }}${{ (position.unrealized_pnl || 0).toLocaleString() }}
                  </td>
                  <td :class="{ positive: (position.unrealized_pnl_percent || 0) >= 0, negative: (position.unrealized_pnl_percent || 0) < 0 }">
                    {{ (position.unrealized_pnl_percent || 0) >= 0 ? '+' : '' }}{{ (position.unrealized_pnl_percent || 0).toFixed(2) }}%
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="section">
          <div class="section-header">
            <h2>{{ t('portfolio.recentTrades') }}</h2>
            <router-link to="/trading" class="view-all">{{ t('common.more') }}</router-link>
          </div>
          <div v-if="tradingStore.trades.length === 0" class="empty-state">
            {{ t('common.noData') }}
          </div>
          <div v-else class="trades-list">
            <div 
              v-for="trade in tradingStore.trades.slice(0, 10)" 
              :key="trade.id" 
              class="trade-item"
            >
              <div class="trade-info">
                <span class="symbol">{{ trade.symbol }}</span>
                <span class="side" :class="trade.side">
                  {{ trade.side === 'buy' ? t('trading.buy') : t('trading.sell') }}
                </span>
                <span class="quantity">{{ trade.quantity }}</span>
              </div>
              <div class="trade-price">
                ${{ trade.price.toLocaleString() }}
              </div>
              <div class="trade-pnl" v-if="trade.pnl !== undefined" :class="{ positive: trade.pnl >= 0, negative: trade.pnl < 0 }">
                {{ trade.pnl >= 0 ? '+' : '' }}${{ trade.pnl.toLocaleString() }}
              </div>
              <div class="trade-time">
                {{ formatTime(trade.created_at) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTradingStore } from '@/stores/trading'
const { t } = useI18n()
const tradingStore = useTradingStore()

const isSimulation = ref(true)

async function switchMode(simulation: boolean) {
  isSimulation.value = simulation
  await tradingStore.loadPortfolio(simulation)
}

function formatTime(time: string) {
  return new Date(time).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(async () => {
  await tradingStore.loadPortfolio(isSimulation.value)
})
</script>

<style scoped>
.portfolio-view {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.portfolio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.portfolio-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
}

.mode-toggle {
  display: flex;
  gap: 8px;
  background: var(--bg-secondary);
  padding: 4px;
  border-radius: 8px;
}

.mode-toggle button {
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.mode-toggle button.active {
  background: var(--primary);
  color: white;
}

.loading, .error {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
}

.error {
  color: var(--danger);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.stat-change {
  font-size: 14px;
  color: var(--text-secondary);
}

.stat-change.positive {
  color: var(--success);
}

.positive {
  color: var(--success);
}

.negative {
  color: var(--danger);
}

.portfolio-sections {
  display: grid;
  gap: 24px;
}

.section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.count {
  color: var(--text-secondary);
  font-size: 14px;
}

.view-all {
  color: var(--primary);
  text-decoration: none;
  font-size: 14px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.positions-table {
  overflow-x: auto;
}

.positions-table table {
  width: 100%;
  border-collapse: collapse;
}

.positions-table th,
.positions-table td {
  padding: 12px;
  text-align: right;
  border-bottom: 1px solid var(--border-color);
}

.positions-table th:first-child,
.positions-table td:first-child {
  text-align: left;
}

.positions-table th {
  font-weight: 500;
  color: var(--text-secondary);
  font-size: 13px;
}

.positions-table td {
  color: var(--text-primary);
  font-size: 14px;
}

.positions-table .symbol {
  font-weight: 600;
}

.trades-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trade-item {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 12px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
  align-items: center;
}

.trade-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trade-info .symbol {
  font-weight: 600;
  color: var(--text-primary);
}

.trade-info .side {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.trade-info .side.buy {
  background: rgba(34, 197, 94, 0.1);
  color: var(--success);
}

.trade-info .side.sell {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
}

.trade-info .quantity {
  color: var(--text-secondary);
  font-size: 14px;
}

.trade-price {
  color: var(--text-primary);
  font-weight: 500;
}

.trade-pnl {
  font-weight: 600;
}

.trade-time {
  color: var(--text-secondary);
  font-size: 13px;
  text-align: right;
}
</style>
