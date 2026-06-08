<template>
  <div class="strategies">
    <div class="page-header">
      <h1 class="page-title">> STRATEGY_MANAGER.EXE</h1>
      <div class="header-actions">
        <button class="btn-primary" @click="showCreateModal = true">
          [ + NEW_STRATEGY ]
        </button>
      </div>
    </div>

    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">TYPE:</span>
        <button class="filter-btn" :class="{ active: activeType === 'all' }" @click="activeType = 'all'">ALL</button>
        <button class="filter-btn" :class="{ active: activeType === 'trend' }" @click="activeType = 'trend'">TREND</button>
        <button class="filter-btn" :class="{ active: activeType === 'mean_reversion' }" @click="activeType = 'mean_reversion'">MEAN_REVERSION</button>
        <button class="filter-btn" :class="{ active: activeType === 'arbitrage' }" @click="activeType = 'arbitrage'">ARBITRAGE</button>
        <button class="filter-btn" :class="{ active: activeType === 'momentum' }" @click="activeType = 'momentum'">MOMENTUM</button>
      </div>
      <div class="filter-group">
        <span class="filter-label">STATUS:</span>
        <button class="filter-btn" :class="{ active: activeStatus === 'all' }" @click="activeStatus = 'all'">ALL</button>
        <button class="filter-btn" :class="{ active: activeStatus === 'active' }" @click="activeStatus = 'active'">ACTIVE</button>
        <button class="filter-btn" :class="{ active: activeStatus === 'paused' }" @click="activeStatus = 'paused'">PAUSED</button>
        <button class="filter-btn" :class="{ active: activeStatus === 'draft' }" @click="activeStatus = 'draft'">DRAFT</button>
      </div>
    </div>

    <div class="strategies-grid">
      <div class="strategy-card" v-for="strategy in filteredStrategies" :key="strategy.id">
        <div class="card-header">
          <div class="card-title-row">
            <span class="card-name">{{ strategy.name }}</span>
            <span class="card-status" :class="strategy.status">{{ strategy.status.toUpperCase() }}</span>
          </div>
          <span class="card-type">{{ strategy.type.toUpperCase().replace('_', '_') }}</span>
        </div>
        <p class="card-description">{{ strategy.description }}</p>
        
        <div class="card-metrics">
          <div class="metric">
            <span class="metric-label">WIN_RATE</span>
            <span class="metric-value" :class="strategy.winRate >= 50 ? 'positive' : 'negative'">{{ strategy.winRate }}%</span>
          </div>
          <div class="metric">
            <span class="metric-label">PROFIT_FACTOR</span>
            <span class="metric-value" :class="strategy.profitFactor >= 1.5 ? 'positive' : 'negative'">{{ strategy.profitFactor }}</span>
          </div>
          <div class="metric">
            <span class="metric-label">MAX_DRAWDOWN</span>
            <span class="metric-value" :class="strategy.maxDrawdown >= -10 ? 'positive' : 'negative'">{{ strategy.maxDrawdown }}%</span>
          </div>
          <div class="metric">
            <span class="metric-label">TOTAL_TRADES</span>
            <span class="metric-value">{{ strategy.totalTrades }}</span>
          </div>
        </div>

        <div class="card-performance">
          <div class="perf-chart">
            <div class="perf-bars">
              <div class="perf-bar" v-for="(bar, i) in strategy.performance" :key="i"
                   :style="{ height: Math.abs(bar) + '%' }"
                   :class="bar >= 0 ? 'positive' : 'negative'">
              </div>
            </div>
          </div>
        </div>

        <div class="card-footer">
          <span class="card-created">CREATED: {{ strategy.createdAt }}</span>
          <div class="card-actions">
            <button class="btn-icon" @click="toggleStrategy(strategy)">
              {{ strategy.status === 'active' ? '[ PAUSE ]' : '[ RUN ]' }}
            </button>
            <button class="btn-icon" @click="editStrategy(strategy)">
              [ EDIT ]
            </button>
            <button class="btn-icon" @click="backtestStrategy(strategy)">
              [ BACKTEST ]
            </button>
            <button class="btn-icon danger" @click="deleteStrategy(strategy.id)">
              [ DELETE ]
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="empty-state" v-if="filteredStrategies.length === 0">
      // NO_STRATEGIES_FOUND
    </div>

    <div class="modal-overlay" v-if="showCreateModal" @click.self="showCreateModal = false">
      <div class="modal">
        <div class="modal-header">
          <span class="modal-title">CREATE_STRATEGY.EXE</span>
          <button class="btn-close" @click="showCreateModal = false">[ X ]</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>STRATEGY_NAME</label>
            <input type="text" v-model="newStrategy.name" placeholder="e.g. BTC_TREND_FOLLOWER" />
          </div>
          <div class="form-group">
            <label>DESCRIPTION</label>
            <textarea v-model="newStrategy.description" rows="3" placeholder="Describe your strategy..."></textarea>
          </div>
          <div class="form-group">
            <label>STRATEGY_TYPE</label>
            <select v-model="newStrategy.type">
              <option value="trend">TREND_FOLLOWING</option>
              <option value="mean_reversion">MEAN_REVERSION</option>
              <option value="arbitrage">ARBITRAGE</option>
              <option value="momentum">MOMENTUM</option>
            </select>
          </div>
          <div class="form-group">
            <label>SYMBOL</label>
            <input type="text" v-model="newStrategy.symbol" placeholder="e.g. BTC/USDT" />
          </div>
          <div class="form-group">
            <label>TIMEFRAME</label>
            <select v-model="newStrategy.timeframe">
              <option value="1m">1_MINUTE</option>
              <option value="5m">5_MINUTES</option>
              <option value="15m">15_MINUTES</option>
              <option value="1h">1_HOUR</option>
              <option value="4h">4_HOURS</option>
              <option value="1d">1_DAY</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showCreateModal = false">[ CANCEL ]</button>
          <button class="btn-primary" @click="createStrategy">[ CREATE ]</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const activeType = ref('all')
