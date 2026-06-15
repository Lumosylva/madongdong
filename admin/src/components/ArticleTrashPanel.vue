<template>
  <section class="panel article-trash-panel">
    <div class="article-manage-head article-trash-head">
      <div class="article-trash-head-main">
        <h3>{{ t('articleTrash.title') }}</h3>
        <p class="article-trash-subtitle">{{ t('articleTrash.subtitle') }}</p>
      </div>
      <span class="article-count article-trash-count">{{ t('articleTrash.count', { n: deletedArticles.length }) }}</span>
    </div>

    <p class="tips article-empty" v-if="displayDeletedArticles.length === 0">{{ t('articleTrash.empty') }}</p>

    <ul v-else class="article-manage-list article-trash-list">
      <li v-for="item in pagedDeletedArticles" :key="item.id" class="article-row article-trash-row">
        <div class="article-row-main article-trash-main">
          <p class="article-row-title article-trash-title">{{ item.title }}</p>
          <small class="article-row-meta article-trash-meta">
            <span>{{ t('articleMeta.category') }}{{ item.category?.name || t('articleMeta.uncategorized') }}</span>
            <span>{{ t('articleMeta.author') }}{{ item.author?.nickname || 'admin' }}</span>
            <span>{{ t('articleMeta.published') }}{{ formatRelativeTime(item.published_at || item.created_at) }}</span>
            <span>{{ t('articleMeta.views') }}{{ item.view_count || 0 }}</span>
            <span>{{ t('articleMeta.comments') }}{{ item.comment_count || 0 }}</span>
          </small>
          <div class="article-trash-time-row">
            <span class="article-trash-time-chip">{{ t('time.deletedAt') }}{{ formatRelativeTime(item.deleted_at || item.updated_at || item.created_at) }}</span>
          </div>
        </div>
        <div class="article-trash-actions">
          <button class="article-trash-restore-btn" @click="$emit('restore', item.id)">{{ t('articleTrash.restore') }}</button>
          <button class="article-trash-delete-btn" @click="$emit('remove-permanently', item.id)">{{ t('articleTrash.permanentDelete') }}</button>
        </div>
      </li>
    </ul>

    <div class="article-pagination article-trash-pagination">
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

import '../styles/article-trash.css'

const { t } = useI18n()

const props = defineProps<{
  deletedArticles: any[]
}>()

defineEmits<{
  restore: [articleId: number]
  'remove-permanently': [articleId: number]
}>()

const pageSizeOptions = [10, 20, 50]
const pageSize = ref(10)
const currentPage = ref(1)

const displayDeletedArticles = computed(() => [...(props.deletedArticles || [])])

const totalPages = computed(() => Math.max(1, Math.ceil(displayDeletedArticles.value.length / pageSize.value)))
const pagedDeletedArticles = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return displayDeletedArticles.value.slice(start, start + pageSize.value)
})

const canGoPrev = computed(() => currentPage.value > 1)
const canGoNext = computed(() => currentPage.value < totalPages.value)
const formatPageLabel = computed(() => t('articleManage.pageInfo', { current: currentPage.value, total: totalPages.value }))

const changePageSize = () => {
  currentPage.value = 1
}

const goPrevPage = () => {
  if (canGoPrev.value) currentPage.value -= 1
}

const goNextPage = () => {
  if (canGoNext.value) currentPage.value += 1
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
