import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/signal/:id',
    name: 'SignalDetail',
    component: () => import('@/views/SignalDetailView.vue'),
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
    name: 'Market',
    component: () => import('@/views/MarketView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: () => import('@/views/NotificationsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/:id',
    name: 'UserProfile',
    component: () => import('@/views/UserProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/trading',
    name: 'Trading',
    component: () => import('@/views/TradingView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/portfolio',
    name: 'Portfolio',
    component: () => import('@/views/PortfolioView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/messages',
    name: 'Messages',
    component: () => import('@/views/MessagesView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/messages/:userId',
    name: 'Chat',
    component: () => import('@/views/ChatView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ai',
    name: 'AI',
    component: () => import('@/views/AIView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ai/chat',
    name: 'AIChat',
    component: () => import('@/views/AIChatView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ai/analysis',
    name: 'AIAnalysis',
    component: () => import('@/views/AIAnalysisView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ai/strategies',
    name: 'AIStrategies',
    component: () => import('@/views/AIStrategiesView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/security',
    name: 'Security',
    component: () => import('@/views/SecurityView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: () => import('@/views/AnalyticsView.vue'),
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
    name: 'Favorites',
    component: () => import('@/views/FavoritesView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/HistoryView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/export',
    name: 'Export',
    component: () => import('@/views/ExportView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/shortcuts',
    name: 'Shortcuts',
    component: () => import('@/views/KeyboardShortcutsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/alerts',
    name: 'Alerts',
    component: () => import('@/views/AlertsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/backup',
    name: 'Backup',
    component: () => import('@/views/BackupView.vue'),
    meta: { requiresAuth: true }
  },
  // 风险管理模块
  {
    path: '/risk/dashboard',
    name: 'RiskDashboard',
    component: () => import('@/views/RiskDashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/risk/alerts',
    name: 'RiskAlerts',
    component: () => import('@/views/RiskAlertsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/risk/settings',
    name: 'RiskSettings',
    component: () => import('@/views/RiskSettingsView.vue'),
    meta: { requiresAuth: true }
  },
  // 市场情报模块
  {
    path: '/market/news',
    name: 'MarketNews',
    component: () => import('@/views/MarketNewsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/market/events',
    name: 'MarketEvents',
    component: () => import('@/views/MarketEventsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/market/indicators',
    name: 'MarketIndicators',
    component: () => import('@/views/MarketIndicatorsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/market/sentiment',
    name: 'MarketSentiment',
    component: () => import('@/views/MarketSentimentView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/market/trending',
    name: 'MarketTrending',
    component: () => import('@/views/MarketTrendingView.vue'),
    meta: { requiresAuth: true }
  },
  // 策略管理模块
  {
    path: '/strategies',
    name: 'Strategies',
    component: () => import('@/views/StrategiesView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/strategies/templates',
    name: 'StrategyTemplates',
    component: () => import('@/views/StrategyTemplatesView.vue'),
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
