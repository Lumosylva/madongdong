import { createRouter, createWebHistory } from 'vue-router'

import { adminApi, isLoggedIn } from './api'
import DashboardView from './views/DashboardView.vue'
import LoginView from './views/LoginView.vue'
import MdEditorV3ProbeView from './views/MdEditorV3ProbeView.vue'

const routerBase = (import.meta.env.BASE_URL || '/admin').replace(/\/$/, '') || '/admin'

export const router = createRouter({
  history: createWebHistory(routerBase),
  routes: [
    { path: '/login', name: 'login', component: LoginView, meta: { title: '登录' } },
    { path: '/md-editor-probe', name: 'md-editor-probe', component: MdEditorV3ProbeView, meta: { requiresAuth: true, title: '编辑器探针' } },
    { path: '/', name: 'dashboard', component: DashboardView, meta: { requiresAuth: true, title: '仪表盘' } },
  ],
})

router.beforeEach(async (to) => {
  if (!to.meta.requiresAuth) {
    if (to.name === 'login' && isLoggedIn()) {
      try {
        await adminApi.getMe()
        return '/'
      } catch {
        document.cookie = 'admin_logged_in=; path=/; max-age=0'
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
    document.cookie = 'logged_in=; path=/; max-age=0'
    return '/login'
  }
})
