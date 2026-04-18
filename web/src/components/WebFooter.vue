<template>
  <footer class="footer">
    <span>{{ copyrightText || '© MaDongDong Blog' }}</span>
    <span v-html="icpBeian || '备案信息待配置'"></span>
  </footer>
</template>

<script setup lang="ts">
defineProps<{
  icpBeian?: string | null
  copyrightText?: string | null
}>()
</script>
