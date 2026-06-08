import { apiClient } from './api'
import type { SecuritySettings, AuditLog, ApiResponse, PaginatedResponse } from '../types'

export const securityService = {
  async setup2FA(method: string = 'totp'): Promise<ApiResponse<{
    secret: string
    provisioning_uri: string
    qr_code: string
    backup_codes: string[]
    method: string
  }>> {
    const response = await apiClient.post('/security/2fa/setup', { method })
    return response.data
  },

  async verify2FA(code: string): Promise<ApiResponse<{ verified: boolean; method: string }>> {
    const response = await apiClient.post('/security/2fa/verify', { code })
    return response.data
  },

  async disable2FA(code: string): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post('/security/2fa/disable', { code })
    return response.data
  },

  async get2FAStatus(): Promise<ApiResponse<{ enabled: boolean; method?: string }>> {
    const response = await apiClient.get('/security/2fa/status')
    return response.data
  },

  async oauthLogin(provider: string, code: string, redirectUri: string): Promise<ApiResponse<{
    access_token: string
    refresh_token: string
    user: any
  }>> {
    const response = await apiClient.post(`/security/oauth/${provider}`, { code, redirect_uri: redirectUri })
    return response.data
  },

  async getAuditLogs(params?: {
    action?: string
    resource_type?: string
    start_date?: string
    end_date?: string
    page?: number
    per_page?: number
  }): Promise<ApiResponse<PaginatedResponse<AuditLog>>> {
    const response = await apiClient.get('/security/audit-logs', { params })
    return response.data
  },

  async getSecuritySettings(): Promise<ApiResponse<SecuritySettings>> {
    const response = await apiClient.get('/security/settings')
    return response.data
  },

  async validatePassword(password: string): Promise<ApiResponse<{ valid: boolean; errors: string[] }>> {
    const response = await apiClient.post('/security/password/validate', { password })
    return response.data
  }
}
