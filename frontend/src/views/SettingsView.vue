<template>
  <div class="settings-page">
    <div class="container">
      <header class="page-header">
        <h1 class="page-title">
        <span class="title-icon">⚙️</span>
        <span>{{ t('nav.settings') }}</span>
      </h1>
      </header>

      <div class="settings-grid">
        <!-- 账户设置 -->
        <div class="settings-card">
          <div class="card-header">
        <h2>👤 {{ t('user.title') }}</h2>
          </div>
          <div class="card-body">
            <router-link to="/profile" class="setting-item">
              <span class="item-icon">👤</span>
              <div class="item-content">
                <span class="item-title">{{ t('user.editProfile') }}</span>
                <span class="item-desc">{{ t('user.editProfile') }}</span>
              </div>
              <span class="item-arrow">→</span>
            </router-link>
            <router-link to="/security" class="setting-item">
              <span class="item-icon">🔐</span>
              <div class="item-content">
                <span class="item-title">{{ t('security.title') }}</span>
                <span class="item-desc">{{ t('security.subtitle') }}</span>
              </div>
              <span class="item-arrow">→</span>
            </router-link>
            <router-link to="/notifications" class="setting-item">
              <span class="item-icon">🔔</span>
              <div class="item-content">
                <span class="item-title">{{ t('notification.title') }}</span>
                <span class="item-desc">{{ t('notification.settings') }}</span>
              </div>
              <span class="item-arrow">→</span>
            </router-link>
          </div>
        </div>

        <!-- 应用设置 -->
        <div class="settings-card">
          <div class="card-header">
        <h2>🎨 {{ t('common.settings') }}</h2>
          </div>
          <div class="card-body">
            <div class="setting-item">
              <span class="item-icon">🌐</span>
              <div class="item-content">
                <span class="item-title">{{ t('language.title') }}</span>
                <span class="item-desc">{{ t('language.selectLanguage') }}</span>
              </div>
              <LanguageSwitcher class="item-control" />
            </div>
            <div class="setting-item">
              <span class="item-icon">🎨</span>
              <div class="item-content">
                <span class="item-title">{{ t('user.theme') }}</span>
                <span class="item-desc">IT 极简风格</span>
              </div>
              <ThemeToggle class="item-control" />
            </div>
            <router-link to="/shortcuts" class="setting-item">
              <span class="item-icon">⌨️</span>
              <div class="item-content">
                <span class="item-title">{{ t('nav.shortcuts') }}</span>
                <span class="item-desc">{{ t('shortcuts.subtitle') }}</span>
              </div>
              <span class="item-arrow">→</span>
            </router-link>
          </div>
        </div>

        <!-- 数据管理 -->
        <div class="settings-card">
          <div class="card-header">
        <h2>💾 {{ t('common.manage') }}</h2>
          </div>
          <div class="card-body">
            <router-link to="/export" class="setting-item">
              <span class="item-icon">📤</span>
              <div class="item-content">
                <span class="item-title">{{ t('nav.export') }}</span>
                <span class="item-desc">{{ t('export.subtitle') }}</span>
              </div>
              <span class="item-arrow">→</span>
            </router-link>
            <router-link to="/backup" class="setting-item">
              <span class="item-icon">💾</span>
              <div class="item-content">
                <span class="item-title">{{ t('nav.backup') }}</span>
                <span class="item-desc">{{ t('backup.subtitle') }}</span>
              </div>
              <span class="item-arrow">→</span>
            </router-link>
          </div>
        </div>

        <!-- 关于 -->
        <div class="settings-card">
          <div class="card-header">
        <h2>ℹ️ {{ t('common.about') || '关于' }}</h2>
          </div>
          <div class="card-body">
            <div class="setting-item">
              <span class="item-icon">🏷️</span>
              <div class="item-content">
                <span class="item-title">版本</span>
                <span class="item-desc">AI Trader v2.0.0</span>
              </div>
            </div>
            <div class="setting-item">
              <span class="item-icon">📝</span>
              <div class="item-content">
                <span class="item-title">架构</span>
                <span class="item-desc">Vue 3 + TypeScript + Flask</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const { t } = useI18n()
</script>

<style scoped>
.settings-page {
  min-height: calc(100vh - 56px);
  background: var(--bg-primary);
  padding: 24px 0;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 24px;
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: 0.02em;
}

.title-icon {
  font-size: 32px;
}

.settings-grid {
  display: grid;
  gap: 20px;
}

.settings-card {
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
}

.card-header {
  padding: 16px 20px;
  border-bottom: 2px solid var(--border-color);
  background: var(--bg-secondary);
}

.card-header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-body {
  padding: 8px 0;
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 20px;
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.1s ease;
  cursor: pointer;
  border-bottom: 1px solid var(--border-color);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item:hover {
  background: var(--bg-secondary);
}

.item-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-title {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.item-desc {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
}

.item-arrow {
  color: var(--text-secondary);
  font-size: 14px;
  flex-shrink: 0;
}

.item-control {
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .settings-page {
    padding: 16px 0;
  }
  
  .container {
    padding: 0 16px;
  }
  
  .page-title {
    font-size: 22px;
  }
  
  .title-icon {
    font-size: 26px;
  }
}
</style>
