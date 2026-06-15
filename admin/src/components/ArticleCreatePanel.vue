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
      </div>

      <div ref="markdownWorkspaceRef" class="article-markdown-workspace">
        <MdEditor
          v-model="contentMarkdownLocal"
          :style="{ height: '640px' }"
          :theme="editorTheme"
          :preview-theme="previewTheme"
          :toolbars-exclude="toolbarsExclude"
          :show-toolbar-name="showToolbarName"
          :editor-id="editorId"
          :scroll-element="scrollElement"
          @on-upload-img="handleUploadImg"
        />
      </div>
    </div>

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

    <div class="article-create-actions">
      <div class="article-create-actions-grid">
        <div class="article-create-field article-create-select-field">
          <label for="article-category-select">{{ t('articleCreate.categoryLabel') }}</label>
          <select id="article-category-select" :value="categoryId" @change="emit('update:categoryId', Number(($event.target as HTMLSelectElement).value))">
            <option v-for="item in categories" :key="item.id" :value="item.id">{{ item.name }}</option>
          </select>
        </div>
        <div class="article-create-field article-create-tag-field">
          <label for="article-tags-input">{{ t('articleCreate.tagLabel') }}</label>
          <input
            id="article-tags-input"
            :value="tagIdsText"
            :placeholder="t('articleCreate.tagPlaceholder')"
            @input="emit('update:tagIdsText', ($event.target as HTMLInputElement).value)"
          />
        </div>
        <div class="article-create-field article-create-status-field">
          <label for="article-action-select">{{ t('articleCreate.statusLabel') }}</label>
          <select id="article-action-select" :value="action" @change="emit('update:action', ($event.target as HTMLSelectElement).value as 'draft' | 'submit' | 'publish')">
            <option value="draft">{{ t('articleCreate.saveDraft') }}</option>
            <option v-if="!isAdmin" value="submit">{{ t('articleCreate.submitReview') }}</option>
            <option v-if="isAdmin" value="publish">{{ t('articleCreate.publishDirect') }}</option>
          </select>
        </div>
      </div>
      <button class="article-create-submit" :disabled="submitLoading" @click="triggerSubmit">{{ submitLoading ? t('articleCreate.submitting') : (editorMode === 'edit' ? t('articleCreate.saveChanges') : t('articleCreate.submitArticle')) }}</button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { MdEditor, type ToolbarNames } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import 'md-editor-v3/lib/preview.css'

import { API_ORIGIN } from '../api'

const { t } = useI18n()

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
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
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

const handleUploadImg = async (_files: File[], callback: (urls: string[]) => void) => {
  callback(['https://picsum.photos/seed/md-editor-probe/800/400'])
}

watch(
  () => props.coverUrl,
  (value) => {
    if (value) showCoverPicker.value = false
  },
)
</script>
