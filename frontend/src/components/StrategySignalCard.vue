<template>
  <div
    class="signal-card"
    :class="{ followed: isFollowed }"
    :style="borderTopStyle"
  >
    <!-- === 第一行：标的名称 + 方向标签 === -->
    <div class="card-top">
      <span class="asset-name">{{ signal.asset }}</span>
      <span class="direction-badge" :class="signal.direction">
        {{ signal.direction === 'long' ? $t('signal.long') : $t('signal.short') }}
      </span>
    </div>

    <!-- === 第二行：策略类型 + 历史胜率 === -->
    <div class="card-meta">
      <span
        class="strategy-tag"
        :style="{ borderColor: strategyHue || '#666', color: strategyHue || '#666' }"
      >
        {{ strategyLabel(signal.strategy) }}
      </span>
      <span v-if="signal.winRate !== undefined" class="meta-stat">
        {{ $t('signal.winRate') }} <strong>{{ signal.winRate }}%</strong>
      </span>
      <span v-else class="meta-stat">
        {{ $t('signal.confidence') }} <strong>{{ signal.confidence }}%</strong>
      </span>
    </div>

    <!-- === 第三层：核心价格数据 === -->
    <div class="card-prices">
      <div class="price-item">
        <span class="price-label">{{ $t('signal.entryPrice') }}</span>
        <span class="price-value">${{ formatPrice(signal.price) }}</span>
      </div>
      <div class="price-item target">
        <span class="price-label">{{ $t('signal.targetPrice') }}</span>
        <span class="price-value">${{ formatPrice(signal.target) }}</span>
      </div>
      <div class="price-item stop">
        <span class="price-label">{{ $t('signal.stopLoss') }}</span>
        <span class="price-value">${{ formatPrice(signal.stopLoss) }}</span>
      </div>
    </div>

    <!-- === 底部：关注按钮 === -->
    <div class="card-actions">
      <button
        class="action-btn follow-btn"
        :class="{ following: isFollowed }"
        @click="$emit('toggleFollow')"
      >
        {{ isFollowed ? $t('signal.following') : $t('signal.follow') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface MockSignal {
  id: number
  strategy: string
  asset: string
  direction: 'long' | 'short'
  confidence: number
  price: number
  target: number
  stopLoss: number
  winRate?: number
}

const props = defineProps<{
  signal: MockSignal
  strategyHue?: string
  isFollowed?: boolean
}>()

defineEmits<{
  'toggleFollow': []
}>()

const { t } = useI18n()

const strategyLabelKeys: Record<string, string> = {
  '动量突破': 'strategy.breakout',
  '均值回归': 'strategy.meanReversion',
  '趋势跟踪': 'strategy.trend',
  '网格交易': 'strategy.grid',
}
function strategyLabel(strategy: string): string {
  return t(strategyLabelKeys[strategy] || strategy)
}

const borderTopStyle = computed(() => {
  if (!props.strategyHue) return {}
  return { borderTop: `3px solid ${props.strategyHue}` }
})

function formatPrice(n: number): string {
  if (n >= 1) return n.toLocaleString()
  return n.toFixed(4)
}

</script>

<style scoped>
/* ===== 卡片容器 ===== */
.signal-card {
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  transition: all 0.1s ease;
  display: flex;
  flex-direction: column;
}
.signal-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: 4px 4px 0 var(--border-color);
  border-color: var(--text-primary);
}

/* 已关注高亮 */
.signal-card.followed {
  border-color: var(--success-color);
}

/* ===== 顶部：标的 + 方向 ===== */
.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px 8px;
}

.asset-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.02em;
}

.direction-badge {
  padding: 3px 12px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  line-height: 1.4;
}
.direction-badge.long {
  background: rgba(0, 255, 65, 0.12);
  color: var(--success-color);
  border: 1px solid rgba(0, 255, 65, 0.35);
}
.direction-badge.short {
  background: rgba(255, 51, 51, 0.12);
  color: var(--danger-color);
  border: 1px solid rgba(255, 51, 51, 0.35);
}

/* ===== 策略 + 胜率 ===== */
.card-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 18px 10px;
  border-bottom: 1px solid var(--border-color);
}

.strategy-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border: 1px solid;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  line-height: 1.4;
}

.meta-stat {
  font-size: 11px;
  color: var(--text-secondary);
  letter-spacing: 0.02em;
}
.meta-stat strong {
  color: var(--text-primary);
  font-weight: 700;
}

/* ===== 核心价格数据 ===== */
.card-prices {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0;
  padding: 12px 18px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.price-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 4px 0;
  border-right: 1px solid var(--border-color);
}
.price-item:last-child {
  border-right: none;
}

.price-label {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.price-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-mono, monospace);
}

.price-item.target .price-value {
  color: var(--success-color);
}

.price-item.stop .price-value {
  color: var(--danger-color);
}

/* ===== 底部操作按钮 ===== */
.card-actions {
  display: flex;
  gap: 0;
}

.action-btn {
  width: 100%;
  padding: 10px;
  border: none;
  border-top: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  letter-spacing: 0.04em;
  transition: all 0.12s ease;
  text-transform: uppercase;
}
.follow-btn:hover {
  background: var(--success-color);
  color: var(--bg-primary);
}
.follow-btn.following {
  color: var(--success-color);
}
.follow-btn.following:hover {
  background: var(--danger-color);
  color: white;
}
</style>
