import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],
  build: {
    // 稍微调高一点警告阈值（因为 highlight.js 本身就挺大）
    chunkSizeWarningLimit: 1200, 
    rollupOptions: {
      output: {
        manualChunks(id) {
          // 核心魔法：只要是来自 node_modules 的库，统统塞进一个叫 vendor 的文件里
          if (id.includes('node_modules')) {
            return 'vendor';
          }
        }
      }
    }
  }
})
