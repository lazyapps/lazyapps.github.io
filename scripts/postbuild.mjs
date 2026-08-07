import { rename, rm } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const dist = fileURLToPath(new URL('../dist/', import.meta.url));

for (const name of ['privacy.en', 'privacy.zh']) {
  const dir = dist + name;
  const index = dir + '/index.html';
  if (!existsSync(index)) continue;
  await rename(index, dist + name + '.html');
  await rm(dir, { recursive: true, force: true });
}

console.log('postbuild: flattened /privacy.*.html');