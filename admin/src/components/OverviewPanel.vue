<template>
  <section class="grid-panels overview-panels">
    <div class="panel overview-panel overview-articles-panel">
      <div class="overview-head">
        <h3>{{ t('overview.articleStats') }}</h3>
        <p v-if="loading" class="tips">{{ t('overview.loadingTip') }}</p>
        <p v-else-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </div>

      <div class="overview-metrics">
        <div class="overview-metric">
          <span class="overview-metric-value">{{ publishedCount }}</span>
          <span class="overview-metric-label">{{ t('status.published') }}</span>
        </div>
        <div class="overview-metric">
          <span class="overview-metric-value">{{ draftCount }}</span>
          <span class="overview-metric-label">{{ t('status.draft') }}</span>
        </div>
        <div class="overview-metric">
          <span class="overview-metric-value">{{ pendingCount }}</span>
          <span class="overview-metric-label">{{ t('status.pending') }}</span>
        </div>
        <div class="overview-metric">
          <span class="overview-metric-value">{{ rejectedCount }}</span>
          <span class="overview-metric-label">{{ t('status.rejected') }}</span>
        </div>
        <div class="overview-metric">
          <span class="overview-metric-value">{{ deletedArticles.length }}</span>
          <span class="overview-metric-label">{{ t('status.trash') }}</span>
        </div>
      </div>
    </div>

    <div class="panel overview-panel overview-comments-panel">
      <h3>{{ t('overview.commentStats') }}</h3>
      <div class="overview-metrics comments-metrics">
        <div class="overview-metric">
          <span class="overview-metric-value">{{ approvedCommentCount }}</span>
          <span class="overview-metric-label">{{ t('status.approved') }}</span>
        </div>
        <div class="overview-metric">
          <span class="overview-metric-value">{{ pendingCommentCount }}</span>
          <span class="overview-metric-label">{{ t('status.pending') }}</span>
        </div>
        <div class="overview-metric">
          <span class="overview-metric-value">{{ rejectedCommentCount }}</span>
          <span class="overview-metric-label">{{ t('status.rejectedComment') }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps<{
  articles: any[]
  deletedArticles: any[]
  comments: any[]
  loading: boolean
  errorMessage: string
  formatArticleStatus: (status: string) => string
}>()

const normalizeStatus = (status: string) => String(status || '').trim().toLowerCase()

const pendingCount = computed(() =>
  props.articles.filter((item) => ['pending', 'pending_review'].includes(normalizeStatus(item.status))).length,
)

const draftCount = computed(() =>
  props.articles.filter((item) => normalizeStatus(item.status) === 'draft').length,
)

const publishedCount = computed(() =>
  props.articles.filter((item) => normalizeStatus(item.status) === 'published').length,
)

const rejectedCount = computed(() =>
  props.articles.filter((item) => normalizeStatus(item.status) === 'rejected').length,
)

const normalizeCommentStatus = (status: string) => String(status || '').trim().toLowerCase()

const approvedCommentCount = computed(() =>
  props.comments.filter((item) => normalizeCommentStatus(item.status) === 'approved').length,
)

const pendingCommentCount = computed(() =>
  props.comments.filter((item) => normalizeCommentStatus(item.status) === 'pending').length,
)

const rejectedCommentCount = computed(() =>
  props.comments.filter((item) => normalizeCommentStatus(item.status) === 'rejected').length,
)
</script>
