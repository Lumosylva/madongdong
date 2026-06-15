<template>
  <div class="shell home-shell" :data-hero="data.site.homepage_hero_image ? '1' : '0'" :data-nav="data.site.homepage_hero_image ? navState : ''" v-if="data">
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

    <div v-if="data.site.homepage_hero_image" class="home-hero">
      <div class="home-hero-bg" :style="{ backgroundImage: `url(${toAbsoluteAssetUrl(data.site.homepage_hero_image)})` }"></div>
      <div class="home-hero-overlay"></div>
    </div>

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
import { onBeforeUnmount, onMounted, ref } from 'vue'
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

let lastScrollY = 0
let ticking = false
const navState = ref<'top' | 'hide' | 'show'>('top')

const handleScroll = () => {
  if (ticking) return
  ticking = true
  requestAnimationFrame(() => {
    const scrollY = window.scrollY
    if (scrollY < 80) {
      navState.value = 'top'
    } else if (scrollY > lastScrollY + 5) {
      navState.value = 'hide'
    } else if (scrollY < lastScrollY - 5) {
      navState.value = 'show'
    }
    lastScrollY = scrollY
    ticking = false
  })
}

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

  if (data.value?.site.homepage_hero_image) {
    window.addEventListener('scroll', handleScroll, { passive: true })
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.home-hero {
  position: relative;
  width: 100vw;
  margin-left: calc(50% - 50vw);
  height: 55vh;
  min-height: 360px;
  max-height: 520px;
  margin-top: calc(-1 * var(--web-topbar-offset));
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.home-hero-bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.home-hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.05) 0%, rgba(0, 0, 0, 0.3) 100%);
}

@media (max-width: 960px) {
  .home-hero {
    height: 40vh;
    min-height: 260px;
  }

  .home-shell .layout {
    grid-template-columns: 1fr !important;
    padding-right: 0 !important;
  }

  .home-shell aside.sidebar {
    position: static !important;
    width: auto !important;
    height: auto !important;
    overflow: visible !important;
    pointer-events: auto !important;
  }

  .home-shell .sidebar-card {
    position: static !important;
    width: auto !important;
    max-height: none !important;
    top: auto !important;
    right: auto !important;
  }
}
</style>

<style>
.home-shell[data-hero="1"] .layout {
  grid-template-columns: 1fr minmax(280px, 340px);
  padding-right: 0;
}

.home-shell[data-hero="1"] aside.sidebar {
  position: static;
  width: auto;
  height: auto;
  overflow: visible;
  pointer-events: auto;
}

.home-shell[data-hero="1"] .sidebar-card {
  position: static;
  width: auto;
  max-height: none;
  top: auto;
  right: auto;
}

@media (max-width: 960px) {
  .home-shell[data-hero="1"] .layout {
    grid-template-columns: 1fr;
    padding-right: 0;
  }

  .home-shell[data-hero="1"] aside.sidebar {
    position: static;
    width: auto;
    height: auto;
    overflow: visible;
    pointer-events: auto;
  }

  .home-shell[data-hero="1"] .sidebar-card {
    position: static;
    width: auto;
    max-height: none;
    top: auto;
    right: auto;
  }
}

.home-shell[data-hero="1"] .topbar {
  background: transparent !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  box-shadow: none !important;
  border: none !important;
}

.home-shell[data-hero="1"] .topbar .brand-block h1,
.home-shell[data-hero="1"] .topbar .brand-subtitle,
.home-shell[data-hero="1"] .topbar .nav a,
.home-shell[data-hero="1"] .topbar .search-launch-btn,
.home-shell[data-hero="1"] .topbar .auth-entry,
.home-shell[data-hero="1"] .topbar .lang-trigger,
.home-shell[data-hero="1"] .topbar .lang-label {
  color: #fff;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.home-shell[data-hero="1"] .topbar .nav a:hover,
.home-shell[data-hero="1"] .topbar .auth-entry:hover,
.home-shell[data-hero="1"] .topbar .lang-trigger:hover {
  color: var(--accent);
}

.home-shell[data-hero="1"] .topbar .brand-mark {
  color: #fff;
  background: rgba(255, 255, 255, 0.15);
}

.home-shell[data-hero="1"] .topbar {
  transition: transform 0.3s ease, background 0.3s ease;
}

.home-shell[data-nav="top"] .topbar {
  background: transparent !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  box-shadow: none !important;
}

.home-shell[data-nav="hide"] .topbar {
  transform: translateY(-100%);
}

.home-shell[data-nav="show"] .topbar {
  background: rgba(0, 0, 0, 0.35) !important;
  backdrop-filter: blur(16px) !important;
  -webkit-backdrop-filter: blur(16px) !important;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08) !important;
}

:root[data-theme='dark'] .home-shell[data-nav="show"] .topbar {
  background: rgba(10, 20, 40, 0.7) !important;
  backdrop-filter: blur(16px) saturate(1.2) !important;
  -webkit-backdrop-filter: blur(16px) saturate(1.2) !important;
}

.home-shell[data-hero="1"] .topbar .lang-trigger,
.home-shell[data-hero="1"] .topbar .auth-entry.icon-entry,
:root[data-theme='dark'] .home-shell[data-hero="1"] .topbar .lang-trigger,
:root[data-theme='dark'] .home-shell[data-hero="1"] .topbar .auth-entry.icon-entry {
  background: transparent !important;
  box-shadow: none !important;
  border-color: transparent !important;
}

.home-shell[data-hero="1"] .topbar .lang-trigger:hover,
.home-shell[data-hero="1"] .topbar .auth-entry.icon-entry:hover,
:root[data-theme='dark'] .home-shell[data-hero="1"] .topbar .lang-trigger:hover,
:root[data-theme='dark'] .home-shell[data-hero="1"] .topbar .auth-entry.icon-entry:hover {
  background: rgba(255, 255, 255, 0.12) !important;
  box-shadow: none !important;
}
</style>
