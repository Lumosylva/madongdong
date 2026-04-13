<template>
  <div class="admin-page">
    <header class="topbar">
      <div class="brand-block">
        <span class="brand-mark">MD</span>
        <h1>Admin</h1>
      </div>
      <div class="topbar-actions">
        <button type="button" class="theme-toggle" :aria-label="themeToggleLabel" @click="toggleTheme">
          <span aria-hidden="true">{{ theme === 'light' ? '◐' : '☼' }}</span>
        </button>
        <div class="user-menu" ref="userMenuRef">
          <button type="button" class="user-trigger" @click="toggleUserMenu">
            <span class="user-name">{{ displayName }}</span>
            <span class="role-badge" :class="isAdmin ? 'admin' : 'author'">{{ roleLabel }}</span>
          </button>
          <div v-if="isUserMenuOpen" class="user-dropdown">
            <button type="button" class="dropdown-item danger" @click="logout">退出登录</button>
          </div>
        </div>
      </div>
    </header>

    <div class="dashboard-shell">
      <aside class="sidebar">
        <h2>控制台</h2>
        <nav class="sidebar-nav">
          <template v-for="item in visibleMainMenus" :key="item.key">
            <a href="javascript:void(0)" :class="{ active: currentView === item.key }" @click="setView(item.key)">{{ item.label }}</a>
            <div v-if="item.key === 'articles' && currentView === 'articles'" class="sidebar-subnav">
              <a
                v-for="sub in articleSubMenus"
                :key="sub.key"
                href="javascript:void(0)"
                :class="{ active: articleSubView === sub.key }"
                @click="setArticleSubView(sub.key)"
              >{{ sub.label }}</a>
            </div>
          </template>
        </nav>
      </aside>

      <main class="dashboard-main">
        <OverviewPanel
          v-if="currentContentView === 'overview'"
          :articles="articles"
          :deleted-articles="deletedArticles"
          :comments="comments"
          :loading="loading"
          :error-message="errorMessage"
          :format-article-status="formatArticleStatus"
        />

        <ArticleManagePanel
          v-if="currentContentView === 'articles-manage'"
          :articles="articles"
          :format-article-status="formatArticleStatus"
          @move-to-trash="moveToTrash"
        />

        <ArticleTrashPanel
          v-if="currentContentView === 'articles-trash'"
          :deleted-articles="deletedArticles"
          @restore="restoreFromTrash"
          @remove-permanently="removePermanently"
        />

        <ArticleCreatePanel
          v-if="currentContentView === 'articles-create'"
          :is-admin="isAdmin"
          :title="title"
          :summary="summary"
          :cover-url="coverUrl"
          :content-markdown="contentMarkdown"
          :category-id="categoryId"
          :tag-ids-text="tagIdsText"
          :action="action"
          @update:title="title = $event"
          @update:summary="summary = $event"
          @update:cover-url="coverUrl = $event"
          @update:content-markdown="contentMarkdown = $event"
          @update:category-id="categoryId = $event"
          @update:tag-ids-text="tagIdsText = $event"
          @update:action="action = $event"
          @submit="createArticle"
        />

        <section class="panel" v-if="currentContentView === 'media'">
          <h3>媒体管理</h3>
          <ul>
            <li v-for="item in media" :key="item.id">{{ item.original_name }} · {{ item.media_type }}</li>
          </ul>
        </section>

        <section class="panel" v-if="currentContentView === 'comments'">
          <h3>评论管理</h3>
          <ul>
            <li v-for="item in comments" :key="item.id">{{ item.content }}</li>
          </ul>
        </section>

        <section class="panel" v-if="currentContentView === 'site'">
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
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { adminApi } from '../api'
import ArticleCreatePanel from '../components/ArticleCreatePanel.vue'
import ArticleManagePanel from '../components/ArticleManagePanel.vue'
import ArticleTrashPanel from '../components/ArticleTrashPanel.vue'
import OverviewPanel from '../components/OverviewPanel.vue'
import type { AdminUser } from '../types'

type ThemeMode = 'light' | 'dark'
type ViewType = 'overview' | 'articles' | 'media' | 'comments' | 'site'
type ArticleSubView = 'manage' | 'trash' | 'create'
type ContentViewKey =
  | 'overview'
  | 'articles-manage'
  | 'articles-trash'
  | 'articles-create'
  | 'media'
  | 'comments'
  | 'site'

type MainMenuItem = {
  key: ViewType
  label: string
  adminOnly?: boolean
}

type ArticleSubMenuItem = {
  key: ArticleSubView
  label: string
}

