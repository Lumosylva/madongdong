<template>
  <div class="profile-page" v-if="siteData.site_title">
    <WebTopbar
      :title="siteData.site_title"
      :subtitle="siteData.site_subtitle"
      :logo-url="toAbsoluteAssetUrl(siteData.site_logo)"
      :nav-items="navItems"
      :theme="theme"
      :current-path="route.path"
      :current-full-path="route.fullPath"
      @toggle-theme="toggleTheme"
    />

    <main class="profile-main">
      <section class="profile-hero">
        <RouterLink to="/" class="profile-back-link">
          <svg viewBox="0 0 24 24" class="profile-back-icon" aria-hidden="true"><path d="M19 12H5m0 0 7 7m-7-7 7-7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          {{ t('common.backToHome') }}
        </RouterLink>
        <p class="profile-eyebrow">Personal Center</p>
        <h2>{{ t('profile.title') }}</h2>
        <p class="profile-hero-desc">{{ t('profile.subtitle') }}</p>
      </section>

      <section v-if="!isLoggedIn" class="profile-auth-card">
        <div class="profile-auth-icon">🔒</div>
        <h3>{{ t('profile.notLoggedIn') }}</h3>
        <p>{{ t('profile.notLoggedInDesc') }}</p>
        <div class="profile-auth-actions">
          <RouterLink to="/login" class="profile-btn primary">{{ t('profile.goToLogin') }}</RouterLink>
          <RouterLink to="/register" class="profile-btn ghost">{{ t('profile.registerNew') }}</RouterLink>
        </div>
      </section>

      <template v-else>
        <transition name="toast-fade">
          <div v-if="successMessage" class="profile-toast success">
            <svg viewBox="0 0 24 24" class="profile-toast-icon" aria-hidden="true"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            {{ successMessage }}
          </div>
        </transition>
        <transition name="toast-fade">
          <div v-if="errorMessage" class="profile-toast error">
            <svg viewBox="0 0 24 24" class="profile-toast-icon" aria-hidden="true"><path d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            {{ errorMessage }}
          </div>
        </transition>

        <div class="profile-grid">
          <div class="profile-card profile-avatar-card">
            <div class="profile-avatar-wrap">
              <img v-if="avatarPreview" :src="avatarPreview" alt="avatar" class="profile-avatar" />
              <div v-else class="profile-avatar-placeholder">{{ avatarInitial }}</div>
            </div>
            <div class="profile-avatar-info">
              <strong>{{ nickname || user?.username }}</strong>
              <span>{{ user?.email }}</span>
            </div>
            <div class="profile-avatar-actions">
              <input ref="avatarInputRef" class="profile-file-input" type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml" @change="onAvatarSelect" />
              <button type="button" class="profile-btn secondary sm" @click="avatarInputRef?.click()">{{ t('profile.changeAvatar') }}</button>
              <button v-if="avatarPreview" type="button" class="profile-btn ghost sm" @click="clearAvatar">{{ t('profile.clear') }}</button>
            </div>
            <p class="profile-hint">{{ t('profile.avatarHint') }}</p>
          </div>

          <div class="profile-form-stack">
            <div class="profile-card">
              <h4>{{ t('profile.basicInfo') }}</h4>
              <label class="profile-field">
                <span>{{ t('profile.username') }}</span>
                <input class="profile-input" :value="user?.username" disabled />
              </label>
              <label class="profile-field">
                <span>{{ t('profile.nickname') }} <em>*</em></span>
                <input class="profile-input" v-model="nickname" :placeholder="t('profile.nicknamePlaceholder')" />
              </label>
              <label class="profile-field">
                <span>{{ t('profile.email') }} <em>*</em></span>
                <input class="profile-input" v-model="email" :placeholder="t('profile.emailPlaceholder')" />
              </label>
            </div>

            <div class="profile-card">
              <h4>{{ t('profile.security') }}</h4>
              <label class="profile-field">
                <span>{{ t('profile.newPassword') }}</span>
                <input class="profile-input" v-model="newPassword" type="password" :placeholder="t('profile.newPwPlaceholder')" />
              </label>
            </div>

            <div class="profile-submit-row">
              <button type="button" class="profile-btn primary lg" :disabled="saving" @click="saveProfile">
                <svg v-if="!saving" viewBox="0 0 24 24" class="profile-btn-icon" aria-hidden="true"><path d="M4.5 12.75l6 6 9-13.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                <span v-if="saving" class="profile-spinner"></span>
                {{ saving ? t('profile.saving') : t('profile.saveChanges') }}
              </button>
            </div>
          </div>
        </div>
      </template>
    </main>
  </div>
  <div v-else class="profile-page skeleton-page">
    <div class="skeleton-card" style="max-width:860px;margin:40px auto;padding:20px;">
      <div class="skeleton skeleton-title"></div>
      <div class="skeleton skeleton-line w-80"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import WebTopbar from '../components/WebTopbar.vue'
