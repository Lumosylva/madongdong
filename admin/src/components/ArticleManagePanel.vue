<template>
  <section class="panel article-manage-panel">
    <div class="article-manage-head">
      <h3>文章管理</h3>
      <span class="article-count">共 {{ displayArticles.length }} 篇</span>
    </div>

    <div class="action-row article-filter-row">
      <input class="article-search-input" v-model="keyword" placeholder="按标题搜索" />
      <select class="article-filter-select" v-model="statusFilter">
        <option value="all">全部状态</option>
        <option value="published">已发布</option>
        <option value="draft">草稿</option>
        <option value="pending">待审核</option>
        <option value="rejected">已驳回</option>
      </select>
      <select class="article-filter-select" v-model="sortOrder">
        <option value="newest">发布时间：最新优先</option>
        <option value="oldest">发布时间：最早优先</option>
      </select>
      <button class="article-reset-btn" @click="resetFilters">重置筛选</button>
    </div>

    <ul class="article-manage-list">
      <li v-for="item in pagedArticles" :key="item.id" class="article-row">
        <div class="article-row-main">
          <p class="article-row-title">
            <span v-html="highlightTitle(item.title)"></span>
            <span class="article-status-chip" :class="`status-${normalizeStatus(item.status)}`">{{ formatArticleStatus(item.status) }}</span>
          </p>
          <small class="article-row-meta">
            <span>分类：{{ item.category?.name || '未分类' }}</span>
            <span>作者：{{ item.author?.nickname || 'admin' }}</span>
            <span>发布时间：{{ formatRelativeTime(item.published_at || item.created_at) }}</span>
            <span>浏览：{{ item.view_count || 0 }}</span>
            <span>评论：{{ item.comment_count || 0 }}</span>
          </small>
        </div>
        <button class="danger-btn" @click="confirmTrash(item.id)">移入垃圾箱</button>
      </li>

      <li v-if="!pagedArticles.length" class="article-empty">暂无符合条件的文章</li>
    </ul>

    <div class="article-pagination">
      <div class="article-page-size">
        <span>每页</span>
        <select v-model="pageSize" @change="changePageSize">
          <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
        </select>
        <span>篇</span>
      </div>
      <span class="article-page-indicator article-page-indicator-center">{{ formatPageLabel }}</span>
      <div class="article-page-controls">
        <button v-if="canGoPrev" type="button" class="article-page-btn" @click="goPrevPage">上一页</button>
        <button v-if="canGoNext" type="button" class="article-page-btn" @click="goNextPage">下一页</button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{
  articles: any[]
  formatArticleStatus: (status: string) => string
}>()

const emit = defineEmits<{
  'move-to-trash': [articleId: number]
}>()

const keyword = ref('')
const statusFilter = ref<'all' | 'published' | 'draft' | 'pending' | 'rejected'>('all')
const sortOrder = ref<'newest' | 'oldest'>('newest')

const normalizeStatus = (status: string) => String(status || '').trim().toLowerCase()

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

const confirmTrash = (articleId: number) => {
  if (window.confirm('确定要将这篇文章移入垃圾箱吗？')) {
    emit('move-to-trash', articleId)
  }
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

const formatPageLabel = computed(() => `当前 ${currentPage.value} 页 / 共 ${totalPages.value} 页`)

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
</script>

<style scoped>
.article-manage-panel :deep(mark) {
  background: rgba(14, 165, 164, 0.2);
  color: var(--text);
  border: 1px solid rgba(14, 165, 164, 0.42);
  border-radius: 6px;
  padding: 0 4px;
}

:global(:root[data-theme='dark']) .article-manage-panel :deep(mark) {
  background: rgba(94, 234, 212, 0.24);
  border-color: rgba(94, 234, 212, 0.5);
  color: #e6fffb;
}

.article-status-chip.status-published {
  background: rgba(14, 165, 164, 0.1);
  border-color: rgba(14, 165, 164, 0.22);
  color: var(--accent);
}

.article-status-chip.status-draft {
  background: rgba(148, 163, 184, 0.1);
  border-color: rgba(148, 163, 184, 0.22);
  color: var(--text-soft);
}

.article-status-chip.status-pending,
.article-status-chip.status-pending_review {
  background: rgba(234, 154, 24, 0.1);
  border-color: rgba(234, 154, 24, 0.22);
  color: #d97706;
}

.article-status-chip.status-rejected {
  background: rgba(227, 91, 119, 0.1);
  border-color: rgba(227, 91, 119, 0.22);
  color: var(--danger);
}

.article-page-btn {
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(148, 163, 184, 0.08);
  color: var(--text-soft);
  min-height: 38px;
  border-radius: 14px;
  padding: 0 16px;
}

.article-page-btn:hover {
  background: rgba(148, 163, 184, 0.14);
  color: var(--text);
}
</style>
