<template>
  <div class="dashboard-shell">
    <header class="topbar">
      <div class="brand-block">
        <span class="brand-mark">MDD</span>
        <div class="brand-info">
          <h1>博客运营后台</h1>
          <p class="brand-subtitle">统一管理文章审核、媒体资源、评论审核与站点设置。</p>
        </div>
      </div>
      <div class="user-menu">
        <button type="button" class="theme-toggle" :aria-label="themeToggleLabel" @click="toggleTheme">
          <span aria-hidden="true">{{ theme === 'light' ? '☀️' : '🌙' }}</span>
        </button>
        <button class="user-profile" @click="logout">
          <span class="user-name">管理员</span>
          <span class="user-avatar">👤</span>
        </button>
      </div>
    </header>
    
    <div class="dashboard-content">
      <aside class="sidebar">
        <div class="sidebar-header">
          <h2>控制台</h2>
        </div>
        <nav>
          <a href="javascript:void(0)" :class="{ active: currentView === 'overview' }" @click.prevent="setView('overview')">概览</a>
          <a href="javascript:void(0)" :class="{ active: currentView === 'articles' }" @click.prevent="setView('articles')">文章</a>
          <a href="javascript:void(0)" :class="{ active: currentView === 'media' }" @click.prevent="setView('media')">媒体</a>
          <a href="javascript:void(0)" :class="{ active: currentView === 'comments' }" @click.prevent="setView('comments')">评论</a>
          <a href="javascript:void(0)" :class="{ active: currentView === 'site' }" @click.prevent="setView('site')">站点</a>
        </nav>
      </aside>

      <main class="dashboard-main">
      <section class="grid-panels" v-show="currentView === 'overview'">
        <div class="panel">
          <h3>文章列表</h3>
          <ul>
            <li v-for="item in articles" :key="item.id">{{ item.title }} · {{ item.status === 'published' ? '已发布' : item.status === 'draft' ? '草稿' : item.status === 'pending' ? '待审核' : item.status }}</li>
          </ul>
        </div>
        <div class="panel">
          <h3>网站访问量统计</h3>
          <div class="visit-stats">
            <div class="stat-item">
              <div class="stat-value">{{ visitStats.total }}</div>
              <div class="stat-label">总访问量</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ visitStats.today }}</div>
              <div class="stat-label">今日访问量</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ visitStats.unique }}</div>
              <div class="stat-label">独立访客</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ visitStats.avgTime }}</div>
              <div class="stat-label">平均停留(秒)</div>
            </div>
          </div>
          <div class="visit-trend">
            <p class="trend-up">📈 较昨日增长 {{ visitStats.dailyGrowth }}%</p>
            <p class="trend-info">数据更新时间: {{ visitStats.updateTime }}</p>
          </div>
        </div>
        <div class="panel">
          <h3>评论审核</h3>
          <ul>
            <li v-for="item in comments" :key="item.id">
              <div class="comment-content">{{ item.content }}</div>
              <div class="comment-meta-overview">
                <span class="comment-author">{{ item.guest_nickname || item.user?.nickname || '匿名' }}</span>
                <span class="comment-email" v-if="item.guest_email">{{ item.guest_email }}</span>
                <span class="comment-date">{{ new Date(item.created_at).toLocaleDateString() }}</span>
              </div>
            </li>
          </ul>
        </div>
      </section>

      <section class="editor-panel" id="articles" v-show="currentView === 'articles'">
        <h3>快速创建文章</h3>
        <input v-model="title" placeholder="标题" />
        <input v-model="summary" placeholder="摘要" />
        <input v-model="coverUrl" placeholder="封面图 URL" />
        <textarea v-model="contentMarkdown" placeholder="Markdown 正文"></textarea>
        <div class="action-row">
          <input v-model.number="categoryId" type="number" placeholder="分类 ID" />
          <input v-model="tagIdsText" placeholder="标签 ID，逗号分隔" />
          <select v-model="action">
            <option value="draft">保存草稿</option>
            <option value="submit">提交审核</option>
            <option value="publish">直接发布</option>
          </select>
          <button @click="createArticle">提交</button>
        </div>
      </section>

      <!-- 文章列表视图 -->
      <section class="panel" v-show="currentView === 'articles'">
        <h3>文章列表</h3>
        <button @click="loadAll">刷新数据</button>
        <ul>
          <li v-for="item in articles" :key="item.id">{{ item.title }} · {{ item.status }}</li>
        </ul>
      </section>

      <!-- 媒体库视图 -->
      <section class="panel" v-show="currentView === 'media'">
        <h3>媒体库</h3>
        <ul>
          <li v-for="item in media" :key="item.id">{{ item.original_name }} · {{ item.media_type }}</li>
        </ul>
      </section>

      <!-- 评论审核视图 -->
      <section class="panel" v-show="currentView === 'comments'">
        <h3>评论审核</h3>
        <button @click="loadAll">刷新数据</button>
        <div class="comments-list">
          <div v-for="item in comments" :key="item.id" class="comment-item">
            <div class="comment-content">{{ item.content }}</div>
            <div class="comment-meta">
              <span class="comment-author">
                {{ item.guest_nickname || item.user?.nickname || '匿名' }}
                {{ item.guest_email ? `(${item.guest_email})` : '' }}
              </span>
              <span class="comment-article">文章ID：{{ item.article_id }}</span>
              <span :class="'comment-status status-' + item.status">
                {{ item.status === 'pending' ? '待审核' : item.status === 'approved' ? '已通过' : '已拒绝' }}
              </span>
              <span class="comment-time">{{ new Date(item.created_at).toLocaleString() }}</span>
            </div>
            <div class="comment-actions" v-if="item.status === 'pending'">
              <button class="btn-approve" @click="approveComment(item.id)">通过</button>
              <button class="btn-reject" @click="rejectComment(item.id)">拒绝</button>
            </div>
          </div>
        </div>
      </section>

      <!-- 站点设置视图 -->
      <section class="panel" v-show="currentView === 'site'">
        <h3>站点设置</h3>
        <input v-model="siteTitle" placeholder="网站标题" />
        <input v-model="siteSubtitle" placeholder="副标题" />
        <input v-model="icpBeian" placeholder="备案信息" />
        <input v-model="copyrightText" placeholder="版权信息" />
        <button @click="saveSite">保存设置</button>
      </section>

      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'

