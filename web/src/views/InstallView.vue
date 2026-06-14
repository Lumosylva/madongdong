<template>
  <div class="install-page">
    <section class="install-shell">
      <aside class="install-hero">
        <div class="install-brand">
          <span class="install-brand-mark">MD</span>
          <div>
            <p class="install-eyebrow">Welcome</p>
            <h1>{{ t('install.welcome') }}</h1>
          </div>
        </div>

        <p class="install-lead">
          {{ t('install.description') }}
        </p>

        <div class="install-steps">
          <div class="install-step" :class="{ active: currentStep >= 1, done: currentStep > 1 }">
            <div class="install-step-num">1</div>
            <div>
              <p class="install-step-title">{{ t('install.step1Title') }}</p>
              <p class="install-step-desc">{{ t('install.step1Desc') }}</p>
            </div>
          </div>
          <div class="install-step" :class="{ active: currentStep >= 2, done: currentStep > 2 }">
            <div class="install-step-num">2</div>
            <div>
              <p class="install-step-title">{{ t('install.step2Title') }}</p>
              <p class="install-step-desc">{{ t('install.step2Desc') }}</p>
            </div>
          </div>
          <div class="install-step" :class="{ active: currentStep >= 3 }">
            <div class="install-step-num">3</div>
            <div>
              <p class="install-step-title">{{ t('install.step3Title') }}</p>
              <p class="install-step-desc">{{ t('install.step3Desc') }}</p>
            </div>
          </div>
        </div>

        <div class="install-tip-card">
          <div class="install-tip-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="16" x2="12" y2="12"/>
              <line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>
          </div>
          <div>
            <strong>{{ t('install.beforeStart') }}</strong>
            <p>{{ t('install.beforeStartDesc') }}</p>
          </div>
        </div>
      </aside>

      <div class="install-card">
        <div class="install-card-header">
          <div>
            <p class="install-card-kicker">Step {{ currentStep }} / 3</p>
            <h2>{{ stepTitles[currentStep - 1] }}</h2>
          </div>
          <p class="install-card-subtitle">{{ stepSubtitles[currentStep - 1] }}</p>
        </div>

        <form class="install-form" @submit.prevent="submitInstall">
          <!-- Step 1: Site Info -->
          <div v-show="currentStep === 1" class="install-step-content">
            <div class="install-grid">
              <label class="install-field">
                <span class="install-field-label">{{ t('install.siteTitle') }} <em>*</em></span>
                <input v-model="form.site_title" required :placeholder="t('install.siteTitlePlaceholder')" />
              </label>
              <label class="install-field">
                <span class="install-field-label">{{ t('install.siteSubtitle') }}</span>
                <input v-model="form.site_subtitle" :placeholder="t('install.siteSubtitlePlaceholder')" />
              </label>
              <label class="install-field install-field-wide">
                <span class="install-field-label">{{ t('install.siteDomain') }}</span>
                <div class="install-field-row">
                  <input v-model="form.site_domain" :placeholder="t('install.siteDomainPlaceholder')" />
                  <button type="button" class="install-field-btn" :title="t('install.autoDetect')" @click="autoDetectDomain">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
                  </button>
                </div>
                <p class="install-field-hint">{{ t('install.siteDomainHint') }}</p>
              </label>
              <label class="install-field install-field-wide">
                <span class="install-field-label">{{ t('install.jwtSecret') }}</span>
                <div class="install-field-row">
                  <input v-model="form.secret_key" :type="showSecretKey ? 'text' : 'password'" :placeholder="t('install.jwtSecretPlaceholder')" />
                  <button type="button" class="install-field-btn" :title="showSecretKey ? t('install.hide') : t('install.show')" @click="showSecretKey = !showSecretKey">
                    <svg v-if="showSecretKey" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3.53 2.47 2.47 3.53l3.06 3.06C3.44 8.3 1.94 10.16 1 12c1.86 3.62 5.75 8 11 8 1.61 0 3.15-.32 4.57-.89l3.9 3.9 1.06-1.06-18-18Zm7.04 9.16 1.8 1.8a2.5 2.5 0 0 1-3.57-3.57l1.77 1.77ZM12 6c4.41 0 8.3 4.38 10 6-1.07 2.09-2.73 4.22-4.78 5.74l-2.05-2.05a4 4 0 0 0-5.61-5.61L7.51 7.51A10.16 10.16 0 0 1 12 6Zm0 12c-4.09 0-7.38-3.1-9.08-6 1.08-1.88 2.6-3.68 4.4-5.01l1.52 1.52a8 8 0 0 0 6.98 6.98l1.52 1.52C15.08 17.52 13.62 18 12 18Z" fill="currentColor"/></svg>
                    <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5c-5.25 0-9.14 4.38-11 7 1.86 2.62 5.75 7 11 7s9.14-4.38 11-7c-1.86-2.62-5.75-7-11-7Zm0 12c-4.09 0-7.38-3.1-9.08-5 1.7-1.9 5-5 9.08-5s7.38 3.1 9.08 5c-1.7 1.9-5 5-9.08 5Zm0-8a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z" fill="currentColor"/></svg>
                  </button>
                  <button type="button" class="install-field-btn" :title="t('install.generateKey')" @click="generateSecretKey">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4v5h5M20 20v-5h-5"/><path d="M20.49 9A9 9 0 0 0 5.64 5.64L4 4m16 16-1.64-1.64A9 9 0 0 1 3.51 15"/></svg>
                  </button>
                </div>
                <p class="install-field-hint">{{ t('install.jwtSecretHint') }}</p>
              </label>
              <label class="install-field install-field-wide">
                <span class="install-field-label">{{ t('install.databaseUrl') }}</span>
                <input v-model="form.database_url" placeholder="sqlite+aiosqlite:///./madongdong.db" />
                <p class="install-field-hint">{{ t('install.databaseUrlHint') }}</p>
              </label>
              <label class="install-field">
                <span class="install-field-label">{{ t('install.pageSize') }}</span>
                <input v-model.number="form.homepage_page_size" type="number" min="1" max="100" />
              </label>
            </div>
          </div>

          <!-- Step 2: Admin Account -->
          <div v-show="currentStep === 2" class="install-step-content">
            <div class="install-grid">
              <label class="install-field">
                <span class="install-field-label">{{ t('install.adminUsername') }} <em>*</em></span>
                <input v-model="form.admin_username" required :placeholder="t('install.adminUsernamePlaceholder')" autocomplete="username" />
              </label>
              <label class="install-field">
                <span class="install-field-label">{{ t('install.adminPassword') }} <em>*</em></span>
                <div class="install-password-shell">
                  <input :type="showPassword ? 'text' : 'password'" v-model="form.admin_password" required :placeholder="t('install.adminPasswordPlaceholder')" autocomplete="new-password" />
                  <button type="button" class="install-password-toggle" :aria-label="showPassword ? t('install.hidePassword') : t('install.showPassword')" @click="showPassword = !showPassword">
                    <svg v-if="showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M3.53 2.47 2.47 3.53l3.06 3.06C3.44 8.3 1.94 10.16 1 12c1.86 3.62 5.75 8 11 8 1.61 0 3.15-.32 4.57-.89l3.9 3.9 1.06-1.06-18-18Zm7.04 9.16 1.8 1.8a2.5 2.5 0 0 1-3.57-3.57l1.77 1.77ZM12 6c4.41 0 8.3 4.38 10 6-1.07 2.09-2.73 4.22-4.78 5.74l-2.05-2.05a4 4 0 0 0-5.61-5.61L7.51 7.51A10.16 10.16 0 0 1 12 6Zm0 12c-4.09 0-7.38-3.1-9.08-6 1.08-1.88 2.6-3.68 4.4-5.01l1.52 1.52a8 8 0 0 0 6.98 6.98l1.52 1.52C15.08 17.52 13.62 18 12 18Z" fill="currentColor"/>
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M12 5c-5.25 0-9.14 4.38-11 7 1.86 2.62 5.75 7 11 7s9.14-4.38 11-7c-1.86-2.62-5.75-7-11-7Zm0 12c-4.09 0-7.38-3.1-9.08-5 1.7-1.9 5-5 9.08-5s7.38 3.1 9.08 5c-1.7 1.9-5 5-9.08 5Zm0-8a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z" fill="currentColor"/>
                    </svg>
                  </button>
                </div>
              </label>
              <label class="install-field">
                <span class="install-field-label">{{ t('install.adminNickname') }} <em>*</em></span>
                <input v-model="form.admin_nickname" required :placeholder="t('install.adminNicknamePlaceholder')" />
              </label>
              <label class="install-field">
                <span class="install-field-label">{{ t('install.adminEmail') }} <em>*</em></span>
                <input v-model="form.admin_email" type="email" required :placeholder="t('install.adminEmailPlaceholder')" autocomplete="email" />
              </label>
            </div>
          </div>

          <!-- Step 3: Advanced Options -->
          <div v-show="currentStep === 3" class="install-step-content">
            <div class="install-grid">
              <label class="install-field install-field-wide">
                <span class="install-field-label">{{ t('install.icpBeian') }}</span>
                <textarea v-model="form.icp_beian" rows="3" :placeholder="t('install.icpBeianPlaceholder')"></textarea>
              </label>
              <label class="install-field">
                <span class="install-field-label">{{ t('install.copyright') }}</span>
                <input v-model="form.copyright_text" :placeholder="t('install.copyrightPlaceholder')" />
              </label>
              <label class="install-checkbox-card">
                <input v-model="form.comment_requires_review" type="checkbox" class="install-checkbox-input" />
                <div class="install-checkbox-box">
                  <svg class="install-checkbox-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                </div>
                <div>
                  <span>{{ t('install.commentReview') }}</span>
                  <p>{{ t('install.commentReviewDesc') }}</p>
                </div>
              </label>
            </div>

            <div class="install-note">
              <div class="install-note-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10 9 9 9 8 9"/>
                </svg>
              </div>
              <div>
                <strong>{{ t('install.footerNote') }}</strong>
                <p>{{ t('install.footerNoteDesc') }}</p>
              </div>
            </div>
          </div>

          <div class="install-feedback">
            <p v-if="errorMessage" class="install-message error">{{ errorMessage }}</p>
            <p v-if="successMessage" class="install-message success">{{ successMessage }}</p>
          </div>

          <div class="install-actions">
            <button v-if="currentStep > 1" type="button" class="install-btn-secondary" @click="currentStep--">
              {{ t('install.prevStep') }}
            </button>
            <div class="install-actions-right">
              <button v-if="currentStep < 3" type="button" class="install-btn-primary" @click="currentStep++">
                {{ t('install.nextStep') }}
              </button>
              <button v-else type="submit" class="install-btn-primary install-btn-submit" :disabled="submitting">
                <svg v-if="submitting" class="install-spinner" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="31.4 31.4" stroke-linecap="round"/>
                </svg>
                <span>{{ submitting ? t('install.initializing') : t('install.confirmInstall') }}</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { webApi } from '../api'
