// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// 部署到 https://hangsau.github.io/hestia-kb/ — GitHub Pages project site 需要 base path
export default defineConfig({
  site: 'https://hangsau.github.io',
  base: '/hestia-kb',
  vite: {
    plugins: [tailwindcss()],
  },
});
