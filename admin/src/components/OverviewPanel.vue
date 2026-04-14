<template>
  <section class="grid-panels overview-panels">
    <div class="panel overview-panel">
      <div class="overview-head">
        <div>
          <h3>文章概览</h3>
          <p class="tips">共 {{ articles.length }} 篇文章，垃圾箱 {{ deletedArticles.length }} 篇</p>
        </div>
        <p v-if="loading" class="tips">正在同步后台数据...</p>
        <p v-else-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </div>

      <ul class="overview-list">
        <li v-for="item in articles.slice(0, 5)" :key="item.id" class="overview-row">
          <div class="overview-main">
            <p class="overview-title">{{ item.title }}</p>
            <small class="overview-meta">
              {{ item.category?.name || '未分类' }}
              · {{ item.author?.nickname || 'admin' }}
              · {{ formatRelativeTime(item.published_at || item.created_at) }}
            </small>
          </div>
          <div class="overview-stats">
            <span>{{ item.view_count || 0 }} 浏览</span>
            <span>{{ item.comment_count || 0 }} 评论</span>
          </div>
        </li>
      </ul>
    </div>

    <div class="panel overview-panel">
      <h3>评论概览</h3>
      <p class="tips">共 {{ comments.length }} 条评论</p>
      <ul class="overview-list">
        <li v-for="item in comments.slice(0, 5)" :key="item.id" class="overview-row overview-comment-row">
          <div class="overview-main">
            <p class="overview-title">{{ item.content }}</p>
            <small class="overview-meta">
              {{ item.article?.title || '未知文章' }}
              · {{ item.user?.nickname || item.guest_nickname || '匿名访客' }}
              · {{ formatRelativeTime(item.created_at) }}
            </small>
          </div>
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  articles: any[]
  deletedArticles: any[]
  comments: any[]
  loading: boolean
  errorMessage: string
  formatArticleStatus: (status: string) => string
}>()

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
