<template>
  <div class="strategy-templates">
    <div class="page-header">
      <h1 class="page-title">&gt; {{ t('strategy.templates').toUpperCase() }}.EXE</h1>
      <div class="status-bar">
        <span class="status-item">{{ t('strategy.totalTemplates') }}: {{ filteredTemplates.length }}</span>
      </div>
    </div>

    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">{{ t('strategy.filterType') }}:</span>
        <button class="filter-btn" :class="{ active: activeCategory === 'all' }" @click="activeCategory = 'all'">{{ t('common.all') }}</button>
        <button class="filter-btn" :class="{ active: activeCategory === 'trend' }" @click="activeCategory = 'trend'">{{ t('strategy.trend') }}</button>
        <button class="filter-btn" :class="{ active: activeCategory === 'mean_reversion' }" @click="activeCategory = 'mean_reversion'">{{ t('strategy.meanReversion') }}</button>
        <button class="filter-btn" :class="{ active: activeCategory === 'arbitrage' }" @click="activeCategory = 'arbitrage'">{{ t('strategy.arbitrage') }}</button>
        <button class="filter-btn" :class="{ active: activeCategory === 'advanced' }" @click="activeCategory = 'advanced'">{{ t('strategy.advanced') }}</button>
      </div>
    </div>

    <div class="templates-grid">
      <div class="template-card" v-for="t in filteredTemplates" :key="t.id">
        <div class="card-header">
          <span class="card-icon">{{ t.icon }}</span>
          <div class="card-info">
            <h3 class="card-name">{{ t.name }}</h3>
            <span class="card-category">{{ t('strategy.' + t.categoryKey) }}</span>
          </div>
          <span class="card-difficulty" :class="t.difficulty">{{ t('strategy.' + t.difficulty) }}</span>
        </div>

        <p class="card-description">{{ t.description }}</p>

        <div class="card-features">
          <div class="feature-item" v-for="feature in t.features" :key="feature">
            <span class="feature-check">✓</span>
            <span class="feature-text">{{ feature }}</span>
          </div>
        </div>

        <div class="card-performance">
          <div class="perf-item">
            <span class="perf-label">{{ t('strategy.expectedWinRate') }}</span>
            <span class="perf-value">{{ t.expectedWinRate }}%</span>
          </div>
          <div class="perf-item">
            <span class="perf-label">{{ t('strategy.expectedProfitFactor') }}</span>
            <span class="perf-value">{{ t.expectedProfitFactor }}</span>
          </div>
          <div class="perf-item">
            <span class="perf-label">{{ t('strategy.riskLevel') }}</span>
            <span class="perf-value" :class="t.riskClass">{{ t.riskLevel }}</span>
          </div>
        </div>

        <div class="card-footer">
          <div class="card-stats">
            <span class="stat-item">
              <span class="stat-label">{{ t('strategy.users') }}:</span>
              <span class="stat-value">{{ t.users }}</span>
            </span>
            <span class="stat-item">
              <span class="stat-label">{{ t('strategy.rating') }}:</span>
              <span class="stat-value">{{ t.rating }}/5</span>
            </span>
          </div>
          <button class="btn-primary" @click="useTemplate(t)">
            [ {{ t('strategy.useTemplate') }} ]
          </button>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">&gt; {{ t('strategy.previewCode') }}</span>
      </div>
      <div class="panel-body">
        <div class="code-preview">
          <pre><code>{{ selectedTemplateCode }}</code></pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

const activeCategory = ref('all')

