<template>
  <div class="shell auth-page">
    <WebTopbar
      :title="t(mode === 'login' ? 'login.title' : 'register.title')"
      :subtitle="t(mode === 'login' ? 'login.subtitle' : 'register.subtitle')"
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
        <h2>{{ t(mode === 'login' ? 'login.heroTitle' : 'register.heroTitle') }}</h2>
        <p>{{ t(mode === 'login' ? 'login.heroDesc' : 'register.heroDesc') }}</p>
      </section>

      <section class="auth-card">
        <div class="auth-tabs">
          <button
            type="button"
            class="auth-tab"
            :class="{ active: mode === 'login' }"
            @click="switchMode('login')"
          >{{ t('login.loginTitle') }}</button>
          <button
            type="button"
            class="auth-tab"
            :class="{ active: mode === 'register' }"
            @click="switchMode('register')"
          >{{ t('register.registerTitle') }}</button>
        </div>

        <div class="auth-field-group">
          <label class="auth-input-shell">
            <span class="auth-input-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </span>
            <input v-model="username" autocomplete="username" :placeholder="t(mode === 'login' ? 'login.usernamePlaceholder' : 'register.usernamePlaceholder')" />
          </label>

          <template v-if="mode === 'register'">
            <label class="auth-input-shell">
              <span class="auth-input-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
              </span>
              <input v-model="nickname" autocomplete="nickname" :placeholder="t('register.nicknamePlaceholder')" />
            </label>
            <label class="auth-input-shell">
              <span class="auth-input-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
              </span>
              <input v-model="email" autocomplete="email" type="email" :placeholder="t('register.emailPlaceholder')" />
            </label>
          </template>

          <label class="auth-input-shell auth-password-shell">
            <span class="auth-input-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </span>
            <input :type="showPassword ? 'text' : 'password'" v-model="password" :autocomplete="mode === 'login' ? 'current-password' : 'new-password'" :placeholder="t(mode === 'login' ? 'login.passwordPlaceholder' : 'register.passwordPlaceholder')" @keyup.enter="submit" />
            <button type="button" class="auth-password-toggle" :aria-label="showPassword ? t(mode === 'login' ? 'login.hidePassword' : 'register.hidePassword') : t(mode === 'login' ? 'login.showPassword' : 'register.showPassword')" :title="showPassword ? t(mode === 'login' ? 'login.hidePassword' : 'register.hidePassword') : t(mode === 'login' ? 'login.showPassword' : 'register.showPassword')" @click="showPassword = !showPassword">
              <svg v-if="showPassword" class="auth-password-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M3.53 2.47 2.47 3.53l3.06 3.06C3.44 8.3 1.94 10.16 1 12c1.86 3.62 5.75 8 11 8 1.61 0 3.15-.32 4.57-.89l3.9 3.9 1.06-1.06-18-18Zm7.04 9.16 1.8 1.8a2.5 2.5 0 0 1-3.57-3.57l1.77 1.77ZM12 6c4.41 0 8.3 4.38 10 6-1.07 2.09-2.73 4.22-4.78 5.74l-2.05-2.05a4 4 0 0 0-5.61-5.61L7.51 7.51A10.16 10.16 0 0 1 12 6Zm0 12c-4.09 0-7.38-3.1-9.08-6 1.08-1.88 2.6-3.68 4.4-5.01l1.52 1.52a8 8 0 0 0 6.98 6.98l1.52 1.52C15.08 17.52 13.62 18 12 18Z" fill="currentColor"/>
              </svg>
              <svg v-else class="auth-password-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 5c-5.25 0-9.14 4.38-11 7 1.86 2.62 5.75 7 11 7s9.14-4.38 11-7c-1.86-2.62-5.75-7-11-7Zm0 12c-4.09 0-7.38-3.1-9.08-5 1.7-1.9 5-5 9.08-5s7.38 3.1 9.08 5c-1.7 1.9-5 5-9.08 5Zm0-8a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z" fill="currentColor"/>
              </svg>
            </button>
          </label>

          <label v-if="mode === 'login'" class="auth-remember-row">
            <input v-model="rememberMe" type="checkbox" />
            <span>{{ t('login.rememberMe') }}</span>
          </label>

          <label class="auth-input-shell auth-password-shell">
            <span class="auth-input-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </span>
            <input v-model="captchaAnswer" :placeholder="captchaQuestion || t(mode === 'login' ? 'login.captchaPlaceholder' : 'register.captchaPlaceholder')" />
            <button type="button" class="auth-password-toggle" :aria-label="t(mode === 'login' ? 'login.refreshCaptcha' : 'register.refreshCaptcha')" :title="t(mode === 'login' ? 'login.refreshCaptcha' : 'register.refreshCaptcha')" @click="loadCaptcha">
              <svg viewBox="0 0 24 24" class="auth-password-icon" aria-hidden="true"><path d="M4 4v5h5M20 20v-5h-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M20.49 9A9 9 0 0 0 5.64 5.64L4 4m16 16-1.64-1.64A9 9 0 0 1 3.51 15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
          </label>

          <p v-if="mode === 'register'" class="auth-field-hint">{{ t('register.autoLoginHint') }}</p>
        </div>

        <button class="auth-submit-btn" :disabled="submitting" @click="submit">
          {{ submitting ? t(mode === 'login' ? 'login.loading' : 'register.loading') : t(mode === 'login' ? 'login.submit' : 'register.submit') }}
        </button>

        <p v-if="message" class="auth-message" :class="status === 'error' ? 'error-message' : 'success-message'">{{ message }}</p>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { API_BASE, toAbsoluteAssetUrl, webApi } from '../api'
