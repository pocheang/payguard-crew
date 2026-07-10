import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://host.docker.internal:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path
      }
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // 将echarts单独打包
          'echarts': ['echarts/core', 'echarts/charts', 'echarts/components', 'echarts/renderers'],
          // 将vue核心库单独打包
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          // 将axios单独打包
          'axios': ['axios']
        }
      }
    },
    // 提高chunk大小警告阈值到800kb（因为echarts较大）
    chunkSizeWarningLimit: 800
  }
})
