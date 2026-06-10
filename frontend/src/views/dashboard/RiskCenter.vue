<template>
  <div class="risk-center">
    <div class="page-title">&gt; {{ $t('nav.riskCenter') }}</div>

    <!-- Mode Switch -->
    <div class="mode-tabs">
      <button
        class="mode-tab"
        :class="{ active: tradingMode === 'sim' }"
        @click="emit('update:tradingMode', 'sim')"
      >
        {{ $t('trading.simulation') }}
      </button>
      <button
        class="mode-tab"
        :class="{ active: tradingMode === 'live' }"
        @click="emit('update:tradingMode', 'live')"
      >
        {{ $t('trading.real') }}
      </button>
    </div>

    <!-- Portfolio Summary -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">&gt; {{ $t('portfolio.overview') }}</span>
      </div>
      <div class="panel-body">
        <div class="portfolio-metrics">
          <div class="metric-card">
            <div class="metric-label">{{ $t('portfolio.totalAssets') }}</div>
            <div class="metric-value">${{ toLocale(activeAssets.totalValue) }}</div>
            <div class="metric-sub">{{ $t('portfolio.availableBalance') }} ${{ toLocale(activeAssets.available) }}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">{{ $t('portfolio.totalPnl') }}</div>
            <div class="metric-value" :class="activeAssets.unrealizedPnL >= 0 ? 'positive' : 'negative'">
              {{ activeAssets.unrealizedPnL >= 0 ? '+' : '' }}${{ toLocale(activeAssets.unrealizedPnL) }}
            </div>
            <div class="metric-sub" :class="portfolio.totalPnlPercent >= 0 ? 'positive' : 'negative'">
              {{ portfolio.totalPnlPercent >= 0 ? '+' : '' }}{{ portfolio.totalPnlPercent }}%
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-label">{{ $t('portfolio.winRate') }}</div>
            <div class="metric-value">{{ portfolio.winRate }}%</div>
            <div class="metric-sub">{{ $t('portfolio.totalTrades') }} {{ portfolio.totalTrades }}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">{{ $t('portfolio.profitFactor') }}</div>
            <div class="metric-value">{{ portfolio.profitFactor.toFixed(2) }}</div>
            <div class="metric-sub">{{ $t('portfolio.monthlyReturn') }} {{ portfolio.monthlyPnl >= 0 ? '+' : '' }}${{ toLocale(portfolio.monthlyPnl) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Portfolio Positions -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">&gt; {{ $t('portfolio.positionDetails') }} ({{ activePositions.length }})</span>
      </div>
      <div class="panel-body">
        <table class="data-table" v-if="activePositions.length">
          <thead>
            <tr>
              <th>{{ $t('trading.symbol') }}</th>
              <th>{{ $t('trading.side') }}</th>
              <th>{{ $t('trading.quantity') }}</th>
              <th>{{ $t('portfolio.entryPrice') }}</th>
              <th>{{ $t('portfolio.markPrice') }}</th>
              <th>{{ $t('portfolio.unrealizedPnl') }}</th>
              <th>{{ $t('trading.roi') }}</th>
              <th>{{ $t('portfolio.margin') }}</th>
              <th>{{ $t('trading.leverage') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in activePositions" :key="p.symbol">
              <td class="symbol">{{ p.symbol }}</td>
              <td><span class="side" :class="p.side">{{ p.side === 'long' ? $t('signal.long') : $t('signal.short') }}</span></td>
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
        <div v-else class="empty">{{ $t('portfolio.noPositions') }}</div>
      </div>
    </div>

    <!-- Risk Metrics -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-label">{{ $t('risk.totalExposure') }}</div>
        <div class="metric-value">${{ toLocale(activeRiskMetrics.totalExposure) }}</div>
        <div class="metric-sub">{{ $t('risk.exposureRate') }} {{ exposurePercent }}%</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">{{ $t('risk.perTradeRisk') }}</div>
        <div class="metric-value">{{ activeRiskMetrics.riskPerTrade }}%</div>
        <div class="metric-sub">{{ $t('risk.suggestedMax') }} &le; 2%</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">{{ $t('risk.currentDrawdown') }}</div>
        <div class="metric-value" :class="activeRiskMetrics.currentDrawdown > 5 ? 'negative' : 'neutral'">
          {{ activeRiskMetrics.currentDrawdown }}%
        </div>
        <div class="metric-sub" :class="activeRiskMetrics.currentDrawdown > 5 ? 'negative' : ''">
          {{ activeRiskMetrics.currentDrawdown > 5 ? '⚠ ' + $t('risk.exceedsWarning') : $t('risk.normalRange') }}
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label">{{ $t('risk.var95') }}</div>
        <div class="metric-value">${{ toLocale(activeRiskMetrics.var95) }}</div>
        <div class="metric-sub">{{ $t('risk.dailyVarEstimate') }}</div>
      </div>
    </div>

    <!-- Risk Alerts -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">&gt; {{ $t('risk.alerts') }} ({{ activeAlerts.length }})</span>
      </div>
      <div class="panel-body">
        <div v-for="alert in activeAlerts" :key="alert.id" class="alert-item" :class="alert.level">
          <div class="alert-level">
            <span v-if="alert.level === 'danger'">&#x1F534;</span>
            <span v-else-if="alert.level === 'warning'">&#x1F7E1;</span>
            <span v-else>&#x1F535;</span>
          </div>
          <div class="alert-message">{{ $t(alert.messageKey, alert.messageArgs) }}</div>
        </div>
        <div v-if="!activeAlerts.length" class="empty">{{ $t('risk.noAlerts') }}</div>
      </div>
    </div>

    <!-- Quick Risk Controls -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">&gt; {{ $t('risk.stopLossTakeProfit') }}</span>
        <button class="config-btn" @click="openEditPanel">&#x2699; {{ $t('common.edit') }}</button>
      </div>
      <div class="panel-body">
        <div class="rules-grid">
          <div class="rule-card">
            <div class="rule-label">{{ $t('risk.defaultStopLoss') }}</div>
            <div class="rule-value negative">-{{ stopLossValue }}%</div>
          </div>
          <div class="rule-card">
            <div class="rule-label">{{ $t('risk.defaultTakeProfit') }}</div>
            <div class="rule-value positive">+{{ takeProfitValue }}%</div>
          </div>
          <div class="rule-card">
            <div class="rule-label">{{ $t('risk.maxLeverage') }}</div>
            <div class="rule-value">{{ maxLeverage }}x</div>
          </div>
          <div class="rule-card">
            <div class="rule-label">{{ $t('risk.concentrationLimit') }}</div>
            <div class="rule-value">{{ concentrationLimit }}%</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 规则编辑面板 Modal -->
    <div class="modal-overlay" :class="{ open: showEditPanel }" @click="closeEditPanel">
      <div class="edit-panel" @click.stop>
        <div class="edit-panel-header">
          <span class="edit-panel-title">{{ $t('risk.editRules') }}</span>
          <button class="close-btn" @click="closeEditPanel">&#x2715;</button>
        </div>
        <div class="edit-panel-body">
          <div class="edit-field">
            <label>{{ $t('risk.defaultStopLoss') }} (%)</label>
            <div class="edit-input-group">
              <input
                type="number"
                v-model.number="editStopLoss"
                step="0.1"
                min="0.1"
                max="50"
                class="edit-input"
              />
              <span class="edit-suffix">%</span>
            </div>
            <p class="edit-hint">{{ $t('risk.stopLossHint') }}</p>
          </div>
          <div class="edit-field">
            <label>{{ $t('risk.defaultTakeProfit') }} (%)</label>
            <div class="edit-input-group">
              <input
                type="number"
                v-model.number="editTakeProfit"
                step="0.1"
                min="0.1"
                max="200"
                class="edit-input"
              />
              <span class="edit-suffix">%</span>
            </div>
            <p class="edit-hint">{{ $t('risk.takeProfitHint') }}</p>
          </div>
          <div class="edit-field">
            <label>{{ $t('risk.maxLeverage') }} (x)</label>
            <div class="edit-input-group">
              <input
                type="number"
                v-model.number="editLeverage"
                step="0.5"
                min="1"
                max="100"
                class="edit-input"
              />
              <span class="edit-suffix">x</span>
            </div>
            <p class="edit-hint">{{ $t('risk.maxLeverageHint') }}</p>
          </div>
          <div class="edit-field">
            <label>{{ $t('risk.concentrationLimit') }} (%)</label>
            <div class="edit-input-group">
              <input
                type="number"
                v-model.number="editConcentration"
                step="1"
                min="1"
                max="100"
                class="edit-input"
              />
              <span class="edit-suffix">%</span>
            </div>
            <p class="edit-hint">{{ $t('risk.concentrationHint') }}</p>
          </div>
        </div>
        <div class="edit-panel-footer">
          <button class="cancel-btn" @click="closeEditPanel">{{ $t('common.cancel') }}</button>
          <button class="save-btn" @click="saveRuleSettings">{{ $t('common.save') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  riskMetrics, riskAlerts, riskSettings,
  portfolioOverview, portfolioPositions, userAssets,
  livePortfolioOverview, livePortfolioPositions, liveUserAssets,
  liveRiskMetrics, liveRiskAlerts,
} from '@/data/mockData'

const props = defineProps<{ tradingMode: 'sim' | 'live' }>()
const emit = defineEmits<{ 'update:tradingMode': [value: 'sim' | 'live'] }>()

// Mode-aware computed data
const activeAssets = computed(() => props.tradingMode === 'sim' ? userAssets : liveUserAssets)
const portfolio = computed(() => props.tradingMode === 'sim' ? portfolioOverview : livePortfolioOverview)
const activePositions = computed(() => props.tradingMode === 'sim' ? portfolioPositions : livePortfolioPositions)
const activeRiskMetrics = computed(() => props.tradingMode === 'sim' ? riskMetrics : liveRiskMetrics)
const activeAlerts = computed(() => props.tradingMode === 'sim' ? riskAlerts : liveRiskAlerts)

const exposurePercent = computed(() => {
  if (portfolio.value.totalValue <= 0) return '0.00'
  return ((activeRiskMetrics.value.totalExposure / portfolio.value.totalValue) * 100).toFixed(1)
})

// 规则编辑面板 — 从共享 riskSettings 初始化
const showEditPanel = ref(false)
const stopLossValue = ref(riskSettings.stopLossPercent)
const takeProfitValue = ref(riskSettings.takeProfitPercent)
const maxLeverage = ref(riskSettings.maxLeverage)
const concentrationLimit = ref(riskSettings.concentrationLimit)
const editStopLoss = ref(riskSettings.stopLossPercent)
const editTakeProfit = ref(riskSettings.takeProfitPercent)
const editLeverage = ref(riskSettings.maxLeverage)
const editConcentration = ref(riskSettings.concentrationLimit)

function openEditPanel() {
  editStopLoss.value = riskSettings.stopLossPercent
  editTakeProfit.value = riskSettings.takeProfitPercent
  editLeverage.value = riskSettings.maxLeverage
  editConcentration.value = riskSettings.concentrationLimit
  showEditPanel.value = true
}

function closeEditPanel() {
  showEditPanel.value = false
}

function saveRuleSettings() {
  riskSettings.stopLossPercent = editStopLoss.value
  riskSettings.takeProfitPercent = editTakeProfit.value
  riskSettings.maxLeverage = editLeverage.value
  riskSettings.concentrationLimit = editConcentration.value
  stopLossValue.value = riskSettings.stopLossPercent
  takeProfitValue.value = riskSettings.takeProfitPercent
  maxLeverage.value = riskSettings.maxLeverage
  concentrationLimit.value = riskSettings.concentrationLimit
  showEditPanel.value = false
}

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

/* Mode Switch Tabs */
.mode-tabs {
  display: flex;
  gap: 0;
  border-bottom: 2px solid var(--border-color);
}

.mode-tab {
  padding: 8px 24px;
  border: 2px solid var(--border-color);
  border-bottom: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin-bottom: -2px;
  transition: all 0.1s ease;
}
.mode-tab:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}
.mode-tab.active {
  background: var(--bg-primary);
  color: var(--text-primary);
  border-bottom: 2px solid var(--bg-primary);
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

.rule-value.positive {
  color: var(--success-color);
}

.rule-value.negative {
  color: var(--danger-color);
}

/* 编辑面板 Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
}

.modal-overlay.open {
  opacity: 1;
  visibility: visible;
}

.edit-panel {
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  width: 420px;
  max-width: 90vw;
  box-shadow: 8px 8px 0 rgba(0, 0, 0, 0.3);
}

.edit-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 2px solid var(--border-color);
  background: var(--bg-secondary);
}

.edit-panel-title {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.edit-panel-header .close-btn {
  width: 28px;
  height: 28px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.edit-panel-header .close-btn:hover {
  background: var(--danger-color);
  border-color: var(--danger-color);
  color: white;
}

.edit-panel-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.edit-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.edit-field label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.edit-input-group {
  display: flex;
  align-items: center;
  gap: 0;
}

.edit-input {
  flex: 1;
  padding: 10px 14px;
  border: 2px solid var(--border-color);
  border-right: none;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 700;
  font-family: var(--font-mono, monospace);
  outline: none;
}
.edit-input:focus {
  border-color: var(--success-color);
}

.edit-suffix {
  padding: 10px 14px;
  border: 2px solid var(--border-color);
  border-left: none;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 600;
  font-family: var(--font-mono, monospace);
}

.edit-hint {
  font-size: 11px;
  color: var(--text-secondary);
  margin: 0;
}

.edit-panel-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px 20px;
  border-top: 2px solid var(--border-color);
}

.cancel-btn {
  padding: 8px 20px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.cancel-btn:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}

.save-btn {
  padding: 8px 20px;
  border: 2px solid var(--success-color);
  background: var(--success-color);
  color: var(--bg-primary);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.save-btn:hover {
  background: transparent;
  color: var(--success-color);
}
</style>
