<template>
  <header class="topbar">
    <a
      class="brand-block brand-link"
      :href="webEntryUrl"
      :title="siteTitle ? `${t('nav.viewSite')}：${siteTitle}` : t('nav.viewSite')"
    >
      <img v-if="siteLogo" :src="siteLogo" class="brand-logo" alt="site logo" />
      <span v-else class="brand-mark">MD</span>
      <div class="brand-text">
        <h1>{{ siteTitle || t('nav.dashboard') }}</h1>
        <p>{{ t('nav.viewSite') }}</p>
      </div>
    </a>
    <div class="topbar-actions">
      <div class="lang-menu" ref="langMenuRef">
        <button type="button" class="lang-trigger" :aria-label="t('nav.switchLanguage')" @click="toggleLangMenu">
          <svg class="lang-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12.87 15.07l-2.54-2.51.03-.03A17.52 17.52 0 0014.07 6H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.08L5 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z" fill="currentColor"/></svg>
          <span class="lang-label">{{ localeLabel }}</span>
        </button>
        <transition name="menu-pop">
          <div v-if="isLangMenuOpen" class="user-dropdown lang-dropdown">
            <button
              v-for="opt in localeOptions"
              :key="opt.value"
              type="button"
              class="dropdown-item"
              :class="{ 'is-active': locale === opt.value }"
              @click="switchLocale(opt.value)"
            >
              {{ opt.label }}
            </button>
          </div>
        </transition>
      </div>
      <div class="user-menu" ref="userMenuRef">
        <button type="button" class="user-trigger" :aria-label="t('nav.accountMenu')" @click="toggleUserMenu">
          <span class="user-name">{{ displayName }}</span>
          <span class="role-badge" :class="isAdmin ? 'admin' : 'author'">{{ roleLabel }}</span>
        </button>
        <div v-if="isUserMenuOpen" class="user-dropdown">
          <button type="button" class="dropdown-item" @click="$emit('openProfile')">{{ t('nav.profile') }}</button>
          <button type="button" class="dropdown-item danger" @click="$emit('logout')">{{ t('nav.logout') }}</button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { localeOptions, setLocale } from '../i18n'

const { t, locale } = useI18n()

const props = defineProps<{
  siteTitle: string
  siteLogo: string
  displayName: string
  roleLabel: string
  isAdmin: boolean
}>()

defineEmits<{
  openProfile: []
  logout: []
}>()

const webEntryUrl = computed(() => {
  const baseUrl = (import.meta.env.VITE_WEB_BASE_URL as string | undefined)?.trim()
  if (baseUrl) return baseUrl.replace(/\/$/, '')
  return window.location.origin
})

const isUserMenuOpen = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)
const isLangMenuOpen = ref(false)
const langMenuRef = ref<HTMLElement | null>(null)

const localeLabel = computed(() => {
  const map: Record<string, string> = { 'zh-CN': '中文', en: 'EN', ja: '日本語' }
  return map[locale.value] || locale.value
})

const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
  isLangMenuOpen.value = false
}

const toggleLangMenu = () => {
  isLangMenuOpen.value = !isLangMenuOpen.value
  isUserMenuOpen.value = false
}

const switchLocale = (val: string) => {
  setLocale(val)
  isLangMenuOpen.value = false
}

const handleDocumentClick = (event: MouseEvent) => {
  const target = event.target as Node | null
  if (isUserMenuOpen.value && userMenuRef.value && !userMenuRef.value.contains(target)) {
    isUserMenuOpen.value = false
  }
  if (isLangMenuOpen.value && langMenuRef.value && !langMenuRef.value.contains(target)) {
    isLangMenuOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>
