<template>
  <section class="grid-panels">
    <div class="panel">
      <h3>文章概览</h3>
      <p class="tips">共 {{ articles.length }} 篇文章，垃圾箱 {{ deletedArticles.length }} 篇</p>
      <p v-if="loading" class="tips">正在同步后台数据...</p>
      <p v-else-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <ul>
        <li v-for="item in articles.slice(0, 5)" :key="item.id">{{ item.title }} · {{ formatArticleStatus(item.status) }}</li>
      </ul>
    </div>
    <div class="panel">
      <h3>评论概览</h3>
      <p class="tips">共 {{ comments.length }} 条评论</p>
      <ul>
        <li v-for="item in comments.slice(0, 5)" :key="item.id">{{ item.content }}</li>
      </ul>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  articles: any[]
  deletedArticles: any[]
  comments: any[]
  loading: boolean
  errorMessage: string
  formatArticleStatus: (status: string) => string
}>()
</script>
