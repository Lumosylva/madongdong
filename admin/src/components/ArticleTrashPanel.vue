<template>
  <section class="panel article-trash-panel">
    <div class="article-manage-head article-trash-head">
      <div class="article-trash-head-main">
        <h3>垃圾箱</h3>
        <p class="article-trash-subtitle">这里的文章可恢复，也可彻底删除</p>
      </div>
      <span class="article-count article-trash-count">共 {{ deletedArticles.length }} 篇</span>
    </div>

    <p class="tips article-empty" v-if="deletedArticles.length === 0">垃圾箱为空</p>

    <ul v-else class="article-manage-list article-trash-list">
      <li v-for="item in deletedArticles" :key="item.id" class="article-row article-trash-row">
        <div class="article-row-main article-trash-main">
          <p class="article-row-title article-trash-title">{{ item.title }}</p>
          <small class="article-row-meta article-trash-meta">
            <span>分类：{{ item.category?.name || '未分类' }}</span>
            <span>作者：{{ item.author?.nickname || 'admin' }}</span>
            <span>发布时间：{{ formatRelativeTime(item.published_at || item.created_at) }}</span>
            <span>浏览：{{ item.view_count || 0 }}</span>
            <span>评论：{{ item.comment_count || 0 }}</span>
          </small>
          <div class="article-trash-time-row">
            <span class="article-trash-time-chip">删除时间：{{ formatRelativeTime(item.deleted_at || item.updated_at || item.created_at) }}</span>
          </div>
        </div>
        <div class="article-trash-actions">
          <button class="article-trash-restore-btn" @click="$emit('restore', item.id)">恢复</button>
          <button class="article-trash-delete-btn" @click="$emit('remove-permanently', item.id)">彻底删除</button>
        </div>
      </li>
    </ul>
  </section>
</template>

<script setup lang="ts">
import '../styles/article-trash.css'

defineProps<{
  deletedArticles: any[]
}>()

defineEmits<{
  restore: [articleId: number]
  'remove-permanently': [articleId: number]
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
