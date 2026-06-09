<template>
  <nav class="navbar">
    <div class="navbar-container">
      <!-- Logo -->
      <router-link to="/" class="navbar-logo">
        <span class="logo-bracket">[</span>
        <span class="logo-text">AI_TRADER</span>
        <span class="logo-bracket">]</span>
        <span class="logo-cursor">_</span>
      </router-link>

      <!-- 主导航菜单 -->
      <div class="navbar-menu" v-if="userStore.isLoggedIn">
        <!-- 交易 -->
        <router-link to="/trading" class="nav-link" :class="{ active: $route.name === 'Trading' }">
          <span class="nav-icon">📈</span>
          <span class="nav-text">{{ t('nav.trading') }}</span>
        </router-link>

        <!-- 信号广场 -->
        <router-link to="/" class="nav-link" :class="{ active: $route.name === 'Home' }">
          <span class="nav-icon">📡</span>
          <span class="nav-text">{{ t('nav.home') }}</span>
        </router-link>

        <!-- 策略中心 -->
        <div class="nav-dropdown">
          <button class="nav-link dropdown-toggle" :class="{ active: $route.path.startsWith('/strategies') }">
            <span class="nav-icon">🎯</span>
            <span class="nav-text">{{ t('nav.strategyCenter') }}</span>
            <span class="dropdown-arrow">▼</span>
          </button>
          <div class="dropdown-menu">
            <router-link to="/strategies" class="dropdown-item">
              <span>{{ t('nav.strategyManagement') }}</span>
            </router-link>
            <router-link to="/strategies/templates" class="dropdown-item">
              <span>{{ t('nav.strategyTemplates') }}</span>
            </router-link>
          </div>
        </div>

        <!-- 市场情报 -->
        <div class="nav-dropdown">
          <button class="nav-link dropdown-toggle" :class="{ active: $route.path.startsWith('/market') }">
            <span class="nav-icon">🌐</span>
            <span class="nav-text">{{ t('nav.marketIntelligence') }}</span>
            <span class="dropdown-arrow">▼</span>
          </button>
          <div class="dropdown-menu">
            <router-link to="/market" class="dropdown-item">
              <span>{{ t('nav.marketOverview') }}</span>
            </router-link>
            <router-link to="/market/news" class="dropdown-item">
              <span>{{ t('nav.marketNews') }}</span>
            </router-link>
            <router-link to="/market/events" class="dropdown-item">
              <span>{{ t('nav.marketEvents') }}</span>
            </router-link>
            <router-link to="/market/indicators" class="dropdown-item">
              <span>{{ t('nav.marketIndicators') }}</span>
            </router-link>
            <router-link to="/market/sentiment" class="dropdown-item">
              <span>{{ t('nav.marketSentiment') }}</span>
            </router-link>
            <router-link to="/market/trending" class="dropdown-item">
              <span>{{ t('nav.marketTrending') }}</span>
            </router-link>
          </div>
        </div>

        <!-- 投资组合 -->
        <router-link to="/portfolio" class="nav-link" :class="{ active: $route.name === 'Portfolio' }">
          <span class="nav-icon">💼</span>
          <span class="nav-text">{{ t('nav.portfolio') }}</span>
        </router-link>

        <!-- 风控中心 -->
        <div class="nav-dropdown">
          <button class="nav-link dropdown-toggle" :class="{ active: $route.path.startsWith('/risk') }">
            <span class="nav-icon">🛡️</span>
            <span class="nav-text">{{ t('nav.riskCenter') }}</span>
            <span class="dropdown-arrow">▼</span>
          </button>
          <div class="dropdown-menu">
            <router-link to="/risk/dashboard" class="dropdown-item">
              <span>{{ t('nav.riskDashboard') }}</span>
            </router-link>
            <router-link to="/risk/alerts" class="dropdown-item">
              <span>{{ t('nav.riskAlerts') }}</span>
            </router-link>
            <router-link to="/risk/settings" class="dropdown-item">
              <span>{{ t('nav.riskSettings') }}</span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- 右侧用户区域 -->
      <div class="navbar-user">
        <!-- 消息通知（移到顶部栏） -->
        <router-link to="/notifications" class="nav-icon-btn" v-if="userStore.isLoggedIn">
          <span class="icon">🔔</span>
          <span class="badge" v-if="notificationStore.unreadCount > 0">
            {{ notificationStore.unreadCount > 99 ? '99+' : notificationStore.unreadCount }}
          </span>
        </router-link>

        <!-- AI 浮动按钮（嵌入式AI能力） -->
        <button class="nav-icon-btn ai-float-btn" @click="toggleAIPanel" v-if="userStore.isLoggedIn">
          <span class="icon">🤖</span>
        </button>

        <LanguageSwitcher />

        <template v-if="userStore.isLoggedIn">
          <!-- 用户下拉菜单 -->
          <div class="user-dropdown">
            <button class="user-info-btn">
              <span class="user-avatar">{{ userStore.user?.display_name?.[0] || 'U' }}</span>
              <span class="user-name">{{ userStore.user?.display_name || userStore.user?.username }}</span>
              <span class="dropdown-arrow">▼</span>
            </button>
            <div class="dropdown-menu user-menu">
              <router-link to="/profile" class="dropdown-item">
                <span>👤</span>
                <span>{{ t('nav.profile') }}</span>
              </router-link>
              <router-link to="/analytics" class="dropdown-item">
                <span>📊</span>
                <span>{{ t('nav.analytics') }}</span>
              </router-link>
              <router-link to="/security" class="dropdown-item">
                <span>🔐</span>
                <span>{{ t('nav.security') }}</span>
              </router-link>
              <router-link to="/settings" class="dropdown-item">
                <span>⚙️</span>
                <span>{{ t('nav.settings') }}</span>
              </router-link>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item logout-item" @click="handleLogout">
                <span>🚪</span>
                <span>{{ t('nav.logout') }}</span>
              </button>
            </div>
          </div>
        </template>
        <template v-else>
          <router-link to="/login" class="btn btn-outline">{{ t('nav.login') }}</router-link>
          <router-link to="/register" class="btn btn-primary">{{ t('nav.register') }}</router-link>
        </template>
      </div>
    </div>

    <!-- AI 浮动侧边栏 -->
    <div class="ai-sidebar" :class="{ open: aiPanelOpen }" v-if="userStore.isLoggedIn">
      <div class="ai-sidebar-header">
        <h3>🤖 {{ t('ai.title') }}</h3>
        <button class="close-btn" @click="toggleAIPanel">✕</button>
      </div>
      <div class="ai-sidebar-content">
        <div class="ai-quick-suggestion">
          <p class="suggestion-text">{{ aiSuggestion }}</p>
        </div>
        <div class="ai-actions">
          <router-link to="/ai/chat" class="ai-action-btn" @click="toggleAIPanel">
            💬 {{ t('ai.chat.title') }}
          </router-link>
          <router-link to="/ai/analysis" class="ai-action-btn" @click="toggleAIPanel">
            📊 {{ t('ai.analysis.title') }}
          </router-link>
          <router-link to="/ai/strategies" class="ai-action-btn" @click="toggleAIPanel">
            🎯 {{ t('ai.strategies.title') }}
          </router-link>
        </div>
      </div>
    </div>
    <div class="ai-sidebar-overlay" :class="{ open: aiPanelOpen }" @click="toggleAIPanel"></div>
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'
import { useRouter } from 'vue-router'
import LanguageSwitcher from './LanguageSwitcher.vue'

