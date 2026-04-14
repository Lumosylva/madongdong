import type { ArticlePageResponse, HomeResponse, SearchResponse } from './types'

const API_BASE = 'http://127.0.0.1:8000/api/v1'
const API_ORIGIN = new URL(API_BASE).origin

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
  getHome(page = 1): Promise<HomeResponse> {
    return request<HomeResponse>('/web/home?page=' + page)
  },
  getArticle(articleId: string | number): Promise<ArticlePageResponse> {
    return request<ArticlePageResponse>(`/web/articles/${articleId}`)
  },
  search(keyword: string, page = 1): Promise<SearchResponse> {
    return request<SearchResponse>(`/web/search?keyword=${encodeURIComponent(keyword)}&page=${page}`)
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
  async getCurrentWebUser() {
    const response = await fetch(`${API_BASE}/web/auth/me`, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: getToken() ? `Bearer ${getToken()}` : '',
      },
    })

    if (!response.ok) {
      const text = await response.text()
      throw new Error(text || '请求失败')
    }

    return response.json() as Promise<{ id: number; username: string; nickname: string; email: string }>
  },
}
