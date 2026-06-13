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
      meta: { title: '安装' },
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { title: '首页' },
    },
    {
      path: '/article/:id',
      name: 'article',
      component: ArticleView,
      meta: { title: '文章详情' },
    },
    {
      path: '/search',
      name: 'search',
      component: SearchView,
      meta: { title: '搜索' },
    },
    {
      path: '/category/:slug',
      name: 'category',
      component: CategoryView,
      meta: { title: '分类' },
    },
    {
      path: '/tag/:slug',
      name: 'tag',
      component: TagView,
      meta: { title: '标签' },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { title: '注册' },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { title: '登录' },
    },
    {
      path: '/friend-links',
      name: 'friend-links',
      component: FriendLinksView,
      meta: { title: '友情链接' },
    },
    {
      path: '/categories',
      name: 'categories',
      component: CategoriesView,
      meta: { title: '分类' },
    },
    {
      path: '/archive',
      name: 'archive',
      component: ArchiveView,
      meta: { title: '归档' },
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView,
      meta: { title: 'About' },
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { title: '个人中心', requiresAuth: true },
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
    const loggedIn = document.cookie.split('; ').some(c => c.startsWith('logged_in='))
    if (!loggedIn) {
      return { name: 'login' }
    }
  }

  return true
})
