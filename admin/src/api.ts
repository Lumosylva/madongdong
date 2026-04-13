import type { AdminUser, LoginResponse } from './types'

const API_BASE = 'http://127.0.0.1:8000/api/v1'

type WrappedResponse<T> = {
  success: boolean
  data: T
}

const getToken = () => localStorage.getItem('blog_admin_token') || ''

const clearToken = () => localStorage.removeItem('blog_admin_token')

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      Authorization: getToken() ? `Bearer ${getToken()}` : '',
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  if (!response.ok) {
    if (response.status === 401) {
      clearToken()
    }
    throw new Error(await response.text())
  }

  return response.json() as Promise<T>
}

export const adminApi = {
  login(username: string, password: string): Promise<LoginResponse> {
    return request<LoginResponse>('/admin/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  },
  getMe(): Promise<WrappedResponse<AdminUser>> {
    return request<WrappedResponse<AdminUser>>('/admin/auth/me')
  },
  getArticles(): Promise<WrappedResponse<any[]>> {
    return request<WrappedResponse<any[]>>('/admin/articles')
  },
  getDeletedArticles(): Promise<WrappedResponse<any[]>> {
    return request<WrappedResponse<any[]>>('/admin/articles/deleted')
  },
  deleteArticle(articleId: number): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/articles/${articleId}`, {
      method: 'DELETE',
    })
  },
  restoreArticle(articleId: number): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/articles/${articleId}/restore`, {
      method: 'POST',
    })
  },
  permanentlyDeleteArticle(articleId: number): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/articles/${articleId}/permanent`, {
      method: 'DELETE',
    })
  },
  getCategories(): Promise<WrappedResponse<any[]>> {
    return request<WrappedResponse<any[]>>('/admin/categories')
  },
  getTags(): Promise<WrappedResponse<any[]>> {
    return request<WrappedResponse<any[]>>('/admin/tags')
  },
  createArticle(payload: Record<string, unknown>): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>('/admin/articles', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  getMedia(): Promise<WrappedResponse<any[]>> {
    return request<WrappedResponse<any[]>>('/admin/media')
  },
  getComments(): Promise<WrappedResponse<any[]>> {
    return request<WrappedResponse<any[]>>('/admin/comments')
  },
  getSiteSettings(): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>('/admin/site/settings')
  },
  updateSiteSettings(payload: Record<string, unknown>): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>('/admin/site/settings', {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
}
