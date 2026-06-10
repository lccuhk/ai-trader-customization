import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { QuickSettings } from '@/types'

const defaultSettings: QuickSettings = {
  theme: 'dark',
  notifications: true,
  sound: false,
  autoRefresh: true,
  refreshInterval: 30,
  compactMode: false,
  showMarketNews: true,
  language: 'zh-CN',
  tradeAlerts: true,
  riskAlerts: true,
  signalAlerts: false,
  autoStopLoss: true
}

export const useSettingsStore = defineStore('settings', () => {
  const savedSettings = localStorage.getItem('quickSettings')
  const settings = ref<QuickSettings>(savedSettings ? JSON.parse(savedSettings) : defaultSettings)

  function saveSettings() {
    localStorage.setItem('quickSettings', JSON.stringify(settings.value))
  }

  function updateSetting<K extends keyof QuickSettings>(key: K, value: QuickSettings[K]) {
    settings.value[key] = value
    saveSettings()
  }

  function resetSettings() {
    settings.value = { ...defaultSettings }
    saveSettings()
  }

  return {
    settings,
    updateSetting,
    resetSettings
  }
})
