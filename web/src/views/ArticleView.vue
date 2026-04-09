<template>
  <div class="article-page">
    <!-- 错误提示 -->
    <div v-if="error" class="error-panel">
      <h3>加载失败</h3>
      <p>{{ error }}</p>
      <button @click="retryLoad" class="retry-btn">重试</button>
    </div>

    <!-- 加载骨架屏 -->
    <div v-else-if="loading" class="skeleton-container">
      <header class="mini-topbar skeleton">
        <div class="skeleton-line short"></div>
        <div class="skeleton-line medium"></div>
      </header>

      <article class="article-panel skeleton">
        <div class="skeleton-line short"></div>
        <div class="skeleton-line long"></div>
        <div class="skeleton-line medium"></div>
        <div class="skeleton-line medium"></div>
        <div class="skeleton-line medium"></div>
        <div class="skeleton-rectangle"></div>
        <div class="skeleton-line long"></div>
        <div class="skeleton-line long"></div>
        <div class="skeleton-line long"></div>
      </article>

      <section class="comment-panel skeleton">
        <div class="skeleton-line medium"></div>
        <div class="skeleton-line short"></div>
        <div class="skeleton-line long"></div>
        <div class="skeleton-line short"></div>
        <div class="skeleton-line long"></div>
      </section>
    </div>

    <!-- 正常内容 -->
    <div v-else-if="data">
      <header class="mini-topbar">
        <RouterLink to="/" class="back-link">← 返回首页</RouterLink>
        <div class="mini-nav">
          <a v-for="item in data.nav_items" :key="item.id" :href="item.path">{{ item.title }}</a>
        </div>
      </header>

      <article class="article-panel">
        <p class="article-category">{{ data.article.category.name }}</p>
        <h1>{{ data.article.title }}</h1>
        <div class="article-meta">
          <span>{{ data.article.author.nickname }}</span>
          <span>{{ formatDate(data.article.published_at || data.article.created_at) }}</span>
          <span>{{ data.article.view_count }} 阅读</span>
          <span>{{ data.article.comment_count }} 评论</span>
        </div>
        
        <!-- 文章操作栏 -->
        <div class="article-actions">
          <button @click="shareArticle" class="share-btn" title="分享文章">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="18" cy="5" r="3"></circle>
              <circle cx="6" cy="12" r="3"></circle>
              <circle cx="18" cy="19" r="3"></circle>
              <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
              <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
            </svg>
            分享
          </button>
        </div>
        
        <p class="article-summary">{{ data.article.summary }}</p>
        
        <!-- 文章目录 -->
        <div v-if="toc.length > 0" class="toc-panel">
          <h3>文章目录</h3>
          <ul class="toc-list">
            <li v-for="item in toc" :key="item.id" :class="`toc-level-${item.level}`">
              <a href="javascript:void(0)" @click.prevent="scrollToHeading(item.id)" :title="item.text">
                {{ item.text }}
              </a>
            </li>
          </ul>
        </div>
        
        <!-- 封面图片懒加载 -->
        <div v-if="data.article.cover_url" class="cover-container" ref="coverContainer">
          <!-- 加载中占位符 -->
          <div v-if="!coverLoaded && !coverError" class="cover-placeholder">
            <div class="cover-skeleton"></div>
          </div>
          <!-- 错误状态 -->
          <div v-if="coverError" class="cover-error">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            <p>图片加载失败</p>
            <button @click="coverError = false; coverLoaded = false;" class="retry-btn small">重试</button>
          </div>
          <!-- 实际图片（仅在进入视口且未出错时渲染） -->
          <img
            v-if="isCoverVisible && !coverError"
            :src="data.article.cover_url"
            class="cover"
            alt="文章封面"
            @load="coverLoaded = true"
            @error="coverError = true"
          />
        </div>
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
          <div v-if="data.comments.length === 0" class="empty-comments">
            <p>暂无评论，快来发表第一条评论吧！</p>
          </div>
          <div v-for="comment in data.comments" :key="comment.id" class="comment-item">
            <strong>{{ comment.user?.nickname || comment.guest_nickname || '匿名访客' }}</strong>
            <span>{{ formatDate(comment.created_at) }}</span>
            <p>{{ comment.content }}</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useIntersectionObserver, useClipboard } from '@vueuse/core'

import { webApi } from '../api'
import type { ArticlePageResponse } from '../types'

const route = useRoute()
const data = ref<ArticlePageResponse | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const commentContent = ref('')
const guestNickname = ref('')
const guestEmail = ref('')