import { buildPageTitle } from '../site-meta'

const currentStep = ref(1)
const showPassword = ref(false)
const showSecretKey = ref(false)
const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const { t } = useI18n()

const stepTitles = computed(() => [t('install.step1Title'), t('install.step2Title'), t('install.step3Title')])
const stepSubtitles = computed(() => [t('install.step1Desc'), t('install.step2Desc'), t('install.step3Desc')])

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
  site_domain: '',
  secret_key: '',
  database_url: 'sqlite+aiosqlite:///./madongdong.db',
})

const getAdminLoginUrl = () => {
  const adminBasePath = (import.meta.env.VITE_ADMIN_BASE_PATH as string | undefined)?.trim() || '/admin'
  const normalized = adminBasePath.startsWith('/') ? adminBasePath : `/${adminBasePath}`
  return `${normalized.replace(/\/$/, '')}/login`
}

const autoDetectDomain = () => {
  form.site_domain = window.location.hostname
}

const generateSecretKey = async () => {
  try {
    const res = await fetch(`${(import.meta.env.VITE_API_BASE as string || '/api/v1')}/install/secret-key`)
    const data = await res.json() as { secret_key: string }
    form.secret_key = data.secret_key
    showSecretKey.value = true
  } catch {
    const array = new Uint8Array(48)
    crypto.getRandomValues(array)
    form.secret_key = btoa(String.fromCharCode(...array)).replace(/[^a-zA-Z0-9]/g, '').slice(0, 64)
    showSecretKey.value = true
  }
}

