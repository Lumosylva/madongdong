<template>
  <div class="admin-page">
    <AdminTopbar
      :site-title="siteTitle"
      :site-logo="siteLogo"
      :display-name="displayName"
      :role-label="roleLabel"
      :is-admin="isAdmin"
      @open-profile="openProfile"
      @logout="logout"
    />

    <div v-if="siteToastMessage" class="panel toast-panel" :class="`toast-${siteToastStatus}`">
      <span class="toast-icon" aria-hidden="true">{{ siteToastStatus === 'success' ? '✓' : '!' }}</span>
      <span class="toast-text">{{ siteToastMessage }}</span>
    </div>

    <div class="dashboard-shell" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
      <AdminSidebar
        :current-view="currentView"
        :article-sub-view="articleSubView"
        :editing-article-id="editingArticleId"
        :is-sidebar-collapsed="isSidebarCollapsed"
        :is-admin="isAdmin"
        @toggle-sidebar="toggleSidebar"
        @set-view="setView"
        @set-article-sub-view="setArticleSubView"
      />

      <main class="dashboard-main">
        <ProfilePanel
          v-if="currentView === 'profile'"
          :user="currentUser"
          @save="updateProfile"
        />
        <component v-else :is="activePanelComponent" v-bind="activePanelProps" v-on="activePanelListeners" />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { adminApi, API_ORIGIN, clearAdminAuthCookies } from '../api'
import { buildPageTitle, setSiteSetting } from '../site-meta'
import AdminTopbar from '../components/AdminTopbar.vue'
import AdminSidebar from '../components/AdminSidebar.vue'
import ArticleCreatePanel from '../components/ArticleCreatePanel.vue'
import ArticleManagePanel from '../components/ArticleManagePanel.vue'
import ArticleTrashPanel from '../components/ArticleTrashPanel.vue'
import CategoryManagePanel from '../components/CategoryManagePanel.vue'
import CommentsPanel from '../components/CommentsPanel.vue'
import FriendLinksPanel from '../components/FriendLinksPanel.vue'
import MediaPanel from '../components/MediaPanel.vue'
import OverviewPanel from '../components/OverviewPanel.vue'
import SiteSettingsPanel from '../components/SiteSettingsPanel.vue'
import UserManagementPanel from '../components/UserManagementPanel.vue'
import ProfilePanel from '../components/ProfilePanel.vue'
import type { AdminUser, FriendLinkItem } from '../types'

type ViewType = 'overview' | 'articles' | 'media' | 'comments' | 'friend-links' | 'users' | 'profile' | 'site'
type ArticleSubView = 'manage' | 'trash' | 'create' | 'edit' | 'category'
type ContentViewKey =
  | 'overview'
  | 'articles-manage'
  | 'articles-trash'
  | 'articles-create'
  | 'articles-edit'
  | 'articles-category'
  | 'media'
  | 'comments'
  | 'friend-links'
  | 'users'
  | 'site'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const currentView = ref<ViewType>('overview')
const articleSubView = ref<ArticleSubView>('manage')

const viewToPath: Record<ViewType, string> = {
  overview: '/',
  articles: '/articles',
  media: '/media',
  comments: '/comments',
  'friend-links': '/friend-links',
  users: '/users',
  profile: '/profile',
  site: '/site',
}

const subViewToPath: Record<ArticleSubView, string> = {
  manage: '',
  create: '/create',
  edit: '/edit',
  category: '/category',
  trash: '/trash',
}

const pathToView = (path: string): { view: ViewType; sub: ArticleSubView } => {
  const seg = path.replace(/^\/+/, '').split('/')[0] || ''
  const viewMap: Record<string, ViewType> = {
    '': 'overview', overview: 'overview', articles: 'articles', media: 'media',
    comments: 'comments', 'friend-links': 'friend-links', users: 'users',
    profile: 'profile', site: 'site',
  }
  const view = viewMap[seg] || 'overview'
  if (view !== 'articles') return { view, sub: 'manage' }
  const subSeg = path.replace(/^\/+/, '').split('/')[1] || ''
  const subMap: Record<string, ArticleSubView> = {
    '': 'manage', create: 'create', edit: 'edit', category: 'category', trash: 'trash',
  }
  return { view, sub: subMap[subSeg] || 'manage' }
}

