<template>
  <section class="panel comments-panel">
    <div class="article-manage-head comments-head">
      <div>
        <h3>评论管理</h3>
        <p class="comments-subtitle">集中审核文章评论，维护社区内容质量</p>
      </div>
      <span class="article-count comments-count">共 {{ displayComments.length }} 条</span>
    </div>

    <div class="action-row comments-filter-row">
      <input class="article-search-input comments-search-input" v-model="keyword" placeholder="按评论内容或文章标题搜索" />
      <select class="article-filter-select comments-filter-select" v-model="statusFilter">
        <option value="all">全部状态</option>
        <option value="APPROVED">已通过</option>
        <option value="PENDING">待审核</option>
        <option value="REJECTED">已拒绝</option>
      </select>
      <select class="article-filter-select comments-filter-select" v-model="sortOrder">
        <option value="newest">评论时间：最新优先</option>
        <option value="oldest">评论时间：最早优先</option>
      </select>
      <button class="article-reset-btn" type="button" @click="resetFilters">重置筛选</button>
    </div>

    <div class="comments-list">
      <article
        v-for="item in pagedComments"
        :key="item.id"
        class="comments-card"
        :class="[
          `status-${normalizeStatus(item.status)}`,
          { 'is-approved': isApproved(item.status), 'is-rejected': isRejected(item.status), 'is-pending': isPending(item.status) },
        ]"
      >
        <div class="comments-card-main">
          <div class="comments-card-headline">
            <p class="comments-content">{{ item.content }}</p>
            <span class="comments-status-badge" :class="`status-${normalizeStatus(item.status)}`">{{ formatCommentStatus(item.status) }}</span>
          </div>
          <a
            v-if="item.article?.id"
            class="comments-article-link comments-article-title"
            :href="webArticleUrl(item.article.id)"
            target="_blank"
            rel="noreferrer"
          >
            {{ truncateText(item.article.title, 80) }}
          </a>
          <div class="comments-meta">
            <span>昵称：{{ item.user?.nickname || item.guest_nickname || '匿名访客' }}</span>
            <span>邮箱：{{ item.guest_email || '-' }}</span>
            <span>时间：<span :title="formatDateTime(item.created_at)">{{ formatRelativeTime(item.created_at) }}</span></span>
          </div>
        </div>
        <div class="comments-actions">
          <button v-if="!isApproved(item.status) && !isRejected(item.status)" type="button" @click="$emit('approve', item.id)">通过</button>
          <button v-if="!isRejected(item.status)" type="button" class="danger-btn" @click="openRejectConfirm(item)">拒绝</button>
        </div>
      </article>

      <p v-if="!pagedComments.length" class="comments-empty">暂无符合条件的评论</p>
    </div>

    <div class="article-pagination comments-pagination">
      <div class="article-page-size">
        <span>每页</span>
        <select v-model="pageSize" @change="changePageSize">
          <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
        </select>
        <span>条</span>
      </div>
      <span class="article-page-indicator article-page-indicator-center">{{ formatPageLabel }}</span>
      <div class="article-page-controls">
        <button v-if="canGoPrev" type="button" class="article-page-btn" @click="goPrevPage">上一页</button>
        <button v-if="canGoNext" type="button" class="article-page-btn" @click="goNextPage">下一页</button>
      </div>
    </div>

    <div v-if="rejectConfirmOpen" class="comment-modal-backdrop" @click.self="closeRejectConfirm">
      <div class="comment-modal">
        <div class="comment-modal-head">
          <div>
            <p class="comment-modal-eyebrow">确认拒绝</p>
            <h4>是否拒绝这条评论？</h4>
          </div>
          <button type="button" class="comment-modal-close" aria-label="关闭弹窗" @click="closeRejectConfirm">×</button>
        </div>

        <p class="comment-modal-text">拒绝后，这条评论将被标记为拒绝状态，并不会在前台展示。</p>

        <div class="comment-modal-preview">
          <div class="comment-modal-label">评论内容</div>
          <div class="comment-modal-content">{{ rejectTarget?.content }}</div>
          <div v-if="rejectTarget?.article?.id" class="comment-modal-article">
            关联文章：
            <a :href="webArticleUrl(rejectTarget.article.id)" target="_blank" rel="noreferrer">{{ truncateText(rejectTarget.article.title, 80) }}</a>
          </div>
        </div>

        <div class="comment-modal-actions">
          <button type="button" class="comment-modal-cancel" @click="closeRejectConfirm">取消</button>
          <button type="button" class="comment-modal-confirm danger-btn" @click="confirmReject">确认拒绝</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

