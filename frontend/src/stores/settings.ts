import { defineStore } from 'pinia'
import { ref } from 'vue'

interface QuickSettings {
  notifications: boolean
  sound: boolean
  autoRefresh: boolean
  refreshInterval: number
  compactMode: boolean
  showMarketNews: boolean
}

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<QuickSettings>(() => {
    const saved = localStorage.getItem('quickSettings')
    return saved ? JSON.parse(saved) : {
      notifications: true,
      sound: false,
      autoRefresh: true,
      refreshInterval: 30,
      compactMode: false,
      showMarketNews: true
    }
  })

  function saveSettings() {
    localStorage.setItem('quickSettings', JSON.stringify(settings.value))
  }

  function updateSetting(key: keyof QuickSettings, value: any) {
    settings.value[key] = value
    saveSettings()
  }

  function resetSettings() {
    settings.value = {
      notifications: true,
      sound: false,
      autoRefresh: true,
      refreshInterval: 30,
      compactMode: false,
      showMarketNews: true
    }
    saveSettings()
  }

  return {
    settings,
    updateSetting,
    resetSettings
  }
})
