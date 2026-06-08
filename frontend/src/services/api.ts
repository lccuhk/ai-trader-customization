import axios, { AxiosInstance, AxiosResponse } from 'axios'
import type {
  User,
  AuthResponse,
  Signal,
  SignalReply,
  SignalParticipant,
  SignalQuality,
  Notification,
  Strategy,
  MarketNews,
  MarketEvent,
  EconomicIndicator,
  ApiResponse,
  LoginRequest,
  RegisterRequest,
  CreateSignalRequest,
  CreateReplyRequest
} from '@/types'

const API_BASE_URL = '/api'

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (data: LoginRequest): Promise<AxiosResponse<AuthResponse>> =>
    api.post('/auth/login', data),

  register: (data: RegisterRequest): Promise<AxiosResponse<AuthResponse>> =>
    api.post('/auth/register', data),

  getCurrentUser: (): Promise<AxiosResponse<ApiResponse<User>>> =>
    api.get('/auth/me')
}

export const signalApi = {
  getSignals: (limit = 20, message_type = '', market = ''): Promise<AxiosResponse<ApiResponse<Signal[]>>> =>
    api.get('/signals/feed', { params: { limit, message_type, market } }),

  getSignalDetail: (id: number): Promise<AxiosResponse<ApiResponse<Signal>>> =>
    api.get(`/signals/${id}`),

  getSignalReplies: (id: number): Promise<AxiosResponse<ApiResponse<SignalReply[]>>> =>
    api.get(`/signals/${id}/replies`),

  getSignalParticipants: (id: number): Promise<AxiosResponse<ApiResponse<SignalParticipant[]>>> =>
    api.get(`/signals/${id}/participants`),

  getSignalQuality: (id: number): Promise<AxiosResponse<ApiResponse<SignalQuality>>> =>
    api.get(`/signals/${id}/quality-detail`),

  createSignal: (data: CreateSignalRequest): Promise<AxiosResponse<ApiResponse<Signal>>> =>
    api.post('/signals', data),

  addReply: (signalId: number, data: CreateReplyRequest): Promise<AxiosResponse<ApiResponse<SignalReply>>> =>
    api.post(`/signals/${signalId}/replies`, data),

  getFollowStatus: (id: number): Promise<AxiosResponse<ApiResponse>> =>
    api.get(`/signals/${id}/follow`),

  toggleFollow: (id: number): Promise<AxiosResponse<ApiResponse>> =>
    api.post(`/signals/${id}/follow`),

  likeSignal: (id: number): Promise<AxiosResponse<ApiResponse>> =>
    api.post(`/signals/${id}/like`),

  likeReply: (signalId: number, replyId: number): Promise<AxiosResponse<ApiResponse>> =>
    api.post(`/signals/${signalId}/replies/${replyId}/like`)
}

export const notificationApi = {
  getNotifications: (limit = 20): Promise<AxiosResponse<ApiResponse<Notification[]>>> =>
    api.get('/notifications', { params: { limit } }),

  markAsRead: (id: number): Promise<AxiosResponse<ApiResponse>> =>
    api.put(`/notifications/${id}/read`),

  markAllAsRead: (): Promise<AxiosResponse<ApiResponse>> =>
    api.put('/notifications/read-all')
}

export const marketApi = {
  getNews: (limit = 10, category = ''): Promise<AxiosResponse<ApiResponse<MarketNews[]>>> =>
    api.get('/market/news', { params: { limit, category } }),

  getNewsDetail: (id: number): Promise<AxiosResponse<ApiResponse<MarketNews>>> =>
    api.get(`/market/news/${id}`),

  getEvents: (limit = 20): Promise<AxiosResponse<ApiResponse<MarketEvent[]>>> =>
    api.get('/market/events', { params: { limit } }),

  getIndicators: (limit = 20): Promise<AxiosResponse<ApiResponse<EconomicIndicator[]>>> =>
    api.get('/market/indicators', { params: { limit } }),

  getStrategies: (): Promise<AxiosResponse<ApiResponse<Strategy[]>>> =>
    api.get('/strategies'),

  getStrategyDetail: (id: number): Promise<AxiosResponse<ApiResponse<Strategy>>> =>
    api.get(`/strategies/${id}`),

  createStrategy: (data: Partial<Strategy>): Promise<AxiosResponse<ApiResponse>> =>
    api.post('/strategies', data)
}

export const apiClient = api
export default api
