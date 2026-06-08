<template>
  <div class="shell auth-page">
    <WebTopbar
      title="用户注册"
      subtitle="创建账号，开启更完整的阅读体验"
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
        <p class="auth-eyebrow">Join the community</p>
        <h2>创建您的账号</h2>
        <p>注册后可参与评论、保存个人昵称，并获得更流畅的站内体验。</p>
      </section>

      <section class="auth-card">
        <div class="auth-card-header">
          <h3>注册账号</h3>
        </div>

        <div class="auth-field-group">
          <label class="auth-input-shell">
            <span class="auth-input-icon" aria-hidden="true">👤</span>
            <input v-model="username" autocomplete="username" placeholder="用户名（3-50位）" />
          </label>
          <label class="auth-input-shell">
            <span class="auth-input-icon" aria-hidden="true">✨</span>
            <input v-model="nickname" autocomplete="nickname" placeholder="昵称" />
          </label>
          <label class="auth-input-shell">
            <span class="auth-input-icon" aria-hidden="true">✉️</span>
            <input v-model="email" autocomplete="email" type="email" placeholder="邮箱" />
          </label>
          <label class="auth-input-shell auth-password-shell">
            <span class="auth-input-icon" aria-hidden="true">🔒</span>
            <input :type="showPassword ? 'text' : 'password'" v-model="password" autocomplete="new-password" placeholder="密码（至少6位）" />
            <button type="button" class="auth-password-toggle" @click="showPassword = !showPassword">{{ showPassword ? '隐藏' : '显示' }}</button>
          </label>
          <p class="auth-field-hint">注册后可自动登录并进入首页。</p>
        </div>

        <button class="auth-submit-btn" :disabled="submitting" @click="submit">
          {{ submitting ? '注册中...' : '注册' }}
        </button>

        <p class="auth-switch-link">
          已有账号？<RouterLink to="/login">返回登录</RouterLink>
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
const nickname = ref('')
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const submitting = ref(false)
const message = ref('')
const status = ref<'success' | 'error' | ''>('')
const siteLogoUrl = ref('')
const authNavItems = computed(() => [
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
    await webApi.registerReader({
      username: username.value.trim(),
      nickname: nickname.value.trim(),
      email: email.value.trim(),
      password: password.value,
    })
    const token = await webApi.loginReader({
      username: username.value.trim(),
      password: password.value,
    })
    localStorage.setItem('md_web_token', token.access_token)
    status.value = 'success'
    message.value = '注册成功，正在自动登录并跳转首页...'
    const displayName = nickname.value.trim() || username.value.trim()
    localStorage.setItem('md-welcome-once', `欢迎加入，${displayName}`)
    localStorage.setItem('md-reader-nickname', displayName)
    localStorage.setItem('md-reader-email', email.value.trim())
    username.value = ''
    nickname.value = ''
    email.value = ''
    password.value = ''
    setTimeout(() => {
      router.push('/')
    }, 500)
  } catch (error) {
    status.value = 'error'
    message.value = error instanceof Error ? error.message : '注册失败'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  document.title = '用户注册 - MaDongDong'
  await loadSiteLogo()
})
</script>
