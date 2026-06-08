<template>
  <div class="profile-view">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="userStore.user" class="profile-content">
      <div class="profile-header">
        <div class="avatar-large">
          {{ userStore.user.display_name?.[0] || userStore.user.username?.[0] || 'U' }}
        </div>
        <div class="profile-info">
          <h1 class="profile-name">{{ userStore.user.display_name || userStore.user.username }}</h1>
          <p class="profile-username">@{{ userStore.user.username }}</p>
          <p class="profile-email">{{ userStore.user.email }}</p>
        </div>
      </div>

      <div class="profile-stats">
        <div class="stat-card">
          <span class="stat-value">{{ stats.signals_count || 0 }}</span>
          <span class="stat-label">发布信号</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ stats.following_count || 0 }}</span>
          <span class="stat-label">关注</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ stats.followers_count || 0 }}</span>
          <span class="stat-label">粉丝</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ stats.total_likes || 0 }}</span>
          <span class="stat-label">获赞</span>
        </div>
      </div>

      <div class="profile-sections">
        <div class="section-card">
          <h2 class="section-title">账户设置</h2>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-name">修改密码</span>
              <span class="setting-desc">定期更新密码以保护账户安全</span>
            </div>
            <button class="btn btn-outline" @click="showPasswordModal = true">修改</button>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-name">通知设置</span>
              <span class="setting-desc">管理接收哪些类型的通知</span>
            </div>
            <button class="btn btn-outline">设置</button>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-name">API 密钥</span>
              <span class="setting-desc">管理你的 API 访问密钥</span>
            </div>
            <button class="btn btn-outline">管理</button>
          </div>
        </div>

        <div class="section-card">
          <h2 class="section-title">我的信号</h2>
          <div v-if="userSignals.length === 0" class="empty-state">
            <p class="empty-text">📝 暂无发布的信号</p>
            <router-link to="/" class="btn btn-primary">去发布</router-link>
          </div>
          <div v-else class="user-signals">
            <div v-for="signal in userSignals" :key="signal.id" class="signal-item">
              <div class="signal-item-header">
                <span class="signal-type" :class="signal.message_type">
                  {{ getTypeLabel(signal.message_type) }}
                </span>
                <span class="signal-date">{{ formatDate(signal.created_at) }}</span>
              </div>
              <h3 class="signal-item-title">{{ signal.title }}</h3>
              <div class="signal-item-stats">
                <span>👍 {{ signal.likes || 0 }}</span>
                <span>💬 {{ signal.reply_count || 0 }}</span>
                <span>👁️ {{ signal.views || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showPasswordModal" class="modal-overlay" @click.self="showPasswordModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>修改密码</h3>
          <button class="close-btn" @click="showPasswordModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>当前密码</label>
            <input v-model="passwordForm.current" type="password" class="form-input" />
          </div>
          <div class="form-group">
            <label>新密码</label>
            <input v-model="passwordForm.new" type="password" class="form-input" />
          </div>
          <div class="form-group">
            <label>确认新密码</label>
            <input v-model="passwordForm.confirm" type="password" class="form-input" />
          </div>
          <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showPasswordModal = false">取消</button>
          <button class="btn btn-primary" :disabled="passwordSubmitting" @click="handleChangePassword">
            {{ passwordSubmitting ? '提交中...' : '确认修改' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import dayjs from 'dayjs'
import { useUserStore } from '@/stores/user'

import type { Signal } from '@/types'

const userStore = useUserStore()

const loading = ref(true)
const showPasswordModal = ref(false)
const passwordSubmitting = ref(false)
const passwordError = ref<string | null>(null)

const stats = reactive({
  signals_count: 0,
  following_count: 0,
  followers_count: 0,
  total_likes: 0
})

const userSignals = ref<Signal[]>([])

const passwordForm = reactive({
  current: '',
  new: '',
  confirm: ''
})

onMounted(async () => {
  await loadProfile()
})

async function loadProfile() {
  loading.value = true
  try {
    if (!userStore.user) {
      await userStore.fetchCurrentUser()
    }
    await loadUserStats()
    await loadUserSignals()
  } finally {
    loading.value = false
  }
}

async function loadUserStats() {
  try {
    const response = await fetch('/api/users/stats', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      }
    })
    const data = await response.json()
    if (data.success) {
      Object.assign(stats, data.data)
    }
  } catch (e) {
    console.error('加载用户统计失败', e)
  }
}

async function loadUserSignals() {
  try {
    const response = await fetch('/api/users/signals', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      }
    })
    const data = await response.json()
    if (data.success) {
      userSignals.value = data.signals || []
    }
  } catch (e) {
    console.error('加载用户信号失败', e)
  }
}