type CommentItem = {
  id: number
  content: string
  status: string
  created_at: string
  guest_nickname?: string | null
  guest_email?: string | null
  user?: { nickname?: string | null }
  article?: { id?: number; title?: string | null } | null
}

const props = defineProps<{
  comments: CommentItem[]
  formatCommentStatus: (status: string) => string
}>()

const emit = defineEmits<{
  approve: [commentId: number]
  reject: [commentId: number]
}>()

const keyword = ref('')
const statusFilter = ref<'all' | 'APPROVED' | 'PENDING' | 'REJECTED'>('all')
const sortOrder = ref<'newest' | 'oldest'>('newest')
const pageSizeOptions = [10, 20, 50]
const pageSize = ref(10)
const currentPage = ref(1)
const rejectConfirmOpen = ref(false)
const rejectTarget = ref<CommentItem | null>(null)

const isApproved = (status: string) => String(status || '').toUpperCase() === 'APPROVED'
const isRejected = (status: string) => String(status || '').toUpperCase() === 'REJECTED'
const isPending = (status: string) => !isApproved(status) && !isRejected(status)
const normalizeStatus = (status: string) => String(status || '').trim().toLowerCase()

const truncateText = (value: string | null | undefined, maxLength: number) => {
  const text = String(value || '').trim()
  if (!text) return ''
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text
}

const WEB_BASE_URL = String(import.meta.env.VITE_WEB_BASE_URL || 'http://localhost:5173').replace(/\/$/, '')
const webArticleUrl = (articleId: number) => `${WEB_BASE_URL}/article/${articleId}`

const parseDateTime = (value: string) => {
  const text = String(value || '').trim()
  if (!text) return new Date(0)
  if (/Z|[+-]\d{2}:?\d{2}$/.test(text)) return new Date(text)
  return new Date(`${text}Z`)
}

const formatDateTime = (value: string) => parseDateTime(value).toLocaleString('zh-CN')

const formatRelativeTime = (value: string) => {
  const date = parseDateTime(value)
  const now = Date.now()
  const diffMs = Math.max(0, now - date.getTime())
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  const year = 365 * day

  if (diffMs < hour) return `${Math.max(1, Math.floor(diffMs / minute))} 分钟前`
  if (diffMs < day) return `${Math.max(1, Math.floor(diffMs / hour))} 小时前`
  if (diffMs < year) return `${Math.max(1, Math.floor(diffMs / day))} 天前`
  return `${Math.max(1, Math.floor(diffMs / year))} 年前`
}

const filteredComments = computed(() => {
  const key = keyword.value.trim().toLowerCase()
  return [...props.comments].filter((item) => {
    const content = String(item.content || '').toLowerCase()
    const articleTitle = String(item.article?.title || '').toLowerCase()
    const keywordMatched = !key || content.includes(key) || articleTitle.includes(key)
    const status = String(item.status || '').toUpperCase()
    const statusMatched =
      statusFilter.value === 'all' ||
      (statusFilter.value === 'APPROVED' && status === 'APPROVED') ||
      (statusFilter.value === 'PENDING' && isPending(status)) ||
      (statusFilter.value === 'REJECTED' && status === 'REJECTED')
    return keywordMatched && statusMatched
  })
})

const displayComments = computed(() => {
  return [...filteredComments.value].sort((a, b) => {
    const t1 = parseDateTime(a.created_at || '').getTime()
    const t2 = parseDateTime(b.created_at || '').getTime()
    return sortOrder.value === 'newest' ? t2 - t1 : t1 - t2
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(displayComments.value.length / pageSize.value)))

const pagedComments = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return displayComments.value.slice(start, start + pageSize.value)
})

const canGoPrev = computed(() => currentPage.value > 1)
const canGoNext = computed(() => currentPage.value < totalPages.value)

const resetFilters = () => {
  keyword.value = ''
  statusFilter.value = 'all'
  sortOrder.value = 'newest'
  currentPage.value = 1
}

const changePageSize = () => {
  currentPage.value = 1
}

const goPrevPage = () => {
  if (canGoPrev.value) currentPage.value -= 1
}

const goNextPage = () => {
  if (canGoNext.value) currentPage.value += 1
}

const formatPageLabel = computed(() => `当前 ${currentPage.value} 页 / 共 ${totalPages.value} 页`)

const openRejectConfirm = (item: CommentItem) => {
  rejectTarget.value = item
  rejectConfirmOpen.value = true
}

const closeRejectConfirm = () => {
  rejectConfirmOpen.value = false
  rejectTarget.value = null
}

const confirmReject = () => {
  if (!rejectTarget.value) return
  emit('reject', rejectTarget.value.id)
  closeRejectConfirm()
}
</script>
