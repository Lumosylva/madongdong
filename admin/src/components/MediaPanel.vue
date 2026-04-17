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

    <div class="media-bulk-bar" v-if="selectedIds.size">
      <span>已选择 {{ selectedIds.size }} 项</span>
      <button type="button" class="media-bulk-clear-btn" @click="clearSelection">清空</button>
      <button type="button" class="media-bulk-delete-btn" @click="confirmDelete([...selectedIds])">批量删除</button>
    </div>

    <div class="media-section-grid">
      <section class="panel media-group-panel">
        <div class="media-group-head">
          <h4>图片</h4>
          <div class="media-group-toolbar">
            <span class="media-group-count">{{ grouped.image.length }}</span>
            <button type="button" class="media-select-all-btn" @click="toggleGroupSelection('image')">{{ isGroupFullySelected('image') ? '取消全选' : '全选' }}</button>
          </div>
        </div>
        <div v-if="grouped.image.length" class="media-grid">
          <button
            v-for="item in grouped.image"
            :key="item.id"
            type="button"
            class="media-card media-card-image"
            :class="{ selected: selectedIds.has(item.id) }"
            @click="openPreview(item)"
          >
            <input class="media-card-checkbox" type="checkbox" :checked="selectedIds.has(item.id)" @click.stop="toggleSelected(item.id)" />
            <img class="media-card-thumb" :src="fullUrl(item.url)" :alt="item.original_name" />
            <div class="media-card-body">
              <p class="media-card-title">{{ item.original_name }}</p>
              <small class="media-card-meta">{{ item.mime_type || 'IMAGE' }}</small>
            </div>
          </button>
        </div>
        <p v-else class="tips media-empty">暂无图片</p>
      </section>

      <section class="panel media-group-panel">
        <div class="media-group-head">
          <h4>音频</h4>
          <div class="media-group-toolbar">
            <span class="media-group-count">{{ grouped.audio.length }}</span>
            <button type="button" class="media-select-all-btn" @click="toggleGroupSelection('audio')">{{ isGroupFullySelected('audio') ? '取消全选' : '全选' }}</button>
          </div>
        </div>
        <div v-if="grouped.audio.length" class="media-grid">
          <article v-for="item in grouped.audio" :key="item.id" class="media-card media-card-file" :class="{ selected: selectedIds.has(item.id) }">
            <input class="media-card-checkbox" type="checkbox" :checked="selectedIds.has(item.id)" @click.stop="toggleSelected(item.id)" />
            <div class="media-card-body">
              <p class="media-card-title">{{ item.original_name }}</p>
              <small class="media-card-meta">{{ item.mime_type || 'AUDIO' }}</small>
              <div class="media-card-link-row">
                <span class="media-card-link-text">{{ fullUrl(item.url) }}</span>
                <button type="button" class="media-copy-btn" @click="copyUrl(item.url, item.original_name)">复制链接</button>
              </div>
            </div>
          </article>
        </div>
        <p v-else class="tips media-empty">暂无音频</p>
      </section>

      <section class="panel media-group-panel">
        <div class="media-group-head">
          <h4>视频</h4>
          <div class="media-group-toolbar">
            <span class="media-group-count">{{ grouped.video.length }}</span>
            <button type="button" class="media-select-all-btn" @click="toggleGroupSelection('video')">{{ isGroupFullySelected('video') ? '取消全选' : '全选' }}</button>
          </div>
        </div>
        <div v-if="grouped.video.length" class="media-grid">
          <article v-for="item in grouped.video" :key="item.id" class="media-card media-card-file" :class="{ selected: selectedIds.has(item.id) }">
            <input class="media-card-checkbox" type="checkbox" :checked="selectedIds.has(item.id)" @click.stop="toggleSelected(item.id)" />
            <div class="media-card-body">
              <p class="media-card-title">{{ item.original_name }}</p>
              <small class="media-card-meta">{{ item.mime_type || 'VIDEO' }}</small>
              <div class="media-card-link-row">
                <span class="media-card-link-text">{{ fullUrl(item.url) }}</span>
                <button type="button" class="media-copy-btn" @click="copyUrl(item.url, item.original_name)">复制链接</button>
              </div>
            </div>
          </article>
        </div>
        <p v-else class="tips media-empty">暂无视频</p>
      </section>
    </div>

    <teleport to="body">
      <transition name="media-delete-fade">
        <div v-if="deleteConfirmOpen" class="media-delete-overlay" @click.self="closeDeleteConfirm">
          <div class="media-delete-modal" role="dialog" aria-modal="true" aria-labelledby="media-delete-title">
            <div class="media-delete-head">
              <span class="media-delete-icon">!</span>
              <div>
                <h4 id="media-delete-title">删除媒体</h4>
                <p class="media-delete-subtitle">删除后无法恢复，请确认操作。</p>
              </div>
            </div>
            <div class="media-delete-body">
              <p class="media-delete-text">将删除 <strong>{{ deleteTargetIds.length }}</strong> 个媒体文件。</p>
              <div class="media-delete-preview-list">
                <span v-for="item in deleteTargetNames" :key="item" class="media-delete-preview-item">{{ item }}</span>
              </div>
            </div>
            <div class="media-delete-actions">
              <button type="button" class="media-delete-cancel" @click="closeDeleteConfirm">取消</button>
              <button type="button" class="media-delete-confirm" @click="submitDeleteConfirm">删除</button>
            </div>
          </div>
        </div>
      </transition>
    </teleport>

    <teleport to="body">
      <transition name="media-preview-fade">
        <div v-if="previewItem" class="media-preview-overlay" @click.self="closePreview">
          <div class="media-preview-modal" role="dialog" aria-modal="true" aria-labelledby="media-preview-title">
            <div class="media-preview-image-wrap">
              <img class="media-preview-image" :src="fullUrl(previewItem.url)" :alt="previewItem.original_name" />
            </div>
            <div class="media-preview-info">
              <div class="media-preview-head">
                <h4 id="media-preview-title">媒体详情</h4>
                <button type="button" class="media-preview-close" @click="closePreview">关闭</button>
              </div>
              <div class="media-preview-meta-list">
                <div class="media-preview-meta-item"><span>上传时间</span><strong>{{ formatDate(previewItem.uploaded_at || previewItem.created_at) }}</strong></div>
                <div class="media-preview-meta-item"><span>上传者</span><strong>{{ previewItem.uploader?.nickname || previewItem.user?.nickname || previewItem.author?.nickname || 'admin' }}</strong></div>
                <div class="media-preview-meta-item"><span>文件名</span><strong>{{ previewItem.original_name }}</strong></div>
                <div class="media-preview-meta-item"><span>文件类型</span><strong>{{ previewItem.mime_type || '未知' }}</strong></div>
                <div class="media-preview-meta-item"><span>文件大小</span><strong>{{ formatFileSize(previewItem.file_size || previewItem.size) }}</strong></div>
                <div class="media-preview-meta-item"><span>分辨率</span><strong>{{ formatResolution(previewItem.width, previewItem.height) }}</strong></div>
                <div class="media-preview-meta-item media-preview-url"><span>文件 URL</span><strong>{{ fullUrl(previewItem.url) }}</strong></div>
              </div>
              <div class="media-preview-actions">
                <button type="button" class="media-copy-btn" @click="copyUrl(previewItem.url, previewItem.original_name)">复制链接</button>
                <button type="button" class="danger-btn media-preview-delete" @click="$emit('delete-media', previewItem.id)">删除</button>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </teleport>
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
  'delete-media-batch': [mediaIds: number[]]
}>()

