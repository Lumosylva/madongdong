<template>
  <div class="article-page" v-if="data" ref="articlePageRef">
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
            {{ t('article.currentLocation') }}
            <RouterLink to="/" class="breadcrumb-link">{{ t('common.home') }}</RouterLink>
            <span class="breadcrumb-sep">/</span>
            <RouterLink
              v-if="data.article.category?.slug"
              :to="`/category/${encodeURIComponent(data.article.category.slug)}`"
              class="breadcrumb-link"
            >
              {{ data.article.category.name }}
            </RouterLink>
            <span v-else>{{ t('common.untitled') }}</span>
            <span class="breadcrumb-sep">/</span>
            <span>{{ t('article.content') }}</span>
          </p>
        </div>
        <div class="article-head-divider"></div>
        <div class="article-head-row">
          <h1>{{ data.article.title }}</h1>
        </div>
        <div class="article-meta article-meta-top">
          <span>{{ data.article.author?.nickname || 'admin' }}</span>
          <span>{{ data.article.category?.name || t('common.untitled') }}</span>
          <span>{{ t('time.publishedAt') }}{{ formatRelativeTime(data.article.published_at || data.article.created_at) }}</span>
          <span>{{ t('time.updatedAt') }}{{ formatRelativeTime(getArticleUpdatedAt(data.article)) }}</span>
          <span>{{ t('article.readingTime', { n: estimatedReadingTime }) }}</span>
          <span>{{ data.article.view_count }} {{ t('common.views') }}</span>
          <span>{{ data.article.comment_count }} {{ t('common.comments') }}</span>
        </div>
        <div class="article-share-row">
          <button type="button" class="share-btn" @click="shareToTwitter" :aria-label="t('article.shareToTwitter')">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
          </button>
          <button type="button" class="share-btn" @click="shareToWeibo" :aria-label="t('article.shareToWeibo')">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M10.098 20.323c-3.977.391-7.414-1.406-7.672-4.02-.259-2.609 2.759-5.047 6.74-5.441 3.979-.394 7.413 1.404 7.671 4.018.259 2.6-2.759 5.049-6.737 5.439l-.002.004zM17.2 6.955c-.266-.749-.935-1.16-1.493-.921-.559.239-.793.976-.527 1.725l.003.007c.263.749.93 1.162 1.49.924.559-.239.796-.978.527-1.735zM20.75 7.7c-.759-2.159-2.691-3.332-4.325-2.611-1.637.725-2.365 2.761-1.606 4.922.759 2.16 2.689 3.33 4.327 2.608 1.634-.723 2.363-2.758 1.604-4.919z"/></svg>
          </button>
          <button type="button" class="share-btn" @click="copyArticleLink" :aria-label="t('article.copyLink')">
            <svg v-if="!linkCopied" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
            <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
          </button>
        </div>
      </div>
      <img v-if="data.article.cover_url" :src="data.article.cover_url" class="cover" alt="cover" decoding="async" />
      <div class="article-content-wrap">
        <div class="article-body article-body-md">
          <MdPreview
            :key="`${articleEditorId}-${theme}`"
            :id="articleEditorId"
            :model-value="data.article.content_markdown || ''"
            :theme="theme"
            code-theme="github"
            :show-code-row-number="true"
            :sanitize="sanitizeMarkdownHtml"
            :markdown-it-config="previewMarkdownItConfig"
          />
        </div>
      </div>

      <section class="article-extra">
        <div class="article-tags">
          <div class="article-tags-head">
            <button v-if="hasMoreTags" type="button" class="tag-expand-btn" @click="showAllTags = !showAllTags">
              <span class="tag-expand-icon" :class="{ rotated: showAllTags }">▾</span>
              {{ showAllTags ? t('article.collapseTags') : t('article.expandTags') }}
            </button>
          </div>
          <div class="tag-list" :class="{ collapsed: hasMoreTags && !showAllTags }">
            <span v-if="!data.article.tags?.length" class="tag-item muted">{{ t('article.noTags') }}</span>
            <span v-else class="tag-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" class="tag-icon-svg" focusable="false" aria-hidden="true">
                <path d="M3 11.5V5.75A2.75 2.75 0 0 1 5.75 3H11.5c.73 0 1.42.29 1.94.81l7.75 7.75a2.75 2.75 0 0 1 0 3.89l-5.5 5.5a2.75 2.75 0 0 1-3.89 0L3.81 13.44A2.75 2.75 0 0 1 3 11.5Zm3.75-5.75a1 1 0 1 0 0 2 1 1 0 0 0 0-2Z" />
              </svg>
            </span>
            <RouterLink
              v-for="tag in visibleTags"
              :key="tag.id"
              :to="`/tag/${encodeURIComponent(tag.slug)}`"
              class="tag-item"
            >
              {{ tag.name }}
            </RouterLink>
          </div>
        </div>

        <div class="article-nav-links">
          <div class="nav-row">
            <span class="meta-label">{{ t('article.prevArticle') }}</span>
            <RouterLink v-if="data.previous_article" :to="`/article/details/${data.previous_article.id}`" class="adjacent-link">
              {{ truncateText(data.previous_article.title, 50) }}
            </RouterLink>
            <span v-else class="adjacent-empty">{{ t('article.noMore') }}</span>
          </div>

          <div class="nav-row">
            <span class="meta-label">{{ t('article.nextArticle') }}</span>
            <RouterLink v-if="data.next_article" :to="`/article/details/${data.next_article.id}`" class="adjacent-link">
              {{ truncateText(data.next_article.title, 50) }}
            </RouterLink>
            <span v-else class="adjacent-empty">{{ t('article.noMore') }}</span>
          </div>
        </div>
      </section>
    </article>

    <section class="comment-panel" id="comment-section">
      <div class="comment-head">
        <h2>{{ t('article.comments') }}</h2>
        <span class="comment-count">{{ t('article.commentCount', { n: data.comments.length }) }}</span>
      </div>

      <form class="comment-form" @submit.prevent="submitComment">
        <div class="comment-inputs-row" :class="{ 'auto-filled': isLoggedIn }">
          <label for="comment-nickname" class="comment-field-wrap">
            <span v-if="isLoggedIn" class="comment-field-badge">{{ t('article.autoFilled') }}</span>
            <input id="comment-nickname" ref="nicknameInputRef" v-model="guestNickname" autocomplete="name" :placeholder="t('article.nicknamePlaceholder')" :readonly="isLoggedIn" />
          </label>
          <label for="comment-email" class="comment-field-wrap">
            <span v-if="isLoggedIn" class="comment-field-badge">{{ t('article.autoFilled') }}</span>
            <input id="comment-email" ref="emailInputRef" v-model="guestEmail" type="email" autocomplete="email" :placeholder="t('article.emailPlaceholder')" :readonly="isLoggedIn" />
          </label>
        </div>
        <label for="comment-content" class="sr-only">{{ t('article.commentPlaceholder') }}</label>
        <textarea
          id="comment-content"
          ref="commentTextareaRef"
          v-model="commentContent"
          :placeholder="t('article.commentPlaceholder')"
          @focus="commentFieldFocused = true"
          @blur="commentFieldFocused = false"
        ></textarea>
        <div class="comment-actions">
          <span class="comment-tip">{{ t('article.commentTip') }}</span>
          <button type="submit" :disabled="commentSubmitting || !commentContent.trim()" :aria-label="t('article.submitComment')">
            {{ commentSubmitting ? t('article.submitting') : (!commentContent.trim() ? t('article.inputContent') : t('article.submitComment')) }}
          </button>
        </div>
      </form>

      <p
        v-if="commentToastMessage"
        class="comment-toast"
        :class="commentToastStatus === 'error' ? 'error' : (commentToastStatus === 'warning' ? 'warning' : 'success')"
        role="status"
        aria-live="polite"
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
          <div class="comment-avatar">
            <img v-if="comment.user?.avatar" :src="comment.user.avatar" :alt="comment.user?.nickname" class="comment-avatar-img" loading="lazy" decoding="async" />
            <div v-else class="comment-avatar-fallback" :style="{ background: avatarColor(comment.user?.nickname || comment.guest_nickname || t('article.anonymousShort')) }">
              {{ avatarLetter(comment.user?.nickname || comment.guest_nickname || t('article.anonymousShort')) }}
            </div>
          </div>
          <div class="comment-body">
            <div class="comment-item-head">
              <strong>{{ comment.user?.nickname || comment.guest_nickname || t('article.anonymousVisitor') }}</strong>
              <span v-if="getClientMetaText(comment)" class="comment-client-meta-inline">{{ getClientMetaText(comment) }}</span>
              <span class="comment-time">{{ formatRelativeTime(comment.created_at) }}</span>
            </div>
            <p>{{ comment.content }}</p>
          </div>
        </div>
      </div>
    </section>

    <WebFooter :icp-beian="data.site.icp_beian" :police-beian="data.site.police_beian" :copyright-text="data.site.copyright_text" />
  </div>
  <div v-else class="article-page skeleton-page">
    <div class="skeleton-card">
      <div class="skeleton skeleton-title"></div>
      <div class="skeleton skeleton-line w-80"></div>
      <div class="skeleton skeleton-line w-60"></div>
    </div>
    <div class="skeleton-card">
      <div class="skeleton skeleton-line w-100"></div>
      <div class="skeleton skeleton-line w-100"></div>
      <div class="skeleton skeleton-line w-80"></div>
      <div class="skeleton skeleton-line w-60"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'
