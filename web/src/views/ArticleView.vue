<template>
  <div class="article-page" v-if="data">
    <WebTopbar
      :title="data.site.site_title"
      :subtitle="data.site.site_subtitle || ''"
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
        <div class="article-breadcrumb-row">
          <p class="article-breadcrumb">
            现在位置：
            <RouterLink to="/" class="breadcrumb-link">首页</RouterLink>
            <span class="breadcrumb-sep">/</span>
            <RouterLink
              v-if="data.article.category?.slug"
              :to="`/category/${encodeURIComponent(data.article.category.slug)}`"
              class="breadcrumb-link"
            >
              {{ data.article.category.name }}
            </RouterLink>
            <span v-else>未分类</span>
            <span class="breadcrumb-sep">/</span>
            <span>正文</span>
          </p>
        </div>
        <div class="article-head-divider"></div>
        <div class="article-head-row">
          <h1>{{ data.article.title }}</h1>
        </div>
        <div class="article-meta article-meta-top">
          <span>{{ data.article.author?.nickname || 'admin' }}</span>
          <span>{{ data.article.category?.name || '未分类' }}</span>
          <span>{{ formatRelativeTime(data.article.published_at || data.article.created_at) }}</span>
          <span>{{ data.article.view_count }} 浏览</span>
          <span>{{ data.article.comment_count }} 评论</span>
        </div>
      </div>
      <img v-if="data.article.cover_url" :src="data.article.cover_url" class="cover" alt="cover" />
      <div class="article-body article-body-md">
        <MdPreview
          :model-value="data.article.content_markdown || ''"
          :theme="theme"
          preview-theme="github"
          :editor-id="articleEditorId"
        />
      </div>

      <section class="article-extra">
        <div class="article-tags">
          <div class="article-tags-head">
            <span class="meta-label">标签</span>
            <button v-if="hasMoreTags" type="button" class="tag-expand-btn" @click="showAllTags = !showAllTags">
              <span class="tag-expand-icon" :class="{ rotated: showAllTags }">▾</span>
              {{ showAllTags ? '收起标签' : '展开更多标签' }}
            </button>
          </div>
          <div class="tag-list" :class="{ collapsed: hasMoreTags && !showAllTags }">
            <span v-if="!data.article.tags?.length" class="tag-item muted">无标签</span>
            <RouterLink
              v-for="tag in visibleTags"
              :key="tag.id"
              :to="`/tag/${encodeURIComponent(tag.slug)}`"
              class="tag-item"
            >
              # {{ tag.name }}
            </RouterLink>
          </div>
        </div>

        <div class="article-nav-links">
          <div class="nav-row">
            <span class="meta-label">上一篇</span>
            <RouterLink v-if="data.previous_article" :to="`/article/${data.previous_article.id}`" class="adjacent-link">
              {{ truncateText(data.previous_article.title, 50) }}
            </RouterLink>
            <span v-else class="adjacent-empty">没有了</span>
          </div>

          <div class="nav-row">
            <span class="meta-label">下一篇</span>
            <RouterLink v-if="data.next_article" :to="`/article/${data.next_article.id}`" class="adjacent-link">
              {{ truncateText(data.next_article.title, 50) }}
            </RouterLink>
            <span v-else class="adjacent-empty">没有了</span>
          </div>
        </div>
      </section>
    </article>

    <section class="comment-panel" id="comment-section">
      <div class="comment-head">
        <h2>评论</h2>
        <span class="comment-count">共 {{ data.comments.length }} 条</span>
      </div>

      <form class="comment-form" @submit.prevent="submitComment">
        <div class="comment-inputs-row" :class="{ 'auto-filled': isLoggedIn }">
          <label class="comment-field-wrap">
            <span v-if="isLoggedIn" class="comment-field-badge">已自动填充</span>
            <input ref="nicknameInputRef" v-model="guestNickname" placeholder="昵称（登录后可自动填充）" :readonly="isLoggedIn" />
          </label>
          <label class="comment-field-wrap">
            <span v-if="isLoggedIn" class="comment-field-badge">已自动填充</span>
            <input ref="emailInputRef" v-model="guestEmail" placeholder="邮箱（登录后可自动填充）" :readonly="isLoggedIn" />
          </label>
        </div>
        <textarea
          ref="commentTextareaRef"
          v-model="commentContent"
          placeholder="写下你的看法（支持友好交流）"
          @focus="commentFieldFocused = true"
          @blur="commentFieldFocused = false"
        ></textarea>
        <div class="comment-actions">
          <span class="comment-tip">提交后将按站点设置进行审核或直接展示</span>
          <button type="submit" :disabled="commentSubmitting || !commentContent.trim()">
            {{ commentSubmitting ? '提交中...' : (!commentContent.trim() ? '请输入评论内容' : '提交评论') }}
          </button>
        </div>
      </form>

      <p
        v-if="commentToastMessage"
        class="comment-toast"
        :class="commentToastStatus === 'error' ? 'error' : (commentToastStatus === 'warning' ? 'warning' : 'success')"
      >
        {{ commentToastMessage }}
      </p>

      <div class="comment-list" ref="commentListRef">
        <div
          v-for="comment in data.comments"
          :key="comment.id"
          class="comment-item"
          :class="{ 'comment-item-new': highlightedCommentId === comment.id }"
          :data-comment-id="comment.id"
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
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MdPreview } from 'md-editor-v3'

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
const commentToastStatus = ref<'success' | 'warning' | 'error' | ''>('')
const commentSubmitting = ref(false)
const commentFieldFocused = ref(false)
type ThemeMode = 'light' | 'dark'
const theme = ref<ThemeMode>('light')
const isLoggedIn = ref(false)
const showAllTags = ref(false)
const articleEditorId = 'web-article-preview'

