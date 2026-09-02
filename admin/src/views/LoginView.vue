<template>
  <section class="login-wrap">
    <header class="topbar topbar-login">
      <div class="brand-block">
        <span class="brand-mark">MD</span>
        <div>
          <h1>{{ t('login.title') }}</h1>
        </div>
      </div>
      <div class="topbar-actions"></div>
    </header>

    <div class="login-stage">
      <aside class="login-hero">
        <div class="login-hero-visual" aria-hidden="true">
          <div class="login-hero-orb orb-a"></div>
          <div class="login-hero-orb orb-b"></div>
        </div>
        <h2>{{ t('login.heroTitle') }}</h2>
        <p class="login-hero-text">{{ t('login.heroDesc') }}</p>
        <div class="login-hero-points">
          <div class="login-hero-point">
            <strong>{{ t('login.feature1Title') }}</strong>
            <span>{{ t('login.feature1Desc') }}</span>
          </div>
          <div class="login-hero-point">
            <strong>{{ t('login.feature2Title') }}</strong>
            <span>{{ t('login.feature2Desc') }}</span>
          </div>
          <div class="login-hero-point">
            <strong>{{ t('login.feature3Title') }}</strong>
            <span>{{ t('login.feature3Desc') }}</span>
          </div>
        </div>
      </aside>

      <form class="login-card" @submit.prevent="submit">
        <div class="login-card-head">
          <h2>{{ t('login.cardTitle') }}</h2>
          <p class="login-card-subtitle">{{ t('login.cardSubtitle') }}</p>
        </div>

        <label class="login-field">
          <span>{{ t('login.username') }}</span>
          <input v-model="username" :placeholder="t('login.usernamePlaceholder')" autocomplete="username" />
        </label>

        <label class="login-field">
          <span>{{ t('login.password') }}</span>
          <div class="login-password-row">
            <input v-model="password" :type="showPassword ? 'text' : 'password'" :placeholder="t('login.passwordPlaceholder')" autocomplete="current-password" />
            <button
              type="button"
              class="login-password-toggle"
              :aria-label="showPassword ? t('login.hidePassword') : t('login.showPassword')"
              @mousedown.prevent="showPassword = true"
              @mouseup.prevent="showPassword = false"
              @mouseleave.prevent="showPassword = false"
              @touchstart.prevent="showPassword = true"
              @touchend.prevent="showPassword = false"
              @touchcancel.prevent="showPassword = false"
              @blur="showPassword = false"
            >
              <svg v-if="showPassword" class="login-password-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/>
              </svg>
              <svg v-else class="login-password-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M1.8 12s3.4-6.2 10.2-6.2S22.2 12 22.2 12s-3.4 6.2-10.2 6.2S1.8 12 1.8 12Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/>
                <path d="M4 20L20 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
        </label>

        <label class="login-field">
          <span>{{ t('login.captcha') }}</span>
          <div class="login-captcha-row">
            <input v-model="captchaAnswer" :placeholder="captchaQuestion || t('login.captchaPlaceholder')" />
            <button type="button" class="login-captcha-refresh" :aria-label="t('login.refreshCaptcha')" :title="t('login.refreshCaptcha')" @click="loadCaptcha">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4v5h5M20 20v-5h-5"/><path d="M20.49 9A9 9 0 0 0 5.64 5.64L4 4m16 16-1.64-1.64A9 9 0 0 1 3.51 15"/></svg>
            </button>
          </div>
        </label>

        <button type="submit" class="login-submit-btn" :disabled="loading">{{ loading ? t('login.loading') : t('login.submit') }}</button>
        <p v-if="errorMessage" class="error-message login-error">{{ errorMessage }}</p>
      </form>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import { adminApi, isLoggedIn } from '../api'
import { buildPageTitle } from '../site-meta'

const { t } = useI18n()
const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')
const showPassword = ref(false)
const captchaQuestion = ref('')
const captchaToken = ref('')
const captchaAnswer = ref('')

const applyTitle = () => {
  document.title = buildPageTitle(t('login.title'))
}

const loadCaptcha = async () => {
  try {
    const data = await adminApi.getCaptcha()
    captchaQuestion.value = data.question
    captchaToken.value = data.token
    captchaAnswer.value = ''
  } catch {
    captchaQuestion.value = t('login.captchaLoadFailed')
  }
}

const submit = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    await adminApi.login(username.value, password.value, captchaToken.value, captchaAnswer.value)
    await router.push('/')
  } catch (error) {
    const message = error instanceof Error ? error.message : t('login.loginFailed')
    if (message.includes('用户名或密码错误')) {
      errorMessage.value = t('login.wrongCredentialsHint')
    } else if (message.includes('仅系统管理员和内容作者可登录后台')) {
      errorMessage.value = t('login.noPermissionHint')
    } else if (message.includes('验证码')) {
      errorMessage.value = message
      await loadCaptcha()
    } else {
      errorMessage.value = message || t('login.loginFailed')
    }
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  applyTitle()
  await loadCaptcha()

  if (!isLoggedIn()) {
    return
  }
  try {
    await adminApi.getMe()
    await router.replace('/')
  } catch {
    document.cookie = 'admin_logged_in=; path=/; max-age=0'
  }
})
</script>

<style scoped>
.login-captcha-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
  align-items: center;
}

.login-captcha-refresh {
  border: 1px solid var(--line);
  background: var(--bg-soft);
  color: var(--text);
  border-radius: 10px;
  width: 36px;
  height: 36px;
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: color 0.18s ease, border-color 0.18s ease;
}

.login-captcha-refresh:hover {
  color: var(--accent);
  border-color: var(--accent);
}
</style>
