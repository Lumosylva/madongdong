const ABSOLUTE_URL_RE = /^https?:\/\//i

export const resolveAssetUrl = (url: string | null | undefined, baseOrigin: string) => {
  const value = String(url || '').trim()
  if (!value) return ''
  if (ABSOLUTE_URL_RE.test(value)) return value
  if (value.startsWith('/admin/')) return `${baseOrigin}${value}`
  if (value.startsWith('/uploads/') || value.startsWith('/api/') || value.startsWith('/static/')) {
    return `${baseOrigin}${value}`
  }
  return `${baseOrigin}/uploads/${value.replace(/^\/+/, '')}`
}
