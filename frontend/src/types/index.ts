export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  display_name: string
  password: string
}

export interface CreateSignalRequest {
  title: string
  content: string
  message_type: string
  symbols: string[]
  market?: string
  direction?: string
  entry_price?: number
  stop_loss?: number
  take_profit?: number
}

export interface CreateReplyRequest {
  content: string
  parent_id?: number
}

export interface User {
  id: number
  username: string
  email: string
  display_name: string
  avatar_url?: string
  bio?: string
  location?: string
  website?: string
  role?: string
  is_verified?: boolean
  is_active?: boolean
  follower_count?: number
  following_count?: number
  last_login_at?: string
  created_at?: string
  updated_at?: string
}

export interface UserProfile extends User {
  signal_count?: number
  total_trades?: number
  win_rate?: number
  total_pnl?: number
  is_following?: boolean
}

export interface AuthResponse {
  success: boolean
  token?: string
  refresh_token?: string
  user?: User
  message?: string
}

export interface Signal {
  id: number
  user_id?: number
  agent_name: string
  title: string
  content: string
  message_type: 'operation' | 'analysis' | 'discussion' | 'long' | 'short' | 'info' | 'alert'
  market: string
  symbols: string[]
  direction?: 'long' | 'short'
  entry_price?: number
  take_profit?: number
  stop_loss?: number
  current_price?: number
  pnl?: number
  pnl_percent?: number
  status?: string
  quality_score: number
  reply_count: number
  participant_count: number
  likes: number
  views: number
  is_following: boolean
  is_liked: boolean
  is_public?: boolean
  is_simulation?: boolean
  moderation_status?: string
  position_size?: number
  created_at: string
}

export interface SignalReply {
  id: number
  signal_id: number
  user_id?: number
  user_name: string
  content: string
  parent_id?: number
  likes: number
  is_liked: boolean
  created_at: string
}

export interface SignalParticipant {
  id: number
  signal_id: number
  user_id?: number
  user_name: string
  role: 'author' | 'follower' | 'commenter'
  joined_at: string
}

export interface SignalQuality {
  accuracy_score: number
  analysis_depth: number
  risk_management: number
  timeliness: number
  clarity: number
  total_score: number
}

export interface Notification {
  id: number
  user_id: number
  title?: string
  message?: string
  content?: string
  notification_type: 'price_alert' | 'signal' | 'risk' | 'system' | 'comment' | 'like' | 'follow' | 'alert' | 'news' | 'new_follower' | 'new_message' | 'mention' | 'signal_moderation'
  type?: string
  priority: 'low' | 'normal' | 'high'
  is_read: boolean
  read?: boolean
  related_url?: string
  data?: Record<string, any>
  created_at: string
}

export interface Strategy {
  id: number
  user_id?: number
  name: string
  description: string
  strategy_type: string
  code: string
  parameters: Record<string, any>
  is_active: boolean
  created_at: string
}

export interface MarketNews {
  id: number
  title: string
  content: string
  summary?: string
  source: string
  category: string
  symbol: string
  symbols?: string[]
  impact_score: number
  sentiment: 'bullish' | 'bearish' | 'neutral'
  url?: string
  published_at?: string
  created_at: string
}

export interface Order {
  id: number
  user_id: number
  exchange_account_id?: number
  signal_id?: number
  symbol: string
  side: 'buy' | 'sell'
  type: 'market' | 'limit' | 'stop'
  quantity: number
  price?: number
  status: 'pending' | 'open' | 'filled' | 'cancelled' | 'failed'
  filled_price?: number
  filled_quantity?: number
  exchange_order_id?: string
  error_message?: string
  is_simulation: boolean
  created_at: string
  filled_at?: string
}

export interface Trade {
  id: number
  user_id: number
  order_id?: number
  signal_id?: number
  symbol: string
  side: 'buy' | 'sell'
  quantity: number
  price: number
  pnl?: number
  pnl_percent?: number
  is_simulation: boolean
  created_at: string
}

export interface Position {
  id: number
  user_id: number
  symbol: string
  quantity: number
  avg_price: number
  current_price?: number
  unrealized_pnl?: number
  unrealized_pnl_percent?: number
  is_simulation: boolean
  created_at: string
  updated_at?: string
}

export interface Portfolio {
  id: number
  user_id: number
  total_balance: number
  total_pnl: number
  unrealized_pnl: number
  total_value: number
  win_rate: number
  total_trades: number
  is_simulation: boolean
  created_at: string
  updated_at?: string
}

export interface PortfolioData {
  portfolio: Portfolio
  positions: Position[]
  recent_trades: Trade[]
}

export interface ExchangeAccount {
  id: number
  user_id: number
  exchange: string
  name: string
  is_sandbox: boolean
  is_active: boolean
  created_at: string
}

export interface UserFollow {
  id: number
  follower_id: number
  following_id: number
  created_at: string
}

export interface DirectMessage {
  id: number
  sender_id: number
  receiver_id: number
  content: string
  is_read: boolean
  sender?: User
  created_at: string
}

