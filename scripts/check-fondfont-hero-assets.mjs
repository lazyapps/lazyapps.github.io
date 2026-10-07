import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { gunzipSync } from 'node:zlib';
import sharp from 'sharp';

for (const name of ['blender-v2/factory-truck-v14.glb', 'pets/cat-v1.glb']) {
  const url = new URL(`../public/v/fondfont/${name}`, import.meta.url);
  const original = await readFile(url), gzip = await readFile(new URL(`${url}.gz`));
  assert.deepEqual(gunzipSync(gzip), original, 'compression preserves every model byte');
  assert.ok(gzip.length < original.length);
}
for (const name of ['wind-leaf-v1', 'drift-dust-v1']) {
  const url = new URL(`../public/v/fondfont/blender-v2/${name}`, import.meta.url);
  const png = sharp(await readFile(new URL(`${url}.png`))), webp = sharp(await readFile(new URL(`${url}.webp`)));
  const [a, b] = await Promise.all([png.metadata(), webp.metadata()]);
  for (const key of ['width', 'height', 'space', 'hasProfile', 'orientation']) assert.equal(a[key], b[key], `same ${key}`);
  assert.deepEqual(a.icc, b.icc, 'color profile preserved');
  assert.deepEqual(await png.ensureAlpha().raw().toBuffer(), await webp.ensureAlpha().raw().toBuffer(), 'every RGBA channel preserved, including invisible pixels');
}
console.log('Byte-exact models and pixel/profile-exact effects passed.');
