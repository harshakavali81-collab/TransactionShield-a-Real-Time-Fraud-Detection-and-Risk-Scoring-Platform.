import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({ base: process.env.GITHUB_PAGES_BASE || '/', plugins: [react()], server: { proxy: { '/api': { target: 'http://localhost:8000', rewrite: path => path.replace(/^\/api/, '') } } } });
