<template>
  <header class="topbar">
    <div class="brand-block">
      <span class="brand-mark">MD</span>
      <h1>{{ title }}</h1>
    </div>

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
        aria-label="展开搜索"
        @click="toggleSearch"
      >
        <span aria-hidden="true">⌕</span>
      </button>

      <input
        v-show="!collapsibleSearch || searchOpen"
        :value="searchKeyword"
        placeholder="搜索文章、摘要与内容"
        @input="onKeywordInput"
      />

      <button v-show="!collapsibleSearch || searchOpen" type="submit" aria-label="搜索">
        <span aria-hidden="true">⌕</span>
      </button>

      <button type="button" class="theme-toggle" :aria-label="themeToggleLabel" @click="$emit('toggle-theme')">
        <span aria-hidden="true">{{ theme === 'light' ? '◐' : '☼' }}</span>
      </button>
    </form>
  </header>
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
    collapsibleSearch?: boolean
  }>(),
  {
    searchKeyword: '',
    currentPath: '/',
    collapsibleSearch: false,
  },
)

const emit = defineEmits<{
  'toggle-theme': []
  search: []
  'update:searchKeyword': [value: string]
}>()

const searchOpen = ref(!props.collapsibleSearch || !!props.searchKeyword)

watch(
  () => props.searchKeyword,
  (value) => {
    if (value && props.collapsibleSearch) {
      searchOpen.value = true
    }
  },
)

const themeToggleLabel = computed(() =>
  props.theme === 'light' ? '切换为暗色主题' : '切换为白天主题',
)

const normalizePath = (path: string) => path.replace(/\/$/, '') || '/'

const isActive = (path: string) => {
  const current = normalizePath(props.currentPath)
  const target = normalizePath(path)

  if (target === '/') return current === '/'
  return current === target || current.startsWith(`${target}/`)
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
