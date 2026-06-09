import { apiClient } from './api'
import type { AISignal, AIAnalysis, AIRiskAlert, AIStrategy, ApiResponse, PaginatedResponse } from '../types'

export const aiService = {
  async generateSignal(data: {
    symbol: string
    strategy?: string
    risk_level?: 'low' | 'medium' | 'high'
  }): Promise<ApiResponse<AISignal>> {
    const response = await apiClient.post('/ai/signals/generate', data)
    return response.data
  },

  async getAISignals(params?: {
    status?: string
    symbol?: string
    page?: number
    per_page?: number
  }): Promise<ApiResponse<PaginatedResponse<AISignal>>> {
    const response = await apiClient.get('/ai/signals', { params })
    return response.data
  },

  async analyzeTrading(analysisType: string = 'comprehensive'): Promise<ApiResponse<AIAnalysis>> {
    const response = await apiClient.post('/ai/analyze/trading', { type: analysisType })
    return response.data
  },

  async checkRiskAlerts(): Promise<ApiResponse<AIRiskAlert[]>> {
    const response = await apiClient.post('/ai/alerts/check')
    return response.data
  },

  async getRiskAlerts(params?: {
    severity?: string
    is_acknowledged?: boolean
    page?: number
    per_page?: number
  }): Promise<ApiResponse<PaginatedResponse<AIRiskAlert>>> {
    const response = await apiClient.get('/ai/alerts', { params })
    return response.data
  },

  async acknowledgeRiskAlert(alertId: number): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post(`/ai/alerts/${alertId}/acknowledge`)
    return response.data
  },

  async generateStrategy(data: {
    type?: string
    risk_level?: string
    symbols?: string[]
  }): Promise<ApiResponse<AIStrategy>> {
    const response = await apiClient.post('/ai/strategies/generate', data)
    return response.data
  },

  async backtestStrategy(strategyId: number, data?: {
    start_date?: string
    end_date?: string
    initial_capital?: number
  }): Promise<ApiResponse<{ strategy_id: number; backtest_result: any }>> {
    const response = await apiClient.post(`/ai/strategies/${strategyId}/backtest`, data)
    return response.data
  },

  async getStrategies(params?: {
    is_active?: boolean
    page?: number
    per_page?: number
  }): Promise<ApiResponse<PaginatedResponse<AIStrategy>>> {
    const response = await apiClient.get('/ai/strategies', { params })
    return response.data
  },

  async chat(message: string, context?: any): Promise<ApiResponse<{ response: string; timestamp: string }>> {
    const response = await apiClient.post('/ai/chat', { message, context })
    return response.data
  },

  async getAnalysisHistory(params?: {
    analysis_type?: string
    page?: number
    per_page?: number
  }): Promise<ApiResponse<PaginatedResponse<AIAnalysis>>> {
    const response = await apiClient.get('/ai/analysis/history', { params })
    return response.data
  },

  async runBacktest(strategyId: number, data?: {
    start_date?: string
    end_date?: string
    initial_capital?: number
  }): Promise<ApiResponse<AIStrategy>> {
    const response = await apiClient.post(`/ai/strategies/${strategyId}/backtest`, data)
    return response.data
  },

  async saveStrategy(strategy: AIStrategy): Promise<ApiResponse<AIStrategy>> {
    const response = await apiClient.post('/ai/strategies', strategy)
    return response.data
  },

  async activateStrategy(strategyId: number): Promise<ApiResponse<{ status: string }>> {
    const response = await apiClient.post(`/ai/strategies/${strategyId}/activate`)
    return response.data
  }
}
