import { apiClient } from './api'
import type { Order, Trade, Position, PortfolioData, ExchangeAccount, ApiResponse, PaginatedResponse } from '../types'

export const tradingService = {
  async createOrder(data: {
    symbol: string
    side: 'buy' | 'sell'
    type: 'market' | 'limit' | 'stop'
    quantity: number
    price?: number
    is_simulation?: boolean
    signal_id?: number
    exchange_account_id?: number
  }): Promise<ApiResponse<Order>> {
    const response = await apiClient.post('/trading/orders', data)
    return response.data
  },

  async cancelOrder(orderId: number): Promise<ApiResponse<Order>> {
    const response = await apiClient.post(`/trading/orders/${orderId}/cancel`)
    return response.data
  },

  async getOrders(params?: {
    status?: string
    symbol?: string
    is_simulation?: boolean
    page?: number
    per_page?: number
  }): Promise<ApiResponse<PaginatedResponse<Order>>> {
    const response = await apiClient.get('/trading/orders', { params })
    return response.data
  },

  async getOrderDetail(orderId: number): Promise<ApiResponse<Order>> {
    const response = await apiClient.get(`/trading/orders/${orderId}`)
    return response.data
  },

  async getPositions(params?: {
    symbol?: string
    is_simulation?: boolean
  }): Promise<ApiResponse<Position[]>> {
    const response = await apiClient.get('/trading/positions', { params })
    return response.data
  },

  async getTrades(params?: {
    symbol?: string
    is_simulation?: boolean
    start_date?: string
    end_date?: string
    page?: number
    per_page?: number
  }): Promise<ApiResponse<PaginatedResponse<Trade>>> {
    const response = await apiClient.get('/trading/trades', { params })
    return response.data
  },

  async getPortfolio(is_simulation: boolean = true): Promise<ApiResponse<PortfolioData>> {
    const response = await apiClient.get('/trading/portfolio', { params: { is_simulation } })
    return response.data
  },

  async getExchangeAccounts(): Promise<ApiResponse<ExchangeAccount[]>> {
    const response = await apiClient.get('/trading/exchange-accounts')
    return response.data
  },

  async createExchangeAccount(data: {
    exchange: string
    api_key: string
    api_secret: string
    passphrase?: string
    is_sandbox?: boolean
    name?: string
  }): Promise<ApiResponse<ExchangeAccount>> {
    const response = await apiClient.post('/trading/exchange-accounts', data)
    return response.data
  },

  async deleteExchangeAccount(accountId: number): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.delete(`/trading/exchange-accounts/${accountId}`)
    return response.data
  },

  async getMarketPrice(symbol: string): Promise<ApiResponse<{ symbol: string; price: number }>> {
    const response = await apiClient.get(`/trading/market/price/${symbol}`)
    return response.data
  },

  async getAllMarketPrices(): Promise<ApiResponse<Record<string, number>>> {
    const response = await apiClient.get('/trading/market/prices')
    return response.data
  }
}
