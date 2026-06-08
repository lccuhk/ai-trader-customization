<template>
  <div class="export-view">
    <div class="page-header">
      <h1>📥 数据导出</h1>
    </div>
    
    <div class="export-cards">
      <div class="export-card">
        <div class="card-icon">📊</div>
        <h3>交易历史</h3>
        <p>导出你的所有交易记录，包括买入卖出详情</p>
        <button class="btn btn-primary" @click="exportTradingHistory">导出交易历史</button>
      </div>
      
      <div class="export-card">
        <div class="card-icon">📈</div>
        <h3>持仓报告</h3>
        <p>导出当前持仓情况和收益报告</p>
        <button class="btn btn-primary" @click="exportPortfolio">导出持仓报告</button>
      </div>
      
      <div class="export-card">
        <div class="card-icon">💡</div>
        <h3>信号数据</h3>
        <p>导出你收藏和发布的所有交易信号</p>
        <button class="btn btn-primary" @click="exportSignals">导出信号数据</button>
      </div>
      
      <div class="export-card">
        <div class="card-icon">📋</div>
        <h3>完整数据</h3>
        <p>导出所有可用数据的完整备份</p>
        <button class="btn btn-secondary" @click="exportAllData">导出全部数据</button>
      </div>
    </div>
    
    <div class="export-formats">
      <h3>导出格式</h3>
      <div class="format-options">
        <label class="format-option">
          <input type="radio" v-model="exportFormat" value="json" />
          <span>JSON</span>
        </label>
        <label class="format-option">
          <input type="radio" v-model="exportFormat" value="csv" />
          <span>CSV</span>
        </label>
      </div>
    </div>
    
    <div v-if="exportStatus" class="export-status">
      {{ exportStatus }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const exportFormat = ref('json')
const exportStatus = ref('')

function exportTradingHistory() {
  const mockData = [
    { id: 1, symbol: 'AAPL', action: 'BUY', price: 180, quantity: 10, date: '2024-01-15' },
    { id: 2, symbol: 'NVDA', action: 'BUY', price: 480, quantity: 5, date: '2024-01-14' },
    { id: 3, symbol: 'TSLA', action: 'SELL', price: 240, quantity: 8, date: '2024-01-13' }
  ]
  downloadFile(mockData, 'trading-history')
  showSuccess('交易历史已导出')
}

function exportPortfolio() {
  const mockData = [
    { symbol: 'AAPL', quantity: 50, avgPrice: 175, currentPrice: 180, pnl: 250 },
    { symbol: 'NVDA', quantity: 25, avgPrice: 450, currentPrice: 480, pnl: 750 },
    { symbol: 'MSFT', quantity: 30, avgPrice: 370, currentPrice: 375, pnl: 150 }
  ]
  downloadFile(mockData, 'portfolio-report')
  showSuccess('持仓报告已导出')
}

function exportSignals() {
  const mockData = [
    { id: 1, title: 'NVDA 突破分析', agent: '量化先锋', quality: 85 },
    { id: 2, title: 'AAPL 买入机会', agent: '趋势追踪者', quality: 78 },
    { id: 3, title: 'BTC 减半行情', agent: '加密猎人', quality: 92 }
  ]
  downloadFile(mockData, 'signals-data')
  showSuccess('信号数据已导出')
}

function exportAllData() {
  const allData = {
    trading: [
      { id: 1, symbol: 'AAPL', action: 'BUY', price: 180, quantity: 10, date: '2024-01-15' }
    ],
    portfolio: [
      { symbol: 'AAPL', quantity: 50, avgPrice: 175, currentPrice: 180, pnl: 250 }
    ],
    signals: [
      { id: 1, title: 'NVDA 突破分析', agent: '量化先锋', quality: 85 }
    ]
  }
  downloadFile(allData, 'complete-data-backup')
  showSuccess('完整数据已导出')
}

function downloadFile(data: any, filename: string) {
  let content: string
  let extension: string
  let mimeType: string
  
  if (exportFormat.value === 'json') {
    content = JSON.stringify(data, null, 2)
    extension = 'json'
    mimeType = 'application/json'
  } else {
    content = convertToCSV(data)
    extension = 'csv'
    mimeType = 'text/csv'
  }
  
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${filename}-${new Date().toISOString().split('T')[0]}.${extension}`
  a.click()
  URL.revokeObjectURL(url)
}

function convertToCSV(data: any) {
  if (Array.isArray(data) && data.length > 0) {
    const headers = Object.keys(data[0])
    const rows = [headers.join(',')]
    for (const item of data) {
      rows.push(headers.map(h => item[h]).join(','))
    }
    return rows.join('\n')
  }
  return JSON.stringify(data)
}

function showSuccess(message: string) {
  exportStatus.value = `✅ ${message}`
  setTimeout(() => {
    exportStatus.value = ''
  }, 3000)
}
</script>

<style scoped>
.export-view {
  padding: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header h1 {
  margin: 0 0 32px 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.export-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.export-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  transition: all 0.2s;
}

.export-card:hover {
  border-color: var(--accent-color);
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.1);
  transform: translateY(-2px);
}

.card-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.export-card h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.export-card p {
  margin: 0 0 20px 0;
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
}

.export-formats {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.export-formats h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.format-options {
  display: flex;
  gap: 24px;
}

.format-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 15px;
  color: var(--text-primary);
}

.format-option input {
  width: 18px;
  height: 18px;
  accent-color: var(--accent-color);
}

.export-status {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  padding: 12px 16px;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  width: 100%;
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
</style>