import DOMPurify from 'dompurify'
import { useI18n } from 'vue-i18n'

import { toAbsoluteAssetUrl, webApi } from '../api'
import WebFooter from '../components/WebFooter.vue'
import WebTopbar from '../components/WebTopbar.vue'
import { useTheme } from '../composables/useTheme'
import { applyArticleMeta, applySiteMetaFromSetting, setSiteSetting } from '../site-meta'
import { useFormatRelativeTime, getArticleUpdatedAt } from '../utils/time'
import { truncateText } from '../utils/text'
import type { ArticlePageResponse, Comment } from '../types'

const { t } = useI18n()
const { formatRelativeTime } = useFormatRelativeTime()
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
const { theme, toggleTheme, initTheme, listenThemeChange, destroyTheme } = useTheme()
const isLoggedIn = ref(false)
const showAllTags = ref(false)
const articleEditorId = 'web-article-preview'

const sanitizeMarkdownHtml = (html: string) => DOMPurify.sanitize(html, {
  USE_PROFILES: { html: true },
  ADD_TAGS: ['video', 'iframe', 'source', 'audio'],
  ADD_ATTR: ['controls', 'preload', 'allow', 'allowfullscreen', 'frameborder', 'scrolling', 'type', 'width', 'height', 'marginwidth', 'marginheight'],
})