import WebTopbar from '../components/WebTopbar.vue'
import { applySiteMetaFromSetting, buildPageTitle, setSiteSetting } from '../site-meta'
import type { NavItem } from '../types'
import { useTheme } from '../composables/useTheme'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const { theme, toggleTheme, initTheme, listenThemeChange, destroyTheme } = useTheme()

const mode = ref<'login' | 'register'>('login')
const username = ref('')
const nickname = ref('')
const email = ref('')
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
])

const switchMode = (m: 'login' | 'register') => {
  if (mode.value === m) return
  mode.value = m
  message.value = ''
  status.value = ''
  password.value = ''
  captchaAnswer.value = ''
  loadCaptcha()
  router.replace({ name: m })
}

watch(() => route.name, (name) => {
  if (name === 'login' || name === 'register') {
    mode.value = name
  }
})

const loadCaptcha = async () => {
  try {
    const res = await fetch(`${API_BASE}/web/captcha`, { credentials: 'include' })
    const data = await res.json() as { question: string; token: string }
    captchaQuestion.value = data.question
    captchaToken.value = data.token
    captchaAnswer.value = ''
  } catch {
    captchaQuestion.value = t(mode.value === 'login' ? 'login.captchaLoadFailed' : 'register.captchaLoadFailed')
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
    if (mode.value === 'login') {
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
      const returnUrl = localStorage.getItem('md-login-return')
      localStorage.removeItem('md-login-return')
      setTimeout(() => { router.push(returnUrl || '/') }, 500)
    } else {
      await webApi.registerReader({
        username: username.value.trim(),
        nickname: nickname.value.trim(),
        email: email.value.trim(),
        password: password.value,
        captcha_token: captchaToken.value,
        captcha_answer: captchaAnswer.value,
      })
      await webApi.loginReader({
        username: username.value.trim(),
        password: password.value,
        captcha_token: captchaToken.value,
        captcha_answer: captchaAnswer.value,
      })
      status.value = 'success'
      message.value = t('register.registerSuccess')
      const displayName = nickname.value.trim() || username.value.trim()
      localStorage.setItem('md-welcome-once', t('register.welcome', { name: displayName }))
      localStorage.setItem('md-reader-nickname', displayName)
      localStorage.setItem('md-reader-email', email.value.trim())
      username.value = ''
      nickname.value = ''
      email.value = ''
      password.value = ''
      const returnUrl = localStorage.getItem('md-login-return')
      localStorage.removeItem('md-login-return')
      setTimeout(() => { router.push(returnUrl || '/') }, 500)
    }
  } catch (error) {
    status.value = 'error'
    if (mode.value === 'login') {
      message.value = error instanceof Error ? error.message : t('login.loginFailed')
    } else {
      message.value = error instanceof Error ? error.message : t('register.registerFailed')
      await loadCaptcha()
    }
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  initTheme()
  listenThemeChange()

  if (route.name === 'register') {
    mode.value = 'register'
  }

  const savedUsername = localStorage.getItem('md-login-username')
  if (savedUsername && mode.value === 'login') {
    username.value = savedUsername
  }

  document.title = buildPageTitle(t(mode.value === 'login' ? 'login.title' : 'register.title'))
  await Promise.all([loadSiteLogo(), loadCaptcha()])
})

onBeforeUnmount(() => {
  destroyTheme()
})
</script>

<style scoped>
.auth-tabs {
  display: flex;
  background: var(--bg-soft);
  border-radius: 12px;
  padding: 4px;
  gap: 4px;
}

.auth-tab {
  flex: 1;
  padding: 10px 0;
  border: none;
  background: transparent;
  color: var(--text-soft);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  position: relative;
  border-radius: 10px;
  transition: color 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.auth-tab:hover:not(.active) {
  color: var(--text);
  background: rgba(148, 163, 184, 0.1);
}

.auth-tab.active {
  color: var(--accent);
  background: var(--bg-panel);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.auth-field-group {
  gap: 12px;
}

.auth-submit-btn {
  margin-top: 4px;
  font-size: 15px;
  letter-spacing: 0.02em;
}

.auth-submit-btn:active:not(:disabled) {
  transform: scale(0.98);
}

:root[data-theme='dark'] .auth-tab.active {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}
</style>
