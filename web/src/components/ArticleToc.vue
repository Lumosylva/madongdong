<template>
  <!-- Desktop sidebar -->
  <nav v-if="headings.length > 1" class="article-toc" :class="{ collapsed: isCollapsed }">
    <div class="toc-header" @click="isCollapsed = !isCollapsed">
      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="15" y2="12"/><line x1="3" y1="18" x2="18" y2="18"/>
      </svg>
      <span>{{ t('article.toc') }}</span>
    </div>
    <transition name="toc-fade">
      <div v-show="!isCollapsed" class="toc-body">
        <ul class="toc-list">
          <li
            v-for="h in headings"
            :key="h.id"
            class="toc-item"
            :class="[`toc-level-${h.level}`, { active: activeId === h.id }]"
          >
            <a :href="`#${h.id}`" class="toc-link" @click.prevent="scrollTo(h.id)" :title="h.text">
              {{ h.text }}
            </a>
          </li>
        </ul>
      </div>
    </transition>
  </nav>

  <!-- Mobile floating button -->
  <button
    v-if="headings.length > 1"
    class="toc-mobile-fab"
    :aria-label="t('article.toc')"
    @click="mobileOpen = true"
  >
    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="15" y2="12"/><line x1="3" y1="18" x2="18" y2="18"/>
    </svg>
  </button>

  <!-- Mobile bottom sheet -->
  <teleport to="body">
    <transition name="toc-sheet-fade">
      <div v-if="mobileOpen" class="toc-sheet-mask" @click="mobileOpen = false">
        <transition name="toc-sheet-slide" appear>
          <div v-if="mobileOpen" class="toc-sheet" @click.stop>
            <div class="toc-sheet-handle" @touchstart="onTouchStart" @touchmove="onTouchMove" @touchend="onTouchEnd">
              <div class="toc-sheet-handle-bar"></div>
            </div>
            <div class="toc-sheet-header">
              <span class="toc-sheet-title">{{ t('article.toc') }}</span>
              <button class="toc-sheet-close" :aria-label="t('common.close')" @click="mobileOpen = false">✕</button>
            </div>
            <div class="toc-sheet-body" ref="sheetBodyRef">
              <ul class="toc-sheet-list">
                <li
                  v-for="h in headings"
                  :key="h.id"
                  class="toc-sheet-item"
                  :class="[`toc-level-${h.level}`, { active: activeId === h.id }]"
                  :ref="el => { if (activeId === h.id) activeItemRef = el as HTMLElement }"
                >
                  <a :href="`#${h.id}`" class="toc-sheet-link" @click.prevent="mobileScrollTo(h.id)">
                    {{ h.text }}
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </transition>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface TocHeading {
  id: string
  text: string
  level: number
}

const props = defineProps<{
  content: string
}>()

const headings = ref<TocHeading[]>([])
const activeId = ref('')
const isCollapsed = ref(false)
const mobileOpen = ref(false)
const sheetBodyRef = ref<HTMLElement | null>(null)
const activeItemRef = ref<HTMLElement | null>(null)
let observer: IntersectionObserver | null = null

const slugify = (text: string): string => {
  return text
    .toLowerCase()
    .replace(/[^\w\u4e00-\u9fff\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim()
}

const scrollTo = (id: string) => {
  const el = document.getElementById(id)
  if (el) {
    const topbar = document.querySelector('.topbar') as HTMLElement | null
    const offset = topbar ? topbar.offsetHeight + 16 : 80
    const y = el.getBoundingClientRect().top + window.scrollY - offset
    window.scrollTo({ top: y, behavior: 'smooth' })
  }
}

const mobileScrollTo = (id: string) => {
  mobileOpen.value = false
  setTimeout(() => scrollTo(id), 300)
}

const setupObserver = () => {
  observer?.disconnect()
  const articleBody = document.querySelector('.article-body-md')
  if (!articleBody) return

  const els = Array.from(articleBody.querySelectorAll('h2, h3, h4, h5, h6'))
  if (!els.length) return

  observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          activeId.value = entry.target.id
          break
        }
      }
    },
    { rootMargin: '-80px 0px -60% 0px', threshold: 0 }
  )

  for (const el of els) {
    if (el.id) observer.observe(el)
  }
}

