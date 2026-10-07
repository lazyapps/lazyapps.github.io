import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { gzipSync, gunzipSync } from 'node:zlib';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const root = new URL('../', import.meta.url);
const models = ['blender-v2/factory-truck-v14.glb', 'pets/cat-v1.glb'];
const effects = ['wind-leaf-v1', 'drift-dust-v1'];
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const manifest = { models: [], effects: [] };
for (const name of models) {
  const url = new URL(`public/v/fondfont/${name}`, root);
  const original = await readFile(url), compressed = gzipSync(original, { level: 9 });
  assert.deepEqual(gunzipSync(compressed), original);
  await writeFile(new URL(`${url}.gz`), compressed);
  manifest.models.push({ name, originalBytes: original.length, downloadBytes: compressed.length, originalSHA256: hash(original), gzipSHA256: hash(compressed) });
}
// Image encoding is explicit maintenance work; CI only regenerates gzip copies.
if (process.argv.includes('--images')) {
  for (const name of effects) {
    const path = fileURLToPath(new URL(`public/v/fondfont/blender-v2/${name}`, root));
    execFileSync('cwebp', ['-lossless', '-exact', '-metadata', 'all', '-m', '6', `${path}.png`, '-o', `${path}.webp`], { stdio: 'pipe' });
  }
}
for (const name of effects) {
  const path = `public/v/fondfont/blender-v2/${name}`;
  const original = await readFile(new URL(`${path}.png`, root)), encoded = await readFile(new URL(`${path}.webp`, root));
  manifest.effects.push({ name, originalBytes: original.length, downloadBytes: encoded.length, originalSHA256: hash(original), webpSHA256: hash(encoded) });
}
const directory = new URL('scripts/assets/fondfont/optimized/', root);
await mkdir(directory, { recursive: true });
await writeFile(new URL('manifest.json', directory), JSON.stringify(manifest, null, 2) + '\n');
console.log('FondFont: lossless model transport prepared; original GLBs retained.');
