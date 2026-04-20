<template>
  <section class="panel profile-panel">
    <div class="article-manage-head profile-head">
      <div>
        <h3>个人中心</h3>
        <p class="profile-subtitle">管理头像、昵称、联系信息和登录密码</p>
      </div>
      <span class="article-count profile-count">{{ user?.username || '-' }}</span>
    </div>

    <div class="profile-stack">
      <section class="profile-card profile-avatar-card">
        <h4>头像</h4>
        <div class="profile-avatar-wrap">
          <img v-if="avatarPreview" :src="avatarPreview" alt="avatar" class="profile-avatar" />
          <div v-else class="profile-avatar-placeholder">{{ avatarInitial }}</div>
        </div>

        <div class="profile-avatar-actions">
          <input ref="avatarInputRef" class="profile-file-input" type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml" @change="onAvatarSelect" />
          <button type="button" class="profile-button secondary" @click="avatarInputRef?.click()">更换头像</button>
        </div>
        <p class="profile-hint">上传后会自动裁剪为正方形并压缩</p>
      </section>

      <section class="profile-card profile-form-card">
        <h4>基础资料</h4>
        <label class="profile-field">
          <span>用户名</span>
          <input class="profile-input" :value="username" disabled />
        </label>
        <label class="profile-field">
          <span>昵称 <em>*</em></span>
          <input class="profile-input" v-model="nickname" placeholder="请输入昵称" />
        </label>
        <label class="profile-field">
          <span>联系信息（邮箱） <em>*</em></span>
          <input class="profile-input" v-model="email" placeholder="请输入邮箱" />
        </label>
      </section>

      <section class="profile-card profile-form-card profile-password-card">
        <h4>安全设置</h4>
        <label class="profile-field">
          <span>新密码</span>
          <input class="profile-input" v-model="newPassword" type="password" placeholder="设置新密码（留空则不修改）" />
        </label>
        <div class="profile-actions">
          <button type="button" class="profile-button primary" :disabled="saving" @click="saveProfile">更新个人资料</button>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

type UserInfo = {
  id: number
  username: string
  nickname: string
  email: string
  avatar?: string | null
}

const props = defineProps<{ user: UserInfo | null }>()
const emit = defineEmits<{ save: [payload: { nickname: string; email: string; avatar: string | null; password: string | null }] }>()

const avatarInputRef = ref<HTMLInputElement | null>(null)
const avatarPreview = ref('')
const nickname = ref('')
const email = ref('')
const newPassword = ref('')
const saving = ref(false)

watch(
  () => props.user,
  (value) => {
    nickname.value = value?.nickname || ''
    email.value = value?.email || ''
    avatarPreview.value = value?.avatar || ''
  },
  { immediate: true },
)

const username = computed(() => props.user?.username || '-')
const avatarInitial = computed(() => (nickname.value || username.value).slice(0, 1).toUpperCase() || 'U')

const loadImage = (file: File) =>
  new Promise<HTMLImageElement>((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = () => reject(new Error('读取头像文件失败'))
    reader.onload = () => {
      const image = new Image()
      image.onerror = () => reject(new Error('加载头像图片失败'))
      image.onload = () => resolve(image)
      image.src = String(reader.result || '')
    }
    reader.readAsDataURL(file)
  })

const compressAvatar = async (file: File) => {
  if (!file.type.startsWith('image/')) {
    return new Promise<string>((resolve, reject) => {
      const reader = new FileReader()
      reader.onerror = () => reject(new Error('读取头像文件失败'))
      reader.onload = () => resolve(String(reader.result || ''))
      reader.readAsDataURL(file)
    })
  }

  if (file.type === 'image/svg+xml') {
    return new Promise<string>((resolve, reject) => {
      const reader = new FileReader()
      reader.onerror = () => reject(new Error('读取头像文件失败'))
      reader.onload = () => resolve(String(reader.result || ''))
      reader.readAsDataURL(file)
    })
  }

  const image = await loadImage(file)
  const size = Math.min(image.width, image.height)
  const offsetX = Math.floor((image.width - size) / 2)
  const offsetY = Math.floor((image.height - size) / 2)
  const canvas = document.createElement('canvas')
  const outputSize = Math.min(256, size || 256)
  canvas.width = outputSize
  canvas.height = outputSize
  const context = canvas.getContext('2d')
  if (!context) throw new Error('头像压缩失败')
  context.drawImage(image, offsetX, offsetY, size, size, 0, 0, outputSize, outputSize)
  return canvas.toDataURL('image/jpeg', 0.9)
}

const onAvatarSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  avatarPreview.value = await compressAvatar(file)
  target.value = ''
}

const saveProfile = async () => {
  if (saving.value) return
  if (!nickname.value.trim()) return
  if (!email.value.trim()) return
  saving.value = true
  try {
    emit('save', {
      nickname: nickname.value.trim(),
      email: email.value.trim(),
      avatar: avatarPreview.value || null,
      password: newPassword.value || null,
    })
  } finally {
    saving.value = false
  }
}
</script>
