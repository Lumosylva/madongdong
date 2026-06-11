<template>
  <div class="shell categories-page" v-if="data">
    <WebTopbar
      :title="data.site.site_title"
      :subtitle="data.site.site_subtitle || '记录技术、生活与长期主义'"
      :logo-url="toAbsoluteAssetUrl(data.site.site_logo)"
      :nav-items="data.nav_items"
      :theme="theme"
      :current-path="route.path"
      :current-full-path="route.fullPath"
      :collapsible-search="true"
      @toggle-theme="toggleTheme"
    />

    <header class="categories-hero">
      <RouterLink to="/" class="categories-back-link">
        <svg class="categories-back-icon" viewBox="0 0 16 16" aria-hidden="true">
          <path d="M10.5 3 5 8l5.5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </svg>
        返回首页
      </RouterLink>
      <div class="categories-hero-body">
        <div class="categories-hero-text">
          <p class="categories-hero-eyebrow">Categories</p>
          <h1 class="categories-hero-title">分类</h1>
          <p class="categories-hero-sub">共 {{ data.categories.length }} 个分类 &nbsp;·&nbsp; {{ data.total_articles }} 篇文章</p>
        </div>
        <div class="categories-hero-metrics">
          <div class="categories-metric-card">
            <strong>{{ data.categories.length }}</strong>
            <span>个分类</span>
          </div>
          <div class="categories-metric-card">
            <strong>{{ data.total_articles }}</strong>
            <span>篇文章</span>
          </div>
        </div>
      </div>
    </header>

    <div v-if="data.categories.length === 0" class="categories-empty">
      暂无分类，请先在后台创建分类并发布文章。
    </div>

    <template v-else>
      <div class="categories-grid">
        <button
          v-for="cat in data.categories"
          :key="cat.id"
          type="button"
          class="category-card"
          :class="{ 'is-selected': selectedSlug === cat.slug }"
          @click="selectCategory(cat)"
        >
          <div class="category-card-top">
            <div class="category-card-icon">{{ cat.name.slice(0, 1) }}</div>
            <span class="category-card-count">{{ cat.article_count }} 篇</span>
          </div>
          <h2 class="category-card-name">{{ cat.name }}</h2>
          <p class="category-card-desc">{{ cat.description || '暂无描述' }}</p>
          <span class="category-card-arrow" aria-hidden="true">▾</span>
        </button>
      </div>

      <transition name="cat-panel">
        <section v-if="selectedSlug" ref="articlePanelRef" class="cat-articles-panel">
          <div class="cat-articles-head">
            <div class="cat-articles-head-left">
              <span class="cat-articles-name">{{ selectedCatName }}</span>
              <span v-if="!catLoading" class="cat-articles-total">{{ catTotal }} 篇</span>
            </div>
            <button type="button" class="cat-articles-close-btn" @click="closeArticles">收起</button>
          </div>

          <div v-if="catLoading" class="cat-articles-loading">
            <span class="cat-loading-dot"></span>
            <span class="cat-loading-dot"></span>
            <span class="cat-loading-dot"></span>
          </div>

          <template v-else>
            <div v-if="catArticles.length === 0" class="cat-articles-empty">该分类下暂无文章。</div>

            <div v-else class="cat-articles-list">
              <RouterLink
                v-for="article in catArticles"
                :key="article.id"
                :to="`/article/${article.id}`"
                class="cat-article-item"
              >
                <div class="cat-article-main">
                  <h3 class="cat-article-title">{{ article.title }}</h3>
                  <p class="cat-article-summary">{{ article.summary }}</p>
                  <div class="cat-article-meta">
                    <span>{{ formatRelativeTime(article.published_at || article.created_at) }}</span>
                    <span>{{ article.view_count }} 浏览</span>
                    <span>{{ article.comment_count }} 评论</span>
                  </div>
                </div>
                <span class="cat-article-arrow" aria-hidden="true">→</span>
              </RouterLink>
            </div>

            <div v-if="catPage < catTotalPages" class="cat-articles-more-row">
              <button
                type="button"
                class="cat-load-more-btn"
                :disabled="catLoadingMore"
                @click="loadMoreArticles"
              >
                {{ catLoadingMore ? '加载中…' : `加载更多（还有 ${catTotal - catArticles.length} 篇）` }}
              </button>
            </div>
          </template>
        </section>
      </transition>
    </template>

    <WebFooter :icp-beian="data.site.icp_beian" :copyright-text="data.site.copyright_text" />
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { toAbsoluteAssetUrl, webApi } from '../api'
import WebFooter from '../components/WebFooter.vue'
import WebTopbar from '../components/WebTopbar.vue'
import { applySiteMetaFromSetting, buildPageTitle, setSiteSetting } from '../site-meta'
import type { Article, CategoriesResponse, CategoryWithCount } from '../types'
import { formatRelativeTime } from '../utils/time'

