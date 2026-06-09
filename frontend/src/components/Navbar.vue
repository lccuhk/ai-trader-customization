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

      <!-- 右侧用户区域 -->
      <div class="navbar-user">
        <!-- 消息通知（移到顶部栏） -->
        <router-link to="/notifications" class="nav-icon-btn" v-if="userStore.isLoggedIn">
          <span class="icon">🔔</span>
          <span class="badge" v-if="notificationStore.unreadCount > 0">
            {{ notificationStore.unreadCount > 99 ? '99+' : notificationStore.unreadCount }}
          </span>
        </router-link>

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
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  height: 56px;
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
}
</style>
