import { defineConfig } from 'astro/config';
import { yiloLegacyRoutes } from './src/content/yilo-routes.mjs';
import { fileURLToPath } from 'node:url';
import { shheepRecordingDev } from './scripts/shheep-recording-dev.mjs';
import { googleAnalytics } from './scripts/google-analytics.mjs';

export default defineConfig({
  site: 'https://lazyapps.com/',
  trailingSlash: 'ignore',
  image: { service: { entrypoint: './src/image-service.mjs' } },
  redirects: {
    ...Object.fromEntries(Object.entries(yiloLegacyRoutes).map(([from, destination]) => [from, { destination, status: 301 }])),
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
