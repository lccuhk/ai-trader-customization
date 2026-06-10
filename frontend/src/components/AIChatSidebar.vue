<template>
  <transition name="slide">
    <div v-if="visible" class="ai-chat-overlay">
      <div class="ai-chat-sidebar" @click.stop>
        <div class="chat-header">
          <span class="header-title">🤖 {{ $t('ai.chat.title') }}</span>
          <button class="close-btn" @click="close">✕</button>
        </div>

        <div class="chat-messages" ref="messagesRef">
          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            class="message"
            :class="msg.role"
          >
            <div class="msg-avatar">{{ msg.role === 'assistant' ? '🤖' : '👤' }}</div>
            <div class="msg-content" v-html="renderMessage(msg.content)"></div>
          </div>
          <!-- Order Confirmation Card -->
          <div v-if="pendingOrder" class="order-confirm-card">
            <div class="confirm-header">📋 {{ $t('trading.orderConfirm') }}</div>
            <div class="confirm-details">
              <div class="confirm-row">
                <span class="confirm-label">{{ $t('trading.symbol') }}</span>
                <span class="confirm-value">{{ pendingOrder.symbol }}</span>
              </div>
              <div class="confirm-row">
                <span class="confirm-label">{{ $t('trading.side') }}</span>
                <span class="confirm-value" :class="pendingOrder.side">{{ pendingOrder.side === 'buy' ? $t('trading.buy') : $t('trading.sell') }}</span>
              </div>
              <div class="confirm-row">
                <span class="confirm-label">{{ $t('trading.type') }}</span>
                <span class="confirm-value">{{ pendingOrder.type === 'market' ? $t('trading.market') : $t('trading.limit') }}</span>
              </div>
              <div class="confirm-row">
                <span class="confirm-label">{{ $t('trading.quantity') }}</span>
                <span class="confirm-value">{{ pendingOrder.quantity }}</span>
              </div>
              <div class="confirm-row" v-if="pendingOrder.price">
                <span class="confirm-label">{{ $t('trading.price') }}</span>
                <span class="confirm-value">${{ pendingOrder.price.toLocaleString() }}</span>
              </div>
              <div class="confirm-row">
                <span class="confirm-label">{{ $t('common.mode') }}</span>
                <span class="confirm-value">{{ tradingMode === 'sim' ? $t('trading.simulation') : $t('trading.real') }}</span>
              </div>
            </div>
            <div class="confirm-actions">
              <button class="confirm-cancel" @click="cancelOrder">{{ $t('common.cancel') }}</button>
              <button class="confirm-submit" @click="executeOrder">✓ {{ $t('trading.confirmOrder') }}</button>
            </div>
          </div>
        </div>

        <div class="quick-actions">
          <button
            v-for="action in aiQuickActions"
            :key="action.command"
            class="quick-btn"
            @click="sendQuickAction(action.command)"
          >
            {{ $t(action.labelKey) }}
          </button>
        </div>

        <div class="chat-input-area">
          <input
            v-model="inputText"
            class="chat-input"
            :placeholder="$t('ai.chat.placeholder')"
            @keyup.enter="sendMessage"
          />
          <button class="send-btn" @click="sendMessage" :disabled="!inputText.trim()">
            ↵
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { aiWelcomeMessage, aiQuickActions, aiResponseKeys } from '@/data/mockData'
import { useTradingStore } from '@/stores/trading'

const props = defineProps<{
  visible: boolean
  tradingMode: 'sim' | 'live'
}>()

const emit = defineEmits<{
  'close': []
}>()

const { t } = useI18n()
const tradingStore = useTradingStore()
const messages = ref<{ role: 'user' | 'assistant'; content: string }[]>([
  { role: aiWelcomeMessage.role, content: t(aiWelcomeMessage.contentKey) }
])
const inputText = ref('')
const messagesRef = ref<HTMLElement | null>(null)

// Pending order state
interface PendingOrder {
  symbol: string
  side: 'buy' | 'sell'
  type: 'market' | 'limit'
  quantity: number
  price?: number
}
const pendingOrder = ref<PendingOrder | null>(null)

