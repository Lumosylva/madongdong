<template>
  <section class="grid-panels overview-panels">
    <div class="panel overview-panel overview-articles-panel">
      <div class="overview-head">
        <div>
          <h3>文章概览</h3>
          <p class="tips">文章统计</p>
        </div>
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
      <h3>评论概览</h3>
      <p class="tips">共 {{ comments.length }} 条评论</p>
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
</script>
