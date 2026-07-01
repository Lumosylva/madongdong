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
        <p class="search-result-count" v-if="data.articles.total > 0">
          {{ t('search.resultCount', { n: data.articles.total }) }}
        </p>
      </div>
    </header>

    <section class="search-result-panel unified-list-panel">
      <template v-if="loading">
        <div class="search-loading">
          <div class="search-loading-spinner"></div>
          <p>{{ t('search.searching') }}</p>
        </div>
      </template>

      <template v-else-if="data.articles.items.length === 0">
        <div class="search-empty">
          <svg class="search-empty-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <h3>{{ t('search.noResults') }}</h3>
          <p>{{ t('search.noResultsHint') }}</p>
          <RouterLink to="/" class="search-empty-home">{{ t('search.tryOther') }}</RouterLink>
        </div>
      </template>

      <template v-else>
        <article v-for="article in data.articles.items" :key="article.id" class="search-card unified-list-card">
          <RouterLink :to="`/article/${article.slug}`" class="search-title" v-html="highlightKeyword(article.title)"></RouterLink>
          <p class="search-card-summary" v-html="highlightKeyword(article.summary)"></p>
          <div class="search-meta unified-list-meta">
            <span class="search-meta-item search-meta-category" v-if="article.category?.name">
              <svg class="search-meta-icon" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M2 4.5A1.5 1.5 0 013.5 3H6.5l1.5 2H12.5A1.5 1.5 0 0114 6.5v5a1.5 1.5 0 01-1.5 1.5h-9A1.5 1.5 0 012 11.5v-7z" stroke="currentColor" stroke-width="1.2"/></svg>
              {{ article.category.name }}
            </span>
            <span class="search-meta-item">
              <svg class="search-meta-icon" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M8 1a4 4 0 014 4c0 1.95-2 3.5-4 5C6 8.5 4 6.95 4 6a4 4 0 014-4z" stroke="currentColor" stroke-width="1.2"/><circle cx="8" cy="5" r="1.5" fill="currentColor"/></svg>
              {{ article.author?.nickname || 'admin' }}
            </span>
            <span class="search-meta-item">
              <svg class="search-meta-icon" viewBox="0 0 16 16" fill="none" aria-hidden="true"><rect x="2" y="3" width="12" height="11" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M2 6.5h12M5.5 1.5v3M10.5 1.5v3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
              {{ formatRelativeTime(article.published_at || article.created_at) }}
            </span>
            <span class="search-meta-item">
              <svg class="search-meta-icon" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M1 8s2.5-5 7-5 7 5 7 5-2.5 5-7 5-7-5-7-5z" stroke="currentColor" stroke-width="1.2"/><circle cx="8" cy="8" r="2.5" stroke="currentColor" stroke-width="1.2"/></svg>
              {{ article.view_count }} {{ t('common.views') }}
            </span>
            <span class="search-meta-item">
              <svg class="search-meta-icon" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M2 3.5A1.5 1.5 0 013.5 2h9A1.5 1.5 0 0114 3.5v7a1.5 1.5 0 01-1.5 1.5H5l-3 2v-2H3.5A1.5 1.5 0 012 10.5v-7z" stroke="currentColor" stroke-width="1.2"/></svg>
              {{ article.comment_count }} {{ t('common.comments') }}
            </span>
          </div>
        </article>

        <div class="pager-row unified-pager-row">
          <div class="pager-meta">
            {{ t('common.page', { n: data.articles.page }) }} / {{ data.articles.total_pages }}
            <span class="pager-size">
              {{ t('common.perPage') }}
              <select v-model.number="pageSize" class="pager-size-select" :aria-label="t('common.perPage')" @change="changePageSize">
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
      </template>
    </section>

    <WebFooter :icp-beian="data.site.icp_beian" :police-beian="data.site.police_beian" :copyright-text="data.site.copyright_text" />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { toAbsoluteAssetUrl, webApi } from '../api'
import WebFooter from '../components/WebFooter.vue'
import WebTopbar from '../components/WebTopbar.vue'
import { applySiteMetaFromSetting, buildPageTitle, setSiteSetting } from '../site-meta'
import { useFormatRelativeTime } from '../utils/time'
import type { SearchResponse } from '../types'
import { useTheme } from '../composables/useTheme'

const { t } = useI18n()
const { formatRelativeTime } = useFormatRelativeTime()
const route = useRoute()
const router = useRouter()
const { theme, toggleTheme, initTheme, listenThemeChange, destroyTheme } = useTheme()
const data = ref<SearchResponse | null>(null)
const keyword = ref('')
const page = ref(1)
const pageSize = ref(20)
const pageSizeOptions = [10, 20, 30, 50]
const loading = ref(false)
const totalPages = computed(() => data.value?.articles.total_pages || 1)

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

const highlightKeyword = (text: string | null | undefined): string => {
  const raw = String(text || '').trim()
  const kw = keyword.value.trim()
  if (!raw || !kw) return raw
  const escaped = kw.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return raw.replace(new RegExp(`(${escaped})`, 'gi'), '<mark class="search-highlight">$1</mark>')
}

const loadData = async () => {
  const queryKeyword = String(route.query.keyword || '')
  keyword.value = queryKeyword
  if (!queryKeyword) return
  loading.value = true
  try {
    data.value = await webApi.search(queryKeyword, page.value, pageSize.value)
    setSiteSetting(data.value.site)
    applySiteMetaFromSetting(data.value.site)
    document.title = buildPageTitle(route.meta?.title as string | undefined)
  } finally {
    loading.value = false
  }
}

watch(() => route.query.keyword, async () => {
  page.value = 1
  await loadData()
})
onMounted(() => {
  initTheme()
  listenThemeChange()
  loadData()
})

onBeforeUnmount(() => {
  destroyTheme()
})
</script>
