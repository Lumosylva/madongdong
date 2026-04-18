<template>
  <div class="admin-page">
    <header class="topbar">
      <div class="brand-block">
        <img v-if="siteLogo" :src="siteLogo" class="brand-logo" alt="site logo" />
        <span v-else class="brand-mark">MD</span>
        <h1>仪表盘</h1>
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

    <div class="dashboard-shell" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
      <aside class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
        <div class="sidebar-head">
          <button type="button" class="sidebar-toggle" :aria-label="sidebarToggleLabel" @click="toggleSidebar">
            <svg v-if="isSidebarCollapsed" class="sidebar-toggle-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M4 6h16M4 12h16M4 18h16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
            <svg v-else class="sidebar-toggle-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M15 6l-6 6 6 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>

        <nav class="sidebar-nav">
          <template v-for="item in visibleMainMenus" :key="item.key">
            <div
              v-if="item.key === 'articles'"
              ref="articleMenuGroupRef"
              class="sidebar-menu-group"
              @mouseenter="isSidebarCollapsed && openArticleFlyout($event)"
              @mouseleave="isSidebarCollapsed && closeArticleFlyoutDelayed()"
            >
              <a
                href="javascript:void(0)"
                :class="{ active: currentView === item.key }"
                @click="setView(item.key)"
              >
                <span class="sidebar-icon">{{ menuIconMap[item.key] }}</span>
                <span class="sidebar-text">{{ item.label }}</span>
                <span v-if="!isSidebarCollapsed" class="sidebar-chevron">›</span>
              </a>

              <transition name="sidebar-flyout-fade">
                <div
                  v-if="isSidebarCollapsed && articleFlyoutOpen"
                  class="sidebar-flyout"
                  :class="`flyout-${sidebarFlyoutSide}`"
                  @mouseenter="openArticleFlyout()"
                  @mouseleave="closeArticleFlyoutDelayed()"
                >
                  <div class="sidebar-flyout-header">
                    <strong class="sidebar-flyout-title">文章</strong>
                  </div>
                  <button
                    v-for="sub in articleSubMenus"
                    :key="sub.key"
                    type="button"
                    class="sidebar-flyout-item"
                    :class="{ active: articleSubView === sub.key }"
                    @click="setArticleSubView(sub.key)"
                  >
                    {{ sub.label }}
                  </button>
                </div>
              </transition>

              <div v-if="!isSidebarCollapsed && currentView === 'articles'" class="sidebar-subnav">
                <a
                  v-for="sub in articleSubMenus"
                  :key="sub.key"
                  href="javascript:void(0)"
                  :class="{ active: articleSubView === sub.key }"
                  @click="setArticleSubView(sub.key)"
                >
                  <span class="sidebar-text">{{ sub.label }}</span>
                </a>
              </div>
            </div>

            <a
              v-else
              href="javascript:void(0)"
              :class="{ active: currentView === item.key }"
              :data-label="item.label"
              @click="setView(item.key)"
            >
              <span class="sidebar-icon">{{ menuIconMap[item.key] }}</span>
              <span class="sidebar-text">{{ item.label }}</span>
            </a>
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
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { adminApi, API_ORIGIN } from '../api'
import ArticleCreatePanel from '../components/ArticleCreatePanel.vue'
import ArticleManagePanel from '../components/ArticleManagePanel.vue'
import ArticleTrashPanel from '../components/ArticleTrashPanel.vue'
import CategoryManagePanel from '../components/CategoryManagePanel.vue'
import CommentsPanel from '../components/CommentsPanel.vue'
import MediaPanel from '../components/MediaPanel.vue'
import OverviewPanel from '../components/OverviewPanel.vue'
import SiteSettingsPanel from '../components/SiteSettingsPanel.vue'
import type { AdminUser } from '../types'

type ThemeMode = 'light' | 'dark'
type ViewType = 'overview' | 'articles' | 'media' | 'comments' | 'site'
type ArticleSubView = 'manage' | 'trash' | 'create' | 'category'
type ContentViewKey =
  | 'overview'
  | 'articles-manage'
  | 'articles-trash'
  | 'articles-create'
  | 'articles-category'
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
  contentKey: Extract<ContentViewKey, 'articles-manage' | 'articles-trash' | 'articles-create' | 'articles-category'>
}

