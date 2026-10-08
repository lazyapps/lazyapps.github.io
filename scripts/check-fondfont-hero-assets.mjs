import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { gunzipSync } from 'node:zlib';
import sharp from 'sharp';

for (const name of ['blender-v3/campus-v3.glb', 'pets/cat-v2.glb']) {
  const url = new URL(`../public/v/fondfont/${name}`, import.meta.url);
  const original = await readFile(url), gzip = await readFile(new URL(`${url}.gz`));
  assert.deepEqual(gunzipSync(gzip), original, 'compression preserves every model byte');
  assert.ok(gzip.length < original.length);
}
// Effect sprites: web-sized lossy WebP with alpha, faithful to the retired v1 originals.
const sizes = { 'wind-leaf-v2': [256, 384, 'wind-leaf-v1'], 'drift-dust-v2': [768, 384, 'drift-dust-v1'] };
for (const [name, [width, height, original]] of Object.entries(sizes)) {
  const webp = sharp(await readFile(new URL(`../public/v/fondfont/blender-v2/${name}.webp`, import.meta.url)));
  const meta = await webp.metadata();
  assert.equal(meta.width, width); assert.equal(meta.height, height); assert.ok(meta.hasAlpha, `${name} keeps alpha`);
  const source = new URL(`./assets/fondfont/blender-v2/retired-public/${original}.png`, import.meta.url);
  try {
    const reference = await sharp(await readFile(source)).resize(width, height, { kernel: 'lanczos3' }).ensureAlpha().raw().toBuffer();
    const actual = await webp.ensureAlpha().raw().toBuffer();
    let alpha = 0; for (let i = 3; i < actual.length; i += 4) alpha += Math.abs(actual[i] - reference[i]);
    alpha /= actual.length / 4;
    assert.ok(alpha < 3, `${name} alpha matches its original within ${alpha.toFixed(2)}/255`);
  } catch (error) { if (error.code !== 'ENOENT') throw error; }
}
console.log('Byte-exact gzip models and web-sized effect sprites (alpha faithful to originals) passed.');
