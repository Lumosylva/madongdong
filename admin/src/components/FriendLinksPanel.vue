<template>
  <section class="panel friend-links-panel">
    <div class="friend-links-panel-head">
      <div>
        <h3>友链管理</h3>
        <p class="friend-links-panel-subtitle">审核友情链接申请，并管理已收录站点</p>
      </div>
      <div class="friend-links-panel-stats">
        <span>共 {{ links.length }} 条</span>
        <span class="friend-links-panel-stat-pill">{{ filteredLinks.length }} 条当前筛选</span>
      </div>
    </div>

    <div class="friend-links-toolbar">
      <select class="article-filter-select comments-filter-select" v-model="statusFilter" aria-label="筛选友链状态">
        <option value="all">全部状态</option>
        <option value="approved">已通过</option>
        <option value="pending">待审核</option>
        <option value="rejected">已拒绝</option>
      </select>
      <button class="article-reset-btn" type="button" @click="refresh">刷新</button>
    </div>

    <div class="friend-links-table-wrap">
      <div class="friend-links-table-head">
        <span>站点</span>
        <span>信息</span>
        <span>状态</span>
        <span>操作</span>
      </div>

      <div class="friend-links-table-body">
        <article v-for="item in filteredLinks" :key="item.id" class="friend-links-row" :class="`status-${item.status}`">
          <div class="friend-links-site-col">
            <div class="friend-links-avatar">{{ item.name.slice(0, 1) }}</div>
            <div class="friend-links-site-text">
              <strong>{{ item.name }}</strong>
              <a :href="item.url" target="_blank" rel="noreferrer">{{ item.url }}</a>
            </div>
          </div>

          <div class="friend-links-info-col">
            <p class="friend-links-description">{{ item.description }}</p>
            <div class="friend-links-meta">
              <span>邮箱：{{ item.email }}</span>
              <span>来源：{{ item.source }}</span>
              <span>时间：{{ formatTime(item.created_at) }}</span>
            </div>
          </div>

          <div class="friend-links-status-col">
            <span class="comments-status-badge" :class="`status-${item.status}`">{{ statusText(item.status) }}</span>
          </div>

          <div class="friend-links-actions-col">
            <button v-if="item.status !== 'approved'" type="button" @click="$emit('approve', item.id)">通过</button>
            <button v-if="item.status !== 'rejected'" type="button" class="danger-btn" @click="$emit('reject', item.id)">拒绝</button>
            <button type="button" class="danger-btn" @click="$emit('delete', item.id)">删除</button>
          </div>
        </article>
      </div>

      <p v-if="!filteredLinks.length" class="comments-empty friend-links-empty-state">暂无符合条件的友链</p>
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
  gap: 16px;
}

.friend-links-panel-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.friend-links-panel h3 {
  margin: 0;
  font-size: 22px;
}

.friend-links-panel-subtitle {
  margin: 8px 0 0;
  color: var(--text-soft);
}

.friend-links-panel-stats {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  justify-content: flex-end;
  color: var(--text-soft);
  font-size: 13px;
}

.friend-links-panel-stat-pill {
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--bg-soft);
  border: 1px solid var(--line);
  color: var(--text);
}

.friend-links-toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.friend-links-table-wrap {
  display: grid;
  gap: 12px;
}

.friend-links-table-head {
  display: grid;
  grid-template-columns: 1.15fr 2fr 0.7fr 0.95fr;
  gap: 12px;
  padding: 0 14px;
  color: var(--text-soft);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.friend-links-table-body {
  display: grid;
  gap: 12px;
}

.friend-links-row {
  display: grid;
  grid-template-columns: 1.15fr 2fr 0.7fr 0.95fr;
  gap: 12px;
  align-items: center;
  padding: 16px 14px;
  border-radius: 18px;
  background: var(--bg-soft);
  border: 1px solid var(--line);
}

.friend-links-row:hover {
  border-color: rgba(14, 165, 164, 0.25);
}

.friend-links-site-col {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.friend-links-avatar {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  font-weight: 800;
  color: #05131d;
  background: linear-gradient(135deg, var(--accent), #93c5fd);
  flex: 0 0 auto;
}

.friend-links-site-text {
  min-width: 0;
  display: grid;
  gap: 4px;
}

.friend-links-site-text strong {
  font-size: 15px;
}

.friend-links-site-text a {
  color: var(--text-soft);
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.friend-links-info-col {
  min-width: 0;
  display: grid;
  gap: 8px;
}

.friend-links-description {
  margin: 0;
  color: var(--text);
  line-height: 1.6;
}

.friend-links-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 14px;
  color: var(--text-soft);
  font-size: 12px;
}

.friend-links-status-col {
  display: flex;
  justify-content: flex-start;
}

.friend-links-actions-col {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 8px;
}

.friend-links-actions-col button {
  border: 1px solid var(--line);
  background: var(--bg-panel);
  color: var(--text);
  border-radius: 999px;
  padding: 8px 12px;
}

.friend-links-actions-col .danger-btn {
  border-color: rgba(239, 68, 68, 0.2);
}

.friend-links-empty-state {
  padding: 20px 0 4px;
}

@media (max-width: 1080px) {
  .friend-links-table-head {
    display: none;
  }

  .friend-links-row {
    grid-template-columns: 1fr;
    align-items: start;
  }

  .friend-links-status-col,
  .friend-links-actions-col {
    justify-content: flex-start;
  }
}

@media (max-width: 640px) {
  .friend-links-panel-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .friend-links-actions-col {
    width: 100%;
  }

  .friend-links-actions-col button {
    flex: 1 1 auto;
  }
}
</style>
