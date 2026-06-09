import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import { router } from './router'
import { webApi } from './api'
import { setSiteSetting, buildPageTitle } from './site-meta'
import './styles.css'
import './styles/article-detail-layout.css'
import './styles/article-detail-comments.css'
import 'md-editor-v3/lib/preview.css'

const bootstrap = async () => {
  try {
    const home = await webApi.getHome(1, 1)
    setSiteSetting(home.site)
    document.title = buildPageTitle(router.currentRoute.value.meta.title as string | undefined)
  } catch {
    document.title = 'MadongDong'
  }

  const app = createApp(App)
  app.use(createPinia())
  app.use(router)

  router.afterEach((to) => {
    document.title = buildPageTitle(to.meta.title as string | undefined)
  })

  app.mount('#app')
}

void bootstrap()
