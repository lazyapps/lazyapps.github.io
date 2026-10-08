import { defineConfig } from 'astro/config';
import { fileURLToPath } from 'node:url';
import { shheepRecordingDev } from './scripts/shheep-recording-dev.mjs';
import { googleAnalytics } from './scripts/google-analytics.mjs';

export default defineConfig({
  site: 'https://lazyapps.com/',
  trailingSlash: 'ignore',
  integrations: [googleAnalytics('G-44V1H8KZ4W')],
  vite: {
    plugins: [shheepRecordingDev()],
    resolve: {
      alias: {
        $assets: fileURLToPath(new URL('./src/assets', import.meta.url)),
      },
    },
  },
});
