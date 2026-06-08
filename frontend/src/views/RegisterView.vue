<template>
  <div class="auth-view">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <div class="logo">[AI_TRADER]_</div>
          <h1>// {{ t('auth.register') }}</h1>
          <p>$ register --new-user</p>
        </div>

        <form class="auth-form" @submit.prevent="handleRegister">
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
            <label for="email">{{ t('auth.email') }}</label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              class="form-input"
              :placeholder="t('auth.email')"
              :disabled="submitting"
            />
          </div>

          <div class="form-group">
            <label for="display_name">{{ t('auth.displayName') }}</label>
            <input
              id="display_name"
              v-model="formData.display_name"
              type="text"
              class="form-input"
              :placeholder="t('auth.displayName')"
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
            />
          </div>

          <div class="form-group">
            <label for="confirm_password">{{ t('auth.confirmPassword') }}</label>
            <input
              id="confirm_password"
              v-model="formData.confirm_password"
              type="password"
              class="form-input"
              :placeholder="t('auth.confirmPassword')"
              :disabled="submitting"
              @keydown.enter="handleRegister"
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
            {{ submitting ? t('common.loading') : t('auth.register') }}
          </button>
        </form>

        <div class="auth-footer">
          <p>{{ t('auth.hasAccount') }} <router-link to="/login">{{ t('auth.login') }}</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const { t } = useI18n()
const router = useRouter()
const userStore = useUserStore()

const submitting = ref(false)
const error = ref<string | null>(null)

const formData = reactive({
  username: '',
  email: '',
  display_name: '',
  password: '',
  confirm_password: ''
})

const isValid = computed(() => {
  return formData.username.trim() &&
    formData.email.trim() &&
    formData.display_name.trim() &&
    formData.password.length >= 6 &&
    formData.password === formData.confirm_password
})

async function handleRegister() {
  if (!isValid.value || submitting.value) return
  
  submitting.value = true
  error.value = null
  
  try {
    const result = await userStore.register({
      username: formData.username.trim(),
      email: formData.email.trim(),
      display_name: formData.display_name.trim(),
      password: formData.password
    })
    
    if (result.success) {
      router.push('/')
    } else {
      error.value = result.message || t('auth.registerFailed')
    }
  } catch (e: any) {
    error.value = e.message || t('auth.registerFailed')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.auth-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
  padding: 20px;
}

.auth-container {
  width: 100%;
  max-width: 420px;
}

.auth-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  font-size: 48px;
  margin-bottom: 16px;
}

.auth-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.auth-header p {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

.auth-form {
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-message {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-color);
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 20px;
}

.btn {
  padding: 12px 24px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--accent-color);
  color: white;
  width: 100%;
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: translateY(-1px);
}

.btn-block {
  width: 100%;
}

.auth-footer {
  text-align: center;
}

.auth-footer p {
  font-size: 14px;
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
