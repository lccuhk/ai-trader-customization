<template>
  <div class="signal-square">
    <div class="page-title">&gt; {{ $t('nav.signalsSquare') }}</div>

    <!-- My Follows Panel -->
    <div class="panel" v-if="followedSignals.length">
      <div class="panel-header">
        <span class="panel-title">&gt; {{ $t('signal.myFollows') }} ({{ followedSignals.length }})</span>
        <button class="clear-btn" @click="clearAllFollows">{{ $t('signal.clearAll') }}</button>
      </div>
      <div class="panel-body">
        <div class="followed-grid">
          <StrategySignalCard
            v-for="s in followedSignals"
            :key="s.id + '-followed'"
            :signal="s"
            :is-followed="true"
            @toggle-follow="toggleFollow(s.id)"
          />
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <button
        v-for="f in filters"
        :key="f.key"
        class="filter-btn"
        :class="{ active: activeFilter === f.key }"
        @click="activeFilter = f.key"
      >
        {{ f.label || $t(f.labelKey) }}
      </button>
    </div>

    <!-- Signal Cards Grid -->
    <div class="cards-grid">
      <template v-for="(group, gIdx) in groupedSignals" :key="gIdx">
        <!-- Strategy group header -->
        <div v-if="groupedSignals.length > 1" class="group-label" :style="{ borderLeftColor: strategyColor(group.strategy) }">
          <span class="group-dot" :style="{ background: strategyColor(group.strategy) }"></span>
          {{ strategyLabel(group.strategy) }}
          <span class="group-count">{{ group.items.length }} {{ $t('signal.signals') }}</span>
        </div>
        <StrategySignalCard
          v-for="s in group.items"
          :key="s.id"
          :signal="s"
          :strategy-hue="strategyColor(s.strategy)"
          :is-followed="followedSet.has(s.id)"
          @toggle-follow="toggleFollow(s.id)"
        />
      </template>
      <div v-if="!filteredSignals.length" class="empty">
        {{ $t('signal.noMatch') }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { signals } from '@/data/mockData'
import StrategySignalCard from '@/components/StrategySignalCard.vue'

const { t } = useI18n()

const activeFilter = ref('all')
const followIds = ref<Set<number>>(new Set())

const filters = [
  { key: 'all', label: t('trading.filterAll') },
  { key: '动量突破', labelKey: 'strategy.breakout' },
  { key: '均值回归', labelKey: 'strategy.meanReversion' },
  { key: '趋势跟踪', labelKey: 'strategy.trend' },
  { key: '网格交易', labelKey: 'strategy.grid' },
]

// Filter by strategy
const filteredSignals = computed(() => {
  if (activeFilter.value === 'all') return signals
  return signals.filter(s => s.strategy === activeFilter.value)
})

// Group by strategy
interface SignalGroup {
  strategy: string
  items: typeof signals
}
const groupedSignals = computed(() => {
  if (activeFilter.value !== 'all') {
    return [{ strategy: activeFilter.value, items: filteredSignals.value }] as SignalGroup[]
  }
  const groups: Record<string, typeof signals> = {}
  for (const s of filteredSignals.value) {
    if (!groups[s.strategy]) groups[s.strategy] = []
    groups[s.strategy].push(s)
  }
  return Object.entries(groups).map(([strategy, items]) => ({ strategy, items })) as SignalGroup[]
})

// Strategy label mapping (mockData uses Chinese keys → locale lookup)
const strategyLabelKeys: Record<string, string> = {
  '动量突破': 'strategy.breakout',
  '均值回归': 'strategy.meanReversion',
  '趋势跟踪': 'strategy.trend',
  '网格交易': 'strategy.grid',
}
function strategyLabel(strategy: string): string {
  return t(strategyLabelKeys[strategy] || strategy)
}

// Strategy accent colors
const strategyColors: Record<string, string> = {
  '动量突破': '#00ff41',
  '均值回归': '#3399ff',
  '趋势跟踪': '#ff9900',
  '网格交易': '#aa66ff',
}

function strategyColor(strategy: string): string {
  return strategyColors[strategy] || '#666666'
}

// Follow logic
const followedSignals = computed(() => {
  return signals.filter(s => followIds.value.has(s.id))
})

const followedSet = computed(() => followIds.value)

function toggleFollow(id: number) {
  const newSet = new Set(followIds.value)
  if (newSet.has(id)) {
    newSet.delete(id)
  } else {
    newSet.add(id)
  }
  followIds.value = newSet
}

function clearAllFollows() {
  if (confirm(t('signal.confirmClearAll'))) {
    followIds.value = new Set()
  }
}
</script>

<style scoped>
.signal-square {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.05em;
}

/* ===== Follows Panel ===== */
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

.clear-btn {
  padding: 4px 10px;
  border: 2px solid var(--danger-color);
  background: transparent;
  color: var(--danger-color);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}
.clear-btn:hover {
  background: var(--danger-color);
  color: white;
}

.panel-body {
  padding: 16px;
}

.followed-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

/* ===== Filter Bar ===== */
.filter-bar {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 0;
  margin-bottom: 0;
}

.filter-btn {
  padding: 8px 20px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  transition: all 0.1s ease;
}
.filter-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}
.filter-btn.active {
  background: var(--bg-primary);
  color: var(--text-primary);
  border-bottom: 2px solid var(--bg-primary);
}

/* ===== Cards Grid ===== */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  align-items: start;
}

.group-label {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0 2px 10px;
  margin-bottom: -4px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  letter-spacing: 0.05em;
  border-left: 3px solid var(--border-color);
  text-transform: uppercase;
}

.group-dot {
  width: 8px;
  height: 8px;
  border: 1px solid var(--border-color);
  flex-shrink: 0;
}

.group-count {
  margin-left: auto;
  font-weight: 400;
  color: var(--text-secondary);
  opacity: 0.7;
}

.empty {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
  font-size: 14px;
}
</style>
