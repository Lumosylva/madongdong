<template>
  <router-view />
  <button v-show="showScrollTop" class="scroll-top-btn" type="button" aria-label="回到顶部" @click="scrollToTop">
    ↑
  </button>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const scrollTop = ref(0)
const showScrollTop = computed(() => scrollTop.value > 320)

const updateScrollTop = () => {
  scrollTop.value = window.scrollY || document.documentElement.scrollTop || 0
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  updateScrollTop()
  window.addEventListener('scroll', updateScrollTop, { passive: true })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', updateScrollTop)
})
</script>
