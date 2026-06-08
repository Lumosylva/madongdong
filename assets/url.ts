const ABSOLUTE_URL_RE = /^https?:\/\//i

export const isAbsoluteUrl = (value: string) => ABSOLUTE_URL_RE.test(String(value || '').trim())

export const normalizePathSegment = (value: string) => String(value || '').trim().replace(/^\/+/, '')