const { t } = useI18n()
const userStore = useUserStore()
const notificationStore = useNotificationStore()
const router = useRouter()

const aiPanelOpen = ref(false)

const aiSuggestion = computed(() => {
  const suggestions = [
    t('ai.chat.greeting'),
    '当前市场波动较大，建议控制仓位在30%以下',
    '检测到你的组合中科技股占比过高，建议分散投资',
    '今日有3个重要经济数据发布，请注意市场风险',
    '你的胜率达到65%，继续保持！可以考虑加大盈利头寸'
  ]
  return suggestions[Math.floor(Math.random() * suggestions.length)]
})

function toggleAIPanel() {
  aiPanelOpen.value = !aiPanelOpen.value
}

onMounted(async () => {
  if (userStore.isLoggedIn) {
    await Promise.all([
      userStore.fetchCurrentUser(),
      notificationStore.fetchNotifications()
    ])
  }
})

async function handleLogout() {
  await userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/* IT 极简风格导航栏 */
.navbar {
  background: var(--bg-primary);
  border-bottom: 2px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.navbar-logo {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  text-decoration: none;
  letter-spacing: 0.05em;
  flex-shrink: 0;
}

.logo-bracket {
  color: var(--success-color);
  font-weight: 700;
}

.logo-text {
  color: var(--text-primary);
}

.logo-cursor {
  color: var(--success-color);
  animation: blink 1s step-end infinite;
  font-weight: 700;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.navbar-menu {
  display: flex;
  gap: 2px;
  flex: 1;
  justify-content: center;
}

.nav-link {
  padding: 6px 12px;
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.1s ease;
  cursor: pointer;
  border: 2px solid transparent;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
  letter-spacing: 0.02em;
}

.nav-link:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-color: var(--border-color);
}

.nav-link.active {
  background: var(--text-primary);
  color: var(--bg-primary);
  border-color: var(--text-primary);
}

.nav-icon {
  font-size: 14px;
}

.nav-text {
  white-space: nowrap;
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.nav-icon-btn {
  position: relative;
  width: 36px;
  height: 36px;
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.1s ease;
  text-decoration: none;
}

.nav-icon-btn:hover {
  background: var(--bg-secondary);
  border-color: var(--text-primary);
}

.nav-icon-btn .icon {
  font-size: 16px;
}

.nav-icon-btn .badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: var(--danger-color);
  color: var(--bg-primary);
  font-size: 10px;
  font-weight: 700;
  padding: 2px 5px;
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--bg-primary);
}

.ai-float-btn {
  animation: pulse 2s infinite;
}

.ai-float-btn:hover {
  background: var(--success-color);
  border-color: var(--success-color);
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(0, 255, 0, 0); }
}

