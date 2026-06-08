import { apiClient } from './api'
import type { ApiResponse } from '../types'

export interface MarketNews {
  id: number
  source: string
  importance: 'low' | 'medium' | 'high'
  category: string
  title: string
  summary: string
  tags: string[]
  time: string
  url: string
}

export interface MarketEvent {
  id: number
  date: string
  time: string
  importance: 'low' | 'medium' | 'high'
  category: string
  title: string
  expected: string
  actual: string | null
  isOngoing: boolean
}

export interface EconomicIndicator {
  id: number
  name: string
  country: string
  value: string
  unit: string
  change: number
  trend: 'up' | 'down' | 'stable'
  nextRelease: string
}

export interface MarketSentiment {
  value: number
  label: string
  change24h: number
  byAsset: { symbol: string; sentiment: number; label: string }[]
  topTopics: { topic: string; count: number; sentiment: number }[]
}

export interface MarketTicker {
  id: number
  symbol: string
  name: string
  price: number
  change24h: number
  changePercent: number
  marketCap: number
  volume: number
  high24h: number
  low24h: number
}

export const marketService = {
  async getNews(params?: {
    category?: string
    importance?: string
    limit?: number
  }): Promise<ApiResponse<MarketNews[]>> {
    const response = await apiClient.get('/market/news', { params })
    return response.data
  },

  async getEvents(params?: {
    startDate?: string
    endDate?: string
    importance?: string
  }): Promise<ApiResponse<MarketEvent[]>> {
    const response = await apiClient.get('/market/events', { params })
    return response.data
  },

  async getIndicators(params?: {
    country?: string
    type?: string
  }): Promise<ApiResponse<EconomicIndicator[]>> {
    const response = await apiClient.get('/market/indicators', { params })
    return response.data
  },

  async getSentiment(): Promise<ApiResponse<MarketSentiment>> {
    const response = await apiClient.get('/market/sentiment')
    return response.data
  },

  async getTrending(params?: {
    type?: 'gainers' | 'losers' | 'volume'
    limit?: number
  }): Promise<ApiResponse<MarketTicker[]>> {
    const response = await apiClient.get('/market/trending', { params })
    return response.data
  },

  async getMarketData(params?: {
    symbols?: string[]
  }): Promise<ApiResponse<MarketTicker[]>> {
    const response = await apiClient.get('/market/data', { params })
    return response.data
  },

  async getPrice(symbol: string): Promise<ApiResponse<{ symbol: string; price: number; timestamp: string }>> {
    const response = await apiClient.get(`/market/price/${symbol}`)
    return response.data
  }
}
