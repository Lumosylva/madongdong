<template>
  <div class="dashboard-shell">
    <aside class="sidebar">
      <h1>控制台</h1>
      <nav>
        <a href="#overview">概览</a>
        <a href="#articles">文章</a>
        <a href="#media">媒体</a>
        <a href="#comments">评论</a>
        <a href="#site">站点</a>
      </nav>
    </aside>

    <main class="dashboard-main">
      <section class="hero-panel" id="overview">
        <p class="eyebrow">Admin Console</p>
        <h2>博客运营后台</h2>
        <p>统一管理文章审核、媒体资源、评论审核与站点设置。</p>
      </section>

      <section class="grid-panels">
        <div class="panel">
          <h3>文章列表</h3>
          <button @click="loadAll">刷新数据</button>
          <ul>
            <li v-for="item in articles" :key="item.id">{{ item.title }} · {{ item.status }}</li>
          </ul>
        </div>
        <div class="panel">
          <h3>媒体库</h3>
          <ul>
            <li v-for="item in media" :key="item.id">{{ item.original_name }} · {{ item.media_type }}</li>
          </ul>
        </div>
        <div class="panel">
          <h3>评论审核</h3>
          <ul>
            <li v-for="item in comments" :key="item.id">{{ item.content }}</li>
          </ul>
        </div>
        <div class="panel" id="site">
          <h3>站点设置</h3>
          <input v-model="siteTitle" placeholder="网站标题" />
          <input v-model="siteSubtitle" placeholder="副标题" />
          <input v-model="icpBeian" placeholder="备案信息" />
          <input v-model="copyrightText" placeholder="版权信息" />
          <button @click="saveSite">保存设置</button>
        </div>
      </section>

      <section class="editor-panel" id="articles">
        <h3>快速创建文章</h3>
        <input v-model="title" placeholder="标题" />
        <input v-model="summary" placeholder="摘要" />
        <input v-model="coverUrl" placeholder="封面图 URL" />
        <textarea v-model="contentMarkdown" placeholder="Markdown 正文"></textarea>
        <div class="action-row">
          <input v-model.number="categoryId" type="number" placeholder="分类 ID" />
          <input v-model="tagIdsText" placeholder="标签 ID，逗号分隔" />
          <select v-model="action">
            <option value="draft">保存草稿</option>
            <option value="submit">提交审核</option>
            <option value="publish">直接发布</option>
          </select>
          <button @click="createArticle">提交</button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { adminApi } from '../api'

const articles = ref<any[]>([])
const media = ref<any[]>([])
const comments = ref<any[]>([])
const siteTitle = ref('')
const siteSubtitle = ref('')
const icpBeian = ref('')
const copyrightText = ref('')

const title = ref('')
const summary = ref('')
const coverUrl = ref('')
const contentMarkdown = ref('')
const categoryId = ref(1)
const tagIdsText = ref('')
const action = ref<'draft' | 'submit' | 'publish'>('draft')

const loadAll = async () => {
  const [articleRes, mediaRes, commentRes, siteRes] = await Promise.all([
    adminApi.getArticles(),
    adminApi.getMedia(),
    adminApi.getComments(),
    adminApi.getSiteSettings(),
  ])
  articles.value = articleRes.data
  media.value = mediaRes.data
  comments.value = commentRes.data
  siteTitle.value = siteRes.data.site_title
  siteSubtitle.value = siteRes.data.site_subtitle || ''
  icpBeian.value = siteRes.data.icp_beian || ''
  copyrightText.value = siteRes.data.copyright_text || ''
}

const saveSite = async () => {
  await adminApi.updateSiteSettings({
    site_title: siteTitle.value,
    site_logo: null,
    site_subtitle: siteSubtitle.value,
    icp_beian: icpBeian.value,
    copyright_text: copyrightText.value,
    homepage_page_size: 10,
    comment_requires_review: true,
  })
  await loadAll()
}

const createArticle = async () => {
  await adminApi.createArticle({
    title: title.value,
    summary: summary.value,
    content_markdown: contentMarkdown.value,
    cover_url: coverUrl.value || null,
    category_id: categoryId.value,
    tag_ids: tagIdsText.value
      .split(',')
      .map((item) => Number(item.trim()))
      .filter((item) => !Number.isNaN(item)),
    action: action.value,
  })
  title.value = ''
  summary.value = ''
  coverUrl.value = ''
  contentMarkdown.value = ''
  tagIdsText.value = ''
  await loadAll()
}

onMounted(loadAll)
</script>
