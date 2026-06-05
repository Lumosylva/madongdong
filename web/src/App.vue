<template>
  <router-view />
  <FloatingTools :theme="theme" @toggle-theme="toggleTheme" />
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import FloatingTools from './components/FloatingTools.vue'

type ThemeMode = 'light' | 'dark'

const theme = ref<ThemeMode>('light')

const applyTheme = (value: ThemeMode) => {
  theme.value = value
  document.documentElement.dataset.theme = value
  localStorage.setItem('md-theme', value)
}

const toggleTheme = () => {
  applyTheme(theme.value === 'light' ? 'dark' : 'light')
}

onMounted(() => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
})
</script>
