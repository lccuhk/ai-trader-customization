<template>
  <div class="alerts-view">
    <div class="page-header">
      <h1>🔔 价格提醒</h1>
      <button class="btn btn-primary" @click="showCreateModal = true">
        + 添加提醒
      </button>
    </div>
    
    <div v-if="alerts.length > 0" class="alerts-list">
      <div v-for="alert in alerts" :key="alert.id" class="alert-card" :class="{ active: alert.active }">
        <div class="alert-info">
          <div class="alert-symbol">{{ alert.symbol }}</div>
          <div class="alert-details">
            <h3>{{ alert.title }}</h3>
            <p class="alert-condition">
              当价格 {{ alert.operator === 'above' ? '高于' : '低于' }} ${{ alert.price }} 时提醒
            </p>
            <span class="alert-status" :class="alert.active ? 'active' : 'paused'">
              {{ alert.active ? '✅ 活跃' : '⏸️ 已暂停' }}
            </span>
          </div>
        </div>
        <div class="alert-actions">
          <button class="btn btn-outline btn-small" @click="toggleAlert(alert.id)">
            {{ alert.active ? '暂停' : '激活' }}
          </button>
          <button class="btn btn-danger btn-small" @click="deleteAlert(alert.id)">
            删除
          </button>
        </div>
      </div>
    </div>
    
    <div v-else class="empty-state">
      <div class="empty-icon">🔕</div>
      <h3>还没有价格提醒</h3>
      <p>设置价格提醒，不错过任何交易机会！</p>
      <button class="btn btn-primary" @click="showCreateModal = true">
        创建第一个提醒
      </button>
    </div>
    
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>创建价格提醒</h2>
          <button class="close-btn" @click="showCreateModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>标的</label>
            <input v-model="newAlert.symbol" type="text" placeholder="例如: AAPL, NVDA, BTC" />
          </div>
          <div class="form-group">
            <label>标题</label>
            <input v-model="newAlert.title" type="text" placeholder="提醒标题" />
          </div>
          <div class="form-group">
            <label>条件</label>
            <div class="condition-row">
              <select v-model="newAlert.operator">
                <option value="above">价格高于</option>
                <option value="below">价格低于</option>
              </select>
              <span class="currency">$</span>
              <input v-model.number="newAlert.price" type="number" placeholder="目标价格" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showCreateModal = false">取消</button>
          <button class="btn btn-primary" @click="createAlert">创建提醒</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const showCreateModal = ref(false)
const alerts = ref([
  { id: 1, symbol: 'NVDA', title: 'NVDA 突破 500', operator: 'above', price: 500, active: true },
  { id: 2, symbol: 'AAPL', title: 'AAPL 回调买入点', operator: 'below', price: 170, active: true },
  { id: 3, symbol: 'TSLA', title: 'TSLA 目标价位', operator: 'above', price: 280, active: false }
])

const newAlert = reactive({
  symbol: '',
  title: '',
  operator: 'above' as 'above' | 'below',
  price: 0
})

function toggleAlert(id: number) {
  const alert = alerts.value.find(a => a.id === id)
  if (alert) {
    alert.active = !alert.active
  }
}

function deleteAlert(id: number) {
  alerts.value = alerts.value.filter(a => a.id !== id)
}

function createAlert() {
  if (newAlert.symbol && newAlert.title && newAlert.price > 0) {
    alerts.value.unshift({
      id: Date.now(),
      symbol: newAlert.symbol,
      title: newAlert.title,
      operator: newAlert.operator,
      price: newAlert.price,
      active: true
    })
    
    newAlert.symbol = ''
    newAlert.title = ''
    newAlert.operator = 'above'
    newAlert.price = 0
    showCreateModal.value = false
  }
}
</script>

<style scoped>
.alerts-view {
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  transition: all 0.2s;
}

.alert-card:hover {
  border-color: var(--accent-color);
}

.alert-card.active {
  border-left: 4px solid var(--accent-color);
}

.alert-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.alert-symbol {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--accent-color), var(--accent-hover));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
}

.alert-details h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.alert-condition {
  margin: 0 0 6px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.alert-status {
  font-size: 13px;
  font-weight: 500;
}

.alert-status.active {
  color: #22c55e;
}

.alert-status.paused {
  color: var(--text-muted);
}

.alert-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-state p {
  margin: 0 0 24px 0;
  font-size: 16px;
  color: var(--text-muted);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--bg-primary);
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-muted);
  padding: 4px;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
  box-sizing: border-box;
}

.condition-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.condition-row select {
  flex: 1;
}

.currency {
  color: var(--text-muted);
  font-weight: 600;
  font-size: 18px;
}

.condition-row input[type="number"] {
  flex: 2;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-small {
  padding: 6px 12px;
  font-size: 13px;
}

.btn-primary {
  background: var(--accent-color);
  color: white;
}

.btn-primary:hover {
  background: var(--accent-hover);
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.btn-outline:hover {
  background: var(--bg-secondary);
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.btn-danger {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.2);
}
</style>
