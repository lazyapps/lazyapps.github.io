import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { test } from 'node:test';
import sharp from 'sharp';
import service from '../src/image-service.mjs';
import { pressKits } from '../src/content/presskit-catalog.mjs';

const config = { service: { config: {} } };
for (const kit of pressKits) {
  for (const icon of kit.files.filter(file => file.kind === 'icon')) {
    test(`${kit.slug}/${icon.path}: thumbnail follows the original ICC profile`, async () => {
      const input = await readFile(new URL(`../${icon.source}`, import.meta.url));
      const result = await service.transform(input, { width: 300, format: 'png' }, config);
      const actual = await sharp(result.data).ensureAlpha().raw().toBuffer();
      const expected = await sharp(input).withIccProfile('srgb').resize(300)
        .ensureAlpha().raw().toBuffer();
      let error = 0, samples = 0;
      for (let i = 0; i < actual.length; i += 4) {
        if (actual[i + 3] < 250) continue;
        for (let channel = 0; channel < 3; channel++) {
          error += Math.abs(actual[i + channel] - expected[i + channel]);
          samples++;
        }
      }
      assert(samples > 0);
      assert(error / samples < 2, `Mean channel error: ${error / samples}`);
    });
  }
}

test('Calmon WebP keeps the green band vivid after 16-bit Display P3 conversion', async () => {
  const input = await readFile(new URL('../src/assets/img/calmon-icon.png', import.meta.url));
  const result = await service.transform(input, { width: 300, format: 'webp', quality: 95 }, config);
  const pixels = await sharp(result.data).ensureAlpha().raw().toBuffer();
  const offset = (150 * 300 + 240) * 4;
  // Independently checked with Pillow ICC conversion of the native PNG.
  const reference = [20, 201, 59];
  reference.forEach((value, channel) => assert(Math.abs(pixels[offset + channel] - value) < 8));
});
