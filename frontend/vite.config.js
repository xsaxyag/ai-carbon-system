import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  base: '/ai-carbon-system/',
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/uploads': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  optimizeDeps: {
    include: ['three', 'echarts']
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Three.js 3D图形库
          'vendor-three': ['three'],
          // ECharts 图表库
          'vendor-echarts': ['echarts'],
          // Element Plus UI框架
          'vendor-element': ['element-plus', '@element-plus/icons-vue'],
          // Vue核心
          'vendor-vue': ['vue', 'vue-router']
        }
      }
    },
    chunkSizeWarningLimit: 1500
  }
})
