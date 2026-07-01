<template>
  <section class="panel media-panel">
    <div class="article-manage-head media-head">
      <div>
        <h3>{{ t('media.title') }}</h3>
        <p class="media-subtitle">{{ t('media.subtitle') }}</p>
      </div>
      <span class="article-count media-count">{{ t('common.count', { n: media.length }) }}</span>
    </div>

    <p v-if="toastMessage" class="tips media-toast" :class="toastStatus === 'error' ? 'error-message' : 'success-message'">
      {{ toastMessage }}
    </p>
    <p v-if="copyMessage" class="tips success-message">{{ copyMessage }}</p>

    <div class="media-upload-row">
      <input ref="fileInputRef" class="media-file-input" type="file" accept="image/*,audio/*,video/*" @change="onSelectFile" />
      <button class="media-upload-btn" :disabled="uploading" @click="triggerUpload">{{ uploading ? t('common.uploading') : t('media.uploadButton') }}</button>
    </div>

    <div class="media-bulk-bar" v-if="selectedIds.size">
      <span>{{ t('media.selectedCount', { n: selectedIds.size }) }}</span>
      <button type="button" class="media-bulk-clear-btn" @click="clearSelection">{{ t('media.clearSelection') }}</button>
      <button type="button" class="media-bulk-delete-btn" @click="confirmDelete([...selectedIds])">{{ t('media.batchDelete') }}</button>
    </div>

    <div class="media-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="media-tab"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        <span class="media-tab-icon" v-html="tab.icon"></span>
        <span class="media-tab-label">{{ tab.label }}</span>
        <span class="media-tab-count">{{ tab.count }}</span>
      </button>
    </div>

    <div class="media-tab-content">
      <!-- Images -->
      <div v-show="activeTab === 'image'" class="media-group-panel">
        <div class="media-group-head">
          <h4>{{ t('media.tabImages') }}</h4>
          <div class="media-group-toolbar">
            <button type="button" class="media-select-all-btn" @click="toggleGroupSelection('image')">{{ isGroupFullySelected('image') ? t('media.deselectAll') : t('media.selectAll') }}</button>
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
            <div class="media-card-thumb-wrap">
              <img
                v-if="!imageLoadErrorIds.has(item.id)"
                class="media-card-thumb"
                :src="fullUrl(item.url)"
                :alt="item.original_name"
                @error="markImageLoadError(item.id)"
              />
              <div v-else class="media-card-thumb-fallback">
                <span>{{ t('media.previewFailed') }}</span>
              </div>
            </div>
            <div class="media-card-body">
              <p class="media-card-title">{{ item.original_name }}</p>
              <small class="media-card-meta">{{ item.mime_type || 'IMAGE' }}</small>
            </div>
          </button>
        </div>
        <p v-else class="tips media-empty">{{ t('media.noImages') }}</p>
      </div>

      <!-- Audio -->
      <div v-show="activeTab === 'audio'" class="media-group-panel">
        <div class="media-group-head">
          <h4>{{ t('media.tabAudio') }}</h4>
          <div class="media-group-toolbar">
            <button type="button" class="media-select-all-btn" @click="toggleGroupSelection('audio')">{{ isGroupFullySelected('audio') ? t('media.deselectAll') : t('media.selectAll') }}</button>
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
                <button type="button" class="media-copy-btn" @click="copyUrl(item.url, item.original_name)">{{ t('common.copyLink') }}</button>
              </div>
            </div>
          </article>
        </div>
        <p v-else class="tips media-empty">{{ t('media.noAudio') }}</p>
      </div>

      <!-- Video -->
      <div v-show="activeTab === 'video'" class="media-group-panel">
        <div class="media-group-head">
          <h4>{{ t('media.tabVideo') }}</h4>
          <div class="media-group-toolbar">
            <button type="button" class="media-select-all-btn" @click="toggleGroupSelection('video')">{{ isGroupFullySelected('video') ? t('media.deselectAll') : t('media.selectAll') }}</button>
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
                <button type="button" class="media-copy-btn" @click="copyUrl(item.url, item.original_name)">{{ t('common.copyLink') }}</button>
              </div>
            </div>
          </article>
        </div>
        <p v-else class="tips media-empty">{{ t('media.noVideo') }}</p>
      </div>
    </div>

    <teleport to="body">
      <transition name="media-delete-fade">
        <div v-if="deleteConfirmOpen" class="media-delete-overlay" @click.self="closeDeleteConfirm">
          <div class="media-delete-modal" role="dialog" aria-modal="true" aria-labelledby="media-delete-title">
            <div class="media-delete-head">
              <span class="media-delete-icon">!</span>
              <div>
                <h4 id="media-delete-title">{{ t('media.deleteTitle') }}</h4>
                <p class="media-delete-subtitle">{{ t('media.deleteSubtitle') }}</p>
              </div>
            </div>
            <div class="media-delete-body">
              <p class="media-delete-text">{{ t('media.deleteConfirm', { n: deleteTargetIds.length }) }}</p>
              <div class="media-delete-preview-list">
                <span v-for="item in deleteTargetNames" :key="item" class="media-delete-preview-item">{{ item }}</span>
              </div>
            </div>
            <div class="media-delete-actions">
              <button type="button" class="media-delete-cancel" @click="closeDeleteConfirm">{{ t('common.cancel') }}</button>
              <button type="button" class="media-delete-confirm" @click="submitDeleteConfirm">{{ t('common.delete') }}</button>
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
              <img v-if="!imagePreviewError" class="media-preview-image" :src="fullUrl(previewItem.url)" :alt="previewItem.original_name" @error="markPreviewLoadError" />
              <div v-else class="media-preview-image-fallback">
                <span>{{ t('media.imageLoadFailed') }}</span>
              </div>
            </div>
            <div class="media-preview-info">
              <div class="media-preview-head">
                <h4 id="media-preview-title">{{ t('media.detailTitle') }}</h4>
                <button type="button" class="media-preview-close" @click="closePreview">{{ t('common.close') }}</button>
              </div>
              <div class="media-preview-meta-list">
                <div class="media-preview-meta-item"><span>{{ t('time.uploadTime') }}</span><strong>{{ formatDate(previewItem.uploaded_at || previewItem.created_at) }}</strong></div>
                <div class="media-preview-meta-item"><span>{{ t('media.uploader') }}</span><strong>{{ previewItem.uploader?.nickname || previewItem.user?.nickname || previewItem.author?.nickname || 'admin' }}</strong></div>
                <div class="media-preview-meta-item"><span>{{ t('media.fileName') }}</span><strong>{{ previewItem.original_name }}</strong></div>
                <div class="media-preview-meta-item"><span>{{ t('media.fileType') }}</span><strong>{{ previewItem.mime_type || t('common.unknown') }}</strong></div>
                <div class="media-preview-meta-item"><span>{{ t('media.fileSize') }}</span><strong>{{ formatFileSize(previewItem.file_size || previewItem.size) }}</strong></div>
                <div class="media-preview-meta-item"><span>{{ t('media.resolution') }}</span><strong>{{ formatResolution(previewItem.width, previewItem.height) }}</strong></div>
                <div class="media-preview-meta-item media-preview-url"><span>{{ t('media.fileUrl') }}</span><strong>{{ fullUrl(previewItem.url) }}</strong></div>
              </div>
              <div class="media-preview-actions">
                <button type="button" class="media-copy-btn" @click="copyUrl(previewItem.url, previewItem.original_name)">{{ t('common.copyLink') }}</button>
                <button type="button" class="danger-btn media-preview-delete" @click="$emit('delete-media', previewItem.id)">{{ t('common.delete') }}</button>
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
import { useI18n } from 'vue-i18n'
import { toAbsoluteAssetUrl } from '../api'

