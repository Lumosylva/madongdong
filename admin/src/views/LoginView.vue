<template>
  <section class="login-wrap">
    <form class="login-card" @submit.prevent="submit">
      <p class="eyebrow">MaDongDong Admin</p>
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
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { adminApi } from '../api'

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
