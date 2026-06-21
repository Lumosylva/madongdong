<template>
  <div class="shell auth-page">
    <WebTopbar
      :title="t('login.title')"
      :subtitle="t('login.subtitle')"
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
        <p class="auth-eyebrow">Reader Portal</p>
        <h2>{{ t('login.heroTitle') }}</h2>
        <p>{{ t('login.heroDesc') }}</p>
      </section>

      <section class="auth-card">
        <div class="auth-card-header">
          <h3>{{ t('login.loginTitle') }}</h3>
          <p>{{ t('login.loginSubtitle') }}</p>
        </div>

        <div class="auth-field-group">
          <label class="auth-input-shell">
            <span class="auth-input-icon" aria-hidden="true">馃懁</span>
            <input v-model="username" autocomplete="username" :placeholder="t('login.usernamePlaceholder')" />
          </label>
          <label class="auth-input-shell auth-password-shell">
            <span class="auth-input-icon" aria-hidden="true">馃敀</span>
            <input :type="showPassword ? 'text' : 'password'" v-model="password" autocomplete="current-password" :placeholder="t('login.passwordPlaceholder')" @keyup.enter="submit" />
            <button type="button" class="auth-password-toggle" :aria-label="showPassword ? t('login.hidePassword') : t('login.showPassword')" :title="showPassword ? t('login.hidePassword') : t('login.showPassword')" @click="showPassword = !showPassword">
              <svg v-if="showPassword" class="auth-password-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M3.53 2.47 2.47 3.53l3.06 3.06C3.44 8.3 1.94 10.16 1 12c1.86 3.62 5.75 8 11 8 1.61 0 3.15-.32 4.57-.89l3.9 3.9 1.06-1.06-18-18Zm7.04 9.16 1.8 1.8a2.5 2.5 0 0 1-3.57-3.57l1.77 1.77ZM12 6c4.41 0 8.3 4.38 10 6-1.07 2.09-2.73 4.22-4.78 5.74l-2.05-2.05a4 4 0 0 0-5.61-5.61L7.51 7.51A10.16 10.16 0 0 1 12 6Zm0 12c-4.09 0-7.38-3.1-9.08-6 1.08-1.88 2.6-3.68 4.4-5.01l1.52 1.52a8 8 0 0 0 6.98 6.98l1.52 1.52C15.08 17.52 13.62 18 12 18Z" fill="currentColor"/>
              </svg>
              <svg v-else class="auth-password-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 5c-5.25 0-9.14 4.38-11 7 1.86 2.62 5.75 7 11 7s9.14-4.38 11-7c-1.86-2.62-5.75-7-11-7Zm0 12c-4.09 0-7.38-3.1-9.08-5 1.7-1.9 5-5 9.08-5s7.38 3.1 9.08 5c-1.7 1.9-5 5-9.08 5Zm0-8a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z" fill="currentColor"/>
              </svg>
            </button>
          </label>
          <label class="auth-remember-row">
            <input v-model="rememberMe" type="checkbox" />
            <span>{{ t('login.rememberMe') }}</span>
          </label>
          <label class="auth-input-shell auth-password-shell">
            <span class="auth-input-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </span>
            <input v-model="captchaAnswer" :placeholder="captchaQuestion || t('login.captchaPlaceholder')" />
            <button type="button" class="auth-password-toggle" :aria-label="t('login.refreshCaptcha')" :title="t('login.refreshCaptcha')" @click="loadCaptcha">
              <svg viewBox="0 0 24 24" class="auth-password-icon" aria-hidden="true"><path d="M4 4v5h5M20 20v-5h-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M20.49 9A9 9 0 0 0 5.64 5.64L4 4m16 16-1.64-1.64A9 9 0 0 1 3.51 15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
          </label>
        </div>

        <button class="auth-submit-btn" :disabled="submitting" @click="submit">
          {{ submitting ? t('login.loading') : t('login.submit') }}
        </button>

        <p class="auth-switch-link">
          {{ t('login.noAccount') }}<RouterLink to="/register">{{ t('login.registerLink') }}</RouterLink>
        </p>
        <p v-if="message" class="auth-message" :class="status === 'error' ? 'error-message' : 'success-message'">{{ message }}</p>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { toAbsoluteAssetUrl, webApi } from '../api'
import WebTopbar from '../components/WebTopbar.vue'
import { applySiteMetaFromSetting, buildPageTitle, setSiteSetting } from '../site-meta'
import type { NavItem } from '../types'
import { useTheme } from '../composables/useTheme'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const { theme, toggleTheme, initTheme, listenThemeChange, destroyTheme } = useTheme()
const username = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberMe = ref(true)
const submitting = ref(false)
const message = ref('')
const status = ref<'success' | 'error' | ''>('')
const siteLogoUrl = ref('')
const captchaQuestion = ref('')
const captchaToken = ref('')
const captchaAnswer = ref('')
const authNavItems = computed<NavItem[]>(() => [
  { id: 1, title: t('common.home'), path: '/', sort_order: 1, is_visible: true, target: null, description: null },
  { id: 2, title: t('common.login'), path: '/login', sort_order: 2, is_visible: true, target: null, description: null },
  { id: 3, title: t('common.register'), path: '/register', sort_order: 3, is_visible: true, target: null, description: null },
])

const loadCaptcha = async () => {
  try {
    const res = await fetch(`${(import.meta.env.VITE_API_BASE as string || '/api/v1')}/web/captcha`, { credentials: 'include' })
    const data = await res.json() as { question: string; token: string }
    captchaQuestion.value = data.question
    captchaToken.value = data.token
    captchaAnswer.value = ''
  } catch {
    captchaQuestion.value = t('login.captchaLoadFailed')
  }
}

const loadSiteLogo = async () => {
  try {
    const home = await webApi.getHome(1, 1)
    siteLogoUrl.value = toAbsoluteAssetUrl(home.site.site_logo)
    setSiteSetting(home.site)
    applySiteMetaFromSetting(home.site)
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
    await webApi.loginReader({
      username: username.value.trim(),
      password: password.value,
      captcha_token: captchaToken.value,
      captcha_answer: captchaAnswer.value,
    })
    if (rememberMe.value) {
      localStorage.setItem('md-login-username', username.value.trim())
    } else {
      localStorage.removeItem('md-login-username')
    }
    const savedNickname = localStorage.getItem('md-reader-nickname')
    const displayName = savedNickname || username.value.trim()
    localStorage.setItem('md-reader-nickname', displayName)
    localStorage.setItem('md-welcome-once', t('login.welcomeBack', { name: displayName }))
    localStorage.removeItem('md-home-welcome-shown')
    status.value = 'success'
    message.value = t('login.loginSuccess')
    setTimeout(() => {
      router.push('/')
    }, 500)
  } catch (error) {
    status.value = 'error'
    message.value = error instanceof Error ? error.message : t('login.loginFailed')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  initTheme()
  listenThemeChange()
  const savedUsername = localStorage.getItem('md-login-username')
  if (savedUsername) {
    username.value = savedUsername
    rememberMe.value = true
  }
  document.title = buildPageTitle(t('login.title'))
  await Promise.all([loadSiteLogo(), loadCaptcha()])
})

onBeforeUnmount(() => {
  destroyTheme()
})
</script>
