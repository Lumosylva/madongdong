<template>
  <div class="search-page" v-if="data">
    <WebTopbar
      :title="data.site.site_title"
      :nav-items="data.nav_items"
      :theme="theme"
      :current-path="route.path"
      :search-keyword="keyword"
      :collapsible-search="true"
      @update:search-keyword="keyword = $event"
      @toggle-theme="toggleTheme"
      @search="goSearch"
    />

    <header class="search-header">
      <RouterLink to="/" class="back-link">← 首页</RouterLink>
      <h1>搜索：{{ data.keyword }}</h1>
    </header>

    <section class="search-result-panel">
      <article v-for="article in data.articles.items" :key="article.id" class="search-card">
        <RouterLink :to="`/article/${article.id}`" class="search-title">{{ article.title }}</RouterLink>
        <p>{{ article.summary }}</p>
        <div class="search-meta">
          <span>{{ article.category.name }}</span>
          <span>{{ article.author.nickname }}</span>
          <span>{{ article.view_count }} 热度</span>
        </div>
      </article>
    </section>

    <WebFooter :icp-beian="data.site.icp_beian" :copyright-text="data.site.copyright_text" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { webApi } from '../api'
import WebFooter from '../components/WebFooter.vue'
import WebTopbar from '../components/WebTopbar.vue'
import type { SearchResponse } from '../types'

const route = useRoute()
const router = useRouter()
const data = ref<SearchResponse | null>(null)
const keyword = ref('')
type ThemeMode = 'light' | 'dark'
const theme = ref<ThemeMode>('light')

const applyTheme = (value: ThemeMode) => {
  theme.value = value
  document.documentElement.dataset.theme = value
  localStorage.setItem('md-theme', value)
}

const toggleTheme = () => {
  applyTheme(theme.value === 'light' ? 'dark' : 'light')
}

const goSearch = () => {
  if (!keyword.value.trim()) return
  router.push(`/search?keyword=${encodeURIComponent(keyword.value.trim())}`)
}

const loadData = async () => {
  const queryKeyword = String(route.query.keyword || '')
  keyword.value = queryKeyword
  if (!queryKeyword) return
  data.value = await webApi.search(queryKeyword)
}

watch(() => route.query.keyword, loadData)
onMounted(() => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  loadData()
})
</script>
