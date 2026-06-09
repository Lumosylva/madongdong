<template>
  <div class="shell friend-links-page" v-if="data">
    <WebTopbar
      :title="data.site.site_title"
      :subtitle="data.site.site_subtitle || '友情链接与站点互访申请'
      "
      :logo-url="toAbsoluteAssetUrl(data.site.site_logo)"
      :nav-items="data.nav_items"
      :theme="theme"
      :current-path="route.path"
      :current-full-path="route.fullPath"
      :search-keyword="keyword"
      :collapsible-search="true"
      @update:search-keyword="keyword = $event"
      @toggle-theme="toggleTheme"
      @search="goSearch"
    />

    <main class="friend-links-layout">
      <section class="friend-links-card friend-links-card-wide friend-links-hero">
        <h2>友情链接</h2>
        <p class="friend-links-hero-text">
          欢迎与本站交换优质链接。我们优先接受内容健康、更新稳定、排版清晰的网站申请，
          共同构建更高质量的内容生态。
        </p>
        <div class="friend-links-metrics">
          <div class="friend-links-metric friend-links-metric-inline">
            <span>已收录</span>
            <strong>{{ links.length }}</strong>
          </div>
        </div>
        <div class="friend-links-hero-actions">
          <a href="#friend-links-form" class="friend-links-action-btn">申请友链</a>
        </div>
      </section>

      <section id="friend-links-form" class="friend-links-card friend-links-card-wide friend-links-form-card">
        <div class="friend-links-card-head">
          <div>
            <h3>申请友情链接</h3>
            <p>提交你的站点信息，我们会尽快审核</p>
          </div>
        </div>

        <form class="friend-links-form" @submit.prevent="submitApplication">
          <div class="friend-links-form-grid">
            <label>
              <span>站点名称</span>
              <input
                v-model="form.name"
                placeholder="例如：我的博客"
                @blur="nameTouched = true; nameError = validateFriendLinkName(form.name)"
                @input="nameTouched = true; nameError = validateFriendLinkName(form.name)"
              />
              <small v-if="nameTouched && nameError" class="friend-links-field-error">{{ nameError }}</small>
            </label>
            <label>
              <span>站点地址</span>
              <input
                v-model="form.url"
                placeholder="https://example.com"
                @blur="urlTouched = true; urlError = validateFriendLinkUrl(form.url)"
                @input="urlTouched = true; urlError = validateFriendLinkUrl(form.url)"
              />
              <small v-if="urlTouched && urlError" class="friend-links-field-error">{{ urlError }}</small>
            </label>
            <label>
              <span>联系邮箱</span>
              <input
                v-model="form.email"
                type="email"
                placeholder="用于审核联系"
                @blur="emailTouched = true; emailError = validateFriendLinkEmail(form.email)"
                @input="emailTouched = true; emailError = validateFriendLinkEmail(form.email)"
              />
              <small v-if="emailTouched && emailError" class="friend-links-field-error">{{ emailError }}</small>
            </label>
            <label class="friend-links-textarea-field">
              <span>站点描述</span>
              <textarea v-model="form.description" rows="4" placeholder="简单介绍你的站点" />
            </label>
          </div>

          <div class="friend-links-form-actions">
            <button class="auth-submit-btn" type="submit" :disabled="submitting">
              {{ submitting ? '提交中...' : '提交申请' }}
            </button>
            <p class="friend-links-form-tip">提交后会保存到浏览器，并同步提交到站点后台审核。</p>
          </div>
        </form>

        <p v-if="message" class="auth-message friend-links-message" :class="status === 'error' ? 'error-message' : 'success-message'">{{ message }}</p>
      </section>

      <section class="friend-links-card friend-links-card-wide friend-links-list-card">
        <div class="friend-links-card-head">
          <div>
            <h3>已收录友情链接</h3>
            <p>精选站点展示，点击可直接访问</p>
          </div>
          <span class="friend-links-count">{{ links.length }} 个站点</span>
        </div>

        <div v-if="links.length" class="friend-links-grid">
          <a
            v-for="item in links"
            :key="item.name + item.url"
            class="friend-link-item"
            :href="item.url"
            target="_blank"
            rel="noreferrer noopener"
          >
            <div class="friend-link-logo">{{ item.name.slice(0, 1) }}</div>
            <div class="friend-link-content">
              <strong>{{ item.name }}</strong>
              <p>{{ item.description }}</p>
              <span>{{ item.url }}</span>
            </div>
          </a>
        </div>
        <p v-else class="friend-links-empty">暂无友情链接，欢迎成为首批合作站点。</p>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { toAbsoluteAssetUrl, webApi } from '../api'
import WebTopbar from '../components/WebTopbar.vue'
import { applySiteMetaFromSetting, buildPageTitle, setSiteSetting } from '../site-meta'

type ThemeMode = 'light' | 'dark'
type FriendLinkItem = { name: string; url: string; description: string }