const activeStatus = ref('all')
const showCreateModal = ref(false)

const strategies = ref([
  {
    id: 1,
    name: 'BTC_TREND_FOLLOWER',
    description: 'Follows 50-day and 200-day moving average crossovers for Bitcoin.',
    type: 'trend',
    status: 'active',
    winRate: 68.5,
    profitFactor: 2.34,
    maxDrawdown: -8.2,
    totalTrades: 156,
    createdAt: '2024-01-10',
    performance: [15, 22, -8, 18, 25, -5, 30, 12, -10, 28]
  },
  {
    id: 2,
    name: 'ETH_MEAN_REVERSION',
    description: 'Bollinger Bands based mean reversion strategy for Ethereum.',
    type: 'mean_reversion',
    status: 'active',
    winRate: 72.3,
    profitFactor: 1.89,
    maxDrawdown: -5.6,
    totalTrades: 234,
    createdAt: '2024-01-05',
    performance: [8, 12, 5, 15, -3, 10, 8, 18, -2, 12]
  },
  {
    id: 3,
    name: 'SOL_MOMENTUM',
    description: 'RSI and MACD based momentum strategy for Solana.',
    type: 'momentum',
    status: 'paused',
    winRate: 55.2,
    profitFactor: 1.45,
    maxDrawdown: -12.8,
    totalTrades: 89,
    createdAt: '2024-01-12',
    performance: [25, -15, 30, -20, 18, -10, 22, -8, 15, -12]
  },
  {
    id: 4,
    name: 'BTC_ETH_SPREAD',
    description: 'Statistical arbitrage between BTC and ETH prices.',
    type: 'arbitrage',
    status: 'draft',
    winRate: 85.0,
    profitFactor: 3.12,
    maxDrawdown: -2.1,
    totalTrades: 45,
    createdAt: '2024-01-15',
    performance: [5, 8, 3, 10, 4, 12, 6, 9, 5, 11]
  },
  {
    id: 5,
    name: 'ALTCOIN_ROTATION',
    description: 'Rotates into top performing altcoins based on weekly momentum.',
    type: 'momentum',
    status: 'active',
    winRate: 61.8,
    profitFactor: 2.01,
    maxDrawdown: -15.3,
    totalTrades: 67,
    createdAt: '2024-01-08',
    performance: [35, -20, 45, -15, 28, -25, 32, -18, 22, -10]
  },
  {
    id: 6,
    name: 'GRID_TRADING_BOT',
    description: 'Automated grid trading strategy for range-bound markets.',
    type: 'mean_reversion',
    status: 'active',
    winRate: 78.4,
    profitFactor: 1.67,
    maxDrawdown: -6.4,
    totalTrades: 312,
    createdAt: '2024-01-03',
    performance: [12, 8, 15, 6, 18, 9, 11, 7, 14, 10]
  }
])

const newStrategy = ref({
  name: '',
  description: '',
  type: 'trend',
  symbol: '',
  timeframe: '1h'
})

