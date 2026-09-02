import { createRouter, createWebHistory } from 'vue-router'
import { API_BASE } from './api'

/** 安装状态缓存：首次查询后不再重复请求（安装态在运行期不会变） */
let cachedInstallStatus: boolean | null = null

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/install',
      name: 'install',
      component: () => import('./views/InstallView.vue'),
      meta: { title: 'install.title' },
    },
    {
      path: '/',
      name: 'home',
      component: () => import('./views/HomeView.vue'),
      meta: { title: 'common.home' },
    },
    {
      path: '/article/:slug',
      name: 'article',
      component: () => import('./views/ArticleView.vue'),
      meta: { title: 'article.content' },
    },
    {
      path: '/article/details/:id',
      name: 'article-legacy',
      component: () => import('./views/ArticleView.vue'),
      meta: { title: 'article.content' },
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('./views/SearchView.vue'),
      meta: { title: 'search.title' },
    },
    {
      path: '/category/:slug',
      name: 'category',
      component: () => import('./views/CategoryView.vue'),
      meta: { title: 'categories.title' },
    },
    {
      path: '/tag/:slug',
      name: 'tag',
      component: () => import('./views/TagView.vue'),
      meta: { title: 'tag.title' },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('./views/AuthView.vue'),
      meta: { title: 'register.title' },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('./views/AuthView.vue'),
      meta: { title: 'login.title' },
    },
    {
      path: '/friend-links',
      name: 'friend-links',
      component: () => import('./views/FriendLinksView.vue'),
      meta: { title: 'friendLinks.title' },
    },
    {
      path: '/categories',
      name: 'categories',
      component: () => import('./views/CategoriesView.vue'),
      meta: { title: 'categories.title' },
    },
    {
      path: '/archive',
      name: 'archive',
      component: () => import('./views/ArchiveView.vue'),
      meta: { title: 'archive.title' },
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('./views/AboutView.vue'),
      meta: { title: 'about.title' },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('./views/ProfileView.vue'),
      meta: { title: 'profile.title', requiresAuth: true },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('./views/NotFoundView.vue'),
      meta: { title: 'notFound.title' },
    },
  ],
})

router.beforeEach(async (to) => {
  if (to.name === 'install') return true

  // 安装状态缓存：只在首次导航时查询一次，后续不再请求
  if (!cachedInstallStatus) {
    const controller = new AbortController()
    const timeout = window.setTimeout(() => controller.abort(), 5000)
    try {
      const res = await fetch(`${API_BASE}/install/status`, { signal: controller.signal })
      if (!res.ok) {
        // 状态接口暂时不可用时不要误判为未安装，交给页面显示请求错误。
        cachedInstallStatus = true
      } else {
        const data = (await res.json()) as { success?: boolean; data?: { installed?: boolean } }
        cachedInstallStatus = !!data?.data?.installed
      }
    } catch {
      // 网络异常不是安装状态，避免把用户带到错误的安装页面。
      cachedInstallStatus = true
    } finally {
      window.clearTimeout(timeout)
    }
    if (!cachedInstallStatus) {
      return { name: 'install' }
    }
  }

  if (to.meta.requiresAuth) {
    const loggedIn = document.cookie.split('; ').some(c => c.startsWith('web_logged_in='))
    if (!loggedIn) {
      localStorage.setItem('md-login-return', to.fullPath)
      return { name: 'login' }
    }
  }

  return true
})
