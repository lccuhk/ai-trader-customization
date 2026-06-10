<template>
  <div class="signal-card" @click="handleCardClick">
    <div class="card-header">
      <div class="agent-info">
        <span class="agent-avatar">{{ signal.agent_name?.[0] || 'A' }}</span>
        <div class="agent-meta">
          <span class="agent-name">{{ signal.agent_name }}</span>
          <span class="signal-time">{{ formatTime(signal.created_at) }}</span>
        </div>
      </div>
      <div class="signal-actions">
        <button
          class="action-btn"
          :class="{ followed: signal.is_following }"
          @click.stop="handleFollow"
        >
          {{ signal.is_following ? $t('signal.following') : $t('signal.follow') }}
        </button>
      </div>
    </div>

    <h3 class="signal-title">{{ signal.title }}</h3>
    <p class="signal-content">{{ signal.content }}</p>

    <div class="signal-tags" v-if="signal.symbols?.length">
      <span class="tag" v-for="symbol in signal.symbols" :key="symbol">{{ symbol }}</span>
    </div>

    <div class="card-footer">
      <div class="signal-stats">
        <span class="stat">
          <span class="stat-icon">👍</span>
          <span class="stat-value">{{ signal.likes || 0 }}</span>
        </span>
        <span class="stat">
          <span class="stat-icon">💬</span>
          <span class="stat-value">{{ signal.reply_count || 0 }}</span>
        </span>
        <span class="stat">
          <span class="stat-icon">👁️</span>
          <span class="stat-value">{{ signal.views || 0 }}</span>
        </span>
      </div>
      <div class="signal-type" :class="signal.message_type">
        {{ $t('signal.' + signal.message_type) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import { useSignalStore } from '@/stores/signal'
import type { Signal } from '@/types'

dayjs.extend(relativeTime)

const props = defineProps<{
  signal: Signal
}>()

const emit = defineEmits<{
  (e: 'follow', signalId: number): void
}>()

const router = useRouter()
const signalStore = useSignalStore()

function formatTime(date: string | undefined) {
  if (!date) return ''
  return dayjs(date).fromNow()
}

function handleCardClick() {
  router.push(`/signal/${props.signal.id}`)
}

async function handleFollow() {
  await signalStore.toggleFollow(props.signal.id)
  emit('follow', props.signal.id)
}
</script>

<style scoped>
/* IT 极简风格信号卡片 */
.signal-card {
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  padding: 16px;
  cursor: pointer;
  transition: all 0.1s ease;
  position: relative;
}

.signal-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: var(--border-light);
  transition: background 0.1s ease;
}

.signal-card:hover {
  border-color: var(--text-primary);
  box-shadow: 4px 4px 0 var(--border-color);
  transform: translate(-2px, -2px);
}

.signal-card:hover::before {
  background: var(--success-color);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  padding-left: 8px;
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.agent-avatar {
  width: 32px;
  height: 32px;
  border: 2px solid var(--border-color);
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
  font-weight: 700;
  font-size: 13px;
}

.agent-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.agent-name {
  font-weight: 700;
  color: var(--text-primary);
  font-size: 13px;
  letter-spacing: 0.02em;
}

.signal-time {
  font-size: 11px;
  color: var(--text-muted);
  font-family: inherit;
}

.signal-time::before {
  content: '@ ';
  color: var(--success-color);
}

.action-btn {
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-secondary);
  transition: all 0.1s ease;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  font-family: inherit;
}

.action-btn:hover {
  border-color: var(--success-color);
  color: var(--success-color);
}

.action-btn.followed {
  background: var(--success-color);
  border-color: var(--success-color);
  color: var(--bg-primary);
}

.signal-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  line-height: 1.4;
  padding-left: 8px;
}

.signal-title::before {
  content: '> ';
  color: var(--success-color);
  font-weight: 700;
}

.signal-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  padding-left: 8px;
}

.signal-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
  padding-left: 8px;
}

.tag {
  padding: 3px 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  font-size: 11px;
  color: var(--text-primary);
  font-weight: 600;
  font-family: inherit;
  letter-spacing: 0.02em;
}

.tag::before {
  content: '$';
  color: var(--success-color);
  margin-right: 2px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid var(--border-light);
  padding-left: 8px;
}

.signal-stats {
  display: flex;
  gap: 16px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 500;
}

.stat-icon {
  font-size: 12px;
}

.signal-type {
  padding: 3px 8px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
}

.signal-type.long {
  border-color: var(--success-color);
  color: var(--success-color);
}

.signal-type.long::before {
  content: '▲ ';
}

.signal-type.short {
  border-color: var(--danger-color);
  color: var(--danger-color);
}

.signal-type.short::before {
  content: '▼ ';
}

.signal-type.alert {
  border-color: var(--warning-color);
  color: var(--warning-color);
}

.signal-type.info,
.signal-type.analysis {
  border-color: var(--text-primary);
  color: var(--text-primary);
}
</style>
