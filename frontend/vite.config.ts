import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The FastAPI backend (backend/main.py) runs on 8000; Vite forwards API and image calls to it.
const API = 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5180,
    strictPort: true,
    proxy: { '/api': API, '/images': API },
  },
})
