<template>
  <aside class="quick-info" :class="{ collapsed: isCollapsed }">
    <button class="toggle-btn" @click="isCollapsed = !isCollapsed">
      {{ isCollapsed ? '◀' : '▶' }}
    </button>

    <div v-if="!isCollapsed" class="info-content">
      <div class="info-section">
        <div class="section-header">
          <span class="section-icon">📊</span>
          <span class="section-title">市场情绪</span>
        </div>
        <div class="sentiment-display">
          <div class="sentiment-score" :class="sentimentLevelClass">
            {{ data.marketSentiment.score }}
          </div>
          <div class="sentiment-details">
            <span class="sentiment-level" :class="sentimentLevelClass">{{ data.marketSentiment.level }}</span>
            <span class="sentiment-trend">{{ data.marketSentiment.trend }} →</span>
          </div>
        </div>
      </div>

      <div class="info-section">
        <div class="section-header">
          <span class="section-icon">⚠</span>
          <span class="section-title">当前预警</span>
        </div>
        <div class="alerts-list">
          <div
            v-for="alert in data.alerts"
            :key="alert.id"
            class="alert-item"
            :class="alert.type"
          >
            <span class="alert-dot">●</span>
            <span class="alert-text">{{ alert.message }}</span>
          </div>
        </div>
      </div>

      <div class="info-section">
        <div class="section-header">
          <span class="section-icon">🤖</span>
          <span class="section-title">AI 建议</span>
        </div>
        <div class="ai-one-liner">
          {{ data.aiOneLiner }}
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { quickInfo } from '@/data/mockData'

const isCollapsed = ref(false)
const data = quickInfo

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
  height: 100vh;
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
</style>
