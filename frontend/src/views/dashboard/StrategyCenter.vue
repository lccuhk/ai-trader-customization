<template>
  <div class="strategy-center">
    <div class="page-title">&gt; {{ $t('nav.strategyCenter') }}</div>

    <!-- My Strategies -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">{{ $t('strategy.myStrategies') }}</span>
        <button class="create-btn" @click="showCreateModal = true">+ {{ $t('strategy.newStrategy') }}</button>
      </div>
      <div class="panel-body">
        <table class="data-table" v-if="strategies.length">
          <thead>
            <tr>
              <th>{{ $t('strategy.strategyName') }}</th>
              <th>{{ $t('strategy.type') }}</th>
              <th>{{ $t('strategy.status') }}</th>
              <th>{{ $t('strategy.returnRate') }}</th>
              <th>{{ $t('strategy.sharpeRatio') }}</th>
              <th>{{ $t('strategy.operations') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in strategies" :key="s.id">
              <td class="strategy-name">{{ s.name }}</td>
              <td class="strategy-type">{{ s.type || '—' }}</td>
              <td>
                <span class="status" :class="s.status">
                  {{ s.status === 'active' ? $t('strategy.active') : $t('strategy.paused') }}
                </span>
              </td>
              <td :class="s.lastReturn >= 0 ? 'positive' : 'negative'">
                {{ s.lastReturn >= 0 ? '+' : '' }}{{ s.lastReturn }}%
              </td>
              <td>{{ s.sharpe.toFixed(2) }}</td>
              <td>
                <div class="action-group">
                  <button class="action-btn" @click="toggleStrategy(s.id)">
                    {{ s.status === 'active' ? $t('strategy.pause') : $t('strategy.run') }}
                  </button>
                  <button class="action-btn delete" @click="deleteStrategy(s.id)">
                    {{ $t('common.delete') }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty">{{ $t('strategy.noStrategies') }}</div>
      </div>
    </div>

    <!-- Simulated Trading Dashboard -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">&gt; {{ $t('strategy.simulatedDashboard') }}</span>
        <span class="sim-badge">{{ $t('strategy.simLabel') }}</span>
      </div>
      <div class="panel-body">
        <!-- Summary Metrics -->
        <div class="sim-metrics">
          <div class="metric-card">
            <div class="metric-label">{{ $t('strategy.totalReturn') }}</div>
            <div class="metric-value positive">{{ sim.totalReturn }}%</div>
            <div class="metric-sub">{{ $t('strategy.startBalance') }} ${{ toLocale(sim.startBalance) }}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">{{ $t('strategy.currentEquity') }}</div>
            <div class="metric-value">${{ toLocale(sim.currentBalance) }}</div>
            <div class="metric-sub" :class="sim.totalReturn >= 0 ? 'positive' : 'negative'">
              +${{ toLocale(sim.currentBalance - sim.startBalance) }}
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-label">{{ $t('strategy.winRate') }}</div>
            <div class="metric-value">{{ sim.winRate }}%</div>
            <div class="metric-sub">{{ $t('strategy.totalTrades') }} {{ sim.totalTrades }}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">{{ $t('strategy.sharpeRatio') }}</div>
            <div class="metric-value">{{ sim.sharpe.toFixed(2) }}</div>
            <div class="metric-sub">{{ $t('strategy.maxDrawdown') }} {{ sim.maxDrawdown }}%</div>
          </div>
        </div>

        <!-- Equity Curve (inline SVG) -->
        <div class="equity-section">
          <div class="section-label">{{ $t('strategy.equityCurve') }}</div>
          <svg class="equity-chart" :viewBox="`0 0 ${eqPoints.length - 1} 100`" preserveAspectRatio="none">
            <polyline
              :points="eqPoints"
              fill="none"
              stroke="var(--success-color)"
              stroke-width="2"
            />
          </svg>
          <div class="equity-labels">
            <span>{{ equityDates[0] }}</span>
            <span>${{ toLocale(sim.startBalance) }}</span>
            <span>{{ equityDates[equityDates.length - 1] }}</span>
            <span>${{ toLocale(sim.currentBalance) }}</span>
          </div>
        </div>

        <!-- Recent Simulated Trades -->
        <div class="section-label">{{ $t('strategy.recentSimTrades') }}</div>
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ $t('trading.symbol') }}</th>
              <th>{{ $t('trading.side') }}</th>
              <th>{{ $t('strategy.entry') }}</th>
              <th>{{ $t('strategy.exit') }}</th>
              <th>{{ $t('trading.pnl') }}</th>
              <th>{{ $t('strategy.returnRate') }}</th>
              <th>{{ $t('common.time') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in simTrades" :key="t.id">
              <td class="symbol">{{ t.symbol }}</td>
              <td><span class="side" :class="t.side">{{ t.side === 'long' ? $t('signal.long') : $t('signal.short') }}</span></td>
              <td class="mono">${{ toLocale(t.entryPrice) }}</td>
              <td class="mono">${{ toLocale(t.exitPrice) }}</td>
              <td :class="t.pnl >= 0 ? 'positive' : 'negative'">{{ t.pnl >= 0 ? '+' : '' }}${{ toLocale(t.pnl) }}</td>
              <td :class="t.pnlPercent >= 0 ? 'positive' : 'negative'">{{ t.pnlPercent >= 0 ? '+' : '' }}{{ t.pnlPercent.toFixed(2) }}%</td>
              <td class="mono time">{{ t.exitTime }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Strategy Templates -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">{{ $t('strategy.templates') }}</span>
      </div>
      <div class="panel-body">
        <div class="templates-grid">
          <div v-for="t in strategyTemplates" :key="t.id" class="template-card">
            <div class="template-name">{{ t.name }}</div>
            <div class="template-tags">
              <span class="tag">{{ t.difficulty }}</span>
              <span class="tag">{{ t.marketType }}</span>
            </div>
            <button class="use-btn" @click="useTemplate(t)">{{ $t('strategy.useTemplate') }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Strategy Modal -->
    <Teleport to="body">
      <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
        <div class="modal-panel">
          <div class="modal-header">
            <span class="modal-title">&gt; {{ $t('strategy.newStrategy') }}</span>
            <button class="modal-close" @click="showCreateModal = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>{{ $t('strategy.strategyName') }}</label>
              <input
                v-model="newStrategy.name"
                type="text"
                :placeholder="$t('strategy.strategyNamePlaceholder')"
                class="form-input"
              />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>{{ $t('strategy.strategyType') }}</label>
                <select v-model="newStrategy.type" class="form-input">
                  <option value="趋势跟踪">{{ $t('strategy.trend') }}</option>
                  <option value="网格交易">{{ $t('strategy.grid') }}</option>
                  <option value="动量突破">{{ $t('strategy.breakout') }}</option>
                  <option value="均值回归">{{ $t('strategy.meanReversion') }}</option>
                  <option value="统计套利">{{ $t('strategy.arbitrage') }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>{{ $t('strategy.riskLevel') }}</label>
                <select v-model="newStrategy.riskLevel" class="form-input">
                  <option value="低">{{ $t('common.low') }} ({{ $t('strategy.conservative') }})</option>
                  <option value="中">{{ $t('common.medium') }} ({{ $t('strategy.moderate') }})</option>
                  <option value="高">{{ $t('common.high') }} ({{ $t('strategy.aggressive') }})</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label>{{ $t('strategy.initialCapital') }} ($)</label>
              <input
                v-model.number="newStrategy.capital"
                type="number"
                placeholder="1000"
                class="form-input"
                min="100"
                step="100"
              />
            </div>
            <div class="form-group">
              <label>{{ $t('strategy.symbols') }}</label>
              <div class="asset-toggles">
                <button
                  v-for="sym in availableSymbols"
                  :key="sym"
                  class="asset-toggle"
                  :class="{ selected: newStrategy.symbols.includes(sym) }"
                  @click="toggleSymbol(sym)"
                >{{ sym }}</button>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="modal-btn cancel" @click="showCreateModal = false">{{ $t('common.cancel') }}</button>
            <button class="modal-btn confirm" :disabled="!newStrategy.name.trim()" @click="createStrategy">{{ $t('strategy.createStrategy') }}</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { myStrategies, strategyTemplates, simulatedOverview, simulatedEquityCurve, simulatedTrades } from '@/data/mockData'

const showCreateModal = ref(false)
const availableSymbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT']

const strategies = ref([...myStrategies])

const newStrategy = reactive({
  name: '',
  type: '趋势跟踪',
  riskLevel: '中',
  capital: 1000,
  symbols: [] as string[],
})

let nextId = strategies.value.length + 1

function toggleSymbol(sym: string) {
  const idx = newStrategy.symbols.indexOf(sym)
  if (idx >= 0) {
    newStrategy.symbols.splice(idx, 1)
  } else {
    newStrategy.symbols.push(sym)
  }
}

function createStrategy() {
  if (!newStrategy.name.trim()) return
  const mockReturn = Math.round((Math.random() * 20 - 5) * 10) / 10
  const mockSharpe = Math.round((Math.random() * 2 + 0.5) * 100) / 100

  strategies.value.push({
    id: nextId++,
    name: newStrategy.name.trim(),
    type: newStrategy.type,
    status: 'active' as const,
    lastReturn: mockReturn,
    sharpe: mockSharpe,
  })

  newStrategy.name = ''
  newStrategy.type = '趋势跟踪'
  newStrategy.riskLevel = '中'
  newStrategy.capital = 1000
  newStrategy.symbols = []
  showCreateModal.value = false
}

function toggleStrategy(id: number) {
  const s = strategies.value.find(s => s.id === id)
  if (s) {
    s.status = s.status === 'active' ? 'paused' : 'active'
  }
}

function deleteStrategy(id: number) {
  const name = strategies.value.find(s => s.id === id)?.name
  if (confirm(`确定要删除策略 "${name}" 吗？`)) {
    strategies.value = strategies.value.filter(s => s.id !== id)
  }
}

function useTemplate(t: typeof strategyTemplates[0]) {
  newStrategy.name = t.name
  newStrategy.type = t.name.replace('模板', '').trim()
  showCreateModal.value = true
}

// Simulated dashboard data
const sim = simulatedOverview
const simTrades = simulatedTrades

const equityDates = computed(() => {
  return simulatedEquityCurve.map(d => d.date)
})

const eqPoints = computed(() => {
  const values = simulatedEquityCurve.map(d => d.value)
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1
  return values.map((v, i) => {
    const y = 100 - ((v - min) / range) * 80 - 10
    return `${i},${y}`
  }).join(' ')
})

function toLocale(n: number): string {
  return n.toLocaleString()
}
</script>

<style scoped>
.strategy-center {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.panel {
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 2px solid var(--border-color);
  background: var(--bg-secondary);
}

.panel-title {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.create-btn {
  padding: 4px 12px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}
.create-btn:hover {
  background: var(--success-color);
  border-color: var(--success-color);
  color: white;
}

.panel-body {
  padding: 16px;
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

.strategy-name {
  font-weight: 700;
}

.strategy-type {
  font-size: 11px;
  color: var(--text-secondary);
}

.status {
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid currentColor;
}
.status.active {
  color: var(--success-color);
}
.status.paused {
  color: var(--text-secondary);
}

.positive {
  color: var(--success-color);
  font-weight: 600;
}

.negative {
  color: var(--danger-color);
  font-weight: 600;
}

.action-group {
  display: flex;
  gap: 6px;
}

.action-btn {
  padding: 4px 10px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}
.action-btn:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}
.action-btn.delete {
  border-color: var(--danger-color);
  color: var(--danger-color);
}
.action-btn.delete:hover {
  background: var(--danger-color);
  color: white;
}

/* Sim Dashboard */
.sim-badge {
  padding: 2px 8px;
  border: 1px solid var(--info-color);
  color: var(--info-color);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.sim-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.metric-card {
  border: 2px solid var(--border-color);
  padding: 16px;
  text-align: center;
}

.metric-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  font-family: var(--font-mono, monospace);
  color: var(--text-primary);
}

.metric-sub {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
  font-family: var(--font-mono, monospace);
}

.metric-sub.positive {
  color: var(--success-color);
}
.metric-sub.negative {
  color: var(--danger-color);
}

/* Equity Curve */
.equity-section {
  margin-bottom: 20px;
}

.section-label {
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 8px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.equity-chart {
  width: 100%;
  height: 120px;
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
}

.equity-labels {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: var(--text-secondary);
  margin-top: 4px;
  font-family: var(--font-mono, monospace);
}

/* Templates */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.template-card {
  border: 2px solid var(--border-color);
  padding: 16px;
  text-align: center;
}

.template-name {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 8px;
}

.template-tags {
  display: flex;
  gap: 6px;
  justify-content: center;
  margin-bottom: 12px;
}

.tag {
  padding: 2px 8px;
  border: 1px solid var(--border-color);
  font-size: 10px;
  color: var(--text-secondary);
  letter-spacing: 0.03em;
}

.use-btn {
  padding: 6px 16px;
  border: 2px solid var(--success-color);
  background: transparent;
  color: var(--success-color);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}
.use-btn:hover {
  background: var(--success-color);
  color: white;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-panel {
  width: 520px;
  max-height: 80vh;
  overflow-y: auto;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  box-shadow: 8px 8px 0 rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 2px solid var(--border-color);
}

.modal-title {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  cursor: pointer;
  font-size: 14px;
}

.modal-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.form-input {
  padding: 8px 12px;
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
}
.form-input:focus {
  border-color: var(--success-color);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.asset-toggles {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.asset-toggle {
  padding: 6px 14px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.asset-toggle.selected {
  border-color: var(--success-color);
  color: var(--success-color);
  background: rgba(0, 255, 65, 0.08);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px 20px;
  border-top: 2px solid var(--border-color);
}

.modal-btn {
  padding: 8px 20px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.modal-btn.confirm {
  background: var(--success-color);
  border-color: var(--success-color);
  color: white;
}
.modal-btn.confirm:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.modal-btn.cancel:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}

.empty {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
  font-size: 13px;
}

.mono {
  font-family: var(--font-mono, monospace);
}

.time {
  font-size: 11px;
  color: var(--text-secondary);
}

.side {
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid currentColor;
}
.side.long {
  color: var(--success-color);
  border-color: var(--success-color);
}
.side.short {
  color: var(--danger-color);
  border-color: var(--danger-color);
}

.symbol {
  font-weight: 700;
}
</style>
