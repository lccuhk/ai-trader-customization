<template>
  <transition name="slide">
    <div v-if="visible" class="ai-chat-overlay">
      <div class="ai-chat-sidebar" @click.stop>
        <div class="chat-header">
          <span class="header-title">🤖 AI 交易助手</span>
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
        </div>

        <div class="quick-actions">
          <button
            v-for="action in aiQuickActions"
            :key="action.command"
            class="quick-btn"
            @click="sendQuickAction(action.command)"
          >
            {{ action.label }}
          </button>
        </div>

        <div class="chat-input-area">
          <input
            v-model="inputText"
            class="chat-input"
            placeholder="输入消息..."
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
import { ref, nextTick, watch } from 'vue'
import { aiWelcomeMessage, aiQuickActions, aiResponses } from '@/data/mockData'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  'close': []
}>()

const messages = ref<{ role: 'user' | 'assistant'; content: string }[]>([aiWelcomeMessage])
const inputText = ref('')
const messagesRef = ref<HTMLElement | null>(null)

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
  // Simple markdown-like rendering
  return content
    .replace(/^### (.*)$/gm, '<strong>$1</strong>')
    .replace(/^## (.*)$/gm, '<strong>$1</strong>')
    .replace(/^# (.*)$/gm, '<strong>$1</strong>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

function sendQuickAction(command: string) {
  addMessage('user', command)
  const response = aiResponses[command] || '抱歉，我不太理解你的问题。'
  setTimeout(() => {
    addMessage('assistant', response)
  }, 500)
}

function sendMessage() {
  const text = inputText.value.trim()
  if (!text) return
  inputText.value = ''
  addMessage('user', text)

  // Check if it matches any quick action
  const matchedAction = aiQuickActions.find(a => text.includes(a.command) || text.includes(a.label))
  setTimeout(() => {
    const response = matchedAction
      ? (aiResponses[matchedAction.command] || '处理中...')
      : '🤔 我还在学习中，请试试快捷按钮吧！\n\n你可以输入 /风险、/市场 或 /信号 来获取对应的分析。'
    addMessage('assistant', response)
  }, 500)
}

function close() {
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
