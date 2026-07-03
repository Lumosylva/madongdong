import { resolveAssetUrl } from '../../assets'
import type { SiteSetting } from './types'

let siteSetting: SiteSetting | null = null

const getBaseTitle = () => siteSetting?.site_title || 'MaDongDong Blog'

const normalizeFaviconUrl = (value: string) => {
  const raw = String(value || '').trim()
  if (!raw) return ''
  try {
    const parsed = new URL(raw, window.location.origin)
    if (parsed.origin === window.location.origin) {
      return parsed.href
    }
    if (parsed.hostname === window.location.hostname && parsed.protocol !== window.location.protocol) {
      parsed.protocol = window.location.protocol
      return parsed.href
    }
    return parsed.href
  } catch {
    return resolveAssetUrl(raw, window.location.origin)
  }
}

export const setSiteSetting = (value: SiteSetting | null) => {
  siteSetting = value
  if (value?.site_title) {
    document.title = value.site_title
  }
}

export const getSiteSetting = () => siteSetting

export const getSiteTitle = () => getBaseTitle()

export const buildPageTitle = (pageTitle?: string | null) => {
  const baseTitle = getBaseTitle()
  const normalizedPageTitle = String(pageTitle || '').trim()
  return normalizedPageTitle ? `${normalizedPageTitle} - ${baseTitle}` : baseTitle
}

function setMetaTag(name: string, content: string, property = false) {
  const attr = property ? 'property' : 'name'
  let el = document.querySelector(`meta[${attr}="${name}"]`) as HTMLMetaElement | null
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, name)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

const setCanonicalUrl = (url: string) => {
  let link = document.querySelector("link[rel='canonical']") as HTMLLinkElement | null
  if (!link) {
    link = document.createElement('link')
    link.rel = 'canonical'
    document.head.appendChild(link)
  }
  link.href = url
}

export const applySiteMeta = (siteTitle: string, siteSubtitle: string | null, siteLogo: string | null, heroImage?: string | null) => {
  const title = String(siteTitle || '').trim()
  const subtitle = String(siteSubtitle || '').trim()
  const fullTitle = title && subtitle ? `${title} - ${subtitle}` : (title || subtitle || getBaseTitle())
  document.title = fullTitle

  setMetaTag('og:title', fullTitle, true)
  setMetaTag('og:site_name', title || getBaseTitle(), true)
  setMetaTag('og:description', subtitle || 'MaDongDong Blog', true)
  setMetaTag('og:url', window.location.href, true)
  setMetaTag('description', subtitle || 'MaDongDong 博客，提供文章阅读、友链浏览。')
  setMetaTag('twitter:title', fullTitle)
  setCanonicalUrl(window.location.href)

  const imageUrl = heroImage ? heroImage : (siteLogo || null)
  if (imageUrl) {
    const normalizedImage = normalizeFaviconUrl(imageUrl)
    if (normalizedImage) {
      setMetaTag('og:image', normalizedImage, true)
    }
  }

  const iconUrl = siteLogo ? String(siteLogo).trim() : ''
  if (!iconUrl) return

  const normalizedIconUrl = normalizeFaviconUrl(iconUrl)
  if (!normalizedIconUrl) return

  let faviconHref = normalizedIconUrl
  try {
    const parsed = new URL(normalizedIconUrl)
    if (parsed.origin === window.location.origin) {
      faviconHref = parsed.pathname + parsed.search + parsed.hash
    }
  } catch {
    // keep normalizedIconUrl as-is
  }

  let iconLink = document.querySelector("link[rel='icon']") as HTMLLinkElement | null
  if (!iconLink) {
    iconLink = document.createElement('link')
    iconLink.rel = 'icon'
    document.head.appendChild(iconLink)
  }
  iconLink.type = faviconHref.endsWith('.svg') ? 'image/svg+xml' : 'image/png'
  iconLink.href = faviconHref
  const appleTouch = document.querySelector("link[rel='apple-touch-icon']") as HTMLLinkElement | null
  if (appleTouch) {
    appleTouch.href = faviconHref
  }
}

