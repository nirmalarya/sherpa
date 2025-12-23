import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3003,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    // Bundle size optimization
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks - separate large dependencies
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'charts': ['recharts'],
          'icons': ['lucide-react'],
          'utils': ['axios'],
        },
      },
    },
    // Minification and compression (using esbuild - faster and no extra dependency)
    minify: 'esbuild',
    // Drop console logs in production
    esbuild: {
      drop: ['console', 'debugger'],
    },
    // Chunk size warnings
    chunkSizeWarningLimit: 500, // Warn if chunk > 500KB
    // Enable CSS code splitting
    cssCodeSplit: true,
  },
  // Optimize dependencies
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom', 'axios', 'recharts', 'lucide-react'],
  },
})
