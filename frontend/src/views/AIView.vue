<template>
  <div class="ai-view">
    <div class="ai-header">
      <h1>AI 助手</h1>
      <p class="subtitle">智能交易分析与建议</p>
    </div>

    <div class="ai-cards">
      <div class="ai-card" @click="$router.push('/ai/chat')">
        <div class="card-icon">💬</div>
        <h3>AI 对话</h3>
        <p>与AI助手交流，获取市场分析和交易建议</p>
        <div class="card-action">开始对话 →</div>
      </div>

      <div class="ai-card" @click="$router.push('/ai/analysis')">
        <div class="card-icon">📊</div>
        <h3>交易分析</h3>
        <p>AI分析你的交易行为，给出个性化建议</p>
        <div class="card-action">查看分析 →</div>
      </div>

      <div class="ai-card" @click="generateSignal">
        <div class="card-icon">🎯</div>
        <h3>AI 信号</h3>
        <p>基于AI模型生成智能交易信号</p>
        <div class="card-action">生成信号 →</div>
      </div>

      <div class="ai-card" @click="$router.push('/ai/strategies')">
        <div class="card-icon">🧠</div>
        <h3>策略生成</h3>
        <p>AI自动生成和回测交易策略</p>
        <div class="card-action">创建策略 →</div>
      </div>
    </div>

    <div class="ai-sections">
      <div class="section">
        <div class="section-header">
          <h2>风险预警</h2>
          <button class="refresh-btn" @click="checkAlerts" :disabled="aiStore.loading">
            {{ aiStore.loading ? '检查中...' : '刷新' }}
          </button>
        </div>
        <div v-if="aiStore.riskAlerts.length === 0" class="empty-state">
          暂无风险预警
        </div>
        <div v-else class="alerts-list">
          <div 
            v-for="alert in aiStore.riskAlerts.slice(0, 5)" 
            :key="alert.id" 
            class="alert-item"
            :class="alert.severity"
          >
            <div class="alert-icon">
              {{ alert.severity === 'high' ? '🔴' : alert.severity === 'medium' ? '🟡' : '🟢' }}
            </div>
            <div class="alert-content">
              <div class="alert-title">{{ alert.title }}</div>
              <div class="alert-message">{{ alert.message }}</div>
              <div class="alert-suggestion" v-if="alert.suggested_action">
                建议: {{ alert.suggested_action }}
              </div>
            </div>
            <button 
              v-if="!alert.is_acknowledged" 
              class="ack-btn"
              @click="acknowledgeAlert(alert.id)"
            >
              知道了
            </button>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-header">
          <h2>最近AI信号</h2>
          <router-link to="/ai" class="view-all">查看全部</router-link>
        </div>
        <div v-if="aiStore.aiSignals.length === 0" class="empty-state">
          暂无AI信号，点击上方生成
        </div>
        <div v-else class="signals-list">
          <div 
            v-for="signal in aiStore.aiSignals.slice(0, 5)" 
            :key="signal.id" 
            class="signal-item"
          >
            <div class="signal-header">
              <span class="symbol">{{ signal.symbol }}</span>
              <span class="direction" :class="signal.direction">
                {{ signal.direction === 'long' ? '做多' : '做空' }}
              </span>
              <span class="confidence" :class="getConfidenceClass(signal.confidence)">
                {{ signal.confidence }}% 置信度
              </span>
            </div>
            <div class="signal-details">
              <div class="detail">
                <span>入场</span>
                <span>${{ signal.entry_price?.toLocaleString() }}</span>
              </div>
              <div class="detail">
                <span>止盈</span>
                <span class="take-profit">${{ signal.take_profit?.toLocaleString() }}</span>
              </div>
              <div class="detail">
                <span>止损</span>
                <span class="stop-loss">${{ signal.stop_loss?.toLocaleString() }}</span>
              </div>
            </div>
            <div class="signal-status" :class="signal.status">
              {{ signal.status === 'active' ? '进行中' : '已关闭' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAIStore } from '@/stores/ai'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const aiStore = useAIStore()
const toast = useToast()

async function generateSignal() {
  try {
    await aiStore.generateSignal({
      symbol: 'BTC',
      strategy: 'technical',
      risk_level: 'medium'
    })
    toast.success('AI信号生成成功')
  } catch (e: any) {
    toast.error(e.message || '生成信号失败')
  }
}

async function checkAlerts() {
  try {
    await aiStore.checkRiskAlerts()
    toast.success('已检查最新风险预警')
  } catch (e: any) {
    toast.error(e.message || '检查预警失败')
  }
}

async function acknowledgeAlert(alertId: number) {
  try {
    await aiStore.acknowledgeAlert(alertId)
  } catch (e: any) {
    toast.error(e.message || '操作失败')
  }
}

function getConfidenceClass(confidence: number) {
  if (confidence >= 80) return 'high'
  if (confidence >= 60) return 'medium'
  return 'low'
}

onMounted(async () => {
  await aiStore.loadAISignals()
  await aiStore.loadRiskAlerts()
})
</script>

<style scoped>
.ai-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.ai-header {
  margin-bottom: 32px;
}

.ai-header h1 {
  font-size: 32px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.subtitle {
  color: var(--text-secondary);
  margin: 0;
}

.ai-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.ai-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s;
}

.ai-card:hover {
  transform: translateY(-4px);
  border-color: var(--primary);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.card-icon {
  font-size: 40px;
  margin-bottom: 16px;
}

.ai-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.ai-card p {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.card-action {
  color: var(--primary);
  font-weight: 500;
  font-size: 14px;
}

.ai-sections {
  display: grid;
  gap: 24px;
}

.section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.refresh-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: var(--bg-secondary);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.view-all {
  color: var(--primary);
  text-decoration: none;
  font-size: 14px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  border-radius: 8px;
  align-items: flex-start;
}

.alert-item.high {
  background: rgba(239, 68, 68, 0.1);
  border-left: 4px solid var(--danger);
}

.alert-item.medium {
  background: rgba(251, 191, 36, 0.1);
  border-left: 4px solid #fbbf24;
}

.alert-item.low {
  background: rgba(34, 197, 94, 0.1);
  border-left: 4px solid var(--success);
}

.alert-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.alert-message {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 4px;
}

.alert-suggestion {
  color: var(--primary);
  font-size: 13px;
}

.ack-btn {
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  flex-shrink: 0;
}

.ack-btn:hover {
  background: var(--bg-secondary);
}

.signals-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.signal-item {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.signal-header {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.symbol {
  font-weight: 600;
  color: var(--text-primary);
}

.direction {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.direction.long {
  background: rgba(34, 197, 94, 0.1);
  color: var(--success);
}

.direction.short {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
}

.confidence {
  font-size: 12px;
  font-weight: 500;
}

.confidence.high {
  color: var(--success);
}

.confidence.medium {
  color: #fbbf24;
}

.confidence.low {
  color: var(--danger);
}

.signal-details {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
}

.detail {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail span:first-child {
  font-size: 12px;
  color: var(--text-secondary);
}

.detail span:last-child {
  font-weight: 500;
  color: var(--text-primary);
}

.take-profit {
  color: var(--success) !important;
}

.stop-loss {
  color: var(--danger) !important;
}

.signal-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  display: inline-block;
}

.signal-status.active {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.signal-status.closed {
  background: rgba(156, 163, 175, 0.1);
  color: #9ca3af;
}
</style>
