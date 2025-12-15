import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Detect if running in Docker (container) or locally
const isDocker = process.env.DOCKER === 'true' || process.env.NODE_ENV === 'docker'

// Use Docker hostnames when in container, localhost when running locally
const backendTarget = isDocker ? 'http://backend:8000' : 'http://localhost:8000'
const forensicTarget = isDocker ? 'http://forensic_agent:8000' : 'http://localhost:8002'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true,
    },
    hmr: {
      port: 5173,
    },
    proxy: {
      '/api': {
        target: backendTarget,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/forensic-api': {
        target: forensicTarget,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/forensic-api/, ''),
      },
    },
  },
})