const applyTheme = (value: ThemeMode) => {
  theme.value = value
  document.documentElement.dataset.theme = value
  localStorage.setItem('md-theme', value)
}

const toggleTheme = () => {
  applyTheme(theme.value === 'light' ? 'dark' : 'light')
}

const nicknameInputRef = ref<HTMLInputElement | null>(null)
const emailInputRef = ref<HTMLInputElement | null>(null)
const commentTextareaRef = ref<HTMLTextAreaElement | null>(null)

const hasMoreTags = computed(() => (data.value?.article.tags?.length || 0) > 6)
const visibleTags = computed(() => {
  const tags = data.value?.article.tags || []
  if (showAllTags.value || tags.length <= 6) return tags
  return tags.slice(0, 6)
})

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

const hydrateCurrentUser = async () => {
  try {
    const currentUser = await webApi.getCurrentWebUser()
    if (currentUser?.nickname) guestNickname.value = currentUser.nickname
    if (currentUser?.email) guestEmail.value = currentUser.email
    isLoggedIn.value = true
  } catch {
    isLoggedIn.value = false
  }
}

const submitComment = async () => {
  if (!data.value || !commentContent.value.trim()) return

  try {
    const created = await webApi.submitComment({
      article_id: data.value.article.id,
      content: commentContent.value,
      guest_nickname: guestNickname.value || null,
      guest_email: guestEmail.value || null,
    }) as { status?: string }

    const createdStatus = String(created?.status || '').toUpperCase()
    commentToastStatus.value = createdStatus === 'APPROVED' ? 'success' : 'warning'
    commentToastMessage.value = createdStatus === 'APPROVED' ? '评论已发布' : '评论已提交，待审核'
    const previousMaxCommentId = Math.max(0, ...(data.value.comments.map((item) => item.id) || [0]))

    commentContent.value = ''
    localStorage.setItem('md-reader-nickname', guestNickname.value.trim())
    localStorage.setItem('md-reader-email', guestEmail.value.trim())
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

watch(() => route.params.id, () => {
  loadData()
  window.scrollTo({ top: 0, behavior: 'smooth' })
})

onMounted(async () => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')

  const savedNickname = localStorage.getItem('md-reader-nickname')
  if (savedNickname && !guestNickname.value.trim()) {
    guestNickname.value = savedNickname
  }
  const savedEmail = localStorage.getItem('md-reader-email')
  if (savedEmail && !guestEmail.value.trim()) {
    guestEmail.value = savedEmail
  }

  await hydrateCurrentUser()
  await loadData()
})
</script>
