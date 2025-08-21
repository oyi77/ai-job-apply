import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // Performance optimizations
  build: {
    // Enable source maps for debugging (disable in production)
    sourcemap: false,
    
    // Optimize chunk size
    chunkSizeWarningLimit: 500,
    
    // Rollup options for better bundling
    rollupOptions: {
      output: {
        // Manual chunk splitting for better caching
        manualChunks: {
          // Vendor chunks
          'react-vendor': ['react', 'react-dom'],
          'router-vendor': ['react-router-dom'],
          'state-vendor': ['zustand', '@tanstack/react-query'],
          'ui-vendor': ['@headlessui/react', '@heroicons/react'],
          'utils-vendor': ['axios', 'react-hook-form'],
        },
        
        // Optimize chunk naming
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId
            ? chunkInfo.facadeModuleId.split('/').pop()?.replace('.tsx', '')
            : 'chunk'
          return `js/${facadeModuleId}-[hash].js`
        },
        
        // Optimize asset naming
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name?.split('.') || []
          const ext = info[info.length - 1]
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(ext || '')) {
            return `images/[name]-[hash][extname]`
          }
          if (/css/i.test(ext || '')) {
            return `css/[name]-[hash][extname]`
          }
          return `assets/[name]-[hash][extname]`
        },
      },
    },
    
    // Minification options
    minify: 'terser',
    
    // CSS optimization
    cssCodeSplit: true,
    
    // Target modern browsers for better optimization (ES2020)
    target: 'es2020',
    
    // Bundle analysis
    reportCompressedSize: true,
  },
  
  // Development optimizations
  server: {
    hmr: true,
    port: 5173,
    // Add host configuration for better development experience
    host: true,
  },
  
  // Resolve aliases for better imports
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@pages': resolve(__dirname, 'src/pages'),
      '@services': resolve(__dirname, 'src/services'),
      '@stores': resolve(__dirname, 'src/stores'),
      '@types': resolve(__dirname, 'src/types'),
      '@utils': resolve(__dirname, 'src/utils'),
    },
  },
  
  // Optimize dependencies
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'zustand',
      '@tanstack/react-query',
      '@headlessui/react',
      '@heroicons/react',
      'axios',
      'react-hook-form',
    ],
  },
  
  // Preview configuration for testing builds
  preview: {
    port: 4173,
    host: true,
  },
})
