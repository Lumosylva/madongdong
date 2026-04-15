<template>
  <section class="editor-panel article-create-panel">
    <div class="article-create-head">
      <div>
        <h3>创建文章</h3>
        <span class="article-create-meta">Markdown 编辑器</span>
      </div>
      <span class="article-create-meta">正文将自动提取摘要（120 字）</span>
    </div>

    <div class="article-create-field">
      <label>标题</label>
      <input :value="title" placeholder="请输入文章标题" @input="emit('update:title', ($event.target as HTMLInputElement).value)" />
    </div>

    <div class="article-create-field">
      <label>封面图</label>
      <div class="article-cover-row">
        <input :value="coverUrl" placeholder="封面图 URL（可选）" @input="emit('update:coverUrl', ($event.target as HTMLInputElement).value)" />
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

    <div ref="markdownPanelRef" class="article-create-field article-markdown-field">
      <div class="article-markdown-toolbar article-markdown-toolbar-title">
        <div class="article-markdown-toolbar-main">
          <label>正文（Markdown）</label>
          <p class="article-markdown-tip">支持标题、列表、引用、代码块、链接、图片和表格</p>
        </div>
        <div class="article-markdown-count">{{ contentLength }} 字</div>
      </div>
      <div class="article-markdown-toolbar article-markdown-toolbar-actions">
        <div ref="toolbarWrapRef" class="article-markdown-mode-switch" role="tablist" aria-label="正文预览模式">
          <button type="button" :class="['article-markdown-mode-btn', { active: previewMode === 'edit' }]" @click="previewMode = 'edit'">编辑</button>
          <button type="button" :class="['article-markdown-mode-btn', { active: previewMode === 'split' }]" @click="previewMode = 'split'">分栏预览</button>
          <button type="button" :class="['article-markdown-mode-btn', { active: previewMode === 'preview' }]" @click="previewMode = 'preview'">实时预览</button>
          <button type="button" class="article-markdown-clear" @click="clearContent">清空正文</button>
        </div>
      </div>

      <div :class="['article-markdown-workspace', `mode-${previewMode}`]">
        <div class="article-markdown-editor-wrap">
          <div ref="editorRef" class="article-markdown-editor"></div>
        </div>

        <aside class="article-markdown-preview-panel" aria-label="正文实时预览">
          <div class="article-markdown-preview-head">
            <span>实时预览</span>
            <span class="article-markdown-preview-meta">所见即所得</span>
          </div>
          <article ref="previewScrollRef" class="article-markdown-preview" v-html="previewHtml"></article>
        </aside>
      </div>
    </div>

    <div class="article-create-actions">
      <div class="article-create-actions-grid">
        <select :value="categoryId" @change="emit('update:categoryId', Number(($event.target as HTMLSelectElement).value))">
          <option v-for="item in categories" :key="item.id" :value="item.id">{{ item.name }}</option>
        </select>
        <input
          :value="tagIdsText"
          placeholder="标签（英文逗号分隔，例如：Python, FastAPI）"
          @input="emit('update:tagIdsText', ($event.target as HTMLInputElement).value)"
        />
        <select :value="action" @change="emit('update:action', ($event.target as HTMLSelectElement).value as 'draft' | 'submit' | 'publish')">
          <option value="draft">保存草稿</option>
          <option v-if="!isAdmin" value="submit">提交审核</option>
          <option v-if="isAdmin" value="publish">直接发布</option>
        </select>
      </div>
      <button class="article-create-submit" @click="emit('submit')">提交</button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, onUnmounted, ref, watch } from 'vue'
import Vditor from 'vditor'
import { marked } from 'marked'

import { API_ORIGIN } from '../api'
import '../styles/markdown-editor.css'

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
const previewMode = ref<'edit' | 'split' | 'preview'>('split')
const toolbarWrapRef = ref<HTMLDivElement | null>(null)
const editorRef = ref<HTMLDivElement | null>(null)
const previewScrollRef = ref<HTMLElement | null>(null)
const markdownPanelRef = ref<HTMLElement | null>(null)
const vditor = ref<Vditor | null>(null)
const resizeObserver = ref<ResizeObserver | null>(null)
const imageMedia = computed(() =>
  props.media.filter(
    (item) => String(item.media_type || '').toUpperCase() === 'IMAGE' || String(item.mime_type || '').toLowerCase() === 'image/svg+xml',
  ),
)
const contentLength = computed(() => props.contentMarkdown.trim().length)
const previewHtml = computed(() => marked.parse(props.contentMarkdown || '', { breaks: true }))

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

