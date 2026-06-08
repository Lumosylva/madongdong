import { createRouter, createWebHistory } from 'vue-router'

import ArticleView from './views/ArticleView.vue'
import HomeView from './views/HomeView.vue'
import SearchView from './views/SearchView.vue'
import CategoryView from './views/CategoryView.vue'
import TagView from './views/TagView.vue'
import RegisterView from './views/RegisterView.vue'
import LoginView from './views/LoginView.vue'
import FriendLinksView from './views/FriendLinksView.vue'
import InstallView from './views/InstallView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/install',
      name: 'install',
      component: InstallView,
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/article/:id',
      name: 'article',
      component: ArticleView,
    },
    {
      path: '/search',
      name: 'search',
      component: SearchView,
    },
    {
      path: '/category/:slug',
      name: 'category',
      component: CategoryView,
    },
    {
      path: '/tag/:slug',
      name: 'tag',
      component: TagView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/friend-links',
      name: 'friend-links',
      component: FriendLinksView,
    },
  ],
})

router.beforeEach(async (to) => {
  if (to.name === 'install') return true
  try {
    const res = await fetch('/api/v1/install/status')
    if (!res.ok) {
      return { name: 'install' }
    }
    const data = (await res.json()) as { success?: boolean; data?: { installed?: boolean } }
    if (!data?.data?.installed) {
      return { name: 'install' }
    }
  } catch {
    return { name: 'install' }
  }
  return true
})