.user-dropdown {
  position: relative;
}

.user-info-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.1s ease;
  font-size: 13px;
  font-weight: 500;
}

.user-info-btn:hover {
  background: var(--bg-secondary);
  border-color: var(--text-primary);
}

.user-avatar {
  width: 28px;
  height: 28px;
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
  font-weight: 700;
  font-size: 12px;
}

.user-name {
  color: var(--text-primary);
  font-weight: 600;
  font-size: 13px;
  letter-spacing: 0.02em;
}

.dropdown-arrow {
  font-size: 10px;
  color: var(--text-secondary);
}

.nav-dropdown {
  position: relative;
}

.dropdown-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  cursor: pointer;
  font: inherit;
  padding: 6px 12px;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 200px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  box-shadow: 4px 4px 0 var(--border-color);
  padding: 4px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-4px);
  transition: all 0.1s ease;
  z-index: 1000;
  margin-top: 4px;
}

.nav-dropdown:hover .dropdown-menu,
.user-dropdown:hover .dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.user-menu {
  right: 0;
  left: auto;
  min-width: 180px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 13px;
  transition: all 0.1s ease;
  border: 1px solid transparent;
  cursor: pointer;
  background: none;
  width: 100%;
  text-align: left;
  font: inherit;
}

.dropdown-item:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-color: var(--border-color);
}

.dropdown-divider {
  height: 2px;
  background: var(--border-color);
  margin: 4px 0;
}

.logout-item:hover {
  background: var(--danger-color);
  border-color: var(--danger-color);
  color: var(--bg-primary);
}

.btn {
  padding: 6px 14px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  border: 2px solid var(--border-color);
  transition: all 0.1s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  color: var(--text-primary);
  letter-spacing: 0.03em;
}

.btn:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}

.btn:active {
  transform: translate(1px, 1px);
}

.btn-primary {
  background: var(--success-color);
  color: var(--bg-primary);
  border-color: var(--success-color);
}

.btn-primary:hover {
  background: var(--text-primary);
  border-color: var(--text-primary);
  color: var(--bg-primary);
}

.btn-outline {
  background: transparent;
  color: var(--text-primary);
  border: 2px solid var(--border-color);
}

.btn-outline:hover {
  background: var(--danger-color);
  border-color: var(--danger-color);
  color: var(--bg-primary);
}

/* AI 侧边栏 */
.ai-sidebar {
  position: fixed;
  top: 56px;
  right: -360px;
  width: 360px;
  height: calc(100vh - 56px);
  background: var(--bg-primary);
  border-left: 2px solid var(--border-color);
  z-index: 999;
  transition: right 0.2s ease;
  display: flex;
  flex-direction: column;
}

.ai-sidebar.open {
  right: 0;
}

.ai-sidebar-header {
  padding: 16px 20px;
  border-bottom: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.ai-sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--text-primary);
  font-weight: 700;
}

.close-btn {
  width: 28px;
  height: 28px;
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.1s ease;
}

.close-btn:hover {
  background: var(--danger-color);
  border-color: var(--danger-color);
  color: var(--bg-primary);
}

.ai-sidebar-content {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.ai-quick-suggestion {
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  padding: 16px;
  margin-bottom: 20px;
}

.suggestion-text {
  margin: 0;
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.6;
}

.ai-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ai-action-btn {
  padding: 12px 16px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  color: var(--text-primary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.1s ease;
  cursor: pointer;
}

.ai-action-btn:hover {
  background: var(--success-color);
  border-color: var(--success-color);
  color: var(--bg-primary);
}

.ai-sidebar-overlay {
  position: fixed;
  top: 56px;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  z-index: 998;
}

.ai-sidebar-overlay.open {
  opacity: 1;
  visibility: visible;
}

@media (max-width: 1024px) {
  .nav-text {
    display: none;
  }
  
  .nav-link {
    padding: 6px 10px;
  }
  
  .navbar-container {
    gap: 12px;
    padding: 0 16px;
  }
}

@media (max-width: 768px) {
  .navbar-menu {
    display: none;
  }
  
  .user-name {
    display: none;
  }
  
  .navbar-container {
    padding: 0 16px;
    height: 48px;
  }
  
  .ai-sidebar {
    width: 100%;
    right: -100%;
  }
}
</style>
