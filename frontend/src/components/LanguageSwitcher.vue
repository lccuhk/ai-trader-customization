<template>
  <div class="language-switcher">
    <button class="lang-toggle" @click="toggleDropdown" :title="t('nav.language')">
      <span class="lang-flag">{{ currentLang.flag }}</span>
      <span class="lang-code">{{ currentLang.code.split('-')[0].toUpperCase() }}</span>
      <span class="lang-arrow">▼</span>
    </button>
    
    <div v-if="isOpen" class="lang-dropdown">
      <div class="lang-header">
        <span class="lang-title">{{ t('language.selectLanguage') }}</span>
      </div>
      <div class="lang-list">
        <button
          v-for="lang in supportedLanguages"
          :key="lang.code"
          class="lang-item"
          :class="{ active: currentLocale === lang.code }"
          @click="selectLanguage(lang.code)"
        >
          <span class="lang-flag">{{ lang.flag }}</span>
          <span class="lang-name">{{ t(lang.name) }}</span>
          <span v-if="currentLocale === lang.code" class="lang-check">✓</span>
        </button>
      </div>
    </div>
    
    <div v-if="isOpen" class="lang-overlay" @click="closeDropdown"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { supportedLanguages, setLocale, getLocale } from '../i18n'

const { t } = useI18n()
const isOpen = ref(false)
const currentLocale = ref(getLocale())

const currentLang = computed(() => {
  return supportedLanguages.find(l => l.code === currentLocale.value) || supportedLanguages[0]
})

function toggleDropdown() {
  isOpen.value = !isOpen.value
}

function closeDropdown() {
  isOpen.value = false
}

function selectLanguage(code: string) {
  currentLocale.value = code
  setLocale(code)
  isOpen.value = false
}

function handleClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.language-switcher')) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.language-switcher {
  position: relative;
}

.lang-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  color: var(--text-primary);
  cursor: pointer;
  font-family: inherit;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.1s ease;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.lang-toggle:hover {
  background: var(--bg-secondary);
  border-color: var(--text-primary);
}

.lang-flag {
  font-size: 16px;
  line-height: 1;
}

.lang-code {
  font-size: 12px;
  font-weight: 700;
}

.lang-arrow {
  font-size: 10px;
  opacity: 0.7;
}

.lang-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  min-width: 200px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  box-shadow: 4px 4px 0 var(--border-color);
  z-index: 1000;
  margin-top: 4px;
}

.lang-header {
  padding: 10px 14px;
  border-bottom: 2px solid var(--border-color);
  background: var(--bg-secondary);
}

.lang-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.lang-list {
  max-height: 320px;
  overflow-y: auto;
}

.lang-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 14px;
  background: none;
  border: none;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
  cursor: pointer;
  font-family: inherit;
  font-size: 13px;
  text-align: left;
  transition: all 0.1s ease;
}

.lang-item:last-child {
  border-bottom: none;
}

.lang-item:hover {
  background: var(--bg-secondary);
}

.lang-item.active {
  background: var(--success-color);
  color: var(--bg-primary);
}

.lang-item.active .lang-name {
  font-weight: 700;
}

.lang-name {
  flex: 1;
}

.lang-check {
  font-weight: 700;
}

.lang-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

/* Scrollbar */
.lang-list::-webkit-scrollbar {
  width: 6px;
}

.lang-list::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

.lang-list::-webkit-scrollbar-thumb {
  background: var(--border-color);
}

.lang-list::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}
</style>
