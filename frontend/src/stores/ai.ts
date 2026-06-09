import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { AISignal, AIAnalysis, AIRiskAlert, AIStrategy } from '../types'
import { aiService } from '../services/ai'

export const useAIStore = defineStore('ai', () => {
  const aiSignals = ref<AISignal[]>([])
  const analysis = ref<AIAnalysis | null>(null)
  const riskAlerts = ref<AIRiskAlert[]>([])
  const strategies = ref<AIStrategy[]>([])
  const chatMessages = ref<Array<{ role: 'user' | 'ai'; content: string; timestamp: string }>>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function generateSignal(data: any) {
    loading.value = true
    error.value = null
    try {
      const response = await aiService.generateSignal(data)
      if (response.success && response.data) {
        aiSignals.value.unshift(response.data)
      }
      return response
    } catch (e: any) {
      error.value = e.message || '生成AI信号失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function loadAISignals(params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await aiService.getAISignals(params)
      if (response.success && response.data) {
        aiSignals.value = response.data.items
      }
    } catch (e: any) {
      error.value = e.message || '加载AI信号失败'
    } finally {
      loading.value = false
    }
  }

  async function analyzeTrading(analysisType: string = 'comprehensive') {
    loading.value = true
    error.value = null
    try {
      const response = await aiService.analyzeTrading(analysisType)
      if (response.success && response.data) {
        analysis.value = response.data
      }
      return response
    } catch (e: any) {
      error.value = e.message || '分析交易失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function checkRiskAlerts() {
    loading.value = true
    error.value = null
    try {
      const response = await aiService.checkRiskAlerts()
      if (response.success && response.data) {
        response.data.forEach(alert => {
          const existing = riskAlerts.value.find(a => a.id === alert.id)
          if (!existing) {
            riskAlerts.value.unshift(alert)
          }
        })
      }
      return response
    } catch (e: any) {
      error.value = e.message || '检查风险预警失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function loadRiskAlerts(params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await aiService.getRiskAlerts(params)
      if (response.success && response.data) {
        riskAlerts.value = response.data.items
      }
    } catch (e: any) {
      error.value = e.message || '加载风险预警失败'
    } finally {
      loading.value = false
    }
  }

  async function acknowledgeAlert(alertId: number) {
    try {
      const response = await aiService.acknowledgeRiskAlert(alertId)
      if (response.success) {
        const alert = riskAlerts.value.find(a => a.id === alertId)
        if (alert) {
          alert.is_acknowledged = true
        }
      }
      return response
    } catch (e: any) {
      error.value = e.message || '确认预警失败'
      throw e
    }
  }

  async function generateStrategy(data: any) {
    loading.value = true
    error.value = null
    try {
      const response = await aiService.generateStrategy(data)
      if (response.success && response.data) {
        strategies.value.unshift(response.data)
      }
      return response
    } catch (e: any) {
      error.value = e.message || '生成策略失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function backtestStrategy(strategyId: number, data?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await aiService.backtestStrategy(strategyId, data)
      return response
    } catch (e: any) {
      error.value = e.message || '回测策略失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function loadStrategies(params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await aiService.getStrategies(params)
      if (response.success && response.data) {
        strategies.value = response.data.items
      }
    } catch (e: any) {
      error.value = e.message || '加载策略列表失败'
    } finally {
      loading.value = false
    }
  }

  const analysisHistory = ref<AIAnalysis[]>([])

  async function getAnalysisHistory(params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await aiService.getAnalysisHistory(params)
      if (response.success && response.data) {
        analysisHistory.value = response.data.items
      }
      return response
    } catch (e: any) {
      error.value = e.message || '加载分析历史失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function chat(message: string, context?: any) {
    chatMessages.value.push({
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    })

    loading.value = true
    error.value = null
    try {
      const response = await aiService.chat(message, context)
      if (response.success && response.data) {
        chatMessages.value.push({
          role: 'ai',
          content: response.data.response,
          timestamp: response.data.timestamp
        })
      }
      return response
    } catch (e: any) {
      error.value = e.message || 'AI对话失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  function addRiskAlert(alert: AIRiskAlert) {
    const existing = riskAlerts.value.find(a => a.id === alert.id)
    if (!existing) {
      riskAlerts.value.unshift(alert)
    }
  }

  function addAISignal(signal: AISignal) {
    const existing = aiSignals.value.find(s => s.id === signal.id)
    if (!existing) {
      aiSignals.value.unshift(signal)
    }
  }

  function clearChat() {
    chatMessages.value = []
  }

  return {
    aiSignals,
    analysis,
    analysisHistory,
    riskAlerts,
    strategies,
    chatMessages,
    loading,
    error,
    generateSignal,
    loadAISignals,
    analyzeTrading,
    checkRiskAlerts,
    loadRiskAlerts,
    acknowledgeAlert,
    generateStrategy,
    backtestStrategy,
    loadStrategies,
    getAnalysisHistory,
    chat,
    addRiskAlert,
    addAISignal,
    clearChat
  }
})
