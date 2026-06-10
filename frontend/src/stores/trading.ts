import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Order, Trade, Position, Portfolio, ExchangeAccount } from '../types'
import { tradingService } from '../services/trading'

export const useTradingStore = defineStore('trading', () => {
  const orders = ref<Order[]>([])
  const positions = ref<Position[]>([])
  const trades = ref<Trade[]>([])
  const portfolio = ref<Portfolio | null>(null)
  const exchangeAccounts = ref<ExchangeAccount[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const totalUnrealizedPnl = computed(() => {
    return positions.value.reduce((sum, p) => sum + (p.unrealized_pnl || 0), 0)
  })

  const totalPositionValue = computed(() => {
    return positions.value.reduce((sum, p) => sum + (p.current_price || 0) * p.quantity, 0)
  })

  async function loadPortfolio(isSimulation: boolean = true) {
    loading.value = true
    error.value = null
    try {
      console.log('[Portfolio] 开始加载...', 'is_simulation:', isSimulation)
      const response = await tradingService.getPortfolio(isSimulation)
      console.log('[Portfolio] 收到响应:', JSON.stringify(response).slice(0, 200))
      if (response.success && response.data) {
        portfolio.value = response.data.portfolio
        positions.value = response.data.positions
        trades.value = response.data.recent_trades
        console.log('[Portfolio] 数据加载成功')
      } else {
        console.warn('[Portfolio] 响应异常:', response)
        error.value = '响应数据格式异常'
      }
    } catch (e: any) {
      console.error('[Portfolio] 请求失败:', e.message)
      error.value = e.message || '加载投资组合失败'
    } finally {
      loading.value = false
      console.log('[Portfolio] 加载完成')
    }
  }

  async function loadOrders(params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await tradingService.getOrders(params)
      if (response.success && response.data) {
        orders.value = response.data.items
      }
    } catch (e: any) {
      error.value = e.message || '加载订单失败'
    } finally {
      loading.value = false
    }
  }

  async function loadPositions(params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await tradingService.getPositions(params)
      if (response.success && response.data) {
        positions.value = response.data
      }
    } catch (e: any) {
      error.value = e.message || '加载持仓失败'
    } finally {
      loading.value = false
    }
  }

  async function loadTrades(params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await tradingService.getTrades(params)
      if (response.success && response.data) {
        trades.value = response.data.items
      }
    } catch (e: any) {
      error.value = e.message || '加载交易历史失败'
    } finally {
      loading.value = false
    }
  }

  async function loadExchangeAccounts() {
    loading.value = true
    error.value = null
    try {
      const response = await tradingService.getExchangeAccounts()
      if (response.success && response.data) {
        exchangeAccounts.value = response.data
      }
    } catch (e: any) {
      error.value = e.message || '加载交易所账户失败'
    } finally {
      loading.value = false
    }
  }

  async function createOrder(data: any) {
    loading.value = true
    error.value = null
    try {
      const response = await tradingService.createOrder(data)
      if (response.success && response.data) {
        orders.value.unshift(response.data)
        return response.data
      }
      throw new Error(response.message || '创建订单失败')
    } catch (e: any) {
      error.value = e.message || '创建订单失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function cancelOrder(orderId: number) {
    try {
      const response = await tradingService.cancelOrder(orderId)
      if (response.success) {
        const index = orders.value.findIndex(o => o.id === orderId)
        if (index !== -1 && response.data) {
          orders.value[index] = response.data
        }
      }
      return response
    } catch (e: any) {
      error.value = e.message || '取消订单失败'
      throw e
    }
  }

  function addOrder(order: Order) {
    const existing = orders.value.find(o => o.id === order.id)
    if (!existing) {
      orders.value.unshift(order)
    } else {
      Object.assign(existing, order)
    }
  }

  function addTrade(trade: Trade) {
    const existing = trades.value.find(t => t.id === trade.id)
    if (!existing) {
      trades.value.unshift(trade)
    }
  }

  function updatePosition(position: Position) {
    const index = positions.value.findIndex(p => p.id === position.id)
    if (index !== -1) {
      positions.value[index] = position
    } else {
      positions.value.push(position)
    }
  }

  function updatePortfolio(portfolioData: Portfolio) {
    portfolio.value = portfolioData
  }

  return {
    orders,
    positions,
    trades,
    portfolio,
    exchangeAccounts,
    loading,
    error,
    totalUnrealizedPnl,
    totalPositionValue,
    loadPortfolio,
    loadOrders,
    loadPositions,
    loadTrades,
    loadExchangeAccounts,
    createOrder,
    cancelOrder,
    addOrder,
    addTrade,
    updatePosition,
    updatePortfolio
  }
})
