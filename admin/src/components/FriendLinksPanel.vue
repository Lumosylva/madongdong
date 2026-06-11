<template>
  <section class="panel fl-panel">
    <div class="fl-head">
      <div>
        <h3>友链管理</h3>
        <p class="fl-subtitle">审核友情链接申请，并管理已收录站点</p>
      </div>
      <span class="fl-count">共 {{ filteredLinks.length }} 条</span>
    </div>

    <div class="fl-toolbar">
      <input
        class="fl-search"
        v-model="keyword"
        placeholder="搜索站点名称、URL 或描述"
        aria-label="搜索友链"
      />
      <select class="fl-select" v-model="statusFilter" aria-label="筛选友链状态">
        <option value="all">全部状态</option>
        <option value="approved">已通过</option>
        <option value="pending">待审核</option>
        <option value="rejected">已拒绝</option>
      </select>
      <button class="fl-refresh-btn" type="button" @click="refresh">刷新</button>
    </div>

    <div class="fl-list">
      <article
        v-for="item in filteredLinks"
        :key="item.id"
        class="fl-card"
        :class="[`status-${item.status}`]"
      >
        <div class="fl-card-top">
          <div class="fl-avatar" :style="{ background: avatarColor(item.name) }">
            {{ avatarLetter(item.name) }}
          </div>
          <div class="fl-site-info">
            <div class="fl-site-head">
              <strong class="fl-site-name">{{ item.name }}</strong>
              <span class="fl-badge" :class="`status-${item.status}`">{{ statusText(item.status) }}</span>
            </div>
            <a class="fl-url" :href="item.url" target="_blank" rel="noreferrer" :title="item.url">{{ item.url }}</a>
          </div>
        </div>

        <p class="fl-desc">{{ item.description || '暂无描述' }}</p>

        <div class="fl-card-bottom">
          <div class="fl-meta">
            <span class="fl-meta-item">
              <span class="fl-meta-label">邮箱</span>
              {{ item.email || '-' }}
            </span>
            <span class="fl-meta-item">
              <span class="fl-meta-label">来源</span>
              {{ item.source || '-' }}
            </span>
            <span class="fl-meta-item">
              <span class="fl-meta-label">申请时间</span>
              {{ formatTime(item.created_at) }}
            </span>
          </div>
          <div class="fl-actions">
            <button
              v-if="item.status !== 'approved'"
              type="button"
              class="fl-btn fl-btn-approve"
              @click="$emit('approve', item.id)"
            >通过</button>
            <button
              v-if="item.status !== 'rejected'"
              type="button"
              class="fl-btn fl-btn-reject"
              @click="$emit('reject', item.id)"
            >拒绝</button>
            <button
              type="button"
              class="fl-btn fl-btn-delete"
              @click="$emit('delete', item.id)"
            >删除</button>
          </div>
        </div>
      </article>

      <p v-if="!filteredLinks.length" class="fl-empty">暂无符合条件的友链</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{ links: any[] }>()

const keyword = ref('')
const statusFilter = ref<'all' | 'approved' | 'pending' | 'rejected'>('all')

const filteredLinks = computed(() => {
  const key = keyword.value.trim().toLowerCase()
  return props.links.filter((item) => {
    const statusMatch = statusFilter.value === 'all' || String(item.status).toLowerCase() === statusFilter.value
    if (!statusMatch) return false
    if (!key) return true
    return (
      String(item.name || '').toLowerCase().includes(key) ||
      String(item.url || '').toLowerCase().includes(key) ||
      String(item.description || '').toLowerCase().includes(key) ||
      String(item.email || '').toLowerCase().includes(key)
    )
  })
})

const statusText = (value: string) => {
  const map: Record<string, string> = { approved: '已通过', pending: '待审核', rejected: '已拒绝' }
  return map[String(value).toLowerCase()] || value
}

const formatTime = (value: string) => String(value || '').replace('T', ' ').slice(0, 19)

const refresh = () => window.location.reload()

const AVATAR_COLORS = [
  '#0ea5a4', '#3b82f6', '#8b5cf6', '#ec4899', '#f97316',
  '#14b8a6', '#6366f1', '#a855f7', '#e11d48', '#f59e0b',
  '#06b6d4', '#8b5cf6', '#d946ef', '#ef4444', '#eab308',
]