const router = useRouter()
const currentView = ref<ViewType>('overview')
const articleSubView = ref<ArticleSubView>('manage')
const isSidebarCollapsed = ref(false)
const articleFlyoutOpen = ref(false)
const articleFlyoutCloseTimer = ref<number | null>(null)
const currentUser = ref<AdminUser | null>(null)
const articles = ref<any[]>([])
const deletedArticles = ref<any[]>([])
const categories = ref<any[]>([])
const media = ref<any[]>([])
const comments = ref<any[]>([])
const siteTitle = ref('')
const siteSubtitle = ref('')
const siteLogo = ref('')
const icpBeian = ref('')
const copyrightText = ref('')
const loading = ref(false)
const errorMessage = ref('')

const articleSubmitting = ref(false)
const articleSubmitError = ref('')
const articleSubmitFocusField = ref<'title' | 'content' | null>(null)
const articleSubmitFocusNonce = ref(0)
let articleSubmitErrorTimer: number | null = null
const title = ref('')
const coverUrl = ref('')
const contentMarkdown = ref('')
const categoryId = ref(1)
const tagIdsText = ref('')
const action = ref<'draft' | 'submit' | 'publish'>('draft')
const articleDraftStorageKey = 'md-admin-article-draft'
const articleDraftSavedAt = ref<number | null>(null)
const articleDraftSessionSaved = ref(false)

const theme = ref<ThemeMode>('light')
const isUserMenuOpen = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)
const logoUploading = ref(false)
const logoUploadMessage = ref('')
const logoUploadStatus = ref<'success' | 'error' | ''>('')
const logoCropApplied = ref(false)
const mediaUploading = ref(false)
const mediaToastMessage = ref('')
const mediaToastStatus = ref<'success' | 'error' | ''>('')

const mainMenus: MainMenuItem[] = [
  { key: 'overview', label: '概览' },
  { key: 'articles', label: '文章' },
  { key: 'media', label: '媒体', adminOnly: true },
  { key: 'comments', label: '评论' },
  { key: 'site', label: '设置', adminOnly: true },
]

const articleSubMenus: ArticleSubMenuItem[] = [
  { key: 'manage', label: '所有文章', contentKey: 'articles-manage' },
  { key: 'create', label: '创建文章', contentKey: 'articles-create' },
  { key: 'category', label: '文章分类', contentKey: 'articles-category' },
  { key: 'trash', label: '垃圾箱', contentKey: 'articles-trash' },
]

const menuIconMap: Record<ViewType, string> = {
  overview: '⌂',
  articles: '✎',
  media: '◫',
  comments: '☍',
  site: '⚙',
}

const sidebarToggleLabel = computed(() => (isSidebarCollapsed.value ? '展开侧边菜单' : '收起侧边菜单'))
const sidebarFlyoutSide = ref<'right' | 'left'>('right')
const articleMenuGroupRef = ref<HTMLElement | null>(null)
const articleMenuGroupEl = ref<HTMLElement | null>(null)

const clearArticleFlyoutTimer = () => {
  if (articleFlyoutCloseTimer.value !== null) {
    window.clearTimeout(articleFlyoutCloseTimer.value)
    articleFlyoutCloseTimer.value = null
  }
}

const openArticleFlyout = (event?: MouseEvent) => {
  clearArticleFlyoutTimer()
  articleFlyoutOpen.value = true
  if (event?.currentTarget instanceof HTMLElement) {
    articleMenuGroupEl.value = event.currentTarget
  }
  updateFlyoutSide()
}

const closeArticleFlyoutDelayed = () => {
  clearArticleFlyoutTimer()
  articleFlyoutCloseTimer.value = window.setTimeout(() => {
    articleFlyoutOpen.value = false
    articleFlyoutCloseTimer.value = null
  }, 180)
}

const updateFlyoutSide = () => {
  const el = articleMenuGroupEl.value || articleMenuGroupRef.value
  if (!el || typeof el.getBoundingClientRect !== 'function') return
  const rect = el.getBoundingClientRect()
  const viewportWidth = window.innerWidth || document.documentElement.clientWidth || 0
  sidebarFlyoutSide.value = rect.right + 220 > viewportWidth ? 'left' : 'right'
}

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  articleFlyoutOpen.value = false
  clearArticleFlyoutTimer()
  localStorage.setItem('md-admin-sidebar-collapsed', isSidebarCollapsed.value ? '1' : '0')
  if (isSidebarCollapsed.value) {
    queueMicrotask(updateFlyoutSide)
  }
}

