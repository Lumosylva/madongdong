<template>
  <div class="search-page unified-list-page" v-if="data">
    <WebTopbar
      :title="data.site.site_title"
      :subtitle="data.site.site_subtitle || t('home.subtitle')"
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

    <header class="list-page-header">
      <RouterLink to="/" class="back-link list-page-back">
        <svg class="list-page-back-icon" viewBox="0 0 16 16" aria-hidden="true"><path d="M10.5 3 5 8l5.5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
        {{ t('common.backToHome') }}
      </RouterLink>
      <div class="list-page-title-wrap">
        <p class="list-page-eyebrow">{{ t('search.title') }}</p>
        <h1 class="list-page-title">{{ data.keyword }}</h1>
      </div>
    </header>

    <section class="search-result-panel unified-list-panel">
      <article v-for="article in data.articles.items" :key="article.id" class="search-card unified-list-card">
        <RouterLink :to="`/article/${article.slug}`" class="search-title">{{ article.title }}</RouterLink>
        <p>{{ article.summary }}</p>
        <div class="search-meta unified-list-meta">
          <span>{{ article.category?.name || t('common.untitled') }}</span>
          <span>{{ article.author?.nickname || 'admin' }}</span>
          <span>{{ formatRelativeTime(article.published_at || article.created_at) }}</span>
          <span>{{ article.view_count }} {{ t('common.views') }}</span>
          <span>{{ article.comment_count }} {{ t('common.comments') }}</span>
        </div>
      </article>

      <div class="pager-row unified-pager-row">
        <div class="pager-meta">
          {{ t('common.page', { n: data.articles.page }) }} / {{ data.articles.total_pages }}
          <span class="pager-size">
            {{ t('common.perPage') }}
            <select v-model.number="pageSize" class="pager-size-select" @change="changePageSize">
              <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
            </select>
            {{ t('common.items') }}
          </span>
        </div>
        <div class="pager-actions">
          <button v-if="hasPrevPage" class="pager-prev-btn" @click="changePage(page - 1)">{{ t('common.previous') }}</button>
          <button v-if="hasNextPage" class="pager-next-btn" @click="changePage(page + 1)">{{ t('common.next') }}</button>
        </div>
      </div>
    </section>

    <WebFooter :icp-beian="data.site.icp_beian" :copyright-text="data.site.copyright_text" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { toAbsoluteAssetUrl, webApi } from '../api'
import WebFooter from '../components/WebFooter.vue'
import WebTopbar from '../components/WebTopbar.vue'
import { applySiteMetaFromSetting, buildPageTitle, setSiteSetting } from '../site-meta'
import { useFormatRelativeTime } from '../utils/time'
import type { SearchResponse } from '../types'

const { t } = useI18n()
const { formatRelativeTime } = useFormatRelativeTime()
const route = useRoute()
const router = useRouter()
const data = ref<SearchResponse | null>(null)
const keyword = ref('')
const page = ref(1)
const pageSize = ref(20)
const pageSizeOptions = [10, 20, 30, 50]
const totalPages = computed(() => data.value?.articles.total_pages || 1)
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

const hasPrevPage = computed(() => page.value > 1)
const hasNextPage = computed(() => page.value < totalPages.value)

const changePageSize = async () => {
  page.value = 1
  await loadData()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}



const loadData = async () => {
  const queryKeyword = String(route.query.keyword || '')
  keyword.value = queryKeyword
  if (!queryKeyword) return
  data.value = await webApi.search(queryKeyword, page.value, pageSize.value)
  setSiteSetting(data.value.site)
  applySiteMetaFromSetting(data.value.site)
  document.title = buildPageTitle(route.meta?.title as string | undefined)
}

watch(() => route.query.keyword, async () => {
  page.value = 1
  await loadData()
})
onMounted(() => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  loadData()
})
</script>