import { webApi, toAbsoluteAssetUrl } from '../api'
import type { NavItem } from '../types'
import { useTheme } from '../composables/useTheme'

const route = useRoute()
const { t } = useI18n()

const { theme, toggleTheme, initTheme, listenThemeChange, destroyTheme } = useTheme()
const isLoggedIn = ref(false)
const user = ref<{ id: number; username: string; nickname: string; email: string; avatar: string | null } | null>(null)
const siteData = ref<{ site_title: string; site_subtitle: string; site_logo: string | null }>({
  site_title: '',
  site_subtitle: '',
  site_logo: null,
})
const navItems = ref<NavItem[]>([])

const avatarInputRef = ref<HTMLInputElement | null>(null)
const avatarPreview = ref('')
const nickname = ref('')
const email = ref('')
const newPassword = ref('')
const saving = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
let messageTimer: number | null = null

const avatarInitial = computed(() => (nickname.value || user.value?.username || 'U').slice(0, 1).toUpperCase())

const showMessage = (msg: string, type: 'success' | 'error') => {
  if (messageTimer) clearTimeout(messageTimer)
  if (type === 'success') {
    successMessage.value = msg
    errorMessage.value = ''
  } else {
    errorMessage.value = msg
    successMessage.value = ''
  }
  messageTimer = window.setTimeout(() => {
    successMessage.value = ''
    errorMessage.value = ''
  }, 4000)
}

const loadImage = (file: File) =>
  new Promise<HTMLImageElement>((resolve, reject) => {
    const reader = new FileReader()
      reader.onerror = () => reject(new Error(t('profile.readFailed')))
    reader.onload = () => {
      const image = new Image()
      image.onerror = () => reject(new Error(t('profile.imageFailed')))
      image.onload = () => resolve(image)
      image.src = String(reader.result || '')
    }
    reader.readAsDataURL(file)
  })

const compressAvatar = async (file: File) => {
  if (!file.type.startsWith('image/') || file.type === 'image/svg+xml') {
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
  try {
    avatarPreview.value = await compressAvatar(file)
  } catch {
    avatarPreview.value = ''
  } finally {
    target.value = ''
  }
}

const clearAvatar = () => {
  avatarPreview.value = ''
  if (avatarInputRef.value) avatarInputRef.value.value = ''
}

const saveProfile = async () => {
  if (saving.value) return
  if (!nickname.value.trim()) return
  if (!email.value.trim()) return
  saving.value = true
  try {
    const updated = await webApi.updateCurrentWebUser({
      nickname: nickname.value.trim(),
      email: email.value.trim(),
      avatar: avatarPreview.value || null,
      password: newPassword.value || null,
    })
    user.value = updated
    localStorage.setItem('md-reader-nickname', updated.nickname)
    localStorage.setItem('md-reader-email', updated.email)
    newPassword.value = ''
    showMessage(t('profile.updated'), 'success')
  } catch (err) {
    showMessage(err instanceof Error ? err.message : t('profile.saveFailed'), 'error')
  } finally {
    saving.value = false
  }
}

watch(
  () => user.value,
  (value) => {
    if (value) {
      nickname.value = value.nickname || ''
      email.value = value.email || ''
      if (!avatarPreview.value) {
        avatarPreview.value = value.avatar || ''
      }
    }
  },
  { immediate: true },
)

onMounted(async () => {
  initTheme()
  listenThemeChange()

  try {
    const homeRes = await webApi.getHome(1, 1)
    siteData.value = {
      site_title: homeRes.site.site_title,
      site_subtitle: homeRes.site.site_subtitle || '',
      site_logo: homeRes.site.site_logo,
    }
    navItems.value = homeRes.nav_items || []
  } catch {
    // ignore
  }

  const hasCookie = document.cookie.split('; ').some(c => c.startsWith('web_logged_in='))
  if (!hasCookie) {
    isLoggedIn.value = false
    return
  }

  try {
    const currentUser = await webApi.getCurrentWebUser()
    user.value = currentUser
    isLoggedIn.value = true
    localStorage.setItem('md-reader-nickname', currentUser.nickname)
  } catch {
    isLoggedIn.value = false
  }
})

onBeforeUnmount(() => {
  destroyTheme()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
}

.profile-main {
  position: relative;
  z-index: 1;
  max-width: 860px;
  margin: 0 auto;
  padding: 28px 20px 60px;
  display: grid;
  gap: 20px;
}

.profile-back-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--text-soft);
  font-size: 13px;
  text-decoration: none;
  transition: color 0.15s ease;
  margin-bottom: 4px;
}

