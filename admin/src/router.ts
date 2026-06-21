import { createRouter, createWebHistory } from 'vue-router'

import { adminApi, clearAdminAuthCookies, isLoggedIn } from './api'

const routerBase = (import.meta.env.BASE_URL || '/admin').replace(/\/$/, '') || '/admin'

export const router = createRouter({
  history: createWebHistory(routerBase),
  routes: [
    { path: '/login', name: 'login', component: () => import('./views/LoginView.vue'), meta: { title: '登录' } },
    // 探针页已移除（仅在开发时手动测试，不进生产路由）
    { path: '/', name: 'dashboard', component: () => import('./views/DashboardView.vue'), meta: { requiresAuth: true, title: '仪表盘' } },
    { path: '/:pathMatch(.*)*', name: 'dashboard-catchall', component: () => import('./views/DashboardView.vue'), meta: { requiresAuth: true, title: '仪表盘' } },
  ],
})

router.beforeEach(async (to) => {
  if (!to.meta.requiresAuth) {
    if (to.name === 'login' && isLoggedIn()) {
      try {
        await adminApi.getMe()
        return '/'
      } catch {
        clearAdminAuthCookies()
      }
    }
    return true
  }

  if (!isLoggedIn()) {
    return '/login'
  }

  try {
    await adminApi.getMe()
    return true
  } catch {
    clearAdminAuthCookies()
    return '/login'
  }
})
