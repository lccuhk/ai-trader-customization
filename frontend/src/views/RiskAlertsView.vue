<template>
  <div class="risk-alerts">
    <div class="page-header">
      <h1 class="page-title">> RISK_ALERTS.EXE</h1>
      <div class="header-actions">
        <button class="btn-primary" @click="showCreateModal = true">
          [ + NEW_ALERT ]
        </button>
      </div>
    </div>

    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">FILTER:</span>
        <button class="filter-btn" :class="{ active: activeFilter === 'all' }" @click="activeFilter = 'all'">ALL</button>
        <button class="filter-btn" :class="{ active: activeFilter === 'active' }" @click="activeFilter = 'active'">ACTIVE</button>
        <button class="filter-btn" :class="{ active: activeFilter === 'triggered' }" @click="activeFilter = 'triggered'">TRIGGERED</button>
        <button class="filter-btn" :class="{ active: activeFilter === 'paused' }" @click="activeFilter = 'paused'">PAUSED</button>
      </div>
    </div>

    <div class="alerts-list">
      <div class="alert-card" v-for="alert in filteredAlerts" :key="alert.id">
        <div class="alert-header">
          <div class="alert-title-row">
            <span class="alert-severity" :class="alert.severity">●</span>
            <span class="alert-name">{{ alert.name }}</span>
            <span class="alert-status" :class="alert.status">{{ alert.status.toUpperCase() }}</span>
          </div>
          <div class="alert-actions">
            <button class="btn-icon" @click="toggleAlert(alert)">
              {{ alert.status === 'active' ? '[ PAUSE ]' : '[ RESUME ]' }}
            </button>
            <button class="btn-icon danger" @click="deleteAlert(alert.id)">
              [ DELETE ]
            </button>
          </div>
        </div>
        <div class="alert-body">
          <div class="alert-condition">
            <span class="condition-label">CONDITION:</span>
            <span class="condition-value">{{ alert.condition }}</span>
          </div>
          <div class="alert-threshold">
            <span class="threshold-label">THRESHOLD:</span>
            <span class="threshold-value">{{ alert.threshold }}</span>
          </div>
          <div class="alert-current">
            <span class="current-label">CURRENT:</span>
            <span class="current-value" :class="alert.currentValue > alert.threshold ? 'danger' : ''">
              {{ alert.currentValue }}
            </span>
          </div>
        </div>
        <div class="alert-footer">
          <span class="alert-created">CREATED: {{ alert.createdAt }}</span>
          <span class="alert-triggered" v-if="alert.lastTriggered">LAST_TRIGGERED: {{ alert.lastTriggered }}</span>
        </div>
      </div>
    </div>

    <div class="empty-state" v-if="filteredAlerts.length === 0">
      // NO_ALERTS_FOUND
    </div>

    <div class="modal-overlay" v-if="showCreateModal" @click.self="showCreateModal = false">
      <div class="modal">
        <div class="modal-header">
          <span class="modal-title">CREATE_ALERT.EXE</span>
          <button class="btn-close" @click="showCreateModal = false">[ X ]</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>ALERT_NAME</label>
            <input type="text" v-model="newAlert.name" placeholder="e.g. BTC_DRAWDOWN_ALERT" />
          </div>
          <div class="form-group">
            <label>SEVERITY</label>
            <select v-model="newAlert.severity">
              <option value="info">INFO</option>
              <option value="warning">WARNING</option>
              <option value="danger">DANGER</option>
            </select>
          </div>
          <div class="form-group">
            <label>CONDITION</label>
            <select v-model="newAlert.condition">
              <option value="price_above">PRICE_ABOVE</option>
              <option value="price_below">PRICE_BELOW</option>
              <option value="drawdown_above">DRAWDOWN_ABOVE</option>
              <option value="exposure_above">EXPOSURE_ABOVE</option>
              <option value="volatility_above">VOLATILITY_ABOVE</option>
            </select>
          </div>
          <div class="form-group">
            <label>SYMBOL</label>
            <input type="text" v-model="newAlert.symbol" placeholder="e.g. BTC" />
          </div>
          <div class="form-group">
            <label>THRESHOLD</label>
            <input type="number" v-model="newAlert.threshold" placeholder="e.g. 10" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showCreateModal = false">[ CANCEL ]</button>
          <button class="btn-primary" @click="createAlert">[ CREATE ]</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

// @ts-ignore: unused variable for i18n
const { t } = useI18n()

const activeFilter = ref('all')
const showCreateModal = ref(false)

