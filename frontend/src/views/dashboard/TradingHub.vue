<template>
  <div class="trading-hub">
    <!-- Order Panel -->
    <div class="panel order-panel">
      <div class="panel-header">
        <span class="panel-title">&gt; 下单面板</span>
        <div class="panel-controls">
          <button class="mode-btn" :class="{ active: orderForm.side === 'buy' }" @click="orderForm.side = 'buy'">买入</button>
          <button class="mode-btn sell" :class="{ active: orderForm.side === 'sell' }" @click="orderForm.side = 'sell'">卖出</button>
        </div>
      </div>
      <div class="panel-body">
        <div class="form-row">
          <div class="form-group">
            <label>标的</label>
            <select v-model="orderForm.symbol">
              <option v-for="s in symbols" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>类型</label>
            <select v-model="orderForm.type">
              <option value="market">市价</option>
              <option value="limit">限价</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>数量</label>
            <input type="number" v-model.number="orderForm.amount" step="0.01" placeholder="0.00" />
          </div>
          <div class="form-group" v-if="orderForm.type === 'limit'">
            <label>价格</label>
            <input type="number" v-model.number="orderForm.price" step="0.01" placeholder="0.00" />
          </div>
          <div class="form-group">
            <label>杠杆</label>
            <select v-model="orderForm.leverage">
              <option v-for="n in [1,2,3,5,10,20]" :key="n" :value="n">{{ n }}x</option>
            </select>
          </div>
        </div>
        <div class="order-estimate" v-if="orderForm.amount > 0">
          <span>预估占用: ${{ estimatedTotal }}</span>
          <span>可用: ${{ userAssets.available.toLocaleString() }}</span>
        </div>
        <button
          class="submit-btn"
          :class="orderForm.side"
          :disabled="orderForm.amount <= 0"
          @click="submitOrder"
        >
          {{ orderForm.side === 'buy' ? '买入' : '卖出' }} {{ orderForm.symbol }}
        </button>
      </div>
    </div>

    <!-- Positions -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">&gt; 持仓 ({{ positions.length }})</span>
      </div>
      <div class="panel-body">
        <table class="data-table" v-if="positions.length">
          <thead>
            <tr>
              <th>标的</th>
              <th>方向</th>
              <th>数量</th>
              <th>开仓价</th>
              <th>标记价</th>
              <th>盈亏</th>
              <th>收益率</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in positions" :key="p.symbol">
              <td class="symbol">{{ p.symbol }}</td>
              <td><span class="side" :class="p.side">{{ p.side === 'long' ? '多' : '空' }}</span></td>
              <td>{{ p.size }}</td>
              <td>${{ toLocale(p.entryPrice) }}</td>
              <td>${{ toLocale(p.markPrice) }}</td>
              <td :class="p.pnl >= 0 ? 'positive' : 'negative'">{{ p.pnl >= 0 ? '+' : '' }}${{ toLocale(p.pnl) }}</td>
              <td :class="p.pnlPercent >= 0 ? 'positive' : 'negative'">{{ p.pnlPercent >= 0 ? '+' : '' }}{{ p.pnlPercent.toFixed(2) }}%</td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty">暂无持仓</div>
      </div>
    </div>

    <!-- Open Orders & Signal Recommendations -->
    <div class="split-row">
      <!-- Open Orders -->
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">&gt; 挂单 ({{ openOrders.length }})</span>
        </div>
        <div class="panel-body">
          <table class="data-table compact" v-if="openOrders.length">
            <thead>
              <tr>
                <th>标的</th>
                <th>方向</th>
                <th>类型</th>
                <th>数量</th>
                <th>价格</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="o in openOrders" :key="o.id">
                <td class="symbol">{{ o.symbol }}</td>
                <td><span class="side" :class="o.side">{{ o.side === 'buy' ? '买' : '卖' }}</span></td>
                <td>{{ o.type === 'limit' ? '限价' : '市价' }}</td>
                <td>{{ o.amount }}</td>
                <td>${{ toLocale(o.price) }}</td>
                <td><span class="status" :class="o.status">{{ o.status === 'open' ? '待成交' : '已成交' }}</span></td>
              </tr>
            </tbody>
          </table>
          <div v-else class="empty">暂无挂单</div>
        </div>
      </div>

      <!-- Signal Recommendations -->
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">&gt; 信号推荐</span>
        </div>
        <div class="panel-body">
          <div v-for="s in signals.slice(0, 3)" :key="s.id" class="signal-card">
            <div class="signal-top">
              <span class="signal-strategy">{{ s.strategy }}</span>
              <span class="signal-confidence" :class="confidenceClass(s.confidence)">{{ s.confidence }}%</span>
            </div>
            <div class="signal-asset">
              <span class="symbol">{{ s.asset }}</span>
              <span class="direction" :class="s.direction">{{ s.direction === 'long' ? '▲ 做多' : '▼ 做空' }}</span>
            </div>
            <div class="signal-prices">
              <span>入场 {{ toLocale(s.price) }}</span>
              <span>目标 {{ toLocale(s.target) }}</span>
              <span class="negative">止损 {{ toLocale(s.stopLoss) }}</span>
            </div>
          </div>
          <div v-if="!signals.length" class="empty">暂无信号</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { positions, signals, userAssets } from '@/data/mockData'

const symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT']

const openOrders = ref([
  { id: 1, symbol: 'ETH/USDT', side: 'buy', type: 'limit', amount: 10, price: 3150, status: 'open' },
  { id: 2, symbol: 'SOL/USDT', side: 'sell', type: 'limit', amount: 5, price: 155, status: 'open' },
  { id: 3, symbol: 'BNB/USDT', side: 'buy', type: 'market', amount: 2, price: 582, status: 'filled' },
])

let nextOrderId = 4

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

  openOrders.value.unshift({
    id: nextOrderId++,
    symbol: orderForm.value.symbol,
    side: orderForm.value.side,
    type: orderForm.value.type,
    amount: orderForm.value.amount,
    price: price || 66000,
    status,
  })

  orderForm.value.amount = 0
  orderForm.value.price = 0
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

.data-table.compact td,
.data-table.compact th {
  padding: 6px 8px;
}

.symbol {
  font-weight: 700;
}

.side {
  padding: 2px 6px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid currentColor;
}
.side.long {
  color: var(--success-color);
}
.side.short {
  color: var(--danger-color);
}

.status {
  padding: 2px 6px;
  font-size: 11px;
  border: 1px solid currentColor;
}
.status.open {
  color: var(--text-primary);
}
.status.filled {
  color: var(--success-color);
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

/* Split row */
.split-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 1100px) {
  .split-row {
    grid-template-columns: 1fr;
  }
}

/* Signal Cards */
.signal-card {
  padding: 12px;
  border: 1px solid var(--border-color);
  margin-bottom: 8px;
  background: var(--bg-secondary);
}
.signal-card:last-child {
  margin-bottom: 0;
}

.signal-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
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
  margin-bottom: 6px;
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
  gap: 12px;
  font-size: 11px;
  color: var(--text-secondary);
}
.signal-prices span {
  font-family: var(--font-mono, monospace);
}
</style>
