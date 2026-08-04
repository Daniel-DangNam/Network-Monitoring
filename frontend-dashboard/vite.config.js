import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  resolve: {
    // Ép Vite bóp nghẹt mọi bản sao của React, chỉ giữ lại đúng 1 bản duy nhất
    dedupe: ['react', 'react-dom'] 
  }
})