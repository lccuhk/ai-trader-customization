<template>
  <div class="app">
    <Navbar v-if="showNavbar" />
    <div class="app-body" v-if="showNavbar">
      <Sidebar v-if="userStore.isLoggedIn" />
      <main class="main-content" :class="{ 'with-sidebar': userStore.isLoggedIn }">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
    <main class="main-content full-width" v-else>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- AI 浮动按钮（右下角） -->
    <button 
      class="ai-float-btn" 
      @click="toggleAIPanel" 
      v-if="userStore.isLoggedIn"
    >
      <span class="icon">🤖</span>
    </button>

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
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import Navbar from '@/components/Navbar.vue'
import Sidebar from '@/components/Sidebar.vue'

const { t } = useI18n()
const route = useRoute()
const userStore = useUserStore()

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

const showNavbar = computed(() => {
  const noNavbarRoutes = ['Login', 'Register', 'NotFound']
  return !noNavbarRoutes.includes(route.name as string)
})
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-body {
  display: flex;
  flex: 1;
  padding-top: 56px;
}

.main-content {
  flex: 1;
  background: var(--bg-secondary);
  margin-left: 0;
  min-height: calc(100vh - 56px);
}

.main-content.with-sidebar {
  margin-left: 240px;
}

.main-content.full-width {
  margin-left: 0;
  min-height: 100vh;
}

@media (max-width: 1024px) {
  .main-content.with-sidebar {
    margin-left: 60px;
  }
}

@media (max-width: 768px) {
  .main-content.with-sidebar {
    margin-left: 0;
  }
}

/* AI 浮动按钮（右下角） */
.ai-float-btn {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: 3px solid var(--success-color);
  background: var(--bg-primary);
  color: var(--success-color);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  z-index: 999;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  animation: pulse 2s infinite;
}

.ai-float-btn:hover {
  background: var(--success-color);
  color: var(--bg-primary);
  transform: scale(1.1);
}

.ai-float-btn .icon {
  font-size: 24px;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.4); }
  50% { box-shadow: 0 0 0 12px rgba(0, 255, 0, 0); }
}

/* AI 侧边栏 */
.ai-sidebar {
  position: fixed;
  bottom: 96px;
  right: -380px;
  width: 360px;
  max-height: calc(100vh - 120px);
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  box-shadow: -4px 4px 0 var(--border-color);
  z-index: 998;
  transition: right 0.25s ease;
  display: flex;
  flex-direction: column;
}

.ai-sidebar.open {
  right: 24px;
}

.ai-sidebar-header {
  padding: 16px 20px;
  border-bottom: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
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
  text-align: left;
}

.ai-action-btn:hover {
  background: var(--success-color);
  border-color: var(--success-color);
  color: var(--bg-primary);
}

.ai-sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  z-index: 997;
}

.ai-sidebar-overlay.open {
  opacity: 1;
  visibility: visible;
}

@media (max-width: 768px) {
  .ai-float-btn {
    bottom: 16px;
    right: 16px;
    width: 48px;
    height: 48px;
  }
  
  .ai-float-btn .icon {
    font-size: 20px;
  }
  
  .ai-sidebar {
    width: calc(100% - 32px);
    right: -100%;
    bottom: 80px;
    max-height: calc(100vh - 100px);
  }
  
  .ai-sidebar.open {
    right: 16px;
  }
}
</style>