const pushViewUrl = (view: ViewType, sub?: ArticleSubView) => {
  const base = viewToPath[view]
  const subPath = view === 'articles' && sub ? subViewToPath[sub] : ''
  router.replace(base + subPath)
}
const isSidebarCollapsed = ref(false)
const currentUser = ref<AdminUser | null>(null)
const articles = ref<any[]>([])
const deletedArticles = ref<any[]>([])
const categories = ref<any[]>([])
const media = ref<any[]>([])
const folders = ref<any[]>([])
const currentFolderId = ref<number | null | undefined>(undefined)
const comments = ref<any[]>([])
const friendLinks = ref<FriendLinkItem[]>([])
const users = ref<any[]>([])
const siteTitle = ref('')
const siteSubtitle = ref('')
const siteLogo = ref('')
const icpBeian = ref('')
const policeBeian = ref('')
const copyrightText = ref('')
const homepageBgmUrl = ref('')
const homepageHeroImage = ref('')
const serverDomain = ref('')
const serverSecretKey = ref('')
const serverDatabaseUrl = ref('')
const serverUploadDir = ref('')
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
const defaultAction = computed<'draft' | 'submit' | 'publish'>(() => (isAdmin.value ? 'publish' : 'draft'))
const action = ref<'draft' | 'submit' | 'publish'>('draft')
const articleDraftStorageKey = 'md-admin-article-draft'
const articleDraftSavedAt = ref<number | null>(null)
const articleDraftSessionSaved = ref(false)
const editingArticleId = ref<number | null>(null)
const editingArticleTitle = ref('')

const siteToastMessage = ref('')
const siteToastStatus = ref<'success' | 'error' | ''>('')
let siteToastTimer: number | null = null
const mediaUploading = ref(false)
const mediaToastMessage = ref('')
const mediaToastStatus = ref<'success' | 'error' | ''>('')
const logoUploading = ref(false)
const logoUploadMessage = ref('')
const logoUploadStatus = ref<'success' | 'error' | ''>('')
const logoCropApplied = ref(false)

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  localStorage.setItem('md-admin-sidebar-collapsed', isSidebarCollapsed.value ? '1' : '0')
}

const setView = (view: ViewType) => {
  currentView.value = view
  if (view === 'articles') {
    articleSubView.value = articleSubView.value || 'manage'
  }
  pushViewUrl(view, view === 'articles' ? articleSubView.value : undefined)
}

const setArticleSubView = (subView: ArticleSubView) => {
  if (subView === 'edit' && !editingArticleId.value) {
    articleSubView.value = 'create'
    currentView.value = 'articles'
    title.value = ''
    coverUrl.value = ''
    contentMarkdown.value = ''
    tagIdsText.value = ''
    action.value = defaultAction.value
    clearArticleDraft()
    resetArticleEditorState()
    pushViewUrl('articles', 'create')
    return
  }
  if (subView === 'create') {
    editingArticleId.value = null
    editingArticleTitle.value = ''
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
        articleDraftSessionSaved.value = true
      } catch {
        title.value = ''
        coverUrl.value = ''
        contentMarkdown.value = ''
        tagIdsText.value = ''
        action.value = defaultAction.value
        clearArticleDraft()
      }
    } else {
      title.value = ''
      coverUrl.value = ''
      contentMarkdown.value = ''
      tagIdsText.value = ''
      action.value = defaultAction.value
      clearArticleDraft()
    }
    resetArticleEditorState()
  }
  articleSubView.value = subView
  currentView.value = 'articles'
  pushViewUrl('articles', subView)
}

const isAdmin = computed(() =>
  currentUser.value?.roles.some((role) => role.name === 'admin' || role.name === '系统管理员') ?? false,
)

const isAuthor = computed(() =>
  currentUser.value?.roles.some((role) => role.name === 'author' || role.name === '内容作者') ?? false,
)

const displayName = computed(() => currentUser.value?.nickname || currentUser.value?.username || t('nav.dashboard'))

const roleLabel = computed(() => {
  if (isAdmin.value) return t('role.admin')
  if (isAuthor.value) return t('role.author')
  return t('role.reader')
})

