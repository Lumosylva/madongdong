<template>
  <section class="panel">
    <h3>站点设置</h3>

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
        type="file"
        accept="image/png,image/jpeg,image/svg+xml"
        :disabled="logoUploading"
        @change="onSelectLogo"
      />
    </div>

    <input :value="siteTitle" placeholder="网站标题" @input="$emit('update:siteTitle', ($event.target as HTMLInputElement).value)" />
    <input :value="siteSubtitle" placeholder="副标题" @input="$emit('update:siteSubtitle', ($event.target as HTMLInputElement).value)" />
    <input :value="icpBeian" placeholder="备案信息" @input="$emit('update:icpBeian', ($event.target as HTMLInputElement).value)" />
    <input :value="copyrightText" placeholder="版权信息" @input="$emit('update:copyrightText', ($event.target as HTMLInputElement).value)" />
    <button :disabled="logoUploading" @click="$emit('save')">
      {{ logoUploading ? 'Logo 上传中...' : '保存设置' }}
    </button>
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
  'update:copyrightText': [value: string]
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
