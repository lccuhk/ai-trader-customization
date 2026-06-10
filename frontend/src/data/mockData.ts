// ======================== Mock Data for Dashboard ========================

export const userAssets = {
  totalValue: 12450.32,
  available: 8450.32,
  margin: 4000.00,
  unrealizedPnL: 342.15,
  currency: 'USD',
}

export const positions = [
  { symbol: 'BTC/USDT', side: 'long', size: 0.25, entryPrice: 65000, markPrice: 66200, pnl: 300, pnlPercent: 1.85 },
  { symbol: 'ETH/USDT', side: 'short', size: 2.5, entryPrice: 3200, markPrice: 3150, pnl: 125, pnlPercent: 1.56 },
  { symbol: 'SOL/USDT', side: 'long', size: 15, entryPrice: 145, markPrice: 148, pnl: 45, pnlPercent: 2.07 },
]

export const livePositions = [
  { symbol: 'BTC/USDT', side: 'long', size: 0.15, entryPrice: 65800, markPrice: 66200, pnl: 60, pnlPercent: 0.61 },
  { symbol: 'ETH/USDT', side: 'long', size: 1.5, entryPrice: 3120, markPrice: 3150, pnl: 45, pnlPercent: 0.96 },
  { symbol: 'SOL/USDT', side: 'short', size: 8, entryPrice: 150, markPrice: 148, pnl: 16, pnlPercent: 1.33 },
]

export const openOrders = [
  { id: 1, symbol: 'BTC/USDT', side: 'buy', type: 'limit', price: 64000, quantity: 0.1, status: 'open', is_simulation: true, created_at: '2026-06-08T10:30:00Z' },
  { id: 2, symbol: 'ETH/USDT', side: 'sell', type: 'limit', price: 3300, quantity: 1.0, status: 'open', is_simulation: true, created_at: '2026-06-08T09:15:00Z' },
  { id: 3, symbol: 'SOL/USDT', side: 'buy', type: 'market', price: 148, quantity: 5, status: 'filled', is_simulation: true, created_at: '2026-06-08T08:00:00Z' },
]

export const liveOpenOrders = [
  { id: 101, symbol: 'BTC/USDT', side: 'buy', type: 'limit', price: 65500, quantity: 0.05, status: 'open', is_simulation: false, created_at: '2026-06-10T08:30:00Z' },
  { id: 102, symbol: 'ETH/USDT', side: 'sell', type: 'limit', price: 3200, quantity: 0.8, status: 'open', is_simulation: false, created_at: '2026-06-10T07:45:00Z' },
  { id: 103, symbol: 'SOL/USDT', side: 'buy', type: 'market', price: 147, quantity: 3, status: 'filled', is_simulation: false, created_at: '2026-06-09T14:20:00Z' },
  { id: 104, symbol: 'XRP/USDT', side: 'sell', type: 'limit', price: 0.55, quantity: 200, status: 'open', is_simulation: false, created_at: '2026-06-09T11:00:00Z' },
]

// Strategy list shared across signals
export const strategyList = [
  { key: '动量突破', label: '动量突破' },
  { key: '均值回归', label: '均值回归' },
  { key: '趋势跟踪', label: '趋势跟踪' },
  { key: '网格交易', label: '网格交易' },
]

