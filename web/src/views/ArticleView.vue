<template>
  <div class="article-page" v-if="data" ref="articlePageRef">
    <ArticleToc :content="data.article.content_markdown || ''" />
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
          <span>{{ likeCount }} {{ t('article.like') }}</span>
        </div>
        <div class="article-share-row">
          <button type="button" class="share-btn" @click="showSharePanel" :aria-label="t('article.qrShareTitle')">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
          </button>
          <button type="button" class="share-btn" @click="copyArticleLink" :aria-label="t('article.copyLink')">
            <svg v-if="!linkCopied" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
            <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
          </button>
        </div>

        <teleport to="body">
          <transition name="qr-modal-fade">
            <div v-if="qrModalVisible" class="qr-modal-mask" @click="qrModalVisible = false">
              <div class="qr-modal" @click.stop>
                <div class="qr-modal-header">
                  <span class="qr-modal-title">{{ t('article.qrShareTitle') }}</span>
                  <button type="button" class="qr-modal-close" :aria-label="t('common.close')" @click="qrModalVisible = false">✕</button>
                </div>
                <div class="qr-modal-body">
                  <div class="qr-code" ref="qrCodeRef"></div>
                  <p class="qr-modal-hint">{{ t('article.scanToShare') }}</p>
                  <div class="share-platform-row">
                    <button type="button" class="share-platform-btn" @click="shareToWeibo">
                      <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M10.098 20.323c-3.977.391-7.414-1.406-7.672-4.02-.259-2.609 2.759-5.047 6.74-5.441 3.979-.394 7.413 1.404 7.671 4.018.259 2.6-2.759 5.049-6.737 5.439l-.002.004zM17.2 6.955c-.266-.749-.935-1.16-1.493-.921-.559.239-.793.976-.527 1.725l.003.007c.263.749.93 1.162 1.49.924.559-.239.796-.978.527-1.735zM20.75 7.7c-.759-2.159-2.691-3.332-4.325-2.611-1.637.725-2.365 2.761-1.606 4.922.759 2.16 2.689 3.33 4.327 2.608 1.634-.723 2.363-2.758 1.604-4.919z"/></svg>
                      <span>微博</span>
                    </button>
                    <button type="button" class="share-platform-btn" @click="shareToQQ">
                      <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M21.395 15.035a39.548 39.548 0 0 0-1.103-2.804c.155-.636.233-1.253.233-1.85 0-3.878-2.963-6.581-6.395-6.581S7.735 6.503 7.735 10.381c0 .597.078 1.214.233 1.85a39.548 39.548 0 0 0-1.103 2.804c-.23.663-.396 1.358-.447 2.002-.014.172-.021.346-.021.516 0 2.68 2.268 4.851 5.067 4.851.89 0 1.755-.22 2.485-.621a4.23 4.23 0 0 0 1.521.621c.527 0 1.045-.135 1.522-.621.73.401 1.594.621 2.485.621 2.799 0 5.067-2.171 5.067-4.851 0-.17-.007-.344-.021-.516-.051-.644-.217-1.339-.447-2.002ZM8.935 10.756a1.072 1.072 0 1 1 0-2.144 1.072 1.072 0 0 1 0 2.144Zm6.13 0a1.072 1.072 0 1 1 0-2.144 1.072 1.072 0 0 1 0 2.144Z"/></svg>
                      <span>QQ</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </transition>
        </teleport>
      </div>
      <div v-if="articleCoverUrl" class="cover-wrap">
        <img
          v-if="!coverError"
          :src="articleCoverUrl"
          class="cover cover-full"
          :class="{ loaded: coverLoaded }"
          :alt="data.article.title"
          decoding="async"
          loading="eager"
          @load="onCoverLoad"
          @error="onCoverError"
        />
        <div v-if="!coverError" class="cover-blur" :class="{ loaded: coverLoaded }" :style="{ backgroundImage: `url(${articleCoverUrl})` }"></div>
        <div v-else class="cover-fallback" role="img" :aria-label="t('article.coverLoadFailed')">
          {{ t('article.coverLoadFailed') }}
        </div>
      </div>
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
            <RouterLink v-if="data.previous_article" :to="articlePath(data.previous_article)" class="adjacent-link">
              {{ truncateText(data.previous_article.title, 50) }}
            </RouterLink>
            <span v-else class="adjacent-empty">{{ t('article.noMore') }}</span>
          </div>

          <div class="nav-row">
            <span class="meta-label">{{ t('article.nextArticle') }}</span>
            <RouterLink v-if="data.next_article" :to="articlePath(data.next_article)" class="adjacent-link">
              {{ truncateText(data.next_article.title, 50) }}
            </RouterLink>
            <span v-else class="adjacent-empty">{{ t('article.noMore') }}</span>
          </div>
        </div>
      </section>
    </article>

    <div class="article-like-row">
      <button
        type="button"
        class="like-btn"
        :class="{ liked: isLiked }"
        @click="toggleLike"
        :disabled="likeLoading"
        :aria-label="t('article.like')"
      >
        <svg class="like-icon" viewBox="0 0 24 24" aria-hidden="true">
          <path v-if="!isLiked" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" fill="none" stroke="currentColor" stroke-width="2"/>
          <path v-else d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" fill="currentColor"/>
        </svg>
        <span class="like-count">{{ formatLikeCount(likeCount) }}</span>
      </button>
    </div>

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
            <img v-if="comment.user?.avatar" :src="assetUrl(comment.user.avatar)" :alt="comment.user?.nickname" class="comment-avatar-img" loading="lazy" decoding="async" />
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
import QRCode from 'qrcode'
import { useI18n } from 'vue-i18n'