const { t, locale } = useI18n()

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
const imageLoadErrorIds = ref<Set<number>>(new Set())
const imagePreviewError = ref(false)
const selectedIds = ref<Set<number>>(new Set())
const deleteConfirmOpen = ref(false)
const deleteTargetIds = ref<number[]>([])
const deleteTargetNames = ref<string[]>([])
const activeTab = ref('image')

const tabIcons = {
  image: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>',
  audio: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>',
  video: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>',
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

const tabs = computed(() => [
  { key: 'image', label: t('media.tabImages'), icon: tabIcons.image, count: grouped.value.image.length },
  { key: 'audio', label: t('media.tabAudio'), icon: tabIcons.audio, count: grouped.value.audio.length },
  { key: 'video', label: t('media.tabVideo'), icon: tabIcons.video, count: grouped.value.video.length },
])

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

const fullUrl = (url: string) => toAbsoluteAssetUrl(url)

const copyUrl = async (url: string, fileName: string) => {
  await navigator.clipboard.writeText(fullUrl(url))
  copyMessage.value = t('media.copySuccess', { name: fileName })
  setTimeout(() => {
    copyMessage.value = ''
  }, 1800)
}

const openPreview = (item: any) => {
  previewItem.value = item
  imagePreviewError.value = false
}

const markImageLoadError = (id: number) => {
  const next = new Set(imageLoadErrorIds.value)
  next.add(id)
  imageLoadErrorIds.value = next
}

const markPreviewLoadError = () => {
  imagePreviewError.value = true
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
  if (!text) return t('common.unknown')
  const date = new Date(text)
  if (Number.isNaN(date.getTime())) return text
  return date.toLocaleString(locale.value)
}

const formatFileSize = (value?: number) => {
  const size = Number(value || 0)
  if (!size) return t('common.unknown')
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  if (size < 1024 * 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  return `${(size / 1024 / 1024 / 1024).toFixed(1)} GB`
}

const formatResolution = (width?: number, height?: number) => {
  const w = Number(width || 0)
  const h = Number(height || 0)
  if (!w || !h) return t('common.unknown')
  return `${w} × ${h} px`
}
</script>

<style scoped>
.media-card-thumb-wrap {
  width: 100%;
  aspect-ratio: 4 / 3;
  border-radius: 12px;
  overflow: hidden;
  background: var(--bg-soft);
}

.media-card-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.media-card-thumb-fallback {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  color: var(--text-soft);
  font-size: 12px;
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.12), rgba(14, 165, 164, 0.08));
}

.media-preview-image,
.media-preview-image-fallback {
  max-width: 100%;
  max-height: 62vh;
  border-radius: 16px;
}

.media-preview-image {
  object-fit: contain;
}

.media-preview-image-fallback {
  width: 100%;
  min-height: 240px;
  display: grid;
  place-items: center;
  color: var(--text-soft);
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.12), rgba(14, 165, 164, 0.08));
}
</style>
