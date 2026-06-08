import { apiClient } from './api'
import type { UserProfile, User, DirectMessage, Conversation, Mention, ApiResponse, PaginatedResponse } from '../types'

export const socialService = {
  async followUser(userId: number): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post(`/social/follow/${userId}`)
    return response.data
  },

  async unfollowUser(userId: number): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post(`/social/unfollow/${userId}`)
    return response.data
  },

  async getFollowers(userId: number, params?: { page?: number; per_page?: number }): Promise<ApiResponse<PaginatedResponse<User>>> {
    const response = await apiClient.get(`/social/followers/${userId}`, { params })
    return response.data
  },

  async getFollowing(userId: number, params?: { page?: number; per_page?: number }): Promise<ApiResponse<PaginatedResponse<User>>> {
    const response = await apiClient.get(`/social/following/${userId}`, { params })
    return response.data
  },

  async getUserProfile(userId: number): Promise<ApiResponse<{ user: UserProfile; signals: any[]; is_following: boolean }>> {
    const response = await apiClient.get(`/social/profile/${userId}`)
    return response.data
  },

  async sendDirectMessage(data: { receiver_id: number; content: string }): Promise<ApiResponse<DirectMessage>> {
    const response = await apiClient.post('/social/messages', data)
    return response.data
  },

  async getDirectMessages(otherUserId: number, params?: { page?: number; per_page?: number }): Promise<ApiResponse<PaginatedResponse<DirectMessage>>> {
    const response = await apiClient.get(`/social/messages/${otherUserId}`, { params })
    return response.data
  },

  async getConversations(): Promise<ApiResponse<Conversation[]>> {
    const response = await apiClient.get('/social/conversations')
    return response.data
  },

  async getMentions(params?: { page?: number; per_page?: number }): Promise<ApiResponse<PaginatedResponse<Mention>>> {
    const response = await apiClient.get('/social/mentions', { params })
    return response.data
  },

  async shareSignal(signalId: number, platform: string = 'link'): Promise<ApiResponse<{ url: string; title: string; content: string; platform: string }>> {
    const response = await apiClient.post(`/social/share/${signalId}`, { platform })
    return response.data
  },

  async searchUsers(query: string, params?: { page?: number; per_page?: number }): Promise<ApiResponse<PaginatedResponse<User>>> {
    const response = await apiClient.get('/social/users/search', { params: { q: query, ...params } })
    return response.data
  }
}