import { toAbsoluteAssetUrl, webApi } from '../api'
import ArticleToc from '../components/ArticleToc.vue'
import WebFooter from '../components/WebFooter.vue'
import WebTopbar from '../components/WebTopbar.vue'
import { useTheme } from '../composables/useTheme'
import { applyArticleJsonLd, applyArticleMeta, applySiteMetaFromSetting, setSiteSetting } from '../site-meta'
import { articlePath } from '../utils/articleLink'
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
const isLiked = ref(false)
const likeCount = ref(0)
const likeLoading = ref(false)
const coverLoaded = ref(false)
const coverError = ref(false)
const articleCoverUrl = computed(() => toAbsoluteAssetUrl(data.value?.article.cover_url))

const onCoverLoad = () => { coverLoaded.value = true }
const onCoverError = () => {
  coverLoaded.value = false
  coverError.value = true
}

const assetUrl = (url: string | null | undefined) => toAbsoluteAssetUrl(url)

let imageObserver: MutationObserver | null = null

const observeArticleImages = () => {
  imageObserver?.disconnect()
  const body = document.querySelector('.article-body-md')
  if (!body) return

  const addLazyAttrs = (img: HTMLImageElement) => {
    if (img.hasAttribute('data-optimized')) return
    img.setAttribute('data-optimized', '1')
    img.loading = 'lazy'
    img.decoding = 'async'

    const src = img.getAttribute('src') || ''
    if (!src || src.startsWith('data:')) return

    img.classList.add('article-img-loading')
    const onLoad = () => {
      img.classList.remove('article-img-loading')
      img.classList.add('article-img-loaded')
      img.removeEventListener('load', onLoad)
      img.removeEventListener('error', onError)
    }
    const onError = () => {
      img.classList.remove('article-img-loading')
      img.classList.add('article-img-failed')
      img.removeEventListener('load', onLoad)
      img.removeEventListener('error', onError)
    }
    if (img.complete) {
      if (img.naturalWidth > 0) onLoad()
      else onError()
    } else {
      img.addEventListener('load', onLoad)
      img.addEventListener('error', onError)
    }
  }

  body.querySelectorAll('img').forEach(addLazyAttrs)

  imageObserver = new MutationObserver((mutations) => {
    for (const m of mutations) {
      for (const node of m.addedNodes) {
        if (node instanceof HTMLImageElement) addLazyAttrs(node)
        if (node instanceof HTMLElement) node.querySelectorAll('img').forEach(addLazyAttrs)
      }
    }
  })
  imageObserver.observe(body, { childList: true, subtree: true })
}

const LIKE_STORAGE_KEY = 'md-liked-articles'

const loadLikeState = () => {
  if (!data.value) return
  const liked = JSON.parse(localStorage.getItem(LIKE_STORAGE_KEY) || '{}')
  isLiked.value = !!liked[data.value.article.id]
  likeCount.value = data.value.article.like_count
}

const formatLikeCount = (n: number) => {
  if (n >= 10000) return `${(n / 10000).toFixed(1)}w`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
  return String(n)
}

const toggleLike = async () => {
  if (!data.value || likeLoading.value) return
  likeLoading.value = true
  try {
    const res = await webApi.likeArticle(data.value.article.id)
    isLiked.value = res.liked
    likeCount.value = res.like_count
    const liked = JSON.parse(localStorage.getItem(LIKE_STORAGE_KEY) || '{}')
    if (res.liked) {
      liked[data.value.article.id] = true
    } else {
      delete liked[data.value.article.id]
    }
    localStorage.setItem(LIKE_STORAGE_KEY, JSON.stringify(liked))
  } catch {
    // ignore
  } finally {
    likeLoading.value = false
  }
}

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
const qrModalVisible = ref(false)
const qrCodeRef = ref<HTMLElement | null>(null)

const showSharePanel = async () => {
  qrModalVisible.value = true
  const url = window.location.href
  try {
    const svg = await QRCode.toString(url, {
      type: 'svg',
      width: 180,
      margin: 1,
      color: { dark: '#000000', light: '#ffffff' },
    })
    await nextTick()
    if (qrCodeRef.value) {
      qrCodeRef.value.innerHTML = svg
    }
  } catch {
    // ignore
  }
}

