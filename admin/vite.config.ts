import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiBase = (env.VITE_API_BASE || '/api/v1').replace(/\/$/, '')

  return {
    base: '/admin/',
    plugins: [vue()],
    server: {
      port: 5174,
      proxy: {
        [apiBase]: {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
        },
        '/uploads': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
        },
      },
    },
    preview: {
      port: 4174,
    },
  }
})