const route = useRoute()
const router = useRouter()
const data = ref<Awaited<ReturnType<typeof webApi.getHome>> | null>(null)
const keyword = ref('')
const theme = ref<ThemeMode>('light')
const submitting = ref(false)
const message = ref('')
const status = ref<'success' | 'error' | ''>('')
const nameTouched = ref(false)
const nameError = ref('')
const urlTouched = ref(false)
const urlError = ref('')
const emailTouched = ref(false)
const emailError = ref('')
const links = ref<FriendLinkItem[]>([])
const form = ref({ name: '', url: '', description: '', email: '' })

const validateFriendLinkName = (value: string) => {
  const input = value.trim()
  if (!input) return '请填写站点名称'
  if (input.length < 2) return '站点名称至少 2 个字符'
  if (input.length > 100) return '站点名称不能超过 100 个字符'
  return ''
}

const validateFriendLinkUrl = (value: string) => {
  const input = value.trim()
  if (!input) return '请填写站点地址'
  if (/\s/.test(input)) return '站点地址不能包含空格'
  if (/^https?:\/\//i.test(input)) return ''
  if (/^[a-z0-9.-]+\.[a-z]{2,}(\/.*)?$/i.test(input)) return ''
  return '请输入正确的网址，例如 https://example.com'
}

const validateFriendLinkEmail = (value: string) => {
  const input = value.trim()
  if (!input) return '请填写联系邮箱'
  if (!/^\S+@\S+\.\S+$/.test(input)) return '请输入有效的邮箱地址'
  if (input.length > 255) return '邮箱长度不能超过 255 个字符'
  return ''
}

const applyTheme = (value: ThemeMode) => {
  theme.value = value
  document.documentElement.dataset.theme = value
  localStorage.setItem('md-theme', value)
}

const toggleTheme = () => {
  applyTheme(theme.value === 'light' ? 'dark' : 'light')
}

const goSearch = () => {
  if (!keyword.value.trim()) return
  router.push(`/search?keyword=${encodeURIComponent(keyword.value.trim())}`)
}

const loadData = async () => {
  const [home, friendLinks] = await Promise.all([webApi.getHome(1, 1), webApi.getFriendLinks()])
  data.value = home
  setSiteSetting(home.site)
  applySiteMetaFromSetting(home.site)
  links.value = friendLinks.map((item) => ({
    name: item.name,
    url: item.url,
    description: item.description,
  }))
  document.title = buildPageTitle('友情链接')
}

const submitApplication = async () => {
  if (submitting.value) return
  const name = form.value.name.trim()
  const url = form.value.url.trim()
  const description = form.value.description.trim()
  const email = form.value.email.trim()
  const nameErrorText = validateFriendLinkName(name)
  const urlErrorText = validateFriendLinkUrl(url)
  const emailErrorText = validateFriendLinkEmail(email)

  nameTouched.value = true
  urlTouched.value = true
  emailTouched.value = true
  nameError.value = nameErrorText
  urlError.value = urlErrorText
  emailError.value = emailErrorText

  if (nameErrorText || urlErrorText || emailErrorText || !description) {
    status.value = 'error'
    message.value = !description ? '请填写站点描述' : '请先修正表单中的错误'
    return
  }

  submitting.value = true
  message.value = ''
  status.value = ''

  try {
    await webApi.submitFriendLink({ name, url: /^https?:\/\//i.test(url) ? url : `https://${url}`, description, email })
    form.value = { name: '', url: '', description: '', email: '' }
    nameTouched.value = false
    urlTouched.value = false
    emailTouched.value = false
    nameError.value = ''
    urlError.value = ''
    emailError.value = ''
    status.value = 'success'
    message.value = '申请已提交，等待审核'
  } catch (error) {
    status.value = 'error'
    message.value = error instanceof Error ? error.message : '提交失败'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  document.title = buildPageTitle('友情链接')
  await loadData()
})
</script>

<style scoped>
.friend-links-page {
  position: relative;
  padding-top: 10px;
}

.friend-links-page::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 12% 10%, rgba(14, 165, 164, 0.12), transparent 22%),
    radial-gradient(circle at 88% 8%, rgba(234, 154, 24, 0.1), transparent 18%);
  z-index: 0;
}

.friend-links-layout {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr;
  gap: 18px;
  align-items: start;
}

.friend-links-hero,
.friend-links-card {
  border: none;
  border-radius: 0;
  background: transparent;
  backdrop-filter: none;
  box-shadow: none;
}

.friend-links-hero {
  padding: 10px 2px 2px;
  gap: 24px;
}

.friend-links-card {
  padding: 0 2px;
}

.friend-links-hero-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.friend-links-eyebrow {
  margin: 0;
  color: var(--accent);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-size: 12px;
  font-weight: 800;
}

.friend-links-pill {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(14, 165, 164, 0.1);
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
}

.friend-links-hero h2,
.friend-links-card h3 {
  margin: 0;
}

.friend-links-hero h2 {
  font-size: clamp(30px, 4vw, 44px);
  line-height: 1.08;
  margin-bottom: 6px;
}

.friend-links-hero-text,
.friend-links-card p,
.friend-links-pending-item p {
  margin: 0;
  color: var(--text-soft);
  line-height: 1.8;
}

.friend-links-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.friend-links-metric {
  padding: 14px;
  border-radius: 18px;
  background: var(--bg-soft);
  border: 1px solid var(--line);
}

.friend-links-metric-inline {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.friend-links-metric-inline span {
  margin-top: 0;
}

.friend-links-metric strong {
  display: block;
  font-size: 22px;
  line-height: 1;
}

.friend-links-metric span {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-soft);
}

.friend-links-hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
}

