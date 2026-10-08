import { resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

export function shheepRecordingDev() {
  return {
    name: 'shheep-local-recording',
    apply: 'serve',
    configureServer(server) {
      server.middlewares.use('/__dev/shheep-recording.js', async (request, response) => {
        const host = new URL(`http://${request.headers.host}`).hostname;
        if (!['localhost', '127.0.0.1', '[::1]'].includes(host)) {
          response.statusCode = 404; response.end(); return;
        }
        try {
          const project = process.env.SHHEEP_WEB_DIR || fileURLToPath(new URL('../../../_vibe/shheep/web/', import.meta.url));
          const { buildRecording } = await import(pathToFileURL(resolve(project, 'scripts/build-recording.mjs')).href);
          const code = await buildRecording();
          response.setHeader('Content-Type', 'text/javascript; charset=utf-8');
          response.setHeader('Cache-Control', 'no-store');
          response.end(code);
        } catch (error) {
          server.config.logger.error(`Shheep recording build failed: ${error.message}`);
          response.statusCode = 503;
          response.setHeader('Content-Type', 'text/javascript; charset=utf-8');
          response.end('throw new Error("Shheep recording requires the private web project. Check SHHEEP_WEB_DIR and install its dependencies.");');
        }
      });
    },
  };
}
