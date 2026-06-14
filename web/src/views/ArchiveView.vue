<template>
  <div class="search-page" v-if="data">
    <WebTopbar
      :title="data.site.site_title"
      :subtitle="data.site.site_subtitle || t('home.subtitle')"
      :logo-url="toAbsoluteAssetUrl(data.site.site_logo)"
      :nav-items="data.nav_items"
      :theme="theme"
      :current-path="route.path"
      :current-full-path="route.fullPath"
      :collapsible-search="true"
      @toggle-theme="toggleTheme"
    />

    <header class="archive-hero">
      <RouterLink to="/" class="archive-back-link">
        <svg class="archive-back-icon" viewBox="0 0 16 16" aria-hidden="true"><path d="M10.5 3 5 8l5.5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
        {{ t('common.backToHome') }}
      </RouterLink>
      <div class="archive-hero-body">
        <div class="archive-hero-text">
          <p class="archive-hero-eyebrow">Archive</p>
          <h1 class="archive-hero-title">{{ t('archive.title') }}</h1>
          <p class="archive-hero-sub">
            <template v-if="yearRangeText">{{ yearRangeText }} &nbsp;·&nbsp; </template>{{ t('archive.subtitle') }}
          </p>
        </div>
        <div class="archive-hero-metrics">
          <div class="archive-metric-card">
            <strong>{{ data.total }}</strong>
            <span>{{ t('archive.articleCount') }}</span>
          </div>
          <div class="archive-metric-card">
            <strong>{{ data.archive.length }}</strong>
            <span>{{ t('archive.yearCount') }}</span>
          </div>
        </div>
      </div>
    </header>

    <section class="search-result-panel archive-panel">
      <div v-if="data.archive.length === 0" class="archive-summary">{{ t('archive.empty') }}</div>

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
          <span class="archive-year-count">{{ t('archive.count', { n: yearGroup.count }) }}</span>
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
                <span class="archive-month-count">{{ t('archive.count', { n: monthGroup.count }) }}</span>
              </div>
              <div
                v-for="article in monthGroup.articles"
                :key="article.id"
                class="archive-article-row"
              >
                <span class="archive-article-date">{{ formatDay(article.published_at) }}</span>
                <RouterLink :to="`/article/${article.slug}`" class="archive-article-link" :title="article.title">
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
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { toAbsoluteAssetUrl, webApi } from '../api'
import WebFooter from '../components/WebFooter.vue'
import WebTopbar from '../components/WebTopbar.vue'
import { applySiteMetaFromSetting, buildPageTitle, setSiteSetting } from '../site-meta'
import type { ArchiveResponse } from '../types'

const route = useRoute()
const { t } = useI18n()
const data = ref<ArchiveResponse | null>(null)
type ThemeMode = 'light' | 'dark'
const theme = ref<ThemeMode>('light')

const openYears = ref<Set<number>>(new Set())

const yearRangeText = computed(() => {
  if (!data.value || data.value.archive.length === 0) return ''
  const max = data.value.archive[0].year
  const min = data.value.archive[data.value.archive.length - 1].year
  return max === min ? String(max) : `${min} — ${max}`
})

const monthNames = computed(() => t('archive.months') as unknown as string[])

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
  document.title = buildPageTitle(t('archive.title'))
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

<style scoped>
.search-page {
  position: relative;
  padding-top: 10px;
}

.search-page::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 12% 10%, rgba(14, 165, 164, 0.12), transparent 22%),
    radial-gradient(circle at 88% 8%, rgba(234, 154, 24, 0.1), transparent 18%);
  z-index: 0;
}
</style>
