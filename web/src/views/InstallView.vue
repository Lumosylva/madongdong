<template>
  <div class="install-page">
    <section class="install-shell">
      <aside class="install-hero">
        <div class="install-brand">
          <span class="install-brand-mark">MD</span>
          <div>
            <p class="install-eyebrow">欢迎使用</p>
            <h1>开始安装 MaDongDong Blog</h1>
          </div>
        </div>

        <p class="install-lead">
          这是一个简洁的安装向导。接下来只需填写站点信息和管理员账号，系统会自动完成初始化，准备好后即可开始使用。
        </p>

        <div class="install-checklist">
          <div class="install-check-item">
            <span class="install-check-dot"></span>
            <span>下一步将自动创建角色、权限与默认站点配置</span>
          </div>
          <div class="install-check-item">
            <span class="install-check-dot"></span>
            <span>系统会自动生成首页、搜索等基础导航</span>
          </div>
          <div class="install-check-item">
            <span class="install-check-dot"></span>
            <span>安装完成后可直接使用管理员账号登录后台</span>
          </div>
        </div>

        <div class="install-tip-card">
          <strong>开始之前</strong>
          <p>请先确认数据库、上传目录和后端服务已经可用，然后继续下一步。</p>
        </div>
      </aside>

      <div class="install-card">
        <div class="install-card-header">
          <div>
            <p class="install-card-kicker">安装配置</p>
            <h2>填写基础信息</h2>
          </div>
          <p class="install-card-subtitle">带 * 的信息建议保持准确，便于后续管理与部署。</p>
        </div>

        <form class="install-form" @submit.prevent="submitInstall">
          <div class="install-grid">
            <label>
              <span>站点标题</span>
              <input v-model="form.site_title" required placeholder="例如：MaDongDong Blog" />
            </label>
            <label>
              <span>副标题</span>
              <input v-model="form.site_subtitle" placeholder="例如：记录技术、生活与长期主义" />
            </label>
            <label>
              <span>管理员用户名</span>
              <input v-model="form.admin_username" required placeholder="例如：admin" />
            </label>
            <label>
              <span>管理员密码</span>
              <input v-model="form.admin_password" type="password" required placeholder="请设置强密码" />
            </label>
            <label>
              <span>管理员昵称</span>
              <input v-model="form.admin_nickname" required placeholder="例如：系统管理员" />
            </label>
            <label>
              <span>管理员邮箱</span>
              <input v-model="form.admin_email" type="email" required placeholder="例如：admin@example.com" />
            </label>
            <label>
              <span>ICP备案</span>
              <input v-model="form.icp_beian" placeholder="没有可先留空" />
            </label>
            <label>
              <span>版权信息</span>
              <input v-model="form.copyright_text" placeholder="例如：© MaDongDong Blog" />
            </label>
            <label>
              <span>首页每页文章数</span>
              <input v-model.number="form.homepage_page_size" type="number" min="1" max="100" />
            </label>
            <label class="checkbox-row checkbox-card">
              <input v-model="form.comment_requires_review" type="checkbox" />
              <div>
                <span>评论需要审核</span>
                <p>开启后，前台提交的评论会先进入审核流程。</p>
              </div>
            </label>
          </div>

          <div class="install-feedback">
            <p v-if="errorMessage" class="message error">{{ errorMessage }}</p>
            <p v-if="successMessage" class="message success">{{ successMessage }}</p>
          </div>

          <div class="actions">
            <button type="submit" :disabled="submitting">{{ submitting ? '正在初始化...' : '确认并安装' }}</button>
          </div>
        </form>
      </div>
    </section>
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

const getAdminLoginUrl = () => {
  const adminBasePath = (import.meta.env.VITE_ADMIN_BASE_PATH as string | undefined)?.trim() || '/admin'
  const normalized = adminBasePath.startsWith('/') ? adminBasePath : `/${adminBasePath}`
  return `${normalized.replace(/\/$/, '')}/login`
}