async function handleChangePassword() {
  if (!passwordForm.current || !passwordForm.new || !passwordForm.confirm) {
    passwordError.value = '请填写所有字段'
    return
  }
  
  if (passwordForm.new !== passwordForm.confirm) {
    passwordError.value = '两次输入的新密码不一致'
    return
  }
  
  if (passwordForm.new.length < 6) {
    passwordError.value = '新密码至少需要6位'
    return
  }
  
  passwordSubmitting.value = true
  passwordError.value = null
  
  try {
    const response = await fetch('/api/users/password', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify({
        current_password: passwordForm.current,
        new_password: passwordForm.new
      })
    })
    
    const data = await response.json()
    if (data.success) {
      showPasswordModal.value = false
      passwordForm.current = ''
      passwordForm.new = ''
      passwordForm.confirm = ''
      alert('密码修改成功！')
    } else {
      passwordError.value = data.message || '修改失败'
    }
  } catch (e: any) {
    passwordError.value = e.message || '修改失败'
  } finally {
    passwordSubmitting.value = false
  }
}

function getTypeLabel(type: string | undefined) {
  const labels: Record<string, string> = {
    'long': '做多',
    'short': '做空',
    'info': '资讯',
    'alert': '预警',
    'analysis': '分析'
  }
  return labels[type || 'info'] || type
}

function formatDate(date: string | undefined) {
  if (!date) return ''
  return dayjs(date).format('YYYY-MM-DD')
}
</script>

<style scoped>
.profile-view {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 20px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: var(--text-muted);
  font-size: 14px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;
  padding: 32px;
  background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-hover) 100%);
  border-radius: 16px;
  color: white;
}

.avatar-large {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  font-weight: 700;
  color: white;
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 4px 0;
}

.profile-username {
  font-size: 16px;
  opacity: 0.9;
  margin: 0 0 4px 0;
}

.profile-email {
  font-size: 14px;
  opacity: 0.8;
  margin: 0;
}

.profile-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
}

.profile-sections {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 20px 0;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--border-color);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-info {
  flex: 1;
}

.setting-name {
  display: block;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.setting-desc {
  font-size: 13px;
  color: var(--text-muted);
}

.btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--accent-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-hover);
}

.btn-outline {
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-outline:hover {
  background: var(--bg-secondary);
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-text {
  color: var(--text-muted);
  font-size: 14px;
  margin: 0 0 16px 0;
}

.user-signals {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.signal-item {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.signal-item:hover {
  background: var(--bg-primary);
  border: 1px solid var(--accent-color);
}

.signal-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.signal-type {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.signal-type.long {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.signal-type.short {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.signal-type.alert {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.signal-type.info,
.signal-type.analysis {
  background: rgba(99, 102, 241, 0.1);
  color: var(--accent-color);
}

.signal-date {
  font-size: 12px;
  color: var(--text-muted);
}

.signal-item-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.signal-item-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-muted);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: var(--bg-primary);
  border-radius: 16px;
  width: 100%;
  max-width: 450px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  color: var(--text-muted);
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.error-message {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-color);
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
    padding: 24px;
  }
  
  .profile-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
