<template>
  <section class="panel comments-panel">
    <div class="comments-head">
      <div>
        <h3>{{ t('comment.title') }}</h3>
        <p class="comments-subtitle">{{ t('comment.subtitle') }}</p>
      </div>
      <span class="comments-count">{{ t('comment.totalCount', { n: commentsTotal }) }}</span>
    </div>

    <div class="comments-filter-row">
      <input class="comments-search-input" v-model="keyword" :placeholder="t('comment.searchPlaceholder')" @input="queueQueryChange" />
      <select class="comments-filter-select" v-model="statusFilter" @change="() => applyQueryChange()">
        <option value="all">{{ t('comment.allStatus') }}</option>
        <option value="APPROVED">{{ t('status.approved') }}</option>
        <option value="PENDING">{{ t('status.pending') }}</option>
        <option value="REJECTED">{{ t('status.rejected') }}</option>
        <option value="SPAM">{{ t('comment.statusSpam') }}</option>
        <option value="TRASH">{{ t('status.trash') }}</option>
      </select>
      <select class="comments-filter-select" v-model="sortOrder" @change="() => applyQueryChange()">
        <option value="newest">{{ t('comment.sortNewest') }}</option>
        <option value="oldest">{{ t('comment.sortOldest') }}</option>
      </select>
      <button class="article-reset-btn" type="button" @click="resetFilters">{{ t('common.reset') }}</button>
      <button class="article-reset-btn" type="button" :title="t('comment.refreshTitle')" @click="emit('refresh')">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:4px"><path d="M4 4v5h5M20 20v-5h-5"/><path d="M20.49 9A9 9 0 0 0 5.64 5.64L4 4m16 16-1.64-1.64A9 9 0 0 1 3.51 15"/></svg>
        {{ t('common.refresh') }}
      </button>
    </div>

    <div class="comments-toolbar">
      <label class="comments-select-all">
        <input type="checkbox" :checked="allVisibleSelected" :indeterminate.prop="indeterminateVisibleSelected" @change="toggleSelectAllVisible" />
        <span>{{ t('common.selectAll') }}</span>
      </label>
      <div class="comments-bulk-actions">
        <button type="button" class="cm-btn cm-btn-approve" :disabled="!hasSelectedPending" @click="bulkApproveSelected">{{ t('comment.batchApprove') }}</button>
        <button type="button" class="cm-btn cm-btn-reject" :disabled="!hasSelectedPending" @click="bulkRejectSelected">{{ t('comment.batchReject') }}</button>
        <button type="button" class="cm-btn cm-btn-delete" :disabled="!hasSelectedRejected" @click="openBulkDeleteConfirm">{{ t('comment.batchDelete') }}</button>
      </div>
    </div>

    <div class="comments-list">
      <article
        v-for="item in comments"
        :key="item.id"
        class="comments-card"
        :class="[
          `status-${normalizeStatus(item.status)}`,
          { 'is-approved': isApproved(item.status), 'is-rejected': isRejected(item.status), 'is-pending': isPending(item.status) },
        ]"
      >
        <label class="comments-checkbox-wrap">
          <input type="checkbox" :checked="selectedIdsSet.has(item.id)" @change="toggleSelectItem(item.id)" />
        </label>
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
            <span>{{ t('comment.nicknamePrefix') }}{{ item.user?.nickname || item.guest_nickname || t('comment.anonymous') }}</span>
            <span>{{ t('comment.emailPrefix') }}{{ item.guest_email || '-' }}</span>
            <span>{{ t('comment.timePrefix') }}<span :title="formatDateTime(item.created_at)">{{ formatRelativeTime(item.created_at) }}</span></span>
          </div>
        </div>
        <div class="comments-actions">
          <button v-if="!isApproved(item.status) && !isRejected(item.status)" type="button" class="cm-btn cm-btn-approve" @click="$emit('approve', item.id)">{{ t('comment.approve') }}</button>
          <button v-if="!isRejected(item.status)" type="button" class="cm-btn cm-btn-reject" @click="openRejectConfirm(item)">{{ t('comment.reject') }}</button>
          <button type="button" class="cm-btn cm-btn-delete" @click="$emit('delete', item.id)">{{ t('common.delete') }}</button>
        </div>
      </article>

      <p v-if="!comments.length" class="comments-empty">{{ t('comment.empty') }}</p>
    </div>

    <div class="article-pagination comments-pagination">
      <div class="article-page-size">
        <span>{{ t('common.perPage') }}</span>
        <select v-model="pageSize" @change="changePageSize">
          <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
        </select>
        <span>{{ t('common.items') }}</span>
      </div>
      <span class="article-page-indicator article-page-indicator-center">{{ formatPageLabel }}</span>
      <div class="article-page-controls">
        <button v-if="canGoPrev" type="button" class="article-page-btn" @click="goPrevPage">{{ t('common.previous') }}</button>
        <button v-if="canGoNext" type="button" class="article-page-btn" @click="goNextPage">{{ t('common.next') }}</button>
      </div>
    </div>

    <div v-if="rejectConfirmOpen || bulkDeleteConfirmOpen" class="comment-modal-backdrop" @click.self="closeActiveConfirm">
      <div class="comment-modal">
        <div class="comment-modal-head">
          <div>
            <p class="comment-modal-eyebrow">{{ bulkDeleteConfirmOpen ? t('comment.confirmDeleteTitle') : t('comment.confirmRejectTitle') }}</p>
            <h4>{{ bulkDeleteConfirmOpen ? t('comment.deleteModalHeading') : t('comment.rejectModalHeading') }}</h4>
          </div>
          <button type="button" class="comment-modal-close" :aria-label="t('comment.closeModalLabel')" @click="closeActiveConfirm">×</button>
        </div>

        <p class="comment-modal-text">
          {{ bulkDeleteConfirmOpen ? t('comment.deleteModalText') : t('comment.rejectModalText') }}
        </p>

        <div class="comment-modal-preview">
          <div class="comment-modal-label">{{ bulkDeleteConfirmOpen ? t('comment.deleteCount') : t('comment.commentContent') }}</div>
          <div v-if="bulkDeleteConfirmOpen" class="comment-modal-content">{{ t('comment.rejectedSelected', { n: selectedRejectedIds.length }) }}</div>
          <div v-else class="comment-modal-content">{{ rejectTarget?.content }}</div>
          <div v-if="!bulkDeleteConfirmOpen && rejectTarget?.article?.id" class="comment-modal-article">
            {{ t('comment.articlePrefix') }}
            <a :href="webArticleUrl(rejectTarget.article.id)" target="_blank" rel="noreferrer">{{ truncateText(rejectTarget.article.title, 80) }}</a>
          </div>
        </div>

        <div class="comment-modal-actions">
          <button type="button" class="cm-btn" @click="closeActiveConfirm">{{ t('common.cancel') }}</button>
          <button v-if="bulkDeleteConfirmOpen" type="button" class="cm-btn cm-btn-delete" @click="confirmBulkDelete">{{ t('comment.confirmDeleteButton') }}</button>
          <button v-else type="button" class="cm-btn cm-btn-reject" @click="confirmReject">{{ t('comment.confirmRejectButton') }}</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

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
  commentsTotal: number
  commentsPage: number
  commentsPageSize: number
  commentsTotalPages: number
  formatCommentStatus: (status: string) => string
}>()

