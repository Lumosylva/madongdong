import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiBase = (env.VITE_API_BASE || '/api/v1').replace(/\/$/, '')

  return {
    plugins: [vue()],
    server: {
      host: '0.0.0.0',
      port: 5173,
      proxy: {
        [apiBase]: {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
        },
        '/uploads': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
        },
        '/robots.txt': {
          target: 'http://127.0.0.1:8000',
          rewrite: () => `${apiBase}/web/robots.txt`,
        },
      },
    },
  }
})
