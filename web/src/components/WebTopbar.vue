<template>
  <header class="topbar">
    <div class="brand-block">
      <img v-if="logoUrl" :src="logoUrl" class="brand-logo" alt="site logo" />
      <span v-else class="brand-mark">MD</span>
      <div>
        <h1>{{ title }}</h1>
        <p v-if="subtitle" class="brand-subtitle">{{ subtitle }}</p>
      </div>
    </div>

    <button
      type="button"
      class="hamburger-btn"
      :aria-label="mobileMenuOpen ? t('topbar.closeMenu') : t('topbar.openMenu')"
      :aria-expanded="mobileMenuOpen"
      @click="mobileMenuOpen = !mobileMenuOpen"
    >
      <span aria-hidden="true">☰</span>
    </button>

    <nav class="nav">
      <RouterLink
        v-for="item in navItems"
        :key="item.id"
        :to="item.path"
        :class="{ active: isActive(item.path) }"
      >
        {{ navTitleMap[item.path] || item.title }}
      </RouterLink>
      <RouterLink to="/categories" :class="{ active: isActive('/categories') }">{{ t('common.categories') }}</RouterLink>
      <RouterLink to="/archive" :class="{ active: isActive('/archive') }">{{ t('common.archive') }}</RouterLink>
      <RouterLink to="/about" :class="{ active: isActive('/about') }">{{ t('common.about') }}</RouterLink>
    </nav>

    <div class="topbar-right">
      <select class="lang-select" :value="locale" @change="onLocaleChange">
        <option value="zh-CN">中文</option>
        <option value="en">EN</option>
        <option value="ja">日本語</option>
      </select>
      <div class="account-menu" ref="accountMenuRef">
        <button
          type="button"
          class="auth-entry icon-entry"
          :aria-label="accountEntryLabel"
          :title="accountEntryTitle"
          @click="toggleAccountMenu"
        >
          <svg class="auth-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 2a5 5 0 1 0 0 10 5 5 0 0 0 0-10Zm0 12c-4.418 0-8 2.91-8 6.5A1.5 1.5 0 0 0 5.5 22h13a1.5 1.5 0 0 0 1.5-1.5C20 16.91 16.418 14 12 14Z" fill="currentColor" />
          </svg>
        </button>
        <transition name="menu-pop">
          <div v-if="accountMenuOpen" class="account-dropdown">
            <RouterLink v-if="!isLoggedIn" to="/login" class="dropdown-item" @click="accountMenuOpen = false">{{ t('common.login') }}</RouterLink>
            <RouterLink v-if="!isLoggedIn" to="/register" class="dropdown-item" @click="accountMenuOpen = false">{{ t('common.register') }}</RouterLink>
            <template v-else>
              <RouterLink to="/profile" class="dropdown-item" @click="accountMenuOpen = false">{{ t('common.profile') }}</RouterLink>
              <button type="button" class="dropdown-item danger" @click="logout">{{ t('common.logout') }}</button>
            </template>
          </div>
        </transition>
      </div>

      <button v-if="!isMobile && collapsibleSearch" type="button" class="search-launch-btn" :aria-label="t('common.search')" :title="t('common.search')" @click="openSearchPanel">
        <span aria-hidden="true">⌕</span>
      </button>
    </div>
  </header>

  <transition name="drawer-fade">
    <div v-if="mobileMenuOpen" class="drawer-mask" @click="mobileMenuOpen = false"></div>
  </transition>

  <transition name="drawer-slide">
    <aside v-if="mobileMenuOpen" class="drawer-panel">
      <div class="drawer-header">
        <img v-if="logoUrl" :src="logoUrl" class="brand-logo drawer-brand-logo" alt="site logo" />
        <span v-else class="brand-mark">MD</span>
        <div>
          <p class="drawer-title">{{ title }}</p>
          <p class="drawer-subtitle">{{ t('topbar.quickNav') }}</p>
        </div>
        <button type="button" class="drawer-close" @click="mobileMenuOpen = false">✕</button>
      </div>
      <nav class="drawer-nav">
        <RouterLink v-for="item in navItems" :key="item.id" :to="item.path" :class="{ active: isActive(item.path) }" @click="mobileMenuOpen = false">
          {{ navTitleMap[item.path] || item.title }}
        </RouterLink>
        <RouterLink to="/categories" :class="{ active: isActive('/categories') }" @click="mobileMenuOpen = false">{{ t('common.categories') }}</RouterLink>
        <RouterLink to="/archive" :class="{ active: isActive('/archive') }" @click="mobileMenuOpen = false">{{ t('common.archive') }}</RouterLink>
        <button v-if="collapsibleSearch" type="button" class="drawer-search-entry" @click="openSearchPanel">{{ t('common.search') }}</button>
        <RouterLink to="/about" :class="{ active: isActive('/about') }" @click="mobileMenuOpen = false">{{ t('common.about') }}</RouterLink>
      </nav>
    </aside>
  </transition>

  <transition name="search-overlay-fade">
    <div v-if="searchPanelOpen" class="search-overlay-mask" @click="closeSearchPanel"></div>
  </transition>

  <transition name="search-overlay-slide">
    <section v-if="searchPanelOpen" class="search-overlay-panel" role="dialog" aria-modal="true" :aria-label="t('common.search')">
      <div class="search-overlay-shell">
        <div class="search-overlay-header">
          <div class="search-overlay-title-wrap">
            <span class="brand-mark search-overlay-mark">⌕</span>
            <div>
              <p class="drawer-title">{{ t('topbar.searchTitle') }}</p>
              <p class="drawer-subtitle">{{ t('topbar.searchSubtitle') }}</p>
            </div>
          </div>
          <button type="button" class="drawer-close" @click="closeSearchPanel">✕</button>
        </div>

        <form class="search-overlay-form" @submit.prevent>
          <input
            ref="searchPanelInputRef"
            v-model="searchPanelKeyword"
            class="search-overlay-input"
            type="search"
            :placeholder="t('topbar.searchPlaceholder')"
          />
        </form>

        <div class="search-overlay-result" ref="searchPanelResultRef">
          <p class="search-overlay-hint">{{ searchPanelHint }}</p>
          <p v-if="searchPanelLoading" class="search-overlay-empty">{{ t('topbar.searching') }}</p>
          <div v-else-if="searchPanelResults.length" class="search-overlay-result-list">
            <RouterLink
              v-for="(item, index) in searchPanelResults"
              :key="item.id"
              :to="`/article/${item.id}`"
              class="search-overlay-result-item"
              :class="{ active: index === searchPanelActiveIndex }"
              @mouseenter="searchPanelActiveIndex = index"
              @click="closeSearchPanel"
            >
              <strong>{{ item.title }}</strong>
              <span>{{ item.summary }}</span>
              <em>{{ item.category?.name || t('common.untitled') }} · {{ item.author?.nickname || 'admin' }}</em>
            </RouterLink>
            <div ref="searchPanelLoadMoreSentinel" class="search-overlay-load-more-sentinel" aria-hidden="true"></div>
          </div>
          <p v-else class="search-overlay-empty">{{ t('topbar.noResults') }}</p>
          <p v-if="searchPanelLoadingMore" class="search-overlay-empty">{{ t('topbar.loadMore') }}</p>
          <p v-else-if="searchPanelResults.length && !searchPanelCanLoadMore" class="search-overlay-empty">{{ t('topbar.noMoreResults') }}</p>
        </div>
      </div>
    </section>
  </transition>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { webApi } from '../api'
