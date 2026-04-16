<template>
  <section class="panel media-panel">
    <h3>媒体管理</h3>

    <p v-if="toastMessage" class="tips media-toast" :class="toastStatus === 'error' ? 'error-message' : 'success-message'">
      {{ toastMessage }}
    </p>
    <p v-if="copyMessage" class="tips success-message">{{ copyMessage }}</p>

    <div class="media-upload-row">
      <input ref="fileInputRef" type="file" accept="image/*,audio/*,video/*" @change="onSelectFile" />
      <button :disabled="uploading" @click="triggerUpload">{{ uploading ? '上传中...' : '上传媒体' }}</button>
    </div>

    <div class="panel media-group-panel">
      <h4>图片</h4>
      <ul v-if="grouped.image.length" class="media-list">
        <li v-for="item in grouped.image" :key="item.id" class="media-row">
          <div>
            <p>{{ item.original_name }}</p>
            <small>
              {{ item.mime_type }} ︱
              <a href="javascript:void(0)" @click="copyUrl(item.url, item.original_name)">{{ fullUrl(item.url) }}</a>
            </small>
          </div>
          <button class="danger-btn" @click="$emit('delete-media', item.id)">删除</button>
        </li>
      </ul>
      <p v-else class="tips">暂无图片</p>
    </div>

    <div class="panel media-group-panel">
      <h4>音频</h4>
      <ul v-if="grouped.audio.length" class="media-list">
        <li v-for="item in grouped.audio" :key="item.id" class="media-row">
          <div>
            <p>{{ item.original_name }}</p>
            <small>
              {{ item.mime_type }} ︱
              <a href="javascript:void(0)" @click="copyUrl(item.url, item.original_name)">{{ fullUrl(item.url) }}</a>
            </small>
          </div>
          <button class="danger-btn" @click="$emit('delete-media', item.id)">删除</button>
        </li>
      </ul>
      <p v-else class="tips">暂无音频</p>
    </div>

    <div class="panel media-group-panel">
      <h4>视频</h4>
      <ul v-if="grouped.video.length" class="media-list">
        <li v-for="item in grouped.video" :key="item.id" class="media-row">
          <div>
            <p>{{ item.original_name }}</p>
            <small>
              {{ item.mime_type }} ︱
              <a href="javascript:void(0)" @click="copyUrl(item.url, item.original_name)">{{ fullUrl(item.url) }}</a>
            </small>
          </div>
          <button class="danger-btn" @click="$emit('delete-media', item.id)">删除</button>
        </li>
      </ul>
      <p v-else class="tips">暂无视频</p>
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
