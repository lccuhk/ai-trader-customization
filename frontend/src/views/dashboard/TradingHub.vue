<template>
  <div class="trading-hub">
    <!-- Order Panel -->
    <div class="panel order-panel">
      <div class="panel-header">
        <span class="panel-title">&gt; {{ $t('trading.orderPanel') }}</span>
        <div class="panel-controls">
          <button class="mode-btn" :class="{ active: orderForm.side === 'buy' }" @click="orderForm.side = 'buy'">{{ $t('trading.buy') }}</button>
          <button class="mode-btn sell" :class="{ active: orderForm.side === 'sell' }" @click="orderForm.side = 'sell'">{{ $t('trading.sell') }}</button>
        </div>
      </div>
      <div class="panel-body">
        <div class="form-row">
          <div class="form-group">
            <label>{{ $t('trading.symbol') }}</label>
            <select v-model="orderForm.symbol">
              <option v-for="s in symbols" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>{{ $t('trading.type') }}</label>
            <select v-model="orderForm.type">
              <option value="market">{{ $t('trading.market') }}</option>
              <option value="limit">{{ $t('trading.limit') }}</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>{{ $t('trading.quantity') }}</label>
            <input type="number" v-model.number="orderForm.amount" step="0.01" placeholder="0.00" />
          </div>
          <div class="form-group" v-if="orderForm.type === 'limit'">
            <label>{{ $t('trading.price') }}</label>
            <input type="number" v-model.number="orderForm.price" step="0.01" placeholder="0.00" />
          </div>
          <div class="form-group">
            <label>{{ $t('trading.leverage') }}</label>
            <select v-model="orderForm.leverage">
              <option v-for="n in [1,2,3,5,10,20]" :key="n" :value="n">{{ n }}x</option>
            </select>
            <div class="leverage-warning" v-if="leverageExceedsLimit">
              {{ $t('trading.leverageWarning', { leverage: orderForm.leverage, max: riskSettings.maxLeverage }) }}
            </div>
          </div>
        </div>
        <div class="order-estimate" v-if="orderForm.amount > 0">
          <span>{{ $t('trading.estimateCost') }}: ${{ estimatedTotal }}</span>
          <span>{{ $t('trading.available') }}: ${{ availableBalance.toLocaleString() }}</span>
        </div>
        <button
          class="submit-btn"
          :class="orderForm.side"
          :disabled="orderForm.amount <= 0"
          @click="submitOrder"
        >
          {{ orderForm.side === 'buy' ? $t('trading.buy') : $t('trading.sell') }} {{ orderForm.symbol }}
        </button>
      </div>
    </div>

    <!-- Positions -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">&gt; {{ $t('trading.positions') }} ({{ activePositions.length }})</span>
      </div>
      <div class="panel-body">
        <table class="data-table" v-if="activePositions.length">
          <thead>
            <tr>
              <th>{{ $t('trading.symbol') }}</th>
              <th>{{ $t('trading.side') }}</th>
              <th>{{ $t('trading.quantity') }}</th>
              <th>{{ $t('trading.entryPrice') }}</th>
              <th>{{ $t('trading.markPrice') }}</th>
              <th>{{ $t('trading.pnl') }}</th>
              <th>{{ $t('trading.roi') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in activePositions" :key="p.symbol">
              <td class="symbol">{{ p.symbol }}</td>
              <td><span class="side" :class="p.side">{{ p.side === 'long' ? $t('signal.long') : $t('signal.short') }}</span></td>
              <td>{{ p.size }}</td>
              <td>${{ toLocale(p.entryPrice) }}</td>
              <td>${{ toLocale(p.markPrice) }}</td>
              <td :class="p.pnl >= 0 ? 'positive' : 'negative'">{{ p.pnl >= 0 ? '+' : '' }}${{ toLocale(p.pnl) }}</td>
              <td :class="p.pnlPercent >= 0 ? 'positive' : 'negative'">{{ p.pnlPercent >= 0 ? '+' : '' }}{{ p.pnlPercent.toFixed(2) }}%</td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty">{{ $t('trading.noPositions') }}</div>
      </div>
    </div>

    <!-- Open Orders -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">&gt; {{ $t('trading.orders') }}</span>
        <div class="panel-controls">
          <button
            class="filter-btn"
            :class="{ active: orderFilter === 'all' }"
            @click="setFilter('all')"
          >{{ $t('trading.filterAll') }} ({{ activeOrders.length }})</button>
          <button
            class="filter-btn"
            :class="{ active: orderFilter === 'open' }"
            @click="setFilter('open')"
          >{{ $t('trading.filterOpen') }} ({{ openCount }})</button>
          <button
            class="filter-btn"
            :class="{ active: orderFilter === 'filled' }"
            @click="setFilter('filled')"
          >{{ $t('trading.filterFilled') }} ({{ filledCount }})</button>
          <button
            class="filter-btn"
            :class="{ active: orderFilter === 'cancelled' }"
            @click="setFilter('cancelled')"
          >{{ $t('trading.cancelled') }} ({{ cancelledCount }})</button>
        </div>
      </div>
      <div class="panel-body">
        <table class="data-table" v-if="filteredOrders.length">
          <thead>
            <tr>
              <th class="col-time">{{ $t('common.time') }}</th>
              <th class="col-symbol">{{ $t('trading.symbol') }}</th>
              <th class="col-side">{{ $t('trading.side') }}</th>
              <th class="col-type">{{ $t('trading.type') }}</th>
              <th class="col-qty">{{ $t('trading.quantity') }}</th>
              <th class="col-price">{{ $t('trading.price') }}</th>
              <th class="col-status">{{ $t('common.status') }}</th>
              <th class="col-action"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="o in filteredOrders" :key="o.id" class="order-row" :class="{ cancelled: o.status === 'cancelled' }">
              <td class="col-time">{{ formatTime(o.created_at) }}</td>
              <td class="col-symbol">{{ o.symbol }}</td>
              <td class="col-side"><span class="side" :class="o.side">{{ o.side === 'buy' ? $t('trading.buy') : $t('trading.sell') }}</span></td>
              <td class="col-type">{{ o.type === 'limit' ? $t('trading.limit') : $t('trading.market') }}</td>
              <td class="col-qty">{{ o.quantity }}</td>
              <td class="col-price">${{ toLocale(o.price) }}</td>
              <td class="col-status"><span class="status-tag" :class="o.status">{{ statusLabel(o.status) }}</span></td>
              <td class="col-action">
                <button
                  v-if="o.status === 'open'"
                  class="cancel-btn"
                  @click="cancelOrder(o.id)"
                >✕ {{ $t('trading.cancelOrder') }}</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty">{{ $t('trading.noOrders') }}</div>
      </div>
    </div>

    <!-- Signal Recommendations -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">&gt; {{ $t('trading.signalRecommendations') }}</span>
      </div>
      <div class="panel-body signals-row">
        <div v-for="s in signals.slice(0, 3)" :key="s.id" class="signal-card">
          <div class="signal-top">
            <span class="signal-strategy">{{ strategyLabel(s.strategy) }}</span>
            <span class="signal-confidence" :class="confidenceClass(s.confidence)">{{ s.confidence }}%</span>
          </div>
          <div class="signal-asset">
            <span class="symbol">{{ s.asset }}</span>
            <span class="direction" :class="s.direction">{{ s.direction === 'long' ? '▲ ' + $t('signal.long') : '▼ ' + $t('signal.short') }}</span>
          </div>
          <div class="signal-prices">
            <span>{{ $t('signal.entryPrice') }} {{ toLocale(s.price) }}</span>
            <span>{{ $t('signal.targetPrice') }} {{ toLocale(s.target) }}</span>
            <span class="negative">{{ $t('signal.stopLoss') }} {{ toLocale(s.stopLoss) }}</span>
          </div>
        </div>
        <div v-if="!signals.length" class="empty">{{ $t('trading.noSignals') }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { positions, signals, userAssets, riskSettings, livePositions, liveUserAssets, openOrders as simOrdersData, liveOpenOrders } from '@/data/mockData'
import { useTradingStore } from '@/stores/trading'

const props = defineProps<{ tradingMode: 'sim' | 'live' }>()

const { t } = useI18n()
const tradingStore = useTradingStore()

// Seed store with mock orders on first load
if (tradingStore.orders.length === 0) {
  simOrdersData.forEach(o => tradingStore.addOrder(o as any))
  liveOpenOrders.forEach(o => tradingStore.addOrder(o as any))
}

const activeOrders = computed(() =>
  tradingStore.orders.filter(o => o.is_simulation === (props.tradingMode === 'sim'))
)

const strategyLabelKeys: Record<string, string> = {
  '动量突破': 'strategy.breakout',
  '均值回归': 'strategy.meanReversion',
  '趋势跟踪': 'strategy.trend',
  '网格交易': 'strategy.grid',
}
function strategyLabel(strategy: string): string {
  return t(strategyLabelKeys[strategy] || strategy)
}

const activePositions = computed(() => props.tradingMode === 'sim' ? positions : livePositions)
const availableBalance = computed(() => props.tradingMode === 'sim' ? userAssets.available : liveUserAssets.available)

const symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT']

// Order ID counter (used for local additions)
let nextOrderId = Date.now()

// Order status filter
const orderFilter = ref<'all' | 'open' | 'filled' | 'cancelled'>('all')

const openCount = computed(() =>
  activeOrders.value.filter(o => o.status === 'open').length
)
const filledCount = computed(() =>
  activeOrders.value.filter(o => o.status === 'filled').length
)
const cancelledCount = computed(() =>
  activeOrders.value.filter(o => o.status === 'cancelled').length
)

const filteredOrders = computed(() => {
  if (orderFilter.value === 'all') return activeOrders.value
  return activeOrders.value.filter(o => o.status === orderFilter.value)
})

function formatTime(iso: string): string {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const orderForm = ref({
  symbol: 'BTC/USDT',
  side: 'buy' as 'buy' | 'sell',
  type: 'market' as 'market' | 'limit',
  amount: 0,
  price: 0,
  leverage: 1,
})

const estimatedTotal = computed(() => {
  const price = orderForm.value.type === 'market' ? 66000 : orderForm.value.price
  return (price * orderForm.value.amount * orderForm.value.leverage).toFixed(2)
})

const leverageExceedsLimit = computed(() => {
  return orderForm.value.leverage > riskSettings.maxLeverage
})

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    open: t('trading.filterOpen'),
    filled: t('trading.filterFilled'),
    cancelled: t('trading.cancelled'),
  }
  return labels[status] || status
}

function toLocale(n: number): string {
  return n.toLocaleString()
}

function confidenceClass(score: number): string {
  if (score >= 80) return 'high'
  if (score >= 65) return 'medium'
  return 'low'
}

function submitOrder() {
  const price = orderForm.value.type === 'market'
    ? 66000  // mock current price
    : orderForm.value.price

  const status = orderForm.value.type === 'market' ? 'filled' : 'open'

  tradingStore.addOrder({
    id: nextOrderId++,
    symbol: orderForm.value.symbol,
    side: orderForm.value.side,
    type: orderForm.value.type,
    quantity: orderForm.value.amount,
    price: price || 66000,
    status,
    is_simulation: props.tradingMode === 'sim',
    created_at: new Date().toISOString(),
    user_id: 1,
  } as any)

  orderForm.value.amount = 0
  orderForm.value.price = 0
}

async function cancelOrder(orderId: number) {
  try {
    // Try API first
    await tradingStore.cancelOrder(orderId).catch(() => {})
    // If API didn't update the store (e.g. backend unavailable), update locally
    const order = tradingStore.orders.find(o => o.id === orderId)
    if (order && order.status !== 'cancelled') {
      order.status = 'cancelled'
    }
  } catch (e: any) {
    // Last-resort fallback
    const order = tradingStore.orders.find(o => o.id === orderId)
    if (order) order.status = 'cancelled'
  }
}

function setFilter(filter: 'all' | 'open' | 'filled' | 'cancelled') {
  orderFilter.value = filter
}
</script>

<style scoped>
.trading-hub {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
  font-family: var(--font-mono, monospace);
}

.panel-controls {
  display: flex;
  gap: 4px;
}

.mode-btn {
  padding: 4px 12px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
}
.mode-btn.active {
  background: var(--success-color);
  border-color: var(--success-color);
  color: white;
}
.mode-btn.sell.active {
  background: var(--danger-color);
  border-color: var(--danger-color);
}

.panel-body {
  padding: 16px;
}

/* Order Form */
.order-panel .panel-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.form-group select,
.form-group input {
  padding: 8px 10px;
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
}
.form-group select:focus,
.form-group input:focus {
  border-color: var(--success-color);
}

.leverage-warning {
  margin-top: 4px;
  padding: 6px 8px;
  background: var(--danger-bg, rgba(255, 51, 51, 0.1));
  border: 1px solid var(--danger-color);
  color: var(--danger-color);
  font-size: 11px;
  font-weight: 600;
  line-height: 1.4;
}

.order-estimate {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--bg-secondary);
  font-size: 12px;
  color: var(--text-secondary);
}

.submit-btn {
  width: 100%;
  padding: 12px;
  border: 2px solid var(--border-color);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: all 0.1s ease;
}
.submit-btn.buy {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}
.submit-btn.sell {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}
.submit-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Table */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  table-layout: fixed;
}

