<template>
  <div class="search-page" v-if="data">
    <WebTopbar
      :title="data.site.site_title"
      :logo-url="toAbsoluteAssetUrl(data.site.site_logo)"
      :nav-items="data.nav_items"
      :theme="theme"
      :current-path="route.path"
      :current-full-path="route.fullPath"
      :collapsible-search="true"
      @toggle-theme="toggleTheme"
    />

    <header class="list-page-header">
      <RouterLink to="/" class="back-link list-page-back">← 首页</RouterLink>
      <div class="list-page-title-wrap">
        <p class="list-page-eyebrow">时间轴</p>
        <h1 class="list-page-title">归档</h1>
        <p class="list-page-subtitle">共 {{ data.total }} 篇文章</p>
      </div>
    </header>

    <section class="search-result-panel archive-panel">
      <div v-if="data.archive.length === 0" class="archive-summary">暂无已发布文章。</div>

      <div
        v-for="yearGroup in data.archive"
        :key="yearGroup.year"
        class="archive-year-group"
      >
        <button
          type="button"
          class="archive-year-header"
          @click="toggleYear(yearGroup.year)"
        >
          <span class="archive-toggle-icon" :class="{ open: isYearOpen(yearGroup.year) }">▶</span>
          <span class="archive-year-title">{{ yearGroup.year }}</span>
          <span class="archive-year-count">{{ yearGroup.count }} 篇</span>
        </button>

        <transition name="archive-collapse">
          <div v-if="isYearOpen(yearGroup.year)" class="archive-year-body">
            <div
              v-for="monthGroup in yearGroup.months"
              :key="monthGroup.month"
              class="archive-month-group"
            >
              <div class="archive-month-header">
                <span>{{ monthNames[monthGroup.month - 1] }}</span>
                <span class="archive-month-count">{{ monthGroup.count }} 篇</span>
              </div>
              <div
                v-for="article in monthGroup.articles"
                :key="article.id"
                class="archive-article-row"
              >
                <span class="archive-article-date">{{ formatDay(article.published_at) }}</span>
                <RouterLink :to="`/article/${article.id}`" class="archive-article-link" :title="article.title">
                  {{ article.title }}
                </RouterLink>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </section>

    <WebFooter :icp-beian="data.site.icp_beian" :copyright-text="data.site.copyright_text" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { toAbsoluteAssetUrl, webApi } from '../api'
import WebFooter from '../components/WebFooter.vue'
import WebTopbar from '../components/WebTopbar.vue'
import { applySiteMetaFromSetting, buildPageTitle, setSiteSetting } from '../site-meta'
import type { ArchiveResponse } from '../types'

const route = useRoute()
const data = ref<ArchiveResponse | null>(null)
type ThemeMode = 'light' | 'dark'
const theme = ref<ThemeMode>('light')

const openYears = ref<Set<number>>(new Set())

const monthNames = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']

const applyTheme = (value: ThemeMode) => {
  theme.value = value
  document.documentElement.dataset.theme = value
  localStorage.setItem('md-theme', value)
}

const toggleTheme = () => {
  applyTheme(theme.value === 'light' ? 'dark' : 'light')
}

const isYearOpen = (year: number) => openYears.value.has(year)

const toggleYear = (year: number) => {
  if (openYears.value.has(year)) {
    openYears.value.delete(year)
  } else {
    openYears.value.add(year)
  }
}

const parseDateTime = (value: string) => {
  const text = String(value || '').trim()
  if (!text) return new Date(0)
  if (/Z|[+-]\d{2}:?\d{2}$/.test(text)) return new Date(text)
  return new Date(`${text}Z`)
}

const formatDay = (value: string) => {
  const d = parseDateTime(value)
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${mm}-${dd}`
}

const loadData = async () => {
  data.value = await webApi.getArchive()
  setSiteSetting(data.value.site)
  applySiteMetaFromSetting(data.value.site)
  document.title = buildPageTitle('归档')
  // Expand the most recent year by default
  if (data.value.archive.length > 0) {
    openYears.value.add(data.value.archive[0].year)
  }
}

onMounted(() => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  loadData()
})
</script>