const articleSubViewToContentKey: Record<ArticleSubView, ContentViewKey> = {
  manage: 'articles-manage',
  trash: 'articles-trash',
  create: 'articles-create',
  edit: 'articles-edit',
  category: 'articles-category',
}

const currentContentView = computed<ContentViewKey>(() => {
  if (currentView.value === 'overview') return 'overview'
  if (currentView.value === 'media') return 'media'
  if (currentView.value === 'comments') return 'comments'
  if (currentView.value === 'friend-links') return 'friend-links'
  if (currentView.value === 'users') return 'users'
  if (currentView.value === 'site') return 'site'
  return articleSubViewToContentKey[articleSubView.value] || 'articles-manage'
})

const panelComponentMap: Record<ContentViewKey, unknown> = {
  overview: OverviewPanel,
  'articles-manage': ArticleManagePanel,
  'articles-trash': ArticleTrashPanel,
  'articles-create': ArticleCreatePanel,
  'articles-edit': ArticleCreatePanel,
  'articles-category': CategoryManagePanel,
  media: MediaPanel,
  comments: CommentsPanel,
  'friend-links': FriendLinksPanel,
  users: UserManagementPanel,
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
        friendLinks: friendLinks.value,
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
        editorMode: 'create',
        editorTitle: t('articleSub.create'),
      }
    case 'articles-edit':
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
        editorMode: 'edit',
        editorTitle: t('articleSub.edit'),
      }
    case 'articles-category':
      return {
        categories: categories.value,
      }
    case 'media':
      return {
        media: media.value,
        folders: folders.value,
        uploading: mediaUploading.value,
        toastMessage: mediaToastMessage.value,
        toastStatus: mediaToastStatus.value,
      }
    case 'comments':
      return {
        comments: comments.value,
        formatCommentStatus,
      }
    case 'friend-links':
      return {
        links: friendLinks.value,
        refreshing: friendLinksRefreshing.value,
      }
    case 'users':
      return {
        users: users.value,
        refreshing: usersRefreshing.value,
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
        policeBeian: policeBeian.value,
        copyrightText: copyrightText.value,
        homepageBgmUrl: homepageBgmUrl.value,
        homepageHeroImage: homepageHeroImage.value,
        media: media.value,
        serverDomain: serverDomain.value,
        serverSecretKey: serverSecretKey.value,
        serverDatabaseUrl: serverDatabaseUrl.value,
        serverUploadDir: serverUploadDir.value,
      }
    default:
      return {}
  }
})

const activePanelListeners = computed(() => {
  switch (currentContentView.value) {
    case 'overview':
      return {
        navigate: handleOverviewNavigate,
        'edit-article': editArticle,
      }
    case 'articles-manage':
      return {
        moveToTrash,
        editArticle,
      }
    case 'articles-trash':
      return {
        restore: restoreFromTrash,
        removePermanently,
      }
    case 'articles-create':
    case 'articles-edit':
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
        'select-folder': selectMediaFolder,
        'create-folder': createMediaFolder,
        'rename-folder': renameMediaFolder,
        'delete-folder': deleteMediaFolder,
        'move-media': moveMedia,
      }
    case 'comments':
      return {
        approve: approveComment,
        reject: rejectComment,
        delete: deleteComment,
        'bulk-approve': bulkApproveComments,
        'bulk-reject': bulkRejectComments,
        'bulk-delete': bulkDeleteComments,
        refresh: refreshComments,
      }
    case 'friend-links':
      return {
        approve: approveFriendLink,
        reject: rejectFriendLink,
        delete: deleteFriendLink,
        edit: editFriendLink,
        refresh: refreshFriendLinks,
      }
    case 'articles-category':
      return {
        create: createCategory,
        update: updateCategory,
        delete: deleteCategory,
      }
    case 'users':
      return {
        create: createUser,
        update: updateUser,
        delete: deleteUsers,
        batchChangeRole: batchChangeUsersRole,
        refresh: refreshUsers,
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
        'update:policeBeian': (value: string) => {
          policeBeian.value = value
        },
        'update:copyrightText': (value: string) => {
          copyrightText.value = value
        },
        'update:homepageBgmUrl': (value: string) => {
          homepageBgmUrl.value = value
        },
        'update:homepageHeroImage': (value: string) => {
          homepageHeroImage.value = value
        },
        'update:serverDomain': (value: string) => {
          serverDomain.value = value
        },
        'update:serverSecretKey': (value: string) => {
          serverSecretKey.value = value
        },
        'detect-domain': () => {
          serverDomain.value = window.location.hostname
        },
        'select-logo': handleSiteLogoSelect,
        save: saveSite,
        'save-server-config': saveServerConfig,
      }
    default:
      return {}
  }
})

