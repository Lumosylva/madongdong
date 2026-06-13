<template>
  <section class="panel settings-panel">
    <div class="settings-head">
      <div>
        <h3>站点设置</h3>
        <p>管理站点品牌信息、页脚内容与全局配置</p>
      </div>
    </div>

    <div class="settings-grid">
      <section class="settings-card">
        <h4>品牌信息</h4>
        <div class="logo-uploader">
          <p class="tips">站点 Logo（支持 png/jpg/svg；png/jpg 将裁剪为 64x64）</p>

          <div
            class="logo-dropzone"
            :class="{ dragging: isDragging }"
            @dragover.prevent="onDragOver"
            @dragleave.prevent="onDragLeave"
            @drop.prevent="onDrop"
          >
            <div class="logo-preview-wrap">
              <img v-if="previewLogo" :src="previewLogo" alt="site logo" class="logo-preview" />
              <div v-else class="logo-placeholder">64 × 64</div>
            </div>

            <p class="tips">拖拽图片到此处，或点击下方按钮选择文件</p>
            <p v-if="sourceSizeText" class="tips">原图尺寸：{{ sourceSizeText }}</p>
            <p v-if="logoUploadMessage" class="tips" :class="logoUploadStatus === 'error' ? 'error-message' : 'success-message'">
              {{ logoUploadMessage }}
            </p>
          </div>

          <input
            ref="fileInputRef"
            class="logo-file-input"
            type="file"
            accept="image/png,image/jpeg,image/svg+xml"
            :disabled="logoUploading"
            @change="onSelectLogo"
          />
          <button type="button" class="logo-file-button" :disabled="logoUploading" @click="fileInputRef?.click()">
            {{ logoUploading ? '上传中...' : '选择文件' }}
          </button>
        </div>

        <label class="settings-field">
          <span>网站标题</span>
          <input class="settings-input" :value="siteTitle" placeholder="请输入网站标题" @input="$emit('update:siteTitle', ($event.target as HTMLInputElement).value)" />
        </label>
        <label class="settings-field">
          <span>副标题</span>
          <input class="settings-input" :value="siteSubtitle" placeholder="请输入副标题" @input="$emit('update:siteSubtitle', ($event.target as HTMLInputElement).value)" />
        </label>
      </section>

      <section class="settings-card">
        <h4>页脚信息</h4>
        <label class="settings-field">
          <textarea class="settings-input settings-textarea" :value="icpBeian" placeholder="请输入页脚 HTML 代码" @input="$emit('update:icpBeian', ($event.target as HTMLTextAreaElement).value)"></textarea>
          <p class="tips">支持 HTML 片段，用于网站底部展示</p>
        </label>

        <div class="save-row">
          <button type="button" class="settings-save-button" :disabled="logoUploading" @click="$emit('save')">
            {{ logoUploading ? 'Logo 上传中...' : '保存设置' }}
          </button>
        </div>
      </section>

      <section class="settings-card">
        <h4>服务器配置</h4>
        <p class="tips" style="margin-bottom:14px">以下配置存储在 .env 文件中，部分修改需重启后端后生效。</p>

        <label class="settings-field">
          <span>站点域名</span>
          <div class="settings-field-row">
            <input class="settings-input" :value="serverDomain" placeholder="例如：example.com" @input="$emit('update:serverDomain', ($event.target as HTMLInputElement).value)" />
            <button type="button" class="settings-field-btn" title="自动获取当前域名" @click="$emit('detect-domain')">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
            </button>
          </div>
          <p class="tips">用于 CORS 来源配置，保存后自动更新 .env</p>
        </label>

        <label class="settings-field">
          <span>JWT 签名密钥</span>
          <div class="settings-field-row">
            <input class="settings-input" :type="showSecretKey ? 'text' : 'password'" :value="serverSecretKey" placeholder="留空则自动生成" @input="$emit('update:serverSecretKey', ($event.target as HTMLInputElement).value)" />
            <button type="button" class="settings-field-btn" :title="showSecretKey ? '隐藏' : '显示'" @click="showSecretKey = !showSecretKey">
              <svg v-if="showSecretKey" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3.53 2.47 2.47 3.53l3.06 3.06C3.44 8.3 1.94 10.16 1 12c1.86 3.62 5.75 8 11 8 1.61 0 3.15-.32 4.57-.89l3.9 3.9 1.06-1.06-18-18Zm7.04 9.16 1.8 1.8a2.5 2.5 0 0 1-3.57-3.57l1.77 1.77ZM12 6c4.41 0 8.3 4.38 10 6-1.07 2.09-2.73 4.22-4.78 5.74l-2.05-2.05a4 4 0 0 0-5.61-5.61L7.51 7.51A10.16 10.16 0 0 1 12 6Zm0 12c-4.09 0-7.38-3.1-9.08-6 1.08-1.88 2.6-3.68 4.4-5.01l1.52 1.52a8 8 0 0 0 6.98 6.98l1.52 1.52C15.08 17.52 13.62 18 12 18Z" fill="currentColor"/></svg>
              <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5c-5.25 0-9.14 4.38-11 7 1.86 2.62 5.75 7 11 7s9.14-4.38 11-7c-1.86-2.62-5.75-7-11-7Zm0 12c-4.09 0-7.38-3.1-9.08-5 1.7-1.9 5-5 9.08-5s7.38 3.1 9.08 5c-1.7 1.9-5 5-9.08 5Zm0-8a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z" fill="currentColor"/></svg>
            </button>
          </div>
          <p class="tips">用于 JWT 令牌签名，修改后需重启后端生效</p>
        </label>

        <label class="settings-field">
          <span>数据库连接</span>
          <input class="settings-input settings-input-readonly" :value="serverDatabaseUrl" readonly />
          <p class="tips">数据库连接字符串（仅显示，修改需手动编辑 .env 文件）</p>
        </label>

        <label class="settings-field">
          <span>文件上传目录</span>
          <input class="settings-input settings-input-readonly" :value="serverUploadDir" readonly />
          <p class="tips">上传文件存储路径（仅显示，修改需手动编辑 .env 文件）</p>
        </label>

        <div class="save-row">
          <button type="button" class="settings-save-button" @click="$emit('save-server-config')">
            保存服务器配置
          </button>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const fileInputRef = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const sourceSizeText = ref('')
