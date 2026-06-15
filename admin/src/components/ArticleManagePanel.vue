<template>
  <section class="panel article-manage-panel">
    <div class="article-manage-head">
      <h3>{{ t('articleManage.title') }}</h3>
      <span class="article-count">{{ t('common.articles', { n: displayArticles.length }) }}</span>
    </div>

    <div class="action-row article-filter-row">
      <input class="article-search-input" v-model="keyword" :placeholder="t('articleManage.searchPlaceholder')" />
      <select class="article-filter-select" v-model="statusFilter">
        <option value="all">{{ t('articleManage.allStatus') }}</option>
        <option value="published">{{ t('status.published') }}</option>
        <option value="draft">{{ t('status.draft') }}</option>
        <option value="pending">{{ t('status.pending') }}</option>
        <option value="rejected">{{ t('status.rejected') }}</option>
      </select>
      <select class="article-filter-select" v-model="sortOrder">
        <option value="newest">{{ t('articleManage.sortNewest') }}</option>
        <option value="oldest">{{ t('articleManage.sortOldest') }}</option>
      </select>
      <button class="article-reset-btn" @click="resetFilters">{{ t('common.reset') }}</button>
    </div>

    <ul class="article-manage-list">
      <li v-for="item in pagedArticles" :key="item.id" class="article-row">
        <div class="article-row-main">
          <p class="article-row-title">
            <span v-html="highlightTitle(item.title)"></span>
            <span class="article-status-chip" :class="`status-${normalizeStatus(item.status)}`">{{ formatArticleStatus(item.status) }}</span>
          </p>
          <small class="article-row-meta">
            <span>{{ t('articleMeta.category') }}{{ item.category?.name || t('articleMeta.uncategorized') }}</span>
            <span>{{ t('articleMeta.author') }}{{ item.author?.nickname || 'admin' }}</span>
            <span>{{ t('articleMeta.published') }}{{ formatRelativeTime(item.published_at || item.created_at) }}</span>
            <span>{{ t('articleMeta.updated') }}{{ formatRelativeTime(getArticleUpdatedAt(item)) }}</span>
            <span>{{ t('articleMeta.views') }}{{ item.view_count || 0 }}</span>
            <span>{{ t('articleMeta.comments') }}{{ item.comment_count || 0 }}</span>
          </small>
        </div>
        <div class="article-row-actions">
          <button type="button" class="article-edit-btn" @click="emit('edit-article', item.id)">{{ t('common.edit') }}</button>
          <button type="button" class="danger-btn article-trash-btn" @click="openTrashConfirm(item.id, item.title)">{{ t('articleManage.trashButton') }}</button>
        </div>
      </li>

      <li v-if="!pagedArticles.length" class="article-empty">{{ t('articleManage.empty') }}</li>
    </ul>

    <ArticleTrashConfirmModal
      :open="trashConfirmOpen"
      :title="trashTargetTitle"
      :message="t('articleManage.trashConfirm')"
      @cancel="closeTrashConfirm"
      @confirm="submitTrashConfirm"
    />

    <div class="article-pagination">
      <div class="article-page-size">
        <span>{{ t('common.perPage') }}</span>
        <select v-model="pageSize" @change="changePageSize">
          <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
        </select>
        <span>{{ t('common.articles') }}</span>
      </div>
      <span class="article-page-indicator article-page-indicator-center">{{ formatPageLabel }}</span>
      <div class="article-page-controls">
        <button v-if="canGoPrev" type="button" class="article-page-btn" @click="goPrevPage">{{ t('common.previous') }}</button>
        <button v-if="canGoNext" type="button" class="article-page-btn" @click="goNextPage">{{ t('common.next') }}</button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import ArticleTrashConfirmModal from './ArticleTrashConfirmModal.vue'

const { t } = useI18n()

const props = defineProps<{
  articles: any[]
  formatArticleStatus: (status: string) => string
}>()

const emit = defineEmits<{
  'move-to-trash': [articleId: number]
  'edit-article': [articleId: number]
}>()

