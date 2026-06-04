<template>
  <router-view />
  <transition name="scroll-top-fade">
    <button v-if="showScrollTop" class="scroll-top-btn" type="button" aria-label="回到顶部" @click="scrollToTop">
      <svg viewBox="0 0 24 24" class="scroll-top-icon" aria-hidden="true" focusable="false">
        <path d="M12 5.5c.4 0 .75.14 1.03.42l5.78 5.78a1.5 1.5 0 1 1-2.12 2.12L13.5 10.63V18a1.5 1.5 0 0 1-3 0v-7.37l-3.19 3.19a1.5 1.5 0 0 1-2.12-2.12l5.78-5.78c.28-.28.63-.42 1.03-.42Z" />
      </svg>
    </button>
  </transition>
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
