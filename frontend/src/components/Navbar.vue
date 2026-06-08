<template>
  <nav class="navbar">
    <div class="navbar-container">
      <router-link to="/" class="navbar-logo">
        <span class="logo-bracket">[</span>
        <span class="logo-text">AI_TRADER</span>
        <span class="logo-bracket">]</span>
        <span class="logo-cursor">_</span>
      </router-link>

      <div class="navbar-menu" v-if="userStore.isLoggedIn">
        <router-link to="/" class="nav-link" :class="{ active: $route.name === 'Home' }">
          {{ t('nav.home') }}
        </router-link>
        <router-link to="/trading" class="nav-link" :class="{ active: $route.name === 'Trading' }">
          {{ t('nav.trading') }}
        </router-link>
        <router-link to="/portfolio" class="nav-link" :class="{ active: $route.name === 'Portfolio' }">
          {{ t('nav.portfolio') }}
        </router-link>
        <div class="nav-dropdown">
          <button class="nav-link dropdown-toggle" :class="{ active: $route.path.startsWith('/ai') }">
            {{ t('nav.ai') }}
          </button>
          <div class="dropdown-menu">
            <router-link to="/ai" class="dropdown-item">{{ t('nav.aiHome') }}</router-link>
            <router-link to="/ai/chat" class="dropdown-item">{{ t('nav.aiChat') }}</router-link>
            <router-link to="/ai/analysis" class="dropdown-item">{{ t('nav.aiAnalysis') }}</router-link>
            <router-link to="/ai/strategies" class="dropdown-item">{{ t('nav.aiStrategies') }}</router-link>
          </div>
        </div>
        <div class="nav-dropdown">
          <button class="nav-link dropdown-toggle" :class="{ active: $route.path.startsWith('/risk') }">
            {{ t('nav.risk') }}
          </button>
          <div class="dropdown-menu">
            <router-link to="/risk/dashboard" class="dropdown-item">{{ t('nav.riskDashboard') }}</router-link>
            <router-link to="/risk/alerts" class="dropdown-item">{{ t('nav.riskAlerts') }}</router-link>
            <router-link to="/risk/settings" class="dropdown-item">{{ t('nav.riskSettings') }}</router-link>
          </div>
        </div>
        <div class="nav-dropdown">
          <button class="nav-link dropdown-toggle" :class="{ active: ['/market/news', '/market/events', '/market/indicators', '/market/sentiment', '/market/trending'].includes($route.path) }">
            {{ t('nav.market') }}
          </button>
          <div class="dropdown-menu">
            <router-link to="/market/news" class="dropdown-item">{{ t('nav.marketNews') }}</router-link>
            <router-link to="/market/events" class="dropdown-item">{{ t('nav.marketEvents') }}</router-link>
            <router-link to="/market/indicators" class="dropdown-item">{{ t('nav.marketIndicators') }}</router-link>
            <router-link to="/market/sentiment" class="dropdown-item">{{ t('nav.marketSentiment') }}</router-link>
            <router-link to="/market/trending" class="dropdown-item">{{ t('nav.marketTrending') }}</router-link>
          </div>
        </div>
        <div class="nav-dropdown">
          <button class="nav-link dropdown-toggle" :class="{ active: $route.path.startsWith('/strategies') }">
            {{ t('nav.strategies') }}
          </button>
          <div class="dropdown-menu">
            <router-link to="/strategies" class="dropdown-item">{{ t('nav.strategyManagement') }}</router-link>
            <router-link to="/strategies/templates" class="dropdown-item">{{ t('nav.strategyTemplates') }}</router-link>
          </div>
        </div>
        <div class="nav-dropdown">
          <button class="nav-link dropdown-toggle" :class="{ active: ['/favorites', '/history', '/export', '/shortcuts', '/alerts', '/backup'].includes($route.path) }">
            {{ t('nav.more') }}
          </button>
          <div class="dropdown-menu">
            <router-link to="/favorites" class="dropdown-item">{{ t('nav.favorites') }}</router-link>
            <router-link to="/history" class="dropdown-item">{{ t('nav.history') }}</router-link>
            <router-link to="/alerts" class="dropdown-item">{{ t('nav.priceAlerts') }}</router-link>
            <router-link to="/export" class="dropdown-item">{{ t('nav.export') }}</router-link>
            <router-link to="/backup" class="dropdown-item">{{ t('nav.backup') }}</router-link>
            <router-link to="/shortcuts" class="dropdown-item">{{ t('nav.shortcuts') }}</router-link>
          </div>
        </div>
        <router-link to="/messages" class="nav-link" :class="{ active: $route.name === 'Messages' }">
          {{ t('nav.messages') }}
        </router-link>
      </div>

      <div class="navbar-user">
        <LanguageSwitcher />
        <template v-if="userStore.isLoggedIn">
          <div class="user-info">
            <span class="user-avatar">{{ userStore.user?.display_name?.[0] || 'U' }}</span>
            <span class="user-name">{{ userStore.user?.display_name || userStore.user?.username }}</span>
          </div>
          <button class="btn btn-outline" @click="handleLogout">{{ t('nav.logout') }}</button>
        </template>
        <template v-else>
          <router-link to="/login" class="btn btn-outline">{{ t('nav.login') }}</router-link>
          <router-link to="/register" class="btn btn-primary">{{ t('nav.register') }}</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'
import { useRouter } from 'vue-router'
import LanguageSwitcher from './LanguageSwitcher.vue'

const { t } = useI18n()
const userStore = useUserStore()
const notificationStore = useNotificationStore()
const router = useRouter()

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
  gap: 32px;
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
  gap: 4px;
  flex: 1;
}

.nav-link {
  padding: 6px 14px;
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.1s ease;
  cursor: pointer;
  border: 2px solid transparent;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
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

.navbar-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
  font-weight: 700;
  font-size: 13px;
}

.user-name {
  color: var(--text-primary);
  font-weight: 600;
  font-size: 13px;
  letter-spacing: 0.02em;
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
  text-transform: uppercase;
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

.nav-dropdown {
  position: relative;
}

.dropdown-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  font: inherit;
  padding: 6px 14px;
}

.dropdown-toggle::after {
  content: '▼';
  font-size: 10px;
  margin-left: 4px;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 180px;
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

.nav-dropdown:hover .dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: block;
  padding: 8px 12px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 13px;
  transition: all 0.1s ease;
  border: 1px solid transparent;
}

.dropdown-item:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-color: var(--border-color);
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
}
</style>
