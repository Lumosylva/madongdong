<template>
  <div class="shell about-page" v-if="data">
    <WebTopbar
      :title="data.site.site_title"
      :subtitle="data.site.site_subtitle || '专注内容、体验与长期价值的个人站点'"
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
        <div class="about-hero-copy">
          <p class="about-eyebrow">About</p>
          <h1 class="about-title">关于本站</h1>
          <p class="about-lead">
            这里是一个围绕技术、产品、创作与日常思考持续更新的内容站点。站点希望用清晰的结构、
            克制的设计和稳定的内容输出，提供值得长期阅读与回访的体验。
          </p>
        </div>
        <div class="about-hero-metrics" aria-label="站点特点">
          <div class="about-metric-card">
            <strong>Clear</strong>
            <span>内容表达清晰</span>
          </div>
          <div class="about-metric-card">
            <strong>Focused</strong>
            <span>主题聚焦稳定</span>
          </div>
          <div class="about-metric-card">
            <strong>Long-term</strong>
            <span>注重长期沉淀</span>
          </div>
        </div>
      </section>

      <section class="about-grid">
        <article class="about-panel">
          <h2>站点定位</h2>
          <p>
            本站用于记录技术实践、知识整理、项目观察以及一些经过筛选的个人表达。内容会优先强调准确性、
            可读性与复用价值，而不是短期噪音。
          </p>
        </article>

        <article class="about-panel">
          <h2>阅读体验</h2>
          <p>
            页面结构保持简洁，导航、归档、分类与搜索共同构成主要的信息入口，方便在浏览、查找与回顾之间快速切换。
          </p>
        </article>

        <article class="about-panel about-panel-wide">
          <h2>联系与合作</h2>
          <p>
            如果你希望就内容交流、友链合作、问题反馈或其他站点相关事项取得联系，可直接发送邮件至下方邮箱。
          </p>
          <a class="about-contact-card" href="mailto:contact@madongdong.com">
            <span class="about-contact-label">联系邮箱</span>
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

import { toAbsoluteAssetUrl, webApi } from '../api'
import WebFooter from '../components/WebFooter.vue'
import WebTopbar from '../components/WebTopbar.vue'
import { applySiteMetaFromSetting, buildPageTitle, setSiteSetting } from '../site-meta'
import type { HomeResponse } from '../types'

type ThemeMode = 'light' | 'dark'

const route = useRoute()
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
  document.title = buildPageTitle('关于')
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
}

.about-page::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 10% 10%, rgba(14, 165, 164, 0.12), transparent 24%),
    radial-gradient(circle at 92% 12%, rgba(234, 154, 24, 0.1), transparent 20%);
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
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.9fr);
  gap: 18px;
  padding: 32px;
  border: 1px solid var(--line);
  border-radius: 24px;
  background: var(--bg-panel);
  overflow: hidden;
}

.about-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  background:
    radial-gradient(circle at 6% 68%, rgba(14, 165, 164, 0.12), transparent 34%),
    radial-gradient(circle at 95% 14%, rgba(234, 154, 24, 0.08), transparent 28%);
}

.about-hero-copy,
.about-hero-metrics {
  position: relative;
  z-index: 1;
}

.about-eyebrow {
  margin: 0 0 10px;
  color: var(--accent);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.about-title {
  margin: 0 0 12px;
  font-size: clamp(34px, 5vw, 52px);
  line-height: 1.06;
  font-weight: 800;
}

.about-lead {
  margin: 0;
  max-width: 60ch;
  color: var(--text-soft);
  font-size: 15px;
  line-height: 1.85;
}

.about-hero-metrics {
  display: grid;
  gap: 12px;
  align-content: center;
}

.about-metric-card {
  display: grid;
  gap: 4px;
  padding: 16px 18px;
  border-radius: 18px;
  border: 1px solid rgba(14, 165, 164, 0.16);
  background: rgba(14, 165, 164, 0.06);
}

.about-metric-card strong {
  font-size: 18px;
  line-height: 1.1;
  color: var(--accent);
}

.about-metric-card span {
  font-size: 13px;
  color: var(--text-soft);
}

.about-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.about-panel {
  padding: 26px;
  border: 1px solid var(--line);
  border-radius: 20px;
  background: var(--bg-panel);
  box-shadow: var(--shadow);
}

.about-panel h2 {
  margin: 0 0 10px;
  font-size: 22px;
  line-height: 1.2;
}

.about-panel p {
  margin: 0;
  color: var(--text-soft);
  font-size: 14px;
  line-height: 1.85;
}

.about-panel-wide {
  grid-column: 1 / -1;
}

.about-contact-card {
  display: grid;
  gap: 6px;
  margin-top: 18px;
  padding: 18px 20px;
  border-radius: 18px;
  border: 1px solid rgba(14, 165, 164, 0.18);
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.08), rgba(56, 189, 248, 0.06));
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

.about-contact-card:hover {
  transform: translateY(-2px);
  border-color: rgba(14, 165, 164, 0.32);
  box-shadow: 0 16px 30px rgba(16, 35, 63, 0.08);
}

.about-contact-label {
  font-size: 12px;
  color: var(--text-soft);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.about-contact-card strong {
  font-size: 20px;
  line-height: 1.25;
  color: var(--text);
  overflow-wrap: anywhere;
}

:global([data-theme='dark']) .about-hero {
  background: rgba(10, 24, 44, 0.76);
}

:global([data-theme='dark']) .about-panel {
  background: rgba(10, 24, 44, 0.82);
}

:global([data-theme='dark']) .about-contact-card {
  background: linear-gradient(135deg, rgba(94, 234, 212, 0.1), rgba(59, 130, 246, 0.08));
}

@media (max-width: 960px) {
  .about-hero {
    grid-template-columns: 1fr;
    padding: 22px 18px;
  }

  .about-grid {
    grid-template-columns: 1fr;
  }

  .about-panel,
  .about-panel-wide {
    grid-column: auto;
  }

  .about-panel {
    padding: 20px 18px;
  }

  .about-contact-card strong {
    font-size: 17px;
  }
}
</style>
