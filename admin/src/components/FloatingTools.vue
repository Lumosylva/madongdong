<template>
  <div class="floating-tools" aria-label="页面辅助工具">
    <button
      type="button"
      class="floating-tool-btn theme-switch-btn"
      :aria-label="themeLabel"
      :title="themeLabel"
      @click="$emit('toggle-theme')"
    >
      <svg v-if="theme === 'light'" viewBox="0 0 24 24" class="floating-tool-icon" aria-hidden="true" focusable="false">
        <path d="M12 18a6 6 0 1 1 0-12 6 6 0 0 1 0 12Zm0 2.5a1 1 0 0 1 1 1V23a1 1 0 1 1-2 0v-.5a1 1 0 0 1 1-1ZM12 1a1 1 0 0 1 1 1v1.5a1 1 0 1 1-2 0V2a1 1 0 0 1 1-1Zm9 11a1 1 0 0 1 0 2h-1.5a1 1 0 1 1 0-2H21ZM4.5 12a1 1 0 0 1-1 1H2a1 1 0 1 1 0-2h1.5a1 1 0 0 1 1 1Zm13.44-6.44a1 1 0 0 1 1.41 0l1.06 1.06a1 1 0 1 1-1.41 1.41l-1.06-1.06a1 1 0 0 1 0-1.41ZM7.09 16.91a1 1 0 0 1 1.41 0l1.06 1.06a1 1 0 0 1-1.41 1.41l-1.06-1.06a1 1 0 0 1 0-1.41Zm9.98 1.06a1 1 0 0 1 0 1.41l-1.06 1.06a1 1 0 1 1-1.41-1.41l1.06-1.06a1 1 0 0 1 1.41 0ZM7.09 7.09a1 1 0 0 1 0 1.41L6.03 9.56a1 1 0 1 1-1.41-1.41L5.68 7.09a1 1 0 0 1 1.41 0Z" />
      </svg>
      <svg v-else viewBox="0 0 24 24" class="floating-tool-icon" aria-hidden="true" focusable="false">
        <path d="M20.37 14.13A8.5 8.5 0 0 1 9.87 3.63 9.5 9.5 0 1 0 20.37 14.13Z" />
      </svg>
    </button>

    <transition name="scroll-top-fade">
      <button
        v-if="showScrollTop"
        class="floating-tool-btn scroll-top-btn"
        type="button"
        aria-label="回到顶部"
        title="回到顶部"
        @click="scrollToTop"
      >
        <svg viewBox="0 0 24 24" class="floating-tool-icon" aria-hidden="true" focusable="false">
          <path d="M12 5.5c.4 0 .75.14 1.03.42l5.78 5.78a1.5 1.5 0 1 1-2.12 2.12L13.5 10.63V18a1.5 1.5 0 0 1-3 0v-7.37l-3.19 3.19a1.5 1.5 0 0 1-2.12-2.12l5.78-5.78c.28-.28.63-.42 1.03-.42Z" />
        </svg>
      </button>
    </transition>

    <transition name="scroll-top-fade">
      <button
        v-if="showScrollBottom"
        class="floating-tool-btn scroll-bottom-btn"
        type="button"
        aria-label="回到底部"
        title="回到底部"
        @click="scrollToBottom"
      >
        <svg viewBox="0 0 24 24" class="floating-tool-icon" aria-hidden="true" focusable="false">
          <path d="M12 18.5c-.4 0-.75-.14-1.03-.42l-5.78-5.78a1.5 1.5 0 1 1 2.12-2.12L12 14.87V7a1.5 1.5 0 0 1 3 0v7.87l3.19-3.19a1.5 1.5 0 0 1 2.12 2.12l-5.78 5.78c-.28.28-.63.42-1.03.42Z" />
        </svg>
      </button>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

type ThemeMode = 'light' | 'dark'

const props = defineProps<{
  theme: ThemeMode
}>()

defineEmits<{
  'toggle-theme': []
}>()

const scrollTop = ref(0)
const showScrollTop = ref(false)
const showScrollBottom = ref(false)
let hideTimer: number | null = null

const themeLabel = computed(() => (props.theme === 'light' ? '切换为暗色主题' : '切换为白天主题'))

const isAtBottom = () => {
  const scrollHeight = document.documentElement.scrollHeight || document.body.scrollHeight
  const clientHeight = document.documentElement.clientHeight || window.innerHeight
  return window.scrollY + clientHeight >= scrollHeight - 80
}

const updateScroll = () => {
  scrollTop.value = window.scrollY || document.documentElement.scrollTop || 0
  showScrollTop.value = scrollTop.value > 320
  showScrollBottom.value = !isAtBottom() && scrollTop.value > 0
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const scrollToBottom = () => {
  window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'smooth' })
}

onMounted(() => {
  updateScroll()
  window.addEventListener('scroll', updateScroll, { passive: true })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', updateScroll)
  if (hideTimer) {
    window.clearTimeout(hideTimer)
    hideTimer = null
  }
})
</script>
