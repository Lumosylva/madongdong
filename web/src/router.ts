import { createRouter, createWebHistory } from 'vue-router'

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
      path: '/article/details/:id',
      name: 'article',
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
      component: () => import('./views/RegisterView.vue'),
      meta: { title: 'register.title' },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('./views/LoginView.vue'),
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
    try {
      const res = await fetch('/api/v1/install/status')
      if (!res.ok) {
        cachedInstallStatus = false
      } else {
        const data = (await res.json()) as { success?: boolean; data?: { installed?: boolean } }
        cachedInstallStatus = !!data?.data?.installed
      }
    } catch {
      cachedInstallStatus = false
    }
    if (!cachedInstallStatus) {
      return { name: 'install' }
    }
  }

  if (to.meta.requiresAuth) {
    const loggedIn = document.cookie.split('; ').some(c => c.startsWith('web_logged_in='))
    if (!loggedIn) {
      return { name: 'login' }
    }
  }

  return true
})