const previewMarkdownItConfig = (md: any) => {
  md.options.html = true
}

const syncTopbarOffset = () => {
  const topbar = document.querySelector('.topbar') as HTMLElement | null
  if (!topbar || !articlePageRef.value) return
  const topbarRect = topbar.getBoundingClientRect()
  const pageRect = articlePageRef.value.getBoundingClientRect()
  const offset = Math.max(0, Math.round(topbarRect.height - Math.max(0, pageRect.top)))
  document.documentElement.style.setProperty('--web-topbar-offset', `${topbarRect.height}px`)
  document.documentElement.style.setProperty('--article-page-top-offset', `${offset}px`)
}

const topbarResizeObserver = ref<ResizeObserver | null>(null)
const articlePageRef = ref<HTMLElement | null>(null)

const hasMoreTags = computed(() => (data.value?.article.tags?.length || 0) > 6)
const visibleTags = computed(() => {
  const tags = data.value?.article.tags || []
  if (showAllTags.value || tags.length <= 6) return tags
  return tags.slice(0, 6)
})

const estimatedReadingTime = computed(() => {
  const content = data.value?.article.content_markdown || ''
  const wordCount = content.length
  const minutes = Math.max(1, Math.ceil(wordCount / 500))
  return minutes
})

const linkCopied = ref(false)

