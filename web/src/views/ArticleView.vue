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
        <div v-if="submitSuccess" class="submit-success">
          <p>✅ 评论已提交成功！等待管理员审核通过后显示。</p>
        </div>
        <div v-if="submitError" class="submit-error">
          <p>❌ {{ submitError }}</p>
        </div>
        <form class="comment-form" @submit.prevent="submitTopLevelComment">
          <input v-model="guestNickname" placeholder="匿名昵称（登录后可留空）" />
          <input v-model="guestEmail" placeholder="匿名邮箱（登录后可留空）" />
          <textarea v-model="commentContent" placeholder="写下你的看法"></textarea>
          <button type="submit" :disabled="submitting">
            {{ submitting ? '提交中...' : '提交评论' }}
          </button>
        </form>
        <div class="comment-list">
          <div v-if="commentTree.length === 0" class="empty-comments">
            <p>暂无评论，快来发表第一条评论吧！</p>
          </div>
          <CommentTreeNode
            v-for="comment in commentTree"
            :key="comment.id"
            :comment="comment"
            :replying-to="replyingTo"
            @reply="handleReply"
            @submit-reply="handleSubmitReply"
          />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, nextTick, computed, defineComponent } from 'vue'
import { useRoute } from 'vue-router'
import { useIntersectionObserver, useClipboard } from '@vueuse/core'

import { webApi } from '../api'
import type { ArticlePageResponse, Comment } from '../types'

// 嵌套评论相关接口
interface CommentNode extends Comment {
  children: CommentNode[]
}

// 扁平评论列表转换为树形结构
function buildCommentTree(comments: Comment[]): CommentNode[] {
  const map = new Map<number, CommentNode>()
  const roots: CommentNode[] = []
  
  // 第一遍：创建所有节点
  comments.forEach(comment => {
    map.set(comment.id, { ...comment, children: [] })
  })
  
  // 第二遍：构建父子关系
  comments.forEach(comment => {
    const node = map.get(comment.id)!
    if (comment.parent_id && map.has(comment.parent_id)) {
      const parent = map.get(comment.parent_id)!
      parent.children.push(node)
    } else {
      roots.push(node)
    }
  })
  
  return roots
}

// 递归评论组件
const CommentTreeNode = defineComponent({
  name: 'CommentTreeNode',
  props: {
    comment: {
      type: Object as () => CommentNode,
      required: true
    },
    replyingTo: {
      type: Number as () => number | null,
      default: null
    },
    depth: {
      type: Number,
      default: 0
    }
  },
  emits: ['reply', 'submit-reply'],
  setup(props, { emit }) {
    const localReplyContent = ref('')
    
    const handleLocalReply = () => {
      emit('reply', props.comment.id)
    }
    
    const handleLocalSubmitReply = () => {
      emit('submit-reply', props.comment.id, localReplyContent.value)
    }
    
    return {
      localReplyContent,
      handleLocalReply,
      handleLocalSubmitReply
    }
  },
  template: `
    <div class="comment-item" :style="{ marginLeft: depth * 32 + 'px' }">
      <strong>{{ comment.user?.nickname || comment.guest_nickname || '匿名访客' }}</strong>
      <span>{{ comment.created_at ? new Date(comment.created_at).toLocaleString('zh-CN') : '' }}</span>
      <p>{{ comment.content }}</p>
      
      <button class="reply-btn" @click="handleLocalReply">回复</button>
      
      <!-- 回复表单（仅当正在回复此评论时显示） -->
      <div v-if="replyingTo === comment.id" class="inline-reply-form">
        <textarea v-model="localReplyContent" :placeholder="'回复 @' + (comment.user?.nickname || comment.guest_nickname || '匿名访客')"></textarea>
        <div style="display: flex; gap: 8px; margin-top: 8px;">
          <button @click="handleLocalSubmitReply" class="submit-reply-btn">提交回复</button>
          <button @click="$emit('reply', null)" class="cancel-reply-btn">取消</button>
        </div>
      </div>
      
      <!-- 递归渲染子评论 -->
      <div v-if="comment.children.length > 0" class="children">
        <CommentTreeNode
          v-for="child in comment.children"
          :key="child.id"
          :comment="child"
          :replying-to="replyingTo"
          :depth="depth + 1"
          @reply="(commentId) => $emit('reply', commentId)"
          @submit-reply="(commentId, content) => $emit('submit-reply', commentId, content)"
        />
      </div>
    </div>
  `
})

const route = useRoute()
const data = ref<ArticlePageResponse | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const commentContent = ref('')
const guestNickname = ref('')
const guestEmail = ref('')
const submitting = ref(false)
const submitError = ref<string | null>(null)
const submitSuccess = ref(false)

// 嵌套评论相关状态
const commentTree = computed(() => buildCommentTree(data.value?.comments || []))
const replyingTo = ref<number | null>(null)
const replyContent = ref('')

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

const submitComment = async (parentId: number | null = null) => {
  const content = parentId ? replyContent.value : commentContent.value
  if (!data.value || !content.trim()) return
  
  // 验证匿名评论必须提供昵称和邮箱
  if (!guestNickname.value.trim() || !guestEmail.value.trim()) {
    submitError.value = '匿名评论必须提供昵称和邮箱'
    return
  }
  
  submitting.value = true
  submitError.value = null
  submitSuccess.value = false
  
  console.log('Submitting comment:', { parentId, content, articleId: data.value.article.id, guestNickname: guestNickname.value, guestEmail: guestEmail.value })
  
  try {
    await webApi.submitComment({
      article_id: data.value.article.id,
      content,
      guest_nickname: guestNickname.value,
      guest_email: guestEmail.value,
      parent_id: parentId || null,
    })
    
    console.log('Comment submitted successfully')
    
    // 显示成功消息
    submitSuccess.value = true
    // 5秒后自动隐藏成功消息
    setTimeout(() => {
      submitSuccess.value = false
    }, 5000)
    
    if (parentId) {
      replyContent.value = ''
      replyingTo.value = null
    } else {
      commentContent.value = ''
      guestNickname.value = ''
      guestEmail.value = ''
    }
    
    await loadData()
  } catch (err) {
    submitError.value = err instanceof Error ? err.message : '提交评论失败，请重试'
    console.error('提交评论失败:', err)
  } finally {
    submitting.value = false
  }
}

const submitTopLevelComment = () => submitComment(null)

const handleReply = (commentId: number) => {
  replyingTo.value = commentId
  replyContent.value = ''
  // 滚动到回复表单可见区域（由模板处理）
}

const handleSubmitReply = (commentId: number, content: string) => {
  replyContent.value = content
  replyingTo.value = commentId
  submitComment(commentId)
}

const formatDate = (value: string) => new Date(value).toLocaleString('zh-CN')

onMounted(loadData)
</script>
