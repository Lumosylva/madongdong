<template>
  <div class="article-page">
    <!-- 错误提示 -->
    <div v-if="error" class="error-panel">
      <h3>加载失败</h3>
      <p>{{ error }}</p>
      <button @click="retryLoad" class="retry-btn">重试</button>
    </div>

    <!-- 加载骨架屏 -->
    <div v-else-if="loading" class="skeleton-container">
      <header class="mini-topbar skeleton">
        <div class="skeleton-line short"></div>
        <div class="skeleton-line medium"></div>
      </header>

      <article class="article-panel skeleton">
        <div class="skeleton-line short"></div>
        <div class="skeleton-line long"></div>
        <div class="skeleton-line medium"></div>
        <div class="skeleton-line medium"></div>
        <div class="skeleton-line medium"></div>
        <div class="skeleton-rectangle"></div>
        <div class="skeleton-line long"></div>
        <div class="skeleton-line long"></div>
        <div class="skeleton-line long"></div>
      </article>

      <section class="comment-panel skeleton">
        <div class="skeleton-line medium"></div>
        <div class="skeleton-line short"></div>
        <div class="skeleton-line long"></div>
        <div class="skeleton-line short"></div>
        <div class="skeleton-line long"></div>
      </section>
    </div>

    <!-- 正常内容 -->
    <div v-else-if="data">
      <header class="mini-topbar">
        <RouterLink to="/" class="back-link">← 返回首页</RouterLink>
        <div class="mini-nav">
          <a v-for="item in data.nav_items" :key="item.id" :href="item.path">{{ item.title }}</a>
        </div>
      </header>

      <article class="article-panel">
        <p class="article-category">{{ data.article.category.name }}</p>
        <h1>{{ data.article.title }}</h1>
        <div class="article-meta">
          <span>{{ data.article.author.nickname }}</span>
          <span>{{ formatDate(data.article.published_at || data.article.created_at) }}</span>
          <span>{{ data.article.view_count }} 阅读</span>
          <span>{{ data.article.comment_count }} 评论</span>
        </div>
        <p class="article-summary">{{ data.article.summary }}</p>
        <img v-if="data.article.cover_url" :src="data.article.cover_url" class="cover" alt="cover" />
        <div class="article-body" v-html="data.article.content_html"></div>
      </article>

      <section class="comment-panel">
        <h2>评论</h2>
        <form class="comment-form" @submit.prevent="submitComment">
          <input v-model="guestNickname" placeholder="匿名昵称（登录后可留空）" />
          <input v-model="guestEmail" placeholder="匿名邮箱（登录后可留空）" />
          <textarea v-model="commentContent" placeholder="写下你的看法"></textarea>
          <button type="submit">提交评论</button>
        </form>
        <div class="comment-list">
          <div v-if="data.comments.length === 0" class="empty-comments">
            <p>暂无评论，快来发表第一条评论吧！</p>
          </div>
          <div v-for="comment in data.comments" :key="comment.id" class="comment-item">
            <strong>{{ comment.user?.nickname || comment.guest_nickname || '匿名访客' }}</strong>
            <span>{{ formatDate(comment.created_at) }}</span>
            <p>{{ comment.content }}</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { webApi } from '../api'
import type { ArticlePageResponse } from '../types'

const route = useRoute()
const data = ref<ArticlePageResponse | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const commentContent = ref('')
const guestNickname = ref('')
const guestEmail = ref('')

const loadData = async () => {
  loading.value = true
  error.value = null
  try {
    data.value = await webApi.getArticle(String(route.params.id))
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载文章失败'
    console.error('加载文章失败:', err)
  } finally {
    loading.value = false
  }
}

const retryLoad = () => {
  loadData()
}

const submitComment = async () => {
  if (!data.value || !commentContent.value.trim()) return
  await webApi.submitComment({
    article_id: data.value.article.id,
    content: commentContent.value,
    guest_nickname: guestNickname.value || null,
    guest_email: guestEmail.value || null,
  })
  commentContent.value = ''
  await loadData()
}

const formatDate = (value: string) => new Date(value).toLocaleString('zh-CN')

onMounted(loadData)
</script>
