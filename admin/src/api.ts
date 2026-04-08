const API_BASE = 'http://127.0.0.1:8000/api/v1'

const getToken = () => localStorage.getItem('blog_admin_token') || ''

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
    throw new Error(await response.text())
  }

  return response.json() as Promise<T>
}

export const adminApi = {
  login(username: string, password: string) {
    return request('/admin/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  },
  getMe() {
    return request('/admin/auth/me')
  },
  getArticles() {
    return request('/admin/articles')
  },
  getCategories() {
    return request('/admin/categories')
  },
  getTags() {
    return request('/admin/tags')
  },
  createArticle(payload: Record<string, unknown>) {
    return request('/admin/articles', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  getMedia() {
    return request('/admin/media')
  },
  getComments() {
    return request('/admin/comments')
  },
  getSiteSettings() {
    return request('/admin/site/settings')
  },
  updateSiteSettings(payload: Record<string, unknown>) {
    return request('/admin/site/settings', {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
}
