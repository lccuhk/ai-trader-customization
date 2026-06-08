<template>
  <button class="theme-toggle" @click="themeStore.toggleTheme" :title="buttonTitle">
    <span class="theme-icon">{{ currentIcon }}</span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

const currentIcon = computed(() => {
  const icons: Record<string, string> = {
    light: '☀️',
    dark: '🌙',
    auto: '🎨'
  }
  return icons[themeStore.currentTheme]
})

const buttonTitle = computed(() => {
  const titles: Record<string, string> = {
    light: '切换到深色模式',
    dark: '切换到自动模式',
    auto: '切换到浅色模式'
  }
  return titles[themeStore.currentTheme]
})
</script>

<style scoped>
.theme-toggle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: var(--bg-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  transition: all 0.2s;
}

.theme-toggle:hover {
  background: var(--accent-color);
  transform: scale(1.1);
}
</style>