import { adminApi } from '../api'

type ThemeMode = 'light' | 'dark'
const theme = ref<ThemeMode>('light')

const applyTheme = (value: ThemeMode) => {
  theme.value = value
  document.documentElement.dataset.theme = value
  localStorage.setItem('md-admin-theme', value)
}

const toggleTheme = () => {
  applyTheme(theme.value === 'light' ? 'dark' : 'light')
}

const themeToggleLabel = computed(() =>
  theme.value === 'light' ? '切换为暗色主题' : '切换为白天主题',
)

type ViewType = 'overview' | 'articles' | 'media' | 'comments' | 'site'
const currentView = ref<ViewType>('overview')
const setView = (view: ViewType) => {
  currentView.value = view
}

const router = useRouter()
const articles = ref<any[]>([])
const media = ref<any[]>([])
const comments = ref<any[]>([])
const visitStats = ref({
  total: 12458,
  today: 342,
  unique: 892,
  avgTime: '2:45',
  dailyGrowth: 12.5,
  updateTime: '今日 09:30'
})
const siteTitle = ref('')
const siteSubtitle = ref('')
const icpBeian = ref('')
const copyrightText = ref('')
const loading = ref(false)
const errorMessage = ref('')

const title = ref('')
const summary = ref('')
const coverUrl = ref('')
const contentMarkdown = ref('')
const categoryId = ref(1)
const tagIdsText = ref('')
const action = ref<'draft' | 'submit' | 'publish'>('draft')

const loadAll = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const [articleRes, mediaRes, commentRes, siteRes] = await Promise.all([
      adminApi.getArticles(),
      adminApi.getMedia(),
      adminApi.getComments(),
      adminApi.getSiteSettings(),
    ])
    articles.value = articleRes.data
    media.value = mediaRes.data
    comments.value = commentRes.data
    siteTitle.value = siteRes.data.site_title
    siteSubtitle.value = siteRes.data.site_subtitle || ''
    icpBeian.value = siteRes.data.icp_beian || ''
    copyrightText.value = siteRes.data.copyright_text || ''
  } catch (error) {
    const message = error instanceof Error ? error.message : '加载后台数据失败'
    if (message.includes('401') || message.includes('未提供认证令牌') || message.includes('无效的认证令牌')) {
      localStorage.removeItem('blog_admin_token')
      await router.push('/login')
      return
    }
    errorMessage.value = message
  } finally {
    loading.value = false
  }
}

const approveComment = async (commentId: number) => {
  try {
    await adminApi.approveComment(commentId)
    await loadAll()
  } catch (error) {
    const message = error instanceof Error ? error.message : '审核操作失败'
    errorMessage.value = message
  }
}

const rejectComment = async (commentId: number) => {
  try {
    await adminApi.rejectComment(commentId)
    await loadAll()
  } catch (error) {
    const message = error instanceof Error ? error.message : '审核操作失败'
    errorMessage.value = message
  }
}

const saveSite = async () => {
  await adminApi.updateSiteSettings({
    site_title: siteTitle.value,
    site_logo: null,
    site_subtitle: siteSubtitle.value,
    icp_beian: icpBeian.value,
    copyright_text: copyrightText.value,
    homepage_page_size: 10,
    comment_requires_review: true,
  })
  await loadAll()
}

const createArticle = async () => {
  await adminApi.createArticle({
    title: title.value,
    summary: summary.value,
    content_markdown: contentMarkdown.value,
    cover_url: coverUrl.value || null,
    category_id: categoryId.value,
    tag_ids: tagIdsText.value
      .split(',')
      .map((item) => Number(item.trim()))
      .filter((item) => !Number.isNaN(item)),
    action: action.value,
  })
  title.value = ''
  summary.value = ''
  coverUrl.value = ''
  contentMarkdown.value = ''
  tagIdsText.value = ''
  await loadAll()
}

const logout = async () => {
  localStorage.removeItem('blog_admin_token')
  await router.push('/login')
}

onMounted(() => {
  const storedTheme = localStorage.getItem('md-admin-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  loadAll()
})
</script>
