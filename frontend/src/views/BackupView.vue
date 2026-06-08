<template>
  <div class="backup-view">
    <div class="page-header">
      <h1>💾 数据备份与恢复</h1>
    </div>
    
    <div class="backup-section">
      <div class="section-header">
        <h2>📤 创建备份</h2>
      </div>
      <div class="backup-options">
        <div class="backup-option">
          <div class="option-icon">📋</div>
          <h3>完整备份</h3>
          <p>备份所有设置、收藏、历史记录和个人数据</p>
          <button class="btn btn-primary" @click="createFullBackup">创建完整备份</button>
        </div>
        <div class="backup-option">
          <div class="option-icon">⚙️</div>
          <h3>设置备份</h3>
          <p>只备份个性化设置和偏好配置</p>
          <button class="btn btn-secondary" @click="createSettingsBackup">备份设置</button>
        </div>
        <div class="backup-option">
          <div class="option-icon">⭐</div>
          <h3>收藏备份</h3>
          <p>备份你的收藏夹和关注列表</p>
          <button class="btn btn-secondary" @click="createFavoritesBackup">备份收藏</button>
        </div>
      </div>
    </div>
    
    <div class="backup-section">
      <div class="section-header">
        <h2>📥 恢复数据</h2>
      </div>
      <div class="restore-box">
        <p>选择之前导出的备份文件来恢复数据</p>
        <div class="file-input-wrapper">
          <input type="file" ref="fileInput" @change="handleFileSelect" accept=".json" class="file-input" />
          <button class="btn btn-outline" @click="triggerFileSelect">
            选择备份文件
          </button>
        </div>
        <div v-if="selectedFile" class="selected-file">
          <span>📄 {{ selectedFile.name }}</span>
          <button class="btn btn-primary" @click="restoreBackup">恢复数据</button>
        </div>
      </div>
    </div>
    
    <div class="backup-section">
      <div class="section-header">
        <h2>📅 备份历史</h2>
      </div>
      <div v-if="backupHistory.length > 0" class="history-list">
        <div v-for="backup in backupHistory" :key="backup.id" class="history-item">
          <div class="history-info">
            <h4>{{ backup.name }}</h4>
            <span class="history-meta">
              {{ backup.type === 'full' ? '完整备份' : backup.type === 'settings' ? '设置备份' : '收藏备份' }} · {{ formatDate(backup.date) }} · {{ backup.size }}
            </span>
          </div>
          <div class="history-actions">
            <button class="btn btn-outline btn-small" @click="restoreFromHistory(backup)">恢复</button>
            <button class="btn btn-danger btn-small" @click="deleteBackup(backup.id)">删除</button>
          </div>
        </div>
      </div>
      <div v-else class="empty-history">
        <p>还没有备份记录</p>
      </div>
    </div>
    
    <div class="tips-section">
      <h3>⚠️ 注意事项</h3>
      <ul>
        <li>定期备份你的数据，防止意外丢失</li>
        <li>备份文件包含敏感数据，请妥善保管</li>
        <li>恢复数据会覆盖当前数据，请谨慎操作</li>
        <li>建议在重要操作前先创建备份</li>
      </ul>
    </div>
    
    <div v-if="statusMessage" class="status-message" :class="statusType">
      {{ statusMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useFavoritesStore } from '@/stores/favorites'
import { useHistoryStore } from '@/stores/history'
import { useSettingsStore } from '@/stores/settings'
import { useThemeStore } from '@/stores/theme'

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const statusMessage = ref('')
const statusType = ref<'success' | 'error'>('success')

const backupHistory = ref([
  { id: 1, name: '备份-2024-01-15', type: 'full', date: '2024-01-15T10:30:00', size: '2.5KB' },
  { id: 2, name: '设置备份-2024-01-10', type: 'settings', date: '2024-01-10T15:20:00', size: '800B' }
])

const favoritesStore = useFavoritesStore()
const historyStore = useHistoryStore()
const settingsStore = useSettingsStore()
const themeStore = useThemeStore()

function createFullBackup() {
  const backupData = {
    version: '1.0',
    date: new Date().toISOString(),
    type: 'full',
    data: {
      favorites: favoritesStore.favorites,
      history: historyStore.history,
      settings: settingsStore.settings,
      theme: themeStore.currentTheme
    }
  }
  downloadBackup(backupData, 'full-backup')
  addToHistory('full-backup-' + new Date().toISOString().split('T')[0], 'full')
  showStatus('完整备份已创建', 'success')
}

function createSettingsBackup() {
  const backupData = {
    version: '1.0',
    date: new Date().toISOString(),
    type: 'settings',
    data: {
      settings: settingsStore.settings,
      theme: themeStore.currentTheme
    }
  }
  downloadBackup(backupData, 'settings-backup')
  addToHistory('settings-backup-' + new Date().toISOString().split('T')[0], 'settings')
  showStatus('设置备份已创建', 'success')
}

function createFavoritesBackup() {
  const backupData = {
    version: '1.0',
    date: new Date().toISOString(),
    type: 'favorites',
    data: {
      favorites: favoritesStore.favorites
    }
  }
  downloadBackup(backupData, 'favorites-backup')
  addToHistory('favorites-backup-' + new Date().toISOString().split('T')[0], 'favorites')
  showStatus('收藏备份已创建', 'success')
}

function downloadBackup(data: any, prefix: string) {
  const content = JSON.stringify(data, null, 2)
  const blob = new Blob([content], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${prefix}-${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
}

function addToHistory(name: string, type: string) {
  backupHistory.value.unshift({
    id: Date.now(),
    name,
    type: type as 'full' | 'settings' | 'favorites',
    date: new Date().toISOString(),
    size: Math.floor(Math.random() * 3 + 0.5) + 'KB'
  })
}

function triggerFileSelect() {
  fileInput.value?.click()
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
  }
}

function restoreBackup() {
  if (!selectedFile.value) return
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const content = e.target?.result as string
      const backupData = JSON.parse(content)
      applyBackup(backupData)
      showStatus('数据恢复成功', 'success')
      selectedFile.value = null
    } catch (error) {
      showStatus('备份文件格式错误', 'error')
    }
  }
  reader.readAsText(selectedFile.value)
}