// 中文模板数据
const zhTemplates = [
  {
    id: 1,
    name: '移动平均线交叉',
    icon: '📊', categoryKey: 'trend', difficulty: 'beginner',
    description: '经典的 50 日和 200 日移动平均线交叉趋势跟踪策略。',
    features: ['金叉/死叉信号', '简单易懂，易于实现', '强趋势市场中表现优异', '可自定义时间周期'],
    expectedWinRate: 62, expectedProfitFactor: 1.8, riskLevel: '中', riskClass: 'warning',
    users: 12453, rating: 4.5
  },
  {
    id: 2,
    name: '布林带均值回归',
    icon: '📈', categoryKey: 'mean_reversion', difficulty: 'intermediate',
    description: '利用布林带识别超买超卖状态的均值回归策略。',
    features: ['在极端价格水平交易', '内置波动率调整', '最适合震荡市场', '包含止损逻辑'],
    expectedWinRate: 75, expectedProfitFactor: 2.1, riskLevel: '低', riskClass: 'positive',
    users: 8921, rating: 4.7
  },
  {
    id: 3,
    name: 'RSI 动量策略',
    icon: '⚡', categoryKey: 'trend', difficulty: 'beginner',
    description: '基于 RSI 指标识别强动量行情的策略。',
    features: ['识别强动量', '避免超买入场', '多时间周期确认', '包含移动止损'],
    expectedWinRate: 58, expectedProfitFactor: 2.3, riskLevel: '高', riskClass: 'danger',
    users: 15678, rating: 4.3
  },
  {
    id: 4,
    name: '统计套利',
    icon: '🔄', categoryKey: 'arbitrage', difficulty: 'advanced',
    description: '利用相关资产价格偏差的对冲交易策略。',
    features: ['市场中性策略', '协整分析', '对冲比率计算', '与市场低相关'],
    expectedWinRate: 82, expectedProfitFactor: 3.5, riskLevel: '低', riskClass: 'positive',
    users: 3421, rating: 4.8
  },
  {
    id: 5,
    name: 'MACD 趋势跟踪',
    icon: '📉', categoryKey: 'trend', difficulty: 'intermediate',
    description: '基于 MACD 柱状图和信号线交叉的综合趋势跟踪策略。',
    features: ['MACD 柱状图背离', '信号线交叉', '趋势强度过滤', '成交量确认'],
    expectedWinRate: 65, expectedProfitFactor: 2.0, riskLevel: '中', riskClass: 'warning',
    users: 9876, rating: 4.4
  },
  {
    id: 6,
    name: '网格交易机器人',
    icon: '🤖', categoryKey: 'mean_reversion', difficulty: 'intermediate',
    description: '在震荡市场中从价格波动中获利的自动网格交易系统。',
    features: ['自动买卖网格', '每层止盈', '可自定义网格间距', '7x24 小时自动运行'],
    expectedWinRate: 78, expectedProfitFactor: 1.7, riskLevel: '低', riskClass: 'positive',
    users: 21543, rating: 4.6
  },
  {
    id: 7,
    name: '三屏交易系统',
    icon: '🎯', categoryKey: 'advanced', difficulty: 'advanced',
    description: 'Dr. Elder 的三重时间框架交易系统。',
    features: ['长期趋势识别', '中期入场时机', '短期执行', '全面风险管理'],
    expectedWinRate: 70, expectedProfitFactor: 2.5, riskLevel: '中', riskClass: 'warning',
    users: 5678, rating: 4.9
  },
  {
    id: 8,
    name: '资金费率套利',
    icon: '💰', categoryKey: 'arbitrage', difficulty: 'advanced',
    description: '捕获现货和永续合约期货市场之间的资金费率差异。',
    features: ['低风险盈利机会', 'Delta 中性持仓', '自动资金收集', '多交易所支持'],
    expectedWinRate: 90, expectedProfitFactor: 4.0, riskLevel: '低', riskClass: 'positive',
    users: 2345, rating: 4.7
  }
]

