<template>
  <section class="panel media-panel">
    <div class="article-manage-head media-head">
      <div>
        <h3>媒体管理</h3>
        <p class="media-subtitle">统一管理图片、音频和视频资源</p>
      </div>
      <span class="article-count media-count">共 {{ media.length }} 项</span>
    </div>

    <p v-if="toastMessage" class="tips media-toast" :class="toastStatus === 'error' ? 'error-message' : 'success-message'">
      {{ toastMessage }}
    </p>
    <p v-if="copyMessage" class="tips success-message">{{ copyMessage }}</p>

    <div class="media-upload-row">
      <input ref="fileInputRef" class="media-file-input" type="file" accept="image/*,audio/*,video/*" @change="onSelectFile" />
      <button class="media-upload-btn" :disabled="uploading" @click="triggerUpload">{{ uploading ? '上传中...' : '上传媒体' }}</button>
    </div>

    <div class="panel media-group-panel">
      <div class="media-group-head">
        <h4>图片</h4>
        <span class="media-group-count">{{ grouped.image.length }}</span>
      </div>
      <ul v-if="grouped.image.length" class="media-list">
        <li v-for="item in grouped.image" :key="item.id" class="article-row media-row">
          <div class="article-row-main media-row-main">
            <p class="article-row-title media-row-title">{{ item.original_name }}</p>
            <small class="article-row-meta media-row-meta">
              <span>{{ item.mime_type }}</span>
              <span>链接：<a href="javascript:void(0)" @click="copyUrl(item.url, item.original_name)">{{ fullUrl(item.url) }}</a></span>
            </small>
          </div>
          <div class="media-row-actions">
            <button class="media-copy-btn" @click="copyUrl(item.url, item.original_name)">复制链接</button>
            <button class="danger-btn media-delete-btn" @click="$emit('delete-media', item.id)">删除</button>
          </div>
        </li>
      </ul>
      <p v-else class="tips media-empty">暂无图片</p>
    </div>

    <div class="panel media-group-panel">
      <div class="media-group-head">
        <h4>音频</h4>
        <span class="media-group-count">{{ grouped.audio.length }}</span>
      </div>
      <ul v-if="grouped.audio.length" class="media-list">
        <li v-for="item in grouped.audio" :key="item.id" class="article-row media-row">
          <div class="article-row-main media-row-main">
            <p class="article-row-title media-row-title">{{ item.original_name }}</p>
            <small class="article-row-meta media-row-meta">
              <span>{{ item.mime_type }}</span>
              <span>链接：<a href="javascript:void(0)" @click="copyUrl(item.url, item.original_name)">{{ fullUrl(item.url) }}</a></span>
            </small>
          </div>
          <div class="media-row-actions">
            <button class="media-copy-btn" @click="copyUrl(item.url, item.original_name)">复制链接</button>
            <button class="danger-btn media-delete-btn" @click="$emit('delete-media', item.id)">删除</button>
          </div>
        </li>
      </ul>
      <p v-else class="tips media-empty">暂无音频</p>
    </div>

    <div class="panel media-group-panel">
      <div class="media-group-head">
        <h4>视频</h4>
        <span class="media-group-count">{{ grouped.video.length }}</span>
      </div>
      <ul v-if="grouped.video.length" class="media-list">
        <li v-for="item in grouped.video" :key="item.id" class="article-row media-row">
          <div class="article-row-main media-row-main">
            <p class="article-row-title media-row-title">{{ item.original_name }}</p>
            <small class="article-row-meta media-row-meta">
              <span>{{ item.mime_type }}</span>
              <span>链接：<a href="javascript:void(0)" @click="copyUrl(item.url, item.original_name)">{{ fullUrl(item.url) }}</a></span>
            </small>
          </div>
          <button class="danger-btn media-delete-btn" @click="$emit('delete-media', item.id)">删除</button>
        </li>
      </ul>
      <p v-else class="tips media-empty">暂无视频</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { API_ORIGIN } from '../api'

const props = defineProps<{
  media: any[]
  uploading: boolean
  toastMessage?: string
  toastStatus?: 'success' | 'error' | ''
}>()

const emit = defineEmits<{
  upload: [file: File]
  'delete-media': [mediaId: number]
}>()

const fileInputRef = ref<HTMLInputElement | null>(null)
const copyMessage = ref('')

const triggerUpload = () => {
  fileInputRef.value?.click()
}

const onSelectFile = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  emit('upload', file)
  target.value = ''
}

const grouped = computed(() => {
  const image = props.media.filter((item) => {
    const mediaType = String(item.media_type || '').toUpperCase()
    const mime = String(item.mime_type || '').toLowerCase()
    return mediaType === 'IMAGE' || mime === 'image/svg+xml'
  })
  const audio = props.media.filter((item) => String(item.media_type || '').toUpperCase() === 'AUDIO')
  const video = props.media.filter((item) => String(item.media_type || '').toUpperCase() === 'VIDEO')
  return { image, audio, video }
})

const fullUrl = (url: string) => {
  const value = String(url || '').trim()
  if (!value) return ''
  if (/^https?:\/\//i.test(value)) return value
  return `${API_ORIGIN}${value.startsWith('/') ? '' : '/'}${value}`
}

const copyUrl = async (url: string, fileName: string) => {
  await navigator.clipboard.writeText(fullUrl(url))
  copyMessage.value = `已复制 URL：${fileName}`
  setTimeout(() => {
    copyMessage.value = ''
  }, 1800)
}
</script>
