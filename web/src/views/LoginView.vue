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
          <label>
            <span>用户名</span>
            <input v-model="username" autocomplete="username" placeholder="请输入用户名" />
          </label>
          <label>
            <span>密码</span>
            <input v-model="password" autocomplete="current-password" type="password" placeholder="请输入密码" @keyup.enter="submit" />
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

type ThemeMode = 'light' | 'dark'

const route = useRoute()
const router = useRouter()
const theme = ref<ThemeMode>('light')
const username = ref('')
const password = ref('')
const submitting = ref(false)
const message = ref('')
const status = ref<'success' | 'error' | ''>('')
const siteLogoUrl = ref('')
const authNavItems = computed(() => [
  { id: 'home', title: '首页', path: '/' },
  { id: 'login', title: '登录', path: '/login' },
  { id: 'register', title: '注册', path: '/register' },
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
  document.title = '用户登录 - MaDongDong'
  await loadSiteLogo()
})
</script>