const trashConfirmOpen = ref(false)
const trashTargetId = ref<number | null>(null)
const trashTargetTitle = ref('')

const keyword = ref('')
const statusFilter = ref<'all' | 'published' | 'draft' | 'pending' | 'rejected'>('all')
const sortOrder = ref<'newest' | 'oldest'>('newest')

const normalizeStatus = (status: string) => String(status || '').trim().toLowerCase()

const getArticleUpdatedAt = (item: any) => {
  const publishedAt = new Date(String(item.published_at || '')).getTime()
  const updatedAt = new Date(String(item.updated_at || '')).getTime()
  const createdAt = new Date(String(item.created_at || '')).getTime()
  if (Number.isNaN(updatedAt)) return item.published_at || item.created_at || ''
  if (!Number.isNaN(publishedAt) && updatedAt <= publishedAt) return item.published_at || item.created_at || ''
  if (!Number.isNaN(createdAt) && updatedAt <= createdAt) return item.published_at || item.created_at || ''
  return item.updated_at || item.published_at || item.created_at || ''
}

const statusMatched = (status: string) => {
  if (statusFilter.value === 'all') return true
  const normalized = normalizeStatus(status)
  if (statusFilter.value === 'published') return normalized === 'published'
  if (statusFilter.value === 'draft') return normalized === 'draft'
  if (statusFilter.value === 'pending') return ['pending', 'pending_review'].includes(normalized)
  if (statusFilter.value === 'rejected') return normalized === 'rejected'
  return true
}

const displayArticles = computed(() => {
  const key = keyword.value.trim().toLowerCase()

  return [...props.articles]
    .filter((item) => {
      const title = String(item.title || '').toLowerCase()
      const keywordMatched = !key || title.includes(key)
      return keywordMatched && statusMatched(item.status)
    })
    .sort((a, b) => {
      const t1 = new Date(a.published_at || a.created_at || 0).getTime()
      const t2 = new Date(b.published_at || b.created_at || 0).getTime()
      return sortOrder.value === 'newest' ? t2 - t1 : t1 - t2
    })
})

const pageSizeOptions = [10, 20, 50]
const pageSize = ref(10)
const currentPage = ref(1)

const totalPages = computed(() => Math.max(1, Math.ceil(displayArticles.value.length / pageSize.value)))

const pagedArticles = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return displayArticles.value.slice(start, start + pageSize.value)
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

const openTrashConfirm = (articleId: number, title: string) => {
  trashTargetId.value = articleId
  trashTargetTitle.value = title
  trashConfirmOpen.value = true
}

const closeTrashConfirm = () => {
  trashConfirmOpen.value = false
  trashTargetId.value = null
  trashTargetTitle.value = ''
}

const submitTrashConfirm = () => {
  if (trashTargetId.value === null) return
  emit('move-to-trash', trashTargetId.value)
  closeTrashConfirm()
}

const escapeHtml = (value: string) =>
  value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

const escapeRegExp = (value: string) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

const highlightTitle = (value: string) => {
  const raw = String(value || '')
  const safe = escapeHtml(raw)
  const key = keyword.value.trim()
  if (!key) return safe

  const pattern = new RegExp(`(${escapeRegExp(key)})`, 'ig')
  return safe.replace(pattern, '<mark>$1</mark>')
}

const formatPageLabel = computed(() => t('articleManage.pageInfo', { current: currentPage.value, total: totalPages.value }))

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
    return t('time.minutesAgo', { n: minutes })
  }
  if (diffMs < day) {
    const hours = Math.max(1, Math.floor(diffMs / hour))
    return t('time.hoursAgo', { n: hours })
  }
  if (diffMs < year) {
    const days = Math.max(1, Math.floor(diffMs / day))
    return t('time.daysAgo', { n: days })
  }
  const years = Math.max(1, Math.floor(diffMs / year))
  return t('time.yearsAgo', { n: years })
}
</script>
