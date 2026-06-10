<template>
  <div class="settings-page">
    <div class="page-title">&gt; {{ $t('nav.settings') }}</div>

    <div class="settings-grid">
      <div class="panel">
        <div class="panel-header"><span class="panel-title">{{ $t('common.general') }}</span></div>
        <div class="panel-body">
          <div class="setting-row">
            <span class="setting-label">{{ $t('common.language') }}</span>
            <select class="setting-input" v-model="draftLang">
              <option value="zh-CN">{{ $t('language.zhCN') }}</option>
              <option value="en-US">{{ $t('language.enUS') }}</option>
            </select>
          </div>
          <div class="setting-row">
            <span class="setting-label">{{ $t('common.theme') }}</span>
            <select class="setting-input" v-model="draftTheme">
              <option value="auto">{{ $t('common.themeAuto') }}</option>
              <option value="light">{{ $t('common.themeLight') }}</option>
              <option value="dark">{{ $t('common.themeDark') }}</option>
            </select>
          </div>
          <div class="setting-row">
            <span class="setting-label">{{ $t('common.simMode') }}</span>
            <span class="setting-status active">● {{ $t('common.running') }}</span>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header"><span class="panel-title">{{ $t('language.apiManagement') }}</span></div>
        <div class="panel-body">
          <div class="setting-row">
            <span class="setting-label">{{ $t('language.exchange') }}</span>
            <span class="setting-value">{{ $t('language.exchange') }} ({{ $t('trading.simulation') }})</span>
          </div>
          <div class="setting-row">
            <span class="setting-label">{{ $t('language.apiKey') }}</span>
            <span class="setting-value muted">••••••••••••••••</span>
          </div>
          <button class="action-btn" @click="alert($t('language.apiManagement'))">{{ $t('language.manageApi') }}</button>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header"><span class="panel-title">{{ $t('common.notifications') }}</span></div>
        <div class="panel-body">
          <div class="setting-row">
            <span class="setting-label">{{ $t('language.tradeAlerts') }}</span>
            <button class="toggle-btn" :class="{ on: draftSettings.tradeAlerts }" @click="draftSettings.tradeAlerts = !draftSettings.tradeAlerts">
              <span class="toggle-track"><span class="toggle-thumb"></span></span>
              <span class="toggle-label">{{ draftSettings.tradeAlerts ? $t('common.on') : $t('common.off') }}</span>
            </button>
          </div>
          <div class="setting-row">
            <span class="setting-label">{{ $t('language.riskAlerts') }}</span>
            <button class="toggle-btn" :class="{ on: draftSettings.riskAlerts }" @click="draftSettings.riskAlerts = !draftSettings.riskAlerts">
              <span class="toggle-track"><span class="toggle-thumb"></span></span>
              <span class="toggle-label">{{ draftSettings.riskAlerts ? $t('common.on') : $t('common.off') }}</span>
            </button>
          </div>
          <div class="setting-row">
            <span class="setting-label">{{ $t('language.signalAlerts') }}</span>
            <button class="toggle-btn" :class="{ on: draftSettings.signalAlerts }" @click="draftSettings.signalAlerts = !draftSettings.signalAlerts">
              <span class="toggle-track"><span class="toggle-thumb"></span></span>
              <span class="toggle-label">{{ draftSettings.signalAlerts ? $t('common.on') : $t('common.off') }}</span>
            </button>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header"><span class="panel-title">{{ $t('language.riskPreferences') }}</span></div>
        <div class="panel-body">
          <div class="setting-row">
            <span class="setting-label">{{ $t('language.perTradeRiskLimit') }}</span>
            <span class="setting-value">2.5%</span>
          </div>
          <div class="setting-row">
            <span class="setting-label">{{ $t('language.maxLeverage') }}</span>
            <span class="setting-value">3x</span>
          </div>
          <div class="setting-row">
            <span class="setting-label">{{ $t('language.autoStopLoss') }}</span>
            <button class="toggle-btn" :class="{ on: draftSettings.autoStopLoss }" @click="draftSettings.autoStopLoss = !draftSettings.autoStopLoss">
              <span class="toggle-track"><span class="toggle-thumb"></span></span>
              <span class="toggle-label">{{ draftSettings.autoStopLoss ? $t('common.on') : $t('common.off') }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="settings-actions">
      <button class="cancel-btn" @click="resetDraft">{{ $t('common.cancel') }}</button>
      <button class="save-btn" @click="saveSettings">{{ $t('language.saveSettings') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useThemeStore } from '@/stores/theme'
import { useSettingsStore } from '@/stores/settings'
import { setLocale, getLocale } from '@/i18n'

const { locale } = useI18n()
const themeStore = useThemeStore()
const settingsStore = useSettingsStore()

// Draft state — changes are local until "保存" is clicked
const draftLang = ref(getLocale())
const draftTheme = ref(themeStore.currentTheme)

const draftSettings = reactive({
  tradeAlerts: settingsStore.settings.tradeAlerts,
  riskAlerts: settingsStore.settings.riskAlerts,
  signalAlerts: settingsStore.settings.signalAlerts,
  autoStopLoss: settingsStore.settings.autoStopLoss,
})

function resetDraft() {
  draftLang.value = getLocale()
  draftTheme.value = themeStore.currentTheme
  draftSettings.tradeAlerts = settingsStore.settings.tradeAlerts
  draftSettings.riskAlerts = settingsStore.settings.riskAlerts
  draftSettings.signalAlerts = settingsStore.settings.signalAlerts
  draftSettings.autoStopLoss = settingsStore.settings.autoStopLoss
}

function saveSettings() {
  // Apply language globally
  setLocale(draftLang.value)
  locale.value = draftLang.value

  // Apply theme globally
  themeStore.setTheme(draftTheme.value as 'light' | 'dark' | 'auto')

  // Apply notification & risk toggles
  settingsStore.updateSetting('tradeAlerts', draftSettings.tradeAlerts)
  settingsStore.updateSetting('riskAlerts', draftSettings.riskAlerts)
  settingsStore.updateSetting('signalAlerts', draftSettings.signalAlerts)
  settingsStore.updateSetting('autoStopLoss', draftSettings.autoStopLoss)
}
</script>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.05em;
  font-family: var(--font-mono, monospace);
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}

.panel {
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
}

.panel-header {
  padding: 12px 16px;
  border-bottom: 2px solid var(--border-color);
  background: var(--bg-secondary);
}

.panel-title {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.05em;
  font-family: var(--font-mono, monospace);
}

.panel-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
  font-size: 13px;
}

