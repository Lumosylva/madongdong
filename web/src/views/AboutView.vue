<template>
  <div class="shell about-page" v-if="data">
    <WebTopbar
      :title="data.site.site_title"
      :subtitle="data.site.site_subtitle || t('about.subtitle')"
      :logo-url="toAbsoluteAssetUrl(data.site.site_logo)"
      :nav-items="data.nav_items"
      :theme="theme"
      :current-path="route.path"
      :current-full-path="route.fullPath"
      :collapsible-search="true"
      @toggle-theme="toggleTheme"
    />

    <main class="about-layout">
      <section class="about-hero">
        <RouterLink to="/" class="about-back-link">
          <svg class="about-back-icon" viewBox="0 0 16 16" aria-hidden="true"><path d="M10.5 3 5 8l5.5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
          {{ t('common.backToHome') }}
        </RouterLink>
        <div class="about-hero-copy">
          <p class="about-eyebrow">About</p>
          <h1 class="about-title">{{ t('about.title') }}</h1>
          <p class="about-lead">
            {{ t('about.description') }}
          </p>
        </div>
      </section>

      <section class="about-grid">
        <article class="about-panel about-panel-wide">
          <h2>{{ t('about.positioning') }}</h2>
          <p>
            {{ t('about.positioningDesc') }}
          </p>
          <a class="about-github-link" href="https://github.com/Lumosylva/madongdong" target="_blank" rel="noopener noreferrer">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
            {{ t('about.github') }}
          </a>
        </article>

        <article class="about-panel about-panel-wide">
          <h2>{{ t('about.contact') }}</h2>
          <p>
            {{ t('about.contactDesc') }}
          </p>
          <a class="about-contact-card" href="mailto:contact@madongdong.com">
            <span class="about-contact-label">{{ t('about.contactEmail') }}</span>
            <strong>contact@madongdong.com</strong>
          </a>
        </article>
      </section>
    </main>

    <WebFooter :icp-beian="data.site.icp_beian" :copyright-text="data.site.copyright_text" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { toAbsoluteAssetUrl, webApi } from '../api'
import WebFooter from '../components/WebFooter.vue'
import WebTopbar from '../components/WebTopbar.vue'
import { applySiteMetaFromSetting, buildPageTitle, setSiteSetting } from '../site-meta'
import type { HomeResponse } from '../types'

type ThemeMode = 'light' | 'dark'

const route = useRoute()
const { t } = useI18n()
const data = ref<HomeResponse | null>(null)
const theme = ref<ThemeMode>('light')

const applyTheme = (value: ThemeMode) => {
  theme.value = value
  document.documentElement.dataset.theme = value
  localStorage.setItem('md-theme', value)
}

const toggleTheme = () => {
  applyTheme(theme.value === 'light' ? 'dark' : 'light')
}

const loadData = async () => {
  data.value = await webApi.getHome(1, 1)
  setSiteSetting(data.value.site)
  applySiteMetaFromSetting(data.value.site)
  document.title = buildPageTitle(t('about.title'))
}

onMounted(async () => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  await loadData()
})
</script>

<style scoped>
.about-page {
  position: relative;
  padding-top: 10px;
}

.about-page::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 12% 10%, rgba(14, 165, 164, 0.12), transparent 22%),
    radial-gradient(circle at 88% 8%, rgba(234, 154, 24, 0.1), transparent 18%);
  z-index: 0;
}

.about-layout {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 18px;
}

.about-hero {
  position: relative;
  padding: 10px 24px 2px;
  border-radius: 0;
  border: none;
  background: transparent;
  overflow: hidden;
}

.about-back-link {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 12px;
  color: var(--text-soft);
  font-size: 13px;
  text-decoration: none;
  transition: color 0.18s ease, gap 0.18s ease;
}

.about-back-link:hover {
  color: var(--accent);
  gap: 7px;
}

.about-back-icon {
  width: 14px;
  height: 14px;
  flex: 0 0 auto;
  display: block;
}

.about-eyebrow {
  margin: 0 0 6px;
  color: var(--accent);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
}

.about-title {
  margin: 0 0 6px;
  font-size: clamp(30px, 4vw, 44px);
  line-height: 1.08;
  font-weight: 800;
}

.about-lead {
  margin: 0;
  color: var(--text-soft);
  font-size: 14px;
  line-height: 1.6;
}

.about-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.about-panel {
  padding: 24px;
  border: none;
  border-radius: 0;
  background: var(--bg-panel);
}

.about-panel h2 {
  margin: 0 0 8px;
  font-size: 16px;
  line-height: 1.2;
  font-weight: 700;
}

.about-panel p {
  margin: 0;
  color: var(--text-soft);
  font-size: 13px;
  line-height: 1.6;
}

.about-panel-wide {
  grid-column: 1 / -1;
}

.about-github-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  padding: 8px 14px;
  border-radius: 10px;
  background: var(--bg-soft);
  color: var(--text);
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.18s ease, color 0.18s ease;
}

.about-github-link:hover {
  background: rgba(14, 165, 164, 0.12);
  color: var(--accent);
}

.about-contact-card {
  display: grid;
  gap: 4px;
  margin-top: 14px;
  padding: 14px 16px;
  border-radius: 12px;
  border: none;
  background: rgba(14, 165, 164, 0.07);
  transition: transform 0.18s ease, background 0.18s ease;
}

.about-contact-card:hover {
  transform: translateY(-2px);
  background: rgba(14, 165, 164, 0.12);
}

.about-contact-label {
  font-size: 11px;
  color: var(--text-soft);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.about-contact-card strong {
  font-size: 16px;
  line-height: 1.25;
  color: var(--text);
  overflow-wrap: anywhere;
}

@media (max-width: 960px) {
  .about-hero {
    grid-template-columns: 1fr;
    padding: 8px 16px 0;
  }

  .about-grid {
    grid-template-columns: 1fr;
  }

  .about-panel,
  .about-panel-wide {
    grid-column: auto;
  }

  .about-panel {
    padding: 20px 16px;
  }

  .about-contact-card strong {
    font-size: 14px;
  }
}
</style>
