import { createRouter, createWebHistory } from 'vue-router'

import ArticleView from './views/ArticleView.vue'
import HomeView from './views/HomeView.vue'
import SearchView from './views/SearchView.vue'

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
  ],
})
