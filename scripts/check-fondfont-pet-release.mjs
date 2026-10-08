import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const hash = path => createHash('sha256').update(readFileSync(resolve(root, path))).digest('hex');
const locales = ['en', 'zh-hans', 'zh-hant', 'ja', 'ko', 'fr', 'de'];
const source = 'scripts/assets/fondfont/pets/calico-cat/';
assert.equal(hash(source + 'source.blend'), 'fda4b80f1a06e67a1cc04396b858085faa5cd9742f28d9bde9837aaeab2727fa', 'downloaded cat stays unchanged');
assert.equal(hash(source + 'LICENSE.html'), hash('public/v/fondfont/pets/calico-cat-original-LICENSE.html'));
assert.ok(!existsSync(resolve(root,'public/v/fondfont/pets/dog-v3.glb')), 'retired dog is not distributed');
assert.ok(!existsSync(resolve(root,'dist/v/fondfont/pets/dog-v3.glb')), 'retired dog is not deployed');
for (const name of ['cat-v2.glb', 'cat-v2.glb.gz', 'CREDITS.txt', 'calico-cat-original-LICENSE.html']) {
  assert.equal(hash('public/v/fondfont/pets/' + name), hash('dist/v/fondfont/pets/' + name), 'production asset matches reviewed source');
}
for (const locale of locales) {
  const html = readFileSync(resolve(root, `dist/fondfont/${locale}/index.html`), 'utf8');
  for (const required of ['JonasDichelle', 'blendswap.com/blend/18519', 'creativecommons.org/licenses/by/3.0/', '/v/fondfont/pets/CREDITS.txt']) {
    assert.ok(html.includes(required), `${locale} retains ${required}`);
  }
  assert.ok(!html.includes('studio.blender.org/characters/autumn/v1/'),'no retired dog credits');
  assert.equal(hash(`public/v/fondfont/blender-v2/poster-${locale}.webp`), hash(`dist/v/fondfont/blender-v2/poster-${locale}.webp`));
}
function files(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    const path = resolve(directory, entry.name);
    return entry.isDirectory() ? files(path) : [path];
  });
}
const restrictedHash = hash('scripts/assets/fondfont/pets/trial/cat.glb');
for (const path of files(resolve(root, 'dist'))) {
  if (path.endsWith('.glb')) {
    const bytes = readFileSync(path);
    assert.notEqual(createHash('sha256').update(bytes).digest('hex'), restrictedHash, 'restricted trial cat stays out of deployment');
    const gltf = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)));
    assert.ok(!gltf.nodes?.some(node => /StudioCat.*sculpt/.test(node.name ?? '')), 'no restricted cat geometry in any deployed model');
  }
  if (path.endsWith('.js')) assert.ok(!readFileSync(path, 'utf8').includes('__fondfont_pet_trial'), 'production has no private asset loader');
}
console.log('Production pets, original-source checksums, seven locale credits/posters and restricted-asset exclusion passed.');