const setView = (view: ViewType) => {
  const targetMenu = mainMenus.find((item) => item.key === view)
  if (targetMenu?.adminOnly && !isAdmin.value) {
    return
  }
  currentView.value = view
  if (view !== 'articles') {
    articleFlyoutOpen.value = false
  }
  if (view === 'articles') {
    articleSubView.value = articleSubView.value || 'manage'
  }
}

const setArticleSubView = (subView: ArticleSubView) => {
  articleSubView.value = subView
  currentView.value = 'articles'
  articleFlyoutOpen.value = false
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
    category: 'articles-category',
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
  'articles-category': CategoryManagePanel,
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
        coverUrl: coverUrl.value,
        contentMarkdown: contentMarkdown.value,
        categoryId: categoryId.value,
        categories: categories.value,
        tagIdsText: tagIdsText.value,
        action: action.value,
        media: media.value,
        showToolbarName: isSidebarCollapsed.value,
        submitLoading: articleSubmitting.value,
        draftSavedAt: articleDraftSavedAt.value,
        draftSessionSaved: articleDraftSessionSaved.value,
        submitError: articleSubmitError.value,
        submitFocusField: articleSubmitFocusField.value,
      }
    case 'articles-category':
      return {
        categories: categories.value,
      }
    case 'media':
      return {
        media: media.value,
        uploading: mediaUploading.value,
        toastMessage: mediaToastMessage.value,
        toastStatus: mediaToastStatus.value,
      }
    case 'comments':
      return {
        comments: comments.value,
        formatCommentStatus,
      }
    case 'site':
      return {
        siteTitle: siteTitle.value,
        siteSubtitle: siteSubtitle.value,
        previewLogo: siteLogo.value,
        logoUploading: logoUploading.value,
        logoUploadMessage: logoUploadMessage.value,
        logoUploadStatus: logoUploadStatus.value,
        logoCropApplied: logoCropApplied.value,
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
        'update:coverUrl': (value: string) => {
          coverUrl.value = value
        },
        'select-cover': (value: string) => {
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
    case 'media':
      return {
        upload: uploadMedia,
        'delete-media': deleteMedia,
        'delete-media-batch': deleteMediaBatch,
      }
    case 'comments':
      return {
        approve: approveComment,
        reject: rejectComment,
        'bulk-approve': bulkApproveComments,
        'bulk-reject': bulkRejectComments,
        'bulk-delete': bulkDeleteComments,
      }
    case 'articles-category':
      return {
        create: createCategory,
        update: updateCategory,
        delete: deleteCategory,
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
        'select-logo': handleSiteLogoSelect,
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

const formatCommentStatus = (status: string) => {
  if (status === 'PENDING' || status === 'pending') return '待审核'
  if (status === 'APPROVED' || status === 'approved') return '已通过'
  if (status === 'REJECTED' || status === 'rejected') return '已拒绝'
  return status
}

const normalizeAssetUrl = (url: string | null | undefined) => {
  const value = String(url || '').trim()
  if (!value) return ''
  if (/^https?:\/\//i.test(value)) return value
  return `${API_ORIGIN}${value.startsWith('/') ? '' : '/'}${value}`
}

const applyAdminMeta = () => {
  const titleText = String(siteTitle.value || '').trim() || 'MaDongDong'
  document.title = `${titleText} - 仪表盘`

  if (!siteLogo.value) return
  let iconLink = document.querySelector("link[rel='icon']") as HTMLLinkElement | null
  if (!iconLink) {
    iconLink = document.createElement('link')
    iconLink.rel = 'icon'
    document.head.appendChild(iconLink)
  }
  iconLink.href = siteLogo.value
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

const handleGlobalKeyDown = (event: KeyboardEvent) => {
  const target = event.target as HTMLElement | null
  const tagName = target?.tagName?.toUpperCase() || ''
  const isEditable = tagName === 'INPUT' || tagName === 'TEXTAREA' || target?.isContentEditable

  if (currentContentView.value !== 'articles-create') return

  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 's') {
    event.preventDefault()
    persistArticleDraft()
    return
  }

  if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
    event.preventDefault()
    if (!articleSubmitting.value) {
      void createArticle()
    }
    return
  }

  if (event.key === 'Escape' && !isEditable) {
    articleFlyoutOpen.value = false
  }
}

const logout = async () => {
  isUserMenuOpen.value = false
  localStorage.removeItem('blog_admin_token')
  await router.push('/login')
}

const persistArticleDraft = () => {
  if (!title.value && !coverUrl.value && !contentMarkdown.value && !tagIdsText.value) {
    localStorage.removeItem(articleDraftStorageKey)
    articleDraftSavedAt.value = null
    articleDraftSessionSaved.value = false
    return
  }
  localStorage.setItem(
    articleDraftStorageKey,
    JSON.stringify({
      title: title.value,
      coverUrl: coverUrl.value,
      contentMarkdown: contentMarkdown.value,
      categoryId: categoryId.value,
      tagIdsText: tagIdsText.value,
      action: action.value,
    }),
  )
  articleDraftSavedAt.value = Date.now()
  articleDraftSessionSaved.value = true
}

let articleDraftSaveTimer: number | null = null
const scheduleArticleDraftSave = () => {
  if (articleDraftSaveTimer !== null) {
    window.clearTimeout(articleDraftSaveTimer)
  }
  articleDraftSaveTimer = window.setTimeout(() => {
    persistArticleDraft()
    articleDraftSaveTimer = null
  }, 500)
}

const loadAll = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const meRes = await adminApi.getMe()
    currentUser.value = meRes.data
    const [articleRes, deletedRes, categoryRes, mediaRes, commentRes, siteRes] = await Promise.all([
      adminApi.getArticles(),
      adminApi.getDeletedArticles(),
      adminApi.getCategories(),
      adminApi.getMedia(),
      adminApi.getComments(),
      adminApi.getSiteSettings(),
    ])
    articles.value = articleRes.data
    deletedArticles.value = deletedRes.data
    categories.value = categoryRes.data
    media.value = mediaRes.data
    comments.value = commentRes.data
    siteTitle.value = siteRes.data.site_title
    siteSubtitle.value = siteRes.data.site_subtitle || ''
    siteLogo.value = normalizeAssetUrl(siteRes.data.site_logo || '')
    applyAdminMeta()
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

const approveComment = async (commentId: number) => {
  const target = comments.value.find((item) => item.id === commentId)
  if (!target || String(target.status).toUpperCase() === 'APPROVED') return
  await adminApi.approveComment(commentId)
  await loadAll()
}

const bulkApproveComments = async (commentIds: number[]) => {
  const targets = commentIds.filter((commentId) => {
    const item = comments.value.find((comment) => comment.id === commentId)
    return item && String(item.status).toUpperCase() !== 'APPROVED'
  })
  if (!targets.length) return
  await Promise.all(targets.map((commentId) => adminApi.approveComment(commentId)))
  await loadAll()
}

const rejectComment = async (commentId: number) => {
  const target = comments.value.find((item) => item.id === commentId)
  if (!target || String(target.status).toUpperCase() === 'REJECTED') return
  await adminApi.rejectComment(commentId)
  await loadAll()
}

const bulkRejectComments = async (commentIds: number[]) => {
  const targets = commentIds.filter((commentId) => {
    const item = comments.value.find((comment) => comment.id === commentId)
    return item && String(item.status).toUpperCase() !== 'REJECTED'
  })
  if (!targets.length) return
  await Promise.all(targets.map((commentId) => adminApi.rejectComment(commentId)))
  await loadAll()
}

const bulkDeleteComments = async (commentIds: number[]) => {
  const targets = commentIds.filter((commentId) => {
    const item = comments.value.find((comment) => comment.id === commentId)
    return item && String(item.status).toUpperCase() === 'REJECTED'
  })
  if (!targets.length) return
  await adminApi.deleteComments(targets)
  await loadAll()
}

const createCategory = async (payload: { name: string; slug: string; description: string | null }) => {
  await adminApi.createCategory(payload)
  await loadAll()
}

watch([title, coverUrl, contentMarkdown, categoryId, tagIdsText, action], () => {
  scheduleArticleDraftSave()
})

const updateCategory = async (payload: { id: number; name: string; slug: string; description: string | null }) => {
  await adminApi.updateCategory(payload.id, {
    name: payload.name,
    slug: payload.slug,
    description: payload.description,
  })
  await loadAll()
}

const deleteCategory = async (categoryIdValue: number) => {
  if (!confirm('确认删除该分类吗？')) return
  await adminApi.deleteCategory(categoryIdValue)
  await loadAll()
}

const uploadMedia = async (file: File) => {
  if (mediaUploading.value) return
  mediaUploading.value = true
  mediaToastStatus.value = ''
  mediaToastMessage.value = ''

  try {
    await adminApi.uploadMediaFile(file)
    mediaToastStatus.value = 'success'
    mediaToastMessage.value = '媒体上传成功'
    await loadAll()
  } catch (error) {
    mediaToastStatus.value = 'error'
    mediaToastMessage.value = error instanceof Error ? error.message : '媒体上传失败'
  } finally {
    mediaUploading.value = false
    setTimeout(() => {
      mediaToastMessage.value = ''
      mediaToastStatus.value = ''
    }, 2400)
  }
}

const deleteMedia = async (mediaId: number) => {
  await deleteMediaBatch([mediaId])
}

const deleteMediaBatch = async (mediaIds: number[]) => {
  if (!mediaIds.length) return
  try {
    await adminApi.deleteMediaFiles(mediaIds)
    mediaToastStatus.value = 'success'
    mediaToastMessage.value = mediaIds.length > 1 ? `已删除 ${mediaIds.length} 项媒体` : '媒体已删除'
    await loadAll()
  } catch (error) {
    mediaToastStatus.value = 'error'
    mediaToastMessage.value = error instanceof Error ? error.message : '删除媒体失败'
  }
}

const cropImageTo64 = async (file: File): Promise<File> => {
  const dataUrl = await new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result || ''))
    reader.onerror = () => reject(new Error('读取图片失败'))
    reader.readAsDataURL(file)
  })

  const image = await new Promise<HTMLImageElement>((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = () => reject(new Error('加载图片失败'))
    img.src = dataUrl
  })

  const size = Math.min(image.width, image.height)
  const sx = Math.floor((image.width - size) / 2)
  const sy = Math.floor((image.height - size) / 2)

  const canvas = document.createElement('canvas')
  canvas.width = 64
  canvas.height = 64
  const ctx = canvas.getContext('2d')
  if (!ctx) throw new Error('无法处理图片')
  ctx.drawImage(image, sx, sy, size, size, 0, 0, 64, 64)

  const blob = await new Promise<Blob>((resolve, reject) => {
    canvas.toBlob((value) => {
      if (value) resolve(value)
      else reject(new Error('导出图片失败'))
    }, 'image/png')
  })

  return new File([blob], `${file.name.replace(/\.[^.]+$/, '')}-64x64.png`, { type: 'image/png' })
}

