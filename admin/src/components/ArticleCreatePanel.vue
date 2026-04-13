<template>
  <section class="editor-panel">
    <h3>创建文章</h3>
    <input :value="title" placeholder="标题" @input="$emit('update:title', ($event.target as HTMLInputElement).value)" />
    <p class="tips">摘要将自动提取正文开头 120 个字符</p>
    <input :value="coverUrl" placeholder="封面图 URL" @input="$emit('update:coverUrl', ($event.target as HTMLInputElement).value)" />
    <textarea
      :value="contentMarkdown"
      placeholder="Markdown 正文"
      @input="$emit('update:contentMarkdown', ($event.target as HTMLTextAreaElement).value)"
    ></textarea>
    <div class="action-row">
      <select :value="categoryId" @change="$emit('update:categoryId', Number(($event.target as HTMLSelectElement).value))">
        <option v-for="item in categories" :key="item.id" :value="item.id">{{ item.name }}</option>
      </select>
      <input
        :value="tagIdsText"
        placeholder="标签（英文逗号分隔，例如：Python, FastAPI）"
        @input="$emit('update:tagIdsText', ($event.target as HTMLInputElement).value)"
      />
      <select :value="action" @change="$emit('update:action', ($event.target as HTMLSelectElement).value as 'draft' | 'submit' | 'publish')">
        <option value="draft">保存草稿</option>
        <option v-if="!isAdmin" value="submit">提交审核</option>
        <option v-if="isAdmin" value="publish">直接发布</option>
      </select>
      <button @click="$emit('submit')">提交</button>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  isAdmin: boolean
  title: string
  coverUrl: string
  contentMarkdown: string
  categoryId: number
  categories: Array<{ id: number; name: string }>
  tagIdsText: string
  action: 'draft' | 'submit' | 'publish'
}>()

defineEmits<{
  'update:title': [value: string]
  'update:coverUrl': [value: string]
  'update:contentMarkdown': [value: string]
  'update:categoryId': [value: number]
  'update:tagIdsText': [value: string]
  'update:action': [value: 'draft' | 'submit' | 'publish']
  submit: []
}>()
</script>
