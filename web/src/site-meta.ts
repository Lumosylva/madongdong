import type { SiteSetting } from './types'

let siteSetting: SiteSetting | null = null

export const setSiteSetting = (value: SiteSetting | null) => {
  siteSetting = value
  if (value?.site_title) {
    document.title = value.site_title
  }
}

export const getSiteSetting = () => siteSetting

export const getSiteTitle = () => siteSetting?.site_title || 'MadongDong'

export const buildPageTitle = (pageTitle?: string | null) => {
  const baseTitle = getSiteTitle()
  const normalizedPageTitle = String(pageTitle || '').trim()
  return normalizedPageTitle ? `${normalizedPageTitle} - ${baseTitle}` : baseTitle
}