const shareToWeibo = () => {
  if (!data.value) return
  const url = encodeURIComponent(window.location.href)
  const title = encodeURIComponent(data.value.article.title)
  window.open(`https://service.weibo.com/share/share.php?url=${url}&title=${title}`, '_blank', 'noopener,noreferrer')
}

const shareToQQ = () => {
  if (!data.value) return
  const url = encodeURIComponent(window.location.href)
  const title = encodeURIComponent(data.value.article.title)
  const desc = encodeURIComponent(data.value.article.summary)
  window.open(`https://connect.qq.com/widget/shareqq/index.html?url=${url}&title=${title}&desc=${desc}`, '_blank', 'noopener,noreferrer')
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
  const articleSlug = String(route.params.slug || '').trim()
  if (!articleId && !articleSlug) return
  coverLoaded.value = false
  coverError.value = false
  data.value = articleSlug
    ? await webApi.getArticleBySlug(articleSlug)
    : await webApi.getArticle(articleId)
  if (!articleSlug) {
    const canonicalPath = articlePath(data.value.article)
    if (canonicalPath !== route.fullPath) {
      await router.replace(canonicalPath)
    }
  }
  loadLikeState()
  setSiteSetting(data.value.site)
  applySiteMetaFromSetting(data.value.site)
  applyArticleMeta(data.value.article.title, data.value.article.summary, data.value.article.cover_url, {
    id: data.value.article.id,
    slug: data.value.article.slug,
    publishedAt: data.value.article.published_at,
    updatedAt: data.value.article.updated_at || data.value.article.created_at,
    author: data.value.article.author?.nickname,
    category: data.value.article.category?.name,
    tags: data.value.article.tags?.map(t => t.name),
  })
  applyArticleJsonLd({
    title: data.value.article.title,
    description: data.value.article.summary || data.value.article.title,
    url: window.location.href,
    image: data.value.article.cover_url ? toAbsoluteAssetUrl(data.value.article.cover_url) : undefined,
    publishedAt: data.value.article.published_at || undefined,
    updatedAt: data.value.article.updated_at || data.value.article.created_at || undefined,
    author: data.value.article.author?.nickname || undefined,
    category: data.value.article.category?.name || undefined,
    tags: data.value.article.tags?.map(t => t.name),
  })
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

watch(() => [route.params.id, route.params.slug], () => {
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
  nextTick(observeArticleImages)
  syncTopbarOffset()
  topbarResizeObserver.value = new ResizeObserver(() => syncTopbarOffset())
  const topbar = document.querySelector('.topbar')
  if (topbar) topbarResizeObserver.value.observe(topbar)
})

onBeforeUnmount(() => {
  imageObserver?.disconnect()
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

.qr-modal-mask {
  position: fixed;
  inset: 0;
  z-index: 9000;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: grid;
  place-items: center;
  padding: 20px;
}

.qr-modal {
  background: var(--bg-panel);
  border-radius: 18px;
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
  width: min(340px, 90vw);
  overflow: hidden;
}

.qr-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--line);
}

.qr-modal-title {
  font-size: 15px;
  font-weight: 700;
}

.qr-modal-close {
  width: 28px;
  height: 28px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--bg-soft);
  color: var(--text);
  cursor: pointer;
  display: grid;
  place-items: center;
  font-size: 12px;
}

.qr-modal-body {
  padding: 24px 20px;
  display: grid;
  justify-items: center;
  gap: 12px;
}

.qr-code {
  width: 180px;
  height: 180px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  border: 1px solid var(--line);
  background: #fff;
  overflow: hidden;
}

.qr-code svg {
  width: 100%;
  height: 100%;
}

.qr-modal-hint {
  margin: 0;
  color: var(--text-soft);
  font-size: 13px;
  text-align: center;
}

.share-platform-row {
  display: flex;
  gap: 12px;
  justify-content: center;
  padding-top: 8px;
  border-top: 1px solid var(--line);
  width: 100%;
}

.share-platform-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--bg-soft);
  color: var(--text);
  font-size: 13px;
  cursor: pointer;
  transition: border-color 0.18s ease, background 0.18s ease;
}

.share-platform-btn:hover {
  border-color: rgba(14, 165, 164, 0.3);
  background: rgba(14, 165, 164, 0.06);
  color: var(--accent);
}

.qr-modal-fade-enter-active,
.qr-modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.qr-modal-fade-enter-from,
.qr-modal-fade-leave-to {
  opacity: 0;
}

.article-like-row {
  display: flex;
  justify-content: center;
  padding: 20px 0 8px;
}

.like-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--bg-panel);
  color: var(--text-soft);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.2s ease, border-color 0.2s ease, background 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.like-btn:hover:not(:disabled) {
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.06);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.1);
}

.like-btn.liked {
  color: var(--text-soft);
  border-color: var(--line);
  background: var(--bg-soft);
}

.like-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.like-icon {
  width: 20px;
  height: 20px;
  display: block;
  flex-shrink: 0;
}

.like-count {
  min-width: 1.2em;
  text-align: center;
}
</style>
