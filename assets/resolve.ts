import { isAbsoluteUrl, normalizePathSegment } from './url'

export const resolveAssetUrl = (url: string | null | undefined, baseOrigin: string) => {
  const value = String(url || '').trim()
  if (!value) return ''
  if (isAbsoluteUrl(value)) return value
  if (value.startsWith('/admin/')) return `${baseOrigin}${value}`
  if (value.startsWith('/uploads/') || value.startsWith('/api/') || value.startsWith('/static/')) {
    return `${baseOrigin}${value}`
  }
  return `${baseOrigin}/uploads/${normalizePathSegment(value)}`
}