const filteredStrategies = computed(() => {
  return strategies.value.filter(item => {
    const typeMatch = activeType.value === 'all' || item.type === activeType.value
    const statusMatch = activeStatus.value === 'all' || item.status === activeStatus.value
    return typeMatch && statusMatch
  })
})

function toggleStrategy(strategy: any) {
  strategy.status = strategy.status === 'active' ? 'paused' : 'active'
}

function editStrategy(strategy: any) {
  console.log('Editing strategy:', strategy.name)
}

function backtestStrategy(strategy: any) {
  console.log('Backtesting strategy:', strategy.name)
  alert('// BACKTEST_STARTED for ' + strategy.name)
}

function deleteStrategy(id: number) {
  if (confirm('// CONFIRM_DELETE_STRATEGY?')) {
    strategies.value = strategies.value.filter(s => s.id !== id)
  }
}

function createStrategy() {
  const strategy = {
    id: Date.now(),
    ...newStrategy.value,
    status: 'draft',
    winRate: 0,
    profitFactor: 0,
    maxDrawdown: 0,
    totalTrades: 0,
    createdAt: new Date().toISOString().slice(0, 10),
    performance: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  }
  strategies.value.unshift(strategy)
  showCreateModal.value = false
  newStrategy.value = { name: '', description: '', type: 'trend', symbol: '', timeframe: '1h' }
}
</script>

<style scoped>
.strategies {
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

.strategies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 16px;
}

.strategy-card {
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
  transition: all 0.1s ease;
}

.strategy-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: 4px 4px 0 var(--text-primary);
}

.card-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.card-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.card-name {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 16px;
}

.card-status {
  font-size: 10px;
  padding: 2px 8px;
  border: 1px solid currentColor;
  font-family: var(--font-mono);
}

.card-status.active {
  color: var(--success-color);
}

.card-status.paused {
  color: var(--warning-color);
}

.card-status.draft {
  color: var(--text-secondary);
}

.card-type {
  font-size: 10px;
  padding: 2px 6px;
  background: var(--bg-secondary);
  font-family: var(--font-mono);
}

.card-description {
  padding: 12px 16px;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.card-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.metric {
  text-align: center;
}

.metric-label {
  display: block;
  font-size: 9px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  margin-bottom: 4px;
}

.metric-value {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 14px;
}

.metric-value.positive {
  color: var(--success-color);
}

.metric-value.negative {
  color: var(--danger-color);
}

.card-performance {
  padding: 16px;
  height: 80px;
}

.perf-chart {
  height: 100%;
}

.perf-bars {
  display: flex;
  align-items: flex-end;
  height: 100%;
  gap: 4px;
}

.perf-bar {
  flex: 1;
  min-height: 4px;
  transition: height 0.3s ease;
}

.perf-bar.positive {
  background: var(--success-color);
}

.perf-bar.negative {
  background: var(--danger-color);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
}

.card-created {
  font-size: 10px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
}

.card-actions {
  display: flex;
  gap: 6px;
}

.btn-icon {
  padding: 4px 10px;
  border: 1px solid var(--text-primary);
  background: transparent;
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 9px;
  cursor: pointer;
}

.btn-icon:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}

.btn-icon.danger {
  border-color: var(--danger-color);
  color: var(--danger-color);
}

.btn-icon.danger:hover {
  background: var(--danger-color);
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

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
  width: 100%;
  max-width: 600px;
  box-shadow: 8px 8px 0 var(--text-primary);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 2px solid var(--text-primary);
  background: var(--text-primary);
  color: var(--bg-primary);
}

.modal-title {
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 1px;
}

.btn-close {
  background: transparent;
  border: none;
  color: var(--bg-primary);
  font-family: var(--font-mono);
  font-size: 12px;
  cursor: pointer;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 11px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 13px;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--success-color);
  box-shadow: 4px 4px 0 var(--success-color);
}

.modal-footer {
  padding: 16px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border: 2px solid var(--text-primary);
  font-family: var(--font-mono);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.1s ease;
}

.btn-primary {
  background: var(--success-color);
  border-color: var(--success-color);
  color: var(--bg-primary);
}

.btn-primary:hover {
  transform: translate(2px, 2px);
  box-shadow: none;
}

.btn-secondary {
  background: transparent;
  color: var(--text-primary);
}

.btn-secondary:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}

@media (max-width: 768px) {
  .strategies-grid {
    grid-template-columns: 1fr;
  }
  
  .card-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .filters {
    flex-direction: column;
    gap: 16px;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style>
