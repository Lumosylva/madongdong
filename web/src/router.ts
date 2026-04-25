import { createRouter, createWebHistory } from 'vue-router'

import ArticleView from './views/ArticleView.vue'
import HomeView from './views/HomeView.vue'
import SearchView from './views/SearchView.vue'
import CategoryView from './views/CategoryView.vue'
import TagView from './views/TagView.vue'
import RegisterView from './views/RegisterView.vue'
import LoginView from './views/LoginView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
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
  ],
})
