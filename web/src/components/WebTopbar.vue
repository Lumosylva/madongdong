<template>
  <header class="topbar">
    <div class="brand-block">
      <span class="brand-mark">MD</span>
      <h1>{{ title }}</h1>
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

    <form class="search-box" :class="{ compact: collapsibleSearch, closed: collapsibleSearch && !searchOpen }" @submit.prevent="onSubmit">
      <button
        v-if="collapsibleSearch"
        type="button"
        class="search-trigger"
        :aria-label="searchOpen ? '收起搜索' : '展开搜索'"
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
import { computed, ref, watch } from 'vue'

import type { NavItem } from '../types'

type ThemeMode = 'light' | 'dark'

const props = withDefaults(
  defineProps<{
    title: string
    navItems: NavItem[]
    theme: ThemeMode
    searchKeyword?: string
    currentPath?: string
    currentFullPath?: string
    collapsibleSearch?: boolean
  }>(),
  {
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

const onSubmit = () => {
  if (props.collapsibleSearch && !searchOpen.value) {
    searchOpen.value = true
    return
  }
  emit('search')
}
</script>
