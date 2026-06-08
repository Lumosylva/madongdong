<template>
  <section class="panel friend-links-panel">
    <div class="article-manage-head comments-head friend-links-head">
      <div>
        <h3>友链管理</h3>
        <p class="comments-subtitle">审核友情链接申请，并管理已收录站点</p>
      </div>
      <span class="article-count comments-count">共 {{ links.length }} 条</span>
    </div>

    <div class="action-row comments-filter-row friend-links-filter-row">
      <select class="article-filter-select comments-filter-select" v-model="statusFilter" aria-label="筛选友链状态">
        <option value="all">全部状态</option>
        <option value="approved">已通过</option>
        <option value="pending">待审核</option>
        <option value="rejected">已拒绝</option>
      </select>
      <button class="article-reset-btn" type="button" @click="refresh">刷新</button>
    </div>

    <div class="comments-list friend-links-list">
      <article
        v-for="item in filteredLinks"
        :key="item.id"
        class="comments-card friend-link-card"
        :class="[`status-${item.status}`, { 'is-approved': item.status === 'approved', 'is-rejected': item.status === 'rejected', 'is-pending': item.status === 'pending' } ]"
      >
        <div class="comments-card-main friend-links-card-main">
          <div class="comments-card-headline friend-links-card-headline">
            <div class="friend-links-site-title">
              <strong>{{ item.name }}</strong>
              <a :href="item.url" target="_blank" rel="noreferrer">{{ item.url }}</a>
            </div>
            <span class="comments-status-badge" :class="`status-${item.status}`">{{ statusText(item.status) }}</span>
          </div>

          <p class="comments-content friend-links-description">{{ item.description }}</p>

          <div class="comments-meta friend-links-meta">
            <span>邮箱：{{ item.email }}</span>
            <span>来源：{{ item.source }}</span>
            <span>时间：{{ formatTime(item.created_at) }}</span>
          </div>
        </div>

        <div class="comments-actions friend-links-actions">
          <button v-if="item.status !== 'approved'" type="button" @click="$emit('approve', item.id)">通过</button>
          <button v-if="item.status !== 'rejected'" type="button" class="danger-btn" @click="$emit('reject', item.id)">拒绝</button>
          <button type="button" class="danger-btn" @click="$emit('delete', item.id)">删除</button>
        </div>
      </article>

      <p v-if="!filteredLinks.length" class="comments-empty friend-links-empty">暂无符合条件的友链</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{ links: any[] }>()
const statusFilter = ref<'all' | 'approved' | 'pending' | 'rejected'>('all')

const filteredLinks = computed(() =>
  props.links.filter((item) =>
    statusFilter.value === 'all' ? true : String(item.status).toLowerCase() === statusFilter.value,
  ),
)
const statusText = (value: string) => {
  const map: Record<string, string> = { approved: '已通过', pending: '待审核', rejected: '已拒绝' }
  return map[String(value).toLowerCase()] || value
}
const formatTime = (value: string) => String(value || '').replace('T', ' ').slice(0, 19)
const refresh = () => window.location.reload()
</script>

<style scoped>
.friend-links-panel {
  display: grid;
  gap: 10px;
}

.friend-links-head {
  margin-bottom: 0;
}

.friend-links-filter-row {
  grid-template-columns: minmax(0, 2.8fr) auto;
  margin-top: -2px;
}

.friend-links-list {
  display: grid;
  gap: 10px;
}

.friend-link-card {
  grid-template-columns: minmax(0, 1fr) auto;
  padding: 14px 14px 14px 10px;
}

.friend-links-card-main {
  gap: 10px;
}

.friend-links-card-headline {
  align-items: flex-start;
}

.friend-links-site-title {
  display: grid;
  gap: 4px;
  min-width: 0;
}

.friend-links-site-title strong {
  font-size: 15px;
  line-height: 1.4;
}

.friend-links-site-title a {
  color: var(--text-soft);
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.friend-links-description {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.friend-links-meta {
  gap: 8px 12px;
}

.friend-links-actions {
  align-items: center;
}

.friend-links-actions button {
  min-height: 32px;
  border-radius: 10px;
  padding: 0 12px;
}

.friend-links-empty {
  padding: 18px 16px;
}

@media (max-width: 900px) {
  .friend-link-card {
    grid-template-columns: 1fr;
  }

  .friend-links-actions {
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}

@media (max-width: 640px) {
  .friend-links-panel {
    gap: 8px;
  }

  .friend-links-filter-row {
    grid-template-columns: 1fr;
    margin-top: 0;
  }
}
</style>
