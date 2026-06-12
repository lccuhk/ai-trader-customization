<template>
  <div class="auth-view">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <div class="logo">[AI_TRADER]_</div>
          <h1>// {{ t('auth.login') }}</h1>
          <p>$ login --user=trader</p>
        </div>

        <div class="test-account-card">
          <div class="test-account-header">
            <span class="test-account-icon">&gt;</span>
            <span class="test-account-title">{{ t('auth.demoHint') }}</span>
          </div>
          <div class="test-account-creds">
            <div class="cred-item">
              <span class="cred-label">EMAIL:</span>
              <code class="cred-value" @click="copyText('demo@example.com')">demo@example.com</code>
            </div>
            <div class="cred-item">
              <span class="cred-label">PASSWORD:</span>
              <code class="cred-value" @click="copyText('demo123456')">demo123456</code>
            </div>
          </div>
          <button @click="fillTestAccount" class="btn-test-fill" :class="{ success: fillSuccess }">
            {{ fillSuccess ? '[ ✓ ' + t('auth.testAccountFilled') + ' ]' : '[ ' + t('auth.fillTestAccount') + ' ]' }}
          </button>
        </div>

        <form class="auth-form" @submit.prevent="handleLogin">
          <div class="form-group">
            <label for="username">{{ t('auth.username') }}</label>
            <input
              id="username"
              v-model="formData.username"
              type="text"
              class="form-input"
              :placeholder="t('auth.username')"
              :disabled="submitting"
            />
          </div>

          <div class="form-group">
            <label for="password">{{ t('auth.password') }}</label>
            <input
              id="password"
              v-model="formData.password"
              type="password"
              class="form-input"
              :placeholder="t('auth.password')"
              :disabled="submitting"
              @keydown.enter="handleLogin"
            />
          </div>

          <div v-if="error" class="error-message">
            ❌ {{ error }}
          </div>

          <button 
            type="submit" 
            class="btn btn-primary btn-block"
            :disabled="submitting || !isValid"
          >
            {{ submitting ? t('common.loading') : t('auth.login') }}
          </button>
        </form>

        <div class="auth-footer">
          <p>{{ t('auth.noAccount') }} <router-link to="/register">{{ t('auth.register') }}</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const { t } = useI18n()

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const submitting = ref(false)
const error = ref<string | null>(null)
const copySuccess = ref<string | null>(null)

const formData = reactive({
  username: '',
  password: ''
})

const isValid = computed(() => {
  return formData.username.trim() && formData.password.trim()
})

async function handleLogin() {
  if (!isValid.value || submitting.value) return
  
  submitting.value = true
  error.value = null
  
  try {
    const result = await userStore.login(formData.username.trim(), formData.password)
    
    if (result.success) {
      const redirect = route.query.redirect as string || '/'
      router.push(redirect)
    } else {
      error.value = result.message || '登录失败，请检查用户名和密码'
    }
  } catch (e: any) {
    error.value = e.message || '登录失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}

const fillSuccess = ref(false)

async function fillTestAccount() {
  // 清除之前的错误
  error.value = null

  // 直接赋值确保响应式更新
  formData.username = 'demo@example.com'
  formData.password = 'demo123456'

  // 显示成功提示
  fillSuccess.value = true
  setTimeout(() => {
    fillSuccess.value = false
  }, 2000)
}

async function copyText(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    copySuccess.value = text
    setTimeout(() => {
      copySuccess.value = null
    }, 2000)
  } catch (e) {
    console.error('Failed to copy text:', e)
  }
}
</script>

<style scoped>
/* IT 极简风格登录页面 */
.auth-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  padding: 20px;
  position: relative;
}

/* 终端风格背景网格 */
.auth-view::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(var(--border-light) 1px, transparent 1px),
    linear-gradient(90deg, var(--border-light) 1px, transparent 1px);
  background-size: 40px 40px;
  opacity: 0.3;
  pointer-events: none;
}

.auth-container {
  width: 100%;
  max-width: 440px;
  position: relative;
  z-index: 1;
}

.auth-card {
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  padding: 32px;
  box-shadow: 8px 8px 0 var(--border-color);
}

/* 终端风格标题栏 */
.auth-card::before {
  content: 'LOGIN.EXE';
  display: block;
  background: var(--text-primary);
  color: var(--bg-primary);
  padding: 8px 12px;
  margin: -32px -32px 24px -32px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.test-account-card {
  background: var(--bg-secondary);
  border: 2px solid var(--success-color);
  padding: 16px;
  margin-bottom: 24px;
}

.test-account-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-light);
}

.test-account-icon {
  font-size: 16px;
  color: var(--success-color);
  font-weight: 700;
}

.test-account-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--success-color);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.test-account-creds {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.cred-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.cred-label {
  color: var(--text-muted);
  min-width: 90px;
  font-weight: 600;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.cred-value {
  background: var(--bg-primary);
  padding: 4px 10px;
  border: 1px solid var(--border-color);
  font-family: inherit;
  font-size: 13px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.1s ease;
}

.cred-value:hover {
  background: var(--success-color);
  border-color: var(--success-color);
  color: var(--bg-primary);
}

.btn-test-fill {
  width: 100%;
  padding: 8px 16px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.1s ease;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: inherit;
}

.btn-test-fill:hover {
  background: var(--text-primary);
  border-color: var(--text-primary);
  color: var(--bg-primary);
}

.btn-test-fill.success {
  background: var(--success-color);
  border-color: var(--success-color);
  color: var(--bg-primary);
}

.auth-header {
  text-align: center;
  margin-bottom: 24px;
}

.logo {
  font-size: 24px;
  font-weight: 700;
  color: var(--success-color);
  margin-bottom: 16px;
  letter-spacing: 0.05em;
}

.auth-header h1 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.auth-header p {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
  font-family: inherit;
}

.auth-form {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  transition: all 0.1s ease;
  box-sizing: border-box;
  outline: none;
}

.form-input:focus {
  border-color: var(--success-color);
  box-shadow: 3px 3px 0 var(--success-color);
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-message {
  background: var(--danger-bg);
  color: var(--danger-color);
  padding: 10px 14px;
  border: 2px solid var(--danger-color);
  font-size: 12px;
  margin-bottom: 16px;
  font-weight: 500;
}

.btn {
  padding: 12px 24px;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
  border: 2px solid var(--border-color);
  transition: all 0.1s ease;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: inherit;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--success-color);
  color: var(--bg-primary);
  border-color: var(--success-color);
  width: 100%;
}

.btn-primary:hover:not(:disabled) {
  background: var(--text-primary);
  border-color: var(--text-primary);
  color: var(--bg-primary);
}

.btn-block {
  width: 100%;
}

.auth-footer {
  text-align: center;
  border-top: 1px solid var(--border-light);
  padding-top: 16px;
}

.auth-footer p {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
}

.auth-footer a {
  color: var(--accent-color);
  text-decoration: none;
  font-weight: 500;
}

.auth-footer a:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .auth-card {
    padding: 30px 24px;
  }
  
  .auth-header h1 {
    font-size: 24px;
  }
}
</style>
