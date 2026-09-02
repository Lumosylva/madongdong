<template>
  <section class="panel profile-panel">
    <div class="profile-head">
      <div>
        <h3>{{ t('profile.title') }}</h3>
        <p class="profile-subtitle">{{ t('profile.subtitle') }}</p>
      </div>
      <span class="profile-count">{{ user?.username || '-' }}</span>
    </div>

    <div class="profile-stack">
      <section class="profile-card profile-avatar-card">
        <h4>{{ t('profile.avatarSection') }}</h4>
        <div class="profile-avatar-wrap">
          <img v-if="avatarPreview" :src="avatarPreview" alt="avatar" class="profile-avatar" />
          <div v-else class="profile-avatar-placeholder">{{ avatarInitial }}</div>
        </div>

        <div class="profile-avatar-actions">
          <input ref="avatarInputRef" class="profile-file-input" type="file" accept="image/png,image/jpeg,image/webp" @change="onAvatarSelect" />
          <button type="button" class="profile-button secondary" @click="avatarInputRef?.click()">{{ t('profile.changeAvatar') }}</button>
        </div>
        <p class="profile-hint">{{ t('profile.avatarTip') }}</p>
      </section>

      <section class="profile-card profile-form-card">
        <h4>{{ t('profile.basicSection') }}</h4>
        <label class="profile-field">
          <span>{{ t('profile.usernameLabel') }}</span>
          <input class="profile-input" :value="username" disabled />
        </label>
        <label class="profile-field">
          <span>{{ t('profile.nicknameLabel') }} <em>*</em></span>
          <input class="profile-input" v-model="nickname" :placeholder="t('profile.nicknamePlaceholder')" />
        </label>
        <label class="profile-field">
          <span>{{ t('profile.emailLabel') }} <em>*</em></span>
          <input class="profile-input" v-model="email" :placeholder="t('profile.emailPlaceholder')" />
        </label>
      </section>

      <section class="profile-card profile-form-card profile-password-card">
        <h4>{{ t('profile.securitySection') }}</h4>
        <label class="profile-field">
          <span>{{ t('profile.newPassword') }}</span>
          <input class="profile-input" v-model="newPassword" type="password" :placeholder="t('profile.newPwPlaceholder')" />
        </label>
        <div class="profile-actions">
          <button type="button" class="profile-button primary" :disabled="saving" @click="saveProfile">{{ t('profile.saveProfile') }}</button>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

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
    reader.onerror = () => reject(new Error(t('profile.readFailed')))
    reader.onload = () => {
      const image = new Image()
      image.onerror = () => reject(new Error(t('profile.loadFailed')))
      image.onload = () => resolve(image)
      image.src = String(reader.result || '')
    }
    reader.readAsDataURL(file)
  })

const compressAvatar = async (file: File) => {
  if (!file.type.startsWith('image/')) {
    return new Promise<string>((resolve, reject) => {
      const reader = new FileReader()
      reader.onerror = () => reject(new Error(t('profile.readFailed')))
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
  if (!context) throw new Error(t('profile.compressFailed'))
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