// 英文模板数据
const enTemplates = [
  {
    id: 1,
    name: 'MOVING_AVERAGE_CROSSOVER', icon: '📊', categoryKey: 'trend', difficulty: 'beginner',
    description: 'Classic trend following strategy using 50-day and 200-day moving average crossovers.',
    features: ['Golden cross / Death cross signals', 'Simple to understand and implement', 'Works well in strong trending markets', 'Customizable time periods'],
    expectedWinRate: 62, expectedProfitFactor: 1.8, riskLevel: 'MEDIUM', riskClass: 'warning',
    users: 12453, rating: 4.5
  },
  {
    id: 2,
    name: 'BOLLINGER_BANDS_REVERSION', icon: '📈', categoryKey: 'mean_reversion', difficulty: 'intermediate',
    description: 'Mean reversion strategy using Bollinger Bands to identify overbought/oversold conditions.',
    features: ['Trade at extreme price levels', 'Built-in volatility adjustment', 'Works best in range-bound markets', 'Includes stop-loss logic'],
    expectedWinRate: 75, expectedProfitFactor: 2.1, riskLevel: 'LOW', riskClass: 'positive',
    users: 8921, rating: 4.7
  },
  {
    id: 3,
    name: 'RSI_MOMENTUM', icon: '⚡', categoryKey: 'trend', difficulty: 'beginner',
    description: 'Momentum strategy based on RSI indicator to capture strong price movements.',
    features: ['Identify strong momentum', 'Avoid overbought entries', 'Multiple timeframe confirmation', 'Trailing stop included'],
    expectedWinRate: 58, expectedProfitFactor: 2.3, riskLevel: 'HIGH', riskClass: 'danger',
    users: 15678, rating: 4.3
  },
  {
    id: 4,
    name: 'STATISTICAL_ARBITRAGE', icon: '🔄', categoryKey: 'arbitrage', difficulty: 'advanced',
    description: 'Pairs trading strategy exploiting price inefficiencies between correlated assets.',
    features: ['Market neutral strategy', 'Cointegration analysis', 'Hedge ratio calculation', 'Low correlation to markets'],
    expectedWinRate: 82, expectedProfitFactor: 3.5, riskLevel: 'LOW', riskClass: 'positive',
    users: 3421, rating: 4.8
  },
  {
    id: 5,
    name: 'MACD_TREND_FOLLOWER', icon: '📉', categoryKey: 'trend', difficulty: 'intermediate',
    description: 'Comprehensive trend following using MACD histogram and signal line crossovers.',
    features: ['MACD histogram divergence', 'Signal line crossovers', 'Trend strength filter', 'Volume confirmation'],
    expectedWinRate: 65, expectedProfitFactor: 2.0, riskLevel: 'MEDIUM', riskClass: 'warning',
    users: 9876, rating: 4.4
  },
  {
    id: 6,
    name: 'GRID_TRADING_BOT', icon: '🤖', categoryKey: 'mean_reversion', difficulty: 'intermediate',
    description: 'Automated grid trading system that profits from price volatility in range-bound markets.',
    features: ['Automated buy/sell grid', 'Profit taking at each level', 'Customizable grid spacing', 'Works 24/7 automatically'],
    expectedWinRate: 78, expectedProfitFactor: 1.7, riskLevel: 'LOW', riskClass: 'positive',
    users: 21543, rating: 4.6
  },
  {
    id: 7,
    name: 'TRIPLE_SCREEN_SYSTEM', icon: '🎯', categoryKey: 'advanced', difficulty: 'advanced',
    description: "Dr. Elder's Triple Screen trading system combining multiple timeframes.",
    features: ['Long-term trend identification', 'Medium-term entry timing', 'Short-term execution', 'Comprehensive risk management'],
    expectedWinRate: 70, expectedProfitFactor: 2.5, riskLevel: 'MEDIUM', riskClass: 'warning',
    users: 5678, rating: 4.9
  },
  {
    id: 8,
    name: 'FUNDING_RATE_ARBITRAGE', icon: '💰', categoryKey: 'arbitrage', difficulty: 'advanced',
    description: 'Capture funding rate differentials between spot and perpetual futures markets.',
    features: ['Low risk profit opportunity', 'Delta neutral position', 'Automated funding collection', 'Multiple exchange support'],
    expectedWinRate: 90, expectedProfitFactor: 4.0, riskLevel: 'LOW', riskClass: 'positive',
    users: 2345, rating: 4.7
  }
]

const templatesList = computed(() => {
  return locale.value === 'zh-CN' ? zhTemplates : enTemplates
})

const filteredTemplates = computed(() => {
  if (activeCategory.value === 'all') return templatesList.value
  return templatesList.value.filter(t => t.categoryKey === activeCategory.value)
})

