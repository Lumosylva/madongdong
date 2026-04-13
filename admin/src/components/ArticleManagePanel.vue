<template>
  <section class="panel">
    <h3>文章管理</h3>
    <ul>
      <li v-for="item in articles" :key="item.id" class="article-row">
        <span>{{ item.title }} · {{ formatArticleStatus(item.status) }}</span>
        <button class="danger-btn" @click="$emit('move-to-trash', item.id)">删除</button>
      </li>
    </ul>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  articles: any[]
  formatArticleStatus: (status: string) => string
}>()

defineEmits<{
  'move-to-trash': [articleId: number]
}>()
</script>
