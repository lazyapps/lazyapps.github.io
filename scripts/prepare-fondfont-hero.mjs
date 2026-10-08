import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { gzipSync, gunzipSync } from 'node:zlib';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';

const root = new URL('../', import.meta.url);
const models = ['blender-v3/campus-v3.glb', 'pets/cat-v2.glb'];
const effects = ['wind-leaf-v2', 'drift-dust-v2'];
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const manifest = { models: [], effects: [] };
for (const name of models) {
  const url = new URL(`public/v/fondfont/${name}`, root);
  const original = await readFile(url), compressed = gzipSync(original, { level: 9 });
  assert.deepEqual(gunzipSync(compressed), original);
  await writeFile(new URL(`${url}.gz`), compressed);
  manifest.models.push({ name, originalBytes: original.length, downloadBytes: compressed.length, originalSHA256: hash(original), gzipSHA256: hash(compressed) });
}
// Effect sprites are produced by prepare-fondfont-effects-v2.py (resized, lossy WebP with alpha).
for (const name of effects) {
  const encoded = await readFile(new URL(`public/v/fondfont/blender-v2/${name}.webp`, root));
  manifest.effects.push({ name, downloadBytes: encoded.length, webpSHA256: hash(encoded) });
}
const directory = new URL('scripts/assets/fondfont/optimized/', root);
await mkdir(directory, { recursive: true });
await writeFile(new URL('manifest.json', directory), JSON.stringify(manifest, null, 2) + '\n');
console.log('FondFont: lossless model transport prepared; original GLBs retained.');
