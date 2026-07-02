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

export const applySiteMeta = (siteTitle: string, siteSubtitle: string | null, siteLogo: string | null) => {
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

  const iconUrl = siteLogo ? String(siteLogo).trim() : ''
  if (!iconUrl) return

  const normalizedIconUrl = normalizeFaviconUrl(iconUrl)
  if (!normalizedIconUrl) return

  let iconLink = document.querySelector("link[rel='icon']") as HTMLLinkElement | null
  if (!iconLink) {
    iconLink = document.createElement('link')
    iconLink.rel = 'icon'
    document.head.appendChild(iconLink)
  }
  iconLink.type = normalizedIconUrl.endsWith('.svg') ? 'image/svg+xml' : 'image/png'
  iconLink.href = normalizedIconUrl
  const appleTouch = document.querySelector("link[rel='apple-touch-icon']") as HTMLLinkElement | null
  if (appleTouch) {
    appleTouch.href = normalizedIconUrl
  }
}

export const applyArticleMeta = (title: string, description: string, coverUrl?: string | null) => {
  const fullTitle = buildPageTitle(title)
  document.title = fullTitle

  setMetaTag('og:title', fullTitle, true)
  setMetaTag('og:description', description || title, true)
  setMetaTag('og:url', window.location.href, true)
  setMetaTag('description', description || title)
  setMetaTag('twitter:title', fullTitle)
  setMetaTag('twitter:description', description || title)

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
