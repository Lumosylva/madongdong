<template>
  <section class="panel">
    <h3>垃圾箱</h3>
    <p class="tips" v-if="deletedArticles.length === 0">垃圾箱为空</p>
    <ul v-else>
      <li v-for="item in deletedArticles" :key="item.id" class="article-row">
        <span>{{ item.title }}</span>
        <div class="row-actions">
          <button @click="$emit('restore', item.id)">恢复</button>
          <button class="danger-btn" @click="$emit('remove-permanently', item.id)">彻底删除</button>
        </div>
      </li>
    </ul>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  deletedArticles: any[]
}>()

defineEmits<{
  restore: [articleId: number]
  'remove-permanently': [articleId: number]
}>()
</script>
