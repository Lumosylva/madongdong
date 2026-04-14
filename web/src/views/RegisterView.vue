<template>
  <div class="shell register-page">
    <WebTopbar
      title="用户注册"
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
        <h2>注册普通读者账号</h2>
        <p class="tips">仅支持注册普通读者角色，系统管理员与内容作者由后台维护。</p>

        <input v-model="username" placeholder="用户名（3-50位）" />
        <input v-model="nickname" placeholder="昵称" />
        <input v-model="email" placeholder="邮箱" />
        <input v-model="password" type="password" placeholder="密码（至少6位）" />

        <button :disabled="submitting" @click="submit">
          {{ submitting ? '注册中...' : '注册' }}
        </button>

        <p v-if="message" class="tips" :class="status === 'error' ? 'error-message' : 'success-message'">{{ message }}</p>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { webApi } from '../api'
import WebTopbar from '../components/WebTopbar.vue'

type ThemeMode = 'light' | 'dark'

const route = useRoute()
const theme = ref<ThemeMode>('light')
const username = ref('')
const nickname = ref('')
const email = ref('')
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
    await webApi.registerReader({
      username: username.value.trim(),
      nickname: nickname.value.trim(),
      email: email.value.trim(),
      password: password.value,
    })
    status.value = 'success'
    message.value = '注册成功，请前往文章页参与评论。'
    username.value = ''
    nickname.value = ''
    email.value = ''
    password.value = ''
  } catch (error) {
    status.value = 'error'
    message.value = error instanceof Error ? error.message : '注册失败'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  document.title = '用户注册 - MaDongDong'
})
</script>