// Expanded signals with many-to-many: one asset appears under multiple strategies,
// and one strategy covers multiple assets. Each signal now includes a winRate.
export const signals = [
  // ——— 动量突破 ———
  { id: 1,  strategy: '动量突破', asset: 'BTC/USDT', direction: 'long',  confidence: 87, price: 66100, target: 67500, stopLoss: 65500, winRate: 72 },
  { id: 2,  strategy: '动量突破', asset: 'SOL/USDT', direction: 'long',  confidence: 81, price: 148,   target: 155,   stopLoss: 144,   winRate: 68 },
  { id: 3,  strategy: '动量突破', asset: 'AVAX/USDT', direction: 'long', confidence: 74, price: 38.5,  target: 42,    stopLoss: 36.8,  winRate: 65 },
  // ——— 均值回归 ———
  { id: 4,  strategy: '均值回归', asset: 'ETH/USDT', direction: 'short', confidence: 72, price: 3150,  target: 3080,  stopLoss: 3190,  winRate: 63 },
  { id: 5,  strategy: '均值回归', asset: 'XRP/USDT', direction: 'short', confidence: 68, price: 0.52,  target: 0.48,  stopLoss: 0.54,  winRate: 60 },
  { id: 6,  strategy: '均值回归', asset: 'DOT/USDT', direction: 'short', confidence: 65, price: 7.2,   target: 6.8,   stopLoss: 7.45,  winRate: 58 },
  // ——— 趋势跟踪 ———
  { id: 7,  strategy: '趋势跟踪', asset: 'SOL/USDT', direction: 'long',  confidence: 81, price: 148,   target: 158,   stopLoss: 142,   winRate: 76 },
  { id: 8,  strategy: '趋势跟踪', asset: 'BTC/USDT', direction: 'long',  confidence: 79, price: 66100, target: 68500, stopLoss: 65200, winRate: 74 },
  { id: 9,  strategy: '趋势跟踪', asset: 'LINK/USDT', direction: 'long', confidence: 73, price: 14.2,  target: 15.8,  stopLoss: 13.5,  winRate: 70 },
  // ——— 网格交易 ———
  { id: 10, strategy: '网格交易', asset: 'BNB/USDT', direction: 'long',  confidence: 65, price: 580,   target: 600,   stopLoss: 565,   winRate: 62 },
  { id: 11, strategy: '网格交易', asset: 'ETH/USDT', direction: 'long',  confidence: 62, price: 3150,  target: 3220,  stopLoss: 3100,  winRate: 60 },
  { id: 12, strategy: '网格交易', asset: 'MATIC/USDT', direction: 'long',confidence: 58, price: 0.72,  target: 0.78,  stopLoss: 0.69,  winRate: 55 },
]

export const quickInfo = {
  marketSentiment: { score: 62, level: 'greed', trend: 'up' },
  alerts: [
    { id: 1, type: 'warning' as const, messageKey: 'quickInfo.btcStopAlert' },
    { id: 2, type: 'info' as const, messageKey: 'quickInfo.ethProfitAlert' },
  ],
  aiOneLinerKey: 'quickInfo.volatilitySuggestion',
}

export const marketQuotes = [
  { symbol: 'BTC/USDT', price: 66200, change24h: 2.3, volume: '28.5B' },
  { symbol: 'ETH/USDT', price: 3150, change24h: -0.8, volume: '12.3B' },
  { symbol: 'SOL/USDT', price: 148, change24h: 5.2, volume: '3.1B' },
  { symbol: 'BNB/USDT', price: 580, change24h: 1.1, volume: '1.2B' },
  { symbol: 'XRP/USDT', price: 0.52, change24h: -0.3, volume: '0.8B' },
]

export const news = [
  { id: 1, title: '美联储维持利率不变，市场预期 9 月降息', time: '2小时前', importance: 'high' as const },
  { id: 2, title: 'BTC 巨鲸过去 24 小时增持 5000 枚', time: '5小时前', importance: 'medium' as const },
  { id: 3, title: '以太坊坎昆升级测试网即将上线', time: '8小时前', importance: 'medium' as const },
  { id: 4, title: 'SOL 突破 150 美元关口，24 小时涨幅超 5%', time: '12小时前', importance: 'low' as const },
]

export const events = [
  { date: '2026-06-12', event: '美国 CPI 数据发布', impact: 'high' as const },
  { date: '2026-06-15', event: '以太坊坎昆升级测试网', impact: 'medium' as const },
  { date: '2026-06-18', event: '美联储议息会议', impact: 'high' as const },
  { date: '2026-06-20', event: 'BTC 期货季度交割', impact: 'medium' as const },
]

export const economicIndicators = [
  { nameKey: 'market.dxy', value: '104.2', change: '-0.3%' },
  { nameKey: 'market.ust10y', value: '4.25%', change: '-0.05%' },
  { nameKey: 'market.sp500', value: '5420', change: '+0.8%' },
  { nameKey: 'market.gold', value: '2345', change: '+0.5%' },
]

