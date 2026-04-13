<template>
  <div class="article-page" v-if="data">
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

    <article class="article-panel">
      <p class="article-category">{{ data.article.category.name }}</p>
      <h1>{{ data.article.title }}</h1>
      <div class="article-meta">
        <span>{{ data.article.author.nickname }}</span>
        <span>{{ formatRelativeTime(data.article.published_at || data.article.created_at) }}</span>
        <span>{{ data.article.view_count }} 浏览</span>
        <span>{{ data.article.comment_count }} 评论</span>
      </div>
      <p class="article-summary">{{ data.article.summary }}</p>
      <img v-if="data.article.cover_url" :src="data.article.cover_url" class="cover" alt="cover" />
      <div class="article-body" v-html="data.article.content_html"></div>
    </article>

    <section class="comment-panel">
      <h2>评论</h2>
      <form class="comment-form" @submit.prevent="submitComment">
        <input v-model="guestNickname" placeholder="匿名昵称（登录后可留空）" />
        <input v-model="guestEmail" placeholder="匿名邮箱（登录后可留空）" />
        <textarea v-model="commentContent" placeholder="写下你的看法"></textarea>
        <button type="submit">提交评论</button>
      </form>
      <div class="comment-list">
        <div v-for="comment in data.comments" :key="comment.id" class="comment-item">
          <strong>{{ comment.user?.nickname || comment.guest_nickname || '匿名访客' }}</strong>
          <span>{{ formatDate(comment.created_at) }}</span>
          <p>{{ comment.content }}</p>
        </div>
      </div>
    </section>

    <WebFooter :icp-beian="data.site.icp_beian" :copyright-text="data.site.copyright_text" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { toAbsoluteAssetUrl, webApi } from '../api'
import WebFooter from '../components/WebFooter.vue'
import WebTopbar from '../components/WebTopbar.vue'
import type { ArticlePageResponse } from '../types'

const route = useRoute()
const router = useRouter()
const data = ref<ArticlePageResponse | null>(null)
const commentContent = ref('')
const guestNickname = ref('')
const guestEmail = ref('')
const keyword = ref('')
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
  data.value = await webApi.getArticle(String(route.params.id))
  applySiteMeta(data.value.site.site_title, data.value.site.site_subtitle, data.value.site.site_logo)
}

const submitComment = async () => {
  if (!data.value || !commentContent.value.trim()) return
  await webApi.submitComment({
    article_id: data.value.article.id,
    content: commentContent.value,
    guest_nickname: guestNickname.value || null,
    guest_email: guestEmail.value || null,
  })
  commentContent.value = ''
  await loadData()
}

const formatDate = (value: string) => new Date(value).toLocaleString('zh-CN')

const formatRelativeTime = (value: string) => {
  const date = new Date(value)
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
    const hours = Math.max(1, Math.floor(diffMs / hour))
    return `${hours} 小时前`
  }
  if (diffMs < year) {
    const days = Math.max(1, Math.floor(diffMs / day))
    return `${days} 天前`
  }
  const years = Math.max(1, Math.floor(diffMs / year))
  return `${years} 年前`
}

onMounted(() => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  loadData()
})
</script>