const formatArticleStatus = (status: string) => {
  if (status === 'PUBLISHED' || status === 'published') return t('status.published')
  if (status === 'DRAFT' || status === 'draft') return t('status.draft')
  if (status === 'PENDING_REVIEW' || status === 'pending_review' || status === 'pending') return t('status.pending')
  if (status === 'REJECTED' || status === 'rejected') return t('status.rejected')
  return status
}

const normalizeArticleAction = (status: string): 'draft' | 'submit' | 'publish' => {
  const normalized = String(status || '').trim().toLowerCase()
  if (normalized === 'published') return 'publish'
  if (normalized === 'pending_review' || normalized === 'pending' || normalized === 'rejected') return 'submit'
  return 'draft'
}

const formatCommentStatus = (status: string) => {
  if (status === 'PENDING' || status === 'pending') return t('status.pending')
  if (status === 'APPROVED' || status === 'approved') return t('status.approved')
  if (status === 'REJECTED' || status === 'rejected') return t('status.rejectedComment')
  return status
}

const normalizeAssetUrl = (url: string | null | undefined) => {
  const value = String(url || '').trim()
  if (!value) return ''
  if (/^https?:\/\//i.test(value)) return value
  return `${API_ORIGIN}${value.startsWith('/') ? '' : '/'}${value}`
}

const applyAdminMeta = () => {
  document.title = buildPageTitle(t('nav.dashboard'))

  if (!siteLogo.value) return
  let iconLink = document.querySelector("link[rel='icon']") as HTMLLinkElement | null
  if (!iconLink) {
    iconLink = document.createElement('link')
    iconLink.rel = 'icon'
    document.head.appendChild(iconLink)
  }
  iconLink.href = siteLogo.value
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
    // Escape key handler
  }
}

const handleOverviewNavigate = (target: string) => {
  if (target === 'articles-create') {
    setArticleSubView('create')
  } else if (target === 'articles-manage') {
    setView('articles')
  } else if (target === 'articles-trash') {
    setArticleSubView('trash')
  } else if (target === 'media') {
    setView('media')
  } else if (target === 'comments') {
    setView('comments')
  } else if (target === 'friend-links') {
    setView('friend-links')
  } else if (target === 'site') {
    setView('site')
  }
}

const openProfile = async () => {
  currentView.value = 'profile'
  pushViewUrl('profile')
}