export const gainersLosers = {
  gainers: [
    { symbol: 'SOL/USDT', change: 5.2 },
    { symbol: 'AVAX/USDT', change: 3.8 },
    { symbol: 'LINK/USDT', change: 2.9 },
  ],
  losers: [
    { symbol: 'MATIC/USDT', change: -2.1 },
    { symbol: 'DOT/USDT', change: -1.5 },
    { symbol: 'ATOM/USDT', change: -1.2 },
  ],
}

export const myStrategies = [
  { id: 1, name: '趋势跟踪 v1', type: '趋势跟踪', status: 'active' as const, lastReturn: 12.5, sharpe: 1.8 },
  { id: 2, name: '网格交易 ETH', type: '网格交易', status: 'paused' as const, lastReturn: 5.2, sharpe: 1.2 },
  { id: 3, name: '动量突破 BTC', type: '动量突破', status: 'active' as const, lastReturn: 18.3, sharpe: 2.1 },
]

export const strategyTemplates = [
  { id: 1, name: '动量突破模板', difficulty: '中级', marketType: '趋势市' },
  { id: 2, name: '均值回归模板', difficulty: '初级', marketType: '震荡市' },
  { id: 3, name: '网格交易模板', difficulty: '中级', marketType: '震荡市' },
  { id: 4, name: '统计套利模板', difficulty: '高级', marketType: '所有市场' },
]

// Portfolio overview (combined with risk center)
export const portfolioOverview = {
  totalBalance: 125000.00,
  totalValue: 128200.50,
  totalPnl: 3200.50,
  totalPnlPercent: 2.56,
  winRate: 65.4,
  totalTrades: 187,
  profitFactor: 1.82,
  dailyPnl: 342.15,
  weeklyPnl: 1250.80,
  monthlyPnl: 4200.30,
}

export const portfolioPositions = [
  { symbol: 'BTC/USDT', side: 'long', size: 0.25, entryPrice: 65000, markPrice: 66200, pnl: 300, pnlPercent: 1.85, unrealizedPnl: 300, margin: 1625.00, leverage: 10 },
  { symbol: 'ETH/USDT', side: 'short', size: 2.5, entryPrice: 3200, markPrice: 3150, pnl: 125, pnlPercent: 1.56, unrealizedPnl: 125, margin: 800.00, leverage: 5 },
  { symbol: 'SOL/USDT', side: 'long', size: 15, entryPrice: 145, markPrice: 148, pnl: 45, pnlPercent: 2.07, unrealizedPnl: 45, margin: 435.00, leverage: 3 },
]

export const portfolioHistory = [
  { date: '2026-06-01', value: 124500 },
  { date: '2026-06-02', value: 125200 },
  { date: '2026-06-03', value: 126100 },
  { date: '2026-06-04', value: 126800 },
  { date: '2026-06-05', value: 127400 },
  { date: '2026-06-06', value: 127900 },
  { date: '2026-06-07', value: 128200 },
]

// Live trading data (for 实盘 mode)
export const liveUserAssets = {
  totalValue: 52340.80,
  available: 48390.80,
  margin: 1950.00,
  unrealizedPnL: 123.50,
  currency: 'USD',
}

// Live trading data (for 实盘 mode in RiskCenter)
export const livePortfolioOverview = {
  totalBalance: 50000.00,
  totalValue: 52340.80,
  totalPnl: 2340.80,
  totalPnlPercent: 4.68,
  winRate: 58.2,
  totalTrades: 93,
  profitFactor: 1.45,
  dailyPnl: 185.50,
  weeklyPnl: 890.30,
  monthlyPnl: 2340.80,
}

