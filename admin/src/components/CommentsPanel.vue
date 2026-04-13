<template>
  <section class="panel">
    <h3>评论管理</h3>
    <ul>
      <li v-for="item in comments" :key="item.id">{{ item.content }}</li>
    </ul>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  comments: any[]
}>()
</script>