async function scrollToBottom() {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

async function addMessage(role: 'user' | 'assistant', content: string) {
  messages.value.push({ role, content })
  await scrollToBottom()
}

function renderMessage(content: string): string {
  return content
    .replace(/^### (.*)$/gm, '<strong>$1</strong>')
    .replace(/^## (.*)$/gm, '<strong>$1</strong>')
    .replace(/^# (.*)$/gm, '<strong>$1</strong>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

const knownSymbols = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOT', 'LINK', 'AVAX', 'MATIC']

const chineseNumerals: Record<string, number> = {
  '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
  '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
  '两': 2,
}

function parseOrderIntent(text: string): PendingOrder | null {
  const lower = text.toLowerCase().trim()

  // Detect side — search anywhere in the text
  let side: 'buy' | 'sell' | null = null
  if (/(buy|买入|做多)/i.test(lower)) side = 'buy'
  else if (/(sell|卖出|做空)/i.test(lower)) side = 'sell'
  // Single-character 买/卖 need word-boundary-like check (avoid matching 买卖)
  else if (/买/i.test(lower) && !/卖/i.test(lower)) side = 'buy'
  else if (/卖/i.test(lower) && !/买/i.test(lower)) side = 'sell'

  if (!side) return null

  // Detect order type
  let type: 'market' | 'limit' = 'market'
  if (/(limit|限价|limit)/i.test(lower)) type = 'limit'

  // Extract symbol
  let symbol: string | null = null
  for (const sym of knownSymbols) {
    if (new RegExp('\\b' + sym + '\\b', 'i').test(lower)) {
      symbol = sym + '/USDT'
      break
    }
  }
  if (!symbol) return null

  // Extract quantity
  let quantity: number | null = null

  // Try Arabic digits first
  const numRegex = /(\d+\.?\d*)/g
  const numbers = [...lower.matchAll(numRegex)].map(m => parseFloat(m[1]))

  // Check for limit price with "at $X" pattern
  let price: number | undefined
  const atPriceRegex = /(?:at|@|price|价|价格)\s*\$?\s*(\d+\.?\d*)/i
  const atMatch = lower.match(atPriceRegex)
  if (atMatch) {
    price = parseFloat(atMatch[1])
    const priceIdx = numbers.indexOf(price)
    if (priceIdx > -1) numbers.splice(priceIdx, 1)
  }

  if (numbers.length > 0) {
    quantity = numbers[0]
  }

  // No Arabic digits found — try Chinese numeral (一 → 1)
  if (!quantity) {
    for (const [cn, val] of Object.entries(chineseNumerals)) {
      if (lower.includes(cn)) {
        quantity = val
        break
      }
    }
  }

  // Default to 1 if no quantity found but we have a symbol + side
  if (!quantity) quantity = 1

  return { symbol, side, type, quantity, price }
}

function getOrderConfirmationMessage(order: PendingOrder): string {
  const mode = props.tradingMode === 'sim' ? t('trading.simulation') : t('trading.real')
  const sideText = order.side === 'buy' ? t('trading.buy') : t('trading.sell')
  const typeText = order.type === 'market' ? t('trading.market') : t('trading.limit')
  let msg = `${t('ai.chat.orderDetected')}\n\n`
  msg += `${t('trading.symbol')}: ${order.symbol}\n`
  msg += `${t('trading.side')}: ${sideText}\n`
  msg += `${t('trading.type')}: ${typeText}\n`
  msg += `${t('trading.quantity')}: ${order.quantity}\n`
  if (order.price) msg += `${t('trading.price')}: $${order.price.toLocaleString()}\n`
  msg += `${t('common.mode')}: ${mode}\n\n`
  msg += `${t('ai.chat.orderConfirmHint')}`
  return msg
}

function cancelOrder() {
  pendingOrder.value = null
}

async function executeOrder() {
  if (!pendingOrder.value) return
  const order = pendingOrder.value
  pendingOrder.value = null

  // Default price for market orders (for display purposes)
  const orderPrice = order.price || 66000

  try {
    // Try API first; if backend unavailable, add directly to store
    const result = await tradingStore.createOrder({
      symbol: order.symbol,
      side: order.side,
      type: order.type,
      quantity: order.quantity,
      price: orderPrice,
      is_simulation: props.tradingMode === 'sim',
    }).catch(() => null)

    if (!result) {
      // Backend not running — add order directly to store so it appears in UI
      tradingStore.addOrder({
        id: Date.now() + Math.floor(Math.random() * 1000),
        symbol: order.symbol,
        side: order.side,
        type: order.type,
        quantity: order.quantity,
        price: orderPrice,
        status: order.type === 'market' ? 'filled' : 'open',
        is_simulation: props.tradingMode === 'sim',
        created_at: new Date().toISOString(),
        user_id: 1,
      } as any)
    }

    const mode = props.tradingMode === 'sim' ? t('trading.simulation') : t('trading.real')
    addMessage('assistant', `✅ ${t('ai.chat.orderSuccess')} (${mode})`)
  } catch (e: any) {
    addMessage('assistant', `❌ ${t('ai.chat.orderFailed')}: ${e.message || ''}`)
  }
}

function sendQuickAction(command: string) {
  addMessage('user', command)
  const responseKey = aiResponseKeys[command]
  const response = responseKey ? t(responseKey) : t('ai.chat.fallbackUnknown')
  setTimeout(() => {
    addMessage('assistant', response)
  }, 500)
}

function sendMessage() {
  const text = inputText.value.trim()
  if (!text) return
  inputText.value = ''
  addMessage('user', text)

  // Check for order intent first
  const parsed = parseOrderIntent(text)
  if (parsed) {
    pendingOrder.value = parsed
    addMessage('assistant', getOrderConfirmationMessage(parsed))
    return
  }

  // Fall back to quick action matching
  const matchedAction = aiQuickActions.find(a => text.includes(a.command))
  setTimeout(() => {
    const response = matchedAction
      ? t(aiResponseKeys[matchedAction.command] || 'ai.chat.fallbackProcessing')
      : t('ai.chat.fallbackLearning')
    addMessage('assistant', response)
  }, 500)
}

function close() {
  pendingOrder.value = null
  emit('close')
}
</script>

<style scoped>
.ai-chat-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
}

.ai-chat-sidebar {
  width: 380px;
  height: 100vh;
  background: var(--bg-primary);
  border-left: 2px solid var(--border-color);
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 2px solid var(--border-color);
}

.header-title {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.03em;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}
.close-btn:hover {
  background: var(--danger-color);
  border-color: var(--danger-color);
  color: white;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  gap: 12px;
  max-width: 100%;
}

.message.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--border-color);
  font-size: 16px;
}

.msg-content {
  padding: 10px 14px;
  background: var(--bg-secondary);
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
  max-width: 280px;
  border: 1px solid var(--border-color);
}

.message.user .msg-content {
  background: var(--text-primary);
  color: var(--bg-primary);
  border-color: var(--text-primary);
}

.quick-actions {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
}

.quick-btn {
  flex: 1;
  padding: 8px 12px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  transition: all 0.1s ease;
}
.quick-btn:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}

.chat-input-area {
  display: flex;
  gap: 0;
  padding: 16px;
  border-top: 2px solid var(--border-color);
}

.chat-input {
  flex: 1;
  padding: 10px 14px;
  border: 2px solid var(--border-color);
  border-right: none;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
}
.chat-input:focus {
  border-color: var(--success-color);
}

.send-btn {
  padding: 10px 16px;
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 16px;
  cursor: pointer;
  font-weight: 700;
}
.send-btn:hover:not(:disabled) {
  background: var(--success-color);
  border-color: var(--success-color);
  color: white;
}
.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Order Confirmation Card */
.order-confirm-card {
  border: 2px solid var(--success-color);
  background: var(--bg-secondary);
  padding: 12px;
}

.confirm-header {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.confirm-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.confirm-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.confirm-label {
  color: var(--text-secondary);
}

.confirm-value {
  color: var(--text-primary);
  font-weight: 600;
}

.confirm-value.buy {
  color: var(--success-color);
}

.confirm-value.sell {
  color: var(--danger-color);
}

.confirm-actions {
  display: flex;
  gap: 8px;
}

.confirm-cancel {
  flex: 1;
  padding: 8px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
}

.confirm-cancel:hover {
  background: var(--text-primary);
  color: var(--bg-primary);
}

.confirm-submit {
  flex: 1;
  padding: 8px;
  border: 2px solid var(--success-color);
  background: var(--success-color);
  color: var(--bg-primary);
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  text-transform: uppercase;
}

.confirm-submit:hover {
  background: transparent;
  color: var(--success-color);
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.2s ease;
}
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
}
.slide-enter-from .ai-chat-sidebar,
.slide-leave-to .ai-chat-sidebar {
  transform: translateX(100%);
}
</style>