const checkInstalled = async () => {
  try {
    const res = await webApi.getInstallStatus()
    if (res.data.installed) {
      window.location.assign(getAdminLoginUrl())
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
    await webApi.installSite({ ...form })
    successMessage.value = '初始化完成，正在跳转到管理员登录页...'
    window.setTimeout(() => {
      const adminBase = (import.meta.env.VITE_ADMIN_BASE_URL as string | undefined)?.trim() || ''
      const target = adminBase ? `${adminBase.replace(/\/$/, '')}/login` : '/login'
      window.location.assign(target)
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

.install-checklist {
  display: grid;
  gap: 12px;
}

.install-check-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  color: var(--text);
}

.install-check-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  margin-top: 7px;
  background: var(--accent);
  box-shadow: 0 0 0 5px rgba(14, 165, 164, 0.12);
  flex: 0 0 auto;
}

.install-tip-card {
  padding: 16px 18px;
  border-radius: 18px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.5);
}

:global([data-theme='dark']) .install-tip-card {
  background: rgba(255, 255, 255, 0.03);
}

.install-tip-card strong {
  display: block;
  margin-bottom: 8px;
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
  margin-bottom: 20px;
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

.install-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.install-grid label,
.checkbox-card {
  border: 1px solid var(--line);
  background: var(--bg-panel);
  border-radius: 18px;
  padding: 14px 14px 12px;
  display: grid;
  gap: 8px;
}

.install-grid label span,
.checkbox-card span {
  font-size: 13px;
  color: var(--text-soft);
}

.install-grid input[type='text'],
.install-grid input[type='email'],
.install-grid input[type='password'],
.install-grid input[type='number'],
.install-grid input:not([type]) {
  width: 100%;
  border: 1px solid transparent;
  background: rgba(255, 255, 255, 0.88);
  border-radius: 12px;
  padding: 12px 14px;
  color: var(--text);
  outline: none;
}

:global([data-theme='dark']) .install-grid input[type='text'],
:global([data-theme='dark']) .install-grid input[type='email'],
:global([data-theme='dark']) .install-grid input[type='password'],
:global([data-theme='dark']) .install-grid input[type='number'],
:global([data-theme='dark']) .install-grid input:not([type]) {
  background: rgba(255, 255, 255, 0.06);
}

.install-grid input:focus {
  border-color: rgba(14, 165, 164, 0.35);
  box-shadow: 0 0 0 4px rgba(14, 165, 164, 0.12);
}

.checkbox-card {
  grid-column: 1 / -1;
  grid-template-columns: auto 1fr;
  align-items: center;
}

.checkbox-card p {
  margin: 2px 0 0;
  color: var(--text-soft);
  line-height: 1.6;
  font-size: 12px;
}

.checkbox-row input {
  width: 18px;
  height: 18px;
  accent-color: var(--accent);
}

.install-feedback {
  min-height: 24px;
}

.message {
  margin: 0;
  padding: 12px 14px;
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.6;
}

.message.error {
  color: #9f1239;
  background: rgba(244, 63, 94, 0.1);
  border: 1px solid rgba(244, 63, 94, 0.2);
}

.message.success {
  color: #065f46;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.actions {
  display: flex;
  justify-content: flex-end;
}

.actions button {
  border: none;
  border-radius: 999px;
  padding: 12px 22px;
  font-weight: 700;
  cursor: pointer;
  color: #05131d;
  background: linear-gradient(135deg, var(--accent), #93c5fd);
  box-shadow: 0 10px 26px rgba(14, 165, 164, 0.2);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.actions button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 14px 30px rgba(14, 165, 164, 0.24);
}

.actions button:disabled {
  opacity: 0.72;
  cursor: not-allowed;
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

  .actions {
    justify-content: stretch;
  }

  .actions button {
    width: 100%;
  }
}
</style>