const hashCode = (str: string) => {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash + str.charCodeAt(i)) | 0
  }
  return Math.abs(hash)
}

const avatarLetter = (name: string) => {
  const s = String(name || '').trim()
  if (!s) return '?'
  const ch = s[0]
  if (ch === '#' || ch === '/') return s.length > 1 ? s[1].toUpperCase() : '?'
  return ch.toUpperCase()
}

const avatarColor = (name: string) => AVATAR_COLORS[hashCode(String(name || '')) % AVATAR_COLORS.length]
</script>

<style scoped>
.fl-panel {
  display: grid;
  gap: 14px;
  min-width: 0;
}

.fl-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 4px 2px 2px;
}

.fl-head h3 {
  margin: 0;
  font-size: 22px;
  letter-spacing: 0.01em;
  line-height: 1.15;
}

.fl-subtitle {
  margin: 4px 0 0;
  color: var(--text-soft);
  font-size: 13px;
  line-height: 1.45;
}

.fl-count {
  flex: 0 0 auto;
  padding: 7px 12px;
  border-radius: 999px;
  border: 1px solid rgba(14, 165, 164, 0.14);
  background: rgba(14, 165, 164, 0.06);
  color: var(--text-soft);
  font-size: 13px;
  line-height: 1;
  white-space: nowrap;
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.55) inset;
}

.fl-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 180px auto;
  gap: 14px;
  align-items: center;
}

.fl-search {
  min-width: 0;
  width: 100%;
  min-height: 46px;
  border-radius: 13px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(255, 255, 255, 0.72);
  color: var(--text);
  padding: 0 14px;
  font-size: 14px;
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.6) inset, 0 6px 16px rgba(16, 35, 63, 0.04);
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease, background 0.18s ease;
}

.fl-search::placeholder {
  color: color-mix(in srgb, var(--text-soft) 70%, white);
}

.fl-search:hover {
  border-color: rgba(14, 165, 164, 0.3);
  background: rgba(255, 255, 255, 0.84);
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.72) inset, 0 10px 20px rgba(16, 35, 63, 0.06);
}

.fl-search:focus {
  outline: none;
  border-color: rgba(14, 165, 164, 0.6);
  box-shadow: 0 0 0 3px rgba(14, 165, 164, 0.16);
  transform: translateY(-1px);
}

.fl-select {
  min-height: 46px;
  border-radius: 13px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(255, 255, 255, 0.72);
  color: var(--text);
  padding: 0 14px;
  font-size: 14px;
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.6) inset, 0 6px 16px rgba(16, 35, 63, 0.04);
  appearance: none;
  background-image:
    linear-gradient(45deg, transparent 50%, var(--text-soft) 50%),
    linear-gradient(135deg, var(--text-soft) 50%, transparent 50%);
  background-position: calc(100% - 18px) 18px, calc(100% - 12px) 18px;
  background-size: 6px 6px, 6px 6px;
  background-repeat: no-repeat;
  padding-right: 34px;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease, background 0.18s ease;
}

.fl-select:hover {
  border-color: rgba(14, 165, 164, 0.3);
  background: rgba(255, 255, 255, 0.84);
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.72) inset, 0 10px 20px rgba(16, 35, 63, 0.06);
}

.fl-select:focus {
  outline: none;
  border-color: rgba(14, 165, 164, 0.6);
  box-shadow: 0 0 0 3px rgba(14, 165, 164, 0.16);
  transform: translateY(-1px);
}

.fl-refresh-btn {
  min-height: 46px;
  border-radius: 13px;
  padding: 0 16px;
  font-weight: 600;
  border: 1px solid rgba(14, 165, 164, 0.18);
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.1), rgba(234, 154, 24, 0.08));
  color: var(--text);
  box-shadow: 0 8px 18px rgba(16, 35, 63, 0.05);
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease, background 0.18s ease;
}

.fl-refresh-btn:hover {
  transform: translateY(-1px);
  border-color: rgba(14, 165, 164, 0.34);
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.14), rgba(234, 154, 24, 0.12));
  box-shadow: 0 10px 22px rgba(16, 35, 63, 0.08);
}

.fl-list {
  display: grid;
  gap: 10px;
}

.fl-card {
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 6px 16px rgba(16, 35, 63, 0.04);
  display: grid;
  gap: 12px;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.fl-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(16, 35, 63, 0.08);
}

