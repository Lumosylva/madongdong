<template>
  <div class="search-page" v-if="data">
    <WebTopbar
      :title="data.site.site_title"
      :logo-url="toAbsoluteAssetUrl(data.site.site_logo)"
      :nav-items="data.nav_items"
      :theme="theme"
      :current-path="route.path"
      :current-full-path="route.fullPath"
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
          <span>{{ formatRelativeTime(article.published_at || article.created_at) }}</span>
          <span>{{ article.view_count }} 浏览</span>
          <span>{{ article.comment_count }} 评论</span>
        </div>
      </article>
    </section>

    <WebFooter :icp-beian="data.site.icp_beian" :copyright-text="data.site.copyright_text" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { toAbsoluteAssetUrl, webApi } from '../api'
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

const applySiteMeta = (siteTitle: string, siteSubtitle: string | null, siteLogo: string | null) => {
  const title = String(siteTitle || '').trim()
  const subtitle = String(siteSubtitle || '').trim()
  document.title = title && subtitle ? `${title} - ${subtitle}` : (title || subtitle || 'MaDongDong')

  const iconUrl = toAbsoluteAssetUrl(siteLogo)
  if (!iconUrl) return

  let iconLink = document.querySelector("link[rel='icon']") as HTMLLinkElement | null
  if (!iconLink) {
    iconLink = document.createElement('link')
    iconLink.rel = 'icon'
    document.head.appendChild(iconLink)
  }
  iconLink.href = iconUrl
}

const parseDateTime = (value: string) => {
  const text = String(value || '').trim()
  if (!text) return new Date(0)
  if (/Z|[+-]\d{2}:?\d{2}$/.test(text)) return new Date(text)
  return new Date(`${text}Z`)
}

const loadData = async () => {
  const queryKeyword = String(route.query.keyword || '')
  keyword.value = queryKeyword
  if (!queryKeyword) return
  data.value = await webApi.search(queryKeyword)
  applySiteMeta(data.value.site.site_title, data.value.site.site_subtitle, data.value.site.site_logo)
}

watch(() => route.query.keyword, loadData)
onMounted(() => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  loadData()
})
</script>
