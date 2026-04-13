<template>
  <section class="login-wrap">
    <header class="topbar topbar-login">
      <div class="brand-block">
        <span class="brand-mark">MD</span>
        <h1>MaDongDong Admin</h1>
      </div>
      <nav class="nav">
        <a href="javascript:void(0)">控制台</a>
        <a href="javascript:void(0)">内容</a>
        <a href="javascript:void(0)">设置</a>
      </nav>
      <div class="topbar-actions">
        <button type="button" class="theme-toggle" :aria-label="themeToggleLabel" @click="toggleTheme">
          <span aria-hidden="true">{{ theme === 'light' ? '◐' : '☼' }}</span>
        </button>
      </div>
    </header>

    <form class="login-card" @submit.prevent="submit">
      <p class="eyebrow">MaDongDong Admin</p>
      <h2>后台登录</h2>
      <input v-model="username" placeholder="用户名" />
      <input v-model="password" type="password" placeholder="密码" />
      <button type="submit" :disabled="loading">{{ loading ? '登录中...' : '登录管理台' }}</button>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <p class="tips">默认账号：admin / admin123456</p>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { adminApi } from '../api'

type ThemeMode = 'light' | 'dark'

const router = useRouter()
const username = ref('admin')
const password = ref('admin123456')
const loading = ref(false)
const errorMessage = ref('')
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
