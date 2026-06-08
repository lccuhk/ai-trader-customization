<template>
  <div class="security-view">
    <div class="security-header">
      <h1>安全设置</h1>
    </div>

    <div class="security-content">
      <div class="section">
        <div class="section-header">
          <h2>双因素认证 (2FA)</h2>
          <span class="status-badge" :class="{ enabled: tfaStatus.enabled }">
            {{ tfaStatus.enabled ? '已启用' : '未启用' }}
          </span>
        </div>
        <p class="section-desc">
          启用双因素认证可以大幅提升账户安全性。我们支持 TOTP (Google Authenticator, Authy 等)
        </p>

        <div v-if="!tfaStatus.enabled && !showSetup" class="setup-section">
          <button class="primary-btn" @click="startSetup">
            启用 2FA
          </button>
        </div>

        <div v-if="showSetup" class="setup-form">
          <div class="qr-section">
            <div class="qr-code">
              <img :src="setupData?.qr_code" alt="QR Code" />
            </div>
            <div class="setup-info">
              <p>1. 打开身份验证器应用</p>
              <p>2. 扫描二维码或手动输入密钥</p>
              <p class="secret-key">密钥: {{ setupData?.secret }}</p>
              <p>3. 输入验证码完成验证</p>
            </div>
          </div>
          <div class="verify-section">
            <input 
              type="text" 
              v-model="verifyCode" 
              placeholder="输入6位验证码"
              maxlength="6"
            />
            <button class="primary-btn" @click="verifySetup" :disabled="verifyCode.length !== 6">
              验证并启用
            </button>
          </div>
          <div class="backup-codes" v-if="setupData?.backup_codes">
            <h4>备用代码</h4>
            <p>请妥善保存这些备用代码，在无法使用身份验证器时可以使用</p>
            <div class="codes-grid">
              <span v-for="code in setupData.backup_codes" :key="code" class="code-item">
                {{ code }}
              </span>
            </div>
          </div>
          <button class="cancel-btn" @click="cancelSetup">
            取消
          </button>
        </div>

        <div v-if="tfaStatus.enabled" class="disable-section">
          <p>双因素认证已启用。如果需要禁用，请输入当前验证码。</p>
          <div class="disable-form">
            <input 
              type="text" 
              v-model="disableCode" 
              placeholder="输入验证码"
              maxlength="6"
            />
            <button class="danger-btn" @click="disable2FA" :disabled="disableCode.length !== 6">
              禁用 2FA
            </button>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-header">
          <h2>第三方登录</h2>
        </div>
        <p class="section-desc">
          绑定第三方账户可以方便快捷地登录
        </p>
        <div class="oauth-list">
          <div class="oauth-item">
            <div class="oauth-info">
              <span class="oauth-icon">🔵</span>
              <span>Google</span>
            </div>
            <button class="link-btn" @click="linkOAuth('google')">
              {{ isLinked('google') ? '已绑定' : '绑定' }}
            </button>
          </div>
          <div class="oauth-item">
            <div class="oauth-info">
              <span class="oauth-icon">⚫</span>
              <span>GitHub</span>
            </div>
            <button class="link-btn" @click="linkOAuth('github')">
              {{ isLinked('github') ? '已绑定' : '绑定' }}
            </button>
          </div>
          <div class="oauth-item">
            <div class="oauth-info">
              <span class="oauth-icon">✈️</span>
              <span>Telegram</span>
            </div>
            <button class="link-btn" @click="linkOAuth('telegram')">
              {{ isLinked('telegram') ? '已绑定' : '绑定' }}
            </button>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-header">
          <h2>密码策略</h2>
        </div>
        <div class="password-requirements">
          <p>为了账户安全，密码需要满足以下要求：</p>
          <ul>
            <li :class="{ valid: passwordChecks.length }">至少8个字符</li>
            <li>包含大写字母</li>
            <li>包含小写字母</li>
            <li>包含数字</li>
            <li>包含特殊字符 (!@#$%^&*)</li>
          </ul>
        </div>
        <div class="password-check">
          <label>测试密码强度</label>
          <input 
            type="password" 
            v-model="testPassword" 
            placeholder="输入密码测试"
            @input="checkPassword"
          />
          <div v-if="passwordResult" class="password-result" :class="{ valid: passwordResult.valid }">
            <span v-if="passwordResult.valid" class="valid-text">✅ 密码符合要求</span>
            <div v-else class="errors">
              <span v-for="error in passwordResult.errors" :key="error" class="error-text">
                ❌ {{ error }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-header">
          <h2>操作日志</h2>
        </div>
        <p class="section-desc">
          查看账户的所有安全相关操作记录
        </p>
        <div class="audit-logs">
          <div v-if="loadingLogs" class="loading">加载中...</div>
          <div v-else-if="auditLogs.length === 0" class="empty-state">
            暂无操作记录
          </div>
          <div v-else class="logs-list">
            <div v-for="log in auditLogs" :key="log.id" class="log-item">
              <div class="log-action">{{ log.action }}</div>
              <div class="log-details">
                <span v-if="log.ip_address">IP: {{ log.ip_address }}</span>
                <span>{{ formatTime(log.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { securityService } from '@/services/security'
import { useToast } from '@/composables/useToast'
import type { TwoFactorAuth, SecuritySettings, AuditLog } from '@/types'

const toast = useToast()

const tfaStatus = ref<TwoFactorAuth>({ enabled: false })
const showSetup = ref(false)
const setupData = ref<any>(null)
const verifyCode = ref('')
const disableCode = ref('')
const testPassword = ref('')
const passwordResult = ref<{ valid: boolean; errors: string[] } | null>(null)
const passwordChecks = ref<string[]>([])
const securitySettings = ref<SecuritySettings | null>(null)
const auditLogs = ref<AuditLog[]>([])
const loadingLogs = ref(false)

async function loadStatus() {
  try {
    const response = await securityService.get2FAStatus()
    if (response.success && response.data) {
      tfaStatus.value = response.data
    }

    const settingsResponse = await securityService.getSecuritySettings()
    if (settingsResponse.success && settingsResponse.data) {
      securitySettings.value = settingsResponse.data
    }
  } catch (e: any) {
    toast.error(e.message || '加载状态失败')
  }
}

async function startSetup() {
  try {
    const response = await securityService.setup2FA('totp')
    if (response.success && response.data) {
      setupData.value = response.data
      showSetup.value = true
    }
  } catch (e: any) {
    toast.error(e.message || '启动2FA设置失败')
  }
}

async function verifySetup() {
  try {
    const response = await securityService.verify2FA(verifyCode.value)
    if (response.success && response.data?.verified) {
      tfaStatus.value.enabled = true
      showSetup.value = false
      toast.success('2FA 已启用')
    } else {
      toast.error('验证码错误，请重试')
    }
  } catch (e: any) {
    toast.error(e.message || '验证失败')
  }
}

function cancelSetup() {
  showSetup.value = false
  setupData.value = null
  verifyCode.value = ''
}

async function disable2FA() {
  try {
    const response = await securityService.disable2FA(disableCode.value)
    if (response.success) {
      tfaStatus.value.enabled = false
      disableCode.value = ''
      toast.success('2FA 已禁用')
    }
  } catch (e: any) {
    toast.error(e.message || '禁用失败')
  }
}

function isLinked(provider: string) {
  return securitySettings.value?.oauth_accounts?.some(a => a.provider === provider)
}

async function linkOAuth(provider: string) {
  toast.info(`${provider} 绑定功能开发中`)
}

async function checkPassword() {
  if (!testPassword.value) {
    passwordResult.value = null
    return
  }

  try {
    const response = await securityService.validatePassword(testPassword.value)
    if (response.success && response.data) {
      passwordResult.value = response.data
    }
  } catch (e) {
    console.error('Password check failed:', e)
  }
}

async function loadAuditLogs() {
  loadingLogs.value = true
  try {
    const response = await securityService.getAuditLogs({ per_page: 10 })
    if (response.success && response.data) {
      auditLogs.value = response.data.items
    }
  } catch (e: any) {
    toast.error(e.message || '加载日志失败')
  } finally {
    loadingLogs.value = false
  }
}

function formatTime(time: string) {
  return new Date(time).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadStatus()
  loadAuditLogs()
})
</script>

<style scoped>
.security-view {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.security-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 24px 0;
}

.section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(156, 163, 175, 0.1);
  color: #9ca3af;
}

.status-badge.enabled {
  background: rgba(34, 197, 94, 0.1);
  color: var(--success);
}

.section-desc {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0 0 20px 0;
  line-height: 1.5;
}

.primary-btn {
  padding: 10px 24px;
  border: none;
  background: var(--primary);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.primary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.danger-btn {
  padding: 10px 24px;
  border: none;
  background: var(--danger);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.danger-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cancel-btn {
  padding: 10px 24px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: var(--bg-secondary);
}

.setup-form {
  margin-top: 20px;
}

.qr-section {
  display: flex;
  gap: 24px;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.qr-code {
  width: 150px;
  height: 150px;
  background: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.qr-code img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.setup-info p {
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.secret-key {
  font-family: monospace;
  background: var(--bg-card);
  padding: 8px 12px;
  border-radius: 4px;
  font-weight: 600;
  color: var(--primary);
  margin: 8px 0 !important;
}

.verify-section {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.verify-section input,
.disable-form input,
.password-check input {
  flex: 1;
  min-width: 200px;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
}

.verify-section input:focus,
.disable-form input:focus,
.password-check input:focus {
  outline: none;
  border-color: var(--primary);
}

.disable-form {
  display: flex;
  gap: 12px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.backup-codes {
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 8px;
  margin-bottom: 20px;
}

.backup-codes h4 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.backup-codes p {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0 0 16px 0;
}

.codes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
}

.code-item {
  font-family: monospace;
  padding: 8px 12px;
  background: var(--bg-card);
  border-radius: 4px;
  text-align: center;
  font-weight: 500;
  color: var(--text-primary);
}

.oauth-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.oauth-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.oauth-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.oauth-icon {
  font-size: 24px;
}

.link-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.link-btn:hover {
  background: var(--bg-card);
}

.password-requirements ul {
  list-style: none;
  padding: 0;
  margin: 12px 0;
}

.password-requirements li {
  padding: 4px 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.password-requirements li::before {
  content: '• ';
  color: var(--text-secondary);
}

.password-check {
  margin-top: 20px;
}

.password-check label {
  display: block;
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.password-result {
  margin-top: 12px;
  padding: 12px;
  border-radius: 8px;
}

.password-result.valid {
  background: rgba(34, 197, 94, 0.1);
}

.valid-text {
  color: var(--success);
  font-weight: 500;
}

.errors {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.error-text {
  color: var(--danger);
  font-size: 14px;
}

.loading, .empty-state {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary);
}

.logs-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 6px;
}

.log-action {
  font-weight: 500;
  color: var(--text-primary);
}

.log-details {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-secondary);
}

.valid {
  color: var(--success);
}
</style>
