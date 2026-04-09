<template>
  <section class="login-wrap">
    <form class="login-card" @submit.prevent="submit">
      <div class="login-header">
        <p class="eyebrow">MaDongDong Admin</p>
        <button type="button" class="theme-toggle" :aria-label="themeToggleLabel" @click="toggleTheme">
          <span aria-hidden="true">{{ theme === 'light' ? '☀️' : '🌙' }}</span>
        </button>
      </div>
      <h1>后台登录</h1>
      <input v-model="username" placeholder="用户名" />
      <input v-model="password" type="password" placeholder="密码" />
      <button type="submit" :disabled="loading">{{ loading ? '登录中...' : '登录管理台' }}</button>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <p class="tips">默认账号：admin / admin123456</p>
    </form>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'

import { adminApi } from '../api'

type ThemeMode = 'light' | 'dark'
const theme = ref<ThemeMode>('light')

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

const router = useRouter()
const username = ref('admin')
const password = ref('admin123456')
const loading = ref(false)
const errorMessage = ref('')

const submit = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await adminApi.login(username.value, password.value)
    localStorage.setItem('blog_admin_token', response.data.access_token)
    await router.push('/')
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '登录失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const storedTheme = localStorage.getItem('md-admin-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  
  const token = localStorage.getItem('blog_admin_token')
  if (!token) {
    return
  }
  try {
    await adminApi.getMe()
    await router.replace('/')
  } catch {
    localStorage.removeItem('blog_admin_token')
  }
})
</script>
