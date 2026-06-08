import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { websocket } from '@/services/websocket'
import type {
  OnlineUser,
  PriceUpdate,
  PnLUpdate,
  Order,
  Trade,
  Position,
  Portfolio,
  DirectMessage,
  Mention,
  AIRiskAlert,
  AISignal,
  WSNewSignalData,
  WSNewCommentData,
  WSNewNotificationData,
  WSSignalUpdateData,
  WSLikeUpdateData,
  WSFollowUpdateData,
  WSOnlineUsersData,
  WSUserStatusData,
  WSSystemMessage,
  WSTypingData,
  WSTypingStopData,
  WSConnectionStatus,
  WSErrorData
} from '@/types'

export const useWebSocketStore = defineStore('websocket', () => {
  const isConnected = ref(false)
  const isAuthenticated = ref(false)
  const isConnecting = ref(false)
  const connectionError = ref<string | null>(null)
  
  const onlineUsers = ref<OnlineUser[]>([])
  const onlineCount = ref(0)
  
  const prices = ref<Map<string, PriceUpdate>>(new Map())
  
  const pnlUpdates = ref<Map<number, PnLUpdate>>(new Map())
  
  const typingUsers = ref<Map<number, Set<number>>>(new Map())
  
  const systemMessages = ref<WSSystemMessage[]>([])
  
  const orders = ref<Map<number, Order>>(new Map())
  const trades = ref<Trade[]>([])
  const positions = ref<Map<number, Position>>(new Map())
  const portfolios = ref<Map<number, Portfolio>>(new Map())
  const directMessages = ref<Map<number, DirectMessage[]>>(new Map())
  const mentions = ref<Mention[]>([])
  const aiAlerts = ref<AIRiskAlert[]>([])
  const aiSignals = ref<AISignal[]>([])
  
  const unsubscribers: (() => void)[] = []

  const connectionStatus = computed(() => {
    if (isConnecting.value) return 'connecting'
    if (isConnected.value && isAuthenticated.value) return 'connected'
    if (connectionError.value) return 'error'
    return 'disconnected'
  })

  async function connect(): Promise<void> {
    if (isConnecting.value || (isConnected.value && isAuthenticated.value)) {
      return
    }

    isConnecting.value = true
    connectionError.value = null

    try {
      await websocket.connect()
      isConnected.value = true
      isAuthenticated.value = true
      setupListeners()
      websocket.getOnlineUsers()
    } catch (e: any) {
      connectionError.value = e.message || '连接失败'
      throw e
    } finally {
      isConnecting.value = false
    }
  }

  function disconnect(): void {
    cleanupListeners()
    websocket.disconnect()
    isConnected.value = false
    isAuthenticated.value = false
    isConnecting.value = false
    onlineUsers.value = []
    onlineCount.value = 0
    prices.value.clear()
    pnlUpdates.value.clear()
    typingUsers.value.clear()
    orders.value.clear()
    trades.value = []
    positions.value.clear()
    portfolios.value.clear()
    directMessages.value.clear()
    mentions.value = []
    aiAlerts.value = []
    aiSignals.value = []
  }

  function setupListeners(): void {
    cleanupListeners()

    unsubscribers.push(
      websocket.on('ws:connected', (data: WSConnectionStatus) => {
        isConnected.value = data.connected
        connectionError.value = null
      })
    )

    unsubscribers.push(
      websocket.on('ws:disconnected', (data: WSConnectionStatus) => {
        isConnected.value = data.connected
        isAuthenticated.value = false
      })
    )

    unsubscribers.push(
      websocket.on('ws:authenticated', () => {
        isAuthenticated.value = true
      })
    )

    unsubscribers.push(
      websocket.on('ws:auth_error', (data: WSErrorData) => {
        connectionError.value = data.error || data.message || '认证失败'
        isAuthenticated.value = false
      })
    )

    unsubscribers.push(
      websocket.on('ws:error', (data: WSErrorData) => {
        connectionError.value = data.error || data.message || '连接错误'
      })
    )

    unsubscribers.push(
      websocket.on('signal:new', (data: WSNewSignalData) => {
        handleNewSignal(data)
      })
    )

    unsubscribers.push(
      websocket.on('signal:update', (data: WSSignalUpdateData) => {
        handleSignalUpdate(data)
      })
    )

    unsubscribers.push(
      websocket.on('comment:new', (data: WSNewCommentData) => {
        handleNewComment(data)
      })
    )

    unsubscribers.push(
      websocket.on('notification:new', (data: WSNewNotificationData) => {
        handleNewNotification(data)
      })
    )

    unsubscribers.push(
      websocket.on('like:update', (data: WSLikeUpdateData) => {
        handleLikeUpdate(data)
      })
    )

    unsubscribers.push(
      websocket.on('follow:update', (data: WSFollowUpdateData) => {
        handleFollowUpdate(data)
      })
    )

    unsubscribers.push(
      websocket.on('price:update', (data: PriceUpdate) => {
        handlePriceUpdate(data)
      })
    )

    unsubscribers.push(
      websocket.on('pnl:update', (data: PnLUpdate) => {
        handlePnLUpdate(data)
      })
    )

    unsubscribers.push(
      websocket.on('users:online', (data: WSOnlineUsersData) => {
        onlineUsers.value = data.data
        onlineCount.value = data.count
      })
    )

    unsubscribers.push(
      websocket.on('user:status', (data: WSUserStatusData) => {
        handleUserStatusChange(data)
      })
    )

    unsubscribers.push(
      websocket.on('system:message', (data: WSSystemMessage) => {
        handleSystemMessage(data)
      })
    )

    unsubscribers.push(
      websocket.on('typing:user', (data: WSTypingData) => {
        handleTypingStart(data)
      })
    )

    unsubscribers.push(
      websocket.on('typing:user_stop', (data: WSTypingStopData) => {
        handleTypingStop(data)
      })
    )

    unsubscribers.push(
      websocket.on('order:update', (data: { order: Order }) => {
        handleOrderUpdate(data.order)
      })
    )

    unsubscribers.push(
      websocket.on('trade:new', (data: { trade: Trade }) => {
        handleNewTrade(data.trade)
      })
    )

    unsubscribers.push(
      websocket.on('position:update', (data: { position: Position }) => {
        handlePositionUpdate(data.position)
      })
    )

    unsubscribers.push(
      websocket.on('portfolio:update', (data: { portfolio: Portfolio }) => {
        handlePortfolioUpdate(data.portfolio)
      })
    )

    unsubscribers.push(
      websocket.on('message:new', (data: { message: DirectMessage }) => {
        handleNewMessage(data.message)
      })
    )

    unsubscribers.push(
      websocket.on('mention:new', (data: { mention: Mention }) => {
        handleNewMention(data.mention)
      })
    )

    unsubscribers.push(
      websocket.on('ai:alert', (data: { alert: AIRiskAlert }) => {
        handleAIAlert(data.alert)
      })
    )

    unsubscribers.push(
      websocket.on('ai:signal', (data: { signal: AISignal }) => {
        handleAISignal(data.signal)
      })
    )
  }

  function cleanupListeners(): void {
    unsubscribers.forEach(unsubscribe => {
      try {
        unsubscribe()
      } catch (e) {
        console.error('[WS] Error cleaning up listener:', e)
      }
    })
    unsubscribers.length = 0
  }

  function handleNewSignal(data: WSNewSignalData): void {
    const signalStore = useSignalStore()
    if (!signalStore.signals.find(s => s.id === data.data.id)) {
      signalStore.signals.unshift(data.data)
    }
  }

  function handleSignalUpdate(data: WSSignalUpdateData): void {
    const signalStore = useSignalStore()
    const signal = signalStore.signals.find(s => s.id === data.signal_id)
    if (signal) {
      Object.assign(signal, data.data)
    }
    if (signalStore.currentSignal?.id === data.signal_id) {
      Object.assign(signalStore.currentSignal, data.data)
    }
  }

  function handleNewComment(data: WSNewCommentData): void {
    const signalStore = useSignalStore()
    if (signalStore.currentSignal?.id === data.signal_id) {
      if (!signalStore.replies.find(r => r.id === data.data.id)) {
        signalStore.replies.unshift(data.data)
      }
    }
    const signal = signalStore.signals.find(s => s.id === data.signal_id)
    if (signal) {
      signal.reply_count = (signal.reply_count || 0) + 1
    }
  }

  function handleNewNotification(data: WSNewNotificationData): void {
    const notificationStore = useNotificationStore()
    if (!notificationStore.notifications.find(n => n.id === data.data.id)) {
      notificationStore.notifications.unshift(data.data)
    }
  }

  function handleLikeUpdate(data: WSLikeUpdateData): void {
    const signalStore = useSignalStore()
    const signal = signalStore.signals.find(s => s.id === data.signal_id)
    if (signal) {
      signal.likes = data.likes
      signal.is_liked = data.is_liked
    }
    if (signalStore.currentSignal?.id === data.signal_id) {
      signalStore.currentSignal.likes = data.likes
      signalStore.currentSignal.is_liked = data.is_liked
    }
  }

  function handleFollowUpdate(data: WSFollowUpdateData): void {
    const signalStore = useSignalStore()
    const signal = signalStore.signals.find(s => s.id === data.signal_id)
    if (signal) {
      signal.is_following = data.is_following
      signal.participant_count = data.participant_count
    }
    if (signalStore.currentSignal?.id === data.signal_id) {
      signalStore.currentSignal.is_following = data.is_following
      signalStore.currentSignal.participant_count = data.participant_count
    }
  }

  function handlePriceUpdate(data: PriceUpdate): void {
    prices.value.set(data.symbol, data)
  }

  function handlePnLUpdate(data: PnLUpdate): void {
    pnlUpdates.value.set(data.signal_id, data)
  }

  function handleUserStatusChange(data: WSUserStatusData): void {
    if (data.status === 'online') {
      if (!onlineUsers.value.find(u => u.user_id === data.user_id)) {
        onlineUsers.value.push({
          user_id: data.user_id,
          username: data.user.username,
          display_name: data.user.display_name,
          connected_at: data.timestamp,
          last_active: data.timestamp
        })
        onlineCount.value = onlineUsers.value.length
      }
    } else {
      const index = onlineUsers.value.findIndex(u => u.user_id === data.user_id)
      if (index > -1) {
        onlineUsers.value.splice(index, 1)
        onlineCount.value = onlineUsers.value.length
      }
    }
  }

  function handleSystemMessage(data: WSSystemMessage): void {
    systemMessages.value.unshift(data)
    if (systemMessages.value.length > 50) {
      systemMessages.value.pop()
    }
  }

  function handleTypingStart(data: WSTypingData): void {
    if (!typingUsers.value.has(data.signal_id)) {
      typingUsers.value.set(data.signal_id, new Set())
    }
    typingUsers.value.get(data.signal_id)!.add(data.user.user_id)
  }

  function handleTypingStop(data: WSTypingStopData): void {
    const users = typingUsers.value.get(data.signal_id)
    if (users) {
      users.delete(data.user_id)
      if (users.size === 0) {
        typingUsers.value.delete(data.signal_id)
      }
    }
  }

  function handleOrderUpdate(order: Order): void {
    orders.value.set(order.id, order)
    try {
      const tradingStore = useTradingStore()
      tradingStore.updateOrder(order)
    } catch (e) {
      console.error('[WS] Error updating order in trading store:', e)
    }
  }

  function handleNewTrade(trade: Trade): void {
    trades.value.unshift(trade)
    if (trades.value.length > 100) {
      trades.value.pop()
    }
    try {
      const tradingStore = useTradingStore()
      tradingStore.addTrade(trade)
    } catch (e) {
      console.error('[WS] Error adding trade to trading store:', e)
    }
  }

  function handlePositionUpdate(position: Position): void {
    positions.value.set(position.id, position)
    try {
      const tradingStore = useTradingStore()
      tradingStore.updatePosition(position)
    } catch (e) {
      console.error('[WS] Error updating position in trading store:', e)
    }
  }

  function handlePortfolioUpdate(portfolio: Portfolio): void {
    portfolios.value.set(portfolio.id, portfolio)
    try {
      const tradingStore = useTradingStore()
      tradingStore.updatePortfolio(portfolio)
    } catch (e) {
      console.error('[WS] Error updating portfolio in trading store:', e)
    }
  }

  function handleNewMessage(message: DirectMessage): void {
    const otherUserId = message.sender_id === useUserStore().user?.id ? message.receiver_id : message.sender_id
    if (!directMessages.value.has(otherUserId)) {
      directMessages.value.set(otherUserId, [])
    }
    directMessages.value.get(otherUserId)!.push(message)
    try {
      const socialStore = useSocialStore()
      socialStore.addMessage(message)
    } catch (e) {
      console.error('[WS] Error adding message to social store:', e)
    }
  }

  function handleNewMention(mention: Mention): void {
    mentions.value.unshift(mention)
    if (mentions.value.length > 50) {
      mentions.value.pop()
    }
    try {
      const socialStore = useSocialStore()
      socialStore.addMention(mention)
    } catch (e) {
      console.error('[WS] Error adding mention to social store:', e)
    }
  }

  function handleAIAlert(alert: AIRiskAlert): void {
    aiAlerts.value.unshift(alert)
    if (aiAlerts.value.length > 50) {
      aiAlerts.value.pop()
    }
    try {
      const aiStore = useAIStore()
      aiStore.addAlert(alert)
    } catch (e) {
      console.error('[WS] Error adding alert to AI store:', e)
    }
  }

  function handleAISignal(signal: AISignal): void {
    aiSignals.value.unshift(signal)
    if (aiSignals.value.length > 50) {
      aiSignals.value.pop()
    }
    try {
      const aiStore = useAIStore()
      aiStore.addSignal(signal)
    } catch (e) {
      console.error('[WS] Error adding AI signal to AI store:', e)
    }
  }

  function getPrice(symbol: string): PriceUpdate | undefined {
    return prices.value.get(symbol)
  }

  function getPnL(signalId: number): PnLUpdate | undefined {
    return pnlUpdates.value.get(signalId)
  }

  function getTypingUsers(signalId: number): number[] {
    const users = typingUsers.value.get(signalId)
    return users ? Array.from(users) : []
  }

  function joinSignalRoom(signalId: number): void {
    websocket.joinSignalRoom(signalId)
  }

  function leaveSignalRoom(signalId: number): void {
    websocket.leaveSignalRoom(signalId)
    typingUsers.value.delete(signalId)
  }

  function subscribeMarket(symbols: string[]): void {
    websocket.subscribeMarket(symbols)
  }

  function unsubscribeMarket(symbols: string[]): void {
    websocket.unsubscribeMarket(symbols)
    symbols.forEach(s => prices.value.delete(s))
  }

  function startTyping(signalId: number): void {
    websocket.startTyping(signalId)
  }

  function stopTyping(signalId: number): void {
    websocket.stopTyping(signalId)
  }

  function refreshOnlineUsers(): void {
    websocket.getOnlineUsers()
  }

  function clearError(): void {
    connectionError.value = null
  }

  function isReady(): boolean {
    return isConnected.value && isAuthenticated.value
  }

  return {
    isConnected,
    isAuthenticated,
    isConnecting,
    connectionError,
    connectionStatus,
    onlineUsers,
    onlineCount,
    prices,
    pnlUpdates,
    systemMessages,
    orders,
    trades,
    positions,
    portfolios,
    directMessages,
    mentions,
    aiAlerts,
    aiSignals,
    connect,
    disconnect,
    isReady,
    getPrice,
    getPnL,
    getTypingUsers,
    joinSignalRoom,
    leaveSignalRoom,
    subscribeMarket,
    unsubscribeMarket,
    startTyping,
    stopTyping,
    refreshOnlineUsers,
    clearError
  }
})

import { useSignalStore } from './signal'
import { useNotificationStore } from './notification'
import { useUserStore } from './user'
import { useTradingStore } from './trading'
import { useSocialStore } from './social'
import { useAIStore } from './ai'
