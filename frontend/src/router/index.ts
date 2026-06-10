import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/dashboard/DashboardLayout.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/signal/:id',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/market',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/notifications',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/user/:id',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/trading',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/portfolio',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/messages',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/messages/:userId',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/ai',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/ai/chat',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/ai/analysis',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/ai/strategies',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/security',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/analytics',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/AdminView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  // 新功能路由
  {
    path: '/favorites',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/export',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/shortcuts',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/alerts',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/backup',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  // 风险管理模块
  {
    path: '/risk/dashboard',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/risk/alerts',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/risk/settings',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  // 市场情报模块
  {
    path: '/market/news',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/market/events',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/market/indicators',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/market/sentiment',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/market/trending',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  // 策略管理模块
  {
    path: '/strategies',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/strategies/templates',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const userStore = useUserStore()
  const isLoggedIn = userStore.isLoggedIn
  const isAdmin = userStore.user?.role === 'admin'

  if (to.meta.requiresAuth && !isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresAdmin && !isAdmin) {
    next({ name: 'Home' })
  } else if (to.meta.guestOnly && isLoggedIn) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
