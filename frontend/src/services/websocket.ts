import { io, Socket } from 'socket.io-client'

const SOCKET_URL = import.meta.env.VITE_WS_URL || '/'

class WebSocketService {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  private reconnectDelay = 1000
  private eventListeners: Map<string, Set<Function>> = new Map()
  private isConnected = false
  private isAuthenticated = false

  connect(token?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.socket?.connected) {
        resolve()
        return
      }

      const authToken = token || localStorage.getItem('auth_token')
      
      if (!authToken) {
        reject(new Error('No authentication token available'))
        return
      }

      this.socket = io(SOCKET_URL, {
        transports: ['websocket', 'polling'],
        auth: {
          token: authToken
        },
        extraHeaders: {
          Authorization: `Bearer ${authToken}`
        },
        reconnection: true,
        reconnectionDelay: this.reconnectDelay,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: this.maxReconnectAttempts,
        timeout: 20000
      })

      this.socket.on('connect', () => {
        this.isConnected = true
        this.reconnectAttempts = 0
        console.log('[WS] Connected')
        this.emit('ws:connected', { connected: true })
      })

      this.socket.on('disconnect', (reason) => {
        this.isConnected = false
        this.isAuthenticated = false
        console.log('[WS] Disconnected:', reason)
        this.emit('ws:disconnected', { connected: false, reason })
      })

      this.socket.on('connect_error', (error) => {
        console.error('[WS] Connection error:', error)
        this.reconnectAttempts++
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
          reject(error)
        }
        this.emit('ws:error', { error: error.message })
      })

      this.socket.on('auth:success', (data) => {
        this.isAuthenticated = true
        console.log('[WS] Authenticated:', data.user?.username)
        this.emit('ws:authenticated', data)
        resolve()
      })

      this.socket.on('auth:error', (data) => {
        console.error('[WS] Auth error:', data.message)
        this.emit('ws:auth_error', data)
        reject(new Error(data.message))
      })

      this.socket.on('signal:new', (data) => {
        this.emit('signal:new', data)
      })

      this.socket.on('signal:update', (data) => {
        this.emit('signal:update', data)
      })

      this.socket.on('comment:new', (data) => {
        this.emit('comment:new', data)
      })

      this.socket.on('notification:new', (data) => {
        this.emit('notification:new', data)
      })

      this.socket.on('like:update', (data) => {
        this.emit('like:update', data)
      })

      this.socket.on('follow:update', (data) => {
        this.emit('follow:update', data)
      })

      this.socket.on('price:update', (data) => {
        this.emit('price:update', data)
      })

      this.socket.on('pnl:update', (data) => {
        this.emit('pnl:update', data)
      })

      this.socket.on('users:online', (data) => {
        this.emit('users:online', data)
      })

      this.socket.on('user:status', (data) => {
        this.emit('user:status', data)
      })

      this.socket.on('system:message', (data) => {
        this.emit('system:message', data)
      })

      this.socket.on('typing:user', (data) => {
        this.emit('typing:user', data)
      })

      this.socket.on('typing:user_stop', (data) => {
        this.emit('typing:user_stop', data)
      })

      this.socket.on('pong', (data) => {
        this.emit('ws:pong', data)
      })

      this.socket.on('error', (data) => {
        console.error('[WS] Error:', data.message)
        this.emit('ws:error', data)
      })
    })
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      this.isConnected = false
      this.isAuthenticated = false
      console.log('[WS] Disconnected manually')
    }
  }

  on(event: string, callback: Function): () => void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set())
    }
    this.eventListeners.get(event)!.add(callback)

    return () => {
      this.eventListeners.get(event)?.delete(callback)
    }
  }

  private emit(event: string, data: any): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data)
        } catch (e) {
          console.error(`[WS] Error in listener for ${event}:`, e)
        }
      })
    }
  }

  send(event: string, data?: any): void {
    if (this.socket?.connected) {
      this.socket.emit(event, data)
    } else {
      console.warn('[WS] Cannot send, not connected:', event)
    }
  }

  joinSignalRoom(signalId: number): void {
    this.send('signal:join', { signal_id: signalId })
  }

  leaveSignalRoom(signalId: number): void {
    this.send('signal:leave', { signal_id: signalId })
  }

  subscribeMarket(symbols: string[]): void {
    this.send('market:subscribe', { symbols })
  }

  unsubscribeMarket(symbols: string[]): void {
    this.send('market:unsubscribe', { symbols })
  }

  getOnlineUsers(): void {
    this.send('users:get_online')
  }

  startTyping(signalId: number): void {
    this.send('typing:start', { signal_id: signalId })
  }

  stopTyping(signalId: number): void {
    this.send('typing:stop', { signal_id: signalId })
  }

  ping(): void {
    this.send('ping')
  }

  getConnectionStatus(): { connected: boolean; authenticated: boolean } {
    return {
      connected: this.isConnected,
      authenticated: this.isAuthenticated
    }
  }

  isReady(): boolean {
    return this.isConnected && this.isAuthenticated
  }
}

export const websocket = new WebSocketService()
export default websocket