import type { NavItem, Article } from '../types'

const { t, locale } = useI18n()

const onLocaleChange = (e: Event) => {
  const val = (e.target as HTMLSelectElement).value
  locale.value = val
  localStorage.setItem('md-locale', val)
}

const navTitleMap = computed<Record<string, string>>(() => ({
  '/': t('common.home'),
  '/search': t('common.search'),
  '/categories': t('common.categories'),
  '/archive': t('common.archive'),
  '/about': t('common.about'),
  '/friend-links': t('common.login'),
  '/register': t('common.register'),
  '/login': t('common.login'),
  '/profile': t('common.profile'),
}))

type ThemeMode = 'light' | 'dark'

const props = withDefaults(
  defineProps<{
    title: string
    navItems: NavItem[]
    theme: ThemeMode
    subtitle?: string
    logoUrl?: string
    searchKeyword?: string
    currentPath?: string
    currentFullPath?: string
    collapsibleSearch?: boolean
  }>(),
  { subtitle: '', logoUrl: '', searchKeyword: '', currentPath: '/', currentFullPath: '/', collapsibleSearch: false },
)

const emit = defineEmits<{ 'toggle-theme': []; search: [] }>()
const mobileMenuOpen = ref(false)
const searchPanelOpen = ref(false)
const searchPanelKeyword = ref('')
const searchPanelInputRef = ref<HTMLInputElement | null>(null)
const searchPanelLoading = ref(false)
const searchPanelLoadingMore = ref(false)
const searchPanelArticles = ref<Article[]>([])
const searchPanelActiveIndex = ref(0)
const searchPanelPage = ref(1)
const searchPanelTotalPages = ref(1)
const searchPanelResultRef = ref<HTMLElement | null>(null)
const searchPanelLoadMoreSentinel = ref<HTMLElement | null>(null)
let searchDebounceTimer: number | null = null
let searchRequestSeq = 0
let searchPanelObserver: IntersectionObserver | null = null
const accountMenuOpen = ref(false)
const accountMenuRef = ref<HTMLElement | null>(null)
const isMobile = ref(false)