export const livePortfolioPositions = [
  { symbol: 'BTC/USDT', side: 'long', size: 0.15, entryPrice: 65800, markPrice: 66200, pnl: 60, pnlPercent: 0.61, unrealizedPnl: 60, margin: 987.00, leverage: 5 },
  { symbol: 'ETH/USDT', side: 'long', size: 1.5, entryPrice: 3120, markPrice: 3150, pnl: 45, pnlPercent: 0.96, unrealizedPnl: 45, margin: 468.00, leverage: 3 },
  { symbol: 'SOL/USDT', side: 'short', size: 8, entryPrice: 150, markPrice: 148, pnl: 16, pnlPercent: 1.33, unrealizedPnl: 16, margin: 400.00, leverage: 2 },
  { symbol: 'BNB/USDT', side: 'long', size: 0.5, entryPrice: 575, markPrice: 580, pnl: 2.50, pnlPercent: 0.87, unrealizedPnl: 2.50, margin: 95.00, leverage: 3 },
]

export const livePortfolioHistory = [
  { date: '2026-06-01', value: 50000 },
  { date: '2026-06-02', value: 50150 },
  { date: '2026-06-03', value: 50480 },
  { date: '2026-06-04', value: 50800 },
  { date: '2026-06-05', value: 51120 },
  { date: '2026-06-06', value: 51500 },
  { date: '2026-06-07', value: 51850 },
  { date: '2026-06-08', value: 52010 },
  { date: '2026-06-09', value: 52180 },
  { date: '2026-06-10', value: 52340 },
]

export const liveRiskMetrics = {
  totalExposure: 1950.00,
  riskPerTrade: 1.8,
  currentDrawdown: 1.5,
  var95: 185.00,
}

export const liveRiskAlerts = [
  { id: 1, level: 'info' as const, messageKey: 'risk.alert.lowPosition', messageArgs: {} },
  { id: 2, level: 'warning' as const, messageKey: 'risk.alert.longProfit', messageArgs: { symbol: 'BTC', pnlPercent: '0.61' } },
]

// Technical indicators for market quotes
export const technicalIndicators: Record<string, {
  rsi: number;
  macd: { value: string; signal: string; histogram: string };
  ma20: number;
  ma50: number;
  bollinger: { upper: number; middle: number; lower: number };
  volume24h: string;
  high24h: number;
  low24h: number;
  marketCap: string;
  recommendation: string;
}> = {
  'BTC/USDT': {
    rsi: 62.5,
    macd: { value: '+320.5', signal: '+280.2', histogram: '+40.3' },
    ma20: 64800,
    ma50: 63500,
    bollinger: { upper: 68500, middle: 64800, lower: 61100 },
    volume24h: '28.5B',
    high24h: 66800,
    low24h: 64500,
    marketCap: '1.28T',
    recommendation: '买入',
  },
  'ETH/USDT': {
    rsi: 45.2,
    macd: { value: '-12.8', signal: '-8.5', histogram: '-4.3' },
    ma20: 3180,
    ma50: 3220,
    bollinger: { upper: 3350, middle: 3180, lower: 3010 },
    volume24h: '12.3B',
    high24h: 3220,
    low24h: 3120,
    marketCap: '378B',
    recommendation: '观望',
  },
  'SOL/USDT': {
    rsi: 72.8,
    macd: { value: '+5.2', signal: '+3.8', histogram: '+1.4' },
    ma20: 142,
    ma50: 135,
    bollinger: { upper: 158, middle: 142, lower: 126 },
    volume24h: '3.1B',
    high24h: 152,
    low24h: 140,
    marketCap: '62B',
    recommendation: '买入',
  },
  'BNB/USDT': {
    rsi: 55.0,
    macd: { value: '+2.1', signal: '+1.5', histogram: '+0.6' },
    ma20: 575,
    ma50: 568,
    bollinger: { upper: 610, middle: 575, lower: 540 },
    volume24h: '1.2B',
    high24h: 588,
    low24h: 572,
    marketCap: '89B',
    recommendation: '持有',
  },
  'XRP/USDT': {
    rsi: 48.3,
    macd: { value: '-0.01', signal: '-0.008', histogram: '-0.002' },
    ma20: 0.53,
    ma50: 0.54,
    bollinger: { upper: 0.58, middle: 0.53, lower: 0.48 },
    volume24h: '0.8B',
    high24h: 0.54,
    low24h: 0.51,
    marketCap: '28B',
    recommendation: '观望',
  },
}

// Shared risk settings (used by RiskCenter & TradingHub)
export const riskSettings = {
  stopLossPercent: 2.5,
  takeProfitPercent: 5.0,
  maxLeverage: 3,
  concentrationLimit: 30,
}

