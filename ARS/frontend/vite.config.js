import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // All /api calls from React are forwarded to FastAPI
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      // Forward audio file requests to FastAPI static mount
      '/audio-files': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})