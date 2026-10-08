import { defineConfig } from 'astro/config';
import { fileURLToPath } from 'node:url';
import { shheepRecordingDev } from './scripts/shheep-recording-dev.mjs';

export default defineConfig({
  site: 'https://lazyapps.com/',
  trailingSlash: 'ignore',
  vite: {
    plugins: [shheepRecordingDev()],
    resolve: {
      alias: {
        $assets: fileURLToPath(new URL('./src/assets', import.meta.url)),
      },
    },
  },
});
