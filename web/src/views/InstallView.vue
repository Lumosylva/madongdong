<template>
  <div class="install-page">
    <div class="install-card">
      <div class="install-header">
        <p class="install-eyebrow">首次安装</p>
        <h1>初始化站点</h1>
        <p>填写站点与管理员信息后即可完成初始化。</p>
      </div>

      <form class="install-form" @submit.prevent="submitInstall">
        <label>
          <span>站点标题</span>
          <input v-model="form.site_title" required />
        </label>
        <label>
          <span>副标题</span>
          <input v-model="form.site_subtitle" />
        </label>
        <label>
          <span>管理员用户名</span>
          <input v-model="form.admin_username" required />
        </label>
        <label>
          <span>管理员密码</span>
          <input v-model="form.admin_password" type="password" required />
        </label>
        <label>
          <span>管理员昵称</span>
          <input v-model="form.admin_nickname" required />
        </label>
        <label>
          <span>管理员邮箱</span>
          <input v-model="form.admin_email" type="email" required />
        </label>
        <label>
          <span>ICP备案</span>
          <input v-model="form.icp_beian" />
        </label>
        <label>
          <span>版权信息</span>
          <input v-model="form.copyright_text" />
        </label>
        <label>
          <span>首页每页文章数</span>
          <input v-model.number="form.homepage_page_size" type="number" min="1" max="100" />
        </label>
        <label class="checkbox-row">
          <input v-model="form.comment_requires_review" type="checkbox" />
          <span>评论需要审核</span>
        </label>

        <p v-if="errorMessage" class="message error">{{ errorMessage }}</p>
        <p v-if="successMessage" class="message success">{{ successMessage }}</p>

        <div class="actions">
          <button type="submit" :disabled="submitting">{{ submitting ? '初始化中...' : '开始安装' }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { webApi } from '../api'

const router = useRouter()
const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const form = reactive({
  site_title: 'MaDongDong Blog',
  site_subtitle: '记录技术、生活与长期主义',
  admin_username: 'admin',
  admin_password: 'admin123456',
  admin_nickname: '系统管理员',
  admin_email: 'admin@example.com',
  icp_beian: '备案信息待配置',
  copyright_text: '© MaDongDong Blog',
  homepage_page_size: 10,
  comment_requires_review: true,
})

const checkInstalled = async () => {
  try {
    const res = await webApi.getInstallStatus()
    if (res.data.installed) {
      router.replace('/')
    }
  } catch {
    errorMessage.value = '无法获取安装状态，请确认后端已启动。'
  }
}

const submitInstall = async () => {
  submitting.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    await fetch('/api/v1/install', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    })
    successMessage.value = '初始化完成，正在跳转...'
    window.setTimeout(() => {
      router.replace('/login')
    }, 900)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '安装失败'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  void checkInstalled()
})
</script>
