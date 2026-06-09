<template>
  <div class="trading-view">
    <div class="trading-header">
      <h1>{{ t('trading.title') }}</h1>
      <div class="mode-toggle">
        <button 
          :class="{ active: isSimulation }" 
          @click="isSimulation = true"
        >
          {{ t('trading.simulation') }}
        </button>
        <button 
          :class="{ active: !isSimulation }" 
          @click="isSimulation = false"
        >
          {{ t('trading.real') }}
        </button>
      </div>
    </div>

    <div class="trading-content">
      <div class="trading-panel">
        <div class="order-form">
          <h2>{{ t('trading.submitOrder') }}</h2>
          
          <div class="form-group">
            <label>{{ t('trading.symbol') }}</label>
            <select v-model="orderForm.symbol">
              <option v-for="symbol in symbols" :key="symbol" :value="symbol">
                {{ symbol }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>{{ t('trading.side') }}</label>
            <div class="side-buttons">
              <button 
                class="buy-btn" 
                :class="{ active: orderForm.side === 'buy' }"
                @click="orderForm.side = 'buy'"
              >
                {{ t('trading.buy') }}
              </button>
              <button 
                class="sell-btn" 
                :class="{ active: orderForm.side === 'sell' }"
                @click="orderForm.side = 'sell'"
              >
                {{ t('trading.sell') }}
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>{{ t('trading.type') }}</label>
            <select v-model="orderForm.type">
              <option value="market">{{ t('trading.marketOrder') }}</option>
              <option value="limit">{{ t('trading.limitOrder') }}</option>
              <option value="stop">{{ t('trading.stopOrder') }}</option>
            </select>
          </div>

          <div class="form-group" v-if="orderForm.type !== 'market'">
            <label>{{ t('trading.price') }}</label>
            <input 
              type="number" 
              v-model.number="orderForm.price" 
              step="0.01"
              :placeholder="t('trading.enterPrice')"
            />
          </div>

          <div class="form-group">
            <label>{{ t('trading.quantity') }}</label>
            <input 
              type="number" 
              v-model.number="orderForm.quantity" 
              step="0.0001"
              :placeholder="t('trading.enterQuantity')"
            />
          </div>

          <div class="price-info" v-if="currentPrice">
            <span>{{ t('trading.currentPrice') }}: ${{ currentPrice.toLocaleString() }}</span>
          </div>

          <div class="order-summary" v-if="orderForm.quantity > 0">
            <div class="summary-row">
              <span>{{ t('trading.estimatedCost') }}</span>
              <span>${{ estimatedTotal.toLocaleString() }}</span>
            </div>
          </div>

          <button 
            class="submit-btn" 
            :class="orderForm.side"
            :disabled="!canSubmit || loading"
            @click="submitOrder"
          >
            {{ loading ? t('common.loading') : (orderForm.side === 'buy' ? t('trading.buy') : t('trading.sell')) }} {{ orderForm.symbol }}
          </button>
        </div>
      </div>

      <div class="trading-data">
        <div class="tabs">
          <button 
            :class="{ active: activeTab === 'positions' }"
            @click="activeTab = 'positions'"
          >
            {{ t('trading.positions') }}
          </button>
          <button 
            :class="{ active: activeTab === 'orders' }"
            @click="activeTab = 'orders'"
          >
            {{ t('trading.orders') }}
          </button>
          <button 
            :class="{ active: activeTab === 'trades' }"
            @click="activeTab = 'trades'"
          >
            {{ t('trading.history') }}
          </button>
        </div>

        <div class="tab-content">
          <div v-if="activeTab === 'positions'" class="positions-list">
            <div v-if="tradingStore.positions.length === 0" class="empty-state">
              {{ t('common.noData') }}
            </div>
            <div 
              v-for="position in tradingStore.positions" 
              :key="position.id" 
              class="position-item"
            >
              <div class="position-header">
                <span class="symbol">{{ position.symbol }}</span>
                <span 
                  class="pnl" 
                  :class="{ positive: (position.unrealized_pnl || 0) >= 0, negative: (position.unrealized_pnl || 0) < 0 }"
                >
                  {{ (position.unrealized_pnl || 0) >= 0 ? '+' : '' }}${{ (position.unrealized_pnl || 0).toLocaleString() }}
                  ({{ (position.unrealized_pnl_percent || 0).toFixed(2) }}%)
                </span>
              </div>
              <div class="position-details">
                <div class="detail-row">
                  <span>{{ t('trading.quantity') }}</span>
                  <span>{{ position.quantity }}</span>
                </div>
                <div class="detail-row">
                  <span>{{ t('trading.averagePrice') }}</span>
                  <span>${{ position.avg_price.toLocaleString() }}</span>
                </div>
                <div class="detail-row">
                  <span>{{ t('trading.currentPrice') }}</span>
                  <span>${{ (position.current_price || 0).toLocaleString() }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="activeTab === 'orders'" class="orders-list">
            <div v-if="tradingStore.orders.length === 0" class="empty-state">
              {{ t('common.noData') }}
            </div>
            <div 
              v-for="order in tradingStore.orders" 
              :key="order.id" 
              class="order-item"
            >
              <div class="order-header">
                <span class="symbol">{{ order.symbol }}</span>
                <span class="side" :class="order.side">
                  {{ order.side === 'buy' ? t('trading.buy') : t('trading.sell') }}
                </span>
                <span class="status" :class="order.status">
                  {{ getStatusText(order.status) }}
                </span>
              </div>
              <div class="order-details">
                <div class="detail-row">
                  <span>{{ t('trading.type') }}</span>
                  <span>{{ getTypeText(order.type) }}</span>
                </div>
                <div class="detail-row">
                  <span>{{ t('trading.quantity') }}</span>
                  <span>{{ order.quantity }}</span>
                </div>
                <div class="detail-row">
                  <span>{{ t('trading.price') }}</span>
                  <span>{{ order.price ? '$' + order.price.toLocaleString() : t('trading.market') }}</span>
                </div>
                <div class="detail-row" v-if="order.status === 'filled'">
                  <span>{{ t('trading.filledPrice') }}</span>
                  <span>${{ (order.filled_price || 0).toLocaleString() }}</span>
                </div>
              </div>
              <div class="order-actions" v-if="order.status === 'pending'">
                <button class="cancel-btn" @click="cancelOrder(order.id)">
                  {{ t('common.cancel') }}
                </button>
              </div>
            </div>
          </div>

          <div v-if="activeTab === 'trades'" class="trades-list">
            <div v-if="tradingStore.trades.length === 0" class="empty-state">
              {{ t('common.noData') }}
            </div>
            <div 
              v-for="trade in tradingStore.trades" 
              :key="trade.id" 
              class="trade-item"
            >
              <div class="trade-header">
                <span class="symbol">{{ trade.symbol }}</span>
                <span class="side" :class="trade.side">
                  {{ trade.side === 'buy' ? t('trading.buy') : t('trading.sell') }}
                </span>
                <span 
                  class="pnl" 
                  :class="{ positive: (trade.pnl || 0) >= 0, negative: (trade.pnl || 0) < 0 }"
                  v-if="trade.pnl !== undefined"
                >
                  {{ (trade.pnl || 0) >= 0 ? '+' : '' }}${{ (trade.pnl || 0).toLocaleString() }}
                </span>
              </div>
              <div class="trade-details">
                <div class="detail-row">
                  <span>{{ t('trading.quantity') }}</span>
                  <span>{{ trade.quantity }}</span>
                </div>
                <div class="detail-row">
                  <span>{{ t('trading.price') }}</span>
                  <span>${{ trade.price.toLocaleString() }}</span>
                </div>
                <div class="detail-row">
                  <span>{{ t('common.time') }}</span>
                  <span>{{ formatTime(trade.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTradingStore } from '@/stores/trading'
import { useWebSocketStore } from '@/stores/websocket'
import { tradingService } from '@/services/trading'

const { t } = useI18n()
const tradingStore = useTradingStore()
const websocketStore = useWebSocketStore()

const isSimulation = ref(true)
const activeTab = ref('positions')
const loading = ref(false)
const currentPrice = ref<number | null>(null)

const symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']

const orderForm = ref({
  symbol: 'BTC',
  side: 'buy' as 'buy' | 'sell',
  type: 'market' as 'market' | 'limit' | 'stop',
  quantity: 0,
  price: 0
})

const estimatedTotal = computed(() => {
  const price = orderForm.value.type === 'market' ? (currentPrice.value || 0) : orderForm.value.price
  return price * orderForm.value.quantity
})

const canSubmit = computed(() => {
  return orderForm.value.symbol && 
         orderForm.value.side && 
         orderForm.value.quantity > 0 &&
         (orderForm.value.type === 'market' || orderForm.value.price > 0)
})

watch(() => orderForm.value.symbol, async (symbol) => {
  try {
    const response = await tradingService.getMarketPrice(symbol)
    if (response.success && response.data) {
      currentPrice.value = response.data.price
    }
  } catch (e) {
    console.error('Failed to get price:', e)
  }
}, { immediate: true })

watch(() => websocketStore.prices, (prices) => {
  const priceUpdate = prices.get(orderForm.value.symbol)
  if (priceUpdate) {
    currentPrice.value = priceUpdate.price
  }
}, { deep: true })

async function submitOrder() {
  if (!canSubmit.value) return

  loading.value = true
  try {
    await tradingStore.createOrder({
      ...orderForm.value,
      is_simulation: isSimulation.value
    })
    
    console.log('订单提交成功')
    orderForm.value.quantity = 0
    orderForm.value.price = 0
    
    await tradingStore.loadPositions({ is_simulation: isSimulation.value })
    await tradingStore.loadOrders({ is_simulation: isSimulation.value })
  } catch (e: any) {
    console.error('订单提交失败:', e.message)
  } finally {
    loading.value = false
  }
}

async function cancelOrder(orderId: number) {
  try {
    await tradingStore.cancelOrder(orderId)
    console.log('订单已取消')
  } catch (e: any) {
    console.error('取消订单失败:', e.message)
  }
}

function getStatusText(status: string) {
  const statusMap: Record<string, string> = {
    pending: t('trading.pending'),
    open: t('trading.open'),
    filled: t('trading.filled'),
    cancelled: t('trading.cancelled'),
    failed: t('common.error')
  }
  return statusMap[status] || status
}

function getTypeText(type: string) {
  const typeMap: Record<string, string> = {
    market: t('trading.marketOrder'),
    limit: t('trading.limitOrder'),
    stop: t('trading.stopOrder')
  }
  return typeMap[type] || type
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
  await tradingStore.loadPositions({ is_simulation: isSimulation.value })
  await tradingStore.loadOrders({ is_simulation: isSimulation.value })
  await tradingStore.loadTrades({ is_simulation: isSimulation.value })
})
</script>

<style scoped>
.trading-view {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.trading-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.trading-header h1 {
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

.trading-content {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 24px;
}

@media (max-width: 900px) {
  .trading-content {
    grid-template-columns: 1fr;
  }
}

.trading-panel {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

.order-form h2 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.form-group select,
.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
  box-sizing: border-box;
}

.form-group select:focus,
.form-group input:focus {
  outline: none;
  border-color: var(--primary);
}

.side-buttons {
  display: flex;
  gap: 8px;
}

.side-buttons button {
  flex: 1;
  padding: 12px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s;
}

.side-buttons .buy-btn.active {
  background: var(--success);
  color: white;
  border-color: var(--success);
}

.side-buttons .sell-btn.active {
  background: var(--danger);
  color: white;
  border-color: var(--danger);
}

.price-info {
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
  text-align: center;
  margin-bottom: 16px;
  color: var(--text-secondary);
}

.order-summary {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  margin-bottom: 16px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.summary-row span:first-child {
  color: var(--text-secondary);
}

.summary-row span:last-child {
  color: var(--text-primary);
  font-weight: 600;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn.buy {
  background: var(--success);
  color: white;
}

.submit-btn.sell {
  background: var(--danger);
  color: white;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.trading-data {
  background: var(--bg-card);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
}

.tabs button {
  flex: 1;
  padding: 16px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.tabs button.active {
  color: var(--primary);
  border-bottom: 2px solid var(--primary);
}

.tab-content {
  padding: 20px;
  max-height: 600px;
  overflow-y: auto;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.position-item,
.order-item,
.trade-item {
  padding: 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 12px;
}

.position-header,
.order-header,
.trade-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.symbol {
  font-weight: 600;
  color: var(--text-primary);
}

.side {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.side.buy {
  background: rgba(34, 197, 94, 0.1);
  color: var(--success);
}

.side.sell {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
}

.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status.pending {
  background: rgba(251, 191, 36, 0.1);
  color: #fbbf24;
}

.status.filled {
  background: rgba(34, 197, 94, 0.1);
  color: var(--success);
}

.status.cancelled {
  background: rgba(156, 163, 175, 0.1);
  color: #9ca3af;
}

.pnl {
  font-weight: 600;
}

.pnl.positive {
  color: var(--success);
}

.pnl.negative {
  color: var(--danger);
}

.position-details,
.order-details,
.trade-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.detail-row span:first-child {
  color: var(--text-secondary);
}

.detail-row span:last-child {
  color: var(--text-primary);
}

.order-actions {
  margin-top: 12px;
  text-align: right;
}

.cancel-btn {
  padding: 6px 12px;
  border: 1px solid var(--danger);
  background: transparent;
  color: var(--danger);
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: var(--danger);
  color: white;
}
</style>
