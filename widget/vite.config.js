import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    cssCodeSplit: false,
    lib: {
      entry: 'src/main.js',
      name: 'FeedFlowWidget',
      fileName: 'widget',
      formats: ['iife']
    },
    rollupOptions: {
      output: {
        entryFileNames: 'widget.js',
      },
    },
    outDir: '../backend/app/static',
    emptyOutDir: false
  }
});
