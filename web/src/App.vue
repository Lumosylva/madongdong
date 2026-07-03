<template>
  <router-view />
  <HomeBgmPlayer :bgm-url="bgmUrl" />
  <FloatingTools :theme="theme" @toggle-theme="toggleTheme" />

  <transition name="error-toast-fade">
    <div v-if="errorVisible" class="global-error-toast" role="alert" aria-live="assertive" @click="hideError">
      <span class="global-error-icon">!</span>
      <span>{{ errorMessage }}</span>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import FloatingTools from './components/FloatingTools.vue'
import HomeBgmPlayer from './components/HomeBgmPlayer.vue'
import { useTheme } from './composables/useTheme'
import { useErrorToast } from './composables/useErrorToast'
import { webApi } from './api'

const { theme, toggleTheme, initTheme } = useTheme()
const { message: errorMessage, visible: errorVisible, showError, hideError } = useErrorToast()
const bgmUrl = ref('')

window.addEventListener('unhandledrejection', (event) => {
  const msg = event.reason instanceof Error ? event.reason.message : String(event.reason || '')
  if (msg) showError(msg)
})

window.addEventListener('error', (event) => {
  const msg = event.message || String(event.error || '')
  if (msg && !msg.includes('ResizeObserver')) showError(msg)
})

onMounted(async () => {
  initTheme()
  try {
    const site = await webApi.getSiteSettings()
    bgmUrl.value = site.homepage_bgm_url || ''
  } catch {
    // ignore - player just won't show
  }
})
</script>

<style>
.global-error-toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10000;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 12px;
  background: var(--danger);
  color: #fff;
  font-size: 14px;
  box-shadow: 0 8px 24px color-mix(in srgb, var(--danger) 25%, transparent);
  backdrop-filter: blur(8px);
  cursor: pointer;
  white-space: nowrap;
  max-width: 90vw;
  overflow: hidden;
  text-overflow: ellipsis;
}

.global-error-icon {
  width: 20px;
  height: 20px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  font-weight: 800;
  font-size: 13px;
  flex-shrink: 0;
}

.error-toast-fade-enter-active,
.error-toast-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.error-toast-fade-enter-from,
.error-toast-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(10px);
}
</style>