.fl-card.status-pending {
  border-color: rgba(234, 154, 24, 0.24);
  background: linear-gradient(135deg, rgba(234, 154, 24, 0.06), rgba(255, 255, 255, 0.72));
}

.fl-card.status-approved {
  border-color: rgba(16, 185, 129, 0.24);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.06), rgba(255, 255, 255, 0.72));
}

.fl-card.status-rejected {
  border-color: rgba(227, 91, 119, 0.24);
  background: linear-gradient(135deg, rgba(227, 91, 119, 0.06), rgba(255, 255, 255, 0.72));
}

.fl-card-top {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.fl-avatar {
  flex: 0 0 auto;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  line-height: 1;
  user-select: none;
}

.fl-site-info {
  min-width: 0;
  display: grid;
  gap: 2px;
  flex: 1 1 auto;
}

.fl-site-head {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.fl-site-name {
  font-size: 15px;
  line-height: 1.4;
}

.fl-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 22px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  border: 1px solid transparent;
  box-shadow: 0 4px 10px rgba(16, 35, 63, 0.06);
}

.fl-badge.status-approved {
  background: rgba(16, 185, 129, 0.12);
  border-color: rgba(16, 185, 129, 0.24);
  color: #0f766e;
}

.fl-badge.status-pending {
  background: rgba(234, 154, 24, 0.12);
  border-color: rgba(234, 154, 24, 0.24);
  color: #b45309;
}

.fl-badge.status-rejected {
  background: rgba(227, 91, 119, 0.12);
  border-color: rgba(227, 91, 119, 0.24);
  color: #be123c;
}

.fl-url {
  display: block;
  color: var(--accent);
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  opacity: 0.82;
  transition: opacity 0.15s ease;
}

.fl-url:hover {
  opacity: 1;
  text-decoration: underline;
}

.fl-desc {
  margin: 0;
  color: var(--text-soft);
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.fl-card-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.fl-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 14px;
  min-width: 0;
}

.fl-meta-item {
  color: var(--text-soft);
  font-size: 12px;
  line-height: 1.5;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.fl-meta-label {
  color: var(--text-soft);
  opacity: 0.65;
}

.fl-actions {
  display: flex;
  gap: 8px;
  flex: 0 0 auto;
  flex-wrap: nowrap;
}

.fl-btn {
  min-height: 34px;
  border-radius: 11px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(148, 163, 184, 0.08);
  color: var(--text-soft);
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease, background 0.18s ease, color 0.18s ease;
}

.fl-btn:hover {
  transform: translateY(-1px);
}

.fl-btn-approve {
  border-color: rgba(16, 185, 129, 0.2);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(14, 165, 164, 0.08));
  color: #0f766e;
}

.fl-btn-approve:hover {
  border-color: rgba(16, 185, 129, 0.38);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.18), rgba(14, 165, 164, 0.14));
  box-shadow: 0 8px 18px rgba(16, 185, 129, 0.12);
}

.fl-btn-reject {
  border-color: rgba(234, 154, 24, 0.2);
  background: linear-gradient(135deg, rgba(234, 154, 24, 0.12), rgba(234, 154, 24, 0.06));
  color: #b45309;
}

.fl-btn-reject:hover {
  border-color: rgba(234, 154, 24, 0.38);
  background: linear-gradient(135deg, rgba(234, 154, 24, 0.18), rgba(234, 154, 24, 0.12));
  box-shadow: 0 8px 18px rgba(234, 154, 24, 0.12);
}

.fl-btn-delete {
  border-color: rgba(227, 91, 119, 0.2);
  background: linear-gradient(135deg, rgba(227, 91, 119, 0.12), rgba(227, 91, 119, 0.06));
  color: #be123c;
}

.fl-btn-delete:hover {
  border-color: rgba(227, 91, 119, 0.38);
  background: linear-gradient(135deg, rgba(227, 91, 119, 0.18), rgba(227, 91, 119, 0.12));
  box-shadow: 0 8px 18px rgba(227, 91, 119, 0.12);
}

.fl-empty {
  margin: 0;
  padding: 20px 16px;
  text-align: center;
  color: var(--text-soft);
  border: 1px dashed var(--line);
  border-radius: 14px;
  background: transparent;
}

:root[data-theme='dark'] .fl-count {
  border-color: rgba(56, 189, 248, 0.14);
  background: rgba(56, 189, 248, 0.06);
}