export interface Conversation {
  user: User
  last_message: {
    id: number
    content: string
    is_read: boolean
    is_sent: boolean
    created_at: string
  }
  unread_count: number
}

export interface Mention {
  id: number
  mentioned_user_id: number
  mentioning_user_id: number
  mentioning_user?: User
  signal_id?: number
  reply_id?: number
  is_read: boolean
  created_at: string
}

export interface AISignal {
  id: number
  user_id?: number
  symbol: string
  direction: 'long' | 'short'
  entry_price?: number
  take_profit?: number
  stop_loss?: number
  current_price?: number
  confidence: number
  reasoning?: string
  strategy?: string
  risk_level?: 'low' | 'medium' | 'high'
  status: 'active' | 'closed'
  pnl?: number
  pnl_percent?: number
  created_at: string
  closed_at?: string
}

export interface AIAnalysisItem {
  title: string
  description: string
  priority?: 'high' | 'medium' | 'low'
}

export interface AIAnalysis {
  id: number
  user_id: number
  analysis_type: string
  summary?: string
  strengths?: AIAnalysisItem[]
  weaknesses?: AIAnalysisItem[]
  recommendations?: AIAnalysisItem[]
  suggestions?: AIAnalysisItem[]
  risk_score?: number
  performance_metrics?: Record<string, any>
  performance?: {
    total_trades?: number
    win_rate?: number
    profit_loss_ratio?: number
    sharpe_ratio?: number
    total_pnl?: number
    total_pnl_percent?: number
    [key: string]: any
  }
  behavior?: {
    trading_frequency?: string
    risk_tolerance?: string
    preferred_assets?: string[]
    holding_period?: string
    [key: string]: any
  }
  risk?: {
    current_exposure?: number
    max_drawdown?: number
    var_95?: number
    var_99?: number
    concentration_risk?: number
    [key: string]: any
  }
  win_rate?: number
  profit_loss_ratio?: number
  sharpe_ratio?: number
  created_at: string
}

export interface AIRiskAlert {
  id: number
  user_id: number
  severity: 'low' | 'medium' | 'high'
  title?: string
  message?: string
  suggested_action?: string
  is_acknowledged: boolean
  created_at: string
}

export interface AIStrategy {
  id: number
  user_id: number
  name?: string
  description?: string
  strategy_type: string
  strategy_code?: string
  parameters?: Record<string, any>
  risk_level?: string
  target_symbols?: string[]
  symbol?: string
  is_active: boolean
  status?: 'active' | 'inactive' | 'testing' | 'deployed'
  backtest_results?: Record<string, any>
  backtest_result?: {
    total_return?: number
    sharpe_ratio?: number
    max_drawdown?: number
    win_rate?: number
    profit_factor?: number
    total_trades?: number
    [key: string]: any
  }
  expected_return?: number
  max_drawdown?: number
  win_rate?: number
  created_at: string
  last_backtest_at?: string
}

export interface TwoFactorAuth {
  enabled: boolean
  method?: string
}

export interface SecuritySettings {
  two_factor: TwoFactorAuth
  oauth_accounts: OAuthAccount[]
  password_last_changed?: string
}

export interface OAuthAccount {
  id: number
  provider: string
  created_at: string
}

export interface AuditLog {
  id: number
  user_id?: number
  action: string
  resource_type?: string
  resource_id?: number
  old_values?: Record<string, any>
  new_values?: Record<string, any>
  ip_address?: string
  created_at: string
}

export interface AnalyticsEvent {
  event_type: string
  event_name: string
  properties?: Record<string, any>
  session_id?: string
}

export interface UserAnalytics {
  period: {
    start_date: string
    end_date: string
    days: number
  }
  daily_stats: Array<{
    date: string
    trades: number
    pnl: number
    volume: number
  }>
  performance: {
    total_trades: number
    winning_trades: number
    losing_trades: number
    win_rate: number
    total_pnl: number
    avg_win: number
    avg_loss: number
    profit_factor: number
    best_trade: number
    worst_trade: number
    sharpe_ratio: number
    max_drawdown: number
  }
  behavior: {
    total_events: number
    events_by_type: Record<string, number>
    signals_created: number
    avg_time_between_trades_seconds: number
    symbols_traded: string[]
    most_traded_symbol?: string
    session_count: number
  }
}

export interface PlatformAnalytics {
  period: { days: number }
  users: {
    total: number
    active: number
    new: number
    growth_rate: number
  }
  signals: {
    total: number
    active: number
    new: number
  }
  trading: {
    total_trades: number
    new_trades: number
    total_volume: number
    total_pnl: number
  }
  leaderboards: {
    top_traders: Array<{
      id: number
      username: string
      display_name: string
      total_pnl: number
    }>
    top_signals: Array<{
      id: number
      title: string
      symbols: string[]
      pnl: number
      pnl_percent: number
      author_username: string
      author_display_name: string
    }>
  }
}

