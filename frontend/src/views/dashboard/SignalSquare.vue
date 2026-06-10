<template>
  <div class="signal-square">
    <div class="page-title">&gt; 信号广场</div>

    <!-- My Follows Panel -->
    <div class="panel" v-if="followedSignals.length">
      <div class="panel-header">
        <span class="panel-title">&gt; 我的关注 ({{ followedSignals.length }})</span>
        <button class="clear-btn" @click="clearAllFollows">取消全部关注</button>
      </div>
      <div class="panel-body">
        <div class="followed-grid">
          <div v-for="s in followedSignals" :key="s.id" class="signal-card followed">
            <div class="card-top">
              <span class="card-strategy">{{ s.strategy }}</span>
              <span class="card-confidence" :class="confidenceClass(s.confidence)">{{ s.confidence }}%</span>
            </div>
            <div class="card-asset">
              <span class="symbol">{{ s.asset }}</span>
              <span class="direction" :class="s.direction">{{ s.direction === 'long' ? '▲ 做多' : '▼ 做空' }}</span>
            </div>
            <div class="card-body">
              <div class="card-row">
                <span class="row-label">入场价格</span>
                <span class="row-value">${{ toLocale(s.price) }}</span>
              </div>
              <div class="card-row">
                <span class="row-label">目标价格</span>
                <span class="row-value positive">${{ toLocale(s.target) }}</span>
              </div>
              <div class="card-row">
                <span class="row-label">止损价格</span>
                <span class="row-value negative">${{ toLocale(s.stopLoss) }}</span>
              </div>
            </div>
            <button class="follow-btn unfollow" @click="toggleFollow(s.id)">取消关注</button>
          </div>
        </div>
      </div>
    </div>

    <div class="filters">
      <button
        v-for="f in filters"
        :key="f.key"
        class="filter-btn"
        :class="{ active: activeFilter === f.key }"
        @click="activeFilter = f.key"
      >
        {{ f.label }}
      </button>
    </div>

    <div class="signals-grid">
      <div v-for="s in filteredSignals" :key="s.id" class="signal-card" :class="{ isFollowed: followedSet.has(s.id) }">
        <div class="card-top">
          <span class="card-strategy">{{ s.strategy }}</span>
          <span class="card-confidence" :class="confidenceClass(s.confidence)">{{ s.confidence }}%</span>
        </div>
        <div class="card-asset">
          <span class="symbol">{{ s.asset }}</span>
          <span class="direction" :class="s.direction">{{ s.direction === 'long' ? '▲ 做多' : '▼ 做空' }}</span>
        </div>
        <div class="card-body">
          <div class="card-row">
            <span class="row-label">入场价格</span>
            <span class="row-value">${{ toLocale(s.price) }}</span>
          </div>
          <div class="card-row">
            <span class="row-label">目标价格</span>
            <span class="row-value positive">${{ toLocale(s.target) }}</span>
          </div>
          <div class="card-row">
            <span class="row-label">止损价格</span>
            <span class="row-value negative">${{ toLocale(s.stopLoss) }}</span>
          </div>
        </div>
        <button
          class="follow-btn"
          :class="{ following: followedSet.has(s.id) }"
          @click="toggleFollow(s.id)"
        >
          {{ followedSet.has(s.id) ? '已关注' : '+ 关注信号' }}
        </button>
      </div>
      <div v-if="!filteredSignals.length" class="empty">
        暂无匹配信号
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { signals } from '@/data/mockData'

const activeFilter = ref('all')
const followIds = ref<Set<number>>(new Set())

const filters = [
  { key: 'all', label: '全部' },
  { key: '动量突破', label: '动量' },
  { key: '均值回归', label: '回归' },
  { key: '趋势跟踪', label: '趋势' },
  { key: '网格交易', label: '网格' },
]

const filteredSignals = computed(() => {
  if (activeFilter.value === 'all') return signals
  return signals.filter(s => s.strategy === activeFilter.value)
})

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
  if (confirm('确定取消全部关注吗？')) {
    followIds.value = new Set()
  }
}

function toLocale(n: number): string {
  return n.toLocaleString()
}

function confidenceClass(score: number): string {
  if (score >= 80) return 'high'
  if (score >= 65) return 'medium'
  return 'low'
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

/* My Follows Section */
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

/* Filters */
.filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 6px 16px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  transition: all 0.1s ease;
}
.filter-btn:hover {
  background: var(--bg-secondary);
}
.filter-btn.active {
  background: var(--text-primary);
  color: var(--bg-primary);
}

/* Signal Grid */
.signals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.signal-card {
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
  transition: all 0.1s ease;
}
.signal-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: 4px 4px 0 var(--border-color);
}
.signal-card.isFollowed {
  border-color: var(--success-color);
}
.signal-card.followed {
  border-color: var(--success-color);
  background: rgba(0, 255, 65, 0.02);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.card-strategy {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--text-secondary);
}

.card-confidence {
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid currentColor;
}
.card-confidence.high { color: var(--success-color); }
.card-confidence.medium { color: var(--text-primary); }
.card-confidence.low { color: var(--text-secondary); }

.card-asset {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border-color);
}

.symbol {
  font-size: 16px;
  font-weight: 700;
}

.direction {
  font-size: 12px;
  font-weight: 600;
}
.direction.long { color: var(--success-color); }
.direction.short { color: var(--danger-color); }

.card-body {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.card-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.row-label {
  color: var(--text-secondary);
}

.row-value {
  font-weight: 600;
}
.row-value.positive { color: var(--success-color); }
.row-value.negative { color: var(--danger-color); }

.follow-btn {
  width: 100%;
  padding: 10px;
  border: none;
  border-top: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.follow-btn:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}
.follow-btn.following {
  color: var(--success-color);
  border-top-color: var(--success-color);
}
.follow-btn.following:hover {
  background: var(--danger-color);
  color: white;
  border-top-color: var(--danger-color);
}
.follow-btn.unfollow {
  color: var(--danger-color);
  border-top-color: var(--danger-color);
}
.follow-btn.unfollow:hover {
  background: var(--danger-color);
  color: white;
}

.empty {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
  font-size: 14px;
}
</style>
