<template>
  <footer class="footer">
    <span v-html="icpBeian || '页脚信息待配置'"></span>
  </footer>
</template>

<script setup lang="ts">
defineProps<{
  icpBeian?: string | null
}>()
</script>
