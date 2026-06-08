import type { ArticlePageResponse, CategoryArticlesResponse, HomeResponse, SearchResponse, TagArticlesResponse } from './types'

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined)?.trim() || '/api/v1'
const API_ORIGIN = new URL(API_BASE, window.location.origin).origin

const getToken = () => localStorage.getItem('md_web_token') || ''

export const toAbsoluteAssetUrl = (url: string | null | undefined) => {
  const value = String(url || '').trim()
  if (!value) return ''
  if (/^https?:\/\//i.test(value)) return value
  return `${API_ORIGIN}${value.startsWith('/') ? '' : '/'}${value}`
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || '请求失败')
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
  registerReader(payload: { username: string; password: string; nickname: string; email: string }) {
    return request('/web/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  loginReader(payload: { username: string; password: string }) {
    return request<{ access_token: string; token_type: string }>('/web/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  getFriendLinks() {
    return request<Array<{ id: number; name: string; url: string; description: string; created_at: string }>>('/web/friend-links')
  },
  submitFriendLink(payload: { name: string; url: string; description: string; email: string }) {
    const normalizedUrl = payload.url.trim().startsWith('http://') || payload.url.trim().startsWith('https://')
      ? payload.url.trim()
      : `https://${payload.url.trim()}`
    return request<{ id: number; name: string; url: string; description: string; created_at: string }>('/web/friend-links', {
      method: 'POST',
      body: JSON.stringify({ ...payload, url: normalizedUrl }),
    })
  },
  async getCurrentWebUser() {
    const token = getToken()
    if (!token) {
      throw new Error('未登录')
    }

    const response = await fetch(`${API_BASE}/web/auth/me`, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const text = await response.text()
      throw new Error(text || '请求失败')
    }

    return response.json() as Promise<{ id: number; username: string; nickname: string; email: string }>
  },
}
