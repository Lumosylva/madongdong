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
      <div>
        <h1>标签：{{ data.tag.name }}</h1>
      </div>
    </header>

    <section class="search-result-panel">
      <article v-for="article in data.articles.items" :key="article.id" class="search-card">
        <RouterLink :to="`/article/${article.id}`" class="search-title">{{ article.title }}</RouterLink>
        <p>{{ article.summary }}</p>
        <div class="search-meta">
          <span>{{ article.category?.name || '未分类' }}</span>
          <span>{{ article.author?.nickname || 'admin' }}</span>
          <span>{{ formatRelativeTime(article.published_at || article.created_at) }}</span>
          <span>{{ article.view_count }} 浏览</span>
          <span>{{ article.comment_count }} 评论</span>
        </div>
      </article>

      <div class="pager-row search-pager-row">
        <div class="pager-meta">
          第 {{ data.articles.page }} / {{ data.articles.total_pages }} 页
          <span class="pager-size">
            每页
            <select v-model.number="pageSize" class="pager-size-select" @change="changePageSize">
              <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
            </select>
            条
          </span>
        </div>
        <div class="pager-actions">
          <button v-if="data.articles.page > 1" class="pager-prev-btn" @click="changePage(data.articles.page - 1)">上一页</button>
          <button v-if="data.articles.page < data.articles.total_pages" class="pager-next-btn" @click="changePage(data.articles.page + 1)">下一页</button>
        </div>
      </div>
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
import type { TagArticlesResponse } from '../types'

const route = useRoute()
const router = useRouter()
const data = ref<TagArticlesResponse | null>(null)
const keyword = ref('')
const page = ref(1)
const pageSize = ref(20)
const pageSizeOptions = [10, 20, 30, 50]
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

const changePage = async (value: number) => {
  page.value = value
  await loadData()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const changePageSize = async () => {
  page.value = 1
  await loadData()
  window.scrollTo({ top: 0, behavior: 'smooth' })
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

const formatRelativeTime = (value: string) => {
  const date = parseDateTime(value)
  const now = Date.now()
  const diffMs = Math.max(0, now - date.getTime())
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  const year = 365 * day

  if (diffMs < hour) return `${Math.max(1, Math.floor(diffMs / minute))} 分钟前`
  if (diffMs < day) return `${Math.max(1, Math.floor(diffMs / hour))} 小时前`
  if (diffMs < year) return `${Math.max(1, Math.floor(diffMs / day))} 天前`
  return `${Math.max(1, Math.floor(diffMs / year))} 年前`
}

const loadData = async () => {
  const slug = String(route.params.slug || '')
  if (!slug) return
  data.value = await webApi.getTagArticles(slug, page.value, pageSize.value)
  keyword.value = data.value.tag.name
  applySiteMeta(data.value.site.site_title, data.value.site.site_subtitle, data.value.site.site_logo)
}

watch(() => route.params.slug, async () => {
  page.value = 1
  await loadData()
})

onMounted(() => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  loadData()
})
</script>