const handleSiteLogoSelect = async (file: File) => {
  const supported = ['image/png', 'image/jpeg', 'image/svg+xml']
  if (!supported.includes(file.type)) {
    logoUploadStatus.value = 'error'
    logoUploadMessage.value = '仅支持 PNG、JPG、SVG 格式'
    return
  }

  if (logoUploading.value) return
  logoUploading.value = true
  logoUploadStatus.value = ''
  logoUploadMessage.value = ''
  logoCropApplied.value = false

  try {
    let uploadFile = file
    if (file.type !== 'image/svg+xml') {
      uploadFile = await cropImageTo64(file)
      logoCropApplied.value = true
    }

    const uploaded = await adminApi.uploadMediaFile(uploadFile)
    siteLogo.value = normalizeAssetUrl(String(uploaded.data?.url || ''))
    logoUploadStatus.value = 'success'
    logoUploadMessage.value = logoCropApplied.value ? 'Logo 上传成功（已裁剪 64×64）' : 'Logo 上传成功'
  } catch (error) {
    logoUploadStatus.value = 'error'
    logoUploadMessage.value = error instanceof Error ? error.message : 'Logo 上传失败'
  } finally {
    logoUploading.value = false
    setTimeout(() => {
      logoUploadMessage.value = ''
      logoUploadStatus.value = ''
    }, 2400)
  }
}

