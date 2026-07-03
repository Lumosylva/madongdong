import { resolveAssetUrl } from '../../assets'
import type { SiteSetting } from './types'

let siteSetting: SiteSetting | null = null

const getBaseTitle = () => siteSetting?.site_title || 'MaDongDong Blog'
const getSiteSubtitle = () => siteSetting?.site_subtitle || ''

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

/**
 * 智能文档标题生成器
 * 参考 WordPress 的 wp_get_document_title() 设计
 */
export const generateDocumentTitle = (context: {
  type: 'home' | 'article' | 'category' | 'tag' | 'search' | 'archive' | 'friend-links' | 'about' | '404'
  title?: string
  page?: number
  totalPages?: number
}) => {
  const siteTitle = getBaseTitle()
  const siteSubtitle = getSiteSubtitle()
  const separator = ' - '

  let titleParts: string[] = []

  switch (context.type) {
    case 'home':
      // 首页：站点标题 - 副标题
      titleParts = siteSubtitle ? [siteTitle, siteSubtitle] : [siteTitle]
      break

    case 'article':
      // 文章页：文章标题 - 站点标题
      titleParts = [context.title || siteTitle, siteTitle]
      break

    case 'category':
      // 分类页：分类名称 - 分类 - 站点标题
      titleParts = [context.title || '分类', '分类', siteTitle]
      break

    case 'tag':
      // 标签页：标签名称 - 标签 - 站点标题
      titleParts = [context.title || '标签', '标签', siteTitle]
      break

    case 'search':
      // 搜索页：搜索: 关键词 - 站点标题
      titleParts = [`搜索: ${context.title || ''}`, siteTitle]
      break

    case 'archive':
      // 归档页：归档 - 站点标题
      titleParts = ['归档', siteTitle]
      break

    case 'friend-links':
      // 友链页：友情链接 - 站点标题
      titleParts = ['友情链接', siteTitle]
      break

    case 'about':
      // 关于页：关于 - 站点标题
      titleParts = ['关于', siteTitle]
      break

    case '404':
      // 404页：页面不存在 - 站点标题
      titleParts = ['页面不存在', siteTitle]
      break

    default:
      titleParts = [siteTitle]
  }

  // 添加分页信息
  if (context.page && context.page > 1) {
    titleParts.push(`第 ${context.page} 页`)
  }

  return titleParts.join(separator)
}

/**
 * @deprecated 使用 generateDocumentTitle 替代
 */
export const buildPageTitle = (pageTitle?: string | null) => {
  const baseTitle = getBaseTitle()
  const normalizedPageTitle = String(pageTitle || '').trim()
  return normalizedPageTitle ? `${normalizedPageTitle} - ${baseTitle}` : baseTitle
}

export const setSiteSetting = (value: SiteSetting | null) => {
  siteSetting = value
  if (value?.site_title) {
    document.title = value.site_title
  }
}

export const getSiteSetting = () => siteSetting

export const getSiteTitle = () => getBaseTitle()

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

/**
 * 设置 robots meta 标签
 * 参考 WordPress 的 wp_robots() 函数
 */
export const setRobotsMeta = (directives: {
  index?: boolean
  follow?: boolean
  archive?: boolean
  snippet?: boolean
  imagePreview?: 'none' | 'standard' | 'large'
  maxSnippet?: number
  maxImagePreview?: 'none' | 'standard' | 'large'
  noTranslate?: boolean
  cacheable?: boolean
}) => {
  const parts: string[] = []
  
  // 基础指令
  if (directives.index === false) parts.push('noindex')
  if (directives.follow === false) parts.push('nofollow')
  if (directives.archive === false) parts.push('noarchive')
  if (directives.snippet === false) parts.push('nosnippet')
  if (directives.noTranslate === true) parts.push('notranslate')
  if (directives.cacheable === false) parts.push('nocache')
  
  // 图片预览
  if (directives.maxImagePreview) {
    parts.push(`max-image-preview:${directives.maxImagePreview}`)
  } else if (directives.imagePreview === 'none') {
    parts.push('max-image-preview:none')
  } else if (directives.imagePreview === 'large') {
    parts.push('max-image-preview:large')
  }
  
  // 片段长度
  if (directives.maxSnippet !== undefined) {
    parts.push(`max-snippet:${directives.maxSnippet}`)
  }
  
  const content = parts.length > 0 ? parts.join(', ') : 'index, follow'
  setMetaTag('robots', content)
}

