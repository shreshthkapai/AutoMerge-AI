import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  },
  root: 'public',
  publicDir: '../public-assets', // Create this empty directory for static assets
  build: {
    outDir: '../dist'
  },
  resolve: {
    alias: {
      // This maps /src in imports to the actual src directory
      '/src': resolve(__dirname, 'src')
    }
  }
})