const route = useRoute()
const data = ref<CategoriesResponse | null>(null)
type ThemeMode = 'light' | 'dark'
const theme = ref<ThemeMode>('light')

const selectedSlug = ref<string | null>(null)
const selectedCatName = ref('')
const catArticles = ref<Article[]>([])
const catLoading = ref(false)
const catLoadingMore = ref(false)
const catPage = ref(1)
const catTotalPages = ref(1)
const catTotal = ref(0)
const articlePanelRef = ref<HTMLElement | null>(null)

const applyTheme = (value: ThemeMode) => {
  theme.value = value
  document.documentElement.dataset.theme = value
  localStorage.setItem('md-theme', value)
}

const toggleTheme = () => {
  applyTheme(theme.value === 'light' ? 'dark' : 'light')
}

const scrollToPanel = async () => {
  await nextTick()
  if (!articlePanelRef.value) return
  const top = articlePanelRef.value.getBoundingClientRect().top + window.scrollY - 88
  window.scrollTo({ top: Math.max(0, top), behavior: 'smooth' })
}

const fetchArticles = async (slug: string, page: number) => {
  const res = await webApi.getCategoryArticles(slug, page, 20)
  return res
}

const selectCategory = async (cat: CategoryWithCount) => {
  if (selectedSlug.value === cat.slug) {
    closeArticles()
    return
  }

  selectedSlug.value = cat.slug
  selectedCatName.value = cat.name
  catArticles.value = []
  catPage.value = 1
  catTotalPages.value = 1
  catTotal.value = 0
  catLoading.value = true

  try {
    const res = await fetchArticles(cat.slug, 1)
    catArticles.value = res.articles.items
    catPage.value = res.articles.page
    catTotalPages.value = res.articles.total_pages
    catTotal.value = res.articles.total
  } catch {
    catArticles.value = []
  } finally {
    catLoading.value = false
  }

  await scrollToPanel()
}

const loadMoreArticles = async () => {
  if (!selectedSlug.value || catLoadingMore.value) return
  catLoadingMore.value = true
  try {
    const res = await fetchArticles(selectedSlug.value, catPage.value + 1)
    catArticles.value = [...catArticles.value, ...res.articles.items]
    catPage.value = res.articles.page
    catTotalPages.value = res.articles.total_pages
  } catch {
    // keep existing
  } finally {
    catLoadingMore.value = false
  }
}

const closeArticles = () => {
  selectedSlug.value = null
  selectedCatName.value = ''
  catArticles.value = []
  catPage.value = 1
  catTotalPages.value = 1
  catTotal.value = 0
}

const loadData = async () => {
  data.value = await webApi.getCategories()
  setSiteSetting(data.value.site)
  applySiteMetaFromSetting(data.value.site)
  document.title = buildPageTitle('分类')
}

onMounted(() => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  loadData()
})
</script>

<style scoped>
.categories-page {
  position: relative;
  padding-top: 10px;
}

.categories-page::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 12% 10%, rgba(14, 165, 164, 0.12), transparent 22%),
    radial-gradient(circle at 88% 8%, rgba(234, 154, 24, 0.1), transparent 18%);
  z-index: 0;
}

/* ── Hero ─────────────────────────────────────── */

.categories-hero {
  position: relative;
  margin-bottom: 14px;
  padding: 10px 24px 2px;
  border-radius: 0;
  border: none;
  background: transparent;
  overflow: hidden;
}