const fileInputRef = ref<HTMLInputElement | null>(null)
const copyMessage = ref('')
const previewItem = ref<any | null>(null)
const selectedIds = ref<Set<number>>(new Set())
const deleteConfirmOpen = ref(false)
const deleteTargetIds = ref<number[]>([])
const deleteTargetNames = ref<string[]>([])

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

const openPreview = (item: any) => {
  previewItem.value = item
}

const closePreview = () => {
  previewItem.value = null
}

const toggleSelected = (id: number) => {
  const next = new Set(selectedIds.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  selectedIds.value = next
}

const clearSelection = () => {
  selectedIds.value = new Set()
}

const toggleGroupSelection = (group: 'image' | 'audio' | 'video') => {
  const groupIds = grouped.value[group].map((item) => item.id)
  const next = new Set(selectedIds.value)
  const allSelected = groupIds.length > 0 && groupIds.every((id) => next.has(id))
  if (allSelected) {
    groupIds.forEach((id) => next.delete(id))
  } else {
    groupIds.forEach((id) => next.add(id))
  }
  selectedIds.value = next
}

const isGroupFullySelected = (group: 'image' | 'audio' | 'video') => {
  const groupIds = grouped.value[group].map((item) => item.id)
  return groupIds.length > 0 && groupIds.every((id) => selectedIds.value.has(id))
}

const confirmDelete = (ids: number[]) => {
  const items = props.media.filter((item) => ids.includes(item.id))
  deleteTargetIds.value = ids
  deleteTargetNames.value = items.map((item) => item.original_name)
  deleteConfirmOpen.value = true
}

const closeDeleteConfirm = () => {
  deleteConfirmOpen.value = false
  deleteTargetIds.value = []
  deleteTargetNames.value = []
}

const submitDeleteConfirm = () => {
  if (!deleteTargetIds.value.length) return
  const ids = [...deleteTargetIds.value]
  if (ids.length === 1) emit('delete-media', ids[0])
  else emit('delete-media-batch', ids)
  if (selectedIds.value.size) {
    const next = new Set(selectedIds.value)
    deleteTargetIds.value.forEach((id) => next.delete(id))
    selectedIds.value = next
  }
  closeDeleteConfirm()
}

const formatDate = (value?: string) => {
  const text = String(value || '').trim()
  if (!text) return '未知'
  const date = new Date(text)
  if (Number.isNaN(date.getTime())) return text
  return date.toLocaleString('zh-CN')
}

const formatFileSize = (value?: number) => {
  const size = Number(value || 0)
  if (!size) return '未知'
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  if (size < 1024 * 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  return `${(size / 1024 / 1024 / 1024).toFixed(1)} GB`
}

const formatResolution = (width?: number, height?: number) => {
  const w = Number(width || 0)
  const h = Number(height || 0)
  if (!w || !h) return '未知'
  return `${w} × ${h}`
}
</script>
