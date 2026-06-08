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
              <svg v-if="showPassword" class="auth-password-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M3.53 2.47 2.47 3.53l3.06 3.06C3.44 8.3 1.94 10.16 1 12c1.86 3.62 5.75 8 11 8 1.61 0 3.15-.32 4.57-.89l3.9 3.9 1.06-1.06-18-18Zm7.04 9.16 1.8 1.8a2.5 2.5 0 0 1-3.57-3.57l1.77 1.77ZM12 6c4.41 0 8.3 4.38 10 6-1.07 2.09-2.73 4.22-4.78 5.74l-2.05-2.05a4 4 0 0 0-5.61-5.61L7.51 7.51A10.16 10.16 0 0 1 12 6Zm0 12c-4.09 0-7.38-3.1-9.08-6 1.08-1.88 2.6-3.68 4.4-5.01l1.52 1.52a8 8 0 0 0 6.98 6.98l1.52 1.52C15.08 17.52 13.62 18 12 18Z" fill="currentColor"/>
              </svg>
              <svg v-else class="auth-password-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 5c-5.25 0-9.14 4.38-11 7 1.86 2.62 5.75 7 11 7s9.14-4.38 11-7c-1.86-2.62-5.75-7-11-7Zm0 12c-4.09 0-7.38-3.1-9.08-5 1.7-1.9 5-5 9.08-5s7.38 3.1 9.08 5c-1.7 1.9-5 5-9.08 5Zm0-8a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z" fill="currentColor"/>
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
