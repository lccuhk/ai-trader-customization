import { apiClient } from './api'
import type { ApiResponse, AdminStats, User, AdminAction, FunnelAnalysis, RetentionAnalysis } from '../types'

export const adminService = {
  getStats: async (): Promise<ApiResponse<AdminStats>> => {
    const response = await apiClient.get('/api/admin/stats')
    return response.data
  },

  getUsers: async (params: any): Promise<ApiResponse<User[]>> => {
    const response = await apiClient.get('/api/admin/users', { params })
    return response.data
  },

  updateUser: async (userId: number, data: any): Promise<ApiResponse<User>> => {
    const response = await apiClient.put(`/api/admin/users/${userId}`, data)
    return response.data
  },

  banUser: async (userId: number): Promise<ApiResponse<void>> => {
    const response = await apiClient.post(`/api/admin/users/${userId}/ban`)
    return response.data
  },

  unbanUser: async (userId: number): Promise<ApiResponse<void>> => {
    const response = await apiClient.post(`/api/admin/users/${userId}/unban`)
    return response.data
  },

  getPendingModeration: async (): Promise<ApiResponse<any[]>> => {
    const response = await apiClient.get('/api/admin/moderation/pending')
    return response.data
  },

  moderateSignal: async (signalId: number, data: { action: string; reason?: string }): Promise<ApiResponse<void>> => {
    const response = await apiClient.post(`/api/admin/moderation/signals/${signalId}`, data)
    return response.data
  },

  getRecentActions: async (): Promise<ApiResponse<AdminAction[]>> => {
    const response = await apiClient.get('/api/admin/actions')
    return response.data
  },

  getFunnelAnalysis: async (params: any): Promise<ApiResponse<FunnelAnalysis[]>> => {
    const response = await apiClient.get('/api/admin/analytics/funnel', { params })
    return response.data
  },

  getRetentionAnalysis: async (params: any): Promise<ApiResponse<RetentionAnalysis[]>> => {
    const response = await apiClient.get('/api/admin/analytics/retention', { params })
    return response.data
  },

  getPlatformAnalytics: async (params: any): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/api/admin/analytics/platform', { params })
    return response.data
  },

  updateSettings: async (settings: any): Promise<ApiResponse<any>> => {
    const response = await apiClient.put('/api/admin/settings', settings)
    return response.data
  },

  sendSystemNotification: async (data: { message: string; user_ids?: number[] }): Promise<ApiResponse<void>> => {
    const response = await apiClient.post('/api/admin/notifications', data)
    return response.data
  },

  runHealthCheck: async (): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/api/health')
    return response.data
  }
}
