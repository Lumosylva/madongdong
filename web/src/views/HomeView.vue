<template>
  <div class="shell home-shell" v-if="data">
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

    <transition name="welcome-toast-fade">
      <div v-if="welcomeMessage" class="welcome-toast">{{ welcomeMessage }}</div>
    </transition>

    <main class="layout">
      <section class="content-panel">
        <article v-for="article in data.latest_articles.items" :key="article.id" class="article-card">
          <RouterLink :to="`/article/${article.slug}`" class="card-title">{{ truncateText(article.title, 50) }}</RouterLink>
          <p class="card-summary">{{ truncateText(article.summary, 120) }}</p>
          <div class="card-meta">
            <span>{{ article.category?.name || t('common.untitled') }}</span>
            <span>{{ article.author?.nickname || 'admin' }}</span>
            <span>{{ t('time.publishedAt') }}{{ formatRelativeTime(article.published_at || article.created_at) }}</span>
            <span>{{ t('time.updatedAt') }}{{ formatRelativeTime(getArticleUpdatedAt(article)) }}</span>
            <span>{{ article.view_count }} {{ t('common.views') }}</span>
            <span>{{ article.comment_count }} {{ t('common.comments') }}</span>
          </div>
        </article>
        <div class="pager-row">
          <div class="pager-meta">
            {{ t('common.page', { n: data.latest_articles.page }) }} / {{ data.latest_articles.total_pages }}
            <span class="pager-size">{{ t('common.perPage') }}
              <select v-model.number="homePageSize" class="pager-size-select" @change="changeHomePageSize">
                <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
              </select>
              {{ t('common.items') }}
            </span>
          </div>
          <div class="pager-actions">
            <button v-if="page > 1" class="pager-prev-btn" @click="changePage(page - 1)">{{ t('common.previous') }}</button>
            <button v-if="page < data.latest_articles.total_pages" class="pager-next-btn" @click="changePage(page + 1)">{{ t('common.next') }}</button>
          </div>
        </div>
      </section>

      <aside class="sidebar">
        <div class="sidebar-card">
          <h3>{{ t('home.hotArticles') }}</h3>
          <div class="hot-list">
            <RouterLink v-for="item in data.hot_articles" :key="item.id" :to="`/article/${item.slug}`" class="hot-link">
              <strong>{{ item.title }}</strong>
              <div class="hot-stats">
                <span class="hot-meta">{{ formatRelativeTime(item.published_at || item.created_at) }}</span>
                <span class="hot-meta">{{ item.view_count }} {{ t('common.views') }}</span>
                <span class="hot-meta">{{ item.comment_count }} {{ t('common.comments') }}</span>
              </div>
            </RouterLink>
          </div>
        </div>
      </aside>
    </main>

    <HomeBgmPlayer v-if="data.site.homepage_bgm_url" :bgm-url="data.site.homepage_bgm_url" />
    <WebFooter :icp-beian="data.site.icp_beian" :friend-links="friendLinks" :copyright-text="data.site.copyright_text" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { toAbsoluteAssetUrl, webApi } from '../api'
import HomeBgmPlayer from '../components/HomeBgmPlayer.vue'
import WebFooter from '../components/WebFooter.vue'
import WebTopbar from '../components/WebTopbar.vue'
import { applySiteMeta, setSiteSetting } from '../site-meta'
import { useFormatRelativeTime, getArticleUpdatedAt } from '../utils/time'
import type { HomeResponse } from '../types'

const { t } = useI18n()
const { formatRelativeTime } = useFormatRelativeTime()
const router = useRouter()
const route = useRoute()
const data = ref<HomeResponse | null>(null)
const keyword = ref('')
const page = ref(1)
const homePageSize = ref(20)
const pageSizeOptions = [10, 20, 30, 50]
const welcomeMessage = ref('')
const welcomeShownKey = 'md-home-welcome-shown'
type ThemeMode = 'light' | 'dark'
const theme = ref<ThemeMode>('light')
const friendLinks = ref<Array<{ id: number; name: string }>>([])

const applyTheme = (value: ThemeMode) => {
  theme.value = value
  document.documentElement.dataset.theme = value
  localStorage.setItem('md-theme', value)
}

const toggleTheme = () => {
  applyTheme(theme.value === 'light' ? 'dark' : 'light')
}

const applyHomeMeta = (siteTitle: string, siteSubtitle: string | null, siteLogo: string | null) => {
  applySiteMeta(siteTitle, siteSubtitle, siteLogo)

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
  data.value = await webApi.getHome(page.value, homePageSize.value)
  friendLinks.value = await webApi.getFriendLinks()
  setSiteSetting(data.value.site)
  applyHomeMeta(data.value.site.site_title, data.value.site.site_subtitle, data.value.site.site_logo)
}

const hydrateWelcomeName = async () => {
  const hasCookie = document.cookie.split('; ').some(c => c.startsWith('web_logged_in='))
  if (!hasCookie) return

  if (localStorage.getItem(welcomeShownKey) === '1') {
    return
  }

  try {
    const currentUser = await webApi.getCurrentWebUser()
    const name = currentUser?.nickname || currentUser?.username || localStorage.getItem('md-reader-nickname') || ''
    if (name) {
      localStorage.setItem('md-reader-nickname', name)
      welcomeMessage.value = t('home.welcomeBack', { name })
      localStorage.setItem(welcomeShownKey, '1')
      setTimeout(() => {
        welcomeMessage.value = ''
      }, 2200)
    }
  } catch {
    const fallbackName = localStorage.getItem('md-reader-nickname')
    if (fallbackName) {
      welcomeMessage.value = t('home.welcomeBack', { name: fallbackName })
      localStorage.setItem(welcomeShownKey, '1')
      setTimeout(() => {
        welcomeMessage.value = ''
      }, 2200)
    }
  }
}

const changePage = async (value: number) => {
  page.value = value
  await loadData()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const changeHomePageSize = async () => {
  page.value = 1
  await loadData()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const goSearch = () => {
  if (!keyword.value.trim()) return
  router.push(`/search?keyword=${encodeURIComponent(keyword.value.trim())}`)
}

const truncateText = (value: string | null | undefined, maxLength: number) => {
  const text = String(value || '').trim()
  if (!text) return ''
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text
}

onMounted(async () => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')

  const onceWelcome = localStorage.getItem('md-welcome-once')
  if (onceWelcome) {
    welcomeMessage.value = onceWelcome
    localStorage.removeItem('md-welcome-once')
    setTimeout(() => {
      welcomeMessage.value = ''
    }, 2600)
  }

  await hydrateWelcomeName()
  await loadData()
})
</script>
