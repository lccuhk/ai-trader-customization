import { apiClient } from './api'
import type { ApiResponse } from '../types'

export interface RiskMetric {
  id: string
  label: string
  value: string
  unit: string
  status: 'safe' | 'warning' | 'danger'
}

export interface RiskAlert {
  id: number
  name: string
  severity: 'low' | 'medium' | 'high' | 'danger'
  status: 'active' | 'paused' | 'triggered'
  condition: string
  symbol: string
  threshold: number
  currentValue: number
  createdAt: string
  lastTriggered: string | null
}

export interface RiskSettings {
  maxDailyLoss: number
  maxPositionSize: number
  maxConcentration: number
  riskTolerance: 'conservative' | 'moderate' | 'aggressive'
  defaultStopLoss: number
  defaultTakeProfit: number
  trailingStop: boolean
  autoStopLoss: boolean
  positionSizing: boolean
  emailAlerts: boolean
  pushAlerts: boolean
  soundAlerts: boolean
}

export const riskService = {
  async getDashboard(): Promise<ApiResponse<{
    metrics: RiskMetric[]
    exposure: { symbol: string; percentage: number; value: number }[]
    activeAlerts: number
    triggeredToday: number
    riskScore: number
  }>> {
    const response = await apiClient.get('/risk/dashboard')
    return response.data
  },

  async getAlerts(params?: {
    status?: string
    severity?: string
    symbol?: string
  }): Promise<ApiResponse<RiskAlert[]>> {
    const response = await apiClient.get('/risk/alerts', { params })
    return response.data
  },

  async createAlert(data: Omit<RiskAlert, 'id' | 'createdAt' | 'lastTriggered'>): Promise<ApiResponse<RiskAlert>> {
    const response = await apiClient.post('/risk/alerts', data)
    return response.data
  },

  async updateAlert(id: number, data: Partial<RiskAlert>): Promise<ApiResponse<RiskAlert>> {
    const response = await apiClient.put(`/risk/alerts/${id}`, data)
    return response.data
  },

  async deleteAlert(id: number): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.delete(`/risk/alerts/${id}`)
    return response.data
  },

  async getSettings(): Promise<ApiResponse<RiskSettings>> {
    const response = await apiClient.get('/risk/settings')
    return response.data
  },

  async updateSettings(data: Partial<RiskSettings>): Promise<ApiResponse<RiskSettings>> {
    const response = await apiClient.put('/risk/settings', data)
    return response.data
  },

  async calculatePositionSize(data: {
    accountSize: number
    riskPercent: number
    entryPrice: number
    stopLossPrice: number
  }): Promise<ApiResponse<{
    positionSize: number
    positionValue: number
    riskAmount: number
    shares: number
  }>> {
    const response = await apiClient.post('/risk/calculate-position-size', data)
    return response.data
  }
}