.data-table th {
  text-align: left;
  padding: 8px 6px;
  border-bottom: 2px solid var(--border-color);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-secondary);
  font-weight: 600;
  white-space: nowrap;
}

.data-table td {
  padding: 8px 6px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
  font-size: 12px;
  vertical-align: middle;
}

/* Column widths */
.col-time { width: 60px; }
.col-symbol { width: 100px; }
.col-side { width: 50px; }
.col-type { width: 50px; }
.col-qty { width: 70px; }
.col-price { width: 100px; }
.col-status { width: 70px; }
.col-action { width: 100px; }

.time-cell {
  font-family: var(--font-mono, monospace);
  font-size: 11px;
  color: var(--text-secondary);
}

.symbol-cell {
  font-weight: 700;
}

.order-row.cancelled td {
  opacity: 0.45;
}
.order-row.cancelled .col-symbol {
  text-decoration: line-through;
}

.side {
  display: inline-block;
  padding: 2px 6px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid currentColor;
  line-height: 1.2;
}
.side.long {
  color: var(--success-color);
}
.side.short {
  color: var(--danger-color);
}
.side.buy {
  color: var(--success-color);
}
.side.sell {
  color: var(--danger-color);
}

.status-tag {
  display: inline-block;
  padding: 2px 6px;
  font-size: 11px;
  border: 1px solid currentColor;
  line-height: 1.2;
}
.status-tag.open {
  color: var(--text-primary);
}
.status-tag.filled {
  color: var(--success-color);
}
.status-tag.cancelled {
  color: var(--text-secondary);
}

