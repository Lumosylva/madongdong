<template>
  <section class="panel friend-links-panel">
    <div class="article-manage-head">
      <div>
        <h3>友链管理</h3>
        <p class="comments-subtitle">审核友情链接申请，并管理已收录站点</p>
      </div>
      <span class="article-count comments-count">共 {{ links.length }} 条</span>
    </div>

    <div class="action-row comments-filter-row">
      <select class="article-filter-select comments-filter-select" v-model="statusFilter">
        <option value="all">全部状态</option>
        <option value="approved">已通过</option>
        <option value="pending">待审核</option>
        <option value="rejected">已拒绝</option>
      </select>
      <button class="article-reset-btn" type="button" @click="refresh">刷新</button>
    </div>

    <div class="comments-list friend-links-list">
      <article v-for="item in filteredLinks" :key="item.id" class="comments-card friend-link-card" :class="`status-${item.status}`">
        <div class="comments-card-main">
          <div class="comments-card-headline">
            <p class="comments-content">{{ item.name }}</p>
            <span class="comments-status-badge" :class="`status-${item.status}`">{{ statusText(item.status) }}</span>
          </div>
          <a class="comments-article-link comments-article-title" :href="item.url" target="_blank" rel="noreferrer">{{ item.url }}</a>
          <div class="comments-meta friend-link-meta">
            <span>描述：{{ item.description }}</span>
            <span>邮箱：{{ item.email }}</span>
            <span>来源：{{ item.source }}</span>
            <span>时间：{{ formatTime(item.created_at) }}</span>
          </div>
        </div>
        <div class="comments-actions friend-link-actions">
          <button v-if="item.status !== 'approved'" type="button" @click="$emit('approve', item.id)">通过</button>
          <button v-if="item.status !== 'rejected'" type="button" class="danger-btn" @click="$emit('reject', item.id)">拒绝</button>
          <button type="button" class="danger-btn" @click="$emit('delete', item.id)">删除</button>
        </div>
      </article>
      <p v-if="!filteredLinks.length" class="comments-empty">暂无符合条件的友链</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{ links: any[] }>()
const statusFilter = ref<'all' | 'approved' | 'pending' | 'rejected'>('all')

const filteredLinks = computed(() => props.links.filter((item) => statusFilter.value === 'all' ? true : String(item.status).toLowerCase() === statusFilter.value))
const statusText = (value: string) => {
  const map: Record<string, string> = { approved: '已通过', pending: '待审核', rejected: '已拒绝' }
  return map[String(value).toLowerCase()] || value
}
const formatTime = (value: string) => String(value || '').replace('T', ' ').slice(0, 19)
const refresh = () => window.location.reload()
</script>
