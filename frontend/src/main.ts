import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import { useUserStore } from './stores/user'
import { useWebSocketStore } from './stores/websocket'
import './styles/global.css'
import './styles/fonts.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)

// 在 mount 前初始化 store 以避免首次渲染时状态为空
const userStore = useUserStore()
userStore.initializeFromStorage()

app.mount('#app')

// 登录后异步初始化（WebSocket 连接等后台任务）
async function initializeApp() {
  // Skip auth check on login/register pages - no token validation needed
  const authPages = ['/login', '/register']
  if (authPages.includes(window.location.pathname.replace(/\/+$/, ''))) {
    return
  }

  if (userStore.isLoggedIn) {
    const isValid = await userStore.fetchCurrentUser()
    if (isValid) {
      const websocketStore = useWebSocketStore()
      websocketStore.connect().catch(e => {
        console.warn('[WS] Auto-connect failed:', e.message)
      })
    } else {
      // Token 无效，重定向到登录页
      router.push({ name: 'Login' })
    }
  }
}

initializeApp()