const checkInstalled = async () => {
  try {
    const res = await webApi.getInstallStatus()
    if (res.data.installed) {
      window.location.assign(getAdminLoginUrl())
    }
  } catch {
    errorMessage.value = t('install.statusCheckFailed')
  }
}

const submitInstall = async () => {
  submitting.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    await webApi.installSite({ ...form })
    successMessage.value = t('install.installSuccess')
    window.setTimeout(() => {
      window.location.assign(getAdminLoginUrl())
    }, 900)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : t('install.installFailed')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  document.title = buildPageTitle(t('install.title'))
  void checkInstalled()
})
</script>

<style scoped>
.install-page {
  min-height: 100vh;
  padding: 28px 16px 40px;
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at top left, rgba(14, 165, 164, 0.12), transparent 28%),
    radial-gradient(circle at top right, rgba(234, 154, 24, 0.1), transparent 24%),
    linear-gradient(180deg, #f8fbff 0%, #edf3f9 100%);
}

:global([data-theme='dark']) .install-page {
  background:
    radial-gradient(circle at top left, rgba(94, 234, 212, 0.12), transparent 30%),
    radial-gradient(circle at top right, rgba(245, 158, 11, 0.08), transparent 26%),
    linear-gradient(180deg, #020814 0%, #07111f 100%);
}

.install-shell {
  width: min(1180px, 100%);
  display: grid;
  grid-template-columns: 1.05fr 1.35fr;
  gap: 22px;
  align-items: stretch;
}

.install-hero,
.install-card {
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(18px);
  box-shadow: var(--shadow);
  border-radius: 24px;
}

:global([data-theme='dark']) .install-hero,
:global([data-theme='dark']) .install-card {
  background: rgba(10, 24, 44, 0.8);
}

.install-hero {
  padding: 28px;
  display: grid;
  gap: 22px;
  align-content: start;
}

.install-brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.install-brand-mark {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  font-weight: 800;
  letter-spacing: 0.1em;
  color: #05131d;
  background: linear-gradient(135deg, var(--accent), #93c5fd);
}

.install-eyebrow {
  margin: 0 0 6px;
  color: var(--text-soft);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
}

.install-hero h1,
.install-card h2 {
  margin: 0;
  line-height: 1.15;
}

.install-hero h1 {
  font-size: clamp(30px, 3vw, 40px);
}

.install-lead {
  margin: 0;
  color: var(--text-soft);
  line-height: 1.8;
  font-size: 15px;
}

.install-steps {
  display: grid;
  gap: 14px;
}

.install-step {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding: 12px 14px;
  border-radius: 14px;
  transition: background 0.2s ease, border-color 0.2s ease;
  border: 1px solid transparent;
}

.install-step.active {
  background: rgba(14, 165, 164, 0.06);
  border-color: rgba(14, 165, 164, 0.16);
}

.install-step.done .install-step-num {
  background: var(--accent);
  color: #fff;
}

.install-step-num {
  width: 28px;
  height: 28px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-size: 13px;
  font-weight: 700;
  flex: 0 0 auto;
  background: var(--bg-soft);
  color: var(--text-soft);
  border: 1px solid var(--line);
  transition: background 0.2s ease, color 0.2s ease;
}

.install-step.active .install-step-num {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}

.install-step-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.install-step-desc {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--text-soft);
}

.install-tip-card {
  padding: 16px 18px;
  border-radius: 18px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.5);
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

:global([data-theme='dark']) .install-tip-card {
  background: rgba(255, 255, 255, 0.03);
}

.install-tip-icon {
  width: 20px;
  height: 20px;
  flex: 0 0 auto;
  margin-top: 1px;
  color: var(--accent);
}

.install-tip-icon svg {
  width: 100%;
  height: 100%;
}

.install-tip-card strong {
  display: block;
  margin-bottom: 4px;
}

.install-tip-card p {
  margin: 0;
  color: var(--text-soft);
  line-height: 1.7;
}

.install-card {
  padding: 28px;
}

.install-card-header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: end;
  margin-bottom: 24px;
}