:root[data-theme='dark'] .fl-search,
:root[data-theme='dark'] .fl-select {
  border-color: rgba(56, 189, 248, 0.16);
  background: rgba(17, 24, 39, 0.96);
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.04) inset, 0 10px 22px rgba(0, 0, 0, 0.34);
}

:root[data-theme='dark'] .fl-search::placeholder {
  color: color-mix(in srgb, var(--text-soft) 78%, black);
}

:root[data-theme='dark'] .fl-search:hover,
:root[data-theme='dark'] .fl-select:hover {
  border-color: rgba(56, 189, 248, 0.28);
  background: rgba(20, 27, 42, 0.98);
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.05) inset, 0 12px 24px rgba(0, 0, 0, 0.42);
}

:root[data-theme='dark'] .fl-search:focus,
:root[data-theme='dark'] .fl-select:focus {
  border-color: rgba(56, 189, 248, 0.52);
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.14), 0 12px 24px rgba(0, 0, 0, 0.42);
}

:root[data-theme='dark'] .fl-refresh-btn {
  border-color: rgba(56, 189, 248, 0.18);
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.12), rgba(251, 191, 36, 0.08));
  color: var(--text);
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.28);
}

:root[data-theme='dark'] .fl-refresh-btn:hover {
  border-color: rgba(56, 189, 248, 0.34);
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.18), rgba(251, 191, 36, 0.12));
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.36);
}

:root[data-theme='dark'] .fl-card {
  background: rgba(17, 24, 39, 0.96);
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.22);
}

:root[data-theme='dark'] .fl-card:hover {
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.32);
}

:root[data-theme='dark'] .fl-card.status-pending {
  background: linear-gradient(135deg, rgba(234, 154, 24, 0.14), rgba(17, 24, 39, 0.96));
}

:root[data-theme='dark'] .fl-card.status-approved {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.14), rgba(17, 24, 39, 0.96));
}

:root[data-theme='dark'] .fl-card.status-rejected {
  background: linear-gradient(135deg, rgba(227, 91, 119, 0.14), rgba(17, 24, 39, 0.96));
}

:root[data-theme='dark'] .fl-avatar {
  opacity: 0.9;
}

:root[data-theme='dark'] .fl-badge.status-approved {
  color: #5eead4;
}

:root[data-theme='dark'] .fl-badge.status-pending {
  color: #fbbf24;
}

:root[data-theme='dark'] .fl-badge.status-rejected {
  color: #fb7185;
}

:root[data-theme='dark'] .fl-btn-approve {
  border-color: rgba(16, 185, 129, 0.22);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.14), rgba(94, 234, 212, 0.08));
  color: #5eead4;
}

:root[data-theme='dark'] .fl-btn-approve:hover {
  border-color: rgba(16, 185, 129, 0.38);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(94, 234, 212, 0.14));
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.28);
}

:root[data-theme='dark'] .fl-btn-reject {
  border-color: rgba(251, 191, 36, 0.22);
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.14), rgba(251, 191, 36, 0.06));
  color: #fbbf24;
}

:root[data-theme='dark'] .fl-btn-reject:hover {
  border-color: rgba(251, 191, 36, 0.38);
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(251, 191, 36, 0.12));
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.28);
}

:root[data-theme='dark'] .fl-btn-delete {
  border-color: rgba(227, 91, 119, 0.22);
  background: linear-gradient(135deg, rgba(227, 91, 119, 0.14), rgba(227, 91, 119, 0.06));
  color: #ff8aa0;
}

:root[data-theme='dark'] .fl-btn-delete:hover {
  border-color: rgba(227, 91, 119, 0.38);
  background: linear-gradient(135deg, rgba(227, 91, 119, 0.2), rgba(227, 91, 119, 0.12));
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.28);
}

@media (max-width: 900px) {
  .fl-toolbar {
    grid-template-columns: 1fr;
  }

  .fl-card-bottom {
    flex-direction: column;
    align-items: flex-start;
  }

  .fl-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .fl-actions .fl-btn {
    flex: 1;
    min-width: 80px;
    text-align: center;
  }
}

@media (max-width: 640px) {
  .fl-panel {
    gap: 10px;
  }

  .fl-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .fl-card {
    padding: 14px;
  }

  .fl-avatar {
    width: 30px;
    height: 30px;
    font-size: 13px;
  }
}
</style>
