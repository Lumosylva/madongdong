<template>
  <section class="panel">
    <h3>媒体管理</h3>
    <ul>
      <li v-for="item in media" :key="item.id">{{ item.original_name }} · {{ item.media_type }}</li>
    </ul>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  media: any[]
}>()
</script>