.install-card-kicker {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-soft);
}

.install-card h2 {
  font-size: 24px;
}

.install-card-subtitle {
  margin: 0;
  max-width: 360px;
  color: var(--text-soft);
  line-height: 1.65;
  font-size: 13px;
}

.install-form {
  display: grid;
  gap: 18px;
}

.install-step-content {
  display: grid;
  gap: 16px;
}

.install-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.install-field {
  display: grid;
  gap: 6px;
  padding: 14px 14px 12px;
  border: 1px solid var(--line);
  background: var(--bg-panel);
  border-radius: 18px;
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
  cursor: text;
}

.install-field:focus-within {
  border-color: rgba(14, 165, 164, 0.35);
  box-shadow: 0 0 0 4px rgba(14, 165, 164, 0.12);
}

.install-field-wide {
  grid-column: 1 / -1;
}

.install-field-label {
  font-size: 13px;
  color: var(--text-soft);
}

.install-field-label em {
  font-style: normal;
  color: var(--accent);
}

.install-field input,
.install-field textarea {
  width: 100%;
  border: 1px solid transparent;
  background: rgba(255, 255, 255, 0.88);
  border-radius: 12px;
  padding: 10px 14px;
  color: var(--text);
  outline: none;
  font: inherit;
  resize: vertical;
}

:global([data-theme='dark']) .install-field input,
:global([data-theme='dark']) .install-field textarea {
  background: rgba(255, 255, 255, 0.06);
}

.install-field-hint {
  margin: 0;
  color: var(--text-soft);
  font-size: 11px;
  line-height: 1.5;
}

.install-field-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 6px;
  align-items: center;
}

