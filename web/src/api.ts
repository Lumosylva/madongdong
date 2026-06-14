import type { ArchiveResponse, ArticlePageResponse, CategoriesResponse, CategoryArticlesResponse, HomeResponse, SearchResponse, TagArticlesResponse } from './types'
import { resolveAssetUrl } from '../../assets'
import i18n from './i18n'

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined)?.trim() || '/api/v1'
const API_ORIGIN = new URL(API_BASE, window.location.origin).origin

export const toAbsoluteAssetUrl = (url: string | null | undefined) => resolveAssetUrl(url, API_ORIGIN)

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const { headers: extraHeaders, ...rest } = init ?? {}
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    ...rest,
    headers: {
      'Content-Type': 'application/json',
      ...extraHeaders,
    },
  })

  if (!response.ok) {
    const rawText = await response.text()
    try {
      const parsed = JSON.parse(rawText) as { detail?: string | { msg?: string }[] }
      if (typeof parsed.detail === 'string') {
        throw new Error(parsed.detail)
      }
      if (Array.isArray(parsed.detail) && parsed.detail.length > 0) {
        const msg = parsed.detail[0]?.msg || i18n.global.t('common.requestFailed')
        throw new Error(msg.replace(/^Value error,?\s*/i, ''))
      }
    } catch (e) {
      if (e instanceof Error && e.message !== i18n.global.t('common.requestFailed')) throw e
    }
    throw new Error(rawText || i18n.global.t('common.requestFailed'))
  }

  return response.json() as Promise<T>
}

export const webApi = {
  getHome(page = 1, pageSize = 20): Promise<HomeResponse> {
    return request<HomeResponse>(`/web/home?page=${page}&page_size=${pageSize}`)
  },
  getArticle(articleId: string | number): Promise<ArticlePageResponse> {
    return request<ArticlePageResponse>(`/web/articles/${articleId}`)
  },
  search(keyword: string, page = 1, pageSize = 20): Promise<SearchResponse> {
    return request<SearchResponse>(`/web/search?keyword=${encodeURIComponent(keyword)}&page=${page}&page_size=${pageSize}`)
  },
  getCategoryArticles(slug: string, page = 1, pageSize = 20): Promise<CategoryArticlesResponse> {
    return request<CategoryArticlesResponse>(`/web/categories/${encodeURIComponent(slug)}/articles?page=${page}&page_size=${pageSize}`)
  },
  getTagArticles(slug: string, page = 1, pageSize = 20): Promise<TagArticlesResponse> {
    return request<TagArticlesResponse>(`/web/tags/${encodeURIComponent(slug)}/articles?page=${page}&page_size=${pageSize}`)
  },
  getArchive(): Promise<ArchiveResponse> {
    return request<ArchiveResponse>('/web/archive')
  },
  getCategories(): Promise<CategoriesResponse> {
    return request<CategoriesResponse>('/web/categories')
  },
  getInstallStatus(): Promise<{ success: boolean; data: { installed: boolean; initialized: boolean } }> {
    return request('/install/status')
  },
  installSite(payload: {
    site_title: string
    site_subtitle: string | null
    admin_username: string
    admin_password: string
    admin_nickname: string
    admin_email: string
    icp_beian: string | null
    copyright_text: string | null
    homepage_page_size: number
    comment_requires_review: boolean
  }) {
    return request('/install', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  submitComment(payload: Record<string, unknown>) {
    return request('/web/comments', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  registerReader(payload: { username: string; password: string; nickname: string; email: string; captcha_token: string; captcha_answer: string }) {
    return request('/web/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  loginReader(payload: { username: string; password: string; captcha_token?: string; captcha_answer?: string }) {
    return request<{ access_token: string; refresh_token: string; token_type: string }>('/web/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  logoutReader() {
    return request('/web/auth/revoke', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: '' }),
    })
  },
  getFriendLinks() {
    return request<Array<{ id: number; name: string; url: string; description: string; created_at: string }>>('/web/friend-links')
  },
  submitFriendLink(payload: { name: string; url: string; description: string; email: string }) {
    const normalizedUrl = payload.url.trim().startsWith('http')
      ? payload.url.trim()
      : `https://${payload.url.trim()}`
    return request<{ id: number; name: string; url: string; description: string; created_at: string }>('/web/friend-links', {
      method: 'POST',
      body: JSON.stringify({ ...payload, url: normalizedUrl }),
    })
  },
  async getCurrentWebUser() {
    const response = await fetch(`${API_BASE}/web/auth/me`, {
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    })

    if (!response.ok) {
      const text = await response.text()
      throw new Error(text || i18n.global.t('common.requestFailed'))
    }

    return response.json() as Promise<{ id: number; username: string; nickname: string; email: string; avatar: string | null }>
  },
  async updateCurrentWebUser(payload: { nickname: string; email: string; avatar?: string | null; password?: string | null }) {
    const response = await fetch(`${API_BASE}/web/auth/me`, {
      method: 'PUT',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const text = await response.text()
      throw new Error(text || i18n.global.t('common.requestFailed'))
    }

    return response.json() as Promise<{ id: number; username: string; nickname: string; email: string; avatar: string | null }>
  },
}
