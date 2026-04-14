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
      <li v-for="item in displayArticles" :key="item.id" class="article-row">
        <div class="article-row-main">
          <p class="article-row-title">
            <span v-html="highlightTitle(item.title)"></span>
            <span class="article-status-chip">{{ formatArticleStatus(item.status) }}</span>
          </p>
          <small class="article-row-meta">
            分类：{{ item.category?.name || '未分类' }}
            ｜ 作者：{{ item.author?.nickname || 'admin' }}
            ｜ 发布时间：{{ formatRelativeTime(item.published_at || item.created_at) }}
            ｜ 流量：{{ item.view_count || 0 }}
            ｜ 评论：{{ item.comment_count || 0 }}
          </small>
        </div>
        <button class="danger-btn" @click="$emit('move-to-trash', item.id)">删除</button>
      </li>

      <li v-if="!displayArticles.length" class="article-empty">暂无符合条件的文章</li>
    </ul>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{
  articles: any[]
  formatArticleStatus: (status: string) => string
}>()

defineEmits<{
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

const resetFilters = () => {
  keyword.value = ''
  statusFilter.value = 'all'
  sortOrder.value = 'newest'
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
</style>