const saveSite = async () => {
  await adminApi.updateSiteSettings({
    site_title: siteTitle.value,
    site_logo: siteLogo.value || null,
    site_subtitle: siteSubtitle.value,
    icp_beian: icpBeian.value,
    copyright_text: copyrightText.value,
    homepage_page_size: 10,
    comment_requires_review: true,
  })
  await loadAll()
}

const tagSlugify = (value: string) =>
  value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\u4e00-\u9fa5\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '') || 'tag'

const extractSummary = (markdown: string, maxLength = 120) => {
  const text = String(markdown || '')
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/!\[[^\]]*]\([^)]+\)/g, ' ')
    .replace(/\[([^\]]+)]\([^)]+\)/g, '$1')
    .replace(/^\s{0,3}#{1,6}\s+/gm, '')
    .replace(/^\s{0,3}>\s?/gm, '')
    .replace(/^\s{0,3}[-*+]\s+/gm, '')
    .replace(/^\s{0,3}\d+\.\s+/gm, '')
    .replace(/\n{2,}/g, '\n')
    .replace(/\s+/g, ' ')
    .trim()

  if (!text) return '暂无摘要'
  if (text.length <= maxLength) return text

  const sliced = text.slice(0, maxLength)
  const punctIndex = Math.max(
    sliced.lastIndexOf('。'),
    sliced.lastIndexOf('！'),
    sliced.lastIndexOf('？'),
    sliced.lastIndexOf('；'),
    sliced.lastIndexOf('.'),
  )

  if (punctIndex > Math.floor(maxLength * 0.6)) {
    return sliced.slice(0, punctIndex + 1)
  }

  return `${sliced.trimEnd()}…`
}

