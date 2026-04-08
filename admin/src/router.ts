import { createRouter, createWebHistory } from 'vue-router'

import { adminApi } from './api'
import DashboardView from './views/DashboardView.vue'
import LoginView from './views/LoginView.vue'

const hasToken = () => Boolean(localStorage.getItem('blog_admin_token'))

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: LoginView },
    { path: '/', name: 'dashboard', component: DashboardView, meta: { requiresAuth: true } },
  ],
})

router.beforeEach(async (to) => {
  if (!to.meta.requiresAuth) {
    if (to.name === 'login' && hasToken()) {
      try {
        await adminApi.getMe()
        return '/'
      } catch {
        localStorage.removeItem('blog_admin_token')
      }
    }
    return true
  }

  if (!hasToken()) {
    return '/login'
  }

  try {
    await adminApi.getMe()
    return true
  } catch {
    localStorage.removeItem('blog_admin_token')
    return '/login'
  }
})