const logout = async () => {
  try {
    await adminApi.logout()
  } catch {
    // ignore
  }
  clearAdminAuthCookies()
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
    const [articleRes, deletedRes, categoryRes, mediaRes, folderRes, commentRes, linkRes, siteRes, userRes, serverCfgRes] = await Promise.all([
      adminApi.getArticles(),
      adminApi.getDeletedArticles(),
      adminApi.getCategories(),
      adminApi.getMedia(currentFolderId.value !== undefined ? { folderId: currentFolderId.value ?? undefined, unorganized: currentFolderId.value === null } : undefined),
      adminApi.getFolders(),
      adminApi.getComments(),
      adminApi.getFriendLinks(),
      adminApi.getSiteSettings(),
      isAdmin.value ? adminApi.getUsers() : Promise.resolve({ data: [] }),
      adminApi.getServerConfig(),
    ])
    articles.value = articleRes.data
    deletedArticles.value = deletedRes.data
    categories.value = categoryRes.data
    media.value = mediaRes.data
    folders.value = folderRes.data
    comments.value = commentRes.data.items || commentRes.data
    friendLinks.value = linkRes.data || []
    users.value = userRes.data || []
    siteTitle.value = siteRes.data.site_title
    siteSubtitle.value = siteRes.data.site_subtitle || ''
    siteLogo.value = normalizeAssetUrl(siteRes.data.site_logo || '')
    setSiteSetting(siteRes.data)
    applyAdminMeta()
    icpBeian.value = siteRes.data.icp_beian || ''
    policeBeian.value = siteRes.data.police_beian || ''
    copyrightText.value = siteRes.data.copyright_text || ''
    homepageBgmUrl.value = siteRes.data.homepage_bgm_url || ''
    homepageHeroImage.value = siteRes.data.homepage_hero_image || ''
    if (serverCfgRes.data) {
      serverDomain.value = serverCfgRes.data.site_domain || ''
      serverDatabaseUrl.value = serverCfgRes.data.database_url || ''
      serverUploadDir.value = serverCfgRes.data.upload_dir || ''
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : t('toast.loadFailed')
    if (message.includes('401') || message.includes('未提供认证令牌') || message.includes('无效的认证令牌')) {
      clearAdminAuthCookies()
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
  if (!confirm(t('confirm.deleteArticle'))) return
  await adminApi.permanentlyDeleteArticle(articleId)
  await loadAll()
}

const approveComment = async (commentId: number) => {
  const target = comments.value.find((item) => item.id === commentId)
  if (!target || String(target.status).toUpperCase() === 'APPROVED') return
  await adminApi.approveComment(commentId)
  await loadAll()
}

const friendLinksRefreshing = ref(false)

const refreshFriendLinks = async () => {
  if (friendLinksRefreshing.value) return
  friendLinksRefreshing.value = true
  try {
    const res = await adminApi.getFriendLinks()
    friendLinks.value = res.data || []
  } catch {
    // ignore
  } finally {
    friendLinksRefreshing.value = false
  }
}

const approveFriendLink = async (linkId: number) => {
  const target = friendLinks.value.find((item) => item.id === linkId)
  if (!target || String(target.status).toLowerCase() === 'approved') return
  await adminApi.updateFriendLink(linkId, { status: 'approved' })
  await loadAll()
}

const rejectFriendLink = async (linkId: number) => {
  const target = friendLinks.value.find((item) => item.id === linkId)
  if (!target || String(target.status).toLowerCase() === 'rejected') return
  await adminApi.updateFriendLink(linkId, { status: 'rejected' })
  await loadAll()
}

const deleteFriendLink = async (linkId: number) => {
  if (!confirm(t('confirm.deleteFriendLink'))) return
  await adminApi.deleteFriendLink(linkId)
  await loadAll()
}

const editFriendLink = async (linkId: number, payload: { name: string; email: string; description: string }) => {
  await adminApi.updateFriendLink(linkId, payload)
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

const deleteComment = async (commentId: number) => {
  if (!confirm(t('confirm.deleteComment'))) return
  await adminApi.deleteComments([commentId])
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

const refreshComments = async () => {
  try {
    const res = await adminApi.getComments()
    comments.value = res.data.items || res.data
  } catch {
    // ignore
  }
}

const createCategory = async (payload: { name: string; slug: string; description: string | null; parent_id: number | null }) => {
  await adminApi.createCategory(payload)
  await loadAll()
}

watch([title, coverUrl, contentMarkdown, categoryId, tagIdsText, action], () => {
  scheduleArticleDraftSave()
})

const updateCategory = async (payload: { id: number; name: string; slug: string; description: string | null; parent_id: number | null }) => {
  await adminApi.updateCategory(payload.id, {
    name: payload.name,
    slug: payload.slug,
    description: payload.description,
    parent_id: payload.parent_id,
  })
  await loadAll()
}

const deleteCategory = async (categoryIdValue: number) => {
  if (!confirm(t('confirm.deleteCategory'))) return
  await adminApi.deleteCategory(categoryIdValue)
  await loadAll()
}

const usersRefreshing = ref(false)

const refreshUsers = async () => {
  if (usersRefreshing.value) return
  usersRefreshing.value = true
  try {
    const res = await adminApi.getUsers()
    users.value = res.data || []
  } catch {
    // ignore
  } finally {
    usersRefreshing.value = false
  }
}

const createUser = async (payload: Record<string, unknown>) => {
  await adminApi.createUser(payload)
  await loadAll()
}

const updateUser = async (payload: Record<string, unknown>) => {
  const userId = Number(payload.id)
  await adminApi.updateUser(userId, payload)
  await loadAll()
}

const deleteUsers = async (ids: number[]) => {
  if (!ids.length) return
  if (!confirm(t('confirm.deleteUsers'))) return
  await adminApi.batchDeleteUsers(ids)
  await loadAll()
}

const batchChangeUsersRole = async (ids: number[], role: string) => {
  if (!ids.length) return
  await adminApi.batchChangeUserRole(ids, role)
  await loadAll()
}

const uploadMedia = async (file: File, folderId?: number | null) => {
  if (mediaUploading.value) return
  mediaUploading.value = true
  mediaToastStatus.value = ''
  mediaToastMessage.value = ''

  try {
    await adminApi.uploadMediaFile(file, folderId)
    mediaToastStatus.value = 'success'
    mediaToastMessage.value = t('toast.mediaUploaded')
    const mediaRes = await adminApi.getMedia(
      currentFolderId.value !== undefined
        ? { folderId: currentFolderId.value ?? undefined, unorganized: currentFolderId.value === null }
        : undefined,
    )
    media.value = mediaRes.data
  } catch (error) {
    mediaToastStatus.value = 'error'
    mediaToastMessage.value = error instanceof Error ? error.message : t('toast.mediaUploadFailed')
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
    mediaToastMessage.value = mediaIds.length > 1 ? t('toast.mediaDeletedCount', { n: mediaIds.length }) : t('toast.mediaDeleted')
    const mediaRes = await adminApi.getMedia(
      currentFolderId.value !== undefined
        ? { folderId: currentFolderId.value ?? undefined, unorganized: currentFolderId.value === null }
        : undefined,
    )
    media.value = mediaRes.data
  } catch (error) {
    mediaToastStatus.value = 'error'
    mediaToastMessage.value = error instanceof Error ? error.message : t('toast.mediaDeleteFailed')
  }
}

const selectMediaFolder = async (folderId: number | null | undefined) => {
  currentFolderId.value = folderId
  const opts =
    folderId === undefined
      ? undefined
      : folderId === null
        ? { unorganized: true }
        : { folderId }
  const mediaRes = await adminApi.getMedia(opts)
  media.value = mediaRes.data
}

const createMediaFolder = async (name: string, parentId: number | null) => {
  await adminApi.createFolder(name, parentId)
  const folderRes = await adminApi.getFolders()
  folders.value = folderRes.data
}

const renameMediaFolder = async (id: number, name: string) => {
  const target = (function findFolder(list: any[]): any {
    for (const f of list) {
      if (f.id === id) return f
      const found = findFolder(f.children || [])
      if (found) return found
    }
    return null
  })(folders.value)
  await adminApi.updateFolder(id, name, target?.parent_id ?? null, target?.sort_order ?? 0)
  const folderRes = await adminApi.getFolders()
  folders.value = folderRes.data
}

const deleteMediaFolder = async (id: number) => {
  await adminApi.deleteFolder(id)
  const [folderRes, mediaRes] = await Promise.all([
    adminApi.getFolders(),
    adminApi.getMedia(
      currentFolderId.value !== undefined
        ? { folderId: currentFolderId.value ?? undefined, unorganized: currentFolderId.value === null }
        : undefined,
    ),
  ])
  folders.value = folderRes.data
  media.value = mediaRes.data
}

const moveMedia = async (mediaIds: number[], targetFolderId: number | null) => {
  await adminApi.moveMediaFiles(mediaIds, targetFolderId)
  const mediaRes = await adminApi.getMedia(
    currentFolderId.value !== undefined
      ? { folderId: currentFolderId.value ?? undefined, unorganized: currentFolderId.value === null }
      : undefined,
  )
  media.value = mediaRes.data
}

const cropImageTo64 = async (file: File): Promise<File> => {
  const dataUrl = await new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result || ''))
    reader.onerror = () => reject(new Error(t('toast.readImageFailed')))
    reader.readAsDataURL(file)
  })

  const image = await new Promise<HTMLImageElement>((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = () => reject(new Error(t('toast.loadImageFailed')))
    img.src = dataUrl
  })

  const size = Math.min(image.width, image.height)
  const sx = Math.floor((image.width - size) / 2)
  const sy = Math.floor((image.height - size) / 2)

  const canvas = document.createElement('canvas')
  canvas.width = 64
  canvas.height = 64
  const ctx = canvas.getContext('2d')
  if (!ctx) throw new Error(t('toast.processImageFailed'))
  ctx.drawImage(image, sx, sy, size, size, 0, 0, 64, 64)

  const blob = await new Promise<Blob>((resolve, reject) => {
    canvas.toBlob((value) => {
      if (value) resolve(value)
      else reject(new Error(t('toast.exportImageFailed')))
    }, 'image/png')
  })

  return new File([blob], `${file.name.replace(/\.[^.]+$/, '')}-64x64.png`, { type: 'image/png' })
}

