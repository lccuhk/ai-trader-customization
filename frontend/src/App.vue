<template>
  <div class="app">
    <Navbar v-if="showNavbar" />
    <div class="app-body" v-if="showNavbar">
      <Sidebar />
      <main class="main-content">
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
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import Sidebar from '@/components/Sidebar.vue'

const route = useRoute()

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
  margin-left: 240px;
  min-height: calc(100vh - 56px);
}

.main-content.full-width {
  margin-left: 0;
  min-height: 100vh;
}

@media (max-width: 1024px) {
  .main-content {
    margin-left: 60px;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }
}
</style>
