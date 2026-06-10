<template>
  <div class="strategy-center">
    <div class="page-title">&gt; 策略中心</div>

    <!-- My Strategies -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">我的策略</span>
        <button class="create-btn" @click="showCreateModal = true">+ 新建</button>
      </div>
      <div class="panel-body">
        <table class="data-table" v-if="strategies.length">
          <thead>
            <tr>
              <th>名称</th>
              <th>类型</th>
              <th>状态</th>
              <th>收益率</th>
              <th>夏普比率</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in strategies" :key="s.id">
              <td class="strategy-name">{{ s.name }}</td>
              <td class="strategy-type">{{ s.type || '—' }}</td>
              <td>
                <span class="status" :class="s.status">
                  {{ s.status === 'active' ? '运行中' : '已暂停' }}
                </span>
              </td>
              <td :class="s.lastReturn >= 0 ? 'positive' : 'negative'">
                {{ s.lastReturn >= 0 ? '+' : '' }}{{ s.lastReturn }}%
              </td>
              <td>{{ s.sharpe.toFixed(2) }}</td>
              <td>
                <div class="action-group">
                  <button class="action-btn" @click="toggleStrategy(s.id)">
                    {{ s.status === 'active' ? '暂停' : '启动' }}
                  </button>
                  <button class="action-btn delete" @click="deleteStrategy(s.id)">
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty">暂无策略，点击"+ 新建"创建你的第一个策略</div>
      </div>
    </div>

    <!-- Strategy Templates -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">策略模板</span>
      </div>
      <div class="panel-body">
        <div class="templates-grid">
          <div v-for="t in strategyTemplates" :key="t.id" class="template-card">
            <div class="template-name">{{ t.name }}</div>
            <div class="template-tags">
              <span class="tag">{{ t.difficulty }}</span>
              <span class="tag">{{ t.marketType }}</span>
            </div>
            <button class="use-btn" @click="useTemplate(t)">使用模板</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Strategy Modal -->
    <Teleport to="body">
      <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
        <div class="modal-panel">
          <div class="modal-header">
            <span class="modal-title">&gt; 新建策略</span>
            <button class="modal-close" @click="showCreateModal = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>策略名称</label>
              <input
                v-model="newStrategy.name"
                type="text"
                placeholder="输入策略名称..."
                class="form-input"
              />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>策略类型</label>
                <select v-model="newStrategy.type" class="form-input">
                  <option value="趋势跟踪">趋势跟踪</option>
                  <option value="网格交易">网格交易</option>
                  <option value="动量突破">动量突破</option>
                  <option value="均值回归">均值回归</option>
                  <option value="统计套利">统计套利</option>
                </select>
              </div>
              <div class="form-group">
                <label>风险等级</label>
                <select v-model="newStrategy.riskLevel" class="form-input">
                  <option value="低">低 (保守)</option>
                  <option value="中">中 (稳健)</option>
                  <option value="高">高 (激进)</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label>初始资金分配 ($)</label>
              <input
                v-model.number="newStrategy.capital"
                type="number"
                placeholder="1000"
                class="form-input"
                min="100"
                step="100"
              />
            </div>
            <div class="form-group">
              <label>交易标的</label>
              <div class="asset-toggles">
                <button
                  v-for="sym in availableSymbols"
                  :key="sym"
                  class="asset-toggle"
                  :class="{ selected: newStrategy.symbols.includes(sym) }"
                  @click="toggleSymbol(sym)"
                >{{ sym }}</button>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="modal-btn cancel" @click="showCreateModal = false">取消</button>
            <button class="modal-btn confirm" :disabled="!newStrategy.name.trim()" @click="createStrategy">创建策略</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { myStrategies, strategyTemplates } from '@/data/mockData'

const showCreateModal = ref(false)
const availableSymbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT']

const strategies = ref([...myStrategies])

const newStrategy = reactive({
  name: '',
  type: '趋势跟踪',
  riskLevel: '中',
  capital: 1000,
  symbols: [] as string[],
})

let nextId = strategies.value.length + 1

function toggleSymbol(sym: string) {
  const idx = newStrategy.symbols.indexOf(sym)
  if (idx >= 0) {
    newStrategy.symbols.splice(idx, 1)
  } else {
    newStrategy.symbols.push(sym)
  }
}