const handleSiteLogoSelect = async (file: File) => {
  const supported = ['image/png', 'image/jpeg', 'image/svg+xml']
  if (!supported.includes(file.type)) {
    logoUploadStatus.value = 'error'
    logoUploadMessage.value = t('toast.imageFormatError')
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
    logoUploadMessage.value = logoCropApplied.value ? t('toast.logoUploadCropped') : t('toast.logoUploaded')
  } catch (error) {
    logoUploadStatus.value = 'error'
    logoUploadMessage.value = error instanceof Error ? error.message : t('toast.logoUploadFailed')
  } finally {
    logoUploading.value = false
    setTimeout(() => {
      logoUploadMessage.value = ''
      logoUploadStatus.value = ''
    }, 2400)
  }
}

const showSiteToast = (message: string, status: 'success' | 'error') => {
  siteToastMessage.value = message
  siteToastStatus.value = status
  if (siteToastTimer !== null) {
    window.clearTimeout(siteToastTimer)
  }
  siteToastTimer = window.setTimeout(() => {
    siteToastMessage.value = ''
    siteToastStatus.value = ''
    siteToastTimer = null
  }, 3000)
}

const updateProfile = async (payload: { nickname: string; email: string; avatar: string | null; password: string | null }) => {
  try {
    const res = await adminApi.updateMe(payload)
    currentUser.value = res.data as AdminUser
    showSiteToast(t('toast.profileUpdated'), 'success')
  } catch (error) {
    showSiteToast(error instanceof Error ? error.message : t('toast.profileUpdateFailed'), 'error')
    throw error
  }
}

