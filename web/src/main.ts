import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import { router } from './router'
import './styles.css'
import './styles/article-detail-layout.css'
import './styles/article-detail-comments.css'
import 'md-editor-v3/lib/preview.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.mount('#app')
