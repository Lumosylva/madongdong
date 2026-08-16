<template>
  <div class="page-loader" :class="{ active: loading }">
    <div class="page-loader-bar"></div>
  </div>
  <router-view v-slot="{ Component }">
    <transition name="page-fade" mode="out-in">
      <component :is="Component" :key="$route.fullPath" />
    </transition>
  </router-view>
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
import { useRouter } from 'vue-router'

import FloatingTools from './components/FloatingTools.vue'
import HomeBgmPlayer from './components/HomeBgmPlayer.vue'
import { useTheme } from './composables/useTheme'
import { useErrorToast } from './composables/useErrorToast'
import { webApi } from './api'

const router = useRouter()
const { theme, toggleTheme, initTheme } = useTheme()
const { message: errorMessage, visible: errorVisible, showError, hideError } = useErrorToast()
const bgmUrl = ref('')
const loading = ref(false)

let loadingTimer: ReturnType<typeof setTimeout> | null = null

const startLoading = () => {
  loading.value = true
  if (loadingTimer) clearTimeout(loadingTimer)
}

const stopLoading = () => {
  if (loadingTimer) clearTimeout(loadingTimer)
  loadingTimer = setTimeout(() => {
    loading.value = false
  }, 200)
}

router.beforeEach(() => { startLoading() })
router.afterEach(() => { stopLoading() })

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
/* ── Page transition ── */

.page-fade-enter-active {
  transition: opacity 0.2s ease 0.05s;
}

.page-fade-leave-active {
  transition: opacity 0.12s ease;
}

.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}

/* ── Top loading bar ── */

.page-loader {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  z-index: 9999;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.15s ease;
}

.page-loader.active {
  opacity: 1;
}

.page-loader-bar {
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, var(--accent), #38bdf8);
  border-radius: 0 2px 2px 0;
  transition: width 0.3s ease;
  box-shadow: 0 0 10px rgba(14, 165, 164, 0.4);
}

.page-loader.active .page-loader-bar {
  width: 70%;
  animation: loader-progress 1.5s ease-out forwards;
}

@keyframes loader-progress {
  0% { width: 0%; }
  30% { width: 45%; }
  60% { width: 65%; }
  80% { width: 75%; }
  100% { width: 80%; }
}

.page-loader:not(.active) .page-loader-bar {
  width: 100%;
  transition: width 0.2s ease;
}
</style>
