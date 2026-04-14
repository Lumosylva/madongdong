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

    <transition name="welcome-toast-fade">
      <div v-if="welcomeMessage" class="welcome-toast">{{ welcomeMessage }}</div>
    </transition>

    <main class="layout">
      <section class="content-panel">
        <article v-for="article in data.latest_articles.items" :key="article.id" class="article-card">
          <RouterLink :to="`/article/${article.id}`" class="card-title">{{ truncateText(article.title, 50) }}</RouterLink>
          <p class="card-summary">{{ truncateText(article.summary, 120) }}</p>
          <div class="card-meta">
            <span>{{ article.category?.name || '未分类' }}</span>
            <span>{{ article.author?.nickname || 'admin' }}</span>
            <span>{{ formatRelativeTime(article.published_at || article.created_at) }}</span>
            <span>{{ article.view_count }} 浏览</span>
            <span>{{ article.comment_count }} 评论</span>
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
                <span class="hot-meta">{{ formatRelativeTime(item.published_at || item.created_at) }}</span>
                <span class="hot-meta">{{ item.view_count }} 浏览</span>
                <span class="hot-meta">{{ item.comment_count }} 评论</span>
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
const welcomeMessage = ref('')
const welcomeShownKey = 'md-home-welcome-shown'
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

const hydrateWelcomeName = async () => {
  const token = localStorage.getItem('md_web_token')
  if (!token) return

  if (localStorage.getItem(welcomeShownKey) === '1') {
    return
  }

  try {
    const currentUser = await webApi.getCurrentWebUser()
    const name = currentUser?.nickname || currentUser?.username || localStorage.getItem('md-reader-nickname') || ''
    if (name) {
      localStorage.setItem('md-reader-nickname', name)
      welcomeMessage.value = `欢迎回来，${name}`
      localStorage.setItem(welcomeShownKey, '1')
      setTimeout(() => {
        welcomeMessage.value = ''
      }, 2200)
    }
  } catch {
    const fallbackName = localStorage.getItem('md-reader-nickname')
    if (fallbackName) {
      welcomeMessage.value = `欢迎回来，${fallbackName}`
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

const goSearch = () => {
  if (!keyword.value.trim()) return
  router.push(`/search?keyword=${encodeURIComponent(keyword.value.trim())}`)
}

const truncateText = (value: string | null | undefined, maxLength: number) => {
  const text = String(value || '').trim()
  if (!text) return ''
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text
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

  if (diffMs < hour) {
    const minutes = Math.max(1, Math.floor(diffMs / minute))
    return `${minutes} 分钟前`
  }
  if (diffMs < day) {
    const hours = Math.floor(diffMs / hour)
    return `${hours} 小时前`
  }
  if (diffMs < year) {
    const days = Math.floor(diffMs / day)
    return `${days} 天前`
  }
  const years = Math.floor(diffMs / year)
  return `${years} 年前`
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