const resolveTagIdsByNames = async (rawInput: string) => {
  const names = rawInput
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)

  if (!names.length) return [] as number[]

  const dedupNames = Array.from(new Set(names))
  const tagsRes = await adminApi.getTags()
  const existingTags = tagsRes.data || []
  const existingMap = new Map<string, any>()
  for (const tag of existingTags) {
    const key = String(tag.name || '').trim().toLowerCase()
    if (key) existingMap.set(key, tag)
  }

  const resolvedIds: number[] = []
  for (const name of dedupNames) {
    const key = name.toLowerCase()
    if (existingMap.has(key)) {
      resolvedIds.push(existingMap.get(key).id)
      continue
    }

    const created = await adminApi.createTag({
      name,
      slug: tagSlugify(name),
    })
    resolvedIds.push(created.data.id)
    existingMap.set(key, created.data)
  }

  return resolvedIds
}

const clearArticleDraft = () => {
  localStorage.removeItem(articleDraftStorageKey)
  articleDraftSavedAt.value = null
  articleDraftSessionSaved.value = false
}

const getArticleCreateErrorMessage = (error: unknown) => {
  const rawMessage = error instanceof Error ? error.message : String(error || '')
  const message = rawMessage.replace(/^Error:\s*/i, '')

  if (message.includes('422')) {
    if (message.includes('title') || message.includes('标题')) return '请先填写文章标题'
    if (message.includes('content_markdown') || message.includes('正文')) return '请先填写文章正文'
    if (message.includes('category_id') || message.includes('分类')) return '请选择文章分类'
    return '提交内容不完整，请检查标题、正文和分类后再试'
  }

  if (message.includes('401')) return '登录已失效，请重新登录'
  if (message.includes('403')) return '当前账号没有提交权限'
  if (message.includes('500')) return '提交失败，服务器暂时出了点问题，请稍后重试'

  return message || '提交失败，请稍后重试'
}

const getArticleCreateFocusField = (error: unknown) => {
  const raw = error instanceof Error ? error.message : String(error || '')
  if (raw.includes('标题') || raw.includes('title') || raw.includes('422')) return 'title'
  if (raw.includes('正文') || raw.includes('content')) return 'content'
  if (raw.includes('category_id') || raw.includes('分类')) return 'title'
  return null
}

