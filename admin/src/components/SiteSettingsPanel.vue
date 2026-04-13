<template>
  <section class="panel">
    <h3>站点设置</h3>
    <input :value="siteTitle" placeholder="网站标题" @input="$emit('update:siteTitle', ($event.target as HTMLInputElement).value)" />
    <input :value="siteSubtitle" placeholder="副标题" @input="$emit('update:siteSubtitle', ($event.target as HTMLInputElement).value)" />
    <input :value="icpBeian" placeholder="备案信息" @input="$emit('update:icpBeian', ($event.target as HTMLInputElement).value)" />
    <input :value="copyrightText" placeholder="版权信息" @input="$emit('update:copyrightText', ($event.target as HTMLInputElement).value)" />
    <button @click="$emit('save')">保存设置</button>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  siteTitle: string
  siteSubtitle: string
  icpBeian: string
  copyrightText: string
}>()

defineEmits<{
  'update:siteTitle': [value: string]
  'update:siteSubtitle': [value: string]
  'update:icpBeian': [value: string]
  'update:copyrightText': [value: string]
  save: []
}>()
</script>
