<template>
  <div class="shell" v-if="data">
    <header class="topbar">
      <div class="brand-block">
        <span class="brand-mark">MDD</span>
        <h1>{{ data.site.site_title }}</h1>
      </div>
      <nav class="nav">
        <a v-for="item in data.nav_items" :key="item.id" :href="item.path">{{ item.title }}</a>
      </nav>
      <form class="search-box" @submit.prevent="goSearch">
        <input v-model="keyword" placeholder="搜索文章、摘要与内容" />
        <button type="submit" aria-label="搜索">
          <span aria-hidden="true">🔎</span>
        </button>
        <button type="button" class="theme-toggle" :aria-label="themeToggleLabel" @click="toggleTheme">
          <span aria-hidden="true">{{ theme === 'light' ? '◐' : '☼' }}</span>
        </button>
      </form>
    </header>

    <main class="layout">
      <section class="content-panel">
        <div class="hero-intro">
          <p class="hero-kicker">Personal Dispatches</p>
          <p class="hero-subtitle">{{ data.site.site_subtitle || '记录技术、生活与长期主义' }}</p>
        </div>
        <div class="section-head">
          <h2>最新文章</h2>
          <span>第 {{ data.latest_articles.page }} / {{ data.latest_articles.total_pages }} 页</span>
        </div>
        <article v-for="article in data.latest_articles.items" :key="article.id" class="article-card">
          <div class="card-meta">
            <span>{{ article.category.name }}</span>
            <span>{{ article.author.nickname }}</span>
            <span>{{ formatDate(article.published_at || article.created_at) }}</span>
          </div>
          <RouterLink :to="`/article/${article.id}`" class="card-title">{{ article.title }}</RouterLink>
          <p class="card-summary">{{ article.summary }}</p>
          <div class="card-footer">
            <span>热度 {{ article.view_count }}</span>
            <span>评论 {{ article.comment_count }}</span>
          </div>
        </article>
        <div class="pager">
          <button :disabled="page <= 1" @click="changePage(page - 1)">上一页</button>
          <button :disabled="page >= data.latest_articles.total_pages" @click="changePage(page + 1)">下一页</button>
        </div>
      </section>

      <aside class="sidebar">
        <div class="sidebar-card">
          <h3>热门文章</h3>
          <RouterLink v-for="item in data.hot_articles" :key="item.id" :to="`/article/${item.id}`" class="hot-link">
            <strong>{{ item.title }}</strong>
            <span>{{ item.view_count }} 热度 / {{ item.comment_count }} 评论</span>
          </RouterLink>
        </div>
      </aside>
    </main>

    <footer class="footer">
      <span>{{ data.site.icp_beian || '备案信息待配置' }}</span>
      <span>{{ data.site.copyright_text || '© 程序人生' }}</span>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { webApi } from '../api'
import type { HomeResponse } from '../types'

const router = useRouter()
const data = ref<HomeResponse | null>(null)
const keyword = ref('')
const page = ref(1)
type ThemeMode = 'light' | 'dark'
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
  data.value = await webApi.getHome(page.value)
}

const changePage = async (value: number) => {
  page.value = value
  await loadData()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const goSearch = () => {
  if (!keyword.value.trim()) return
  router.push(`/search?keyword=${encodeURIComponent(keyword.value.trim())}`)
}

const formatDate = (value: string) => new Date(value).toLocaleDateString('zh-CN')

const themeToggleLabel = computed(() =>
  theme.value === 'light' ? '切换为暗色主题' : '切换为白天主题',
)

onMounted(() => {
  const storedTheme = localStorage.getItem('md-theme')
  applyTheme(storedTheme === 'dark' ? 'dark' : 'light')
  loadData()
})
</script>
