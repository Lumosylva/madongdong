<template>
  <footer class="footer">
    <div class="footer-inner">
      <nav v-if="footerNav.length" class="footer-menu-row" :aria-label="t('footer.footerMenuLabel')">
        <template v-for="item in footerNav" :key="item.id">
          <a
            v-if="isExternal(item.path)"
            :href="item.path"
            class="footer-menu-link"
            :target="item.target || '_blank'"
            rel="noopener noreferrer"
          >{{ item.title }}</a>
          <RouterLink
            v-else
            :to="item.path"
            class="footer-menu-link"
          >{{ item.title }}</RouterLink>
        </template>
      </nav>

      <div v-if="footerNav.length" class="footer-divider"></div>

      <div class="footer-links-row">
        <RouterLink to="/friend-links" class="footer-friend-links-link">
          <svg class="footer-link-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M13.828 10.172a4 4 0 0 0-5.656 0l-4 4a4 4 0 1 0 5.656 5.656l1.102-1.101m-.758-4.899a4 4 0 0 0 5.656 0l4-4a4 4 0 0 0-5.656-5.656l-1.1 1.1" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          {{ t('footer.friendLinks') }}
        </RouterLink>
        <a :href="rssUrl" class="footer-rss-link" target="_blank" rel="noopener noreferrer">
          <svg class="footer-rss-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M3.34 17a10.018 10.018 0 0 1-.43-2.8c0-5.89 4.81-10.7 10.7-10.7A10.745 10.745 0 0 1 21.32 13h-2.02A8.72 8.72 0 0 0 10.6 4.3c-4.82 0-8.73 3.91-8.73 8.73 0 3.1 1.64 5.84 4.12 7.42l.56-1.45Zm6.14 3.09a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3Z" fill="currentColor"/></svg>
          RSS
        </a>
      </div>

      <div class="footer-copy-section">
        <span v-if="copyrightText" v-html="sanitizedCopyright" class="footer-copyright"></span>
        <span v-if="icpBeian" v-html="sanitizedIcp" class="footer-icp"></span>
        <span v-if="policeBeian" v-html="sanitizedPolice" class="footer-police"></span>
        <span v-if="!copyrightText && !icpBeian && !policeBeian" v-html="sanitizedIcp"></span>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import DOMPurify from 'dompurify'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useFooterNav } from '../composables/useFooterNav'

const { t } = useI18n()

const props = defineProps<{
  icpBeian?: string | null
  policeBeian?: string | null
  copyrightText?: string | null
}>()

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined)?.trim() || '/api/v1'
const rssUrl = `${API_BASE}/web/rss`

const sanitize = (html: string) => DOMPurify.sanitize(html, { USE_PROFILES: { html: true } })

const sanitizedCopyright = computed(() => sanitize(props.copyrightText || ''))
const sanitizedIcp = computed(() => sanitize(props.icpBeian || t('footer.footerPending')))
const sanitizedPolice = computed(() => sanitize(props.policeBeian || ''))

const footerNav = useFooterNav()
const isExternal = (p: string) => /^https?:\/\//i.test(String(p || ''))
</script>

<style scoped>
.footer {
  margin-top: auto;
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);
  width: 100vw;
  padding: 0;
  border-top: 1px solid var(--line);
  background: rgba(14, 165, 164, 0.04);
  backdrop-filter: blur(16px);
}

:root[data-theme='dark'] .footer {
  background: rgba(94, 234, 212, 0.06);
}

.footer-inner {
  max-width: min(1500px, 100%);
  margin: 0 auto;
  padding: 16px 20px 18px;
  display: grid;
  gap: 0;
}

.footer-divider {
  width: 32px;
  height: 1px;
  margin: 10px auto;
  background: var(--line);
}

.footer-links-row {
  justify-self: center;
  display: flex;
  align-items: center;
  gap: 14px;
}

.footer-friend-links-link,
.footer-rss-link {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--text);
  padding: 4px 2px;
  position: relative;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.footer-friend-links-link::after,
.footer-rss-link::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 2px;
  width: 100%;
  height: 1px;
  background: color-mix(in srgb, var(--accent) 55%, transparent);
  transform: scaleX(0.7);
  transform-origin: center;
  transition: transform 0.18s ease, opacity 0.18s ease;
  opacity: 0.8;
}

.footer-friend-links-link:hover::after,
.footer-rss-link:hover::after {
  transform: scaleX(1);
  opacity: 1;
}

.footer-link-icon,
.footer-rss-icon {
  width: 14px;
  height: 14px;
  fill: none;
  stroke: currentColor;
  display: block;
  flex-shrink: 0;
}

.footer-rss-icon {
  fill: currentColor;
  stroke: none;
}

.footer-menu-row {
  justify-self: center;
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
  justify-content: center;
}

.footer-menu-link {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--text);
  padding: 4px 2px;
  position: relative;
  text-decoration: none;
}

.footer-menu-link::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 2px;
  width: 100%;
  height: 1px;
  background: color-mix(in srgb, var(--accent) 55%, transparent);
  transform: scaleX(0.7);
  transform-origin: center;
  transition: transform 0.18s ease, opacity 0.18s ease;
  opacity: 0.8;
}

.footer-menu-link:hover::after {
  transform: scaleX(1);
  opacity: 1;
}

.footer-copy-section {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--line);
  text-align: center;
  color: var(--text-soft);
  font-size: 11px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 2px 12px;
}

.footer-copyright,
.footer-icp,
.footer-police {
  white-space: nowrap;
}

@media (max-width: 640px) {
  .footer-inner {
    padding: 14px 14px 16px;
  }

  .footer-copy-section {
    flex-direction: column;
    gap: 2px;
  }
}
</style>