const emit = defineEmits<{
  approve: [commentId: number]
  reject: [commentId: number]
  delete: [commentId: number]
  'bulk-approve': [commentIds: number[]]
  'bulk-reject': [commentIds: number[]]
  'bulk-delete': [commentIds: number[]]
  'query-change': [query: { page: number; pageSize: number; keyword: string; status: string; sort: 'newest' | 'oldest' }]
  refresh: []
}>()

const keyword = ref('')
const statusFilter = ref<'all' | 'APPROVED' | 'PENDING' | 'REJECTED' | 'SPAM' | 'TRASH'>('all')
const sortOrder = ref<'newest' | 'oldest'>('newest')
const pageSizeOptions = [10, 20, 50]
const pageSize = ref(10)
const currentPage = ref(1)
const selectedIds = ref<number[]>([])
const rejectConfirmOpen = ref(false)
const bulkDeleteConfirmOpen = ref(false)
const rejectTarget = ref<CommentItem | null>(null)

const isApproved = (status: string) => String(status || '').toUpperCase() === 'APPROVED'
const isRejected = (status: string) => String(status || '').toUpperCase() === 'REJECTED'
const isPending = (status: string) => String(status || '').toUpperCase() === 'PENDING'
const normalizeStatus = (status: string) => String(status || '').trim().toLowerCase()
let queryTimer: number | null = null

const truncateText = (value: string | null | undefined, maxLength: number) => {
  const text = String(value || '').trim()
  if (!text) return ''
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text
}

const webArticleBaseUrl = () => {
  const configuredUrl = String(import.meta.env.VITE_WEB_BASE_URL || '').trim()
  if (configuredUrl) return configuredUrl.replace(/\/$/, '')

  if (import.meta.env.DEV) {
    const webOrigin = new URL(window.location.origin)
    webOrigin.port = '5173'
    return webOrigin.origin
  }

  return window.location.origin
}

const webArticleUrl = (articleId: number) => `${webArticleBaseUrl()}/article/details/${articleId}`

const parseDateTime = (value: string) => {
  const text = String(value || '').trim()
  if (!text) return new Date(0)
  if (/Z|[+-]\d{2}:?\d{2}$/.test(text)) return new Date(text)
  return new Date(`${text}Z`)
}

const formatDateTime = (value: string) => parseDateTime(value).toLocaleString(locale.value)

const formatRelativeTime = (value: string) => {
  const date = parseDateTime(value)
  const now = Date.now()
  const diffMs = Math.max(0, now - date.getTime())
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  const year = 365 * day

  if (diffMs < hour) return t('time.minutesAgo', { n: Math.max(1, Math.floor(diffMs / minute)) })
  if (diffMs < day) return t('time.hoursAgo', { n: Math.max(1, Math.floor(diffMs / hour)) })
  if (diffMs < year) return t('time.daysAgo', { n: Math.max(1, Math.floor(diffMs / day)) })
  return t('time.yearsAgo', { n: Math.max(1, Math.floor(diffMs / year)) })
}