const showSecretKey = ref(false)

defineProps<{
  siteTitle: string
  siteSubtitle: string
  icpBeian: string
  copyrightText: string
  previewLogo: string
  logoUploading?: boolean
  logoUploadMessage?: string
  logoUploadStatus?: 'success' | 'error' | ''
  logoCropApplied?: boolean
  serverDomain: string
  serverSecretKey: string
  serverDatabaseUrl: string
  serverUploadDir: string
}>()

const emit = defineEmits<{
  'update:siteTitle': [value: string]
  'update:siteSubtitle': [value: string]
  'update:icpBeian': [value: string]
  'update:serverDomain': [value: string]
  'update:serverSecretKey': [value: string]
  'select-logo': [file: File]
  'detect-domain': []
  save: []
  'save-server-config': []
}>()

const inspectImageSize = (file: File) => {
  if (!file.type.startsWith('image/')) {
    sourceSizeText.value = ''
    return
  }
  const reader = new FileReader()
  reader.onload = () => {
    const img = new Image()
    img.onload = () => {
      sourceSizeText.value = `${img.width} × ${img.height}`
    }
    img.src = String(reader.result || '')
  }
  reader.readAsDataURL(file)
}

const emitFile = (file: File) => {
  inspectImageSize(file)
  emit('select-logo', file)
}

const onSelectLogo = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  emitFile(file)
  target.value = ''
}

const onDragOver = () => {
  isDragging.value = true
}

const onDragLeave = () => {
  isDragging.value = false
}

const onDrop = (event: DragEvent) => {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (!file) return
  emitFile(file)
}
</script>