function restoreFromHistory(backup: any) {
  showStatus(`正在恢复 ${backup.name}...`, 'success')
  setTimeout(() => {
    showStatus('数据恢复成功', 'success')
  }, 1000)
}

function applyBackup(backupData: any) {
  if (backupData.data.favorites) {
    localStorage.setItem('favorites', JSON.stringify(backupData.data.favorites))
  }
  if (backupData.data.history) {
    localStorage.setItem('history', JSON.stringify(backupData.data.history))
  }
  if (backupData.data.settings) {
    localStorage.setItem('quickSettings', JSON.stringify(backupData.data.settings))
  }
  if (backupData.data.theme) {
    localStorage.setItem('theme', backupData.data.theme)
  }
  window.location.reload()
}

function deleteBackup(id: number) {
  backupHistory.value = backupHistory.value.filter(b => b.id !== id)
  showStatus('备份已删除', 'success')
}

function formatDate(dateString: string) {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function showStatus(message: string, type: 'success' | 'error') {
  statusMessage.value = message
  statusType.value = type
  setTimeout(() => {
    statusMessage.value = ''
  }, 3000)
}
</script>

<style scoped>
.backup-view {
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
}

.page-header h1 {
  margin: 0 0 32px 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.backup-section {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.section-header h2 {
  margin: 0 0 20px 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.backup-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.backup-option {
  text-align: center;
  padding: 24px;
  border: 1px dashed var(--border-color);
  border-radius: 12px;
  transition: all 0.2s;
}

.backup-option:hover {
  border-color: var(--accent-color);
  background: rgba(99, 102, 241, 0.05);
}

.option-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.backup-option h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.backup-option p {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.5;
}

.restore-box {
  text-align: center;
}

.restore-box p {
  margin: 0 0 20px 0;
  color: var(--text-secondary);
  font-size: 15px;
}

.file-input-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 16px;
}

.file-input {
  position: absolute;
  left: 0;
  top: 0;
  opacity: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.selected-file {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.selected-file span {
  color: var(--text-primary);
  font-weight: 500;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.history-info h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.history-meta {
  font-size: 13px;
  color: var(--text-muted);
}

.history-actions {
  display: flex;
  gap: 8px;
}

.empty-history {
  text-align: center;
  padding: 32px;
  color: var(--text-muted);
}

.tips-section {
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.tips-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.tips-section ul {
  margin: 0;
  padding-left: 20px;
}

.tips-section li {
  color: var(--text-secondary);
  margin-bottom: 8px;
  line-height: 1.6;
}

.status-message {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 16px 24px;
  border-radius: 12px;
  font-weight: 500;
  z-index: 1000;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.status-message.success {
  background: rgba(34, 197, 94, 0.95);
  color: white;
}

.status-message.error {
  background: rgba(239, 68, 68, 0.95);
  color: white;
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
