import { createI18n } from 'vue-i18n'

import en from './locales/en'
import ja from './locales/ja'
import zhCN from './locales/zh-CN'

const savedLocale = localStorage.getItem('md-admin-locale') || 'zh-CN'

const langMap: Record<string, string> = {
  'zh-CN': 'zh-CN',
  en: 'en',
  ja: 'ja',
}

document.documentElement.lang = langMap[savedLocale] || 'en'

const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'en',
  messages: {
    'zh-CN': zhCN,
    en,
    ja,
  },
})

export default i18n

export const localeOptions = [
  { value: 'zh-CN', label: '简体中文' },
  { value: 'en', label: 'English' },
  { value: 'ja', label: '日本語' },
]

export function setLocale(locale: string) {
  ;(i18n.global.locale as any).value = locale
  localStorage.setItem('md-admin-locale', locale)
  document.documentElement.lang = langMap[locale] || 'en'
}