.categories-hero::after {
  content: 'Categories';
  position: absolute;
  right: 20px;
  bottom: -8px;
  font-size: 56px;
  font-weight: 900;
  letter-spacing: -0.04em;
  line-height: 1;
  color: rgba(14, 165, 164, 0.055);
  pointer-events: none;
  user-select: none;
  white-space: nowrap;
}

:global([data-theme='dark']) .categories-hero::after {
  color: rgba(94, 234, 212, 0.07);
}

.categories-back-link {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 12px;
  color: var(--text-soft);
  font-size: 13px;
  transition: color 0.18s ease, gap 0.18s ease;
}

.categories-back-link:hover {
  color: var(--accent);
  gap: 7px;
}

.categories-back-icon {
  width: 14px;
  height: 14px;
  flex: 0 0 auto;
  display: block;
}

.categories-hero-body {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
}

.categories-hero-text { min-width: 0; }

.categories-hero-eyebrow {
  margin: 0 0 6px;
  color: var(--accent);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
}

.categories-hero-title {
  margin: 0 0 6px;
  font-size: clamp(30px, 4vw, 44px);
  line-height: 1.08;
  font-weight: 800;
  letter-spacing: -0.03em;
}

.categories-hero-sub {
  margin: 0;
  color: var(--text-soft);
  font-size: 13px;
  line-height: 1.6;
}

.categories-hero-metrics {
  display: flex;
  gap: 8px;
  flex: 0 0 auto;
}

.categories-metric-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  min-width: 60px;
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(14, 165, 164, 0.07);
  border: none;
}

.categories-metric-card strong {
  font-size: 22px;
  font-weight: 800;
  line-height: 1;
  color: var(--accent);
  letter-spacing: -0.02em;
}

.categories-metric-card span {
  font-size: 11px;
  color: var(--text-soft);
  white-space: nowrap;
}

/* ── Category grid ────────────────────────────── */

.categories-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 18px;
}

.category-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px 16px 12px;
  border-radius: 0;
  border: none;
  background: var(--bg-panel);
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
  overflow: hidden;
  color: var(--text);
  cursor: pointer;
  text-align: left;
  font: inherit;
}

.category-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  border-radius: 0;
  background: linear-gradient(90deg, var(--accent), #38bdf8);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.category-card:hover,
.category-card.is-selected {
  transform: translateY(-3px);
  box-shadow: 0 16px 32px rgba(16, 35, 63, 0.1);
}

.category-card.is-selected {
  background: linear-gradient(160deg, rgba(14, 165, 164, 0.06), rgba(14, 165, 164, 0.03));
}

:global([data-theme='dark']) .category-card.is-selected {
  background: linear-gradient(160deg, rgba(14, 165, 164, 0.12), rgba(14, 165, 164, 0.05));
}

.category-card:hover::before,
.category-card.is-selected::before {
  opacity: 1;
}

:global([data-theme='dark']) .category-card:hover,
:global([data-theme='dark']) .category-card.is-selected {
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.28);
}

.category-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.category-card-icon {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-size: 15px;
  font-weight: 800;
  color: var(--text);
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.6), rgba(56, 189, 248, 0.6));
  flex: 0 0 auto;
}

.category-card-count {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--bg-soft);
  border: 1px solid var(--line);
  font-size: 11px;
  color: var(--text-soft);
  white-space: nowrap;
}

.category-card-name {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  line-height: 1.25;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.category-card-desc {
  margin: 0;
  font-size: 12px;
  color: var(--text-soft);
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

:global([data-theme='dark']) .category-card-desc {
  color: var(--text);
}

.category-card-arrow {
  display: inline-block;
  font-size: 14px;
  color: var(--accent);
  line-height: 1;
  opacity: 0;
  transition: opacity 0.18s ease, transform 0.22s ease;
  align-self: flex-end;
}

.category-card:hover .category-card-arrow {
  opacity: 0.6;
}

.category-card.is-selected .category-card-arrow {
  opacity: 1;
  transform: rotate(180deg);
}

/* ── Article panel ────────────────────────────── */

.cat-articles-panel {
  margin-bottom: 24px;
  border-radius: 18px;
  border: 1px solid var(--line);
  background: var(--bg-panel);
  overflow: hidden;
}

.cat-articles-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--line);
  background: var(--bg-soft);
}

