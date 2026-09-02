<template>
  <div v-if="bgmUrl" class="bgm-player">
    <button type="button" class="bgm-toggle" :class="{ playing: isPlaying }" @click="togglePlay" :aria-label="isPlaying ? '暂停' : '播放'">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55C7.79 13 6 14.79 6 17s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/></svg>
    </button>
    <transition name="bgm-tip-fade">
      <div v-if="showTip" class="bgm-tip">点击播放背景音乐</div>
    </transition>
    <div ref="bgmContainerRef" class="bgm-container" v-html="sanitizedBgm"></div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, nextTick, ref } from 'vue'
import DOMPurify from 'dompurify'

const props = defineProps<{
  bgmUrl: string
}>()

const isPlaying = ref(false)
const showTip = ref(true)
const bgmContainerRef = ref<HTMLElement | null>(null)

let tipTimer: number | null = null

const parseBgmEmbed = (input: string): string => {
  const trimmed = input.trim()

  if (trimmed.startsWith('<iframe') || trimmed.startsWith('<audio')) {
    return trimmed
  }

  const songMatch = trimmed.match(/music\.163\.com\/#\/song\?id=(\d+)/)
  if (songMatch) {
    return `<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width="300" height="110" src="https://music.163.com/outchain/player?type=2&id=${songMatch[1]}&auto=0&height=110"></iframe>`
  }

  const playlistMatch = trimmed.match(/music\.163\.com\/#\/playlist\?id=(\d+)/)
  if (playlistMatch) {
    return `<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width="300" height="450" src="https://music.163.com/outchain/player?type=0&id=${playlistMatch[1]}&auto=0&height=450"></iframe>`
  }

  const directMatch = trimmed.match(/music\.163\.com.*[?&]id=(\d+)/)
  if (directMatch) {
    return `<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width="300" height="110" src="https://music.163.com/outchain/player?type=2&id=${directMatch[1]}&auto=0&height=110"></iframe>`
  }

  return `<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width="300" height="110" src="${trimmed}"></iframe>`
}

const renderedBgm = computed(() => parseBgmEmbed(props.bgmUrl))
const sanitizedBgm = computed(() => DOMPurify.sanitize(renderedBgm.value, {
  USE_PROFILES: { html: true },
  ADD_TAGS: ['iframe', 'audio', 'source'],
  ADD_ATTR: ['allow', 'allowfullscreen', 'frameborder', 'marginheight', 'marginwidth', 'preload', 'type', 'width', 'height', 'controls'],
  ALLOWED_URI_REGEXP: /^https:\/\/(?:[^/]+\.)?(?:music\.163\.com|qq\.com)(?:\/|$)/i,
}))

const togglePlay = async () => {
  isPlaying.value = !isPlaying.value
  showTip.value = false

  await nextTick()
  const container = bgmContainerRef.value
  if (!container) return

  const iframe = container.querySelector('iframe') as HTMLIFrameElement | null
  if (!iframe) return

  try {
    iframe.contentWindow?.postMessage(JSON.stringify({ type: isPlaying.value ? 'play' : 'pause' }), '*')
  } catch {
    // cross-origin
  }
}

onMounted(() => {
  tipTimer = window.setTimeout(() => {
    showTip.value = false
  }, 5000)
})

onBeforeUnmount(() => {
  if (tipTimer) {
    window.clearTimeout(tipTimer)
    tipTimer = null
  }
})
</script>

<style scoped>
.bgm-player {
  position: fixed;
  bottom: 18px;
  left: 18px;
  z-index: 998;
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.bgm-toggle {
  width: 40px;
  height: 40px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(237, 242, 249, 0.9));
  color: var(--text);
  box-shadow: 0 12px 30px rgba(16, 35, 63, 0.18);
  backdrop-filter: blur(12px);
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: transform 0.18s ease, background 0.18s ease, box-shadow 0.18s ease, color 0.18s ease;
  flex: 0 0 auto;
}

.bgm-toggle:hover {
  transform: translateY(-2px);
  background: linear-gradient(135deg, rgba(255, 255, 255, 1), rgba(237, 242, 249, 0.98));
  box-shadow: 0 16px 34px rgba(16, 35, 63, 0.2);
  color: var(--accent);
}

.bgm-toggle.playing {
  color: var(--accent);
  border-color: rgba(14, 165, 164, 0.3);
}

.bgm-tip {
  position: absolute;
  bottom: 48px;
  left: 0;
  white-space: nowrap;
  padding: 6px 12px;
  border-radius: 8px;
  background: var(--bg-panel);
  border: 1px solid var(--line);
  color: var(--text-soft);
  font-size: 12px;
  box-shadow: 0 4px 12px rgba(16, 35, 63, 0.1);
  pointer-events: none;
}

.bgm-tip-fade-enter-active,
.bgm-tip-fade-leave-active {
  transition: opacity 0.22s ease;
}

.bgm-tip-fade-enter-from,
.bgm-tip-fade-leave-to {
  opacity: 0;
}

.bgm-container {
  position: absolute;
  bottom: 48px;
  left: 0;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
}

.bgm-toggle.playing ~ .bgm-container {
  opacity: 1;
  pointer-events: auto;
}

:root[data-theme='dark'] .bgm-toggle {
  background: rgba(9, 20, 38, 0.88);
  color: var(--text);
  border-color: rgba(120, 170, 255, 0.18);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.28);
}

:root[data-theme='dark'] .bgm-toggle:hover {
  background: linear-gradient(135deg, rgba(19, 36, 62, 0.98), rgba(10, 24, 44, 0.96));
  color: var(--accent);
  box-shadow: 0 16px 34px rgba(0, 0, 0, 0.32);
}

:root[data-theme='dark'] .bgm-tip {
  background: rgba(10, 24, 44, 0.92);
  border-color: rgba(120, 170, 255, 0.18);
}

@media (max-width: 960px) {
  .bgm-player {
    bottom: 12px;
    left: 12px;
  }

  .bgm-toggle {
    width: 36px;
    height: 36px;
  }
}
</style>
