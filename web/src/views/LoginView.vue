<template>
  <div class="shell register-page">
    <WebTopbar
      title="用户登录"
      :nav-items="[]"
      :theme="theme"
      :current-path="route.path"
      :current-full-path="route.fullPath"
      :search-keyword="''"
      :collapsible-search="true"
      @update:search-keyword="() => {}"
      @toggle-theme="toggleTheme"
      @search="() => {}"
    />

    <main class="register-main">
      <section class="register-card">
        <h2>读者登录</h2>
        <p class="tips">仅支持普通读者账号登录前台。</p>

        <input v-model="username" placeholder="用户名" />
        <input v-model="password" type="password" placeholder="密码" @keyup.enter="submit" />

        <button :disabled="submitting" @click="submit">
          {{ submitting ? '登录中...' : '登录' }}
        </button>

        <p class="tips">还没有账号？<RouterLink to="/register">立即注册</RouterLink></p>
        <p v-if="message" class="tips" :class="status === 'error' ? 'error-message' : 'success-message'">{{ message }}</p>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { webApi } from '../api'
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

const applyTheme = (value: ThemeMode) => {
  theme.value = value
  document.documentElement.dataset.theme = value
  localStorage.setItem('md-theme', value)
}

const toggleTheme = () => {
  applyTheme(theme.value === 'light' ? 'dark' : 'light')
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
    if (savedNickname) {
      localStorage.setItem('md-welcome-once', `欢迎回来，${savedNickname}`)
    }
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

onMounted(() => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  document.title = '用户登录 - MaDongDong'
})
</script>
