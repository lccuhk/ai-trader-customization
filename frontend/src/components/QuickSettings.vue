<template>
  <div class="quick-settings">
    <button class="settings-toggle" @click="showSettings = !showSettings">
      ⚙️ 设置
    </button>
    
    <div v-if="showSettings" class="settings-panel">
      <div class="settings-header">
        <h3>快捷设置</h3>
        <button class="close-btn" @click="showSettings = false">✕</button>
      </div>
      
      <div class="settings-list">
        <div class="setting-item">
          <span class="setting-label">📢 通知</span>
          <button class="toggle-btn" :class="{ active: settingsStore.settings.notifications }" @click="settingsStore.updateSetting('notifications', !settingsStore.settings.notifications)">
            {{ settingsStore.settings.notifications ? '开' : '关' }}
          </button>
        </div>
        
        <div class="setting-item">
          <span class="setting-label">🔊 声音</span>
          <button class="toggle-btn" :class="{ active: settingsStore.settings.sound }" @click="settingsStore.updateSetting('sound', !settingsStore.settings.sound)">
            {{ settingsStore.settings.sound ? '开' : '关' }}
          </button>
        </div>
        
        <div class="setting-item">
          <span class="setting-label">🔄 自动刷新</span>
          <button class="toggle-btn" :class="{ active: settingsStore.settings.autoRefresh }" @click="settingsStore.updateSetting('autoRefresh', !settingsStore.settings.autoRefresh)">
            {{ settingsStore.settings.autoRefresh ? '开' : '关' }}
          </button>
        </div>
        
        <div class="setting-item">
          <span class="setting-label">📰 显示新闻</span>
          <button class="toggle-btn" :class="{ active: settingsStore.settings.showMarketNews }" @click="settingsStore.updateSetting('showMarketNews', !settingsStore.settings.showMarketNews)">
            {{ settingsStore.settings.showMarketNews ? '开' : '关' }}
          </button>
        </div>
        
        <div class="setting-item">
          <span class="setting-label">📐 紧凑模式</span>
          <button class="toggle-btn" :class="{ active: settingsStore.settings.compactMode }" @click="settingsStore.updateSetting('compactMode', !settingsStore.settings.compactMode)">
            {{ settingsStore.settings.compactMode ? '开' : '关' }}
          </button>
        </div>
        
        <div class="setting-item">
          <span class="setting-label">⏱️ 刷新间隔</span>
          <select class="select-input" :value="settingsStore.settings.refreshInterval" @change="(e) => settingsStore.updateSetting('refreshInterval', parseInt((e.target as HTMLSelectElement).value))">
            <option :value="10">10秒</option>
            <option :value="30">30秒</option>
            <option :value="60">1分钟</option>
            <option :value="120">2分钟</option>
          </select>
        </div>
      </div>
      
      <div class="settings-actions">
        <button class="btn btn-secondary" @click="settingsStore.resetSettings">重置</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()
const showSettings = ref(false)
</script>

<style scoped>
.quick-settings {
  position: relative;
}

.settings-toggle {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.settings-toggle:hover {
  border-color: var(--accent-color);
  background: var(--bg-primary);
}

.settings-panel {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  width: 280px;
  z-index: 1000;
}

.settings-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.settings-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-muted);
  padding: 4px;
}

.settings-list {
  padding: 12px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  font-size: 14px;
  color: var(--text-primary);
}

.toggle-btn {
  padding: 6px 16px;
  border-radius: 20px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s;
}

.toggle-btn.active {
  background: var(--accent-color);
  border-color: var(--accent-color);
  color: white;
}

.select-input {
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 13px;
}

.settings-actions {
  padding: 12px;
  border-top: 1px solid var(--border-color);
}

.btn {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background: var(--bg-secondary);
  opacity: 0.9;
}
</style>
