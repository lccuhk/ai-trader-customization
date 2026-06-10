<template>
  <div class="settings-page">
    <div class="page-title">&gt; 设置</div>

    <div class="settings-grid">
      <div class="panel">
        <div class="panel-header"><span class="panel-title">通用</span></div>
        <div class="panel-body">
          <div class="setting-row">
            <span class="setting-label">语言</span>
            <select class="setting-input">
              <option>简体中文</option>
              <option>English</option>
            </select>
          </div>
          <div class="setting-row">
            <span class="setting-label">主题</span>
            <select class="setting-input">
              <option>跟随系统</option>
              <option>浅色</option>
              <option>深色</option>
            </select>
          </div>
          <div class="setting-row">
            <span class="setting-label">模拟模式</span>
            <span class="setting-status active">● 运行中</span>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header"><span class="panel-title">API</span></div>
        <div class="panel-body">
          <div class="setting-row">
            <span class="setting-label">交易所</span>
            <span class="setting-value">币安 (模拟)</span>
          </div>
          <div class="setting-row">
            <span class="setting-label">API Key</span>
            <span class="setting-value muted">••••••••••••••••</span>
          </div>
          <button class="action-btn" @click="alert('API 设置')">管理 API</button>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header"><span class="panel-title">通知</span></div>
        <div class="panel-body">
          <div class="setting-row">
            <span class="setting-label">交易提醒</span>
            <span class="setting-status active">● 已开启</span>
          </div>
          <div class="setting-row">
            <span class="setting-label">风险预警</span>
            <span class="setting-status active">● 已开启</span>
          </div>
          <div class="setting-row">
            <span class="setting-label">信号推送</span>
            <span class="setting-status">○ 已关闭</span>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header"><span class="panel-title">风控偏好</span></div>
        <div class="panel-body">
          <div class="setting-row">
            <span class="setting-label">单笔风险上限</span>
            <span class="setting-value">2.5%</span>
          </div>
          <div class="setting-row">
            <span class="setting-label">最大杠杆</span>
            <span class="setting-value">3x</span>
          </div>
          <div class="setting-row">
            <span class="setting-label">自动止损</span>
            <span class="setting-status active">● 已开启</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

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
</style>
