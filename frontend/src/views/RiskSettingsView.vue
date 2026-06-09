<template>
  <div class="risk-settings">
    <div class="page-header">
      <h1 class="page-title">> RISK_SETTINGS.EXE</h1>
    </div>

    <div class="settings-grid">
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">> GENERAL_RISK_SETTINGS</span>
        </div>
        <div class="panel-body">
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">MAX_DAILY_LOSS</span>
              <span class="setting-desc">Maximum allowed loss per trading day</span>
            </div>
            <div class="setting-control">
              <input type="number" v-model="settings.maxDailyLoss" class="input-number" />
              <span class="setting-unit">%</span>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">MAX_POSITION_SIZE</span>
              <span class="setting-desc">Maximum position size as % of portfolio</span>
            </div>
            <div class="setting-control">
              <input type="number" v-model="settings.maxPositionSize" class="input-number" />
              <span class="setting-unit">%</span>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">MAX_CONCENTRATION</span>
              <span class="setting-desc">Maximum concentration in single asset</span>
            </div>
            <div class="setting-control">
              <input type="number" v-model="settings.maxConcentration" class="input-number" />
              <span class="setting-unit">%</span>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">RISK_TOLERANCE</span>
              <span class="setting-desc">Overall risk tolerance level</span>
            </div>
            <div class="setting-control">
              <select v-model="settings.riskTolerance" class="input-select">
                <option value="conservative">CONSERVATIVE</option>
                <option value="moderate">MODERATE</option>
                <option value="aggressive">AGGRESSIVE</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">> STOP_LOSS_SETTINGS</span>
        </div>
        <div class="panel-body">
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">DEFAULT_STOP_LOSS</span>
              <span class="setting-desc">Default stop loss percentage</span>
            </div>
            <div class="setting-control">
              <input type="number" v-model="settings.defaultStopLoss" class="input-number" />
              <span class="setting-unit">%</span>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">DEFAULT_TAKE_PROFIT</span>
              <span class="setting-desc">Default take profit percentage</span>
            </div>
            <div class="setting-control">
              <input type="number" v-model="settings.defaultTakeProfit" class="input-number" />
              <span class="setting-unit">%</span>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">TRAILING_STOP</span>
              <span class="setting-desc">Enable trailing stop by default</span>
            </div>
            <div class="setting-control">
              <label class="toggle">
                <input type="checkbox" v-model="settings.trailingStop" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">TRAILING_STOP_DISTANCE</span>
              <span class="setting-desc">Trailing stop distance percentage</span>
            </div>
            <div class="setting-control">
              <input type="number" v-model="settings.trailingStopDistance" class="input-number" :disabled="!settings.trailingStop" />
              <span class="setting-unit">%</span>
            </div>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">> NOTIFICATION_SETTINGS</span>
        </div>
        <div class="panel-body">
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">EMAIL_ALERTS</span>
              <span class="setting-desc">Receive risk alerts via email</span>
            </div>
            <div class="setting-control">
              <label class="toggle">
                <input type="checkbox" v-model="settings.emailAlerts" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">PUSH_NOTIFICATIONS</span>
              <span class="setting-desc">Receive push notifications</span>
            </div>
            <div class="setting-control">
              <label class="toggle">
                <input type="checkbox" v-model="settings.pushNotifications" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">ALERT_THRESHOLD</span>
              <span class="setting-desc">Minimum severity for alerts</span>
            </div>
            <div class="setting-control">
              <select v-model="settings.alertThreshold" class="input-select">
                <option value="info">INFO</option>
                <option value="warning">WARNING</option>
                <option value="danger">DANGER</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">> ADVANCED_SETTINGS</span>
        </div>
        <div class="panel-body">
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">AUTO_STOP_LOSS</span>
              <span class="setting-desc">Automatically apply stop loss to all trades</span>
            </div>
            <div class="setting-control">
              <label class="toggle">
                <input type="checkbox" v-model="settings.autoStopLoss" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">POSITION_SIZING</span>
              <span class="setting-desc">Use risk-based position sizing</span>
            </div>
            <div class="setting-control">
              <label class="toggle">
                <input type="checkbox" v-model="settings.positionSizing" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">RISK_PER_TRADE</span>
              <span class="setting-desc">Maximum risk per trade</span>
            </div>
            <div class="setting-control">
              <input type="number" v-model="settings.riskPerTrade" class="input-number" />
              <span class="setting-unit">%</span>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">MAX_OPEN_TRADES</span>
              <span class="setting-desc">Maximum number of open trades</span>
            </div>
            <div class="setting-control">
              <input type="number" v-model="settings.maxOpenTrades" class="input-number" />
              <span class="setting-unit">trades</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="actions-bar">
      <button class="btn-secondary" @click="resetSettings">[ RESET_DEFAULTS ]</button>
      <button class="btn-primary" @click="saveSettings">[ SAVE_SETTINGS ]</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

const settings = reactive({
  maxDailyLoss: 5,
  maxPositionSize: 20,
  maxConcentration: 30,
  riskTolerance: 'moderate',
  defaultStopLoss: 5,
  defaultTakeProfit: 10,
  trailingStop: true,
  trailingStopDistance: 3,
  emailAlerts: true,
  pushNotifications: true,
  alertThreshold: 'warning',
  autoStopLoss: true,
  positionSizing: true,
  riskPerTrade: 1,
  maxOpenTrades: 10
})

const defaultSettings = { ...settings }

function resetSettings() {
  Object.assign(settings, defaultSettings)
}

function saveSettings() {
  console.log('Saving settings:', settings)
  alert('// SETTINGS_SAVED_SUCCESSFULLY')
}
</script>

<style scoped>
.risk-settings {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  border-bottom: 2px solid var(--text-primary);
  padding-bottom: 16px;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  letter-spacing: 2px;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.panel {
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
}

.panel-header {
  padding: 12px 16px;
  border-bottom: 2px solid var(--text-primary);
  background: var(--text-primary);
  color: var(--bg-primary);
}

.panel-title {
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 1px;
}

.panel-body {
  padding: 16px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--border-color);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-info {
  flex: 1;
}

.setting-label {
  display: block;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 13px;
  margin-bottom: 4px;
}

.setting-desc {
  font-size: 11px;
  color: var(--text-secondary);
}

.setting-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.input-number {
  width: 80px;
  padding: 8px 12px;
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 13px;
  text-align: right;
}

.input-number:focus {
  outline: none;
  border-color: var(--success-color);
}

.input-number:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-select {
  padding: 8px 12px;
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 12px;
}

.input-select:focus {
  outline: none;
  border-color: var(--success-color);
}

.setting-unit {
  font-size: 11px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  min-width: 50px;
}

.toggle {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 26px;
}

.toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--bg-secondary);
  border: 2px solid var(--text-primary);
  transition: 0.1s;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 3px;
  bottom: 3px;
  background: var(--text-primary);
  transition: 0.1s;
}

.toggle input:checked + .toggle-slider {
  background: var(--success-color);
  border-color: var(--success-color);
}

.toggle input:checked + .toggle-slider:before {
  transform: translateX(24px);
  background: var(--bg-primary);
}

.actions-bar {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px;
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border: 2px solid var(--text-primary);
  font-family: var(--font-mono);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.1s ease;
}

.btn-primary {
  background: var(--success-color);
  border-color: var(--success-color);
  color: var(--bg-primary);
}

.btn-primary:hover {
  transform: translate(2px, 2px);
  box-shadow: none;
}

.btn-secondary {
  background: transparent;
  color: var(--text-primary);
}

.btn-secondary:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}

@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .setting-control {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