/**
 * 预设的 robots 指令组合
 */
export const RobotsDirectives = {
  /** 默认：允许索引和跟踪 */
  DEFAULT: { index: true, follow: true },
  
  /** 不允许索引但允许跟踪 */
  NOINDEX_FOLLOW: { index: false, follow: true },
  
  /** 允许索引但不跟踪 */
  INDEX_NOFOLLOW: { index: true, follow: false },
  
  /** 完全禁止 */
  NOINDEX_NOFOLLOW: { index: false, follow: false },
  
  /** 搜索结果页：不索引 */
  SEARCH: { index: false, follow: true },
  
  /** 404页面：不索引不跟踪 */
  NOT_FOUND: { index: false, follow: false },
  
  /** 文章页：允许索引和跟踪，大图预览 */
  ARTICLE: { index: true, follow: true, maxImagePreview: 'large' as const },
  
  /** 分类/标签页：允许索引和跟踪 */
  TAXONOMY: { index: true, follow: true },
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
  const fullTitle = generateDocumentTitle({ type: 'home' })
  document.title = fullTitle

  setMetaTag('og:title', fullTitle, true)
  setMetaTag('og:site_name', siteTitle || getBaseTitle(), true)
  setMetaTag('og:description', siteSubtitle || 'MaDongDong 博客，提供文章阅读、友链浏览。', true)
  setMetaTag('og:url', window.location.href, true)
  setMetaTag('description', siteSubtitle || 'MaDongDong 博客，提供文章阅读、友链浏览。')
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
  const fullTitle = generateDocumentTitle({ type: 'article', title })
  document.title = fullTitle

  setMetaTag('og:type', 'article', true)
  setMetaTag('og:title', fullTitle, true)
  setMetaTag('og:description', description || title, true)
  setMetaTag('og:url', window.location.href, true)
  setMetaTag('description', description || title)
  setMetaTag('twitter:title', fullTitle)
  setMetaTag('twitter:description', description || title)
  setRobotsMeta(RobotsDirectives.ARTICLE)

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
  const fullTitle = generateDocumentTitle({ type: 'category', title: name })
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
  const fullTitle = generateDocumentTitle({ type: 'tag', title: name })
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

export const applySearchMeta = (keyword: string, siteSubtitle: string | null) => {
  const fullTitle = generateDocumentTitle({ type: 'search', title: keyword })
  document.title = fullTitle

  setMetaTag('og:title', fullTitle, true)
  setMetaTag('og:description', `搜索 "${keyword}" 的结果`, true)
  setMetaTag('og:type', 'website', true)
  setMetaTag('og:url', window.location.href, true)
  setMetaTag('description', `搜索 "${keyword}" 的结果 - ${siteSubtitle || getBaseTitle()}`)
  setMetaTag('twitter:title', fullTitle)
  setMetaTag('twitter:description', `搜索 "${keyword}" 的结果`)
  setRobotsMeta(RobotsDirectives.SEARCH)
  setCanonicalUrl(window.location.href)
}

export const applyArchiveMeta = (siteSubtitle: string | null) => {
  const fullTitle = generateDocumentTitle({ type: 'archive' })
  document.title = fullTitle

  setMetaTag('og:title', fullTitle, true)
  setMetaTag('og:description', siteSubtitle || '按时间轴浏览全部文章', true)
  setMetaTag('og:type', 'website', true)
  setMetaTag('og:url', window.location.href, true)
  setMetaTag('description', siteSubtitle || '按时间轴浏览全部文章')
  setMetaTag('twitter:title', fullTitle)
  setMetaTag('twitter:description', siteSubtitle || '按时间轴浏览全部文章')
  setCanonicalUrl(window.location.href)
}

export const applyNotFoundMeta = () => {
  const fullTitle = generateDocumentTitle({ type: '404' })
  document.title = fullTitle

  setMetaTag('og:title', fullTitle, true)
  setMetaTag('og:description', '抱歉，您访问的页面不存在或已被移除。', true)
  setMetaTag('og:type', 'website', true)
  setMetaTag('og:url', window.location.href, true)
  setMetaTag('description', '抱歉，您访问的页面不存在或已被移除。')
  setMetaTag('twitter:title', fullTitle)
  setMetaTag('twitter:description', '抱歉，您访问的页面不存在或已被移除。')
  setRobotsMeta(RobotsDirectives.NOT_FOUND)
  setCanonicalUrl(window.location.href)
}
