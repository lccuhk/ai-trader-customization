<template>
  <div class="risk-center">
    <div class="page-title">&gt; 风控中心</div>

    <!-- Portfolio Summary -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">&gt; 资产概览</span>
      </div>
      <div class="panel-body">
        <div class="portfolio-metrics">
          <div class="metric-card">
            <div class="metric-label">总资产</div>
            <div class="metric-value">${{ toLocale(portfolio.totalValue) }}</div>
            <div class="metric-sub">余额 ${{ toLocale(portfolio.totalBalance) }}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">总盈亏</div>
            <div class="metric-value" :class="portfolio.totalPnl >= 0 ? 'positive' : 'negative'">
              {{ portfolio.totalPnl >= 0 ? '+' : '' }}${{ toLocale(portfolio.totalPnl) }}
            </div>
            <div class="metric-sub" :class="portfolio.totalPnlPercent >= 0 ? 'positive' : 'negative'">
              {{ portfolio.totalPnlPercent >= 0 ? '+' : '' }}{{ portfolio.totalPnlPercent }}%
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-label">胜率</div>
            <div class="metric-value">{{ portfolio.winRate }}%</div>
            <div class="metric-sub">总交易 {{ portfolio.totalTrades }}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">利润因子</div>
            <div class="metric-value">{{ portfolio.profitFactor.toFixed(2) }}</div>
            <div class="metric-sub">月收益 {{ portfolio.monthlyPnl >= 0 ? '+' : '' }}${{ toLocale(portfolio.monthlyPnl) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Portfolio Positions -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">&gt; 持仓明细 ({{ portfolioPositions.length }})</span>
      </div>
      <div class="panel-body">
        <table class="data-table" v-if="portfolioPositions.length">
          <thead>
            <tr>
              <th>标的</th>
              <th>方向</th>
              <th>数量</th>
              <th>开仓价</th>
              <th>标记价</th>
              <th>未实现盈亏</th>
              <th>收益率</th>
              <th>占用保证金</th>
              <th>杠杆</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in portfolioPositions" :key="p.symbol">
              <td class="symbol">{{ p.symbol }}</td>
              <td><span class="side" :class="p.side">{{ p.side === 'long' ? '多' : '空' }}</span></td>
              <td>{{ p.size }}</td>
              <td>${{ toLocale(p.entryPrice) }}</td>
              <td>${{ toLocale(p.markPrice) }}</td>
              <td :class="p.unrealizedPnl >= 0 ? 'positive' : 'negative'">
                {{ p.unrealizedPnl >= 0 ? '+' : '' }}${{ toLocale(p.unrealizedPnl) }}
              </td>
              <td :class="p.pnlPercent >= 0 ? 'positive' : 'negative'">
                {{ p.pnlPercent >= 0 ? '+' : '' }}{{ p.pnlPercent.toFixed(2) }}%
              </td>
              <td>${{ toLocale(p.margin) }}</td>
              <td>{{ p.leverage }}x</td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty">暂无持仓</div>
      </div>
    </div>

    <!-- Risk Metrics -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-label">总敞口</div>
        <div class="metric-value">${{ toLocale(riskMetrics.totalExposure) }}</div>
        <div class="metric-sub">占资产 {{ exposurePercent }}%</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">单笔风险</div>
        <div class="metric-value">{{ riskMetrics.riskPerTrade }}%</div>
        <div class="metric-sub">建议 ≤ 2%</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">当前回撤</div>
        <div class="metric-value" :class="riskMetrics.currentDrawdown > 5 ? 'negative' : 'neutral'">
          {{ riskMetrics.currentDrawdown }}%
        </div>
        <div class="metric-sub" :class="riskMetrics.currentDrawdown > 5 ? 'negative' : ''">
          {{ riskMetrics.currentDrawdown > 5 ? '⚠ 超过预警线' : '正常范围' }}
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label">VaR (95%)</div>
        <div class="metric-value">${{ toLocale(riskMetrics.var95) }}</div>
        <div class="metric-sub">日 VaR 估算</div>
      </div>
    </div>

    <!-- Risk Alerts -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">&gt; 风险预警 ({{ riskAlerts.length }})</span>
        <button class="config-btn" @click="alert('风控设置')">⚙ 设置</button>
      </div>
      <div class="panel-body">
        <div v-for="alert in riskAlerts" :key="alert.id" class="alert-item" :class="alert.level">
          <div class="alert-level">
            <span v-if="alert.level === 'danger'">🔴</span>
            <span v-else-if="alert.level === 'warning'">🟡</span>
            <span v-else>🔵</span>
          </div>
          <div class="alert-message">{{ alert.message }}</div>
        </div>
        <div v-if="!riskAlerts.length" class="empty">暂无预警</div>
      </div>
    </div>

    <!-- Quick Risk Controls -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">&gt; 止损止盈规则</span>
      </div>
      <div class="panel-body">
        <div class="rules-grid">
          <div class="rule-card">
            <div class="rule-label">默认止损</div>
            <div class="rule-value">-2.5%</div>
            <button class="rule-btn" @click="alert('编辑默认止损')">编辑</button>
          </div>
          <div class="rule-card">
            <div class="rule-label">默认止盈</div>
            <div class="rule-value">+5.0%</div>
            <button class="rule-btn" @click="alert('编辑默认止盈')">编辑</button>
          </div>
          <div class="rule-card">
            <div class="rule-label">最大杠杆</div>
            <div class="rule-value">3x</div>
            <button class="rule-btn" @click="alert('编辑最大杠杆')">编辑</button>
          </div>
          <div class="rule-card">
            <div class="rule-label">集中度限制</div>
            <div class="rule-value">30%</div>
            <button class="rule-btn" @click="alert('编辑集中度限制')">编辑</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { riskMetrics, riskAlerts, portfolioOverview, portfolioPositions } from '@/data/mockData'

const portfolio = portfolioOverview

const exposurePercent = computed(() => {
  if (portfolio.totalValue <= 0) return '0.00'
  return ((riskMetrics.totalExposure / portfolio.totalValue) * 100).toFixed(1)
})

function toLocale(n: number): string {
  return n.toLocaleString()
}
</script>

<style scoped>
.risk-center {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.05em;
}

/* Portfolio & Risk Metrics Grid */
.portfolio-metrics,
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.metric-card {
  padding: 20px;
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
  text-align: center;
}

.metric-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.metric-sub {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.metric-sub.positive {
  color: var(--success-color);
}
.metric-sub.negative {
  color: var(--danger-color);
}

.metric-value.neutral {
  color: var(--text-primary);
}

.metric-value.negative {
  color: var(--danger-color);
}

.metric-value.positive {
  color: var(--success-color);
}

/* Panel styling */
.panel {
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 2px solid var(--border-color);
  background: var(--bg-secondary);
}

.panel-title {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.config-btn {
  padding: 4px 10px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 11px;
  cursor: pointer;
}
.config-btn:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}

.panel-body {
  padding: 16px;
}

/* Data Table */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.data-table th {
  text-align: left;
  padding: 8px 10px;
  border-bottom: 2px solid var(--border-color);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--text-secondary);
  font-weight: 600;
}

.data-table td {
  padding: 8px 10px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.symbol {
  font-weight: 700;
}

.side {
  padding: 2px 6px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid currentColor;
}
.side.long { color: var(--success-color); }
.side.short { color: var(--danger-color); }

.positive { color: var(--success-color); font-weight: 600; }
.negative { color: var(--danger-color); font-weight: 600; }

/* Alerts */
.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
  font-size: 13px;
}

.alert-item:last-child {
  border-bottom: none;
}

.alert-item.danger {
  background: var(--danger-bg);
}
.alert-item.warning {
  background: var(--warning-bg);
}

.alert-level {
  flex-shrink: 0;
  font-size: 16px;
}

.alert-message {
  color: var(--text-primary);
  line-height: 1.4;
}

.empty {
  text-align: center;
  padding: 32px;
  color: var(--text-secondary);
  font-size: 13px;
}

/* Rules */
.rules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.rule-card {
  padding: 16px;
  border: 2px solid var(--border-color);
  background: var(--bg-secondary);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rule-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.rule-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.rule-btn {
  padding: 6px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 11px;
  cursor: pointer;
  text-transform: uppercase;
}
.rule-btn:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}
</style>
