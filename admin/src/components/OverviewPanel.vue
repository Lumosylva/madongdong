<template>
  <section class="overview-page">
    <!-- Welcome Banner -->
    <div class="overview-welcome panel">
      <div class="overview-welcome-content">
        <h2 class="overview-welcome-title">{{ t('overview.welcomeTitle') }}</h2>
        <p class="overview-welcome-desc">{{ t('overview.welcomeDesc') }}</p>
      </div>
      <div class="overview-welcome-decoration" aria-hidden="true">
        <svg viewBox="0 0 120 120" fill="none">
          <circle cx="60" cy="60" r="58" stroke="currentColor" stroke-width="2" stroke-dasharray="4 4" opacity="0.3"/>
          <path d="M30 60L50 80L90 40" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="overview-quick-actions">
      <button class="overview-action-card" @click="$emit('navigate', 'articles-create')">
        <span class="overview-action-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 5v14M5 12h14"/>
          </svg>
        </span>
        <span class="overview-action-label">{{ t('overview.writeArticle') }}</span>
      </button>
      <button class="overview-action-card" @click="$emit('navigate', 'media')">
        <span class="overview-action-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <polyline points="21 15 16 10 5 21"/>
          </svg>
        </span>
        <span class="overview-action-label">{{ t('overview.uploadMedia') }}</span>
      </button>
      <button class="overview-action-card" @click="$emit('navigate', 'comments')">
        <span class="overview-action-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </span>
        <span class="overview-action-label">{{ t('overview.manageComments') }}</span>
      </button>
      <button class="overview-action-card" @click="$emit('navigate', 'site')">
        <span class="overview-action-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        </span>
        <span class="overview-action-label">{{ t('overview.siteSettings') }}</span>
      </button>
    </div>

    <!-- Stats Grid -->
    <div class="overview-stats-grid">
      <!-- Article Stats -->
      <div class="panel overview-panel overview-articles-panel">
        <div class="overview-head">
          <h3>{{ t('overview.articleStats') }}</h3>
          <p v-if="loading" class="tips">{{ t('overview.loadingTip') }}</p>
          <p v-else-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        </div>
        <div class="overview-metrics">
          <div class="overview-metric metric-published">
            <span class="overview-metric-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </span>
            <span class="overview-metric-value">{{ publishedCount }}</span>
            <span class="overview-metric-label">{{ t('status.published') }}</span>
          </div>
          <div class="overview-metric metric-draft">
            <span class="overview-metric-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
            </span>
            <span class="overview-metric-value">{{ draftCount }}</span>
            <span class="overview-metric-label">{{ t('status.draft') }}</span>
          </div>
          <div class="overview-metric metric-pending">
            <span class="overview-metric-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </span>
            <span class="overview-metric-value">{{ pendingCount }}</span>
            <span class="overview-metric-label">{{ t('status.pending') }}</span>
          </div>
          <div class="overview-metric metric-rejected">
            <span class="overview-metric-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
              </svg>
            </span>
            <span class="overview-metric-value">{{ rejectedCount }}</span>
            <span class="overview-metric-label">{{ t('status.rejected') }}</span>
          </div>
          <div class="overview-metric metric-trash">
            <span class="overview-metric-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
            </span>
            <span class="overview-metric-value">{{ deletedArticles.length }}</span>
            <span class="overview-metric-label">{{ t('status.trash') }}</span>
          </div>
        </div>
      </div>

      <!-- Comment Stats -->
      <div class="panel overview-panel overview-comments-panel">
        <div class="overview-head">
          <h3>{{ t('overview.commentStats') }}</h3>
        </div>
        <div class="overview-metrics comments-metrics">
          <div class="overview-metric metric-approved">
            <span class="overview-metric-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>
              </svg>
            </span>
            <span class="overview-metric-value">{{ approvedCommentCount }}</span>
            <span class="overview-metric-label">{{ t('status.approved') }}</span>
          </div>
          <div class="overview-metric metric-pending-comment">
            <span class="overview-metric-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </span>
            <span class="overview-metric-value">{{ pendingCommentCount }}</span>
            <span class="overview-metric-label">{{ t('status.pending') }}</span>
          </div>
          <div class="overview-metric metric-rejected-comment">
            <span class="overview-metric-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"/>
              </svg>
            </span>
            <span class="overview-metric-value">{{ rejectedCommentCount }}</span>
            <span class="overview-metric-label">{{ t('status.rejectedComment') }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Grid: Recent Articles + Pending Tasks -->
    <div class="overview-bottom-grid">
      <!-- Recent Articles -->
      <div class="panel overview-panel overview-recent-panel">
        <div class="overview-head">
          <h3>{{ t('overview.recentArticles') }}</h3>
          <button class="overview-view-all" @click="$emit('navigate', 'articles-manage')">
            {{ t('overview.viewAll') }}
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </button>
        </div>
        <div v-if="recentArticles.length" class="overview-recent-list">
          <div v-for="article in recentArticles" :key="article.id" class="overview-recent-item" @click="$emit('edit-article', article.id)">
            <div class="overview-recent-main">
              <span class="overview-recent-title">{{ article.title }}</span>
              <span class="overview-recent-meta">{{ formatTimeAgo(article.published_at || article.created_at) }}</span>
            </div>
            <span class="overview-recent-status" :class="`status-${normalizeStatus(article.status)}`">
              {{ formatArticleStatus(article.status) }}
            </span>
          </div>
        </div>
        <p v-else class="overview-empty">{{ t('overview.noRecentArticles') }}</p>
      </div>

      <!-- Pending Tasks -->
      <div class="panel overview-panel overview-pending-panel">
        <div class="overview-head">
          <h3>{{ t('overview.pendingTasks') }}</h3>
        </div>
        <div class="overview-pending-list">
          <div class="overview-pending-item" :class="{ 'has-items': pendingCommentCount > 0 }" @click="$emit('navigate', 'comments')">
            <span class="overview-pending-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
            </span>
            <div class="overview-pending-info">
              <span class="overview-pending-label">{{ t('overview.pendingComments') }}</span>
              <span class="overview-pending-count" :class="{ 'count-zero': pendingCommentCount === 0 }">{{ pendingCommentCount }}</span>
            </div>
          </div>
          <div class="overview-pending-item" :class="{ 'has-items': pendingFriendLinks > 0 }" @click="$emit('navigate', 'friend-links')">
            <span class="overview-pending-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
              </svg>
            </span>
            <div class="overview-pending-info">
              <span class="overview-pending-label">{{ t('overview.pendingFriendLinks') }}</span>
              <span class="overview-pending-count" :class="{ 'count-zero': pendingFriendLinks === 0 }">{{ pendingFriendLinks }}</span>
            </div>
          </div>
          <div class="overview-pending-item" :class="{ 'has-items': deletedArticles.length > 0 }" @click="$emit('navigate', 'articles-trash')">
            <span class="overview-pending-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
            </span>
            <div class="overview-pending-info">
              <span class="overview-pending-label">{{ t('overview.deletedArticles') }}</span>
              <span class="overview-pending-count" :class="{ 'count-zero': deletedArticles.length === 0 }">{{ deletedArticles.length }}</span>
            </div>
          </div>
          <p v-if="pendingCommentCount === 0 && pendingFriendLinks === 0 && deletedArticles.length === 0" class="overview-empty">
            {{ t('overview.noPending') }}
          </p>
        </div>
      </div>
    </div>

    <!-- Mini Trend Chart -->
    <div class="panel overview-panel overview-trend-panel">
      <div class="overview-head">
        <h3>{{ t('overview.trendTitle') }}</h3>
      </div>
      <div class="overview-trend-chart">
        <div class="overview-trend-bars">
          <div v-for="(day, index) in trendData" :key="index" class="overview-trend-bar-group">
            <div class="overview-trend-bar-stack">
              <div class="overview-trend-bar bar-published" :style="{ height: `${day.published * 10}px` }" :title="`${t('overview.publishedTrend')}: ${day.published}`"/>
              <div class="overview-trend-bar bar-draft" :style="{ height: `${day.draft * 10}px` }" :title="`${t('overview.draftTrend')}: ${day.draft}`"/>
              <div class="overview-trend-bar bar-comment" :style="{ height: `${day.comments * 10}px` }" :title="`${t('overview.commentTrend')}: ${day.comments}`"/>
            </div>
            <span class="overview-trend-day">{{ day.label }}</span>
          </div>
        </div>
        <div class="overview-trend-legend">
          <span class="overview-trend-legend-item">
            <span class="overview-trend-dot dot-published"></span>
            {{ t('overview.publishedTrend') }}
          </span>
          <span class="overview-trend-legend-item">
            <span class="overview-trend-dot dot-draft"></span>
            {{ t('overview.draftTrend') }}
          </span>
          <span class="overview-trend-legend-item">
            <span class="overview-trend-dot dot-comment"></span>
            {{ t('overview.commentTrend') }}
          </span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps<{
  articles: any[]
  deletedArticles: any[]
  comments: any[]
  friendLinks?: any[]
  loading: boolean
  errorMessage: string
  formatArticleStatus: (status: string) => string
}>()

defineEmits<{
  navigate: [view: string]
  'edit-article': [id: number]
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

const pendingFriendLinks = computed(() => {
  const links = props.friendLinks || []
  return links.filter((item: any) => String(item.status || '').trim().toLowerCase() === 'pending').length
})

const recentArticles = computed(() => {
  return [...props.articles]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5)
})

const formatTimeAgo = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  const diffHour = Math.floor(diffMs / 3600000)
  const diffDay = Math.floor(diffMs / 86400000)

  if (diffMin < 1) return t('time.justNow')
  if (diffMin < 60) return t('time.minutesAgo', { n: diffMin })
  if (diffHour < 24) return t('time.hoursAgo', { n: diffHour })
  if (diffDay < 365) return t('time.daysAgo', { n: diffDay })
  return t('time.yearsAgo', { n: Math.floor(diffDay / 365) })
}

const trendData = computed(() => {
  const days = ['日', '一', '二', '三', '四', '五', '六']
  const result = []
  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    const dayOfWeek = days[date.getDay()]
    const dateStr = date.toISOString().split('T')[0]
    const dayArticles = props.articles.filter((a) => (a.created_at || '').startsWith(dateStr))
    const dayComments = props.comments.filter((c) => (c.created_at || '').startsWith(dateStr))
    result.push({
      label: dayOfWeek,
      published: dayArticles.filter((a) => normalizeStatus(a.status) === 'published').length,
      draft: dayArticles.filter((a) => normalizeStatus(a.status) === 'draft').length,
      comments: dayComments.length,
    })
  }
  return result
})
</script>
