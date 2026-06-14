import { createRouter, createWebHistory } from 'vue-router'

import AboutView from './views/AboutView.vue'
import ArchiveView from './views/ArchiveView.vue'
import ArticleView from './views/ArticleView.vue'
import CategoriesView from './views/CategoriesView.vue'
import HomeView from './views/HomeView.vue'
import SearchView from './views/SearchView.vue'
import CategoryView from './views/CategoryView.vue'
import TagView from './views/TagView.vue'
import RegisterView from './views/RegisterView.vue'
import LoginView from './views/LoginView.vue'
import FriendLinksView from './views/FriendLinksView.vue'
import InstallView from './views/InstallView.vue'
import ProfileView from './views/ProfileView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/install',
      name: 'install',
      component: InstallView,
      meta: { title: 'install.title' },
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { title: 'common.home' },
    },
    {
      path: '/article/:id',
      name: 'article',
      component: ArticleView,
      meta: { title: 'article.content' },
    },
    {
      path: '/search',
      name: 'search',
      component: SearchView,
      meta: { title: 'search.title' },
    },
    {
      path: '/category/:slug',
      name: 'category',
      component: CategoryView,
      meta: { title: 'categories.title' },
    },
    {
      path: '/tag/:slug',
      name: 'tag',
      component: TagView,
      meta: { title: 'tag.title' },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { title: 'register.title' },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { title: 'login.title' },
    },
    {
      path: '/friend-links',
      name: 'friend-links',
      component: FriendLinksView,
      meta: { title: 'friendLinks.title' },
    },
    {
      path: '/categories',
      name: 'categories',
      component: CategoriesView,
      meta: { title: 'categories.title' },
    },
    {
      path: '/archive',
      name: 'archive',
      component: ArchiveView,
      meta: { title: 'archive.title' },
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView,
      meta: { title: 'about.title' },
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { title: 'profile.title', requiresAuth: true },
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

  if (to.meta.requiresAuth) {
    const loggedIn = document.cookie.split('; ').some(c => c.startsWith('web_logged_in='))
    if (!loggedIn) {
      return { name: 'login' }
    }
  }

  return true
})
