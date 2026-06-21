<template>
  <aside class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
    <div class="sidebar-head">
      <button type="button" class="sidebar-toggle" :aria-label="sidebarToggleLabel" @click="$emit('toggleSidebar')">
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
            href="#"
            :class="{ active: currentView === item.key }"
            @click.prevent="$emit('setView', item.key)"
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
                <strong class="sidebar-flyout-title">{{ articleFlyoutTitle }}</strong>
              </div>
              <button
                v-for="sub in articleSubMenus"
                :key="sub.key"
                type="button"
                class="sidebar-flyout-item"
                :class="{ active: articleSubView === sub.key, disabled: sub.key === 'edit' && !editingArticleId }"
                :disabled="sub.key === 'edit' && !editingArticleId"
                @click="handleSubViewClick(sub.key)"
              >
                {{ sub.label }}
              </button>
            </div>
          </transition>

          <div v-if="!isSidebarCollapsed && currentView === 'articles'" class="sidebar-subnav">
            <a
              v-for="sub in articleSubMenus"
              :key="sub.key"
              href="#"
              :class="{ active: articleSubView === sub.key, disabled: sub.key === 'edit' && !editingArticleId }"
              @click.prevent="handleSubViewClick(sub.key)"
            >
              <span class="sidebar-text">{{ sub.label }}</span>
            </a>
          </div>
        </div>

        <a
          v-else
          href="#"
          :class="{ active: currentView === item.key }"
          :data-label="item.label"
          @click.prevent="$emit('setView', item.key)"
        >
          <span class="sidebar-icon">{{ menuIconMap[item.key] }}</span>
          <span class="sidebar-text">{{ item.label }}</span>
        </a>
      </template>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

type ViewType = 'overview' | 'articles' | 'media' | 'comments' | 'friend-links' | 'users' | 'profile' | 'site'
type ArticleSubView = 'manage' | 'trash' | 'create' | 'edit' | 'category'

type MainMenuItem = {
  key: ViewType
  label: string
  adminOnly?: boolean
}

type ArticleSubMenuItem = {
  key: ArticleSubView
  label: string
}

const props = defineProps<{
  currentView: ViewType
  articleSubView: ArticleSubView
  editingArticleId: number | null
  isSidebarCollapsed: boolean
  isAdmin: boolean
}>()

const emit = defineEmits<{
  toggleSidebar: []
  setView: [view: ViewType]
  setArticleSubView: [subView: ArticleSubView]
}>()

const mainMenus = computed<MainMenuItem[]>(() => [
  { key: 'overview', label: t('menu.overview') },
  { key: 'articles', label: t('menu.articles') },
  { key: 'media', label: t('menu.media'), adminOnly: true },
  { key: 'comments', label: t('menu.comments') },
  { key: 'friend-links', label: t('menu.friendLinks') },
  { key: 'users', label: t('menu.users'), adminOnly: true },
  { key: 'profile', label: t('menu.profile') },
  { key: 'site', label: t('menu.site'), adminOnly: true },
])

const articleSubMenus = computed<ArticleSubMenuItem[]>(() => [
  { key: 'manage', label: t('articleSub.manage') },
  { key: 'create', label: t('articleSub.create') },
  { key: 'edit', label: t('articleSub.edit') },
  { key: 'category', label: t('articleSub.category') },
  { key: 'trash', label: t('articleSub.trash') },
])

const menuIconMap: Record<ViewType, string> = {
  overview: '⌂',
  articles: '✎',
  media: '◫',
  comments: '☍',
  'friend-links': '🔗',
  users: '⚑',
  site: '⚙',
  profile: '◉',
}

const sidebarToggleLabel = computed(() => (props.isSidebarCollapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar')))

const visibleMainMenus = computed(() =>
  mainMenus.value.filter((item) => !item.adminOnly || props.isAdmin),
)

const articleFlyoutOpen = ref(false)
const articleFlyoutCloseTimer = ref<number | null>(null)
const articleMenuGroupRef = ref<HTMLElement | null>(null)
const articleMenuGroupEl = ref<HTMLElement | null>(null)
const sidebarFlyoutSide = ref<'right' | 'left'>('right')

const articleFlyoutTitle = computed(() => {
  if (props.currentView !== 'articles') return t('menu.articles')
  if (props.articleSubView === 'edit' && !props.editingArticleId) return t('menu.articles')
  const currentSub = articleSubMenus.value.find((item) => item.key === props.articleSubView)
  return currentSub ? `${t('menu.articles')} / ${currentSub.label}` : t('menu.articles')
})

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

const handleSubViewClick = (key: ArticleSubView) => {
  if (key === 'edit' && !props.editingArticleId) return
  emit('setArticleSubView', key)
}

onMounted(() => {
  window.addEventListener('resize', updateFlyoutSide)
  updateFlyoutSide()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateFlyoutSide)
  clearArticleFlyoutTimer()
})
</script>
