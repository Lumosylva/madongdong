<template>
  <section class="panel">
    <h3>评论管理</h3>
    <ul>
      <li v-for="item in comments" :key="item.id" class="article-row">
        <div>
          <p>
            {{ item.content }}
            <template v-if="item.article?.id">
              -
              <a :href="webArticleUrl(item.article.id)" target="_blank" rel="noreferrer">
                {{ truncateText(item.article.title, 50) }}
              </a>
            </template>
          </p>
          <small>
            昵称：{{ item.user?.nickname || item.guest_nickname || '匿名访客' }}
            ｜ 邮箱：{{ item.guest_email || '-' }}
            ｜ 时间：<span :title="formatDateTime(item.created_at)">{{ formatRelativeTime(item.created_at) }}</span>
            ｜ 状态：{{ formatCommentStatus(item.status) }}
          </small>
        </div>
        <div class="row-actions">
          <button :disabled="isApproved(item.status)" @click="$emit('approve', item.id)">通过</button>
          <button class="danger-btn" :disabled="isRejected(item.status)" @click="$emit('reject', item.id)">拒绝</button>
        </div>
      </li>
    </ul>
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

const formatDateTime = (value: string) => new Date(value).toLocaleString('zh-CN')

const formatRelativeTime = (value: string) => {
  const date = new Date(value)
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