const shareToTwitter = () => {
  if (!data.value) return
  const url = window.location.href
  const text = encodeURIComponent(data.value.article.title)
  window.open(`https://twitter.com/intent/tweet?text=${text}&url=${encodeURIComponent(url)}`, '_blank', 'noopener,noreferrer')
}

const shareToWeibo = () => {
  if (!data.value) return
  const url = encodeURIComponent(window.location.href)
  const title = encodeURIComponent(data.value.article.title)
  window.open(`https://service.weibo.com/share/share.php?url=${url}&title=${title}`, '_blank', 'noopener,noreferrer')
}

const copyArticleLink = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href)
    linkCopied.value = true
    setTimeout(() => { linkCopied.value = false }, 2000)
  } catch {
    // fallback
  }
}

const goSearch = () => {
  if (!keyword.value.trim()) return
  router.push(`/search?keyword=${encodeURIComponent(keyword.value.trim())}`)
}



const loadData = async () => {
  const articleId = Number(route.params.id)
  if (!articleId) return
  data.value = await webApi.getArticle(articleId)
  setSiteSetting(data.value.site)
  applySiteMetaFromSetting(data.value.site)
  applyArticleMeta(data.value.article.title, data.value.article.summary, data.value.article.cover_url)
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
    commentToastMessage.value = createdStatus === 'APPROVED' ? t('article.commentPublished') : t('article.commentPending')
    const previousMaxCommentId = Math.max(0, ...(data.value.comments.map((item) => item.id) || [0]))

    localStorage.setItem('md-reader-nickname', guestNickname.value.trim())
    localStorage.setItem('md-reader-email', guestEmail.value.trim())
    await loadData()
    commentContent.value = ''

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
    commentToastMessage.value = error instanceof Error ? error.message : t('article.commentFailed')
  } finally {
    setTimeout(() => {
      commentToastMessage.value = ''
      commentToastStatus.value = ''
    }, 2200)
  }
}

const getClientMetaText = (comment: Comment) => {
  const browser = [comment.client_browser, comment.client_browser_version].filter(Boolean).join(' ').trim()
  const os = [comment.client_os, comment.client_os_version].filter(Boolean).join(' ').trim()
  const parts = [browser ? `🌐 ${browser}` : '', os ? `🖥️ ${os}` : ''].filter(Boolean)
  return parts.join(' ')
}

const AVATAR_COLORS = [
  '#0ea5a4', '#3b82f6', '#8b5cf6', '#ec4899', '#f97316',
  '#14b8a6', '#6366f1', '#a855f7', '#e11d48', '#f59e0b',
  '#06b6d4', '#8b5cf6', '#d946ef', '#ef4444', '#eab308',
]

const hashCode = (str: string) => {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash + str.charCodeAt(i)) | 0
  }
  return Math.abs(hash)
}

const avatarLetter = (name: string) => {
  const s = String(name || '').trim()
  if (!s) return '?'
  const ch = s[0]
  if (ch === '#' || ch === '/') return s.length > 1 ? s[1].toUpperCase() : '?'
  return ch.toUpperCase()
}

const avatarColor = (name: string) => AVATAR_COLORS[hashCode(String(name || '')) % AVATAR_COLORS.length]

watch(() => route.params.id, () => {
  loadData()
  window.scrollTo({ top: 0, behavior: 'smooth' })
})

onMounted(async () => {
  initTheme()
  listenThemeChange()

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
  syncTopbarOffset()
  topbarResizeObserver.value = new ResizeObserver(() => syncTopbarOffset())
  const topbar = document.querySelector('.topbar')
  if (topbar) topbarResizeObserver.value.observe(topbar)
})

onBeforeUnmount(() => {
  topbarResizeObserver.value?.disconnect()
  destroyTheme()
})
</script>

<style scoped>
.article-share-row {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.share-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--bg-soft);
  color: var(--text-soft);
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: color 0.18s ease, border-color 0.18s ease, background 0.18s ease;
}

.share-btn:hover {
  color: var(--accent);
  border-color: rgba(14, 165, 164, 0.3);
  background: rgba(14, 165, 164, 0.06);
}

:root[data-theme='dark'] .share-btn {
  background: rgba(25, 48, 76, 0.5);
}
</style>