const isLoggedIn = computed(() => {
  return document.cookie.split('; ').some(c => c.startsWith('web_logged_in='))
})
const accountName = computed(() => localStorage.getItem('md-reader-nickname') || t('topbar.loggedInUser'))
const accountEntryLabel = computed(() => (isLoggedIn.value ? t('topbar.accountLabel', { name: accountName.value }) : t('topbar.loginRegister')))
const accountEntryTitle = computed(() => (isLoggedIn.value ? accountName.value : t('topbar.loginRegister')))

const searchPanelResults = computed(() => searchPanelArticles.value)
const searchPanelCanLoadMore = computed(() => searchPanelPage.value < searchPanelTotalPages.value)

const searchPanelHint = computed(() =>
  searchPanelKeyword.value.trim() ? t('topbar.searchHint') : t('topbar.searchHintEmpty'),
)

watch(() => props.currentFullPath, () => {
  mobileMenuOpen.value = false
  accountMenuOpen.value = false
})

watch(searchPanelOpen, (opened) => {
  document.documentElement.style.overflow = opened ? 'hidden' : ''
  if (opened) {
    window.setTimeout(() => setupSearchObserver(), 0)
  } else {
    if (searchPanelObserver) {
      searchPanelObserver.disconnect()
      searchPanelObserver = null
    }
    if (searchDebounceTimer) {
      window.clearTimeout(searchDebounceTimer)
      searchDebounceTimer = null
    }
  }
})

watch(searchPanelKeyword, async (value) => {
  if (searchDebounceTimer) {
    window.clearTimeout(searchDebounceTimer)
  }

  const keyword = value.trim()
  if (!keyword) {
    searchPanelLoading.value = false
    searchPanelLoadingMore.value = false
    searchPanelArticles.value = []
    searchPanelPage.value = 1
    searchPanelTotalPages.value = 1
    return
  }

  searchPanelLoading.value = true
  searchPanelLoadingMore.value = false
  searchPanelPage.value = 1
  const requestId = ++searchRequestSeq

  searchDebounceTimer = window.setTimeout(async () => {
    try {
      const res = await webApi.search(keyword, 1, 20)
      if (requestId !== searchRequestSeq) return
      searchPanelArticles.value = res.articles.items
      searchPanelPage.value = res.articles.page
      searchPanelTotalPages.value = res.articles.total_pages
    } catch {
      if (requestId !== searchRequestSeq) return
      searchPanelArticles.value = []
      searchPanelPage.value = 1
      searchPanelTotalPages.value = 1
    } finally {
      if (requestId === searchRequestSeq) {
        searchPanelLoading.value = false
      }
    }
    searchDebounceTimer = null
  }, 180)
})