export const riskMetrics = {
  totalExposure: 8450.32,
  riskPerTrade: 2.5,
  currentDrawdown: 3.2,
  var95: 425.00,
}

export const riskAlerts = [
  { id: 1, level: 'warning' as const, messageKey: 'risk.alert.concentration', messageArgs: { symbol: 'BTC', current: 45, limit: 30 } },
  { id: 2, level: 'info' as const, messageKey: 'risk.alert.dailyPnl', messageArgs: { value: '+$342.15' } },
  { id: 3, level: 'danger' as const, messageKey: 'risk.alert.stopLossClose', messageArgs: { symbol: 'SOL', stopLoss: 144, current: 148 } },
]

// Simulated trading results for Strategy Center (paper trading dashboard)
export const simulatedOverview = {
  totalReturn: 8.42,
  winRate: 62.3,
  totalTrades: 45,
  profitFactor: 1.65,
  maxDrawdown: 4.2,
  sharpe: 1.35,
  startBalance: 10000,
  currentBalance: 10842,
  monthlyReturn: 3.2,
  avgTradeReturn: 1.87,
}

export const simulatedEquityCurve = [
  { date: '2026-06-01', value: 10000 },
  { date: '2026-06-02', value: 10050 },
  { date: '2026-06-03', value: 9980 },
  { date: '2026-06-04', value: 10120 },
  { date: '2026-06-05', value: 10250 },
  { date: '2026-06-06', value: 10380 },
  { date: '2026-06-07', value: 10500 },
  { date: '2026-06-08', value: 10620 },
  { date: '2026-06-09', value: 10750 },
  { date: '2026-06-10', value: 10842 },
]

export const simulatedTrades = [
  { id: 1, symbol: 'BTC/USDT', side: 'long', entryPrice: 65000, exitPrice: 66200, pnl: 300, pnlPercent: 1.85, exitTime: '2026-06-09 14:30' },
  { id: 2, symbol: 'ETH/USDT', side: 'short', entryPrice: 3200, exitPrice: 3150, pnl: 125, pnlPercent: 1.56, exitTime: '2026-06-08 09:15' },
  { id: 3, symbol: 'SOL/USDT', side: 'long', entryPrice: 145, exitPrice: 148, pnl: 45, pnlPercent: 2.07, exitTime: '2026-06-07 16:45' },
  { id: 4, symbol: 'BTC/USDT', side: 'short', entryPrice: 66800, exitPrice: 65800, pnl: -100, pnlPercent: -1.50, exitTime: '2026-06-06 11:00' },
  { id: 5, symbol: 'LINK/USDT', side: 'long', entryPrice: 14.2, exitPrice: 15.0, pnl: 56, pnlPercent: 5.63, exitTime: '2026-06-05 10:30' },
  { id: 6, symbol: 'ETH/USDT', side: 'long', entryPrice: 3180, exitPrice: 3220, pnl: 100, pnlPercent: 1.26, exitTime: '2026-06-04 13:00' },
  { id: 7, symbol: 'SOL/USDT', side: 'short', entryPrice: 152, exitPrice: 148, pnl: 60, pnlPercent: 2.63, exitTime: '2026-06-03 15:20' },
  { id: 8, symbol: 'AVAX/USDT', side: 'long', entryPrice: 38.5, exitPrice: 37.2, pnl: -52, pnlPercent: -3.38, exitTime: '2026-06-02 10:00' },
]

// AI Chat mock responses
export const aiQuickActions = [
  { command: '/风险', labelKey: 'ai.chat.quickRisk' },
  { command: '/市场', labelKey: 'ai.chat.quickMarket' },
  { command: '/信号', labelKey: 'ai.chat.quickSignal' },
]

export const aiWelcomeMessage = {
  role: 'assistant' as const,
  contentKey: 'ai.chat.welcomeContent',
}

export const aiResponseKeys: Record<string, string> = {
  '/风险': 'ai.chat.responseRisk',
  '/市场': 'ai.chat.responseMarket',
  '/信号': 'ai.chat.responseSignal',
}
