import { ref } from 'vue'
import type { ThemeMode } from '../types'

export function useTheme() {
  const theme = ref<ThemeMode>('light')

  const applyTheme = (value: ThemeMode) => {
    theme.value = value
    document.documentElement.dataset.theme = value
    localStorage.setItem('md-theme', value)
    window.dispatchEvent(new CustomEvent('md-theme-change', { detail: value }))

    const themeColor = document.querySelector('meta[name="theme-color"]') as HTMLMetaElement | null
    if (themeColor) {
      themeColor.setAttribute('content', value === 'dark' ? '#07111f' : '#f8fbff')
    }
  }

  const toggleTheme = () => {
    applyTheme(theme.value === 'light' ? 'dark' : 'light')
  }

  const handleThemeChange = (event: Event) => {
    const detail = (event as CustomEvent<ThemeMode>).detail
    if (detail === 'dark' || detail === 'light') {
      theme.value = detail
      document.documentElement.dataset.theme = detail
    }
  }

  const initTheme = () => {
    const storedTheme = localStorage.getItem('md-theme')
    if (storedTheme === 'dark' || storedTheme === 'light') {
      applyTheme(storedTheme)
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      applyTheme('dark')
    } else {
      applyTheme('light')
    }
  }

  const listenThemeChange = () => {
    window.addEventListener('md-theme-change', handleThemeChange as EventListener)
  }

  const destroyTheme = () => {
    window.removeEventListener('md-theme-change', handleThemeChange as EventListener)
  }

  return { theme, applyTheme, toggleTheme, initTheme, listenThemeChange, destroyTheme }
}
