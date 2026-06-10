<template>
  <div class="dashboard-layout">
    <!-- Left Sidebar Navigation -->
    <SidebarNav :activeNav="activeNav" @update:activeNav="activeNav = $event" />

    <!-- Main Content Area -->
    <div class="main-column">
      <!-- Top Bar: User Assets -->
      <div class="top-bar">
        <div class="asset-display">
          <span class="asset-label">总资产</span>
          <span class="asset-value">${{ toLocale(userAssets.totalValue) }}</span>
          <span class="asset-detail">
            可用 ${{ toLocale(userAssets.available) }}
            <span v-if="userAssets.unrealizedPnL >= 0" class="positive">+${{ toLocale(userAssets.unrealizedPnL) }}</span>
            <span v-else class="negative">-${{ toLocale(Math.abs(userAssets.unrealizedPnL)) }}</span>
          </span>
        </div>
        <div class="top-bar-right">
          <span class="sim-badge">模拟</span>
          <button class="logout-btn" @click="handleLogout">退出</button>
        </div>
      </div>

      <!-- Main Content -->
      <main class="main-area">
        <TradingHub v-if="activeNav === 'trading'" />
        <SignalSquare v-if="activeNav === 'signals'" />
        <StrategyCenter v-if="activeNav === 'strategy'" />
        <MarketIntelligence v-if="activeNav === 'market'" />
        <RiskCenter v-if="activeNav === 'risk'" />
        <SettingsPage v-if="activeNav === 'settings'" />
      </main>

      <!-- Bottom Status Bar -->
      <div class="status-bar">
        <span class="status-item">连接: <span class="connected">已连接</span></span>
        <span class="status-item">最后更新: {{ lastUpdate }}</span>
        <span class="status-item">模式: 模拟交易</span>
      </div>
    </div>

    <!-- Right Quick Info Panel -->
    <QuickInfoPanel />

    <!-- AI Floating Button -->
    <button class="ai-float-btn" @click="showAIChat = true">
      <span class="ai-float-icon">AI</span>
    </button>

    <!-- AI Chat Sidebar -->
    <AIChatSidebar :visible="showAIChat" @close="showAIChat = false" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import SidebarNav from '@/components/SidebarNav.vue'
import QuickInfoPanel from '@/components/QuickInfoPanel.vue'
import AIChatSidebar from '@/components/AIChatSidebar.vue'
import TradingHub from './TradingHub.vue'
import SignalSquare from './SignalSquare.vue'
import StrategyCenter from './StrategyCenter.vue'
import MarketIntelligence from './MarketIntelligence.vue'
import RiskCenter from './RiskCenter.vue'
import SettingsPage from './SettingsPage.vue'
import { userAssets } from '@/data/mockData'

const router = useRouter()
const activeNav = ref('trading')
const showAIChat = ref(false)
const lastUpdate = ref(new Date().toLocaleTimeString())

function toLocale(n: number): string {
  return n.toLocaleString()
}

function handleLogout() {
  localStorage.removeItem('auth_token')
  router.push('/login')
}
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-secondary);
}

/* Main Column: top-bar + content + status-bar */
.main-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* Top Bar */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: var(--bg-primary);
  border-bottom: 2px solid var(--border-color);
  height: 56px;
}

.asset-display {
  display: flex;
  align-items: center;
  gap: 16px;
}

.asset-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.asset-value {
  font-size: 22px;
  font-weight: 700;
  font-family: var(--font-mono, monospace);
  color: var(--text-primary);
}

.asset-detail {
  font-size: 12px;
  color: var(--text-secondary);
  font-family: var(--font-mono, monospace);
}

.asset-detail .positive {
  color: var(--success-color);
  font-weight: 600;
}
.asset-detail .negative {
  color: var(--danger-color);
  font-weight: 600;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sim-badge {
  padding: 2px 10px;
  font-size: 11px;
  font-weight: 600;
  border: 2px solid var(--success-color);
  color: var(--success-color);
}

.logout-btn {
  padding: 4px 12px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}
.logout-btn:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}

/* Main Area */
.main-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* Status Bar */
.status-bar {
  display: flex;
  gap: 24px;
  padding: 8px 24px;
  background: var(--bg-primary);
  border-top: 2px solid var(--border-color);
  font-size: 11px;
  color: var(--text-secondary);
  font-family: var(--font-mono, monospace);
}

.status-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.connected {
  color: var(--success-color);
  font-weight: 600;
}

/* AI Float Button */
.ai-float-btn {
  position: fixed;
  bottom: 32px;
  right: 32px;
  width: 52px;
  height: 52px;
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  z-index: 100;
  box-shadow: 4px 4px 0 var(--border-color);
}
.ai-float-btn:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 var(--border-color);
}

.ai-float-icon {
  font-size: 16px;
  font-weight: 700;
  font-family: var(--font-mono, monospace);
}
</style>