const totalPages = computed(() => Math.max(1, props.commentsTotalPages || 1))

const visibleIds = computed(() => props.comments.map((item) => item.id))
const selectedIdsSet = computed(() => new Set(selectedIds.value))
const visibleSelectedIds = computed(() => visibleIds.value.filter((id) => selectedIdsSet.value.has(id)))
const allVisibleSelected = computed(() => visibleIds.value.length > 0 && visibleSelectedIds.value.length === visibleIds.value.length)
const indeterminateVisibleSelected = computed(() => visibleSelectedIds.value.length > 0 && visibleSelectedIds.value.length < visibleIds.value.length)
const selectedPendingIds = computed(() => selectedIds.value.filter((id) => {
  const item = props.comments.find((comment) => comment.id === id)
  return item ? isPending(item.status) : false
}))
const selectedRejectedIds = computed(() => selectedIds.value.filter((id) => {
  const item = props.comments.find((comment) => comment.id === id)
  return item ? isRejected(item.status) : false
}))
const hasSelectedPending = computed(() => selectedPendingIds.value.length > 0)
const hasSelectedRejected = computed(() => selectedRejectedIds.value.length > 0)
const canGoPrev = computed(() => currentPage.value > 1)
const canGoNext = computed(() => currentPage.value < totalPages.value)

const resetFilters = () => {
  keyword.value = ''
  statusFilter.value = 'all'
  sortOrder.value = 'newest'
  currentPage.value = 1
  selectedIds.value = []
  applyQueryChange()
}

const changePageSize = () => {
  currentPage.value = 1
  applyQueryChange()
}

const toggleSelectItem = (id: number) => {
  if (selectedIds.value.includes(id)) {
    selectedIds.value = selectedIds.value.filter((item) => item !== id)
    return
  }
  selectedIds.value = [...selectedIds.value, id]
}

const toggleSelectAllVisible = () => {
  if (allVisibleSelected.value) {
    selectedIds.value = selectedIds.value.filter((id) => !visibleIds.value.includes(id))
    return
  }
  const merged = new Set([...selectedIds.value, ...visibleIds.value])
  selectedIds.value = Array.from(merged)
}

const bulkApproveSelected = () => {
  const targets = selectedPendingIds.value
  if (!targets.length) return
  emit('bulk-approve', targets)
  selectedIds.value = selectedIds.value.filter((id) => !targets.includes(id))
}

const bulkRejectSelected = () => {
  const targets = selectedPendingIds.value
  if (!targets.length) return
  emit('bulk-reject', targets)
  selectedIds.value = selectedIds.value.filter((id) => !targets.includes(id))
}

const openBulkDeleteConfirm = () => {
  const targets = selectedRejectedIds.value
  if (!targets.length) return
  bulkDeleteConfirmOpen.value = true
}

const goPrevPage = () => {
  if (!canGoPrev.value) return
  currentPage.value -= 1
  applyQueryChange(false)
}

const goNextPage = () => {
  if (!canGoNext.value) return
  currentPage.value += 1
  applyQueryChange(false)
}

const formatPageLabel = computed(() => t('comment.pageInfo', { current: currentPage.value, total: totalPages.value }))

const openRejectConfirm = (item: CommentItem) => {
  rejectTarget.value = item
  rejectConfirmOpen.value = true
}

const closeRejectConfirm = () => {
  rejectConfirmOpen.value = false
  rejectTarget.value = null
}

const closeBulkDeleteConfirm = () => {
  bulkDeleteConfirmOpen.value = false
}

const closeActiveConfirm = () => {
  closeRejectConfirm()
  closeBulkDeleteConfirm()
}

const confirmReject = () => {
  if (!rejectTarget.value) return
  emit('reject', rejectTarget.value.id)
  closeRejectConfirm()
}

const confirmBulkDelete = () => {
  const targets = selectedRejectedIds.value
  if (!targets.length) return
  emit('bulk-delete', targets)
  selectedIds.value = selectedIds.value.filter((id) => !targets.includes(id))
  closeBulkDeleteConfirm()
}

const emitQueryChange = () => {
  selectedIds.value = []
  emit('query-change', {
    page: currentPage.value,
    pageSize: Number(pageSize.value),
    keyword: keyword.value,
    status: statusFilter.value,
    sort: sortOrder.value,
  })
}

const applyQueryChange = (resetPage = true) => {
  if (queryTimer !== null) {
    window.clearTimeout(queryTimer)
    queryTimer = null
  }
  if (resetPage) currentPage.value = 1
  emitQueryChange()
}

const queueQueryChange = () => {
  if (queryTimer !== null) window.clearTimeout(queryTimer)
  queryTimer = window.setTimeout(() => {
    queryTimer = null
    currentPage.value = 1
    emitQueryChange()
  }, 250)
}

watch(() => props.commentsPage, (value) => {
  currentPage.value = value || 1
})

watch(() => props.commentsPageSize, (value) => {
  pageSize.value = value || 10
})
</script>
