<template>
  <aside class="quick-info" :class="{ collapsed: isCollapsed }">
    <button class="toggle-btn" @click="isCollapsed = !isCollapsed">
      {{ isCollapsed ? '◀' : '▶' }}
    </button>

    <div v-if="!isCollapsed" class="info-content">
      <div class="info-section">
        <div class="section-header">
          <span class="section-icon">📊</span>
          <span class="section-title">{{ $t('market.sentiment') }}</span>
        </div>
        <div class="sentiment-display">
          <div class="sentiment-score" :class="sentimentLevelClass">
            {{ data.marketSentiment.score }}
          </div>
          <div class="sentiment-details">
            <span class="sentiment-level" :class="sentimentLevelClass">{{ $t('market.' + data.marketSentiment.level) }}</span>
            <span class="sentiment-trend">{{ $t('market.' + data.marketSentiment.trend) }} →</span>
          </div>
        </div>
      </div>

      <div class="info-section">
        <div class="section-header">
          <span class="section-icon">💹</span>
          <span class="section-title">{{ $t('market.marketQuotes') }}</span>
        </div>
        <div class="quotes-list">
          <div v-for="q in data.quotes" :key="q.symbol" class="quote-item">
            <span class="quote-symbol">{{ q.symbol.replace('/USDT', '') }}</span>
            <span class="quote-price">${{ formatQuotePrice(q.price) }}</span>
            <span class="quote-change" :class="q.change24h >= 0 ? 'positive' : 'negative'">
              {{ q.change24h >= 0 ? '+' : '' }}{{ q.change24h }}%
            </span>
          </div>
        </div>
      </div>

      <div class="info-section">
        <div class="section-header">
          <span class="section-icon">🌍</span>
          <span class="section-title">{{ $t('market.indicators') }}</span>
        </div>
        <div class="indicators-list">
          <div v-for="ind in data.economicIndicators" :key="ind.nameKey" class="indicator-item">
            <span class="indicator-name">{{ $t(ind.nameKey) }}</span>
            <span class="indicator-value">{{ ind.value }}</span>
            <span class="indicator-change" :class="ind.change.startsWith('+') ? 'positive' : 'negative'">
              {{ ind.change }}
            </span>
          </div>
        </div>
      </div>

      <div class="info-section">
        <div class="section-header">
          <span class="section-icon">⚠</span>
          <span class="section-title">{{ $t('risk.activeWarnings') }}</span>
        </div>
        <div class="alerts-list">
          <div
            v-for="alert in data.alerts"
            :key="alert.id"
            class="alert-item"
            :class="alert.type"
          >
            <span class="alert-dot">●</span>
            <span class="alert-text">{{ $t(alert.messageKey) }}</span>
          </div>
        </div>
      </div>

      <div class="info-section">
        <div class="section-header">
          <span class="section-icon">🤖</span>
          <span class="section-title">{{ $t('ai.suggestion') }}</span>
        </div>
        <div class="ai-one-liner">
          {{ $t(data.aiOneLinerKey) }}
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { quickInfo, marketQuotes, economicIndicators } from '@/data/mockData'

const isCollapsed = ref(false)
const data = {
  ...quickInfo,
  quotes: marketQuotes,
  economicIndicators,
}

function formatQuotePrice(price: number): string {
  if (price >= 1) return price.toLocaleString()
  return price.toFixed(4)
}

const sentimentLevelClass = computed(() => {
  const score = data.marketSentiment.score
  if (score >= 75) return 'extreme-greed'
  if (score >= 55) return 'greed'
  if (score >= 45) return 'neutral'
  if (score >= 25) return 'fear'
  return 'extreme-fear'
})
</script>

<style scoped>
.quick-info {
  width: 280px;
  min-width: 280px;
  min-height: 100vh;
  background: var(--bg-primary);
  border-left: 2px solid var(--border-color);
  display: flex;
  flex-direction: column;
  position: relative;
  transition: all 0.2s ease;
  overflow-y: auto;
}

.quick-info.collapsed {
  width: 40px;
  min-width: 40px;
}

.toggle-btn {
  position: absolute;
  top: 16px;
  left: 0;
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 14px;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 2px solid var(--border-color);
  border-bottom: 2px solid var(--border-color);
}
.toggle-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.info-content {
  padding: 16px;
  padding-top: 64px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.section-icon {
  font-size: 16px;
}

.section-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-primary);
}

.sentiment-display {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: var(--bg-secondary);
}

.sentiment-score {
  font-size: 36px;
  font-weight: 700;
  font-family: var(--font-mono, monospace);
  line-height: 1;
}

.sentiment-score.extreme-greed,
.sentiment-score.greed {
  color: var(--success-color);
}
.sentiment-score.extreme-fear,
.sentiment-score.fear {
  color: var(--danger-color);
}
.sentiment-score.neutral {
  color: var(--text-primary);
}

.sentiment-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sentiment-level {
  font-size: 14px;
  font-weight: 700;
}
.sentiment-level.extreme-greed,
.sentiment-level.greed {
  color: var(--success-color);
}
.sentiment-level.extreme-fear,
.sentiment-level.fear {
  color: var(--danger-color);
}
.sentiment-level.neutral {
  color: var(--text-primary);
}

.sentiment-trend {
  font-size: 11px;
  color: var(--text-secondary);
  font-family: var(--font-mono, monospace);
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.alert-item {
  display: flex;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-secondary);
  font-size: 12px;
  line-height: 1.4;
}

.alert-item.warning {
  border-left: 3px solid var(--warning-color);
}
.alert-item.info {
  border-left: 3px solid var(--success-color);
}
.alert-item.danger {
  border-left: 3px solid var(--danger-color);
}

.alert-dot {
  flex-shrink: 0;
  font-size: 10px;
  margin-top: 2px;
}
.alert-item.warning .alert-dot {
  color: var(--warning-color);
}
.alert-item.info .alert-dot {
  color: var(--success-color);
}
.alert-item.danger .alert-dot {
  color: var(--danger-color);
}

.alert-text {
  color: var(--text-secondary);
}

.ai-one-liner {
  padding: 12px;
  background: var(--bg-secondary);
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-primary);
  border-left: 3px solid var(--text-primary);
}

/* Market Quotes */
.quotes-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.quote-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--bg-secondary);
  font-size: 12px;
}

.quote-symbol {
  font-weight: 700;
  color: var(--text-primary);
  width: 36px;
  flex-shrink: 0;
}

.quote-price {
  flex: 1;
  color: var(--text-primary);
  font-family: var(--font-mono, monospace);
  text-align: right;
}

.quote-change {
  font-weight: 600;
  font-family: var(--font-mono, monospace);
  width: 60px;
  text-align: right;
}
.quote-change.positive {
  color: var(--success-color);
}
.quote-change.negative {
  color: var(--danger-color);
}

/* Economic Indicators */
.indicators-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.indicator-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--bg-secondary);
  font-size: 12px;
}

.indicator-name {
  flex: 1;
  color: var(--text-secondary);
  font-size: 11px;
}

.indicator-value {
  font-weight: 600;
  color: var(--text-primary);
  font-family: var(--font-mono, monospace);
}

.indicator-change {
  font-weight: 600;
  font-family: var(--font-mono, monospace);
  width: 50px;
  text-align: right;
}
.indicator-change.positive {
  color: var(--success-color);
}
.indicator-change.negative {
  color: var(--danger-color);
}
</style>
