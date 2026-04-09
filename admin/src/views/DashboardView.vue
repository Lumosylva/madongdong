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
            <li v-for="item in comments.filter(c => c.status === 'pending')" :key="item.id">
              <div class="comment-content">{{ item.content }}</div>
              <div class="comment-meta-overview">
                <span class="comment-author">{{ item.guest_nickname || item.user?.nickname || '匿名' }}</span>
                <span class="comment-email" v-if="item.guest_email">{{ item.guest_email }}</span>
                <span class="comment-date">{{ new Date(item.created_at).toLocaleDateString() }}</span>
              </div>
            </li>
          </ul>
          <p v-if="comments.filter(c => c.status === 'pending').length === 0" class="no-pending-comments">暂无待审核评论</p>
        </div>
      </section>

      <!-- 文章列表视图 -->
      <section class="panel" v-show="currentView === 'articles'">
        <h3>文章列表</h3>
        <p v-if="loading" class="loading">加载中...</p>
        <p v-else-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        <p v-else-if="articles.length === 0" class="no-articles">暂无文章</p>
        <ul v-else>
          <li v-for="item in articles" :key="item.id" class="article-item">
            <div class="article-info">
              {{ item.title }} · {{ item.status === 'published' ? '已发布' : item.status === 'draft' ? '草稿' : item.status === 'pending' ? '待审核' : item.status }}
            </div>
            <div class="article-actions">
              <button class="btn-edit" @click="editArticle(item)">编辑</button>
              <button class="btn-delete" @click="deleteArticle(item.id)">删除</button>
            </div>
          </li>
        </ul>
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

      <!-- 垃圾箱视图 -->
      <section class="panel" v-show="currentView === 'articles'">
        <h3>垃圾箱</h3>
        <div v-if="deletedArticles.length === 0" class="empty-trash">垃圾箱为空</div>
        <ul v-else>
          <li v-for="item in deletedArticles" :key="item.id" class="article-item deleted-item">
            <div class="article-info">
              {{ item.title }} · 已删除于 {{ new Date(item.deleted_at).toLocaleDateString() }}
            </div>
            <div class="article-actions">
              <button class="btn-restore" @click="restoreArticle(item.id)">恢复</button>
              <button class="btn-permanent-delete" @click="permanentlyDeleteArticle(item.id)">永久删除</button>
            </div>
          </li>
        </ul>
        <button v-if="deletedArticles.length > 0" class="btn-clear-all" @click="clearAllTrash">清空垃圾箱</button>
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

      <!-- 编辑文章模态框 -->
      <div v-if="isEditModalOpen" class="modal-overlay" @click="isEditModalOpen = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>编辑文章</h3>
            <button class="modal-close" @click="isEditModalOpen = false">&times;</button>
          </div>
          <div class="modal-body">
            <input v-model="editTitle" placeholder="标题" />
            <input v-model="editSummary" placeholder="摘要" />
            <input v-model="editCoverUrl" placeholder="封面图 URL" />
            <textarea v-model="editContentMarkdown" placeholder="Markdown 正文" rows="10"></textarea>
            <div class="action-row">
              <input v-model.number="editCategoryId" type="number" placeholder="分类 ID" />
              <input v-model="editTagIdsText" placeholder="标签 ID，逗号分隔" />
              <select v-model="editAction">
                <option value="draft">保存草稿</option>
                <option value="submit">提交审核</option>
                <option value="publish">直接发布</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="isEditModalOpen = false">取消</button>
            <button @click="updateArticle">保存</button>
          </div>
        </div>
      </div>

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
const deletedArticles = ref<any[]>([])
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

const editingArticle = ref<any | null>(null)
const isEditModalOpen = ref(false)
const editTitle = ref('')
const editSummary = ref('')
const editCoverUrl = ref('')
const editContentMarkdown = ref('')
const editCategoryId = ref(1)
const editTagIdsText = ref('')
const editAction = ref<'draft' | 'submit' | 'publish'>('draft')

const loadAll = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const [articleRes, deletedArticleRes, mediaRes, commentRes, siteRes] = await Promise.all([
      adminApi.getArticles(),
      adminApi.getDeletedArticles(),
      adminApi.getMedia(),
      adminApi.getComments(),
      adminApi.getSiteSettings(),
    ])
    articles.value = articleRes.data
    deletedArticles.value = deletedArticleRes.data
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

const editArticle = (article: any) => {
  editingArticle.value = article
  editTitle.value = article.title
  editSummary.value = article.summary
  editCoverUrl.value = article.cover_url || ''
  editContentMarkdown.value = article.content_markdown
  editCategoryId.value = article.category_id
  editTagIdsText.value = article.tags.map((tag: any) => tag.id).join(',')
  editAction.value = article.status
  isEditModalOpen.value = true
}

const updateArticle = async () => {
  if (!editingArticle.value) return
  
  try {
    loading.value = true
    const tagIds = editTagIdsText.value
      .split(',')
      .map((item: string) => Number(item.trim()))
      .filter((item: number) => !Number.isNaN(item))
    
    await adminApi.updateArticle(editingArticle.value.id, {
      title: editTitle.value,
      summary: editSummary.value,
      content_markdown: editContentMarkdown.value,
      cover_url: editCoverUrl.value || null,
      category_id: editCategoryId.value,
      tag_ids: tagIds,
      action: editAction.value,
    })
    
    isEditModalOpen.value = false
    editingArticle.value = null
    await loadAll()
  } catch (error) {
    const message = error instanceof Error ? error.message : '更新文章失败'
    errorMessage.value = message
  } finally {
    loading.value = false
  }
}

const deleteArticle = async (articleId: number) => {
  if (!confirm('确定要删除这篇文章吗？删除后将移入垃圾箱。')) return
  
  try {
    loading.value = true
    await adminApi.deleteArticle(articleId)
    await loadAll()
  } catch (error) {
    const message = error instanceof Error ? error.message : '删除文章失败'
    errorMessage.value = message
  } finally {
    loading.value = false
  }
}

const restoreArticle = async (articleId: number) => {
  if (!confirm('确定要恢复这篇文章吗？')) return
  
  try {
    loading.value = true
    await adminApi.restoreArticle(articleId)
    await loadAll()
  } catch (error) {
    const message = error instanceof Error ? error.message : '恢复文章失败'
    errorMessage.value = message
  } finally {
    loading.value = false
  }
}

const permanentlyDeleteArticle = async (articleId: number) => {
  if (!confirm('确定要永久删除这篇文章吗？此操作无法撤销！')) return
  
  try {
    loading.value = true
    await adminApi.permanentlyDeleteArticle(articleId)
    await loadAll()
  } catch (error) {
    const message = error instanceof Error ? error.message : '永久删除文章失败'
    errorMessage.value = message
  } finally {
    loading.value = false
  }
}

const clearAllTrash = async () => {
  if (!confirm(`确定要清空垃圾箱吗？将永久删除 ${deletedArticles.value.length} 篇文章，此操作无法撤销！`)) return
  
  try {
    loading.value = true
    for (const article of deletedArticles.value) {
      await adminApi.permanentlyDeleteArticle(article.id)
    }
    await loadAll()
  } catch (error) {
    const message = error instanceof Error ? error.message : '清空垃圾箱失败'
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
