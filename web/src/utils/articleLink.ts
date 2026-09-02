import type { Article } from '../types'

export const articlePath = (article: Pick<Article, 'id' | 'slug'> | null | undefined) => {
  if (!article) return '#'
  const slug = String(article.slug || '').trim()
  return slug ? `/article/${encodeURIComponent(slug)}` : `/article/details/${article.id}`
}
