<template>
  <div class="ai-chat-view">
    <div class="chat-header">
      <h1>AI 对话</h1>
      <button class="clear-btn" @click="clearChat">
        清空对话
      </button>
    </div>

    <div class="chat-container" ref="chatContainer">
      <div v-if="aiStore.chatMessages.length === 0" class="welcome-screen">
        <div class="welcome-icon">🤖</div>
        <h2>你好！我是你的AI交易助手</h2>
        <p>我可以帮你分析市场、解答交易问题、提供策略建议</p>
        <div class="quick-questions">
          <button v-for="q in quickQuestions" :key="q" @click="sendQuickQuestion(q)">
            {{ q }}
          </button>
        </div>
      </div>

      <div 
        v-for="(msg, index) in aiStore.chatMessages" 
        :key="index" 
        class="chat-message"
        :class="msg.role"
      >
        <div class="message-avatar">
          {{ msg.role === 'user' ? '👤' : '🤖' }}
        </div>
        <div class="message-bubble">
          <div class="message-content">{{ msg.content }}</div>
          <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
        </div>
      </div>

      <div v-if="aiStore.loading" class="typing-indicator">
        <div class="dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>

    <div class="chat-input-area">
      <input 
        type="text" 
        v-model="messageInput" 
        placeholder="输入你的问题..."
        @keyup.enter="sendMessage"
        :disabled="aiStore.loading"
      />
      <button @click="sendMessage" :disabled="!messageInput.trim() || aiStore.loading">
        发送
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useAIStore } from '@/stores/ai'
import { useToast } from '@/composables/useToast'

const aiStore = useAIStore()
const toast = useToast()

const messageInput = ref('')
const chatContainer = ref<HTMLElement | null>(null)

const quickQuestions = [
  '分析一下当前BTC的走势',
  '如何设置止损止盈？',
  '推荐一个交易策略',
  '今天有什么交易机会？'
]

async function sendMessage() {
  if (!messageInput.value.trim() || aiStore.loading) return

  const message = messageInput.value.trim()
  messageInput.value = ''

  try {
    await aiStore.chat(message)
    await nextTick()
    scrollToBottom()
  } catch (e: any) {
    toast.error(e.message || '发送失败')
  }
}

function sendQuickQuestion(question: string) {
  messageInput.value = question
  sendMessage()
}

function clearChat() {
  aiStore.clearChat()
}

function formatTime(time: string) {
  return new Date(time).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

function scrollToBottom() {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

watch(() => aiStore.chatMessages.length, () => {
  nextTick(() => scrollToBottom())
})
</script>

<style scoped>
.ai-chat-view {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
  height: calc(100vh - 80px);
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chat-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.clear-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: var(--bg-secondary);
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
}

.welcome-screen {
  text-align: center;
  padding: 60px 20px;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 24px;
}

.welcome-screen h2 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.welcome-screen p {
  color: var(--text-secondary);
  margin: 0 0 32px 0;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.quick-questions button {
  padding: 10px 20px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.quick-questions button:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.chat-message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: flex-start;
}

.chat-message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.chat-message.user .message-avatar {
  background: var(--primary);
}

.message-bubble {
  max-width: 70%;
}

.chat-message.user .message-bubble {
  text-align: right;
}

.message-content {
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-radius: 16px;
  color: var(--text-primary);
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.chat-message.user .message-content {
  background: var(--primary);
  color: white;
}

.message-time {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.typing-indicator {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.typing-indicator .dots {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-radius: 16px;
}

.typing-indicator .dots span {
  width: 8px;
  height: 8px;
  background: var(--text-secondary);
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator .dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator .dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

.chat-input-area {
  display: flex;
  gap: 12px;
}

.chat-input-area input {
  flex: 1;
  padding: 14px 20px;
  border: 1px solid var(--border-color);
  border-radius: 24px;
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 14px;
}

.chat-input-area input:focus {
  outline: none;
  border-color: var(--primary);
}

.chat-input-area input:disabled {
  opacity: 0.5;
}

.chat-input-area button {
  padding: 14px 28px;
  border: none;
  background: var(--primary);
  color: white;
  border-radius: 24px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.chat-input-area button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