const alerts = ref([
  {
    id: 1,
    name: 'BTC_PRICE_DROP',
    severity: 'danger',
    status: 'active',
    condition: 'price_below',
    symbol: 'BTC',
    threshold: 40000,
    currentValue: 42500,
    createdAt: '2024-01-15_10:30',
    lastTriggered: '2024-01-14_08:15'
  },
  {
    id: 2,
    name: 'PORTFOLIO_DRAWDOWN',
    severity: 'warning',
    status: 'active',
    condition: 'drawdown_above',
    symbol: 'PORTFOLIO',
    threshold: 15,
    currentValue: 12.3,
    createdAt: '2024-01-10_14:20',
    lastTriggered: null
  },
  {
    id: 3,
    name: 'BTC_EXPOSURE_LIMIT',
    severity: 'warning',
    status: 'triggered',
    condition: 'exposure_above',
    symbol: 'BTC',
    threshold: 30,
    currentValue: 35.2,
    createdAt: '2024-01-08_09:15',
    lastTriggered: '2024-01-15_11:00'
  },
  {
    id: 4,
    name: 'ETH_VOLATILITY',
    severity: 'info',
    status: 'paused',
    condition: 'volatility_above',
    symbol: 'ETH',
    threshold: 50,
    currentValue: 45.8,
    createdAt: '2024-01-05_16:45',
    lastTriggered: '2024-01-12_14:30'
  }
])

const newAlert = ref({
  name: '',
  severity: 'warning',
  condition: 'price_below',
  symbol: '',
  threshold: 0
})

const filteredAlerts = computed(() => {
  if (activeFilter.value === 'all') return alerts.value
  return alerts.value.filter(a => a.status === activeFilter.value)
})

function toggleAlert(alert: any) {
  alert.status = alert.status === 'active' ? 'paused' : 'active'
}

function deleteAlert(id: number) {
  alerts.value = alerts.value.filter(a => a.id !== id)
}

function createAlert() {
  const alert = {
    id: Date.now(),
    ...newAlert.value,
    status: 'active',
    currentValue: 0,
    createdAt: new Date().toISOString().replace('T', '_').slice(0, 16),
    lastTriggered: null
  }
  alerts.value.unshift(alert)
  showCreateModal.value = false
  newAlert.value = { name: '', severity: 'warning', condition: 'price_below', symbol: '', threshold: 0 }
}
</script>

<style scoped>
.risk-alerts {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid var(--text-primary);
  padding-bottom: 16px;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  letter-spacing: 2px;
}

.filters {
  margin-bottom: 24px;
}

.filter-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.filter-label {
  font-size: 11px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  margin-right: 8px;
}

.filter-btn {
  padding: 6px 16px;
  border: 2px solid var(--text-primary);
  background: transparent;
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.1s ease;
}

.filter-btn:hover,
.filter-btn.active {
  background: var(--text-primary);
  color: var(--bg-primary);
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.alert-card {
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.alert-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.alert-severity.danger {
  color: var(--danger-color);
}

.alert-severity.warning {
  color: var(--warning-color);
}

.alert-severity.info {
  color: var(--text-secondary);
}

.alert-name {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 14px;
}

.alert-status {
  font-size: 10px;
  padding: 2px 8px;
  border: 1px solid currentColor;
  font-family: var(--font-mono);
}

.alert-status.active {
  color: var(--success-color);
}

.alert-status.triggered {
  color: var(--danger-color);
}

.alert-status.paused {
  color: var(--text-secondary);
}

.alert-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  padding: 4px 12px;
  border: 1px solid var(--text-primary);
  background: transparent;
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 10px;
  cursor: pointer;
}

.btn-icon:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}

.btn-icon.danger {
  border-color: var(--danger-color);
  color: var(--danger-color);
}

.btn-icon.danger:hover {
  background: var(--danger-color);
  color: var(--bg-primary);
}

.alert-body {
  padding: 16px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.condition-label,
.threshold-label,
.current-label {
  font-size: 10px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  display: block;
  margin-bottom: 4px;
}

.condition-value,
.threshold-value,
.current-value {
  font-family: var(--font-mono);
  font-weight: 700;
}

.current-value.danger {
  color: var(--danger-color);
}

.alert-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  font-size: 14px;
  border: 2px dashed var(--border-color);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
  width: 100%;
  max-width: 500px;
  box-shadow: 8px 8px 0 var(--text-primary);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 2px solid var(--text-primary);
  background: var(--text-primary);
  color: var(--bg-primary);
}

.modal-title {
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 1px;
}

.btn-close {
  background: transparent;
  border: none;
  color: var(--bg-primary);
  font-family: var(--font-mono);
  font-size: 12px;
  cursor: pointer;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 11px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid var(--text-primary);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 13px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--success-color);
  box-shadow: 4px 4px 0 var(--success-color);
}

.modal-footer {
  padding: 16px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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
  .alert-body {
    grid-template-columns: 1fr;
  }
  
  .alert-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .alert-footer {
    flex-direction: column;
    gap: 4px;
  }
}
</style>
