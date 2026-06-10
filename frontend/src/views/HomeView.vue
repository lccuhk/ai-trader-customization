<template>
  <div class="home-view">
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-prefix">&gt;</div>
        <h1 class="hero-title">AI_TRADING_SIGNALS</h1>
        <p class="hero-subtitle">// {{ t('nav.home') }}</p>
        <button class="btn btn-primary btn-large" @click="showCreateModal = true">
          [ {{ t('common.create') }} ]
        </button>
      </div>
      <div class="hero-stats">
        <div class="stat-item">
          <span class="stat-label">ACTIVE</span>
          <span class="stat-value success">● ONLINE</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">LATENCY</span>
          <span class="stat-value">12ms</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">SIGNALS</span>
          <span class="stat-value">1,247</span>
        </div>
      </div>
    </div>

    <div class="content-section">
      <SignalList :title="t('nav.home')" />
    </div>

    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ t('common.create') }}</h3>
          <button class="close-btn" @click="showCreateModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>{{ t('common.title') }}</label>
            <input v-model="formData.title" type="text" class="form-input" :placeholder="t('common.title')" />
          </div>
          <div class="form-group">
            <label>{{ t('common.content') }}</label>
            <textarea v-model="formData.content" class="form-input" rows="4" :placeholder="t('common.content')"></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>{{ t('common.type') }}</label>
              <select v-model="formData.message_type" class="form-input">
                <option value="long">{{ t('trading.buy') }}</option>
                <option value="short">{{ t('trading.sell') }}</option>
                <option value="info">{{ t('market.news') }}</option>
                <option value="alert">{{ t('risk.alerts') }}</option>
                <option value="analysis">{{ t('ai.analysis') }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>{{ t('trading.symbol') }}</label>
              <input v-model="formData.symbols" type="text" class="form-input" placeholder="BTC, ETH" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showCreateModal = false">{{ t('common.cancel') }}</button>
          <button class="btn btn-primary" :disabled="submitting" @click="handleCreate">
            {{ submitting ? t('common.loading') : t('common.submit') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSignalStore } from '@/stores/signal'
import SignalList from '@/components/SignalList.vue'

const { t } = useI18n()

const signalStore = useSignalStore()

const showCreateModal = ref(false)
const submitting = ref(false)

const formData = reactive({
  title: '',
  content: '',
  message_type: 'info',
  symbols: ''
})

async function handleCreate() {
  if (!formData.title.trim() || !formData.content.trim()) return
  
  submitting.value = true
  try {
    const symbols = formData.symbols
      .split(',')
      .map(s => s.trim().toUpperCase())
      .filter(s => s)
    
    await signalStore.createSignal({
      title: formData.title.trim(),
      content: formData.content.trim(),
      message_type: formData.message_type,
      symbols
    })
    
    showCreateModal.value = false
    formData.title = ''
    formData.content = ''
    formData.symbols = ''
    formData.message_type = 'info'

    signalStore.fetchSignals()
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
/* IT 极简风格首页 */
.home-view {
  min-height: calc(100vh - 56px);
}

.hero-section {
  background: var(--text-primary);
  color: var(--bg-primary);
  padding: 48px 24px;
  border-bottom: 4px solid var(--success-color);
  position: relative;
  overflow: hidden;
}

/* 终端风格扫描线效果 */
.hero-section::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 255, 0, 0.03) 2px,
    rgba(0, 255, 0, 0.03) 4px
  );
  pointer-events: none;
}

.hero-content {
  max-width: 900px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.hero-prefix {
  display: inline-block;
  color: var(--success-color);
  font-size: 36px;
  font-weight: 700;
  margin-right: 8px;
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.hero-title {
  display: inline-block;
  font-size: 36px;
  font-weight: 700;
  color: var(--bg-primary);
  margin: 0 0 12px 0;
  letter-spacing: 0.05em;
}

.hero-subtitle {
  font-size: 16px;
  color: var(--success-color);
  margin: 0 0 24px 0;
  font-family: inherit;
}

.btn {
  padding: 10px 20px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  border: 2px solid var(--border-color);
  transition: all 0.1s ease;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: inherit;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--success-color);
  color: var(--bg-primary);
  border-color: var(--success-color);
}

.btn-primary:hover:not(:disabled) {
  background: var(--bg-primary);
  color: var(--text-primary);
  border-color: var(--bg-primary);
}

.btn-large {
  padding: 12px 28px;
  font-size: 14px;
  font-weight: 700;
}

.btn-outline {
  background: transparent;
  color: var(--text-primary);
  border: 2px solid var(--border-color);
}

.btn-outline:hover {
  background: var(--danger-color);
  border-color: var(--danger-color);
  color: var(--bg-primary);
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 48px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.stat-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--bg-primary);
  font-family: inherit;
}

.stat-value.success {
  color: var(--success-color);
}

.content-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 8px 8px 0 var(--border-color);
}

/* 模态框标题栏 */
.modal-content::before {
  content: 'CREATE_SIGNAL.EXE';
  display: block;
  background: var(--text-primary);
  color: var(--bg-primary);
  padding: 8px 16px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 2px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.close-btn {
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  font-size: 18px;
  color: var(--text-primary);
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.1s ease;
  font-weight: 700;
}

.close-btn:hover {
  background: var(--danger-color);
  border-color: var(--danger-color);
  color: var(--bg-primary);
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-row {
  display: flex;
  gap: 12px;
}

.form-row .form-group {
  flex: 1;
}

.form-group label {
  display: block;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  transition: all 0.1s ease;
  box-sizing: border-box;
  outline: none;
}

.form-input:focus {
  border-color: var(--success-color);
  box-shadow: 3px 3px 0 var(--success-color);
}

textarea.form-input {
  resize: vertical;
  min-height: 100px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 28px;
  }
  
  .hero-subtitle {
    font-size: 16px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
  }
}
</style>
