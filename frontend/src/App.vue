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

    <!-- AI 助手由 DashboardLayout 中的 AIChatSidebar 提供，此处不再重复添加 -->
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import Navbar from '@/components/Navbar.vue'
import Sidebar from '@/components/Sidebar.vue'

const route = useRoute()
const userStore = useUserStore()

const authPages = ['Login', 'Register', 'NotFound']
const isAuthPage = computed(() => authPages.includes(route.name as string))
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: var(--bg-secondary, #0a0a0a);
  color: var(--text-primary, #e0e0e0);
}

:root {
  --bg-primary: #111111;
  --bg-secondary: #0a0a0a;
  --text-primary: #e0e0e0;
  --text-secondary: #666666;
  --border-color: #333333;
  --success-color: #00ff41;
  --danger-color: #ff3333;
  --warning-color: #ff9900;
  --info-color: #3399ff;
  --danger-bg: rgba(255, 51, 51, 0.08);
  --warning-bg: rgba(255, 153, 0, 0.08);
  --font-mono: 'Courier New', Courier, monospace;
}

/* Unified font — terminal aesthetic throughout */
body,
input, select, textarea, button,
table, th, td,
.panel-title, .page-title,
.metric-value, .setting-value, .status-bar {
  font-family: var(--font-mono);
}
</style>

<style scoped>
.app {
  min-height: 100vh;
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

/* AI 助手按钮由 DashboardLayout 中的 AIChatSidebar 提供 */
</style>
