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
    </nav>

    <div class="topbar-right">
      <div class="account-menu" ref="accountMenuRef">
        <button type="button" class="auth-entry" @click="toggleAccountMenu">
          {{ accountLabel }}
        </button>
        <transition name="menu-pop">
          <div v-if="accountMenuOpen" class="account-dropdown">
            <p v-if="isLoggedIn" class="account-name">{{ accountName }}</p>
            <button v-if="isLoggedIn && isOnArticlePage" type="button" class="dropdown-item" @click="goToCommentSection">去评论</button>
            <RouterLink v-if="!isLoggedIn" to="/login" class="dropdown-item" @click="accountMenuOpen = false">登录</RouterLink>
            <RouterLink v-if="!isLoggedIn" to="/register" class="dropdown-item" @click="accountMenuOpen = false">注册</RouterLink>
            <button v-else type="button" class="dropdown-item danger" @click="logout">退出登录</button>
          </div>
        </transition>
      </div>

      <form class="search-box" :class="{ compact: collapsibleSearch, closed: collapsibleSearch && !searchOpen }" @submit.prevent="onSubmit">
        <button
          v-if="collapsibleSearch && !searchOpen"
          type="button"
          class="search-trigger"
          aria-label="展开搜索"
          :aria-expanded="searchOpen"
          @click="toggleSearch"
        >
          <span aria-hidden="true">⌕</span>
        </button>

        <transition name="search-fade-slide">
          <div v-if="!collapsibleSearch || searchOpen" class="search-input-wrap">
            <input
              :value="searchKeyword"
              placeholder="输入关键词回车搜索"
              @input="onKeywordInput"
            />
            <button type="submit" aria-label="搜索" class="search-submit-inside">
              <span aria-hidden="true">⌕</span>
            </button>
          </div>
        </transition>

        <button type="button" class="theme-toggle" :aria-label="themeToggleLabel" @click="$emit('toggle-theme')">
          <span aria-hidden="true">{{ theme === 'light' ? '◐' : '☼' }}</span>
        </button>
      </form>
    </div>
  </header>

  <transition name="drawer-fade">
    <div v-if="mobileMenuOpen" class="drawer-mask" @click="mobileMenuOpen = false"></div>
  </transition>

  <transition name="drawer-slide">
    <aside v-if="mobileMenuOpen" class="drawer-panel">
      <div class="drawer-header">
        <span class="brand-mark">MD</span>
        <div>
          <p class="drawer-title">{{ title }}</p>
          <p class="drawer-subtitle">快速导航</p>
        </div>
        <button type="button" class="drawer-close" @click="mobileMenuOpen = false">✕</button>
      </div>
      <nav class="drawer-nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.id"
          :to="item.path"
          :class="{ active: isActive(item.path) }"
          @click="mobileMenuOpen = false"
        >
          {{ item.title }}
        </RouterLink>
      </nav>
    </aside>
  </transition>
</template>

<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'

import type { NavItem } from '../types'

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
  {
    subtitle: '',
    logoUrl: '',
    searchKeyword: '',
    currentPath: '/',
    currentFullPath: '/',
    collapsibleSearch: false,
  },
)

const emit = defineEmits<{
  'toggle-theme': []
  search: []
  'update:searchKeyword': [value: string]
}>()

const searchOpen = ref(!props.collapsibleSearch || !!props.searchKeyword)
const mobileMenuOpen = ref(false)
const accountMenuOpen = ref(false)
const accountMenuRef = ref<HTMLElement | null>(null)

const isLoggedIn = computed(() => !!localStorage.getItem('md_web_token'))
const accountName = computed(() => localStorage.getItem('md-reader-nickname') || '已登录用户')
const accountLabel = computed(() => (isLoggedIn.value ? '账号' : '登录 / 注册'))
const isOnArticlePage = computed(() => (props.currentPath || '').startsWith('/article/'))

watch(
  () => props.searchKeyword,
  (value) => {
    if (value && props.collapsibleSearch) {
      searchOpen.value = true
    }
  },
)

watch(
  () => props.currentFullPath,
  () => {
    mobileMenuOpen.value = false
  },
)

const themeToggleLabel = computed(() =>
  props.theme === 'light' ? '切换为暗色主题' : '切换为白天主题',
)

const splitPathAndQuery = (value: string) => {
  const [pathPart = '/', queryPart = ''] = value.split('?')
  const normalizedPath = pathPart.replace(/\/$/, '') || '/'
  const normalizedQuery = queryPart.trim()
  return { path: normalizedPath, query: normalizedQuery }
}

const isActive = (navTarget: string) => {
  const current = splitPathAndQuery(props.currentFullPath || props.currentPath)
  const target = splitPathAndQuery(navTarget)

  if (target.query) {
    return current.path === target.path && current.query === target.query
  }

  if (target.path === '/') return current.path === '/'
  return current.path === target.path || current.path.startsWith(`${target.path}/`)
}

const onKeywordInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:searchKeyword', target.value)
}

const toggleSearch = () => {
  searchOpen.value = !searchOpen.value
}

const toggleAccountMenu = () => {
  accountMenuOpen.value = !accountMenuOpen.value
}

const goToCommentSection = () => {
  accountMenuOpen.value = false
  const el = document.querySelector('#comment-section')
  if (el instanceof HTMLElement) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    el.classList.add('section-highlight')
    window.setTimeout(() => el.classList.remove('section-highlight'), 1800)
  }
}

const logout = () => {
  localStorage.removeItem('md_web_token')
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

const onSubmit = () => {
  if (props.collapsibleSearch && !searchOpen.value) {
    searchOpen.value = true
    return
  }
  emit('search')
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>
