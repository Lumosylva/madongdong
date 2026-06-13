import type { AdminUser, FriendLinkItem, LoginResponse } from './types'
import { resolveAssetUrl } from '../../assets'

const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1'
const API_ORIGIN_ENV = String(import.meta.env.VITE_API_ORIGIN || '').trim()
export const API_ORIGIN = API_ORIGIN_ENV || window.location.origin

export const toAbsoluteAssetUrl = (url: string | null | undefined) => resolveAssetUrl(url, API_ORIGIN)

type WrappedResponse<T> = {
  success: boolean
  data: T
}

export const isLoggedIn = () => document.cookie.split('; ').some(c => c.startsWith('admin_logged_in='))

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  })

  if (!response.ok) {
    if (response.status === 401) {
      document.cookie = 'admin_logged_in=; path=/; max-age=0'
    }

    const rawText = await response.text()
    try {
      const parsed = JSON.parse(rawText) as { detail?: string | { msg?: string }[] }
      if (typeof parsed.detail === 'string') {
        throw new Error(parsed.detail)
      }
      if (Array.isArray(parsed.detail) && parsed.detail.length > 0) {
        const first = parsed.detail[0]
        throw new Error(first?.msg || '请求失败')
      }
    } catch {
      // ignore JSON parse errors and fall through to raw text
    }

    throw new Error(rawText || '请求失败')
  }

  return response.json() as Promise<T>
}

export const adminApi = {
  login(username: string, password: string, captchaToken: string, captchaAnswer: string): Promise<LoginResponse> {
    return request<LoginResponse>('/admin/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password, captcha_token: captchaToken, captcha_answer: captchaAnswer }),
    })
  },
  logout() {
    return request('/admin/auth/revoke', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: '' }),
    })
  },
  getMe(): Promise<WrappedResponse<AdminUser>> {
    return request<WrappedResponse<AdminUser>>('/admin/auth/me')
  },
  updateMe(payload: { nickname: string; email: string; avatar: string | null; password: string | null }): Promise<WrappedResponse<AdminUser>> {
    return request<WrappedResponse<AdminUser>>('/admin/auth/me', {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  getUsers(): Promise<WrappedResponse<any[]>> {
    return request<WrappedResponse<any[]>>('/admin/auth/users')
  },
  createUser(payload: Record<string, unknown>): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>('/admin/auth/users', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  updateUser(userId: number, payload: Record<string, unknown>): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/auth/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  deleteUser(userId: number): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/auth/users/${userId}`, {
      method: 'DELETE',
    })
  },
  batchDeleteUsers(userIds: number[]): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>('/admin/auth/users/batch/delete', {
      method: 'POST',
      body: JSON.stringify({ user_ids: userIds }),
    })
  },
  batchChangeUserRole(userIds: number[], roleName: string): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>('/admin/auth/users/batch/role', {
      method: 'POST',
      body: JSON.stringify({ user_ids: userIds, role_name: roleName }),
    })
  },
  getArticles(): Promise<WrappedResponse<any[]>> {
    return request<WrappedResponse<any[]>>('/admin/articles')
  },
  getArticle(articleId: number): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/articles/${articleId}`)
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
  createCategory(payload: { name: string; slug: string; description: string | null }): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>('/admin/categories', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  updateCategory(categoryId: number, payload: { name: string; slug: string; description: string | null }): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/categories/${categoryId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  deleteCategory(categoryId: number): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/categories/${categoryId}`, {
      method: 'DELETE',
    })
  },
  getTags(): Promise<WrappedResponse<any[]>> {
    return request<WrappedResponse<any[]>>('/admin/tags')
  },
  createTag(payload: { name: string; slug: string }): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>('/admin/tags', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  createArticle(payload: Record<string, unknown>): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>('/admin/articles', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  updateArticle(articleId: number, payload: Record<string, unknown>): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/articles/${articleId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  getMedia(): Promise<WrappedResponse<any[]>> {
    return request<WrappedResponse<any[]>>('/admin/media')
  },
  deleteMediaFiles(mediaIds: number[]): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>('/admin/media/delete', {
      method: 'POST',
      body: JSON.stringify({ media_ids: mediaIds }),
    })
  },
  getComments(): Promise<WrappedResponse<any[]>> {
    return request<WrappedResponse<any[]>>('/admin/comments')
  },
  approveComment(commentId: number): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/comments/${commentId}/approve`, {
      method: 'POST',
    })
  },
  rejectComment(commentId: number): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/comments/${commentId}/reject`, {
      method: 'POST',
    })
  },
  deleteComments(commentIds: number[]): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>('/admin/comments/delete', {
      method: 'POST',
      body: JSON.stringify({ comment_ids: commentIds }),
    })
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
  getServerConfig(): Promise<WrappedResponse<{ secret_key: string; database_url: string; site_domain: string; upload_dir: string }>> {
    return request<WrappedResponse<{ secret_key: string; database_url: string; site_domain: string; upload_dir: string }>>('/admin/site/server-config')
  },
  updateServerConfig(payload: { secret_key?: string; site_domain?: string }): Promise<WrappedResponse<{ message: string }>> {
    return request<WrappedResponse<{ message: string }>>('/admin/site/server-config', {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  getFriendLinks(): Promise<WrappedResponse<FriendLinkItem[]>> {
    return request<WrappedResponse<FriendLinkItem[]>>('/admin/friend-links')
  },
  updateFriendLink(linkId: number, payload: Record<string, unknown>): Promise<WrappedResponse<FriendLinkItem>> {
    return request<WrappedResponse<FriendLinkItem>>(`/admin/friend-links/${linkId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  deleteFriendLink(linkId: number): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/friend-links/${linkId}`, {
      method: 'DELETE',
    })
  },
  async uploadMediaFile(file: File, folderId?: number | null): Promise<WrappedResponse<any>> {
    const formData = new FormData()
    formData.append('file', file)
    if (folderId !== undefined && folderId !== null) {
      formData.append('folder_id', String(folderId))
    }

    const response = await fetch(`${API_BASE}/admin/media/upload`, {
      method: 'POST',
      credentials: 'include',
      body: formData,
    })

    if (!response.ok) {
      if (response.status === 401) {
        document.cookie = 'admin_logged_in=; path=/; max-age=0'
      }
      throw new Error(await response.text())
    }

    return response.json() as Promise<WrappedResponse<any>>
  },
}
