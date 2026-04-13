<template>
  <div class="admin-page">
    <header class="topbar">
      <div class="brand-block">
        <span class="brand-mark">MD</span>
        <h1>MaDongDong Admin</h1>
      </div>
      <div class="topbar-actions">
        <button type="button" class="theme-toggle" :aria-label="themeToggleLabel" @click="toggleTheme">
          <span aria-hidden="true">{{ theme === 'light' ? '◐' : '☼' }}</span>
        </button>
        <button type="button" class="logout-btn" @click="logout">退出登录</button>
      </div>
    </header>

    <div class="dashboard-shell">
      <aside class="sidebar">
        <h2>控制台</h2>
        <nav class="sidebar-nav">
          <a href="javascript:void(0)" :class="{ active: currentView === 'overview' }" @click="setView('overview')">概览</a>
          <a href="javascript:void(0)" :class="{ active: currentView === 'articles' }" @click="setView('articles')">文章</a>
          <a href="javascript:void(0)" :class="{ active: currentView === 'media' }" @click="setView('media')">媒体</a>
          <a href="javascript:void(0)" :class="{ active: currentView === 'comments' }" @click="setView('comments')">评论</a>
          <a href="javascript:void(0)" :class="{ active: currentView === 'site' }" @click="setView('site')">站点</a>
        </nav>
      </aside>

      <main class="dashboard-main">
        <section class="grid-panels" v-if="currentView === 'overview'">
          <div class="panel">
            <h3>文章概览</h3>
            <p class="tips">共 {{ articles.length }} 篇文章</p>
            <p v-if="loading" class="tips">正在同步后台数据...</p>
            <p v-else-if="errorMessage" class="error-message">{{ errorMessage }}</p>
            <ul>
              <li v-for="item in articles.slice(0, 5)" :key="item.id">{{ item.title }} · {{ item.status }}</li>
            </ul>
          </div>
          <div class="panel">
            <h3>评论概览</h3>
            <p class="tips">共 {{ comments.length }} 条评论</p>
            <ul>
              <li v-for="item in comments.slice(0, 5)" :key="item.id">{{ item.content }}</li>
            </ul>
          </div>
        </section>

        <section class="panel" v-if="currentView === 'articles'">
          <div class="section-head">
            <h3>文章管理</h3>
            <button @click="loadAll">刷新数据</button>
          </div>
          <ul>
            <li v-for="item in articles" :key="item.id">{{ item.title }} · {{ item.status }}</li>
          </ul>
        </section>

        <section class="editor-panel" v-if="currentView === 'articles'">
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

        <section class="panel" v-if="currentView === 'media'">
          <div class="section-head">
            <h3>媒体管理</h3>
            <button @click="loadAll">刷新数据</button>
          </div>
          <ul>
            <li v-for="item in media" :key="item.id">{{ item.original_name }} · {{ item.media_type }}</li>
          </ul>
        </section>

        <section class="panel" v-if="currentView === 'comments'">
          <div class="section-head">
            <h3>评论管理</h3>
            <button @click="loadAll">刷新数据</button>
          </div>
          <ul>
            <li v-for="item in comments" :key="item.id">{{ item.content }}</li>
          </ul>
        </section>

        <section class="panel" v-if="currentView === 'site'">
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
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { adminApi } from '../api'

type ThemeMode = 'light' | 'dark'
type ViewType = 'overview' | 'articles' | 'media' | 'comments' | 'site'

const router = useRouter()
const currentView = ref<ViewType>('overview')
const articles = ref<any[]>([])
const media = ref<any[]>([])
const comments = ref<any[]>([])
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

const theme = ref<ThemeMode>('light')

const setView = (view: ViewType) => {
  currentView.value = view
}

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

const logout = async () => {
  localStorage.removeItem('blog_admin_token')
  await router.push('/login')
}

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
  currentView.value = 'articles'
  await loadAll()
}

onMounted(() => {
  const storedTheme = localStorage.getItem('md-admin-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  loadAll()
})
</script>
