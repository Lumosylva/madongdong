<template>
  <div class="admin-page">
    <section class="panel md-editor-probe-page">
      <div class="section-head md-editor-probe-head">
        <div>
          <h2>MdEditorV3 试验页</h2>
          <p class="article-create-hint">
            用于验证编辑绑定、分栏预览、滚动同步、图片插入和预览样式接管。
          </p>
        </div>
        <div class="md-editor-probe-meta">
          <span>{{ contentLength }} 字</span>
          <span>{{ syncStatus }}</span>
        </div>
      </div>

      <div class="md-editor-probe-toolbar">
        <button type="button" @click="loadSample">加载示例</button>
        <button type="button" @click="clearContent">清空</button>
        <button type="button" @click="appendContent">追加一段</button>
      </div>

      <div class="md-editor-probe-layout">
        <div class="md-editor-probe-editor">
          <MdEditor
            v-model="content"
            :style="{ height: '640px' }"
            :theme="theme"
            :preview-theme="previewTheme"
            :toolbars-exclude="toolbarsExclude"
            :show-toolbar-name="true"
            :scroll-element="scrollElement"
            @on-upload-img="handleUploadImg"
            @on-change="handleChange"
          />
        </div>

        <aside class="md-editor-probe-preview">
          <div class="md-editor-probe-preview-head">
            <span>预览</span>
            <button type="button" @click="toggleTheme">切换主题</button>
          </div>
          <MdPreview
            :model-value="content"
            :theme="theme"
            :preview-theme="previewTheme"
            :scroll-element="scrollElement"
            class="md-editor-probe-preview-body"
          />
        </aside>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { MdEditor, MdPreview, type ToolbarNames } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import 'md-editor-v3/lib/preview.css'

const theme = ref<'light' | 'dark'>('light')
const previewTheme = ref<'default' | 'github'>('github')
const content = ref(`# MdEditorV3 试验页\n\n这是一个用于验证分栏编辑能力的试验页。\n\n## 滚动测试\n\n${Array.from({ length: 60 }, (_, index) => `- 测试段落 ${index + 1}`).join('\n')}\n`)

const scrollElement = '.md-editor-probe-layout'
const syncStatus = ref('待测试')
const toolbarsExclude: ToolbarNames[] = ['save', 'htmlPreview', 'catalog', 'pageFullscreen']

const contentLength = computed(() => content.value.trim().length)

const handleChange = (value: string) => {
  content.value = value
  syncStatus.value = '已同步'
}

const clearContent = () => {
  content.value = ''
  syncStatus.value = '已清空'
}

const loadSample = () => {
  content.value = `# MdEditorV3 示例\n\n- 编辑内容是否正常绑定\n- 分栏是否自然\n- 滚动同步是否稳定\n- 图片插入是否可控\n- 预览样式是否容易接管\n\n> 这是试验页示例内容。\n\n\n${Array.from({ length: 40 }, (_, index) => `\n### 段落 ${index + 1}\n\n这里是用于撑开内容高度的测试文本。`).join('')}`
  syncStatus.value = '已加载示例'
}

const appendContent = () => {
  content.value += `\n\n### 新增段落\n\n用于继续测试滚动同步与预览渲染。`
  syncStatus.value = '已追加'
}

const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}

const handleUploadImg = async (_files: File[], callback: (urls: string[]) => void) => {
  callback(['https://picsum.photos/seed/md-editor-probe/800/400'])
}
</script>
