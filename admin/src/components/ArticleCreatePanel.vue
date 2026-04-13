<template>
  <section class="editor-panel">
    <h3>创建文章</h3>
    <input :value="title" placeholder="标题" @input="$emit('update:title', ($event.target as HTMLInputElement).value)" />
    <input :value="summary" placeholder="摘要" @input="$emit('update:summary', ($event.target as HTMLInputElement).value)" />
    <input :value="coverUrl" placeholder="封面图 URL" @input="$emit('update:coverUrl', ($event.target as HTMLInputElement).value)" />
    <textarea
      :value="contentMarkdown"
      placeholder="Markdown 正文"
      @input="$emit('update:contentMarkdown', ($event.target as HTMLTextAreaElement).value)"
    ></textarea>
    <div class="action-row">
      <input
        :value="categoryId"
        type="number"
        placeholder="分类 ID"
        @input="$emit('update:categoryId', Number(($event.target as HTMLInputElement).value || 1))"
      />
      <input
        :value="tagIdsText"
        placeholder="标签 ID，逗号分隔"
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
  summary: string
  coverUrl: string
  contentMarkdown: string
  categoryId: number
  tagIdsText: string
  action: 'draft' | 'submit' | 'publish'
}>()

defineEmits<{
  'update:title': [value: string]
  'update:summary': [value: string]
  'update:coverUrl': [value: string]
  'update:contentMarkdown': [value: string]
  'update:categoryId': [value: number]
  'update:tagIdsText': [value: string]
  'update:action': [value: 'draft' | 'submit' | 'publish']
  submit: []
}>()
</script>
