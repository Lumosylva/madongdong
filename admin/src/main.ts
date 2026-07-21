import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import i18n from './i18n'
import { adminApi, isLoggedIn } from './api'
import { router } from './router'
import { setSiteSetting, buildPageTitle } from './site-meta'
import './styles.css'

const bootstrap = async () => {
  try {
    if (isLoggedIn()) {
      const siteSettings = await adminApi.getSiteSettings()
      setSiteSetting(siteSettings.data || null)
    } else {
      setSiteSetting(null)
    }
  } catch {
    setSiteSetting(null)
  }

  document.title = buildPageTitle(router.currentRoute.value.meta.title as string | undefined)

  const app = createApp(App)
  app.use(createPinia())
  app.use(router)
  app.use(i18n)

  router.afterEach((to) => {
    document.title = buildPageTitle(to.meta.title as string | undefined)
  })

  app.mount('#app')
}

void bootstrap()
