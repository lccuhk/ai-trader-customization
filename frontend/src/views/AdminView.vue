<template>
  <div class="admin-view">
    <div class="container mx-auto px-4 py-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">管理员后台</h1>
        <p class="text-gray-600">平台管理和数据分析中心</p>
      </div>

      <div class="mb-6">
        <div class="flex border-b border-gray-200">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            @click="activeTab = tab.key"
            class="px-6 py-3 font-medium text-sm border-b-2 transition-colors"
            :class="activeTab === tab.key ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <div v-if="activeTab === 'overview'">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500">总用户数</p>
                <p class="text-2xl font-bold text-gray-900">{{ adminStats?.overview.total_users || 0 }}</p>
              </div>
              <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
            </div>
            <p class="text-sm text-green-600 mt-2">+{{ adminStats?.new_users_today || 0 }} 今日新增</p>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500">总信号数</p>
                <p class="text-2xl font-bold text-gray-900">{{ adminStats?.overview.total_signals || 0 }}</p>
              </div>
              <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
            <p class="text-sm text-green-600 mt-2">+{{ adminStats?.today.new_signals || 0 }} 今日新增</p>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500">总交易量</p>
                <p class="text-2xl font-bold text-gray-900">{{ adminStats?.total_trades || 0 }}</p>
              </div>
              <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
            </div>
            <p class="text-sm text-gray-500 mt-2">${{ adminStats?.trading.total_volume?.toLocaleString() || 0 }} 交易额</p>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500">待审核信号</p>
                <p class="text-2xl font-bold text-yellow-600">{{ adminStats?.pending_moderation || 0 }}</p>
              </div>
              <div class="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
                <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
            </div>
            <p class="text-sm text-yellow-600 mt-2">需要及时处理</p>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">用户增长趋势</h3>
            <div class="h-64 flex items-end justify-around">
              <div v-for="(day, index) in userGrowthData" :key="index" class="flex flex-col items-center">
                <div
                  class="w-8 bg-blue-500 rounded-t transition-all hover:bg-blue-600"
                  :style="{ height: (day.users / maxUserGrowth) * 200 + 'px' }"
                ></div>
                <span class="text-xs text-gray-500 mt-2">{{ day.date }}</span>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">最近操作日志</h3>
            <div class="space-y-3">
              <div v-for="log in recentLogs" :key="log.id" class="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div
                  class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                  :class="{
                    'bg-blue-100': log.action === 'create',
                    'bg-yellow-100': log.action === 'update',
                    'bg-red-100': log.action === 'delete'
                  }"
                >
                  <svg
                    class="w-4 h-4"
                    :class="{
                      'text-blue-600': log.action === 'create',
                      'text-yellow-600': log.action === 'update',
                      'text-red-600': log.action === 'delete'
                    }"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900">{{ log.action }}</p>
                  <p class="text-xs text-gray-500">{{ log.admin_name }} · {{ formatDate(log.created_at) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'users'">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-semibold text-gray-900">用户管理</h3>
            <div class="flex gap-4">
              <input
                v-model="userSearch"
                type="text"
                placeholder="搜索用户..."
                class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <select
                v-model="userFilter"
                class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">全部用户</option>
                <option value="active">活跃用户</option>
                <option value="inactive">未激活</option>
                <option value="verified">已认证</option>
              </select>
            </div>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="border-b border-gray-200">
                  <th class="text-left py-3 px-4 text-sm font-medium text-gray-500">用户</th>
                  <th class="text-left py-3 px-4 text-sm font-medium text-gray-500">邮箱</th>
                  <th class="text-left py-3 px-4 text-sm font-medium text-gray-500">状态</th>
                  <th class="text-left py-3 px-4 text-sm font-medium text-gray-500">注册时间</th>
                  <th class="text-left py-3 px-4 text-sm font-medium text-gray-500">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in filteredUsers" :key="user.id" class="border-b border-gray-100 hover:bg-gray-50">
                  <td class="py-3 px-4">
                    <div class="flex items-center gap-3">
                      <img :src="user.avatar_url || 'https://picsum.photos/40/40'" class="w-10 h-10 rounded-full" />
                      <div>
                        <p class="font-medium text-gray-900">{{ user.username }}</p>
                        <p class="text-sm text-gray-500">{{ user.role }}</p>
                      </div>
                    </div>
                  </td>
                  <td class="py-3 px-4 text-sm text-gray-600">{{ user.email }}</td>
                  <td class="py-3 px-4">
                    <span
                      class="px-2 py-1 rounded-full text-xs font-medium"
                      :class="{
                        'bg-green-100 text-green-800': user.is_active,
                        'bg-gray-100 text-gray-800': !user.is_active
                      }"
                    >
                      {{ user.is_active ? '活跃' : '未激活' }}
                    </span>
                  </td>
                  <td class="py-3 px-4 text-sm text-gray-600">{{ formatDate(user.created_at) }}</td>
                  <td class="py-3 px-4">
                    <div class="flex gap-2">
                      <button @click="viewUser(user)" class="text-blue-600 hover:text-blue-800 text-sm">查看</button>
                      <button @click="editUser(user)" class="text-yellow-600 hover:text-yellow-800 text-sm">编辑</button>
                      <button @click="banUser(user)" class="text-red-600 hover:text-red-800 text-sm">封禁</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'moderation'">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-6">内容审核</h3>
          <div class="space-y-4">
            <div v-for="signal in pendingSignals" :key="signal.id" class="border border-gray-200 rounded-lg p-4">
              <div class="flex items-start justify-between mb-3">
                <div class="flex items-center gap-3">
                  <img :src="signal.user?.avatar_url || 'https://picsum.photos/40/40'" class="w-10 h-10 rounded-full" />
                  <div>
                    <p class="font-medium text-gray-900">{{ signal.user?.username }}</p>
                    <p class="text-sm text-gray-500">{{ formatDate(signal.created_at) }}</p>
                  </div>
                </div>
                <span class="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-medium">
                  待审核
                </span>
              </div>
              <h4 class="font-medium text-gray-900 mb-2">{{ signal.title }}</h4>
              <p class="text-sm text-gray-600 mb-3">{{ signal.description }}</p>
              <div class="flex items-center gap-4 mb-3">
                <span class="text-sm text-gray-500">{{ signal.symbol }}</span>
                <span class="text-sm" :class="signal.direction === 'long' ? 'text-green-600' : 'text-red-600'">
                  {{ signal.direction === 'long' ? '做多' : '做空' }}
                </span>
                <span class="text-sm text-gray-500">入场: {{ signal.entry_price }}</span>
              </div>
              <div class="flex gap-3">
                <button
                  @click="moderateSignal(signal.id, 'approved')"
                  class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                >
                  批准
                </button>
                <button
                  @click="moderateSignal(signal.id, 'rejected')"
                  class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
                >
                  拒绝
                </button>
                <button
                  @click="moderateSignal(signal.id, 'deleted')"
                  class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm"
                >
                  删除
                </button>
              </div>
            </div>
          </div>
          <div v-if="pendingSignals.length === 0" class="text-center py-12 text-gray-500">
            暂无待审核内容
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'analytics'">
        <div class="space-y-6">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">漏斗分析</h3>
            <div class="space-y-4">
              <div v-for="step in funnelData[0]?.steps || []" :key="step.name" class="flex items-center gap-4">
                <div class="w-32 text-sm text-gray-600">{{ step.name }}</div>
                <div class="flex-1">
                  <div class="h-8 bg-gray-100 rounded-lg overflow-hidden">
                    <div
                      class="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg transition-all"
                      :style="{ width: step.conversion + '%' }"
                    ></div>
                  </div>
                </div>
                <div class="w-24 text-right">
                  <span class="font-medium text-gray-900">{{ step.count }}</span>
                  <span class="text-sm text-gray-500 ml-2">{{ step.conversion.toFixed(1) }}%</span>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">留存分析</h3>
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead>
                  <tr class="border-b border-gray-200">
                    <th class="text-left py-3 px-4 text-sm font-medium text-gray-500"> cohort</th>
                    <th class="text-center py-3 px-4 text-sm font-medium text-gray-500">D1</th>
                    <th class="text-center py-3 px-4 text-sm font-medium text-gray-500">D7</th>
                    <th class="text-center py-3 px-4 text-sm font-medium text-gray-500">D30</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="cohort in retentionData" :key="cohort.week" class="border-b border-gray-100">
                    <td class="py-3 px-4 text-sm font-medium text-gray-900">{{ cohort.week }}</td>
                    <td class="py-3 px-4 text-center">
                      <span
                        class="px-2 py-1 rounded text-sm"
                        :class="cohort.d1 >= 50 ? 'bg-green-100 text-green-800' : cohort.d1 >= 30 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'"
                      >
                        {{ cohort.d1.toFixed(1) }}%
                      </span>
                    </td>
                    <td class="py-3 px-4 text-center">
                      <span
                        class="px-2 py-1 rounded text-sm"
                        :class="cohort.d7 >= 30 ? 'bg-green-100 text-green-800' : cohort.d7 >= 15 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'"
                      >
                        {{ cohort.d7.toFixed(1) }}%
                      </span>
                    </td>
                    <td class="py-3 px-4 text-center">
                      <span
                        class="px-2 py-1 rounded text-sm"
                        :class="cohort.d30 >= 15 ? 'bg-green-100 text-green-800' : cohort.d30 >= 5 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'"
                      >
                        {{ cohort.d30.toFixed(1) }}%
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'settings'">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-6">系统设置</h3>
          <div class="space-y-6">
            <div>
              <h4 class="font-medium text-gray-900 mb-3">平台配置</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">平台名称</label>
                  <input
                    v-model="settings.platform_name"
                    type="text"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">支持邮箱</label>
                  <input
                    v-model="settings.support_email"
                    type="email"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </div>
            <div>
              <h4 class="font-medium text-gray-900 mb-3">功能开关</h4>
              <div class="space-y-3">
                <label class="flex items-center gap-3">
                  <input v-model="settings.enable_registration" type="checkbox" class="w-4 h-4 text-blue-600 rounded" />
                  <span class="text-sm text-gray-700">允许新用户注册</span>
                </label>
                <label class="flex items-center gap-3">
                  <input v-model="settings.enable_trading" type="checkbox" class="w-4 h-4 text-blue-600 rounded" />
                  <span class="text-sm text-gray-700">启用交易功能</span>
                </label>
                <label class="flex items-center gap-3">
                  <input v-model="settings.enable_moderation" type="checkbox" class="w-4 h-4 text-blue-600 rounded" />
                  <span class="text-sm text-gray-700">启用内容审核</span>
                </label>
                <label class="flex items-center gap-3">
                  <input v-model="settings.maintenance_mode" type="checkbox" class="w-4 h-4 text-blue-600 rounded" />
                  <span class="text-sm text-gray-700">维护模式</span>
                </label>
              </div>
            </div>
            <div class="flex gap-4">
              <button
                @click="saveSettings"
                class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                保存设置
              </button>
              <button
                @click="sendSystemNotification"
                class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                发送系统通知
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { adminService } from '../services/admin'
import type { User, AdminStats, AdminAction, FunnelAnalysis, RetentionAnalysis } from '../types'

const activeTab = ref('overview')
const userSearch = ref('')
const userFilter = ref('all')

const tabs = [
  { key: 'overview', label: '概览' },
  { key: 'users', label: '用户管理' },
  { key: 'moderation', label: '内容审核' },
  { key: 'analytics', label: '数据分析' },
  { key: 'settings', label: '系统设置' }
]

const adminStats = ref<AdminStats | null>(null)
const users = ref<User[]>([])
const pendingSignals = ref<any[]>([])
const recentLogs = ref<AdminAction[]>([])
const funnelData = ref<FunnelAnalysis[]>([])
const retentionData = ref<RetentionAnalysis[]>([])

const settings = ref({
  platform_name: 'Trading Agent',
  support_email: 'support@tradingagent.com',
  enable_registration: true,
  enable_trading: true,
  enable_moderation: true,
  maintenance_mode: false
})

const userGrowthData = ref([
  { date: '周一', users: 45 },
  { date: '周二', users: 52 },
  { date: '周三', users: 38 },
  { date: '周四', users: 65 },
  { date: '周五', users: 78 },
  { date: '周六', users: 92 },
  { date: '周日', users: 85 }
])

const maxUserGrowth = computed(() => Math.max(...userGrowthData.value.map(d => d.users)))

const filteredUsers = computed(() => {
  let result = users.value
  if (userSearch.value) {
    const search = userSearch.value.toLowerCase()
    result = result.filter(u =>
      u.username.toLowerCase().includes(search) ||
      u.email.toLowerCase().includes(search)
    )
  }
  if (userFilter.value === 'active') {
    result = result.filter(u => u.is_active)
  } else if (userFilter.value === 'inactive') {
    result = result.filter(u => !u.is_active)
  } else if (userFilter.value === 'verified') {
    result = result.filter(u => u.is_verified)
  }
  return result
})

const getRetentionRate = (cohort: any, day: number): number => {
  const retention = cohort.retention?.find((r: any) => r.week === day)
  return retention?.rate || 0
}

const loadData = async () => {
  try {
    const [statsRes, usersRes, signalsRes, logsRes, funnelRes, retentionRes] = await Promise.all([
      adminService.getStats(),
      adminService.getUsers({}),
      adminService.getPendingModeration(),
      adminService.getRecentActions(),
      adminService.getFunnelAnalysis({}),
      adminService.getRetentionAnalysis({})
    ])
    adminStats.value = statsRes.data || null
    users.value = Array.isArray(usersRes.data) ? usersRes.data : (usersRes.data as any)?.items || []
    pendingSignals.value = signalsRes.data || []
    recentLogs.value = logsRes.data || []
    funnelData.value = Array.isArray(funnelRes.data) ? funnelRes.data : (funnelRes.data ? [funnelRes.data] : [])
    retentionData.value = Array.isArray(retentionRes.data) ? retentionRes.data : (retentionRes.data ? [retentionRes.data] : [])
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const moderateSignal = async (signalId: number, action: string) => {
  try {
    await adminService.moderateSignal(signalId, { action })
    pendingSignals.value = pendingSignals.value.filter(s => s.id !== signalId)
  } catch (error) {
    console.error('审核失败:', error)
  }
}

const viewUser = (user: User) => {
  console.log('查看用户:', user)
}

const editUser = (user: User) => {
  console.log('编辑用户:', user)
}

const banUser = (user: User) => {
  if (confirm(`确定要封禁用户 ${user.username} 吗？`)) {
    console.log('封禁用户:', user)
  }
}

const saveSettings = async () => {
  try {
    await adminService.updateSettings(settings.value)
    alert('设置保存成功')
  } catch (error) {
    console.error('保存设置失败:', error)
  }
}

const sendSystemNotification = async () => {
  const message = prompt('请输入系统通知内容：')
  if (message) {
    try {
      await adminService.sendSystemNotification({ message })
      alert('通知发送成功')
    } catch (error) {
      console.error('发送通知失败:', error)
    }
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  loadData()
})
</script>
