import type { AdminUser, FriendLinkItem, LoginResponse } from './types'
import { resolveAssetUrl } from '../../assets'

export const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1'
const API_ORIGIN_ENV = String(import.meta.env.VITE_API_ORIGIN || '').trim()
export const API_ORIGIN = API_ORIGIN_ENV || window.location.origin
const DEFAULT_TIMEOUT = 15_000
const REQUEST_FAILED_MESSAGE = '请求失败'

export class ApiRequestError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiRequestError'
    this.status = status
  }
}

export const toAbsoluteAssetUrl = (url: string | null | undefined) => resolveAssetUrl(url, API_ORIGIN)

type WrappedResponse<T> = {
  success: boolean
  data: T
}

/** 从 cookie 中读取指定键的值 */
function getCookieValue(name: string): string {
  return (document.cookie.split('; ').find(c => c.startsWith(`${name}=`)) || '').split('=').slice(1).join('=')
}

/** 统一清除 admin 认证相关 cookie（所有需要登出/401 的地方调用此函数） */
export function clearAdminAuthCookies() {
  const cookies = ['admin_access_token', 'admin_refresh_token', 'admin_logged_in', 'csrf_token']
  for (const name of cookies) {
    document.cookie = `${name}=; path=/; max-age=0`
  }
}

export const isLoggedIn = () => document.cookie.split('; ').some(c => c.startsWith('admin_logged_in='))

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const { headers: extraHeaders, signal: userSignal, ...rest } = init ?? {}
  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), DEFAULT_TIMEOUT)

  if (userSignal) {
    userSignal.addEventListener('abort', () => controller.abort(), { once: true })
  }

  try {
    const method = (rest.method || 'GET').toUpperCase()
    const isWrite = method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS'
    const csrfToken = isWrite ? getCookieValue('csrf_token') : ''

    const response = await fetch(`${API_BASE}${path}`, {
      credentials: 'include',
      ...rest,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...extraHeaders,
        ...(csrfToken ? { 'X-CSRF-Token': csrfToken } : {}),
      },
    })

    if (!response.ok) {
      if (response.status === 401) {
        clearAdminAuthCookies()
      }

      throw new ApiRequestError(await parseErrorMessage(response), response.status)
    }

    return response.json() as Promise<T>
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiRequestError(REQUEST_FAILED_MESSAGE, 0)
    }
    throw error
  } finally {
    window.clearTimeout(timer)
  }
}

async function parseErrorMessage(response: Response): Promise<string> {
  const rawText = await response.text()
  try {
    const parsed = JSON.parse(rawText) as { detail?: string | { msg?: string }[] }
    if (typeof parsed.detail === 'string') {
      return parsed.detail
    }
    if (Array.isArray(parsed.detail) && parsed.detail.length > 0) {
      const first = parsed.detail[0]
      const msg = first?.msg || REQUEST_FAILED_MESSAGE
      return msg.replace(/^Value error,?\s*/i, '')
    }
  } catch {
    // Fall through to raw text.
  }
  return rawText || REQUEST_FAILED_MESSAGE
}

async function uploadRequest<T>(path: string, body: FormData, init?: RequestInit): Promise<T> {
  const { headers: extraHeaders, signal: userSignal, ...rest } = init ?? {}
  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), DEFAULT_TIMEOUT)

  if (userSignal) {
    userSignal.addEventListener('abort', () => controller.abort(), { once: true })
  }

  try {
    const csrfToken = getCookieValue('csrf_token')
    const response = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      credentials: 'include',
      ...rest,
      signal: controller.signal,
      headers: {
        ...extraHeaders,
        ...(csrfToken ? { 'X-CSRF-Token': csrfToken } : {}),
      },
      body,
    })

    if (!response.ok) {
      if (response.status === 401) {
        clearAdminAuthCookies()
      }
      throw new ApiRequestError(await parseErrorMessage(response), response.status)
    }

    return response.json() as Promise<T>
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiRequestError(REQUEST_FAILED_MESSAGE, 0)
    }
    throw error
  } finally {
    window.clearTimeout(timer)
  }
}

