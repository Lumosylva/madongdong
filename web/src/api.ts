const API_BASE = 'http://127.0.0.1:8000/api/v1'

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
  getHome(page = 1) {
    return request('/web/home?page=' + page)
  },
  getArticle(articleId: string | number) {
    return request(`/web/articles/${articleId}`)
  },
  search(keyword: string, page = 1) {
    return request(`/web/search?keyword=${encodeURIComponent(keyword)}&page=${page}`)
  },
  submitComment(payload: Record<string, unknown>) {
    return request('/web/comments', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
}
