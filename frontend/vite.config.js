import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/uploads': { target: 'http://localhost:8000', changeOrigin: true }
    }
  },
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') }
  },
  build: {
    target: 'es2015',
    chunkSizeWarningLimit: 2000,
    sourcemap: false,
    minify: false,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('echarts')) return 'echarts'
            if (id.includes('element-plus')) return 'element-plus'
            if (id.includes('vue')) return 'vue-vendor'
            return 'vendor'
          }
        }
      }
    }
  },
  // terserOptions: {
  //   compress: { drop_console: true, passes: 1 },
  //   mangle: { safari10: true }
  // },
  optimizeDeps: {
    include: ['vue', 'vue-router', 'echarts', 'element-plus']
  }
})