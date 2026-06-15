<template>
  <section class="editor-panel article-create-panel">
    <div class="article-create-head">
      <div>
        <h3>{{ editorTitle || (editorMode === 'edit' ? t('articleCreate.editTitle') : t('articleCreate.createTitle')) }}</h3>
      </div>
      <span class="article-create-meta">{{ t('articleCreate.summaryHint') }}</span>
    </div>
    <p v-if="submitError" class="article-create-error" :class="{ 'is-focus': submitFocusField }">{{ submitError }}</p>
    <div class="article-create-help-row">
      <span v-if="draftSessionSaved && draftSavedAt" class="article-create-save-time">{{ t('articleCreate.savedAt') }} {{ formatSavedTime(draftSavedAt) }}</span>
      <p class="article-create-shortcuts-hint">{{ t('articleCreate.shortcutsHint') }}</p>
    </div>

    <div class="article-create-field">
      <label for="article-title-input">{{ t('articleCreate.titleLabel') }}</label>
      <input
        id="article-title-input"
        ref="titleInputRef"
        :value="title"
        :placeholder="t('articleCreate.titlePlaceholder')"
        @input="emit('update:title', ($event.target as HTMLInputElement).value)"
      />
    </div>

    <div class="article-create-field article-markdown-field">
      <div class="article-markdown-toolbar article-markdown-toolbar-title">
        <div class="article-markdown-toolbar-main">
          <label for="article-content-input">{{ t('articleCreate.contentLabel') }}</label>
        </div>
        <button type="button" class="video-insert-btn" @click="openVideoModal">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
          {{ t('articleCreate.insertVideo') }}
        </button>
      </div>

      <div ref="markdownWorkspaceRef" class="article-markdown-workspace">
        <MdEditor
          ref="mdEditorRef"
          v-model="contentMarkdownLocal"
          :style="{ height: '640px' }"
          :theme="editorTheme"
          :preview-theme="previewTheme"
          :toolbars-exclude="toolbarsExclude"
          :show-toolbar-name="showToolbarName"
          :editor-id="editorId"
          :scroll-element="scrollElement"
          :markdown-it-config="markdownItConfig"
          @on-upload-img="handleUploadImg"
        />
      </div>
    </div>

    <input
      ref="videoFileInputRef"
      type="file"
      accept="video/mp4,video/webm,video/ogg"
      style="display: none"
      @change="onVideoFileSelect"
    />

    <transition name="video-modal-fade">
      <div v-if="videoModalOpen" class="video-modal-mask" @click.self="closeVideoModal"></div>
    </transition>
    <transition name="video-modal-slide">
      <div v-if="videoModalOpen" class="video-modal-panel">
        <div class="video-modal-header">
          <h4>{{ t('articleCreate.insertVideo') }}</h4>
          <button type="button" class="video-modal-close" @click="closeVideoModal">&times;</button>
        </div>
        <div class="video-modal-tabs">
          <button
            type="button"
            class="video-tab"
            :class="{ active: videoModalTab === 'upload' }"
            @click="videoModalTab = 'upload'"
          >{{ t('articleCreate.uploadVideo') }}</button>
          <button
            type="button"
            class="video-tab"
            :class="{ active: videoModalTab === 'embed' }"
            @click="videoModalTab = 'embed'"
          >{{ t('articleCreate.embedVideo') }}</button>
        </div>
        <div class="video-modal-body">
          <div v-if="videoModalTab === 'upload'" class="video-upload-area">
            <p class="video-upload-hint">{{ t('articleCreate.uploadVideoHint') }}</p>
            <button type="button" class="video-upload-btn" :disabled="videoUploading" @click="videoFileInputRef?.click()">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
              {{ videoUploading ? t('articleCreate.uploadingVideo') : t('articleCreate.uploadVideo') }}
            </button>
          </div>
          <div v-else class="video-embed-area">
            <p class="video-embed-hint">{{ t('articleCreate.embedVideoHint') }}</p>
            <textarea
              v-model="embedVideoUrl"
              class="video-embed-input"
              :placeholder="t('articleCreate.embedVideoPlaceholder')"
              rows="4"
            ></textarea>
            <button type="button" class="video-embed-insert-btn" :disabled="!embedVideoUrl.trim()" @click="insertEmbedVideo">
              {{ t('articleCreate.insertVideoConfirm') }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <div class="article-create-field">
      <label for="article-cover-url-input">{{ t('articleCreate.coverLabel') }}</label>
      <div class="article-cover-combo">
        <div class="article-cover-row">
          <input
            id="article-cover-url-input"
            :value="coverUrl"
            :placeholder="t('articleCreate.coverPlaceholder')"
            @input="emit('update:coverUrl', ($event.target as HTMLInputElement).value)"
          />
          <button type="button" class="article-cover-pick-btn" @click="showCoverPicker = !showCoverPicker">{{ t('articleCreate.pickFromMedia') }}</button>
        </div>
        <p class="article-create-hint">{{ t('articleCreate.coverHint') }}</p>
        <transition name="cover-picker-fade">
          <div v-if="showCoverPicker" class="article-cover-picker">
            <button
              v-for="item in imageMedia"
              :key="item.id"
              type="button"
              class="article-cover-thumb"
              :class="{ selected: item.url === coverUrl }"
              @click="selectCover(item.url)"
            >
              <img :src="previewUrl(item.url)" :alt="item.original_name" />
              <span>{{ item.original_name }}</span>
            </button>
            <p v-if="!imageMedia.length" class="article-create-hint">{{ t('articleCreate.noImages') }}</p>
          </div>
        </transition>
      </div>
    </div>

    <div class="article-create-field">
      <label for="article-category-select">{{ t('articleCreate.categoryLabel') }}</label>
      <select
        id="article-category-select"
        :value="categoryId"
        @input="emit('update:categoryId', Number(($event.target as HTMLSelectElement).value))"
      >
        <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
      </select>
    </div>

    <div class="article-create-field">
      <label for="article-tags-input">{{ t('articleCreate.tagLabel') }}</label>
      <input
        id="article-tags-input"
        :value="tagIdsText"
        :placeholder="t('articleCreate.tagPlaceholder')"
        @input="emit('update:tagIdsText', ($event.target as HTMLInputElement).value)"
      />
    </div>

    <div class="article-create-field">
      <label for="article-action-select">{{ t('articleCreate.statusLabel') }}</label>
      <select
        id="article-action-select"
        :value="action"
        @input="emit('update:action', ($event.target as HTMLSelectElement).value as 'draft' | 'submit' | 'publish')"
      >
        <option value="draft">{{ t('articleCreate.saveDraft') }}</option>
        <option value="submit">{{ t('articleCreate.submitReview') }}</option>
        <option v-if="isAdmin" value="publish">{{ t('articleCreate.publishDirect') }}</option>
      </select>
    </div>

    <div class="article-create-actions">
      <button type="button" class="article-create-submit" :disabled="submitLoading" @click="triggerSubmit">
        {{ submitLoading ? t('articleCreate.submitting') : (editorMode === 'edit' ? t('articleCreate.saveChanges') : t('articleCreate.submitArticle')) }}
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { MdEditor, type ToolbarNames } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import 'md-editor-v3/lib/preview.css'

import { adminApi, API_ORIGIN } from '../api'

const { t, locale } = useI18n()

const props = defineProps<{
  isAdmin: boolean
  title: string
  coverUrl: string
  contentMarkdown: string
  categoryId: number
  categories: Array<{ id: number; name: string }>
  tagIdsText: string
  action: 'draft' | 'submit' | 'publish'
  media: Array<{ id: number; url: string; original_name: string; media_type?: string; mime_type?: string }>
  showToolbarName?: boolean
  submitLoading?: boolean
  draftSavedAt?: number | null
  draftSessionSaved?: boolean
  submitError?: string
  submitFocusField?: 'title' | 'content' | null
  editorMode?: 'create' | 'edit'
  editorTitle?: string
}>()

const emit = defineEmits<{
  'update:title': [value: string]
  'update:coverUrl': [value: string]
  'update:contentMarkdown': [value: string]
  'update:categoryId': [value: number]
  'update:tagIdsText': [value: string]
  'update:action': [value: 'draft' | 'submit' | 'publish']
  submit: []
}>()

const showCoverPicker = ref(false)
const editorTheme = ref<'light' | 'dark'>('light')
const previewTheme = ref<'default' | 'github'>('github')
const editorId = 'article-create-md-editor'
const scrollElement = '.article-markdown-preview'
const toolbarsExclude: ToolbarNames[] = ['save', 'htmlPreview', 'catalog', 'pageFullscreen']
const mdEditorRef = ref<InstanceType<typeof MdEditor> | null>(null)

const syncEditorTheme = () => {
  editorTheme.value = document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light'
}

onMounted(() => {
  syncEditorTheme()
})

const themeObserver = new MutationObserver(syncEditorTheme)
themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })

onBeforeUnmount(() => {
  themeObserver.disconnect()
})

const titleInputRef = ref<HTMLInputElement | null>(null)
const videoFileInputRef = ref<HTMLInputElement | null>(null)
const videoModalOpen = ref(false)
const videoModalTab = ref<'upload' | 'embed'>('upload')
const videoUploading = ref(false)
const embedVideoUrl = ref('')

const focusFirstMissingField = async (missingField?: 'title' | 'content') => {
  await nextTick()
  if (missingField === 'title') {
    titleInputRef.value?.focus()
  }
}

const triggerSubmit = async () => {
  emit('submit')
}

watch(
  () => props.submitFocusField,
  async (field) => {
    if (!field) return
    await focusFirstMissingField(field)
  },
)

const contentMarkdownLocal = computed({
  get: () => props.contentMarkdown,
  set: (value: string) => emit('update:contentMarkdown', value),
})

const imageMedia = computed(() =>
  props.media.filter(
    (item) => String(item.media_type || '').toUpperCase() === 'IMAGE' || String(item.mime_type || '').toLowerCase() === 'image/svg+xml',
  ),
)

const formatSavedTime = (timestamp: number) => {
  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleTimeString(locale.value, { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const previewUrl = (url: string) => fullUrl(url)

const fullUrl = (url: string) => {
  const value = String(url || '').trim()
  if (!value) return ''
  if (/^https?:\/\//i.test(value)) return value
  return `${API_ORIGIN}${value.startsWith('/') ? '' : '/'}${value}`
}

const selectCover = (url: string) => {
  emit('update:coverUrl', fullUrl(url))
  showCoverPicker.value = false
}

const handleUploadImg = async (files: File[], callback: (urls: string[]) => void) => {
  const urls: string[] = []
  for (const file of files) {
    try {
      const res = await adminApi.uploadMediaFile(file)
      urls.push(fullUrl(res.data?.url || ''))
    } catch {
      urls.push('')
    }
  }
  callback(urls)
}

const openVideoModal = () => {
  videoModalOpen.value = true
  videoModalTab.value = 'upload'
  embedVideoUrl.value = ''
}

const closeVideoModal = () => {
  videoModalOpen.value = false
  videoUploading.value = false
}

const insertAtCursor = (html: string) => {
  const editor = mdEditorRef.value as any
  if (editor && typeof editor.insert === 'function') {
    editor.insert(() => ({ targetValue: html }))
  } else {
    const current = contentMarkdownLocal.value
    contentMarkdownLocal.value = current + '\n' + html + '\n'
  }
}

const markdownItConfig = (md: any) => {
  md.options.html = true
}

const onVideoFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  videoUploading.value = true
  try {
    const res = await adminApi.uploadMediaFile(file)
    const url = fullUrl(res.data?.url || '')
    const html = `<video controls width="100%" preload="metadata">\n  <source src="${url}" type="${file.type}">\n</video>`
    insertAtCursor(html)
    closeVideoModal()
  } catch {
    // ignore
  } finally {
    videoUploading.value = false
    target.value = ''
  }
}

const parseVideoEmbed = (input: string): string => {
  const trimmed = input.trim()

  if (trimmed.startsWith('<iframe') || trimmed.startsWith('<video')) {
    return trimmed
  }

  const youtubeMatch = trimmed.match(/(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/)
  if (youtubeMatch) {
    return `<iframe width="100%" height="400" src="https://www.youtube.com/embed/${youtubeMatch[1]}" frameborder="0" allowfullscreen></iframe>`
  }

  const bilibiliMatch = trimmed.match(/bilibili\.com\/video\/(BV[a-zA-Z0-9]+)/)
  if (bilibiliMatch) {
    return `<iframe width="100%" height="400" src="https://player.bilibili.com/player.html?bvid=${bilibiliMatch[1]}" frameborder="0" allowfullscreen></iframe>`
  }

  return `<iframe width="100%" height="400" src="${trimmed}" frameborder="0" allowfullscreen></iframe>`
}

const insertEmbedVideo = () => {
  if (!embedVideoUrl.value.trim()) return
  const html = parseVideoEmbed(embedVideoUrl.value)
  insertAtCursor(html)
  closeVideoModal()
}

watch(
  () => props.coverUrl,
  (value) => {
    if (value) showCoverPicker.value = false
  },
)
</script>
