<template>
  <div class="shell" v-if="data">
    <WebTopbar
      :title="data.site.site_title"
      :subtitle="data.site.site_subtitle || '记录技术、生活与长期主义'"
      :logo-url="toAbsoluteAssetUrl(data.site.site_logo)"
      :nav-items="data.nav_items"
      :theme="theme"
      :current-path="route.path"
      :current-full-path="route.fullPath"
      :search-keyword="keyword"
      @update:search-keyword="keyword = $event"
      @toggle-theme="toggleTheme"
      @search="goSearch"
    />

    <main class="layout">
      <section class="content-panel">
        <div class="section-head">
          <h2>最新文章</h2>
        </div>
        <article v-for="article in data.latest_articles.items" :key="article.id" class="article-card">
          <div class="card-meta">
            <span>{{ article.category.name }}</span>
            <span>{{ article.author.nickname }}</span>
            <span>{{ formatDate(article.published_at || article.created_at) }}</span>
          </div>
          <RouterLink :to="`/article/${article.id}`" class="card-title">{{ article.title }}</RouterLink>
          <p class="card-summary">{{ article.summary }}</p>
          <div class="card-footer">
            <span>热度 {{ article.view_count }}</span>
            <span>评论 {{ article.comment_count }}</span>
          </div>
        </article>
        <div class="pager-meta">第 {{ data.latest_articles.page }} / {{ data.latest_articles.total_pages }} 页</div>
        <div class="pager">
          <button v-if="page > 1" @click="changePage(page - 1)">上一页</button>
          <button v-if="page < data.latest_articles.total_pages" @click="changePage(page + 1)">下一页</button>
        </div>
      </section>

      <aside class="sidebar">
        <div class="sidebar-card">
          <h3>热门文章</h3>
          <div class="hot-list">
            <RouterLink v-for="item in data.hot_articles" :key="item.id" :to="`/article/${item.id}`" class="hot-link">
              <strong>{{ item.title }}</strong>
              <div class="hot-stats">
                <span class="hot-meta">浏览 {{ item.view_count }}</span>
                <span class="hot-meta">评论 {{ item.comment_count }}</span>
              </div>
            </RouterLink>
          </div>
        </div>
      </aside>
    </main>

    <WebFooter :icp-beian="data.site.icp_beian" :copyright-text="data.site.copyright_text" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { toAbsoluteAssetUrl, webApi } from '../api'
import WebFooter from '../components/WebFooter.vue'
import WebTopbar from '../components/WebTopbar.vue'
import type { HomeResponse } from '../types'

const router = useRouter()
const route = useRoute()
const data = ref<HomeResponse | null>(null)
const keyword = ref('')
const page = ref(1)
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

const loadData = async () => {
  data.value = await webApi.getHome(page.value)
  applySiteMeta(data.value.site.site_title, data.value.site.site_subtitle, data.value.site.site_logo)
}

const changePage = async (value: number) => {
  page.value = value
  await loadData()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const goSearch = () => {
  if (!keyword.value.trim()) return
  router.push(`/search?keyword=${encodeURIComponent(keyword.value.trim())}`)
}

const formatDate = (value: string) => new Date(value).toLocaleDateString('zh-CN')

onMounted(() => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  loadData()
})
</script>