.profile-back-link:hover {
  color: var(--accent);
}

.profile-back-icon {
  width: 16px;
  height: 16px;
}

.profile-eyebrow {
  margin: 0;
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.profile-hero {
  display: grid;
  gap: 8px;
}

.profile-hero h2 {
  margin: 0;
  font-size: clamp(26px, 3.5vw, 36px);
  line-height: 1.15;
}

.profile-hero-desc {
  margin: 0;
  color: var(--text-soft);
  font-size: 15px;
  line-height: 1.7;
  max-width: 52ch;
}

.profile-auth-card {
  text-align: center;
  padding: 48px 30px;
  border: 1px solid var(--line);
  border-radius: 24px;
  background: var(--bg-panel);
  backdrop-filter: blur(10px);
  display: grid;
  gap: 12px;
  justify-items: center;
  position: relative;
}

.profile-auth-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.18), transparent 34%, transparent 66%, rgba(14, 165, 164, 0.06));
  opacity: 0.5;
}

.profile-auth-icon {
  font-size: 48px;
  line-height: 1;
}

.profile-auth-card h3 {
  margin: 0;
  font-size: 20px;
}

.profile-auth-card > p {
  margin: 0;
  color: var(--text-soft);
  font-size: 14px;
}

.profile-auth-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

/* ── Toast ── */

.profile-toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid transparent;
}

.profile-toast-icon {
  width: 20px;
  height: 20px;
  flex: 0 0 auto;
}

.profile-toast.success {
  color: var(--accent);
  background: rgba(14, 165, 164, 0.1);
  border-color: rgba(14, 165, 164, 0.22);
}

.profile-toast.error {
  color: var(--danger);
  background: rgba(227, 91, 119, 0.08);
  border-color: rgba(227, 91, 119, 0.18);
}

.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ── Grid Layout ── */

.profile-grid {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}

.profile-form-stack {
  display: grid;
  gap: 16px;
}

/* ── Cards ── */

.profile-card {
  border: 1px solid var(--line);
  border-radius: 24px;
  background: var(--bg-panel);
  backdrop-filter: blur(10px);
  padding: 24px;
  display: grid;
  gap: 16px;
  position: relative;
}

.profile-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.18), transparent 34%, transparent 66%, rgba(14, 165, 164, 0.06));
  opacity: 0.5;
}

.profile-card h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  position: relative;
}

/* ── Avatar Card ── */

.profile-avatar-card {
  justify-items: center;
  text-align: center;
}

.profile-avatar-wrap {
  position: relative;
  width: 110px;
  height: 110px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid rgba(14, 165, 164, 0.25);
  box-shadow: 0 12px 32px rgba(16, 35, 63, 0.12);
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.16), rgba(56, 189, 248, 0.12));
  display: grid;
  place-items: center;
}

.profile-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-avatar-placeholder {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  font-size: 38px;
  font-weight: 800;
  color: #0f172a;
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.25), rgba(59, 130, 246, 0.16));
}

.profile-avatar-info {
  display: grid;
  gap: 2px;
  position: relative;
}

.profile-avatar-info strong {
  font-size: 16px;
  line-height: 1.4;
}

.profile-avatar-info span {
  color: var(--text-soft);
  font-size: 13px;
}

.profile-avatar-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
  position: relative;
}

.profile-file-input {
  display: none;
}

.profile-hint {
  margin: 0;
  color: var(--text-soft);
  font-size: 12px;
  line-height: 1.5;
  position: relative;
}

/* ── Form Fields ── */

.profile-field {
  display: grid;
  gap: 6px;
}

.profile-field > span {
  color: var(--text-soft);
  font-size: 13px;
  font-weight: 500;
}

.profile-field em {
  color: var(--danger);
  font-style: normal;
}

.profile-input {
  width: 100%;
  min-height: 44px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(255, 255, 255, 0.6);
  color: var(--text);
  padding: 0 14px;
  font-size: 14px;
  position: relative;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease, background 0.18s ease;
}

.profile-input::placeholder {
  color: color-mix(in srgb, var(--text-soft) 70%, white);
}

.profile-input:hover {
  border-color: rgba(14, 165, 164, 0.3);
  background: rgba(255, 255, 255, 0.8);
}

.profile-input:focus {
  outline: none;
  border-color: rgba(14, 165, 164, 0.6);
  box-shadow: 0 0 0 3px rgba(14, 165, 164, 0.16);
  transform: translateY(-1px);
}

.profile-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: rgba(148, 163, 184, 0.06);
}

/* ── Buttons ── */

