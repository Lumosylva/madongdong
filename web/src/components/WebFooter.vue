<template>
  <footer class="footer">
    <div class="footer-inner">
      <div class="footer-links-row">
        <RouterLink to="/friend-links" class="footer-friend-links-link">{{ t('footer.friendLinks') }}</RouterLink>
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
</script>

<style scoped>
.footer {
  margin-top: 28px;
  padding: 24px 0 30px;
}

.footer-inner {
  display: grid;
  gap: 12px;
}

.footer-links-row {
  justify-self: center;
  display: flex;
  align-items: center;
  gap: 20px;
}

.footer-friend-links-link,
.footer-rss-link {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--text);
  padding: 8px 2px;
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

.footer-rss-icon {
  width: 16px;
  height: 16px;
  fill: currentColor;
  display: block;
}

.footer-copy-section {
  text-align: center;
  color: var(--text-soft);
  font-size: 13px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 4px 16px;
}

.footer-copyright,
.footer-icp,
.footer-police {
  white-space: nowrap;
}

@media (max-width: 640px) {
  .footer {
    padding: 18px 0 24px;
  }

  .footer-copy-section {
    flex-direction: column;
    gap: 4px;
  }
}
</style>