const splitPathAndQuery = (value: string) => {
  const [pathPart = '/', queryPart = ''] = value.split('?')
  return { path: pathPart.replace(/\/$/, '') || '/', query: queryPart.trim() }
}

const isActive = (navTarget: string) => {
  const current = splitPathAndQuery(props.currentFullPath || props.currentPath)
  const target = splitPathAndQuery(navTarget)
  if (target.query) return current.path === target.path && current.query === target.query
  if (target.path === '/') return current.path === '/'
  return current.path === target.path || current.path.startsWith(`${target.path}/`)
}

const handleResize = () => {
  isMobile.value = window.innerWidth <= 960
}

const openSearchPanel = () => {
  mobileMenuOpen.value = false
  accountMenuOpen.value = false
  searchPanelOpen.value = true
  searchPanelKeyword.value = ''
  searchPanelArticles.value = []
  searchPanelActiveIndex.value = 0
  searchPanelPage.value = 1
  searchPanelTotalPages.value = 1
  window.setTimeout(() => {
    searchPanelInputRef.value?.focus()
    setupSearchObserver()
  }, 50)
}

const closeSearchPanel = () => {
  searchPanelOpen.value = false
}



const handleSearchResultScroll = async () => {
  const el = searchPanelResultRef.value
  if (!el || searchPanelLoading.value || searchPanelLoadingMore.value || !searchPanelCanLoadMore.value) return
  const nearBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 120
  if (!nearBottom) return

  const keyword = searchPanelKeyword.value.trim()
  if (!keyword) return

  searchPanelLoadingMore.value = true
  const requestId = ++searchRequestSeq
  const nextPage = searchPanelPage.value + 1

  try {
    const res = await webApi.search(keyword, nextPage, 20)
    if (requestId !== searchRequestSeq) return
    searchPanelArticles.value = [...searchPanelArticles.value, ...res.articles.items]
    searchPanelPage.value = res.articles.page
    searchPanelTotalPages.value = res.articles.total_pages
  } catch {
    // keep existing results
  } finally {
    if (requestId === searchRequestSeq) {
      searchPanelLoadingMore.value = false
    }
  }
}

const setupSearchObserver = () => {
  if (searchPanelObserver) {
    searchPanelObserver.disconnect()
    searchPanelObserver = null
  }

  if (!searchPanelResultRef.value || !searchPanelLoadMoreSentinel.value) return

  searchPanelObserver = new IntersectionObserver(
    (entries) => {
      const entry = entries[0]
      if (!entry?.isIntersecting) return
      void handleSearchResultScroll()
    },
    {
      root: searchPanelResultRef.value,
      rootMargin: '120px 0px 120px 0px',
      threshold: 0.01,
    },
  )

  searchPanelObserver.observe(searchPanelLoadMoreSentinel.value)
}

const toggleAccountMenu = () => {
  accountMenuOpen.value = !accountMenuOpen.value
}

const logout = async () => {
  try {
    await webApi.logoutReader()
  } catch {
    // ignore errors
  }
  document.cookie = 'web_logged_in=; path=/; max-age=0'
  document.cookie = 'web_access_token=; path=/; max-age=0'
  document.cookie = 'web_refresh_token=; path=/; max-age=0'
  localStorage.removeItem('md-reader-nickname')
  localStorage.removeItem('md-reader-email')
  accountMenuOpen.value = false
  window.location.reload()
}

const handleDocumentClick = (event: MouseEvent) => {
  const target = event.target as Node | null
  if (accountMenuRef.value && target && !accountMenuRef.value.contains(target)) {
    accountMenuOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  handleResize()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
  window.removeEventListener('resize', handleResize)
})
</script>
