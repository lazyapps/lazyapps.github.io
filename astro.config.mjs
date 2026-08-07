import { defineConfig } from 'astro/config';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  site: 'https://lazyapps.com/',
  trailingSlash: 'ignore',
  vite: {
    resolve: {
      alias: {
        $assets: fileURLToPath(new URL('./src/assets', import.meta.url)),
      },
    },
  },
});