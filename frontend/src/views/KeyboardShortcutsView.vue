<template>
  <div class="shortcuts-view">
    <div class="page-header">
      <h1>⌨️ 键盘快捷键</h1>
    </div>
    
    <div class="shortcuts-grid">
      <div class="shortcut-section">
        <h2>导航</h2>
        <div class="shortcut-list">
          <div class="shortcut-item">
            <kbd>1</kbd>
            <span>跳转到信号广场</span>
          </div>
          <div class="shortcut-item">
            <kbd>2</kbd>
            <span>跳转到交易页面</span>
          </div>
          <div class="shortcut-item">
            <kbd>3</kbd>
            <span>跳转到资产页面</span>
          </div>
          <div class="shortcut-item">
            <kbd>4</kbd>
            <span>跳转到 AI 助手</span>
          </div>
          <div class="shortcut-item">
            <kbd>5</kbd>
            <span>跳转到通知</span>
          </div>
        </div>
      </div>
      
      <div class="shortcut-section">
        <h2>全局操作</h2>
        <div class="shortcut-list">
          <div class="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>K</kbd>
            <span>打开搜索</span>
          </div>
          <div class="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>/</kbd>
            <span>切换主题</span>
          </div>
          <div class="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>Q</kbd>
            <span>打开快捷设置</span>
          </div>
          <div class="shortcut-item">
            <kbd>Esc</kbd>
            <span>关闭弹窗/菜单</span>
          </div>
          <div class="shortcut-item">
            <kbd>?</kbd>
            <span>显示快捷键帮助</span>
          </div>
        </div>
      </div>
      
      <div class="shortcut-section">
        <h2>页面操作</h2>
        <div class="shortcut-list">
          <div class="shortcut-item">
            <kbd>r</kbd>
            <span>刷新当前页面</span>
          </div>
          <div class="shortcut-item">
            <kbd>f</kbd>
            <span>收藏/取消收藏</span>
          </div>
          <div class="shortcut-item">
            <kbd>s</kbd>
            <span>打开设置</span>
          </div>
          <div class="shortcut-item">
            <kbd>h</kbd>
            <span>返回首页</span>
          </div>
          <div class="shortcut-item">
            <kbd>Backspace</kbd>
            <span>返回上一页</span>
          </div>
        </div>
      </div>
      
      <div class="shortcut-section">
        <h2>编辑操作</h2>
        <div class="shortcut-list">
          <div class="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>N</kbd>
            <span>新建信号</span>
          </div>
          <div class="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>S</kbd>
            <span>保存</span>
          </div>
          <div class="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>E</kbd>
            <span>编辑</span>
          </div>
          <div class="shortcut-item">
            <kbd>Del</kbd>
            <span>删除</span>
          </div>
          <div class="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>Z</kbd>
            <span>撤销</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="tips-section">
      <h3>💡 提示</h3>
      <ul>
        <li>你可以随时按 <kbd>?</kbd> 键来查看这个页面</li>
        <li>键盘快捷键可以大幅提高你的操作效率</li>
        <li>在 Mac 上，用 <kbd>Cmd</kbd> 键代替 <kbd>Ctrl</kbd> 键</li>
        <li>建议先从导航快捷键开始熟悉</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'

const router = useRouter()
const themeStore = useThemeStore()

function handleKeydown(event: KeyboardEvent) {
  const key = event.key.toLowerCase()
  const isCtrl = event.ctrlKey || event.metaKey
  
  if (key === '?') {
    router.push('/shortcuts')
    return
  }
  
  if (isCtrl && key === 'k') {
    event.preventDefault()
    const searchInput = document.querySelector('.search-input') as HTMLInputElement
    searchInput?.focus()
    return
  }
  
  if (isCtrl && key === '/') {
    event.preventDefault()
    themeStore.toggleTheme()
    return
  }
  
  if (isCtrl && key === 'q') {
    event.preventDefault()
    const settingsBtn = document.querySelector('.settings-toggle') as HTMLButtonElement
    settingsBtn?.click()
    return
  }
  
  if (!isCtrl && ['1', '2', '3', '4', '5'].includes(key)) {
    const routes = ['/', '/trading', '/portfolio', '/ai', '/notifications']
    router.push(routes[parseInt(key) - 1])
    return
  }
  
  if (!isCtrl && key === 'h') {
    router.push('/')
    return
  }
  
  if (!isCtrl && key === 'r') {
    window.location.reload()
    return
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.shortcuts-view {
  padding: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header h1 {
  margin: 0 0 32px 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.shortcuts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.shortcut-section {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.shortcut-section h2 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.shortcut-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.shortcut-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color);
}

.shortcut-item:last-child {
  border-bottom: none;
}

.shortcut-item span {
  color: var(--text-secondary);
  font-size: 14px;
}

kbd {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 4px 8px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-primary);
  box-shadow: 0 2px 0 rgba(0, 0, 0, 0.1);
}

.tips-section {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 12px;
  padding: 20px;
}

.tips-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.tips-section ul {
  margin: 0;
  padding-left: 20px;
}

.tips-section li {
  color: var(--text-secondary);
  margin-bottom: 8px;
  line-height: 1.6;
}
</style>
