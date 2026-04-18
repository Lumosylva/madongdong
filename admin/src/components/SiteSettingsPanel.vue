<template>
  <section class="panel settings-panel">
    <h3>站点设置</h3>

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
        <h4>站点信息</h4>
        <label class="settings-field">
          <span>备案信息</span>
          <textarea class="settings-input settings-textarea" :value="icpBeian" placeholder="请输入页脚HTML代码" @input="$emit('update:icpBeian', ($event.target as HTMLTextAreaElement).value)"></textarea>
          <p class="tips">页脚HTML代码，用于网站底部展示</p>
        </label>

        <div class="save-row">
          <button :disabled="logoUploading" @click="$emit('save')">
            {{ logoUploading ? 'Logo 上传中...' : '保存设置' }}
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
}>()

const emit = defineEmits<{
  'update:siteTitle': [value: string]
  'update:siteSubtitle': [value: string]
  'update:icpBeian': [value: string]
  'select-logo': [file: File]
  save: []
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
