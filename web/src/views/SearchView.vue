<template>
  <div class="search-page" v-if="data">
    <header class="search-header">
      <RouterLink to="/" class="back-link">← 首页</RouterLink>
      <h1>搜索：{{ data.keyword }}</h1>
    </header>

    <section class="search-result-panel">
      <article v-for="article in data.articles.items" :key="article.id" class="search-card">
        <RouterLink :to="`/article/${article.id}`" class="search-title">{{ article.title }}</RouterLink>
        <p>{{ article.summary }}</p>
        <div class="search-meta">
          <span>{{ article.category.name }}</span>
          <span>{{ article.author.nickname }}</span>
          <span>{{ article.view_count }} 热度</span>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { webApi } from '../api'
import type { SearchResponse } from '../types'

const route = useRoute()
const data = ref<SearchResponse | null>(null)

const loadData = async () => {
  const keyword = String(route.query.keyword || '')
  if (!keyword) return
  data.value = await webApi.search(keyword)
}

watch(() => route.query.keyword, loadData)
onMounted(loadData)
</script>