const router = useRouter()
const currentView = ref<ViewType>('overview')
const articleSubView = ref<ArticleSubView>('manage')
const currentUser = ref<AdminUser | null>(null)
const articles = ref<any[]>([])
const deletedArticles = ref<any[]>([])
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
const isUserMenuOpen = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)

const mainMenus: MainMenuItem[] = [
  { key: 'overview', label: '概览' },
  { key: 'articles', label: '文章' },
  { key: 'media', label: '媒体', adminOnly: true },
  { key: 'comments', label: '评论', adminOnly: true },
  { key: 'site', label: '站点', adminOnly: true },
]

const articleSubMenus: ArticleSubMenuItem[] = [
  { key: 'manage', label: '文章管理' },
  { key: 'trash', label: '垃圾箱' },
  { key: 'create', label: '创建文章' },
]

const setView = (view: ViewType) => {
  const targetMenu = mainMenus.find((item) => item.key === view)
  if (targetMenu?.adminOnly && !isAdmin.value) {
    return
  }
  currentView.value = view
  if (view === 'articles') {
    articleSubView.value = articleSubView.value || 'manage'
  }
}

const setArticleSubView = (subView: ArticleSubView) => {
  articleSubView.value = subView
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

const isAdmin = computed(() =>
  currentUser.value?.roles.some((role) => role.name === 'admin' || role.name === '系统管理员') ?? false,
)

const isAuthor = computed(() =>
  currentUser.value?.roles.some((role) => role.name === 'author' || role.name === '内容作者') ?? false,
)

const displayName = computed(() => currentUser.value?.nickname || currentUser.value?.username || '未登录用户')

const roleLabel = computed(() => {
  if (isAdmin.value) return '系统管理员'
  if (isAuthor.value) return '内容作者'
  return '普通用户'
})

const visibleMainMenus = computed(() =>
  mainMenus.filter((item) => !item.adminOnly || isAdmin.value),
)

const currentContentView = computed<ContentViewKey>(() => {
  if (currentView.value === 'overview') return 'overview'
  if (currentView.value === 'media') return 'media'
  if (currentView.value === 'comments') return 'comments'
  if (currentView.value === 'site') return 'site'

  if (articleSubView.value === 'trash') return 'articles-trash'
  if (articleSubView.value === 'create') return 'articles-create'
  return 'articles-manage'
})

const formatArticleStatus = (status: string) => {
  if (status === 'PUBLISHED' || status === 'published') return '已发布'
  if (status === 'DRAFT' || status === 'draft') return '草稿'
  if (status === 'PENDING_REVIEW' || status === 'pending_review' || status === 'pending') return '待审核'
  if (status === 'REJECTED' || status === 'rejected') return '已驳回'
  return status
}

const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
}

const handleDocumentClick = (event: MouseEvent) => {
  if (!isUserMenuOpen.value) return
  const target = event.target as Node | null
  if (userMenuRef.value && target && !userMenuRef.value.contains(target)) {
    isUserMenuOpen.value = false
  }
}

const logout = async () => {
  isUserMenuOpen.value = false
  localStorage.removeItem('blog_admin_token')
  await router.push('/login')
}

const loadAll = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const meRes = await adminApi.getMe()
    currentUser.value = meRes.data
    const [articleRes, deletedRes, mediaRes, commentRes, siteRes] = await Promise.all([
      adminApi.getArticles(),
      adminApi.getDeletedArticles(),
      adminApi.getMedia(),
      adminApi.getComments(),
      adminApi.getSiteSettings(),
    ])
    articles.value = articleRes.data
    deletedArticles.value = deletedRes.data
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

const moveToTrash = async (articleId: number) => {
  if (!confirm('确认将该文章移入垃圾箱？')) return
  await adminApi.deleteArticle(articleId)
  await loadAll()
}

const restoreFromTrash = async (articleId: number) => {
  await adminApi.restoreArticle(articleId)
  await loadAll()
}

const removePermanently = async (articleId: number) => {
  if (!confirm('确认彻底删除？该操作不可恢复。')) return
  await adminApi.permanentlyDeleteArticle(articleId)
  await loadAll()
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
  const finalAction = isAdmin.value
    ? (action.value === 'publish' ? 'publish' : 'draft')
    : (action.value === 'submit' ? 'submit' : 'draft')

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
    action: finalAction,
  })
  title.value = ''
  summary.value = ''
  coverUrl.value = ''
  contentMarkdown.value = ''
  tagIdsText.value = ''
  currentView.value = 'articles'
  await loadAll()
}

onMounted(async () => {
  const storedTheme = localStorage.getItem('md-admin-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  await loadAll()
  action.value = isAdmin.value ? 'publish' : 'submit'
  document.addEventListener('click', handleDocumentClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>