const saveSite = async () => {
  try {
    await adminApi.updateSiteSettings({
      site_title: siteTitle.value,
      site_logo: siteLogo.value || null,
      site_subtitle: siteSubtitle.value,
      icp_beian: icpBeian.value,
      police_beian: policeBeian.value,
      copyright_text: copyrightText.value,
      homepage_page_size: 10,
      comment_requires_review: true,
      homepage_bgm_url: homepageBgmUrl.value || null,
      homepage_hero_image: homepageHeroImage.value || null,
    })
    await loadAll()
    showSiteToast(t('toast.settingsSaved'), 'success')
  } catch (error) {
    showSiteToast(error instanceof Error ? error.message : t('toast.settingsSaveFailed'), 'error')
  }
}

const saveServerConfig = async () => {
  try {
    const res = await adminApi.updateServerConfig({
      secret_key: serverSecretKey.value,
      site_domain: serverDomain.value,
    })
    serverSecretKey.value = ''
    showSiteToast(res.data?.message || t('toast.serverConfigSaved'), 'success')
  } catch (error) {
    showSiteToast(error instanceof Error ? error.message : t('toast.serverConfigSaveFailed'), 'error')
  }
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

  if (!text) return t('toast.noSummary')
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
    if (message.includes('title') || message.includes('标题')) return t('toast.titleRequired')
    if (message.includes('content_markdown') || message.includes('正文')) return t('toast.contentRequired')
    if (message.includes('category_id') || message.includes('分类')) return t('toast.categoryRequired')
    return t('toast.contentIncomplete')
  }

  if (message.includes('401')) return t('toast.authExpired')
  if (message.includes('403')) return t('toast.noPermission')
  if (message.includes('500')) return t('toast.submitFailed')

  return message || t('toast.submitGenericFailed')
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

const resetArticleEditorState = () => {
  editingArticleId.value = null
  editingArticleTitle.value = ''
}

const fillArticleEditor = (article: any) => {
  title.value = String(article.title || '')
  coverUrl.value = String(article.cover_url || '')
  contentMarkdown.value = String(article.content_markdown || '')
  categoryId.value = Number(article.category_id || categories.value[0]?.id || 1)
  tagIdsText.value = Array.isArray(article.tags) ? article.tags.map((tag: any) => tag.name).join(', ') : ''
  action.value = normalizeArticleAction(article.status)
}

