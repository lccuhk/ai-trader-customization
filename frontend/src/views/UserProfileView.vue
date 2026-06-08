<template>
  <div class="user-profile-view">
    <div v-if="socialStore.loading" class="loading">
      加载中...
    </div>

    <div v-else-if="socialStore.error" class="error">
      {{ socialStore.error }}
    </div>

    <div v-else-if="socialStore.userProfile" class="profile-content">
      <div class="profile-header">
        <div class="avatar-section">
          <div class="avatar">
            {{ socialStore.userProfile.display_name?.charAt(0) || socialStore.userProfile.username?.charAt(0) }}
          </div>
          <div class="user-info">
            <h1>{{ socialStore.userProfile.display_name || socialStore.userProfile.username }}</h1>
            <p class="username">@{{ socialStore.userProfile.username }}</p>
            <p class="bio" v-if="socialStore.userProfile.bio">{{ socialStore.userProfile.bio }}</p>
            <div class="user-meta" v-if="socialStore.userProfile.location || socialStore.userProfile.website">
              <span v-if="socialStore.userProfile.location">📍 {{ socialStore.userProfile.location }}</span>
              <a v-if="socialStore.userProfile.website" :href="socialStore.userProfile.website" target="_blank">
                🔗 {{ socialStore.userProfile.website }}
              </a>
            </div>
          </div>
        </div>

        <div class="profile-actions" v-if="currentUserId !== socialStore.userProfile.id">
          <button 
            class="follow-btn" 
            :class="{ following: socialStore.userProfile.is_following }"
            @click="toggleFollow"
          >
            {{ socialStore.userProfile.is_following ? '已关注' : '关注' }}
          </button>
          <button class="message-btn" @click="sendMessage">
            私信
          </button>
        </div>
      </div>

      <div class="stats-row">
        <div class="stat">
          <span class="stat-value">{{ socialStore.userProfile.follower_count || 0 }}</span>
          <span class="stat-label">粉丝</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ socialStore.userProfile.following_count || 0 }}</span>
          <span class="stat-label">关注</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ socialStore.userProfile.signal_count || 0 }}</span>
          <span class="stat-label">信号</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ socialStore.userProfile.total_trades || 0 }}</span>
          <span class="stat-label">交易</span>
        </div>
        <div class="stat" v-if="socialStore.userProfile.win_rate !== undefined">
          <span class="stat-value">{{ socialStore.userProfile.win_rate.toFixed(2) }}%</span>
          <span class="stat-label">胜率</span>
        </div>
        <div class="stat" v-if="socialStore.userProfile.total_pnl !== undefined">
          <span class="stat-value" :class="{ positive: socialStore.userProfile.total_pnl >= 0 }">
            {{ socialStore.userProfile.total_pnl >= 0 ? '+' : '' }}${{ socialStore.userProfile.total_pnl.toLocaleString() }}
          </span>
          <span class="stat-label">总盈亏</span>
        </div>
      </div>

      <div class="profile-tabs">
        <button 
          :class="{ active: activeTab === 'signals' }"
          @click="activeTab = 'signals'"
        >
          发布的信号
        </button>
        <button 
          :class="{ active: activeTab === 'about' }"
          @click="activeTab = 'about'"
        >
          关于
        </button>
      </div>

      <div class="tab-content">
        <div v-if="activeTab === 'signals'" class="signals-list">
          <div v-if="!userSignals || userSignals.length === 0" class="empty-state">
            暂无公开信号
          </div>
          <div 
            v-for="signal in userSignals" 
            :key="signal.id" 
            class="signal-card"
            @click="goToSignal(signal.id)"
          >
            <div class="signal-header">
              <div class="signal-symbols">
                <span v-for="symbol in signal.symbols" :key="symbol" class="symbol-tag">
                  {{ symbol }}
                </span>
              </div>
              <span class="signal-direction" :class="signal.direction">
                {{ signal.direction === 'long' ? '做多' : '做空' }}
              </span>
            </div>
            <h3 class="signal-title">{{ signal.title }}</h3>
            <div class="signal-stats">
              <span class="status" :class="signal.status">
                {{ getStatusText(signal.status) }}
              </span>
              <span class="pnl" v-if="signal.pnl !== undefined" :class="{ positive: signal.pnl >= 0 }">
                {{ signal.pnl >= 0 ? '+' : '' }}{{ signal.pnl_percent?.toFixed(2) }}%
              </span>
            </div>
            <div class="signal-meta">
              <span>{{ formatTime(signal.created_at) }}</span>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'about'" class="about-section">
          <div class="about-item">
            <span class="label">加入时间</span>
            <span class="value">{{ formatDate(socialStore.userProfile.created_at) }}</span>
          </div>
          <div class="about-item" v-if="socialStore.userProfile.last_login_at">
            <span class="label">最后活跃</span>
            <span class="value">{{ formatDate(socialStore.userProfile.last_login_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSocialStore } from '@/stores/social'
import { useUserStore } from '@/stores/user'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const router = useRouter()
const socialStore = useSocialStore()
const userStore = useUserStore()
const toast = useToast()

const activeTab = ref('signals')
const userSignals = ref<any[]>([])

const currentUserId = computed(() => userStore.user?.id)

async function loadProfile() {
  const userId = parseInt(route.params.id as string)
  if (userId) {
    const response = await socialStore.loadUserProfile(userId)
    if (response.success && response.data) {
      userSignals.value = response.data.signals
    }
  }
}

async function toggleFollow() {
  if (!socialStore.userProfile) return

  try {
    if (socialStore.userProfile.is_following) {
      await socialStore.unfollowUser(socialStore.userProfile.id)
      toast.success('已取消关注')
    } else {
      await socialStore.followUser(socialStore.userProfile.id)
      toast.success('关注成功')
    }
  } catch (e: any) {
    toast.error(e.message || '操作失败')
  }
}

function sendMessage() {
  if (socialStore.userProfile) {
    router.push(`/messages/${socialStore.userProfile.id}`)
  }
}

function goToSignal(signalId: number) {
  router.push(`/signal/${signalId}`)
}

function getStatusText(status: string) {
  const statusMap: Record<string, string> = {
    active: '进行中',
    closed: '已平仓',
    partial: '部分平仓',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

function formatTime(time: string) {
  return new Date(time).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatDate(time: string | undefined) {
  if (!time) return '-'
  return new Date(time).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.user-profile-view {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.loading, .error {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
}

.error {
  color: var(--danger);
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  gap: 24px;
}

.avatar-section {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}

.user-info h1 {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.username {
  color: var(--text-secondary);
  margin: 0 0 12px 0;
}

.bio {
  color: var(--text-primary);
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.user-meta {
  display: flex;
  gap: 16px;
  color: var(--text-secondary);
  font-size: 14px;
}

.user-meta a {
  color: var(--primary);
  text-decoration: none;
}

.profile-actions {
  display: flex;
  gap: 12px;
}

.follow-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--primary);
  color: white;
}

.follow-btn.following {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.message-btn {
  padding: 10px 24px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.message-btn:hover {
  background: var(--bg-secondary);
}

.stats-row {
  display: flex;
  gap: 32px;
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  margin-bottom: 24px;
  overflow-x: auto;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-value.positive {
  color: var(--success);
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.profile-tabs {
  display: flex;
  gap: 8px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.profile-tabs button {
  padding: 12px 24px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 14px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.profile-tabs button.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}

.tab-content {
  min-height: 300px;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
}

.signals-list {
  display: grid;
  gap: 16px;
}

.signal-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.signal-card:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
}

.signal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.signal-symbols {
  display: flex;
  gap: 6px;
}

.symbol-tag {
  padding: 4px 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  font-size: 12px;
  color: var(--text-primary);
}

.signal-direction {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.signal-direction.long {
  background: rgba(34, 197, 94, 0.1);
  color: var(--success);
}

.signal-direction.short {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
}

.signal-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.signal-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
}

.status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status.active {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status.closed {
  background: rgba(156, 163, 175, 0.1);
  color: #9ca3af;
}

.pnl {
  font-weight: 600;
  font-size: 14px;
}

.pnl.positive {
  color: var(--success);
}

.signal-meta {
  color: var(--text-secondary);
  font-size: 13px;
}

.about-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.about-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.about-item:last-child {
  border-bottom: none;
}

.about-item .label {
  color: var(--text-secondary);
}

.about-item .value {
  color: var(--text-primary);
  font-weight: 500;
}

.positive {
  color: var(--success);
}
</style>
