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
        <p class="list-page-eyebrow">{{ t('tag.title') }}</p>
        <h1 class="list-page-title">{{ data.tag.name }}</h1>
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
            <select v-model.number="pageSize" class="pager-size-select" :aria-label="t('common.perPage')" @change="changePageSize">
              <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
            </select>
            {{ t('common.items') }}
          </span>
        </div>
        <div class="pager-actions">
          <button v-if="data.articles.page > 1" class="pager-prev-btn" @click="changePage(data.articles.page - 1)">{{ t('common.previous') }}</button>
          <button v-if="data.articles.page < data.articles.total_pages" class="pager-next-btn" @click="changePage(data.articles.page + 1)">{{ t('common.next') }}</button>
        </div>
      </div>
    </section>

    <WebFooter :icp-beian="data.site.icp_beian" :police-beian="data.site.police_beian" :copyright-text="data.site.copyright_text" />
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { toAbsoluteAssetUrl, webApi } from '../api'
import WebFooter from '../components/WebFooter.vue'
import WebTopbar from '../components/WebTopbar.vue'
import { applySiteMetaFromSetting, buildPageTitle, setSiteSetting } from '../site-meta'
import { useFormatRelativeTime } from '../utils/time'
import type { TagArticlesResponse } from '../types'
import { useTheme } from '../composables/useTheme'

const { t } = useI18n()
const { formatRelativeTime } = useFormatRelativeTime()
const route = useRoute()
const router = useRouter()
const { theme, toggleTheme, initTheme, listenThemeChange, destroyTheme } = useTheme()
const data = ref<TagArticlesResponse | null>(null)
const keyword = ref('')
const page = ref(1)
const pageSize = ref(20)
const pageSizeOptions = [10, 20, 30, 50]

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



const loadData = async () => {
  const slug = String(route.params.slug || '')
  if (!slug) return
  data.value = await webApi.getTagArticles(slug, page.value, pageSize.value)
  keyword.value = data.value.tag.name
  setSiteSetting(data.value.site)
  applySiteMetaFromSetting(data.value.site)
  document.title = buildPageTitle(`${data.value.tag.name} - ${route.meta?.title as string | undefined}`)
}

watch(() => route.params.slug, async () => {
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
