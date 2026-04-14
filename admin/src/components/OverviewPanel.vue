<template>
  <section class="grid-panels overview-panels">
    <div class="panel overview-panel overview-articles-panel">
      <div class="overview-head">
        <h3>文章统计</h3>
        <p v-if="loading" class="tips">正在同步后台数据...</p>
        <p v-else-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </div>

      <div class="overview-metrics">
        <div class="overview-metric">
          <span class="overview-metric-value">{{ publishedCount }}</span>
          <span class="overview-metric-label">已发布</span>
        </div>
        <div class="overview-metric">
          <span class="overview-metric-value">{{ draftCount }}</span>
          <span class="overview-metric-label">草稿</span>
        </div>
        <div class="overview-metric">
          <span class="overview-metric-value">{{ pendingCount }}</span>
          <span class="overview-metric-label">待审核</span>
        </div>
        <div class="overview-metric">
          <span class="overview-metric-value">{{ rejectedCount }}</span>
          <span class="overview-metric-label">已驳回</span>
        </div>
        <div class="overview-metric">
          <span class="overview-metric-value">{{ deletedArticles.length }}</span>
          <span class="overview-metric-label">垃圾箱</span>
        </div>
      </div>
    </div>

    <div class="panel overview-panel overview-comments-panel">
      <h3>评论统计</h3>
      <div class="overview-metrics comments-metrics">
        <div class="overview-metric">
          <span class="overview-metric-value">{{ approvedCommentCount }}</span>
          <span class="overview-metric-label">已通过</span>
        </div>
        <div class="overview-metric">
          <span class="overview-metric-value">{{ pendingCommentCount }}</span>
          <span class="overview-metric-label">待审核</span>
        </div>
        <div class="overview-metric">
          <span class="overview-metric-value">{{ rejectedCommentCount }}</span>
          <span class="overview-metric-label">已拒绝</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'

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