.cancel-btn {
  padding: 3px 8px;
  border: 1px solid var(--danger-color);
  background: transparent;
  color: var(--danger-color);
  font-size: 10px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  transition: all 0.1s ease;
}
.cancel-btn:hover {
  background: var(--danger-color);
  color: white;
}

.positive {
  color: var(--success-color);
  font-weight: 600;
}
.negative {
  color: var(--danger-color);
  font-weight: 600;
}

.empty {
  text-align: center;
  padding: 32px;
  color: var(--text-secondary);
  font-size: 13px;
}

/* Signal Cards - horizontal row */
.signals-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.signal-card {
  padding: 14px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.signal-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.signal-strategy {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.signal-confidence {
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 700;
  border: 1px solid currentColor;
}
.signal-confidence.high {
  color: var(--success-color);
}
.signal-confidence.medium {
  color: var(--text-primary);
}
.signal-confidence.low {
  color: var(--text-secondary);
}

.signal-asset {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.direction {
  font-size: 11px;
  font-weight: 600;
}
.direction.long {
  color: var(--success-color);
}
.direction.short {
  color: var(--danger-color);
}

.signal-prices {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 11px;
  color: var(--text-secondary);
  font-family: var(--font-mono, monospace);
}

@media (max-width: 900px) {
  .signals-row {
    grid-template-columns: 1fr;
  }
}

.filter-btn {
  padding: 3px 10px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  transition: all 0.1s ease;
}
.filter-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}
.filter-btn.active {
  background: var(--text-primary);
  color: var(--bg-primary);
  border-color: var(--text-primary);
}
</style>
