import { defineConfig } from 'astro/config';
import { fileURLToPath } from 'node:url';
import { shheepRecordingDev } from './scripts/shheep-recording-dev.mjs';
import { googleAnalytics } from './scripts/google-analytics.mjs';

export default defineConfig({
  site: 'https://lazyapps.com/',
  trailingSlash: 'ignore',
  image: { service: { entrypoint: './src/image-service.mjs' } },
  redirects: {
    '/calmon/en': '/calmon/',
    '/pane': '/calmon/',
    '/pane/en': '/calmon/',
    '/pane/presskit': '/calmon/presskit/',
    '/keyhop/presskit': '/keyhop/',
  },
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