export const adminApi = {
  login(username: string, password: string, captchaToken: string, captchaAnswer: string): Promise<LoginResponse> {
    return request<LoginResponse>('/admin/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password, captcha_token: captchaToken, captcha_answer: captchaAnswer }),
    })
  },
  getCaptcha(): Promise<{ question: string; token: string }> {
    return request<{ question: string; token: string }>('/web/captcha')
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
  createCategory(payload: { name: string; slug: string; description: string | null; parent_id: number | null }): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>('/admin/categories', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  updateCategory(categoryId: number, payload: { name: string; slug: string; description: string | null; parent_id: number | null }): Promise<WrappedResponse<any>> {
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
  getMedia(options?: { folderId?: number; unorganized?: boolean }): Promise<WrappedResponse<any[]>> {
    const params = new URLSearchParams()
    if (options?.unorganized) {
      params.set('unorganized', 'true')
    } else if (options?.folderId !== undefined && options?.folderId !== null) {
      params.set('folder_id', String(options.folderId))
    }
    const qs = params.toString()
    return request<WrappedResponse<any[]>>(`/admin/media${qs ? `?${qs}` : ''}`)
  },
  getFolders(): Promise<WrappedResponse<any[]>> {
    return request<WrappedResponse<any[]>>('/admin/media/folders')
  },
  createFolder(name: string, parentId: number | null, sortOrder = 0): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>('/admin/media/folders', {
      method: 'POST',
      body: JSON.stringify({ name, parent_id: parentId, sort_order: sortOrder }),
    })
  },
  updateFolder(id: number, name: string, parentId: number | null, sortOrder = 0): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/media/folders/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ name, parent_id: parentId, sort_order: sortOrder }),
    })
  },
  deleteFolder(id: number): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/media/folders/${id}`, {
      method: 'DELETE',
    })
  },
  moveMediaFiles(mediaIds: number[], targetFolderId: number | null): Promise<WrappedResponse<any[]>> {
    return request<WrappedResponse<any[]>>('/admin/media/move', {
      method: 'POST',
      body: JSON.stringify({ media_ids: mediaIds, target_folder_id: targetFolderId }),
    })
  },
  deleteMediaFiles(mediaIds: number[]): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>('/admin/media/delete', {
      method: 'POST',
      body: JSON.stringify({ media_ids: mediaIds }),
    })
  },
  getComments(options?: {
    page?: number
    pageSize?: number
    keyword?: string
    status?: string
    sort?: 'newest' | 'oldest'
  }): Promise<WrappedResponse<{ items: any[]; total: number; page: number; page_size: number; total_pages: number }>> {
    const params = new URLSearchParams()
    if (options?.page) params.set('page', String(options.page))
    if (options?.pageSize) params.set('page_size', String(options.pageSize))
    if (options?.keyword?.trim()) params.set('keyword', options.keyword.trim())
    if (options?.status && options.status !== 'all') params.set('status', options.status)
    if (options?.sort) params.set('sort', options.sort)
    const qs = params.toString()
    return request<WrappedResponse<{ items: any[]; total: number; page: number; page_size: number; total_pages: number }>>(`/admin/comments${qs ? `?${qs}` : ''}`)
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
  getNavItems(location?: 'header' | 'footer'): Promise<WrappedResponse<any[]>> {
    const qs = location ? `?location=${location}` : ''
    return request<WrappedResponse<any[]>>(`/admin/site/nav-items${qs}`)
  },
  createNavItem(payload: Record<string, unknown>): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>('/admin/site/nav-items', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  updateNavItem(id: number, payload: Record<string, unknown>): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/site/nav-items/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  deleteNavItem(id: number): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/site/nav-items/${id}`, {
      method: 'DELETE',
    })
  },
  async uploadMediaFile(file: File, folderId?: number | null): Promise<WrappedResponse<any>> {
    const formData = new FormData()
    formData.append('file', file)
    if (folderId !== undefined && folderId !== null) {
      formData.append('folder_id', String(folderId))
    }

    return uploadRequest<WrappedResponse<any>>('/admin/media/upload', formData)
  },
}