const syncWithDom = () => {
  const articleBody = document.querySelector('.article-body-md')
  if (!articleBody) {
    headings.value = []
    return
  }

  const domHeadings = Array.from(articleBody.querySelectorAll('h2, h3, h4, h5, h6'))
  const result: TocHeading[] = []
  const counts = new Map<string, number>()

  for (const el of domHeadings) {
    const level = parseInt(el.tagName[1], 10)
    const text = (el.textContent || '').trim()
    if (!text) continue

    const base = slugify(text)
    const count = counts.get(base) || 0
    const id = count > 0 ? `${base}-${count}` : base
    counts.set(base, count + 1)

    if (!el.id) el.id = id
    result.push({ id: el.id, text, level })
  }

  headings.value = result
  nextTick(setupObserver)
}

const updatePosition = () => {
  const panel = document.querySelector('.article-panel') as HTMLElement | null
  const toc = document.querySelector('.article-toc') as HTMLElement | null
  if (!panel || !toc) return
  const panelRect = panel.getBoundingClientRect()
  const tocWidth = toc.offsetWidth || 240
  const gap = 16
  const left = panelRect.left - tocWidth - gap
  if (left >= 24) {
    toc.style.left = `${left}px`
  } else {
    toc.style.left = '24px'
  }
}

const scrollToActiveInSheet = () => {
  if (!activeItemRef.value || !sheetBodyRef.value) return
  const container = sheetBodyRef.value
  const item = activeItemRef.value
  const scrollTop = item.offsetTop - container.offsetTop - container.clientHeight / 3
  container.scrollTo({ top: scrollTop, behavior: 'smooth' })
}

watch(mobileOpen, (v) => {
  if (v) {
    document.body.style.overflow = 'hidden'
    nextTick(scrollToActiveInSheet)
  } else {
    document.body.style.overflow = ''
  }
})

let touchStartY = 0
const onTouchStart = (e: TouchEvent) => { touchStartY = e.touches[0].clientY }
const onTouchMove = (e: TouchEvent) => {
  const dy = e.touches[0].clientY - touchStartY
  if (dy > 80) mobileOpen.value = false
}
const onTouchEnd = () => { touchStartY = 0 }

let resizeObserver: ResizeObserver | null = null

onMounted(async () => {
  await nextTick(syncWithDom)
  await nextTick(updatePosition)
  window.addEventListener('resize', updatePosition)
  const panel = document.querySelector('.article-panel')
  if (panel) {
    resizeObserver = new ResizeObserver(updatePosition)
    resizeObserver.observe(panel)
  }
})

