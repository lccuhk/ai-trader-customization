import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { authApi } from '@/services/api'
import { useWebSocketStore } from './websocket'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  function setUser(userData: User | null) {
    user.value = userData
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData))
    } else {
      localStorage.removeItem('user')
    }
  }

  function setToken(newToken: string | null) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('auth_token', newToken)
    } else {
      localStorage.removeItem('auth_token')
    }
  }

  async function login(username: string, password: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await authApi.login({ username, password })
      if (response.data.success && response.data.token && response.data.user) {
        setToken(response.data.token)
        setUser(response.data.user)
        
        // Try to connect websocket in background without blocking
        const websocketStore = useWebSocketStore()
        websocketStore.connect().catch((e: any) => {
          console.warn('[WS] Connect after login failed:', e.message)
        })
        
        return { success: true }
      }
      return { success: false, message: response.data.message || '登录失败' }
    } catch (e: any) {
      const resp = e.response?.data
      error.value = resp?.message || resp?.detail || '登录失败'
      return { success: false, message: error.value }
    } finally {
      isLoading.value = false
    }
  }

  async function register(data: { username: string; email: string; display_name: string; password: string }) {
    isLoading.value = true
    error.value = null
    try {
      const response = await authApi.register(data)
      if (response.data.success) {
        if (response.data.token && response.data.user) {
          setToken(response.data.token)
          setUser(response.data.user)
          
          const websocketStore = useWebSocketStore()
          websocketStore.connect().catch((e: any) => {
            console.warn('[WS] Connect after register failed:', e.message)
          })
        }
        return { success: true, message: response.data.message }
      }
      return { success: false, message: response.data.message || '注册失败' }
    } catch (e: any) {
      const resp = e.response?.data
      error.value = resp?.message || resp?.detail || '注册失败'
      return { success: false, message: error.value }
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCurrentUser() {
    if (!token.value) return
    try {
      const response = await authApi.getCurrentUser()
      if (response.data.success && response.data.data) {
        setUser(response.data.data)
        return true
      } else {
        setUser(null)
        setToken(null)
        return false
      }
    } catch (e: any) {
      console.error('Failed to fetch user:', e)
      if (e.response?.status === 401) {
        setUser(null)
        setToken(null)
      }
      return false
    }
  }

  function logout() {
    const websocketStore = useWebSocketStore()
    websocketStore.disconnect()
    
    setUser(null)
    setToken(null)
  }

  function initializeFromStorage() {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch {
        localStorage.removeItem('user')
      }
    }
  }

  return {
    user,
    token,
    isLoading,
    error,
    isLoggedIn,
    login,
    register,
    fetchCurrentUser,
    logout,
    initializeFromStorage
  }
})