.install-field-btn {
  border: 1px solid var(--line);
  background: var(--bg-soft);
  color: var(--text-soft);
  border-radius: 8px;
  width: 32px;
  height: 32px;
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: color 0.18s ease, border-color 0.18s ease;
  flex: 0 0 auto;
}

.install-field-btn:hover {
  color: var(--accent);
  border-color: var(--accent);
}

.install-field input:focus,
.install-field textarea:focus {
  border-color: rgba(14, 165, 164, 0.35);
  box-shadow: 0 0 0 3px rgba(14, 165, 164, 0.12);
}

.install-password-shell {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 8px;
}

.install-password-shell input {
  padding-right: 0;
}

.install-password-toggle {
  border: none;
  background: transparent;
  color: var(--accent);
  cursor: pointer;
  padding: 0;
  width: 22px;
  height: 22px;
  display: grid;
  place-items: center;
}

.install-password-toggle svg {
  width: 18px;
  height: 18px;
}

.install-checkbox-card {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 12px;
  padding: 14px 14px 12px;
  border: 1px solid var(--line);
  background: var(--bg-panel);
  border-radius: 18px;
  cursor: pointer;
  transition: border-color 0.18s ease;
}

.install-checkbox-card:hover {
  border-color: rgba(14, 165, 164, 0.28);
}

.install-checkbox-input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.install-checkbox-box {
  width: 20px;
  height: 20px;
  border-radius: 6px;
  border: 2px solid var(--line);
  display: grid;
  place-items: center;
  transition: background 0.18s ease, border-color 0.18s ease;
  flex: 0 0 auto;
}

.install-checkbox-input:checked + .install-checkbox-box {
  background: var(--accent);
  border-color: var(--accent);
}

.install-checkbox-icon {
  width: 12px;
  height: 12px;
  color: #fff;
  opacity: 0;
  transform: scale(0.5);
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.install-checkbox-input:checked + .install-checkbox-box .install-checkbox-icon {
  opacity: 1;
  transform: scale(1);
}

.install-checkbox-card > div:last-child span {
  font-size: 14px;
  color: var(--text);
  font-weight: 500;
}

.install-checkbox-card > div:last-child p {
  margin: 2px 0 0;
  color: var(--text-soft);
  line-height: 1.6;
  font-size: 12px;
}

.install-note {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(14, 165, 164, 0.04);
  border: 1px solid rgba(14, 165, 164, 0.12);
}

.install-note-icon {
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
  margin-top: 2px;
  color: var(--accent);
}

.install-note-icon svg {
  width: 100%;
  height: 100%;
}

.install-note strong {
  display: block;
  margin-bottom: 2px;
  font-size: 13px;
}

.install-note p {
  margin: 0;
  color: var(--text-soft);
  line-height: 1.6;
  font-size: 12px;
}

.install-feedback {
  min-height: 24px;
}

.install-message {
  margin: 0;
  padding: 12px 14px;
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.6;
}

.install-message.error {
  color: #9f1239;
  background: rgba(244, 63, 94, 0.1);
  border: 1px solid rgba(244, 63, 94, 0.2);
}

.install-message.success {
  color: #065f46;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.install-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.install-actions-right {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.install-btn-primary,
.install-btn-secondary {
  border: none;
  border-radius: 999px;
  padding: 12px 22px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.install-btn-primary {
  color: #05131d;
  background: linear-gradient(135deg, var(--accent), #93c5fd);
  box-shadow: 0 10px 26px rgba(14, 165, 164, 0.2);
}

.install-btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 14px 30px rgba(14, 165, 164, 0.24);
}

.install-btn-primary:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

.install-btn-secondary {
  color: var(--text-soft);
  background: var(--bg-panel);
  border: 1px solid var(--line);
}

.install-btn-secondary:hover {
  color: var(--text);
  border-color: var(--accent);
}

.install-btn-submit {
  min-width: 140px;
  justify-content: center;
}

.install-spinner {
  width: 18px;
  height: 18px;
  animation: install-spin 0.8s linear infinite;
}

@keyframes install-spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 980px) {
  .install-shell {
    grid-template-columns: 1fr;
  }

  .install-card-header {
    flex-direction: column;
    align-items: start;
  }

  .install-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .install-page {
    padding: 16px;
  }

  .install-hero,
  .install-card {
    padding: 20px;
    border-radius: 20px;
  }

  .install-actions {
    flex-direction: column;
  }

  .install-actions-right {
    width: 100%;
    margin-left: 0;
  }

  .install-btn-primary,
  .install-btn-secondary {
    width: 100%;
    justify-content: center;
  }
}
</style>
