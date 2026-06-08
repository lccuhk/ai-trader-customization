import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import './styles/global.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)

// 延迟初始化 store，避免循环依赖问题
app.mount('#app')

// 现在可以安全地使用 store 了
import { useUserStore } from './stores/user'
import { useWebSocketStore } from './stores/websocket'

const userStore = useUserStore()
userStore.initializeFromStorage()

async function initializeApp() {
  if (userStore.isLoggedIn) {
    const isValid = await userStore.fetchCurrentUser()
    if (isValid) {
      const websocketStore = useWebSocketStore()
      websocketStore.connect().catch(e => {
        console.warn('[WS] Auto-connect failed:', e.message)
      })
    }
  }
}

initializeApp()