function createStrategy() {
  if (!newStrategy.name.trim()) return
  // Generate a random return between -5 and +15 for mock
  const mockReturn = Math.round((Math.random() * 20 - 5) * 10) / 10
  const mockSharpe = Math.round((Math.random() * 2 + 0.5) * 100) / 100

  strategies.value.push({
    id: nextId++,
    name: newStrategy.name.trim(),
    type: newStrategy.type,
    status: 'active' as const,
    lastReturn: mockReturn,
    sharpe: mockSharpe,
  })

  // Reset form
  newStrategy.name = ''
  newStrategy.type = '趋势跟踪'
  newStrategy.riskLevel = '中'
  newStrategy.capital = 1000
  newStrategy.symbols = []
  showCreateModal.value = false
}

function toggleStrategy(id: number) {
  const s = strategies.value.find(s => s.id === id)
  if (s) {
    s.status = s.status === 'active' ? 'paused' : 'active'
  }
}

function deleteStrategy(id: number) {
  if (confirm(`确定要删除策略 "${strategies.value.find(s => s.id === id)?.name}" 吗？`)) {
    strategies.value = strategies.value.filter(s => s.id !== id)
  }
}

function useTemplate(t: typeof strategyTemplates[0]) {
  newStrategy.name = t.name
  newStrategy.type = t.name.replace('模板', '').trim()
  showCreateModal.value = true
}
</script>

<style scoped>
.strategy-center {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.panel {
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 2px solid var(--border-color);
  background: var(--bg-secondary);
}

.panel-title {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.create-btn {
  padding: 4px 12px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}
.create-btn:hover {
  background: var(--success-color);
  border-color: var(--success-color);
  color: white;
}

.panel-body {
  padding: 16px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.data-table th {
  text-align: left;
  padding: 8px 10px;
  border-bottom: 2px solid var(--border-color);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--text-secondary);
  font-weight: 600;
}

.data-table td {
  padding: 8px 10px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.strategy-name {
  font-weight: 700;
}

.strategy-type {
  font-size: 11px;
  color: var(--text-secondary);
}

.status {
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid currentColor;
}
.status.active {
  color: var(--success-color);
}
.status.paused {
  color: var(--text-secondary);
}

.positive {
  color: var(--success-color);
  font-weight: 600;
}
.negative {
  color: var(--danger-color);
  font-weight: 600;
}

.action-btn {
  padding: 4px 10px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 11px;
  cursor: pointer;
}
.action-btn:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}
.action-btn.delete {
  color: var(--danger-color);
  border-color: var(--danger-color);
}
.action-btn.delete:hover {
  background: var(--danger-color);
  color: white;
}

.action-group {
  display: flex;
  gap: 4px;
}

.empty {
  text-align: center;
  padding: 32px;
  color: var(--text-secondary);
  font-size: 13px;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}

.template-card {
  padding: 16px;
  border: 2px solid var(--border-color);
  background: var(--bg-secondary);
  transition: all 0.1s ease;
}
.template-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: 3px 3px 0 var(--border-color);
}

.template-name {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 8px;
}

.template-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 12px;
}

.tag {
  padding: 2px 8px;
  font-size: 10px;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.use-btn {
  width: 100%;
  padding: 8px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
}
.use-btn:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}

/* ===== Modal ===== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-panel {
  width: 520px;
  max-width: 90vw;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  box-shadow: 8px 8px 0 rgba(0, 0, 0, 0.4);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 2px solid var(--border-color);
  background: var(--bg-secondary);
}

.modal-title {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.modal-close {
  background: none;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  padding: 2px 8px;
}
.modal-close:hover {
  color: var(--text-primary);
  background: var(--bg-primary);
}

.modal-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.form-input {
  padding: 8px 10px;
  border: 2px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
}
.form-input:focus {
  border-color: var(--success-color);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.asset-toggles {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.asset-toggle {
  padding: 6px 12px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}
.asset-toggle:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}
.asset-toggle.selected {
  background: var(--text-primary);
  color: var(--bg-primary);
  border-color: var(--text-primary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 14px 20px;
  border-top: 2px solid var(--border-color);
  background: var(--bg-secondary);
}

.modal-btn {
  padding: 8px 20px;
  border: 2px solid var(--border-color);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.modal-btn.cancel {
  background: transparent;
  color: var(--text-primary);
}
.modal-btn.cancel:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}
.modal-btn.confirm {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}
.modal-btn.confirm:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