const editArticle = async (articleId: number) => {
  articleSubmitting.value = true
  articleSubmitError.value = ''
  try {
    const res = await adminApi.getArticle(articleId)
    const article = res.data
    if (!article || !article.id) throw new Error(t('toast.getArticleFailed'))
    editingArticleId.value = articleId
    editingArticleTitle.value = String(article.title || '')
    fillArticleEditor(article)
    currentView.value = 'articles'
    articleSubView.value = 'edit'
    pushViewUrl('articles', 'edit')
    await nextTick()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (error) {
    articleSubmitError.value = error instanceof Error ? error.message : t('toast.getArticleFailed')
    currentView.value = 'articles'
    articleSubView.value = 'manage'
    editingArticleId.value = null
    editingArticleTitle.value = ''
    pushViewUrl('articles', 'manage')
  } finally {
    articleSubmitting.value = false
  }
}

const createArticle = async () => {
  if (articleSubmitting.value) return
  articleSubmitting.value = true
  articleSubmitError.value = ''
  const finalAction = editingArticleId.value !== null
    ? (action.value === 'publish' ? 'publish' : action.value === 'submit' ? 'submit' : 'draft')
    : (isAdmin.value ? (action.value === 'publish' ? 'publish' : 'draft') : (action.value === 'submit' ? 'submit' : 'draft'))

  try {
    const trimmedTitle = title.value.trim()
    const trimmedContent = contentMarkdown.value.trim()
    if (!trimmedTitle) {
      showArticleSubmitError(t('toast.titleRequired'), 'title')
      return
    }
    if (!trimmedContent) {
      showArticleSubmitError(t('toast.contentRequired'), 'content')
      return
    }

    const autoSummary = extractSummary(contentMarkdown.value, 120)
    const resolvedTagIds = await resolveTagIdsByNames(tagIdsText.value)

    const payload = {
      title: trimmedTitle,
      summary: autoSummary || t('toast.noSummary'),
      content_markdown: contentMarkdown.value,
      cover_url: coverUrl.value || null,
      category_id: categoryId.value,
      tag_ids: resolvedTagIds,
      action: finalAction,
    }

    if (editingArticleId.value !== null) {
      await adminApi.updateArticle(editingArticleId.value, payload)
    } else {
      await adminApi.createArticle(payload)
    }
    title.value = ''
    coverUrl.value = ''
    contentMarkdown.value = ''
    tagIdsText.value = ''
    resetArticleEditorState()
    clearArticleDraft()
    if (articleSubmitErrorTimer !== null) {
      window.clearTimeout(articleSubmitErrorTimer)
      articleSubmitErrorTimer = null
    }
    articleSubmitError.value = ''
    articleSubmitFocusField.value = null
    currentView.value = 'articles'
    articleSubView.value = 'manage'
    pushViewUrl('articles', 'manage')
    await nextTick()
    await loadAll()
  } catch (error) {
    showArticleSubmitError(getArticleCreateErrorMessage(error), getArticleCreateFocusField(error))
  } finally {
    articleSubmitting.value = false
  }
}

onMounted(async () => {
  const storedSidebarState = localStorage.getItem('md-admin-sidebar-collapsed')
  isSidebarCollapsed.value = storedSidebarState === '1'
  await loadAll()
  action.value = isAdmin.value ? 'publish' : 'submit'

  const { view, sub } = pathToView(route.path)
  currentView.value = view
  if (view === 'articles') {
    articleSubView.value = sub
  }

  document.addEventListener('keydown', handleGlobalKeyDown)

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
  document.removeEventListener('keydown', handleGlobalKeyDown)
  if (articleDraftSaveTimer !== null) {
    window.clearTimeout(articleDraftSaveTimer)
    articleDraftSaveTimer = null
  }
  if (articleSubmitErrorTimer !== null) {
    window.clearTimeout(articleSubmitErrorTimer)
    articleSubmitErrorTimer = null
  }
  if (siteToastTimer !== null) {
    window.clearTimeout(siteToastTimer)
    siteToastTimer = null
  }
})
</script>
