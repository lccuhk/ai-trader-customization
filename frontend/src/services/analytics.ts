import { apiClient } from './api'
import type { UserAnalytics, PlatformAnalytics, FunnelAnalysis, RetentionAnalysis, ABTest, AdminStats, ApiResponse, PaginatedResponse } from '../types'

export const analyticsService = {
  async trackEvent(data: {
    event_type: string
    event_name: string
    properties?: Record<string, any>
    session_id?: string
  }): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post('/analytics/track', data)
    return response.data
  },

  async getUserAnalytics(params?: {
    start_date?: string
    end_date?: string
    days?: number
  }): Promise<ApiResponse<UserAnalytics>> {
    const response = await apiClient.get('/analytics/user', { params })
    return response.data
  },

  async getABVariant(featureName: string): Promise<ApiResponse<{ variant: string; test_id?: number; test_name?: string }>> {
    const response = await apiClient.get('/analytics/ab/variant', { params: { feature_name: featureName } })
    return response.data
  },

  async trackABConversion(data: {
    test_id: number
    variant: string
    conversion_type: string
  }): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post('/analytics/ab/conversion', data)
    return response.data
  },

  async getPlatformAnalytics(params?: { days?: number }): Promise<ApiResponse<PlatformAnalytics>> {
    const response = await apiClient.get('/admin/analytics/platform', { params })
    return response.data
  },

  async getFunnelAnalysis(params?: { funnel?: string; days?: number }): Promise<ApiResponse<FunnelAnalysis>> {
    const response = await apiClient.get('/admin/analytics/funnel', { params })
    return response.data
  },

  async getRetentionAnalysis(params?: { days?: number; cohort_days?: number }): Promise<ApiResponse<RetentionAnalysis>> {
    const response = await apiClient.get('/admin/analytics/retention', { params })
    return response.data
  },

  async getAdminStats(): Promise<ApiResponse<AdminStats>> {
    const response = await apiClient.get('/admin/stats')
    return response.data
  },

  async getABTests(params?: { is_active?: boolean; page?: number; per_page?: number }): Promise<ApiResponse<PaginatedResponse<ABTest>>> {
    const response = await apiClient.get('/admin/ab-tests', { params })
    return response.data
  },

  async createABTest(data: {
    name: string
    feature_name: string
    variants: string[]
    traffic_split: Record<string, number>
  }): Promise<ApiResponse<ABTest>> {
    const response = await apiClient.post('/admin/ab-tests', data)
    return response.data
  }
}
