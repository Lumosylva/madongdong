<template>
  <div class="shell auth-page">
    <WebTopbar
      title="用户登录"
      subtitle="欢迎回来，继续阅读精彩内容"
      :logo-url="siteLogoUrl"
      :nav-items="authNavItems"
      :theme="theme"
      :current-path="route.path"
      :current-full-path="route.fullPath"
      :search-keyword="''"
      :collapsible-search="false"
      @update:search-keyword="() => {}"
      @toggle-theme="toggleTheme"
      @search="() => {}"
    />

    <main class="auth-main">
      <section class="auth-hero">
        <p class="auth-eyebrow">Reader Portal</p>
        <h2>登录您的账号</h2>
        <p>在这里进入您的个人阅读中心，继续浏览、评论与收藏感兴趣的内容。</p>
      </section>

      <section class="auth-card">
        <div class="auth-card-header">
          <h3>登录</h3>
          <p>使用账号登录前台</p>
        </div>

        <div class="auth-field-group">
          <label class="auth-input-shell">
            <span class="auth-input-icon" aria-hidden="true">👤</span>
            <input v-model="username" autocomplete="username" placeholder="用户名" />
          </label>
          <label class="auth-input-shell auth-password-shell">
            <span class="auth-input-icon" aria-hidden="true">🔒</span>
            <input :type="showPassword ? 'text' : 'password'" v-model="password" autocomplete="current-password" placeholder="密码" @keyup.enter="submit" />
            <button type="button" class="auth-password-toggle" :aria-label="showPassword ? '隐藏密码' : '显示密码'" :title="showPassword ? '隐藏密码' : '显示密码'" @click="showPassword = !showPassword">
              <svg v-if="showPassword" viewBox="0 0 24 24" aria-hidden="true" class="auth-password-toggle-icon">
                <path d="M3.98 5.11 5.4 3.7l14.9 14.9-1.42 1.41-2.02-2.02A10.74 10.74 0 0 1 12 19c-5.2 0-9.64-3.22-11.38-7.75a1.24 1.24 0 0 1 0-.9A11.57 11.57 0 0 1 5.15 5.55L3.98 5.11Zm4.16 4.17a4 4 0 0 0 5.68 5.68l-1.45-1.45A2 2 0 0 1 8.28 9.73l-.14-.45Zm4.52-4.5A11.45 11.45 0 0 1 22.4 11a1.24 1.24 0 0 1 0 .9 11.46 11.46 0 0 1-2.84 4.27l-1.41-1.41A9.45 9.45 0 0 0 19.96 11 9.5 9.5 0 0 0 15 6.47l.01.01Zm-1.93 1.2A4 4 0 0 0 10.55 14l-1.46-1.46a4 4 0 0 1 3.47-5.57Z" fill="currentColor"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" aria-hidden="true" class="auth-password-toggle-icon">
                <path d="M12 5c5.2 0 9.64 3.22 11.38 7.75a1.24 1.24 0 0 1 0 .9C21.64 18.18 17.2 21.4 12 21.4S2.36 18.18.62 13.65a1.24 1.24 0 0 1 0-.9C2.36 8.22 6.8 5 12 5Zm0 2C8 7 4.64 9.4 3.17 12c1.47 2.6 4.83 5 8.83 5s7.36-2.4 8.83-5C19.36 9.4 16 7 12 7Zm0 1.6A3.4 3.4 0 1 1 8.6 12 3.4 3.4 0 0 1 12 8.6Zm0 2A1.4 1.4 0 1 0 13.4 12 1.4 1.4 0 0 0 12 10.6Z" fill="currentColor"/>
              </svg>
            </button>
          </label>
          <label class="auth-remember-row">
            <input v-model="rememberMe" type="checkbox" />
            <span>记住我</span>
          </label>
        </div>

        <button class="auth-submit-btn" :disabled="submitting" @click="submit">
          {{ submitting ? '登录中...' : '登录' }}
        </button>

        <p class="auth-switch-link">
          还没有账号？<RouterLink to="/register">立即注册</RouterLink>
        </p>
        <p v-if="message" class="auth-message" :class="status === 'error' ? 'error-message' : 'success-message'">{{ message }}</p>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { toAbsoluteAssetUrl, webApi } from '../api'
import WebTopbar from '../components/WebTopbar.vue'
import type { NavItem } from '../types'

type ThemeMode = 'light' | 'dark'

const route = useRoute()
const router = useRouter()
const theme = ref<ThemeMode>('light')
const username = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberMe = ref(true)
const submitting = ref(false)
const message = ref('')
const status = ref<'success' | 'error' | ''>('')
const siteLogoUrl = ref('')
const authNavItems = computed<NavItem[]>(() => [
  { id: 1, title: '首页', path: '/', sort_order: 1, is_visible: true, target: null, description: null },
  { id: 2, title: '登录', path: '/login', sort_order: 2, is_visible: true, target: null, description: null },
  { id: 3, title: '注册', path: '/register', sort_order: 3, is_visible: true, target: null, description: null },
])

const applyTheme = (value: ThemeMode) => {
  theme.value = value
  document.documentElement.dataset.theme = value
  localStorage.setItem('md-theme', value)
}

const toggleTheme = () => {
  applyTheme(theme.value === 'light' ? 'dark' : 'light')
}

const loadSiteLogo = async () => {
  try {
    const home = await webApi.getHome(1, 1)
    siteLogoUrl.value = toAbsoluteAssetUrl(home.site.site_logo)
  } catch {
    siteLogoUrl.value = ''
  }
}

const submit = async () => {
  if (submitting.value) return
  submitting.value = true
  message.value = ''
  status.value = ''

  try {
    const token = await webApi.loginReader({
      username: username.value.trim(),
      password: password.value,
    })
    localStorage.setItem('md_web_token', token.access_token)
    if (rememberMe.value) {
      localStorage.setItem('md-login-username', username.value.trim())
    } else {
      localStorage.removeItem('md-login-username')
    }
    const savedNickname = localStorage.getItem('md-reader-nickname')
    const displayName = savedNickname || username.value.trim()
    localStorage.setItem('md-reader-nickname', displayName)
    localStorage.setItem('md-welcome-once', `欢迎回来，${displayName}`)
    localStorage.removeItem('md-home-welcome-shown')
    status.value = 'success'
    message.value = '登录成功，正在跳转首页...'
    setTimeout(() => {
      router.push('/')
    }, 500)
  } catch (error) {
    status.value = 'error'
    message.value = error instanceof Error ? error.message : '登录失败'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  const savedUsername = localStorage.getItem('md-login-username')
  if (savedUsername) {
    username.value = savedUsername
    rememberMe.value = true
  }
  document.title = '用户登录 - MaDongDong'
  await loadSiteLogo()
})
</script>