.setting-row:last-child {
  border-bottom: none;
}

.setting-label {
  color: var(--text-secondary);
  font-weight: 500;
}

.setting-value {
  color: var(--text-primary);
  font-weight: 600;
  font-family: var(--font-mono, monospace);
}
.setting-value.muted {
  color: var(--text-secondary);
  letter-spacing: 0.1em;
}

.setting-input {
  padding: 4px 8px;
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 12px;
  outline: none;
}

.setting-status {
  font-size: 12px;
  font-weight: 600;
}
.setting-status.active {
  color: var(--success-color);
}

.action-btn {
  width: 100%;
  padding: 8px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
}
.action-btn:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}

/* Toggle switch */
.toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
}

.toggle-track {
  width: 36px;
  height: 20px;
  border: 2px solid var(--border-color);
  background: var(--bg-secondary);
  position: relative;
  transition: background 0.15s ease;
}

.toggle-btn.on .toggle-track {
  background: var(--success-color);
  border-color: var(--success-color);
}

.toggle-thumb {
  width: 12px;
  height: 12px;
  background: var(--text-primary);
  position: absolute;
  top: 2px;
  left: 2px;
  transition: left 0.15s ease;
}

.toggle-btn.on .toggle-thumb {
  left: 18px;
  background: white;
}

.toggle-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 600;
}

/* Action buttons */
.settings-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 8px;
}

.cancel-btn {
  padding: 10px 28px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.cancel-btn:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}

.save-btn {
  padding: 10px 28px;
  border: 2px solid var(--success-color);
  background: var(--success-color);
  color: var(--bg-primary);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.save-btn:hover {
  background: transparent;
  color: var(--success-color);
}
</style>
