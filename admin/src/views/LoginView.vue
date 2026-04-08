<template>
  <section class="login-wrap">
    <form class="login-card" @submit.prevent="submit">
      <p class="eyebrow">MaDongDong Admin</p>
      <h1>后台登录</h1>
      <input v-model="username" placeholder="用户名" />
      <input v-model="password" type="password" placeholder="密码" />
      <button type="submit">登录管理台</button>
      <p class="tips">默认账号：admin / admin123456</p>
    </form>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { adminApi } from '../api'

const router = useRouter()
const username = ref('admin')
const password = ref('admin123456')

const submit = async () => {
  const response = await adminApi.login(username.value, password.value)
  localStorage.setItem('blog_admin_token', response.data.access_token)
  router.push('/')
}
</script>