onBeforeUnmount(() => {
  observer?.disconnect()
  resizeObserver?.disconnect()
  window.removeEventListener('resize', updatePosition)
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* ===== Desktop sidebar ===== */
.article-toc {
  position: fixed;
  left: 12px;
  top: 120px;
  width: 240px;
  max-height: calc(100vh - 160px);
  z-index: 10;
  font-size: 13px;
  user-select: none;
}

.toc-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 10px;
  background: var(--bg-panel);
  border: 1px solid var(--line);
  color: var(--text-soft);
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: color 0.18s ease, border-color 0.18s ease;
  backdrop-filter: blur(12px);
}

.toc-header:hover {
  color: var(--accent);
  border-color: color-mix(in srgb, var(--accent) 35%, transparent);
}

.toc-body {
  margin-top: 6px;
  padding: 8px 0;
  border-radius: 10px;
  background: var(--bg-panel);
  border: 1px solid var(--line);
  backdrop-filter: blur(12px);
  overflow-y: auto;
  max-height: calc(100vh - 200px);
  scrollbar-width: thin;
  scrollbar-color: var(--line) transparent;
}

.toc-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.toc-item {
  margin: 0;
  padding: 0;
}

.toc-link {
  display: block;
  padding: 5px 12px;
  color: var(--text-soft);
  text-decoration: none;
  line-height: 1.5;
  border-left: 2px solid transparent;
  transition: color 0.15s ease, border-color 0.15s ease, background 0.15s ease;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.toc-link:hover {
  color: var(--accent);
  background: color-mix(in srgb, var(--accent) 6%, transparent);
}

.toc-level-2 .toc-link {
  padding-left: 12px;
  font-weight: 600;
}

.toc-level-3 .toc-link {
  padding-left: 24px;
}

.toc-level-4 .toc-link {
  padding-left: 36px;
  font-size: 12px;
}

.toc-level-5 .toc-link,
.toc-level-6 .toc-link {
  padding-left: 48px;
  font-size: 12px;
}

.toc-item.active .toc-link {
  color: var(--accent);
  border-left-color: var(--accent);
  background: color-mix(in srgb, var(--accent) 8%, transparent);
}

.toc-fade-enter-active,
.toc-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.toc-fade-enter-from,
.toc-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ===== Mobile FAB ===== */
.toc-mobile-fab {
  display: none;
  position: fixed;
  right: 12px;
  bottom: 160px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid var(--line);
  background: var(--bg-panel);
  color: var(--text-soft);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(12px);
  cursor: pointer;
  z-index: 100;
  place-items: center;
  transition: color 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

.toc-mobile-fab:hover {
  color: var(--accent);
  border-color: color-mix(in srgb, var(--accent) 40%, transparent);
  box-shadow: 0 4px 20px rgba(14, 165, 164, 0.15);
}

/* ===== Mobile bottom sheet ===== */
.toc-sheet-mask {
  position: fixed;
  inset: 0;
  z-index: 9000;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.toc-sheet {
  width: 100%;
  max-width: 480px;
  max-height: 70vh;
  background: var(--bg-panel);
  border-radius: 16px 16px 0 0;
  border: 1px solid var(--line);
  border-bottom: none;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  backdrop-filter: blur(16px);
}

.toc-sheet-handle {
  display: flex;
  justify-content: center;
  padding: 10px 0 4px;
  cursor: grab;
}

.toc-sheet-handle-bar {
  width: 36px;
  height: 4px;
  border-radius: 2px;
  background: var(--line);
}

.toc-sheet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 20px 12px;
  border-bottom: 1px solid var(--line);
}

.toc-sheet-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
}

.toc-sheet-close {
  width: 28px;
  height: 28px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--bg-soft);
  color: var(--text);
  cursor: pointer;
  display: grid;
  place-items: center;
  font-size: 12px;
}

.toc-sheet-body {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
  scrollbar-color: var(--line) transparent;
}

.toc-sheet-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.toc-sheet-item {
  margin: 0;
}

.toc-sheet-link {
  display: block;
  padding: 10px 20px;
  color: var(--text-soft);
  text-decoration: none;
  line-height: 1.5;
  border-left: 3px solid transparent;
  transition: color 0.15s ease, border-color 0.15s ease, background 0.15s ease;
  font-size: 14px;
}

.toc-sheet-link:active {
  background: color-mix(in srgb, var(--accent) 10%, transparent);
}

.toc-sheet-item.active .toc-sheet-link {
  color: var(--accent);
  border-left-color: var(--accent);
  background: color-mix(in srgb, var(--accent) 8%, transparent);
  font-weight: 600;
}

.toc-sheet-item.toc-level-3 .toc-sheet-link {
  padding-left: 36px;
}

.toc-sheet-item.toc-level-4 .toc-sheet-link {
  padding-left: 52px;
  font-size: 13px;
}

.toc-sheet-item.toc-level-5 .toc-sheet-link,
.toc-sheet-item.toc-level-6 .toc-sheet-link {
  padding-left: 68px;
  font-size: 13px;
}

/* ===== Transitions ===== */
.toc-sheet-fade-enter-active,
.toc-sheet-fade-leave-active {
  transition: opacity 0.25s ease;
}

.toc-sheet-fade-enter-from,
.toc-sheet-fade-leave-to {
  opacity: 0;
}

.toc-sheet-slide-enter-active {
  transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.toc-sheet-slide-leave-active {
  transition: transform 0.25s cubic-bezier(0.32, 0.72, 0, 1);
}

.toc-sheet-slide-enter-from,
.toc-sheet-slide-leave-to {
  transform: translateY(100%);
}

/* ===== Responsive ===== */
@media (max-width: 1300px) {
  .article-toc {
    display: none;
  }

  .toc-mobile-fab {
    display: grid;
  }
}
</style>
