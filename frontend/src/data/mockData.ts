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

export const openOrders = [
  { id: 1, symbol: 'BTC/USDT', side: 'buy', type: 'limit', price: 64000, amount: 0.1, status: 'open', time: '2026-06-08 10:30' },
  { id: 2, symbol: 'ETH/USDT', side: 'sell', type: 'limit', price: 3300, amount: 1.0, status: 'open', time: '2026-06-08 09:15' },
  { id: 3, symbol: 'SOL/USDT', side: 'buy', type: 'market', price: 148, amount: 5, status: 'filled', time: '2026-06-08 08:00' },
]

export const signals = [
  { id: 1, strategy: '动量突破', asset: 'BTC/USDT', direction: 'long', confidence: 87, price: 66100, target: 67500, stopLoss: 65500 },
  { id: 2, strategy: '均值回归', asset: 'ETH/USDT', direction: 'short', confidence: 72, price: 3150, target: 3080, stopLoss: 3190 },
  { id: 3, strategy: '趋势跟踪', asset: 'SOL/USDT', direction: 'long', confidence: 81, price: 148, target: 155, stopLoss: 144 },
  { id: 4, strategy: '网格交易', asset: 'BNB/USDT', direction: 'long', confidence: 65, price: 580, target: 600, stopLoss: 565 },
]

export const quickInfo = {
  marketSentiment: { score: 62, level: '贪婪', trend: '上升' },
  alerts: [
    { id: 1, type: 'warning' as const, message: 'BTC 接近止损价 65500' },
    { id: 2, type: 'info' as const, message: 'ETH 盈利已超过 1.5%' },
  ],
  aiOneLiner: '当前波动率上升，建议降低杠杆至 2x，关注 BTC 66000 支撑位',
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
  { name: '美元指数', value: '104.2', change: '-0.3%' },
  { name: '10年期美债收益率', value: '4.25%', change: '-0.05%' },
  { name: '标普500', value: '5420', change: '+0.8%' },
  { name: '黄金 (XAU/USD)', value: '2345', change: '+0.5%' },
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

export const riskMetrics = {
  totalExposure: 8450.32,
  riskPerTrade: 2.5,
  currentDrawdown: 3.2,
  var95: 425.00,
}

export const riskAlerts = [
  { id: 1, level: 'warning' as const, message: 'BTC 仓位集中度 45%，超过建议 30%' },
  { id: 2, level: 'info' as const, message: '今日已实现盈亏: +$342.15' },
  { id: 3, level: 'danger' as const, message: 'SOL 止损位 144 接近当前价格 148' },
]

// AI Chat mock responses
export const aiQuickActions = [
  { command: '/风险', label: '风险评估' },
  { command: '/市场', label: '市场分析' },
  { command: '/信号', label: '当前信号' },
]

export const aiWelcomeMessage = {
  role: 'assistant' as const,
  content: '你好！我是 AI 交易助手。我可以帮你分析市场、评估风险、解读信号。试试下面的快捷按钮吧！',
}

export const aiResponses: Record<string, string> = {
  '/风险': '📊 **风险评估**\n\n当前账户风险状况：\n- 总敞口: $8,450.32 (67.8%)\n- 单笔风险: 2.5%\n- 最大回撤: 3.2%\n- VaR(95%): $425.00\n\n⚠️ **建议**: BTC 仓位集中度偏高(45%)，建议适当减仓或设置更紧的止损。',
  '/市场': '📈 **市场分析**\n\n**BTC**: 66200 (+2.3%) — 突破 66000 阻力位，量能配合良好\n**ETH**: 3150 (-0.8%) — 短期回调，3200 为关键压力位\n**SOL**: 148 (+5.2%) — 强势突破，关注 155 目标位\n\n整体情绪偏向贪婪(62)，短期注意回调风险。',
  '/信号': '🔔 **当前信号**\n\n1. BTC/USDT 动量突破 — 多头 87分 → 入场 66100\n2. ETH/USDT 均值回归 — 空头 72分 → 入场 3150\n3. SOL/USDT 趋势跟踪 — 多头 81分 → 入场 148\n\n建议优先关注 BTC 信号，置信度最高。',
}