const showArticleSubmitError = (message: string, focusField: 'title' | 'content' | null = null) => {
  articleSubmitError.value = message
  articleSubmitFocusField.value = focusField
  articleSubmitFocusNonce.value += 1
  if (articleSubmitErrorTimer !== null) {
    window.clearTimeout(articleSubmitErrorTimer)
  }
  articleSubmitErrorTimer = window.setTimeout(() => {
    articleSubmitError.value = ''
    articleSubmitFocusField.value = null
    articleSubmitErrorTimer = null
  }, 3000)
}

const createArticle = async () => {
  if (articleSubmitting.value) return
  articleSubmitting.value = true
  articleSubmitError.value = ''
  const finalAction = isAdmin.value
    ? (action.value === 'publish' ? 'publish' : 'draft')
    : (action.value === 'submit' ? 'submit' : 'draft')

  try {
    const trimmedTitle = title.value.trim()
    const trimmedContent = contentMarkdown.value.trim()
    if (!trimmedTitle) {
      showArticleSubmitError('请先填写文章标题', 'title')
      return
    }
    if (!trimmedContent) {
      showArticleSubmitError('请先填写文章正文', 'content')
      return
    }

    const autoSummary = extractSummary(contentMarkdown.value, 120)
    const resolvedTagIds = await resolveTagIdsByNames(tagIdsText.value)

    await adminApi.createArticle({
      title: trimmedTitle,
      summary: autoSummary || '暂无摘要',
      content_markdown: contentMarkdown.value,
      cover_url: coverUrl.value || null,
      category_id: categoryId.value,
      tag_ids: resolvedTagIds,
      action: finalAction,
    })
    title.value = ''
    coverUrl.value = ''
    contentMarkdown.value = ''
    tagIdsText.value = ''
    clearArticleDraft()
    if (articleSubmitErrorTimer !== null) {
      window.clearTimeout(articleSubmitErrorTimer)
      articleSubmitErrorTimer = null
    }
    articleSubmitError.value = ''
    articleSubmitFocusField.value = null
    currentView.value = 'articles'
    await nextTick()
    await loadAll()
  } catch (error) {
    showArticleSubmitError(getArticleCreateErrorMessage(error), getArticleCreateFocusField(error))
  } finally {
    articleSubmitting.value = false
  }
}

onMounted(async () => {
  const storedTheme = localStorage.getItem('md-admin-theme')
  const storedSidebarState = localStorage.getItem('md-admin-sidebar-collapsed')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  isSidebarCollapsed.value = storedSidebarState === '1'
  await loadAll()
  action.value = isAdmin.value ? 'publish' : 'submit'
  document.addEventListener('click', handleDocumentClick)
  document.addEventListener('keydown', handleGlobalKeyDown)
  window.addEventListener('resize', updateFlyoutSide)
  updateFlyoutSide()

  const savedDraftRaw = localStorage.getItem(articleDraftStorageKey)
  if (savedDraftRaw) {
    try {
      const savedDraft = JSON.parse(savedDraftRaw) as {
        title?: string
        coverUrl?: string
        contentMarkdown?: string
        categoryId?: number
        tagIdsText?: string
        action?: 'draft' | 'submit' | 'publish'
      }
      if (typeof savedDraft.title === 'string') title.value = savedDraft.title
      if (typeof savedDraft.coverUrl === 'string') coverUrl.value = savedDraft.coverUrl
      if (typeof savedDraft.contentMarkdown === 'string') contentMarkdown.value = savedDraft.contentMarkdown
      if (typeof savedDraft.categoryId === 'number') categoryId.value = savedDraft.categoryId
      if (typeof savedDraft.tagIdsText === 'string') tagIdsText.value = savedDraft.tagIdsText
      if (savedDraft.action) action.value = savedDraft.action
      articleDraftSavedAt.value = null
      articleDraftSessionSaved.value = false
    } catch {
      localStorage.removeItem(articleDraftStorageKey)
    }
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
  document.removeEventListener('keydown', handleGlobalKeyDown)
  window.removeEventListener('resize', updateFlyoutSide)
  clearArticleFlyoutTimer()
  if (articleDraftSaveTimer !== null) {
    window.clearTimeout(articleDraftSaveTimer)
    articleDraftSaveTimer = null
  }
  if (articleSubmitErrorTimer !== null) {
    window.clearTimeout(articleSubmitErrorTimer)
    articleSubmitErrorTimer = null
  }
})
</script>
