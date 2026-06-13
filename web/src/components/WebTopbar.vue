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
      :aria-label="mobileMenuOpen ? '关闭导航菜单' : '打开导航菜单'"
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
        {{ item.title }}
      </RouterLink>
      <RouterLink to="/categories" :class="{ active: isActive('/categories') }">分类</RouterLink>
      <RouterLink to="/archive" :class="{ active: isActive('/archive') }">归档</RouterLink>
      <RouterLink to="/about" :class="{ active: isActive('/about') }">关于</RouterLink>
    </nav>

    <div class="topbar-right">
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
            <RouterLink v-if="!isLoggedIn" to="/login" class="dropdown-item" @click="accountMenuOpen = false">登录</RouterLink>
            <RouterLink v-if="!isLoggedIn" to="/register" class="dropdown-item" @click="accountMenuOpen = false">注册</RouterLink>
            <template v-else>
              <RouterLink to="/profile" class="dropdown-item" @click="accountMenuOpen = false">个人中心</RouterLink>
              <button type="button" class="dropdown-item danger" @click="logout">退出登录</button>
            </template>
          </div>
        </transition>
      </div>

      <button v-if="!isMobile && collapsibleSearch" type="button" class="search-launch-btn" aria-label="打开搜索" title="搜索" @click="openSearchPanel">
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
          <p class="drawer-subtitle">快速导航</p>
        </div>
        <button type="button" class="drawer-close" @click="mobileMenuOpen = false">✕</button>
      </div>
      <nav class="drawer-nav">
        <RouterLink v-for="item in navItems" :key="item.id" :to="item.path" :class="{ active: isActive(item.path) }" @click="mobileMenuOpen = false">
          {{ item.title }}
        </RouterLink>
        <RouterLink to="/categories" :class="{ active: isActive('/categories') }" @click="mobileMenuOpen = false">分类</RouterLink>
        <RouterLink to="/archive" :class="{ active: isActive('/archive') }" @click="mobileMenuOpen = false">归档</RouterLink>
        <button v-if="collapsibleSearch" type="button" class="drawer-search-entry" @click="openSearchPanel">搜索</button>
        <RouterLink to="/about" :class="{ active: isActive('/about') }" @click="mobileMenuOpen = false">关于</RouterLink>
      </nav>
    </aside>
  </transition>

  <transition name="search-overlay-fade">
    <div v-if="searchPanelOpen" class="search-overlay-mask" @click="closeSearchPanel"></div>
  </transition>

  <transition name="search-overlay-slide">
    <section v-if="searchPanelOpen" class="search-overlay-panel" role="dialog" aria-modal="true" aria-label="搜索">
      <div class="search-overlay-shell">
        <div class="search-overlay-header">
          <div class="search-overlay-title-wrap">
            <span class="brand-mark search-overlay-mark">⌕</span>
            <div>
              <p class="drawer-title">搜索站点内容</p>
              <p class="drawer-subtitle">输入关键词后下方即时显示结果</p>
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
            placeholder="请输入文章、分类或标签关键词"
          />
        </form>

        <div class="search-overlay-result" ref="searchPanelResultRef">
          <p class="search-overlay-hint">{{ searchPanelHint }}</p>
          <p v-if="searchPanelLoading" class="search-overlay-empty">正在搜索...</p>
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
              <em>{{ item.category?.name || '未分类' }} · {{ item.author?.nickname || 'admin' }}</em>
            </RouterLink>
            <div ref="searchPanelLoadMoreSentinel" class="search-overlay-load-more-sentinel" aria-hidden="true"></div>
          </div>
          <p v-else class="search-overlay-empty">未找到匹配结果，请尝试其他关键词。</p>
          <p v-if="searchPanelLoadingMore" class="search-overlay-empty">加载更多中...</p>
          <p v-else-if="searchPanelResults.length && !searchPanelCanLoadMore" class="search-overlay-empty">没有更多结果了。</p>
        </div>
      </div>
    </section>
  </transition>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { webApi } from '../api'
import type { NavItem, Article } from '../types'

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
  return document.cookie.split('; ').some(c => c.startsWith('logged_in='))
})
const accountName = computed(() => localStorage.getItem('md-reader-nickname') || '已登录用户')
const accountEntryLabel = computed(() => (isLoggedIn.value ? `账户：${accountName.value}` : '登录 / 注册'))
const accountEntryTitle = computed(() => (isLoggedIn.value ? accountName.value : '登录 / 注册'))

const searchPanelResults = computed(() => searchPanelArticles.value)
const searchPanelCanLoadMore = computed(() => searchPanelPage.value < searchPanelTotalPages.value)

const searchPanelHint = computed(() =>
  searchPanelKeyword.value.trim() ? '下方显示当前关键词匹配的结果。' : '可输入文章、分类或标签关键词进行搜索。',
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
