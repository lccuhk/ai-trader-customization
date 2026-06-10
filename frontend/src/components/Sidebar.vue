<template>
  <aside class="sidebar" v-if="userStore.isLoggedIn">
    <div class="sidebar-content">
      <!-- 主导航菜单 -->
      <nav class="sidebar-nav">
        <!-- 交易 -->
        <router-link to="/trading" class="nav-item" :class="{ active: $route.name === 'Trading' }">
          <span class="nav-icon">📈</span>
          <span class="nav-text">{{ t('nav.trading') }}</span>
        </router-link>

        <!-- 信号广场 -->
        <router-link to="/" class="nav-item" :class="{ active: $route.name === 'Home' }">
          <span class="nav-icon">📡</span>
          <span class="nav-text">{{ t('nav.home') }}</span>
        </router-link>

        <!-- 策略中心 -->
        <div class="nav-group">
          <button 
            class="nav-item group-toggle" 
            :class="{ active: $route.path.startsWith('/strategies'), open: strategyOpen }"
            @click="strategyOpen = !strategyOpen"
          >
            <span class="nav-icon">🎯</span>
            <span class="nav-text">{{ t('nav.strategyCenter') }}</span>
            <span class="group-arrow">▶</span>
          </button>
          <div class="submenu" :class="{ open: strategyOpen }">
            <router-link to="/strategies" class="submenu-item" :class="{ active: $route.name === 'Strategies' }">
              {{ t('nav.strategyManagement') }}
            </router-link>
            <router-link to="/strategies/templates" class="submenu-item" :class="{ active: $route.name === 'StrategyTemplates' }">
              {{ t('nav.strategyTemplates') }}
            </router-link>
          </div>
        </div>

        <!-- 市场情报 -->
        <div class="nav-group">
          <button 
            class="nav-item group-toggle" 
            :class="{ active: $route.path.startsWith('/market'), open: marketOpen }"
            @click="marketOpen = !marketOpen"
          >
            <span class="nav-icon">🌐</span>
            <span class="nav-text">{{ t('nav.marketIntelligence') }}</span>
            <span class="group-arrow">▶</span>
          </button>
          <div class="submenu" :class="{ open: marketOpen }">
            <router-link to="/market" class="submenu-item" :class="{ active: $route.name === 'Market' }">
              {{ t('nav.marketOverview') }}
            </router-link>
            <router-link to="/market/news" class="submenu-item" :class="{ active: $route.name === 'MarketNews' }">
              {{ t('nav.marketNews') }}
            </router-link>
            <router-link to="/market/events" class="submenu-item" :class="{ active: $route.name === 'MarketEvents' }">
              {{ t('nav.marketEvents') }}
            </router-link>
            <router-link to="/market/indicators" class="submenu-item" :class="{ active: $route.name === 'MarketIndicators' }">
              {{ t('nav.marketIndicators') }}
            </router-link>
            <router-link to="/market/sentiment" class="submenu-item" :class="{ active: $route.name === 'MarketSentiment' }">
              {{ t('nav.marketSentiment') }}
            </router-link>
            <router-link to="/market/trending" class="submenu-item" :class="{ active: $route.name === 'MarketTrending' }">
              {{ t('nav.marketTrending') }}
            </router-link>
          </div>
        </div>

        <!-- 投资组合 -->
        <router-link to="/portfolio" class="nav-item" :class="{ active: $route.name === 'Portfolio' }">
          <span class="nav-icon">💼</span>
          <span class="nav-text">{{ t('nav.portfolio') }}</span>
        </router-link>

        <!-- 交易组合 -->
        <div class="nav-group">
          <button 
            class="nav-item group-toggle" 
            :class="{ active: $route.path.startsWith('/risk'), open: riskOpen }"
            @click="riskOpen = !riskOpen"
          >
            <span class="nav-icon">🛡️</span>
            <span class="nav-text">{{ t('nav.riskCenter') }}</span>
            <span class="group-arrow">▶</span>
          </button>
          <div class="submenu" :class="{ open: riskOpen }">
            <router-link to="/risk/dashboard" class="submenu-item" :class="{ active: $route.name === 'RiskDashboard' }">
              {{ t('nav.riskDashboard') }}
            </router-link>
            <router-link to="/risk/alerts" class="submenu-item" :class="{ active: $route.name === 'RiskAlerts' }">
              {{ t('nav.riskAlerts') }}
            </router-link>
            <router-link to="/risk/settings" class="submenu-item" :class="{ active: $route.name === 'RiskSettings' }">
              {{ t('nav.riskSettings') }}
            </router-link>
          </div>
        </div>
      </nav>

      <!-- 底部分隔线 -->
      <div class="sidebar-divider"></div>

      <!-- 底部设置 -->
      <nav class="sidebar-bottom">
        <router-link to="/settings" class="nav-item" :class="{ active: $route.name === 'Settings' }">
          <span class="nav-icon">⚙️</span>
          <span class="nav-text">{{ t('nav.settings') }}</span>
        </router-link>
      </nav>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/stores/user'

const { t } = useI18n()
const userStore = useUserStore()

const strategyOpen = ref(true)
const marketOpen = ref(true)
const riskOpen = ref(true)
</script>

<style scoped>
.sidebar {
  width: 240px;
  background: var(--bg-primary);
  border-right: 2px solid var(--border-color);
  height: calc(100vh - 56px);
  position: fixed;
  top: 56px;
  left: 0;
  z-index: 90;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 12px 0;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  font-size: 13px;
  transition: all 0.1s ease;
  cursor: pointer;
  border: 2px solid transparent;
  background: none;
  width: 100%;
  text-align: left;
  font: inherit;
  letter-spacing: 0.02em;
}

.nav-item:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-color: var(--border-color);
}

.nav-item.active {
  background: var(--text-primary);
  color: var(--bg-primary);
  border-color: var(--text-primary);
}

.nav-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.nav-text {
  flex: 1;
  white-space: nowrap;
}

.group-toggle {
  position: relative;
}

.group-arrow {
  font-size: 10px;
  transition: transform 0.15s ease;
  flex-shrink: 0;
}

.group-toggle.open .group-arrow {
  transform: rotate(90deg);
}

.nav-group {
  display: flex;
  flex-direction: column;
}

.submenu {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.2s ease;
  margin-left: 28px;
  border-left: 2px solid var(--border-color);
}

.submenu.open {
  max-height: 500px;
}

.submenu-item {
  display: block;
  padding: 8px 14px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 12px;
  transition: all 0.1s ease;
  border: 1px solid transparent;
  margin: 2px 4px;
}

.submenu-item:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-color: var(--border-color);
}

.submenu-item.active {
  background: var(--success-color);
  color: var(--bg-primary);
  border-color: var(--success-color);
}

.sidebar-divider {
  height: 2px;
  background: var(--border-color);
  margin: 8px 16px;
}

.sidebar-bottom {
  padding: 0 8px 8px;
}

/* 滚动条样式 */
.sidebar::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-track {
  background: var(--bg-primary);
}

.sidebar::-webkit-scrollbar-thumb {
  background: var(--border-color);
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

@media (max-width: 1024px) {
  .sidebar {
    width: 60px;
  }
  
  .nav-text,
  .group-arrow {
    display: none;
  }
  
  .nav-item {
    justify-content: center;
    padding: 12px;
  }
  
  .submenu {
    display: none;
  }
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.2s ease;
  }
  
  .sidebar.mobile-open {
    transform: translateX(0);
  }
}
</style>
