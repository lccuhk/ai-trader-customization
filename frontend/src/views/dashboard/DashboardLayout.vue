<template>
  <div class="dashboard-layout">
    <!-- Left Sidebar Navigation -->
    <SidebarNav :activeNav="activeNav" @update:activeNav="activeNav = $event" />

    <!-- Main Content Area -->
    <div class="main-column">
      <!-- Top Bar: User Assets -->
      <div class="top-bar">
        <div class="asset-display">
          <span class="asset-label">{{ $t('portfolio.totalAssets') }}</span>
          <span class="asset-value">${{ toLocale(headerAssets.totalValue) }}</span>
          <span class="asset-detail">
            {{ $t('trading.available') }} ${{ toLocale(headerAssets.available) }}
            <span v-if="headerAssets.unrealizedPnL >= 0" class="positive">+${{ toLocale(headerAssets.unrealizedPnL) }}</span>
            <span v-else class="negative">-${{ toLocale(Math.abs(headerAssets.unrealizedPnL)) }}</span>
          </span>
        </div>
        <div class="top-bar-right">
          <div class="mode-switch">
            <button
              class="mode-switch-btn"
              :class="{ active: tradingMode === 'sim' }"
              @click="tradingMode = 'sim'"
            >{{ $t('trading.simulation') }}</button>
            <button
              class="mode-switch-btn live"
              :class="{ active: tradingMode === 'live' }"
              @click="tradingMode = 'live'"
            >{{ $t('trading.real') }}</button>
          </div>
          <button class="logout-btn" @click="showLogoutConfirm = true">{{ $t('nav.logout') }}</button>
        </div>
      </div>

      <!-- Logout Confirmation Dialog -->
      <div v-if="showLogoutConfirm" class="dialog-overlay" @click="showLogoutConfirm = false">
        <div class="dialog-box" @click.stop>
          <div class="dialog-title">{{ $t('common.confirm') }}</div>
          <div class="dialog-body">{{ $t('auth.confirmLogout') }}</div>
          <div class="dialog-actions">
            <button class="dialog-btn cancel" @click="showLogoutConfirm = false">{{ $t('common.cancel') }}</button>
            <button class="dialog-btn confirm" @click="handleLogout">{{ $t('nav.logout') }}</button>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <main class="main-area">
        <TradingHub v-if="activeNav === 'trading'" :trading-mode="tradingMode" />
        <SignalSquare v-if="activeNav === 'signals'" />
        <StrategyCenter v-if="activeNav === 'strategy'" />
        <MarketIntelligence v-if="activeNav === 'market'" />
        <RiskCenter v-if="activeNav === 'risk'" v-model:tradingMode="tradingMode" />
        <SettingsPage v-if="activeNav === 'settings'" />
      </main>

      <!-- Bottom Status Bar -->
      <div class="status-bar">
        <span class="status-item">{{ $t('common.connected') }}: <span class="connected">●</span></span>
        <span class="status-item">{{ $t('common.lastUpdate') }}: {{ lastUpdate }}</span>
        <span class="status-item">{{ $t('common.mode') }}: {{ tradingMode === 'sim' ? $t('common.simMode') : $t('common.liveMode') }}</span>
      </div>
    </div>

    <!-- Right Quick Info Panel -->
    <QuickInfoPanel />

    <!-- AI Floating Button -->
    <button class="ai-float-btn" @click="showAIChat = true">
      <span class="ai-float-icon">AI</span>
    </button>

    <!-- AI Chat Sidebar -->
    <AIChatSidebar :visible="showAIChat" :trading-mode="tradingMode" @close="showAIChat = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
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
import { userAssets, liveUserAssets } from '@/data/mockData'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const activeNav = ref('trading')
const showAIChat = ref(false)
const showLogoutConfirm = ref(false)
const lastUpdate = ref(new Date().toLocaleTimeString())
const tradingMode = ref<'sim' | 'live'>('sim')

const headerAssets = computed(() =>
  tradingMode.value === 'sim' ? userAssets : liveUserAssets
)

function toLocale(n: number): string {
  return n.toLocaleString()
}

function handleLogout() {
  const userStore = useUserStore()
  userStore.logout()
  showLogoutConfirm.value = false
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

.mode-switch {
  display: flex;
  gap: 0;
  border: 2px solid var(--border-color);
}

.mode-switch-btn {
  padding: 4px 14px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  transition: all 0.1s ease;
}
.mode-switch-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}
.mode-switch-btn.active {
  background: var(--success-color);
  color: white;
}
.mode-switch-btn.live.active {
  background: var(--danger-color);
  color: white;
}
.mode-switch-btn + .mode-switch-btn {
  border-left: 2px solid var(--border-color);
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

/* Logout Confirmation Dialog */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog-box {
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  width: 360px;
  padding: 24px;
  box-shadow: 8px 8px 0 rgba(0, 0, 0, 0.15);
}

.dialog-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 12px;
  letter-spacing: 0.03em;
}

.dialog-body {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 20px;
}

.dialog-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.dialog-btn {
  padding: 8px 20px;
  border: 2px solid var(--border-color);
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  transition: all 0.1s ease;
}
.dialog-btn.cancel {
  background: transparent;
  color: var(--text-primary);
}
.dialog-btn.cancel:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}
.dialog-btn.confirm {
  background: var(--danger-color);
  border-color: var(--danger-color);
  color: white;
}
.dialog-btn.confirm:hover {
  background: transparent;
  color: var(--danger-color);
}
</style>