// 封面图片懒加载相关
const coverContainer = ref<HTMLElement | null>(null)
const coverLoaded = ref(false)
const coverError = ref(false)
const isCoverVisible = ref(false)

// 观察封面容器是否进入视口
useIntersectionObserver(
  coverContainer,
  ([entry]) => {
    isCoverVisible.value = entry.isIntersecting
  },
  { threshold: 0.1 }
)

// 当封面进入视口且未加载时，重置状态（实际加载由 img 标签的 src 触发）
watch(isCoverVisible, (visible) => {
  if (visible && data.value?.article.cover_url) {
    // 可以在这里触发加载，但 img 的 src 已经绑定，浏览器会自动加载
    // 我们只需要确保状态正确
    coverError.value = false
  }
})

// 目录相关
type TOCItem = { id: string; text: string; level: number }
const toc = ref<TOCItem[]>([])

// 生成目录
const generateTOC = () => {
  toc.value = []
  nextTick(() => {
    const articleBody = document.querySelector('.article-body')
    if (!articleBody) return
    
    const headings = articleBody.querySelectorAll('h2, h3, h4')
    const items: TOCItem[] = []
    
    headings.forEach((heading, index) => {
      const tagName = heading.tagName.toLowerCase()
      const level = parseInt(tagName.charAt(1)) // h2 -> 2, h3 -> 3, h4 -> 4
      const text = heading.textContent || `标题 ${index + 1}`
      
      // 生成唯一 ID
      let id = heading.id
      if (!id) {
        id = 'heading-' + index
        heading.id = id
      }
      
      items.push({ id, text, level })
    })
    
    toc.value = items
  })
}

// 点击目录项平滑滚动
const scrollToHeading = (id: string) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

// 设置代码块复制按钮
const setupCodeCopyButtons = () => {
  nextTick(() => {
    const preElements = document.querySelectorAll('.article-body pre')
    preElements.forEach((pre) => {
      // 避免重复添加按钮
      if (pre.querySelector('.copy-code-btn')) return
      
      const button = document.createElement('button')
      button.className = 'copy-code-btn'
      button.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        </svg>
        复制
      `
      button.title = '复制代码'
      button.addEventListener('click', async () => {
        const code = pre.querySelector('code')?.textContent || pre.textContent || ''
        try {
          await navigator.clipboard.writeText(code)
          button.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            已复制
          `
          button.classList.add('copied')
          setTimeout(() => {
            button.innerHTML = `
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
              复制
            `
            button.classList.remove('copied')
          }, 2000)
        } catch (err) {
          console.error('复制失败:', err)
          button.textContent = '复制失败'
          setTimeout(() => {
            button.innerHTML = `
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
              复制
            `
          }, 2000)
        }
      })
      
      // 将按钮添加到 pre 元素中
      const preEl = pre as HTMLElement
      preEl.style.position = 'relative'
      button.style.position = 'absolute'
      button.style.top = '8px'
      button.style.right = '8px'
      preEl.appendChild(button)
    })
  })
}

// 当文章数据加载完成后生成目录和代码复制按钮
watch(() => data.value, (newData) => {
  if (newData?.article.content_html) {
    generateTOC()
    setupCodeCopyButtons()
  }
})

// 文章分享功能
const { copy, isSupported: isClipboardSupported } = useClipboard()
const shareArticle = async () => {
  if (!data.value) return
  
  const title = data.value.article.title
  const url = window.location.href
  
  // 优先使用 Web Share API
  if (navigator.share) {
    try {
      await navigator.share({
        title,
        text: data.value.article.summary,
        url,
      })
      return
    } catch (err) {
      // 用户取消分享，不处理
      if (err instanceof Error && err.name === 'AbortError') return
      console.error('分享失败:', err)
    }
  }
  
  // 降级方案：复制链接
  if (isClipboardSupported.value) {
    try {
      await copy(url)
      alert('链接已复制到剪贴板！')
    } catch (err) {
      console.error('复制失败:', err)
      alert('复制失败，请手动复制链接：' + url)
    }
  } else {
    // 最终降级：提示手动复制
    prompt('请手动复制以下链接：', url)
  }
}

const loadData = async () => {
  loading.value = true
  error.value = null
  coverLoaded.value = false
  coverError.value = false
  isCoverVisible.value = false
  try {
    data.value = await webApi.getArticle(String(route.params.id))
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载文章失败'
    console.error('加载文章失败:', err)
  } finally {
    loading.value = false
  }
}

const retryLoad = () => {
  loadData()
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

onMounted(loadData)
</script>