const syncContent = (value: string) => {
  emit('update:contentMarkdown', value)
}

const clearContent = () => {
  vditor.value?.setValue('')
  syncContent('')
}

const syncPreviewScroll = () => {
  const editorScroll = editorRef.value?.querySelector('.vditor-content') as HTMLElement | null
  const previewScroll = previewScrollRef.value
  if (!editorScroll || !previewScroll) return

  const editorMax = editorScroll.scrollHeight - editorScroll.clientHeight
  if (editorMax <= 0) return

  const ratio = editorScroll.scrollTop / editorMax
  const previewMax = previewScroll.scrollHeight - previewScroll.clientHeight
  previewScroll.scrollTop = previewMax > 0 ? ratio * previewMax : 0
}

const syncEditorHeight = () => {
  const panel = markdownPanelRef.value
  const editorRoot = editorRef.value?.querySelector('.vditor') as HTMLElement | null
  const editorScroll = editorRef.value?.querySelector('.vditor-content') as HTMLElement | null
  const previewPanel = previewScrollRef.value?.closest('.article-markdown-preview-panel') as HTMLElement | null
  const previewBody = previewScrollRef.value
  if (!panel || !editorRoot || !editorScroll || !previewPanel || !previewBody) return

  const availableHeight = Math.max(480, Math.round(panel.getBoundingClientRect().width * 0.72))
  const headerHeight = 44
  const bodyHeight = availableHeight - headerHeight
  editorRoot.style.height = `${availableHeight}px`
  editorScroll.style.height = `${bodyHeight}px`
  previewPanel.style.height = `${availableHeight}px`
  previewBody.style.height = `${bodyHeight}px`
  previewBody.style.maxHeight = `${bodyHeight}px`
}

const updateToolbarWidth = () => {
  void toolbarWrapRef.value?.getBoundingClientRect().width
  syncEditorHeight()
}

const initEditor = async () => {
  if (!editorRef.value || vditor.value) return
  vditor.value = new Vditor(editorRef.value, {
    height: 620,
    mode: 'ir',
    theme: 'classic',
    icon: 'ant',
    cache: { enable: false },
    placeholder: '请在这里输入文章正文，支持 Markdown 语法。',
    value: props.contentMarkdown,
    counter: {
      enable: true,
      type: 'markdown',
    },
    toolbarConfig: {
      pin: true,
    },
    toolbar: [
      'headings',
      'bold',
      'italic',
      'strike',
      '|',
      'line',
      'quote',
      'list',
      'ordered-list',
      'check',
      '|',
      'code',
      'inline-code',
      'table',
      'link',
      'upload',
      '|',
      'undo',
      'redo',
      'fullscreen',
    ],
    input: (value) => syncContent(value),
    after: () => {
      if (vditor.value) {
        vditor.value.setValue(props.contentMarkdown || '')
      }
      const editorScroll = editorRef.value?.querySelector('.vditor-content') as HTMLElement | null
      editorScroll?.addEventListener('scroll', syncPreviewScroll, { passive: true })
      syncEditorHeight()
    },
  })
  await nextTick()
}

watch(
  () => props.contentMarkdown,
  (value) => {
    if (vditor.value && value !== vditor.value.getValue()) {
      vditor.value.setValue(value || '')
    }
  },
)

watch(
  () => props.coverUrl,
  (value) => {
    if (value) {
      showCoverPicker.value = false
    }
  },
)

onMounted(() => {
  initEditor()
  updateToolbarWidth()
  window.addEventListener('resize', updateToolbarWidth)
  resizeObserver.value = new ResizeObserver(() => syncEditorHeight())
  if (markdownPanelRef.value) {
    resizeObserver.value.observe(markdownPanelRef.value)
  }
  syncEditorHeight()
})

onUnmounted(() => {
  window.removeEventListener('resize', updateToolbarWidth)
  resizeObserver.value?.disconnect()
  resizeObserver.value = null
})

onBeforeUnmount(() => {
  const editorScroll = editorRef.value?.querySelector('.vditor-content') as HTMLElement | null
  editorScroll?.removeEventListener('scroll', syncPreviewScroll)
  vditor.value?.destroy()
  vditor.value = null
})
</script>
