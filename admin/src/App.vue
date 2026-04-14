<template>
  <router-view />
  <button v-show="showScrollTop" class="scroll-top-btn" type="button" aria-label="回到顶部" @click="scrollToTop">
    ↑
  </button>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

const scrollTop = ref(0)
const showScrollTop = ref(false)
let hideTimer: number | null = null

const updateScrollTop = () => {
  scrollTop.value = window.scrollY || document.documentElement.scrollTop || 0
  if (scrollTop.value > 320) {
    showScrollTop.value = true
    if (hideTimer) {
      window.clearTimeout(hideTimer)
      hideTimer = null
    }
  } else if (!hideTimer) {
    hideTimer = window.setTimeout(() => {
      showScrollTop.value = false
      hideTimer = null
    }, 220)
  }
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
  if (hideTimer) {
    window.clearTimeout(hideTimer)
    hideTimer = null
  }
})
</script>