const selectedTemplateCode = ref(`// STRATEGY_TEMPLATE_EXAMPLE
// MOVING_AVERAGE_CROSSOVER

strategy("MA_Crossover", overlay=true)

// Inputs
fast_len = input.int(50, "Fast_MA_Length")
slow_len = input.int(200, "Slow_MA_Length")

// Calculate MAs
fast_ma = ta.sma(close, fast_len)
slow_ma = ta.sma(close, slow_len)

// Plot
plot(fast_ma, color=color.new(color.blue, 0))
plot(slow_ma, color=color.new(color.red, 0))

// Signals
golden_cross = ta.crossover(fast_ma, slow_ma)
death_cross = ta.crossunder(fast_ma, slow_ma)

// Execute trades
if (golden_cross)
    strategy.entry("Long", strategy.long)

if (death_cross)
    strategy.close("Long")`)

function useTemplate(template: any) {
  console.log('Using template:', template.name)
  alert(t('strategy.templateLoaded'))
}
</script>

<style scoped>
.strategy-templates {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid var(--text-primary);
  padding-bottom: 16px;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  letter-spacing: 2px;
}

.status-bar {
  display: flex;
  gap: 24px;
  font-size: 12px;
  font-family: var(--font-mono);
}

.status-item {
  color: var(--text-secondary);
}

.filters {
  margin-bottom: 24px;
}

.filter-group {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 11px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  margin-right: 8px;
}

.filter-btn {
  padding: 6px 16px;
  border: 2px solid var(--text-primary);
  background: transparent;
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.1s ease;
}

.filter-btn:hover,
.filter-btn.active {
  background: var(--text-primary);
  color: var(--bg-primary);
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.template-card {
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
  transition: all 0.1s ease;
}

.template-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: 4px 4px 0 var(--text-primary);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.card-icon {
  font-size: 32px;
}

.card-info {
  flex: 1;
}

.card-name {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 14px;
  margin-bottom: 4px;
}

.card-category {
  font-size: 10px;
  padding: 2px 6px;
  background: var(--bg-secondary);
  font-family: var(--font-mono);
}

.card-difficulty {
  font-size: 10px;
  padding: 2px 8px;
  border: 1px solid currentColor;
  font-family: var(--font-mono);
}

.card-difficulty.beginner {
  color: var(--success-color);
}

.card-difficulty.intermediate {
  color: var(--warning-color);
}

.card-difficulty.advanced {
  color: var(--danger-color);
}

.card-description {
  padding: 12px 16px;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.card-features {
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  font-size: 12px;
}

.feature-check {
  color: var(--success-color);
  font-weight: 700;
}

.feature-text {
  font-family: var(--font-mono);
}

.card-performance {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.perf-item {
  text-align: center;
}

.perf-label {
  display: block;
  font-size: 9px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  margin-bottom: 4px;
}

.perf-value {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 13px;
}

.perf-value.positive {
  color: var(--success-color);
}

.perf-value.warning {
  color: var(--warning-color);
}

.perf-value.danger {
  color: var(--danger-color);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
}

.card-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  font-size: 10px;
  font-family: var(--font-mono);
}

.stat-label {
  color: var(--text-secondary);
  margin-right: 4px;
}

.stat-value {
  font-weight: 700;
}

.btn-primary {
  padding: 8px 16px;
  border: 2px solid var(--success-color);
  background: var(--success-color);
  color: var(--bg-primary);
  font-family: var(--font-mono);
  font-size: 10px;
  cursor: pointer;
  transition: all 0.1s ease;
}

.btn-primary:hover {
  transform: translate(2px, 2px);
  box-shadow: none;
}

.panel {
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
}

.panel-header {
  padding: 12px 16px;
  border-bottom: 2px solid var(--text-primary);
  background: var(--text-primary);
  color: var(--bg-primary);
}

.panel-title {
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 1px;
}

.panel-body {
  padding: 0;
}

.code-preview {
  padding: 16px;
  overflow-x: auto;
}

.code-preview pre {
  margin: 0;
}

.code-preview code {
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .templates-grid {
    grid-template-columns: 1fr;
  }

  .card-footer {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .card-performance {
    grid-template-columns: 1fr;
  }
}
</style>