export const applyArticleMeta = (
  title: string,
  description: string,
  coverUrl?: string | null,
  options?: {
    id?: number
    publishedAt?: string | null
    updatedAt?: string | null
    author?: string | null
    category?: string | null
    tags?: string[]
  }
) => {
  const fullTitle = buildPageTitle(title)
  document.title = fullTitle

  setMetaTag('og:type', 'article', true)
  setMetaTag('og:title', fullTitle, true)
  setMetaTag('og:description', description || title, true)
  setMetaTag('og:url', window.location.href, true)
  setMetaTag('description', description || title)
  setMetaTag('twitter:title', fullTitle)
  setMetaTag('twitter:description', description || title)

  if (options?.id) {
    setCanonicalUrl(`${window.location.origin}/article/details/${options.id}`)
  } else {
    setCanonicalUrl(window.location.href)
  }

  if (options?.publishedAt) {
    setMetaTag('article:published_time', options.publishedAt, true)
  }
  if (options?.updatedAt) {
    setMetaTag('article:modified_time', options.updatedAt, true)
  }
  if (options?.author) {
    setMetaTag('article:author', options.author, true)
  }
  if (options?.category) {
    setMetaTag('article:section', options.category, true)
  }
  if (options?.tags?.length) {
    document.querySelectorAll("meta[property='article:tag']").forEach(el => el.remove())
    options.tags.forEach(tag => setMetaTag('article:tag', tag, true))
  }

  if (coverUrl) {
    const normalizedCover = normalizeFaviconUrl(coverUrl)
    if (normalizedCover) {
      setMetaTag('og:image', normalizedCover, true)
      setMetaTag('twitter:image', normalizedCover)
      setMetaTag('twitter:card', 'summary_large_image')
    }
  } else {
    setMetaTag('twitter:card', 'summary')
  }
}

export const setHtmlLang = (locale: string) => {
  const langMap: Record<string, string> = {
    'zh-CN': 'zh-CN',
    en: 'en',
    ja: 'ja',
  }
  document.documentElement.lang = langMap[locale] || 'en'
}

export const applySiteMetaFromSetting = (value: SiteSetting | null) => {
  if (!value) return
  applySiteMeta(value.site_title, value.site_subtitle, value.site_logo)
  ensureRssLink()
}

function ensureRssLink() {
  let rssLink = document.querySelector("link[rel='alternate'][type='application/rss+xml']") as HTMLLinkElement | null
  if (!rssLink) {
    rssLink = document.createElement('link')
    rssLink.rel = 'alternate'
    rssLink.type = 'application/rss+xml'
    rssLink.title = 'RSS'
    document.head.appendChild(rssLink)
  }
  rssLink.href = '/api/v1/web/rss'
}

export const applyArticleJsonLd = (options: {
  title: string
  description: string
  url: string
  image?: string | null
  publishedAt?: string | null
  updatedAt?: string | null
  author?: string | null
  category?: string | null
  tags?: string[]
}) => {
  document.querySelectorAll("script[type='application/ld+json']").forEach(el => el.remove())

  const currentSiteSetting = getSiteSetting()
  const jsonLd: Record<string, unknown> = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: options.title,
    description: options.description,
    url: options.url,
  }

  if (options.image) {
    jsonLd.image = options.image
  }
  if (options.publishedAt) {
    jsonLd.datePublished = options.publishedAt
  }
  if (options.updatedAt) {
    jsonLd.dateModified = options.updatedAt
  }
  if (options.author) {
    jsonLd.author = { '@type': 'Person', name: options.author }
  }
  if (options.category) {
    jsonLd.articleSection = options.category
  }
  if (options.tags?.length) {
    jsonLd.keywords = options.tags.join(', ')
  }

  jsonLd.publisher = {
    '@type': 'Organization',
    name: currentSiteSetting?.site_title || 'MaDongDong Blog',
  }

  const script = document.createElement('script')
  script.type = 'application/ld+json'
  script.textContent = JSON.stringify(jsonLd)
  document.head.appendChild(script)
}

export const applyCategoryMeta = (name: string, description: string | null, siteSubtitle: string | null) => {
  const fullTitle = buildPageTitle(`${name} - 分类`)
  document.title = fullTitle

  setMetaTag('og:title', fullTitle, true)
  setMetaTag('og:description', description || siteSubtitle || name, true)
  setMetaTag('og:type', 'website', true)
  setMetaTag('og:url', window.location.href, true)
  setMetaTag('description', description || siteSubtitle || name)
  setMetaTag('twitter:title', fullTitle)
  setMetaTag('twitter:description', description || siteSubtitle || name)
  setCanonicalUrl(window.location.href)
}

export const applyTagMeta = (name: string, siteSubtitle: string | null) => {
  const fullTitle = buildPageTitle(`${name} - 标签`)
  document.title = fullTitle

  setMetaTag('og:title', fullTitle, true)
  setMetaTag('og:description', siteSubtitle || name, true)
  setMetaTag('og:type', 'website', true)
  setMetaTag('og:url', window.location.href, true)
  setMetaTag('description', siteSubtitle || name)
  setMetaTag('twitter:title', fullTitle)
  setMetaTag('twitter:description', siteSubtitle || name)
  setCanonicalUrl(window.location.href)
}