.friend-links-action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0 16px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--accent), #38bdf8);
  color: #02131f;
  font-weight: 800;
  box-shadow: 0 14px 28px rgba(14, 165, 164, 0.2);
}

.friend-links-action-btn.secondary {
  background: transparent;
  color: var(--text);
  border: 1px solid var(--line);
  box-shadow: none;
}

.friend-links-card {
  padding: 24px;
}

.friend-links-card-wide {
  width: 100%;
}

.friend-links-form-card,
.friend-links-pending-card {
  align-self: start;
}

.friend-links-card-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.friend-links-card-head h3 {
  font-size: 22px;
}

.friend-links-count {
  flex: 0 0 auto;
  color: var(--text-soft);
  font-size: 13px;
}

.friend-links-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.friend-link-item {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr);
  gap: 14px;
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.45));
  border: 1px solid var(--line);
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

:global([data-theme='dark']) .friend-link-item {
  background: linear-gradient(180deg, rgba(10, 24, 44, 0.8), rgba(10, 24, 44, 0.58));
}

.friend-link-item:hover {
  transform: translateY(-2px);
  border-color: rgba(14, 165, 164, 0.25);
  box-shadow: 0 18px 32px rgba(16, 35, 63, 0.08);
}

.friend-link-logo {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 18px;
  color: #04111d;
  background: linear-gradient(135deg, var(--accent), #93c5fd);
}

.friend-link-content {
  min-width: 0;
  display: grid;
  gap: 6px;
}

.friend-link-content strong {
  font-size: 16px;
}

.friend-link-content p,
.friend-link-content span {
  font-size: 13px;
}

.friend-link-content span {
  color: var(--text-soft);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.friend-links-empty {
  padding: 18px 0 2px;
  color: var(--text-soft);
}

.friend-links-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.friend-links-form-grid label {
  display: grid;
  gap: 8px;
}

.friend-links-field-error {
  color: #ef4444;
  font-size: 12px;
  line-height: 1.4;
}

.friend-links-form-grid label span {
  font-size: 13px;
  color: var(--text-soft);
}

.friend-links-form-grid input,
.friend-links-form-grid textarea {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: var(--bg-soft);
  color: var(--text);
  padding: 12px 14px;
  outline: none;
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

.friend-links-form-grid input:focus,
.friend-links-form-grid textarea:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 4px rgba(14, 165, 164, 0.12);
}

.friend-links-textarea-field {
  grid-column: 1 / -1;
}

.friend-links-textarea-field textarea {
  min-height: 96px;
  resize: vertical;
}

.friend-links-form-actions {
  margin-top: 18px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.friend-links-form-tip {
  color: var(--text-soft);
  font-size: 12px;
}

.friend-links-message {
  margin-top: 16px;
}

.friend-links-pending-list {
  display: grid;
  gap: 12px;
}

.friend-links-pending-item {
  padding: 16px;
  border-radius: 18px;
  background: var(--bg-soft);
  border: 1px solid var(--line);
  display: grid;
  gap: 8px;
}

.friend-links-pending-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.friend-links-pending-head span {
  font-size: 12px;
  color: var(--accent);
  font-weight: 700;
}

.friend-links-pending-item a,
.friend-links-pending-item em {
  font-size: 13px;
  color: var(--text-soft);
  overflow-wrap: anywhere;
  word-break: break-word;
}

@media (max-width: 1024px) {
  .friend-links-layout {
    grid-template-columns: 1fr;
  }

  .friend-links-hero {
    position: relative;
    grid-row: auto;
  }

  .friend-links-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .friend-links-form-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .friend-links-card,
  .friend-links-hero {
    padding: 8px 0 0;
    border-radius: 0;
  }

  .friend-links-grid {
    grid-template-columns: 1fr;
  }

  .friend-links-metrics {
    grid-template-columns: 1fr;
  }

  .friend-links-card-head,
  .friend-links-pending-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .friend-link-item {
    grid-template-columns: 42px minmax(0, 1fr);
    padding: 16px;
  }

  .friend-link-logo {
    width: 42px;
    height: 42px;
    border-radius: 14px;
  }

  .friend-links-action-btn {
    width: 100%;
  }

  .friend-links-hero-actions {
    flex-direction: column;
  }

  .friend-links-form-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
