import { useI18n } from 'vue-i18n'

export const parseDateTime = (value: string) => {
  const text = String(value || '').trim()
  if (!text) return new Date(0)
  if (/Z|[+-]\d{2}:?\d{2}$/.test(text)) return new Date(text)
  return new Date(`${text}Z`)
}

export const useFormatRelativeTime = () => {
  const { t } = useI18n()

  const formatRelativeTime = (value: string) => {
    const date = parseDateTime(value)
    const now = Date.now()
    const diffMs = Math.max(0, now - date.getTime())
    const minute = 60 * 1000
    const hour = 60 * minute
    const day = 24 * hour
    const year = 365 * day

    if (diffMs < hour) {
      const minutes = Math.max(1, Math.floor(diffMs / minute))
      return t('time.minutesAgo', { n: minutes })
    }
    if (diffMs < day) {
      const hours = Math.max(1, Math.floor(diffMs / hour))
      return t('time.hoursAgo', { n: hours })
    }
    if (diffMs < year) {
      const days = Math.max(1, Math.floor(diffMs / day))
      return t('time.daysAgo', { n: days })
    }
    const years = Math.max(1, Math.floor(diffMs / year))
    return t('time.yearsAgo', { n: years })
  }

  return { formatRelativeTime }
}

export const getArticleUpdatedAt = (article: { updated_at?: string; published_at?: string | null; created_at?: string }) => {
  return article.updated_at || article.published_at || article.created_at || ''
}
