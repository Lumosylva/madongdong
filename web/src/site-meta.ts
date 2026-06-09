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

export const applySiteMeta = (siteTitle: string, siteSubtitle: string | null, siteLogo: string | null) => {
  const title = String(siteTitle || '').trim()
  const subtitle = String(siteSubtitle || '').trim()
  document.title = title && subtitle ? `${title} - ${subtitle}` : (title || subtitle || getBaseTitle())

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

export const applySiteMetaFromSetting = (value: SiteSetting | null) => {
  if (!value) return
  applySiteMeta(value.site_title, value.site_subtitle, value.site_logo)
}
