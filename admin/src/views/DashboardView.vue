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
        <component :is="activePanelComponent" v-bind="activePanelProps" v-on="activePanelListeners" />
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
import CommentsPanel from '../components/CommentsPanel.vue'
import MediaPanel from '../components/MediaPanel.vue'
import OverviewPanel from '../components/OverviewPanel.vue'
import SiteSettingsPanel from '../components/SiteSettingsPanel.vue'
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
  contentKey: Extract<ContentViewKey, 'articles-manage' | 'articles-trash' | 'articles-create'>
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
  { key: 'manage', label: '文章管理', contentKey: 'articles-manage' },
  { key: 'trash', label: '垃圾箱', contentKey: 'articles-trash' },
  { key: 'create', label: '创建文章', contentKey: 'articles-create' },
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

const articleSubViewToContentKey = articleSubMenus.reduce<Record<ArticleSubView, ContentViewKey>>(
  (acc, item) => {
    acc[item.key] = item.contentKey
    return acc
  },
  {
    manage: 'articles-manage',
    trash: 'articles-trash',
    create: 'articles-create',
  },
)

const currentContentView = computed<ContentViewKey>(() => {
  if (currentView.value === 'overview') return 'overview'
  if (currentView.value === 'media') return 'media'
  if (currentView.value === 'comments') return 'comments'
  if (currentView.value === 'site') return 'site'

  return articleSubViewToContentKey[articleSubView.value] || 'articles-manage'
})

const panelComponentMap: Record<ContentViewKey, unknown> = {
  overview: OverviewPanel,
  'articles-manage': ArticleManagePanel,
  'articles-trash': ArticleTrashPanel,
  'articles-create': ArticleCreatePanel,
  media: MediaPanel,
  comments: CommentsPanel,
  site: SiteSettingsPanel,
}

const activePanelComponent = computed(() => panelComponentMap[currentContentView.value])

const activePanelProps = computed<Record<string, unknown>>(() => {
  switch (currentContentView.value) {
    case 'overview':
      return {
        articles: articles.value,
        deletedArticles: deletedArticles.value,
        comments: comments.value,
        loading: loading.value,
        errorMessage: errorMessage.value,
        formatArticleStatus,
      }
    case 'articles-manage':
      return {
        articles: articles.value,
        formatArticleStatus,
      }
    case 'articles-trash':
      return {
        deletedArticles: deletedArticles.value,
      }
    case 'articles-create':
      return {
        isAdmin: isAdmin.value,
        title: title.value,
        summary: summary.value,
        coverUrl: coverUrl.value,
        contentMarkdown: contentMarkdown.value,
        categoryId: categoryId.value,
        tagIdsText: tagIdsText.value,
        action: action.value,
      }
    case 'media':
      return {
        media: media.value,
      }
    case 'comments':
      return {
        comments: comments.value,
      }
    case 'site':
      return {
        siteTitle: siteTitle.value,
        siteSubtitle: siteSubtitle.value,
        icpBeian: icpBeian.value,
        copyrightText: copyrightText.value,
      }
    default:
      return {}
  }
})

const activePanelListeners = computed<Record<string, (...args: any[]) => void>>(() => {
  switch (currentContentView.value) {
    case 'articles-manage':
      return {
        moveToTrash,
      }
    case 'articles-trash':
      return {
        restore: restoreFromTrash,
        removePermanently,
      }
    case 'articles-create':
      return {
        'update:title': (value: string) => {
          title.value = value
        },
        'update:summary': (value: string) => {
          summary.value = value
        },
        'update:coverUrl': (value: string) => {
          coverUrl.value = value
        },
        'update:contentMarkdown': (value: string) => {
          contentMarkdown.value = value
        },
        'update:categoryId': (value: number) => {
          categoryId.value = value
        },
        'update:tagIdsText': (value: string) => {
          tagIdsText.value = value
        },
        'update:action': (value: 'draft' | 'submit' | 'publish') => {
          action.value = value
        },
        submit: createArticle,
      }
    case 'site':
      return {
        'update:siteTitle': (value: string) => {
          siteTitle.value = value
        },
        'update:siteSubtitle': (value: string) => {
          siteSubtitle.value = value
        },
        'update:icpBeian': (value: string) => {
          icpBeian.value = value
        },
        'update:copyrightText': (value: string) => {
          copyrightText.value = value
        },
        save: saveSite,
      }
    default:
      return {}
  }
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
