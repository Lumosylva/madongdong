<template>
  <section class="login-wrap">
    <header class="topbar topbar-login">
      <div class="brand-block">
        <span class="brand-mark">MD</span>
        <div>
          <h1>MaDongDong仪表盘</h1>
        </div>
      </div>
      <div class="topbar-actions">
        <button type="button" class="theme-toggle login-theme-toggle" :aria-label="themeToggleLabel" @click="toggleTheme">
          <span aria-hidden="true">{{ theme === 'light' ? '◐' : '☼' }}</span>
        </button>
      </div>
    </header>

    <div class="login-stage">
      <aside class="login-hero">
        <div class="login-hero-visual" aria-hidden="true">
          <div class="login-hero-orb orb-a"></div>
          <div class="login-hero-orb orb-b"></div>
        </div>
        <h2>欢迎进入仪表盘</h2>
        <p class="login-hero-text">统一管理文章、媒体、分类与评论，保持内容生产与审核流程清晰、高效。</p>
        <div class="login-hero-points">
          <div class="login-hero-point">
            <strong>文章管理</strong>
            <span>发布、草稿、垃圾箱一站式处理</span>
          </div>
          <div class="login-hero-point">
            <strong>媒体管理</strong>
            <span>上传、预览、批量删除更顺手</span>
          </div>
          <div class="login-hero-point">
            <strong>分类与评论</strong>
            <span>快速维护内容结构与互动质量</span>
          </div>
        </div>
      </aside>

      <form class="login-card" @submit.prevent="submit">
        <div class="login-card-head">
          <h2>进入仪表盘</h2>
          <p class="login-card-subtitle">请输入管理员账号与密码</p>
        </div>

        <label class="login-field">
          <span>用户名</span>
          <input v-model="username" placeholder="请输入用户名" autocomplete="username" />
        </label>

        <label class="login-field">
          <span>密码</span>
          <div class="login-password-row">
            <input v-model="password" :type="showPassword ? 'text' : 'password'" placeholder="请输入密码" autocomplete="current-password" />
            <button
              type="button"
              class="login-password-toggle"
              :aria-label="showPassword ? '隐藏密码' : '显示密码'"
              @mousedown.prevent="showPassword = true"
              @mouseup.prevent="showPassword = false"
              @mouseleave.prevent="showPassword = false"
              @touchstart.prevent="showPassword = true"
              @touchend.prevent="showPassword = false"
              @touchcancel.prevent="showPassword = false"
              @blur="showPassword = false"
            >
              <svg v-if="showPassword" class="login-password-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/>
              </svg>
              <svg v-else class="login-password-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M1.8 12s3.4-6.2 10.2-6.2S22.2 12 22.2 12s-3.4 6.2-10.2 6.2S1.8 12 1.8 12Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/>
                <path d="M4 20L20 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
        </label>

        <button type="submit" class="login-submit-btn" :disabled="loading">{{ loading ? '登录中...' : '登录' }}</button>
        <p v-if="errorMessage" class="error-message login-error">{{ errorMessage }}</p>
      </form>
    </div>
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
const showPassword = ref(false)
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
    const message = error instanceof Error ? error.message : '登录失败，请稍后重试'
    if (message.includes('用户名或密码错误')) {
      errorMessage.value = '用户名或密码错误，请检查后重试'
    } else {
      errorMessage.value = message || '登录失败，请稍后重试'
    }
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