.profile-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 42px;
  border-radius: 12px;
  padding: 0 20px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  border: 1px solid rgba(14, 165, 164, 0.2);
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.14), rgba(56, 189, 248, 0.08));
  color: var(--text);
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}

.profile-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  border-color: rgba(14, 165, 164, 0.34);
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.2), rgba(56, 189, 248, 0.14));
  box-shadow: 0 10px 22px rgba(16, 35, 63, 0.09);
}

.profile-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.profile-btn.primary {
  background: linear-gradient(135deg, var(--accent), rgba(56, 189, 248, 0.8));
  color: #fff;
  border-color: transparent;
  box-shadow: 0 8px 20px rgba(14, 165, 164, 0.25);
}

.profile-btn.primary:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--accent), rgba(56, 189, 248, 0.9));
  box-shadow: 0 12px 28px rgba(14, 165, 164, 0.35);
}

.profile-btn.secondary {
  border-color: rgba(148, 163, 184, 0.22);
  background: rgba(255, 255, 255, 0.5);
  color: var(--text-soft);
}

.profile-btn.secondary:hover:not(:disabled) {
  border-color: rgba(14, 165, 164, 0.3);
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.1), rgba(56, 189, 248, 0.06));
  color: var(--text);
}

.profile-btn.ghost {
  border-color: transparent;
  background: transparent;
  color: var(--text-soft);
}

.profile-btn.ghost:hover:not(:disabled) {
  color: var(--text);
  background: rgba(148, 163, 184, 0.08);
}

.profile-btn.sm {
  min-height: 34px;
  padding: 0 14px;
  font-size: 13px;
  border-radius: 10px;
}

.profile-btn.lg {
  min-height: 48px;
  padding: 0 28px;
  font-size: 15px;
  border-radius: 14px;
}

.profile-btn-icon {
  width: 18px;
  height: 18px;
}

.profile-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.profile-submit-row {
  display: flex;
  justify-content: flex-end;
}

/* ── Dark Mode ── */

:root[data-theme='dark'] .profile-card {
  background: rgba(17, 24, 39, 0.72);
}

:root[data-theme='dark'] .profile-card::before {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.04), transparent 34%, transparent 66%, rgba(56, 189, 248, 0.04));
}

:root[data-theme='dark'] .profile-avatar-wrap {
  border-color: rgba(56, 189, 248, 0.25);
}

:root[data-theme='dark'] .profile-avatar-placeholder {
  color: #e2e8f0;
}

:root[data-theme='dark'] .profile-input {
  border-color: rgba(56, 189, 248, 0.16);
  background: rgba(17, 24, 39, 0.6);
}

:root[data-theme='dark'] .profile-input::placeholder {
  color: color-mix(in srgb, var(--text-soft) 78%, var(--bg));
}

:root[data-theme='dark'] .profile-input:hover {
  border-color: rgba(56, 189, 248, 0.28);
  background: rgba(20, 27, 42, 0.8);
}

:root[data-theme='dark'] .profile-input:focus {
  border-color: rgba(56, 189, 248, 0.52);
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.14);
}

:root[data-theme='dark'] .profile-btn {
  border-color: rgba(56, 189, 248, 0.22);
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.14), rgba(14, 165, 164, 0.08));
}

:root[data-theme='dark'] .profile-btn:hover:not(:disabled) {
  border-color: rgba(56, 189, 248, 0.38);
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(14, 165, 164, 0.14));
}

:root[data-theme='dark'] .profile-btn.primary {
  background: linear-gradient(135deg, #0ea5a4, rgba(94, 234, 212, 0.8));
  box-shadow: 0 8px 20px rgba(14, 165, 164, 0.3);
}

:root[data-theme='dark'] .profile-btn.secondary {
  background: rgba(20, 27, 42, 0.6);
}

:root[data-theme='dark'] .profile-auth-card {
  background: rgba(17, 24, 39, 0.72);
}

:root[data-theme='dark'] .profile-auth-card::before {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.04), transparent 34%, transparent 66%, rgba(56, 189, 248, 0.04));
}

/* ── Responsive ── */

@media (max-width: 768px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }

  .profile-avatar-card {
    justify-items: start;
    text-align: left;
  }

  .profile-avatar-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 640px) {
  .profile-main {
    padding: 16px 14px 48px;
  }

  .profile-card {
    padding: 18px;
    border-radius: 18px;
  }

  .profile-avatar-wrap {
    width: 90px;
    height: 90px;
  }

  .profile-avatar-placeholder {
    font-size: 30px;
  }

  .profile-submit-row {
    justify-content: stretch;
  }

  .profile-btn.lg {
    width: 100%;
  }

  .profile-auth-actions {
    flex-direction: column;
    width: 100%;
  }

  .profile-auth-actions .profile-btn {
    width: 100%;
  }
}
</style>
