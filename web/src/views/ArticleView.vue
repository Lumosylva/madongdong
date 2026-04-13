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
      <div class="article-head">
        <p class="article-category">{{ data.article.category?.name || '未分类' }}</p>
        <h1>{{ data.article.title }}</h1>
        <div class="article-meta article-meta-top">
          <span>{{ data.article.author?.nickname || 'admin' }}</span>
          <span>{{ formatRelativeTime(data.article.published_at || data.article.created_at) }}</span>
          <span>{{ data.article.view_count }} 浏览</span>
          <span>{{ data.article.comment_count }} 评论</span>
        </div>
      </div>
      <p class="article-summary">{{ data.article.summary }}</p>
      <img v-if="data.article.cover_url" :src="data.article.cover_url" class="cover" alt="cover" />
      <div class="article-body" v-html="data.article.content_html"></div>
    </article>

    <section class="comment-panel">
      <div class="comment-head">
        <h2>评论</h2>
        <span class="comment-count">共 {{ data.comments.length }} 条</span>
      </div>

      <form class="comment-form" @submit.prevent="submitComment">
        <div class="comment-inputs-row">
          <input v-model="guestNickname" placeholder="匿名昵称（登录后可留空）" />
          <input v-model="guestEmail" placeholder="匿名邮箱（登录后可留空）" />
        </div>
        <textarea v-model="commentContent" placeholder="写下你的看法（支持友好交流）"></textarea>
        <div class="comment-actions">
          <span class="comment-tip">提交后将按站点设置进行审核或直接展示</span>
          <button type="submit">提交评论</button>
        </div>
      </form>

      <p v-if="commentToastMessage" class="comment-toast" :class="commentToastStatus === 'error' ? 'error' : 'success'">
        {{ commentToastMessage }}
      </p>

      <div class="comment-list" ref="commentListRef">
        <div
          v-for="comment in data.comments"
          :key="comment.id"
          class="comment-item"
          :class="{ 'comment-item-new': highlightedCommentId === comment.id }"
        >
          <div class="comment-item-head">
            <strong>{{ comment.user?.nickname || comment.guest_nickname || '匿名访客' }}</strong>
            <span>{{ formatRelativeTime(comment.created_at) }}</span>
          </div>
          <p>{{ comment.content }}</p>
        </div>
      </div>
    </section>

    <WebFooter :icp-beian="data.site.icp_beian" :copyright-text="data.site.copyright_text" />
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
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
const commentListRef = ref<HTMLElement | null>(null)
const highlightedCommentId = ref<number | null>(null)
const commentToastMessage = ref('')
const commentToastStatus = ref<'success' | 'error' | ''>('')
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

  try {
    await webApi.submitComment({
      article_id: data.value.article.id,
      content: commentContent.value,
      guest_nickname: guestNickname.value || null,
      guest_email: guestEmail.value || null,
    })

    commentToastStatus.value = 'success'
    commentToastMessage.value = '评论提交成功'
    const previousMaxCommentId = Math.max(0, ...(data.value.comments.map((item) => item.id) || [0]))

    commentContent.value = ''
    guestNickname.value = ''
    guestEmail.value = ''
    await loadData()

    const latest = data.value?.comments.find((item) => item.id > previousMaxCommentId) || data.value?.comments[0]
    if (latest) {
      highlightedCommentId.value = latest.id
      await nextTick()
      const target = commentListRef.value?.querySelector(`[data-comment-id="${latest.id}"]`)
      if (target instanceof HTMLElement) {
        target.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
      setTimeout(() => {
        highlightedCommentId.value = null
      }, 2000)
    }
  } catch (error) {
    commentToastStatus.value = 'error'
    commentToastMessage.value = error instanceof Error ? error.message : '评论提交失败，请稍后重试'
  } finally {
    setTimeout(() => {
      commentToastMessage.value = ''
      commentToastStatus.value = ''
    }, 2200)
  }
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
