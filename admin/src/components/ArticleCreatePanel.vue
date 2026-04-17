<template>
  <section class="editor-panel article-create-panel">
    <div class="article-create-head">
      <div>
        <h3>创建文章</h3>
      </div>
      <span class="article-create-meta">正文将自动提取摘要（120 字）</span>
    </div>
    <p v-if="submitError" class="article-create-error" :class="{ 'is-focus': submitFocusField }">{{ submitError }}</p>
    <div class="article-create-help-row">
      <span v-if="draftSessionSaved && draftSavedAt" class="article-create-save-time">已临时保存 · {{ formatSavedTime(draftSavedAt) }}</span>
      <p class="article-create-shortcuts-hint">快捷键：Ctrl/Cmd + S 临时保存，Ctrl/Cmd + Enter 提交</p>
    </div>

    <div class="article-create-field">
      <label for="article-title-input">标题</label>
      <input
        id="article-title-input"
        ref="titleInputRef"
        :value="title"
        placeholder="请输入文章标题"
        @input="emit('update:title', ($event.target as HTMLInputElement).value)"
      />
    </div>

    <div class="article-create-field article-markdown-field">
      <div class="article-markdown-toolbar article-markdown-toolbar-title">
        <div class="article-markdown-toolbar-main">
          <label for="article-content-input">正文</label>
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
      <label for="article-cover-url-input">封面图</label>
      <div class="article-cover-combo">
        <div class="article-cover-row">
          <input
            id="article-cover-url-input"
            :value="coverUrl"
            placeholder="封面图 URL（可选）"
            @input="emit('update:coverUrl', ($event.target as HTMLInputElement).value)"
          />
          <button type="button" class="article-cover-pick-btn" @click="showCoverPicker = !showCoverPicker">从媒体库选择</button>
        </div>
        <p class="article-create-hint">从媒体库选择图片后会自动填入封面地址</p>
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
            <p v-if="!imageMedia.length" class="article-create-hint">暂无可用图片，请先到媒体库上传图片。</p>
          </div>
        </transition>
      </div>
    </div>

    <div class="article-create-actions">
      <div class="article-create-actions-grid">
        <div class="article-create-field article-create-select-field">
          <label for="article-category-select">分类</label>
          <select id="article-category-select" :value="categoryId" @change="emit('update:categoryId', Number(($event.target as HTMLSelectElement).value))">
            <option v-for="item in categories" :key="item.id" :value="item.id">{{ item.name }}</option>
          </select>
        </div>
        <div class="article-create-field article-create-tag-field">
          <label for="article-tags-input">标签</label>
          <input
            id="article-tags-input"
            :value="tagIdsText"
            placeholder="标签（英文逗号分隔，例如：Python, FastAPI）"
            @input="emit('update:tagIdsText', ($event.target as HTMLInputElement).value)"
          />
        </div>
        <div class="article-create-field article-create-status-field">
          <label for="article-action-select">发布状态</label>
          <select id="article-action-select" :value="action" @change="emit('update:action', ($event.target as HTMLSelectElement).value as 'draft' | 'submit' | 'publish')">
            <option value="draft">保存草稿</option>
            <option v-if="!isAdmin" value="submit">提交审核</option>
            <option v-if="isAdmin" value="publish">直接发布</option>
          </select>
        </div>
      </div>
      <button class="article-create-submit" :disabled="submitLoading" @click="triggerSubmit">{{ submitLoading ? '提交中...' : '提交' }}</button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { MdEditor, type ToolbarNames } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import 'md-editor-v3/lib/preview.css'

import { API_ORIGIN } from '../api'

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

onBeforeUnmount(() => {
  // no-op placeholder for future cleanup hooks
})

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