export interface ABTest {
  id: number
  name: string
  feature_name: string
  variants: string[]
  traffic_split: Record<string, number>
  is_active: boolean
  results?: Record<string, any>
  created_at: string
  started_at?: string
  ended_at?: string
}

export interface FunnelAnalysis {
  funnel: string
  period: { days: number }
  steps: Array<{
    name: string
    count: number
    conversion: number
  }>
}

export interface RetentionAnalysis {
  period: { days: number }
  cohorts: Array<{
    cohort: string
    size: number
    retention: Array<{
      week: number
      active_users: number
      rate: number
    }>
  }>
}

export interface AdminStats {
  overview: {
    total_users: number
    total_signals: number
    total_trades: number
    total_orders: number
  }
  today: {
    new_users: number
    new_signals: number
    new_trades: number
  }
  moderation: {
    pending_count: number
  }
  recent_actions: AdminAction[]
}

export interface AdminAction {
  id: number
  action: string
  admin?: {
    id: number
    username: string
    display_name: string
  }
  target_user_id?: number
  reason?: string
  details?: Record<string, any>
  created_at: string
}

export interface PriceUpdate {
  symbol: string
  price: number
  change_24h: number
}

export interface OnlineUser {
  id: number
  username: string
  display_name: string
}

export interface WSNewSignalData {
  type: string
  data: Signal
}

export interface WSNewCommentData {
  type: string
  signal_id: number
  data: SignalReply
}

export interface WSPriceUpdateData {
  type: string
  data: PriceUpdate
}

export interface WSPnLUpdateData {
  type: string
  signal_id: number
  pnl: number
  pnl_percent: number
}

export interface WSNotificationData {
  type: string
  data: Notification
}

export interface WSOrderUpdateData {
  type: string
  data: Order
}

export interface WSTradeUpdateData {
  type: string
  data: Trade
}

export interface WSPositionUpdateData {
  type: string
  data: Position
}

export interface WSPortfolioUpdateData {
  type: string
  data: Portfolio
}

export interface WSMessageData {
  type: string
  data: DirectMessage
}

export interface WSMentionData {
  type: string
  data: Mention
}

export interface WSAIAlertData {
  type: string
  data: AIRiskAlert
}

export interface WSAISignalData {
  type: string
  data: AISignal
}

export interface ApiResponse<T = any> {
  success: boolean
  code?: number
  message?: string
  data?: T
  signal?: T
  signals?: T[]
  reply?: T
  replies?: T[]
  participant?: T
  participants?: T[]
  quality?: T
  news?: T[]
  events?: T[]
  indicators?: T[]
  token?: string
  user?: User
  is_following?: boolean
  likes?: number
  [key: string]: any
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
}

// Missing types from old architecture
export interface MarketEvent {
  id: number
  title: string
  description: string
  event_type: string
  symbol: string
  impact: 'low' | 'medium' | 'high'
  event_date: string
  created_at: string
}

export interface EconomicIndicator {
  id: number
  name: string
  value: number
  previous_value?: number
  forecast_value?: number
  unit: string
  country: string
  release_date: string
  impact: 'low' | 'medium' | 'high'
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  display_name?: string
}

export interface CreateSignalRequest {
  title: string
  content: string
  message_type: string
  market: string
  symbols: string[]
  direction?: 'long' | 'short'
  entry_price?: number
  take_profit?: number
  stop_loss?: number
  is_public?: boolean
  is_simulation?: boolean
}

export interface CreateReplyRequest {
  content: string
  parent_id?: number
}

export interface PnLUpdate {
  signal_id: number
  pnl: number
  pnl_percent: number
}

// Additional WebSocket types
export interface WSNewNotificationData {
  type: string
  data: Notification
}

export interface WSSignalUpdateData {
  type: string
  signal_id: number
  data: Partial<Signal>
}

export interface WSLikeUpdateData {
  type: string
  signal_id: number
  reply_id?: number
  likes: number
  is_liked: boolean
}

export interface WSFollowUpdateData {
  type: string
  signal_id: number
  is_following: boolean
  follower_count: number
  participant_count: number
}

export interface WSOnlineUsersData {
  type: string
  data: OnlineUser[]
  count?: number
}

export interface WSUserStatusData {
  type: string
  user_id: number
  status: 'online' | 'offline'
}

export interface WSSystemMessage {
  type: string
  message: string
  level: 'info' | 'warning' | 'error'
}

export interface WSTypingData {
  type: string
  signal_id: number
  user_id: number
  username: string
  user: {
    user_id: number
    username: string
    display_name: string
  }
}

export interface WSTypingStopData {
  type: string
  signal_id: number
  user_id: number
}

export interface WSConnectionStatus {
  type: string
  connected: boolean
  reconnecting?: boolean
}

export interface WSErrorData {
  type: string
  error: string
  message: string
  code?: number
}

// Quick settings type
export interface QuickSettings {
  theme: 'dark' | 'light'
  notifications: boolean
  sound: boolean
  autoRefresh: boolean
  refreshInterval: number
  compactMode: boolean
  showMarketNews: boolean
  language: string
}