.cat-articles-head-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.cat-articles-name {
  font-size: 15px;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cat-articles-total {
  display: inline-flex;
  align-items: center;
  padding: 2px 9px;
  border-radius: 999px;
  background: rgba(14, 165, 164, 0.08);
  color: var(--accent);
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  flex: 0 0 auto;
}

.cat-articles-close-btn {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: transparent;
  color: var(--text-soft);
  font-size: 12px;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.cat-articles-close-btn:hover {
  background: var(--bg-soft);
  color: var(--text);
  border-color: rgba(14, 165, 164, 0.25);
}

/* Loading dots */
.cat-articles-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 36px 0;
}

.cat-loading-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent);
  opacity: 0.25;
  animation: catDotPulse 1.1s ease-in-out infinite;
}

.cat-loading-dot:nth-child(2) { animation-delay: 0.18s; }
.cat-loading-dot:nth-child(3) { animation-delay: 0.36s; }

@keyframes catDotPulse {
  0%, 80%, 100% { opacity: 0.2; transform: scale(0.9); }
  40% { opacity: 1; transform: scale(1.12); }
}

/* Article list */
.cat-articles-empty {
  padding: 32px 20px;
  color: var(--text-soft);
  font-size: 14px;
  text-align: center;
}

.cat-articles-list {
  display: flex;
  flex-direction: column;
}

.cat-article-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--line);
  color: var(--text);
  text-decoration: none;
  transition: background 0.16s ease;
}

.cat-article-item:last-child {
  border-bottom: none;
}

.cat-article-item:hover {
  background: var(--bg-soft);
}

.cat-article-main {
  flex: 1;
  min-width: 0;
  display: grid;
  gap: 5px;
}

.cat-article-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.35;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color 0.16s ease;
}

.cat-article-item:hover .cat-article-title {
  color: var(--accent);
}

.cat-article-summary {
  margin: 0;
  font-size: 13px;
  color: var(--text-soft);
  line-height: 1.6;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cat-article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 12px;
  color: var(--text-soft);
}

.cat-article-arrow {
  flex: 0 0 auto;
  font-size: 14px;
  color: var(--accent);
  opacity: 0;
  transform: translateX(-4px);
  transition: opacity 0.16s ease, transform 0.16s ease;
}

.cat-article-item:hover .cat-article-arrow {
  opacity: 1;
  transform: translateX(0);
}

/* Load more */
.cat-articles-more-row {
  padding: 14px 20px;
  border-top: 1px solid var(--line);
  display: flex;
  justify-content: center;
}

.cat-load-more-btn {
  display: inline-flex;
  align-items: center;
  padding: 8px 20px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: var(--bg-soft);
  color: var(--text);
  font-size: 13px;
  cursor: pointer;
  transition: background 0.16s ease, border-color 0.16s ease, color 0.16s ease;
}

.cat-load-more-btn:hover:not(:disabled) {
  background: rgba(14, 165, 164, 0.08);
  border-color: rgba(14, 165, 164, 0.3);
  color: var(--accent);
}

.cat-load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ── Panel transition ─────────────────────────── */

.cat-panel-enter-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.cat-panel-leave-active {
  transition: opacity 0.16s ease, transform 0.16s ease;
}

.cat-panel-enter-from,
.cat-panel-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ── Empty state ──────────────────────────────── */

.categories-empty {
  padding: 40px 0;
  text-align: center;
  color: var(--text-soft);
  font-size: 14px;
}

/* ── Responsive ───────────────────────────────── */

@media (max-width: 960px) {
  .categories-hero {
    padding: 8px 16px 0;
  }

  .categories-hero::after {
    font-size: 40px;
    right: 14px;
    bottom: -6px;
  }

  .categories-hero-body {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .categories-hero-metrics {
    width: 100%;
    gap: 10px;
  }

  .categories-metric-card {
    flex: 1;
    min-width: 0;
    padding: 8px 10px;
  }

  .categories-metric-card strong {
    font-size: 22px;
  }

  .categories-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
  }

  .cat-article-summary {
    display: none;
  }
}

@media (max-width: 560px) {
  .categories-grid {
    grid-template-columns: 1fr;
  }
}
</style>
