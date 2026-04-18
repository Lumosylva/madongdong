<template>
  <section class="panel comments-panel">
    <div class="article-manage-head comments-head">
      <div>
        <h3>评论管理</h3>
        <p class="comments-subtitle">集中审核文章评论，维护社区内容质量</p>
      </div>
      <span class="article-count comments-count">共 {{ comments.length }} 条</span>
    </div>

    <div class="comments-list">
      <article v-for="item in comments" :key="item.id" class="comments-card" :class="[
        `status-${String(item.status || '').toLowerCase()}`,
        { 'is-approved': isApproved(item.status), 'is-rejected': isRejected(item.status), 'is-pending': !isApproved(item.status) && !isRejected(item.status) },
      ]">
        <div class="comments-card-main">
          <p class="comments-content">
            {{ item.content }}
            <template v-if="item.article?.id">
              <span class="comments-content-separator">·</span>
              <a class="comments-article-link" :href="webArticleUrl(item.article.id)" target="_blank" rel="noreferrer">
                {{ truncateText(item.article.title, 50) }}
              </a>
            </template>
          </p>
          <div class="comments-meta">
            <span>昵称：{{ item.user?.nickname || item.guest_nickname || '匿名访客' }}</span>
            <span>邮箱：{{ item.guest_email || '-' }}</span>
            <span>时间：<span :title="formatDateTime(item.created_at)">{{ formatRelativeTime(item.created_at) }}</span></span>
            <span class="comments-status">状态：{{ formatCommentStatus(item.status) }}</span>
          </div>
        </div>
        <div class="comments-actions">
          <button v-if="!isApproved(item.status) && !isRejected(item.status)" @click="$emit('approve', item.id)">通过</button>
          <button v-if="!isRejected(item.status)" class="danger-btn" @click="$emit('reject', item.id)">拒绝</button>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  comments: any[]
  formatCommentStatus: (status: string) => string
}>()

defineEmits<{
  approve: [commentId: number]
  reject: [commentId: number]
}>()

const isApproved = (status: string) => String(status || '').toUpperCase() === 'APPROVED'
const isRejected = (status: string) => String(status || '').toUpperCase() === 'REJECTED'

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
