import { apiClient } from './api'
import type { ApiResponse } from '../types'

export interface Strategy {
  id: number
  name: string
  description: string
  type: 'trend' | 'mean_reversion' | 'arbitrage' | 'momentum' | 'custom'
  status: 'active' | 'paused' | 'draft'
  code: string
  parameters: Record<string, any>
  winRate: number
  profitFactor: number
  maxDrawdown: number
  totalTrades: number
  createdAt: string
  updatedAt: string
}

export interface StrategyTemplate {
  id: number
  name: string
  description: string
  category: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  expectedWinRate: number
  expectedProfitFactor: number
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH'
  users: number
  rating: number
  code: string
  parameters: Record<string, any>
}

export interface BacktestResult {
  totalReturn: number
  annualReturn: number
  maxDrawdown: number
  winRate: number
  profitFactor: number
  sharpeRatio: number
  totalTrades: number
  winningTrades: number
  losingTrades: number
  equityCurve: { date: string; value: number }[]
  tradeHistory: any[]
}

export const strategyService = {
  async getStrategies(params?: {
    status?: string
    type?: string
  }): Promise<ApiResponse<Strategy[]>> {
    const response = await apiClient.get('/strategies', { params })
    return response.data
  },

  async getStrategy(id: number): Promise<ApiResponse<Strategy>> {
    const response = await apiClient.get(`/strategies/${id}`)
    return response.data
  },

  async createStrategy(data: Omit<Strategy, 'id' | 'createdAt' | 'updatedAt'>): Promise<ApiResponse<Strategy>> {
    const response = await apiClient.post('/strategies', data)
    return response.data
  },

  async updateStrategy(id: number, data: Partial<Strategy>): Promise<ApiResponse<Strategy>> {
    const response = await apiClient.put(`/strategies/${id}`, data)
    return response.data
  },

  async deleteStrategy(id: number): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.delete(`/strategies/${id}`)
    return response.data
  },

  async getTemplates(params?: {
    category?: string
    difficulty?: string
  }): Promise<ApiResponse<StrategyTemplate[]>> {
    const response = await apiClient.get('/strategies/templates', { params })
    return response.data
  },

  async runBacktest(strategyId: number, params: {
    startDate: string
    endDate: string
    initialCapital: number
    symbols: string[]
  }): Promise<ApiResponse<BacktestResult>> {
    const response = await apiClient.post(`/strategies/${strategyId}/backtest`, params)
    return response.data
  },

  async toggleStrategy(id: number, active: boolean): Promise<ApiResponse<Strategy>> {
    const response = await apiClient.post(`/strategies/${id}/toggle`, { active })
    return response.data
  }
}
