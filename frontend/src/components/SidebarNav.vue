<template>
  <aside class="sidebar">
    <div class="sidebar-top">
      <router-link to="/" class="sidebar-logo">
        <span class="logo-bracket">[</span>
        <span class="logo-text">AI_TRADER</span>
        <span class="logo-bracket">]</span>
      </router-link>

      <nav class="sidebar-nav">
        <button
          v-for="item in navItems"
          :key="item.key"
          class="nav-item"
          :class="{ active: activeNav === item.key }"
          @click="navigate(item.key)"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ $t(item.labelKey) }}</span>
        </button>
      </nav>
    </div>

    <div class="sidebar-bottom">
      <button
        class="nav-item"
        :class="{ active: activeNav === 'settings' }"
        @click="navigate('settings')"
      >
        <span class="nav-icon">⚙</span>
        <span class="nav-label">{{ $t('nav.settings') }}</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps<{
  activeNav: string
}>()

const emit = defineEmits<{
  'update:activeNav': [value: string]
}>()

const router = useRouter()

const navItems = [
  { key: 'trading', icon: '⇄', labelKey: 'nav.trading' },
  { key: 'signals', icon: '⚡', labelKey: 'nav.signalsSquare' },
  { key: 'strategy', icon: '◈', labelKey: 'nav.strategyCenter' },
  { key: 'market', icon: '◎', labelKey: 'nav.marketIntelligence' },
  { key: 'risk', icon: '📊', labelKey: 'nav.riskCenter' },
]

function navigate(key: string) {
  emit('update:activeNav', key)
}
</script>

<style scoped>
.sidebar {
  width: 220px;
  min-width: 220px;
  min-height: 100vh;
  background: var(--bg-primary);
  border-right: 2px solid var(--border-color);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow-y: auto;
}

.sidebar-top {
  display: flex;
  flex-direction: column;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 20px 16px 16px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  text-decoration: none;
  letter-spacing: 0.05em;
  border-bottom: 2px solid var(--border-color);
}

.logo-bracket {
  color: var(--success-color);
  font-weight: 700;
}

.logo-text {
  color: var(--text-primary);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  padding: 8px;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 2px solid transparent;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  transition: all 0.1s ease;
  text-align: left;
  width: 100%;
  border-radius: 0;
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
  font-size: 18px;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.nav-label {
  white-space: nowrap;
}

.sidebar-bottom {
  padding: 8px;
  border-top: 2px solid var(--border-color);
}
</style>
